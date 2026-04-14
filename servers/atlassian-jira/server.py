#!/usr/bin/env python3
"""
Atlassian Jira MCP Server

API Info:
- API License: Apache 2.0 (http://www.apache.org/licenses/LICENSE-2.0.html)
- Terms of Service: https://developer.atlassian.com/platform/marketplace/atlassian-developer-terms/

Generated: 2026-04-14 18:15:24 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import random
import sys
import time
import uuid
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Annotated, Any, Literal, overload

try:
    from dotenv import load_dotenv
    _env_path = Path(__file__).parent / '.env'
    if _env_path.exists():
        load_dotenv(_env_path)
except ImportError:
    pass

import _auth
import _models
import httpx
import pydantic
from fastmcp import FastMCP
from fastmcp.server.middleware import Middleware
from pydantic import AfterValidator, Field

BASE_URL = os.getenv("BASE_URL", "https://your-domain.atlassian.net")
SERVER_NAME = "Atlassian Jira"
SERVER_VERSION = "1.0.0"

CONNECTION_POOL_SIZE = int(os.getenv("CONNECTION_POOL_SIZE", "100"))
MAX_KEEPALIVE_CONNECTIONS = int(os.getenv("MAX_KEEPALIVE_CONNECTIONS", "20"))

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
if LOG_LEVEL not in ("DEBUG", "INFO", "WARNING", "ERROR"):
    LOG_LEVEL = "INFO"

HTTPX_TIMEOUT = httpx.Timeout(
    connect=float(os.getenv("HTTPX_CONNECT_TIMEOUT", "10.0")),
    read=float(os.getenv("HTTPX_READ_TIMEOUT", "60.0")),
    write=float(os.getenv("HTTPX_WRITE_TIMEOUT", "30.0")),
    pool=float(os.getenv("HTTPX_POOL_TIMEOUT", "5.0"))
)

DEFAULT_TIMEOUT = float(os.getenv("TOOL_EXECUTION_TIMEOUT", "90.0"))

MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
RETRY_BACKOFF_FACTOR = float(os.getenv("RETRY_BACKOFF_FACTOR", "2.0"))
CIRCUIT_BREAKER_FAILURE_THRESHOLD = int(os.getenv("CIRCUIT_BREAKER_FAILURE_THRESHOLD", "5"))
CIRCUIT_BREAKER_TIMEOUT_SECONDS = float(os.getenv("CIRCUIT_BREAKER_TIMEOUT_SECONDS", "60.0"))
RATE_LIMIT_REQUESTS_PER_SECOND = int(os.getenv("RATE_LIMIT_REQUESTS_PER_SECOND", "10"))
client: httpx.AsyncClient | None = None

@dataclass
class RetryConfig:
    """Retry with exponential backoff configuration."""
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    retry_on_status_codes: list[int] | None = None

    def __post_init__(self):
        if self.retry_on_status_codes is None:
            self.retry_on_status_codes = [429, 500, 502, 503, 504]

class TokenBucket:
    """Token bucket rate limiter."""

    def __init__(self, rate: float, capacity: int):
        self.rate = rate
        self.capacity = capacity
        self.tokens = float(capacity)
        self.last_update = time.monotonic()

    def _refill(self):
        now = time.monotonic()
        elapsed = now - self.last_update
        self.tokens = min(self.capacity, self.tokens + (elapsed * self.rate))
        self.last_update = now

    def consume(self, tokens: int = 1) -> tuple[bool, float | None]:
        self._refill()
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True, None
        tokens_needed = tokens - self.tokens
        return False, tokens_needed / self.rate

class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Blocking requests
    HALF_OPEN = "half_open"  # Testing recovery

@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration."""
    failure_threshold: int = 5
    success_threshold: int = 2
    timeout: float = 60.0

class CircuitBreakerError(Exception):
    """Circuit breaker is open, request blocked."""
    def __init__(self, message: str, retry_after: float | None = None):
        super().__init__(message)
        self.retry_after = retry_after

class CircuitBreaker:
    """Circuit breaker to prevent cascading failures."""

    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: float | None = None

    def before_call(self):
        """Check if circuit allows request."""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self._transition_to_half_open()
            else:
                retry_after = self._time_until_recovery()
                raise CircuitBreakerError(
                    "Circuit breaker OPEN due to repeated failures",
                    retry_after=retry_after
                )

    def on_success(self):
        """Handle successful request."""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self._transition_to_closed()
        elif self.state == CircuitState.CLOSED:
            if self.failure_count > 0:
                self.failure_count = 0

    def on_failure(self, error: Exception):
        """Handle failed request."""
        logging.debug(f"Circuit breaker recorded failure: {error}")
        if self.state == CircuitState.HALF_OPEN:
            self._transition_to_open()
        elif self.state == CircuitState.CLOSED:
            self.failure_count += 1
            if self.failure_count >= self.config.failure_threshold:
                self._transition_to_open()

    def _should_attempt_reset(self) -> bool:
        """Check if timeout elapsed for recovery."""
        if self.last_failure_time is None:
            return True
        return (time.monotonic() - self.last_failure_time) >= self.config.timeout

    def _time_until_recovery(self) -> float:
        """Time remaining until recovery attempt."""
        if self.last_failure_time is None:
            return 0.0
        elapsed = time.monotonic() - self.last_failure_time
        return max(0.0, self.config.timeout - elapsed)

    def _transition_to_open(self):
        """Transition to OPEN state."""
        self.state = CircuitState.OPEN
        self.last_failure_time = time.monotonic()
        self.success_count = 0
        logging.error(f"Circuit breaker OPEN after {self.failure_count} failures")

    def _transition_to_half_open(self):
        """Transition to HALF_OPEN state."""
        self.state = CircuitState.HALF_OPEN
        self.failure_count = 0
        self.success_count = 0
        logging.info("Circuit breaker HALF_OPEN - testing recovery")

    def _transition_to_closed(self):
        """Transition to CLOSED state."""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        logging.info("Circuit breaker CLOSED - recovered")

# Global resilience configuration
retry_config: RetryConfig | None = None
rate_limiter = None  # Initialized based on mode in main()
circuit_breaker: CircuitBreaker | None = None

# ============================================================================
# Error Formatting
# ============================================================================

def _format_api_error_message(
    tool_name: str | None,
    method: str,
    path: str,
    status_code: int,
    request_id: str | None,
    error_data: dict
) -> str:
    """
    Format API error for LLM consumption with structured, parseable details.

    Args:
        tool_name: MCP tool function name
        method: HTTP method (GET, POST, etc.)
        path: API endpoint path
        status_code: HTTP status code
        request_id: Request UUID
        error_data: Sanitized error response from API

    Returns:
        Structured error message for LLM with available details
    """
    parts = []

    # Add tool name if available
    if tool_name:
        parts.append(f"Tool: {tool_name}")

    parts.append(f"Status: {status_code}")

    # Extract error message from various API response formats
    error_message = None
    if isinstance(error_data, dict):
        # Format 1: {"message": "..."}
        if 'message' in error_data:
            error_message = error_data['message']
        # Format 2: {"error": {"message": "...", "code": ..., "errors": [...]}}  (Google APIs)
        elif 'error' in error_data:
            err = error_data['error']
            if isinstance(err, dict):
                if 'message' in err:
                    error_message = err['message']
                # Also include error code if available
                if 'code' in err and error_message:
                    error_message = f"[{err['code']}] {error_message}"
            elif isinstance(err, str):
                error_message = err
        # Format 3: {"detail": "..."} (FastAPI/OpenAPI)
        elif 'detail' in error_data:
            detail = error_data['detail']
            if isinstance(detail, str):
                error_message = detail
            elif isinstance(detail, list) and detail:
                # Validation errors: [{"loc": [...], "msg": "...", "type": "..."}]
                msgs = [d.get('msg', str(d)) if isinstance(d, dict) else str(d) for d in detail[:3]]
                error_message = "; ".join(msgs)
                if len(detail) > 3:
                    error_message += f" (+{len(detail) - 3} more)"
        # Format 4: {"errors": [...]} (GraphQL-style)
        elif 'errors' in error_data and isinstance(error_data['errors'], list):
            errors = error_data['errors']
            if errors:
                msgs = [e.get('message', str(e)) if isinstance(e, dict) else str(e) for e in errors[:3]]
                error_message = "; ".join(msgs)
                if len(errors) > 3:
                    error_message += f" (+{len(errors) - 3} more)"

    if error_message:
        parts.append(f"Error: {error_message}")

    parts.append(f"Request: {method} {path}")

    # Add request ID if available
    if request_id:
        parts.append(f"ID: {request_id}")

    return "\n".join(parts)

# ============================================================================
# Response Sanitization
# ============================================================================

# Sanitization level configuration
SANITIZATION_LEVEL = os.getenv("SANITIZATION_LEVEL", "DISABLED").upper()
if SANITIZATION_LEVEL not in ("DISABLED", "LOW", "MEDIUM", "HIGH"):
    SANITIZATION_LEVEL = "DISABLED"

# Pattern sets by level
_PATTERNS_LOW = [
    'password', 'passwd', 'pwd',
    'token', 'secret', 'private_key', 'priv_key',
]
_PATTERNS_MEDIUM = _PATTERNS_LOW + [
    'auth_token', 'access_token', 'refresh_token', 'bearer',
    'credentials', 'authorization',
]
_PATTERNS_HIGH = _PATTERNS_MEDIUM + [
    'session_id', 'sessionid', 'cookie',
    'api_key', 'apikey', 'api-key',
    'user_id', 'userid', 'account_id', 'accountid', 'internal_id',
    'ip_address', 'ipaddress', 'ip_addr',
    'hostname', 'host_name', 'server_name', 'servername',
    'internal_ip', 'private_ip',
]

def _get_sensitive_patterns() -> list:
    """Get patterns based on current sanitization level."""
    if SANITIZATION_LEVEL == "DISABLED":
        return []
    if SANITIZATION_LEVEL == "LOW":
        return _PATTERNS_LOW
    if SANITIZATION_LEVEL == "MEDIUM":
        return _PATTERNS_MEDIUM
    return _PATTERNS_HIGH

def sanitize_response(response_data: Any) -> Any:
    """Remove sensitive fields from API responses before returning to LLM.

    Controlled by SANITIZATION_LEVEL env var:
    - DISABLED: No filtering (fastest)
    - LOW: Basic secrets (password, token, secret, private_key)
    - MEDIUM: LOW + Auth fields
    - HIGH: MEDIUM + Session/IDs

    Args:
        response_data: API response (dict, list, or primitive)

    Returns:
        Sanitized response with sensitive fields removed (based on level)
    """
    sensitive_patterns = _get_sensitive_patterns()

    # Skip sanitization if disabled
    if not sensitive_patterns:
        return response_data

    def should_filter(key: str) -> bool:
        """Check if field name matches sensitive patterns."""
        key_lower = key.lower()
        return any(pattern in key_lower for pattern in sensitive_patterns)

    def sanitize_dict(data: dict) -> dict:
        """Recursively sanitize dictionary."""
        sanitized: dict[str, Any] = {}
        for key, value in data.items():
            if should_filter(key):
                # Skip sensitive fields
                logging.debug(f"Filtered sensitive field: {key}")
                continue

            # Recursively sanitize nested structures
            if isinstance(value, dict):
                sanitized[key] = sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[key] = sanitize_list(value)
            else:
                sanitized[key] = value

        return sanitized

    def sanitize_list(data: list[Any]) -> list[Any]:
        """Recursively sanitize list."""
        sanitized: list[Any] = []
        for item in data:
            if isinstance(item, dict):
                sanitized.append(sanitize_dict(item))
            elif isinstance(item, list):
                sanitized.append(sanitize_list(item))
            else:
                sanitized.append(item)
        return sanitized

    # Handle different response types
    if isinstance(response_data, dict):
        return sanitize_dict(response_data)
    if isinstance(response_data, list):
        return sanitize_list(response_data)
    # Primitive types (str, int, bool, None) pass through
    return response_data

def get_safe_error_response(
    error_type: str,
    status_code: int | None = None,
    retry_after: int | None = None,
    request_id: str | None = None
) -> dict:
    """Generate safe error response for client (LLM).

    Returns generic, actionable error messages without leaking:
    - API keys, tokens, credentials
    - Internal server details, IP addresses, hostnames
    - Stack traces, exception messages
    - User data from other users

    Args:
        error_type: Type of error (auth, rate_limit, timeout, etc.)
        status_code: HTTP status code
        retry_after: Retry-After header value (seconds)
        request_id: Request correlation ID for debugging

    Returns:
        Safe error response dictionary
    """
    error_messages = {
        'AUTHENTICATION_ERROR': {
            'error': 'AUTHENTICATION_ERROR',
            'message': 'Authentication failed. Please check your credentials.',
            'retry': False
        },
        'RATE_LIMIT_ERROR': {
            'error': 'RATE_LIMIT_ERROR',
            'message': 'Rate limit exceeded. Please retry after the specified delay.',
            'retry': True
        },
        'TIMEOUT_ERROR': {
            'error': 'TIMEOUT_ERROR',
            'message': 'Request timed out. The API did not respond in time.',
            'retry': True
        },
        'VALIDATION_ERROR': {
            'error': 'VALIDATION_ERROR',
            'message': 'Invalid request parameters. Please check your input.',
            'retry': False
        },
        'NOT_FOUND': {
            'error': 'NOT_FOUND',
            'message': 'The requested resource was not found.',
            'retry': False
        },
        'PERMISSION_DENIED': {
            'error': 'PERMISSION_DENIED',
            'message': 'You do not have permission to access this resource.',
            'retry': False
        },
        'API_ERROR': {
            'error': 'API_ERROR',
            'message': 'An error occurred while calling the external API.',
            'retry': True
        },
        'INTERNAL_ERROR': {
            'error': 'INTERNAL_ERROR',
            'message': 'An internal error occurred. Please try again later.',
            'retry': False
        }
    }

    # Get base error response
    response = error_messages.get(error_type, error_messages['INTERNAL_ERROR']).copy()

    # Add optional fields
    if status_code:
        response['status_code'] = status_code

    if retry_after:
        response['retry_after_seconds'] = retry_after

    if request_id:
        response['request_id'] = request_id

    return response

async def _make_request(
    method: str,
    path: str,
    params: dict[str, Any] | None = None,
    body: Any = None,
    body_content_type: str | None = None,
    headers: dict[str, str] | None = None,
    cookies: dict[str, str] | None = None,
    tool_name: str | None = None,
    request_id: str | None = None,
    raw_querystring: str | None = None,
) -> tuple[dict[str, Any], int]:
    """Make HTTP request with retry, rate limiting, and circuit breaker."""
    global client, retry_config, rate_limiter, circuit_breaker

    if client is None:
        client = httpx.AsyncClient(
            base_url=BASE_URL,
            timeout=HTTPX_TIMEOUT,
            limits=httpx.Limits(max_keepalive_connections=MAX_KEEPALIVE_CONNECTIONS, max_connections=CONNECTION_POOL_SIZE),
            cookies=None,
            follow_redirects=True,
        )

    if headers is None:
        headers = {}
    headers.setdefault("Accept", "application/json")
    if method.upper() in ("POST", "PUT", "PATCH") and (body_content_type is None or body_content_type == "application/json"):
        headers.setdefault("Content-Type", "application/json")


    if rate_limiter is not None:
        allowed, wait_time = rate_limiter.consume()
        if not allowed:
            return {
                "error": "Rate limit exceeded",
                "retry_after": wait_time,
                "message": f"Rate limit exceeded. Wait {wait_time:.1f}s"
            }, 429

    if circuit_breaker is not None:
        try:
            circuit_breaker.before_call()
        except CircuitBreakerError as e:
            return {
                "error": "Circuit breaker open",
                "retry_after": e.retry_after,
                "message": str(e)
            }, 503

    if retry_config is not None:
        max_attempts = retry_config.max_attempts
        retry_status_codes = retry_config.retry_on_status_codes or []
    else:
        max_attempts = 1
        retry_status_codes = []

    # Append raw querystring before retry loop to avoid repeated appending
    # (OAS 3.2 in: querystring — already serialized per media type)
    if raw_querystring:
        _qs_sep = "&" if "?" in path else "?"
        path = f"{path}{_qs_sep}{raw_querystring}"

    last_error: httpx.HTTPStatusError | Exception | None = None
    _auth_retried = False  # Guard: only attempt one auth refresh per request
    for attempt in range(max_attempts):
        try:
            # Dispatch body to correct httpx kwarg based on content type
            _json = body if body_content_type is None or body_content_type == "application/json" else None
            _data = body if body_content_type in ("application/x-www-form-urlencoded", "multipart/form-data") else None
            _content = None
            if body_content_type is not None and body_content_type not in ("application/json", "application/x-www-form-urlencoded", "multipart/form-data"):
                _raw = body
                _content = json.dumps(_raw).encode() if isinstance(_raw, (dict, list)) else _raw
            response = await client.request(
                method=method,
                url=path,
                params=params,
                json=_json,
                data=_data,
                content=_content,
                headers=headers,
                cookies=cookies
            )

            # Get status code and data before raise_for_status
            status_code = response.status_code

            # Handle empty response body (204 No Content, 205 Reset Content, or empty body)
            if status_code in (204, 205) or not response.content:
                response_data = {"status": status_code, "message": "Success"}
            else:
                # Parse response JSON (graceful fallback to text)
                try:
                    response_data = response.json()
                except Exception:
                    response_data = {"text": response.text}

            # Check for HTTP errors
            if status_code >= 400:
                last_error = httpx.HTTPStatusError(
                    message=f"HTTP {status_code}",
                    request=response.request,
                    response=response
                )

                # On 401: clear stale tokens and retry once with fresh auth
                if status_code == 401 and not _auth_retried and tool_name:
                    _auth_retried = True
                    logging.warning(f"401 Unauthorized for {tool_name} - clearing token and re-authorizing")
                    _on_auth_failure()
                    _fresh_auth = await _get_auth_for_operation(tool_name)
                    if _fresh_auth.get("headers"):
                        headers = {**headers, **_fresh_auth["headers"]}
                    if _fresh_auth.get("params") and params is not None:
                        params = {**params, **_fresh_auth["params"]}
                    continue  # Retry immediately with fresh auth (no backoff)

                # Check if should retry
                if status_code not in retry_status_codes or attempt == max_attempts - 1:
                    # Don't retry or last attempt - notify circuit breaker of failure
                    if circuit_breaker is not None and status_code in [500, 502, 503, 504]:
                        circuit_breaker.on_failure(last_error)

                    # Log error information - WARNING for client errors (4xx), ERROR for server errors (5xx)
                    log_level = logging.WARNING if 400 <= status_code < 500 else logging.ERROR
                    logging.log(
                        log_level,
                        f"API request failed: {method} {path} (status: {status_code})",
                        extra={
                            "status_code": status_code,
                            "endpoint": path,
                            "method": method,
                            "attempt": attempt + 1,
                            "max_attempts": max_attempts,
                            "error_detail": str(response_data)[:500]
                        },
                        exc_info=False
                    )

                    # Sanitize response before returning/raising
                    sanitized_data = sanitize_response(response_data)

                    # Raise exception with structured error message for LLM
                    error_message = _format_api_error_message(
                        tool_name=tool_name,
                        method=method,
                        path=path,
                        status_code=status_code,
                        request_id=request_id,
                        error_data=sanitized_data
                    )
                    raise ValueError(error_message)

                # Will retry - continue to backoff logic below

            else:
                # Success - notify circuit breaker
                if circuit_breaker is not None:
                    circuit_breaker.on_success()

                # Sanitize response before returning to client
                sanitized_data = sanitize_response(response_data)
                return sanitized_data, status_code

            # Exponential backoff with jitter (for retry)
            # retry_config is guaranteed non-None here since max_attempts > 1
            assert retry_config is not None
            base_delay = retry_config.base_delay
            max_delay = retry_config.max_delay
            exponential_base = retry_config.exponential_base
            use_jitter = retry_config.jitter

            # Honor Retry-After header for 429 responses
            delay: float
            if status_code == 429:
                retry_after = response.headers.get('Retry-After')
                if retry_after:
                    try:
                        delay = float(retry_after)
                    except ValueError:
                        delay = min(base_delay * (exponential_base ** attempt), max_delay)
                else:
                    delay = min(base_delay * (exponential_base ** attempt), max_delay)
            else:
                delay = min(base_delay * (exponential_base ** attempt), max_delay)

            # Add jitter
            if use_jitter:
                delay = delay * (0.5 + random.random() * 0.5)  # noqa: S311

            logging.warning(
                f"Request failed with {status_code} (attempt {attempt + 1}/{max_attempts}). "
                f"Retrying in {delay:.2f}s"
            )
            await asyncio.sleep(delay)

        except httpx.HTTPStatusError:
            # Already handled above - shouldn't reach here
            continue

        except Exception as e:
            last_error = e

            # Network/connection errors - notify circuit breaker
            if circuit_breaker is not None:
                circuit_breaker.on_failure(e)

            # Log detailed error information for debugging (internal only)
            logging.error(
                f"Request failed with exception: {method} {path}",
                extra={
                    "endpoint": path,
                    "method": method,
                    "attempt": attempt + 1,
                    "max_attempts": max_attempts,
                    "error_type": e.__class__.__name__,
                    "error_detail": str(e)
                },
                exc_info=True
            )

            # Don't retry on non-HTTP errors - raise immediately with details
            # This ensures the LLM sees the actual error message
            error_message = (
                f"Tool: {tool_name}\n"
                f"Error: {e.__class__.__name__}\n"
                f"Request: {method} {path}\n"
                f"ID: {request_id}\n"
                f"Details: {str(e)}"
            )
            raise ConnectionError(error_message) from e

    # Log retry exhaustion with full context (internal only)
    logging.error(
        f"All retry attempts exhausted: {method} {path}",
        extra={
            "endpoint": path,
            "method": method,
            "total_attempts": max_attempts,
            "last_error_type": last_error.__class__.__name__ if last_error else "Unknown",
            "last_error_detail": str(last_error) if last_error else "Unknown"
        },
        exc_info=True
    )

    # Raise exception with error details
    if isinstance(last_error, httpx.HTTPStatusError):
        try:
            error_data = last_error.response.json()
        except Exception:
            error_data = {"error": last_error.response.text[:1000]}

        sanitized_error = sanitize_response(error_data)
        error_message = _format_api_error_message(
            tool_name=tool_name,
            method=method,
            path=path,
            status_code=last_error.response.status_code,
            request_id=request_id,
            error_data=sanitized_error
        )
        raise ValueError(error_message)

    # Network/connection error - structured format for consistency
    error_message = (
        f"Tool: {tool_name}\n"
        f"Error: Network error after {max_attempts} attempts\n"
        f"Request: {method} {path}\n"
        f"ID: {request_id}\n"
        f"Details: {str(last_error)}"
    )
    raise ConnectionError(error_message)

# ============================================================================
# MCP Input Coercion Middleware
# ============================================================================
# Defensive middleware: some MCP clients (including Claude) may send dict/list
# arguments as JSON strings instead of native objects. This violates the MCP spec
# but is a known, widespread client-side issue. This middleware transparently
# parses stringified JSON before Pydantic validation, preventing tool call failures.
# See: https://github.com/PrefectHQ/fastmcp/issues/932

class _JsonCoercionMiddleware(Middleware):
    async def on_call_tool(self, context, call_next):
        if context.message.arguments:
            for key, value in context.message.arguments.items():
                if isinstance(value, str) and len(value) > 1 and value[0] in ('{', '['):
                    try:
                        context.message.arguments[key] = json.loads(value)
                    except (json.JSONDecodeError, ValueError):
                        pass
        return await call_next(context)


# ============================================================================
# Helper Functions
# ============================================================================

@overload
def _parse_int(v: str | int) -> int: ...
@overload
def _parse_int(v: None) -> None: ...
def _parse_int(v: str | int | None) -> int | None:
    """Convert a string representation of an integer to a Python int.

    Formatted integer parameters (int32, int64, uint64, etc.) are exposed as str
    in the tool signature to prevent JS float64 precision loss for large IDs.
    This helper converts them back to int before Pydantic model construction.
    None passes through for optional parameters.
    Raises ValueError for non-integer strings or unexpected types (e.g. bool).
    """
    if v is None:
        return None
    if isinstance(v, bool):
        raise ValueError(f"Expected an integer value, got {v!r}")
    if isinstance(v, int):
        return v
    try:
        return int(v)
    except (ValueError, TypeError) as _e:
        raise ValueError(f"Expected an integer value, got {v!r}") from _e

def _check_unique_items(v: list) -> list:
    """Validate that array items are unique (OAS uniqueItems: true)."""
    seen = []
    for item in v:
        if item in seen:
            raise ValueError("array items must be unique")
        seen.append(item)
    return v

def _log_tool_invocation(tool_name: str, method: str, path: str, request_id: str, _redact: str = "") -> None:
    """Log tool invocation. If _redact is set, that value is partially masked in the logged path."""
    log_path = path
    if _redact:
        log_path = log_path.replace(_redact, _redact[:4] + "***" if len(_redact) > 4 else "***")

    logging.info(
        f"Tool invoked: {tool_name}",
        extra={
            "request_id": request_id,
            "tool": tool_name,
            "method": method,
            "path": log_path,
            "timeout": DEFAULT_TIMEOUT
        }
    )

def _build_path(
    template: str,
    path_params: dict[str, Any],
) -> str:
    """Build path from template and parameters.

    Args:
        template: Path template with {param} placeholders
        path_params: Dictionary of parameter names to values

    Returns:
        Path with all  placeholders replaced

    Example:
        _build_path("/files/{fileId}/copy", {"fileId": "abc123"})
        Returns: "/files/abc123/copy"
    """
    result = template
    for key, value in path_params.items():
        result = result.replace("{" + key + "}", str(value))
    # Normalize double slashes from path param substitution (e.g. "/{path}" + "/foo")
    # but preserve "://" in URL-valued params (e.g. siteUrl="https://example.com")
    while "//" in result:
        cleaned = result.replace("://", ":%SCHEME%")
        cleaned = cleaned.replace("//", "/")
        cleaned = cleaned.replace(":%SCHEME%", "://")
        if cleaned == result:
            break
        result = cleaned
    return result

async def _execute_tool_request(
    tool_name: str,
    method: str,
    path: str,
    request_id: str,
    params: dict[str, Any] | None = None,
    body: Any = None,
    body_content_type: str | None = None,
    headers: dict[str, str] | None = None,
    cookies: dict[str, str] | None = None,
    raw_querystring: str | None = None,
) -> tuple[dict[str, Any], int]:
    """
    Execute tool request with timeout handling and metrics recording.

    Returns:
        Tuple of (normalized_response_data, status_code).
        Response data is normalized to dict format for Pydantic validation.
        Status code: HTTP status code from the API response.
    """
    start_time = time.time()
    try:
        # Wrap API call with timeout to prevent hanging
        async with asyncio.timeout(DEFAULT_TIMEOUT):
            # Call unified _make_request() which handles all resilience + security features
            result, status_code = await _make_request(
                method=method,
                path=path,
                params=params,
                body=body,
                body_content_type=body_content_type,
                headers=headers,
                cookies=cookies,
                tool_name=tool_name,
                request_id=request_id,
                raw_querystring=raw_querystring,
            )

        latency_ms = (time.time() - start_time) * 1000.0

        logging.info(f"Tool completed: {tool_name}", extra={"request_id": request_id, "latency_ms": f"{latency_ms:.2f}"})

        # Normalize response to dict and return with status code
        # Use "value" key for consistency with generated response models
        if isinstance(result, dict):
            return result, status_code
        return {"value": result}, status_code

    except asyncio.TimeoutError as e:
        latency_ms = (time.time() - start_time) * 1000.0

        # Request timed out
        logging.error(
            f"Tool timeout: {tool_name}",
            extra={
                "request_id": request_id,
                "tool": tool_name,
                "method": method,
                "path": path,
                "timeout": DEFAULT_TIMEOUT,
                "latency_ms": f"{latency_ms:.2f}"
            }
        )

        # Raise exception with structured error message for consistency
        # FastMCP will catch this and set isError: true in MCP response
        timeout_message = (
            f"Tool: {tool_name}\n"
            f"Error: Request timed out after {DEFAULT_TIMEOUT} seconds\n"
            f"ID: {request_id}"
        )
        raise asyncio.TimeoutError(timeout_message) from e

    except ValueError:
        latency_ms = (time.time() - start_time) * 1000.0
        raise

    except ConnectionError:
        latency_ms = (time.time() - start_time) * 1000.0
        raise

    except Exception:
        latency_ms = (time.time() - start_time) * 1000.0
        raise

# ============================================================================
# Authentication
# ============================================================================

# Authentication scheme priority (most secure first)
AUTH_SCHEME_PRIORITY = [
    'OAuth2',
    'basicAuth',
]

# Initialize authentication handlers at server startup
_auth_handlers: dict[str, Any] = {}
try:
    _auth_handlers["OAuth2"] = _auth.OAuth2Auth()
    logging.info("Authentication configured: OAuth2")
except ValueError as e:
    # Extract credential names from error message (first sentence before "Leave empty")
    error_msg = str(e).split("Leave empty")[0].strip()
    logging.warning(f"Credentials for OAuth2 not configured: {error_msg}")
    _auth_handlers["OAuth2"] = None
try:
    _auth_handlers["basicAuth"] = _auth.BasicAuth(env_var_username="BASIC_AUTH_USERNAME", env_var_password="BASIC_AUTH_PASSWORD")
    logging.info("Authentication configured: basicAuth")
except ValueError as e:
    # Extract credential names from error message (first sentence before "Leave empty")
    error_msg = str(e).split("Leave empty")[0].strip()
    logging.warning(f"Credentials for basicAuth not configured: {error_msg}")
    _auth_handlers["basicAuth"] = None

# Warn only if NO auth handlers were successfully configured
if all(handler is None for handler in _auth_handlers.values()):
    logging.warning("Server will attempt unauthenticated requests (may fail if API requires auth)")

def _on_auth_failure() -> None:
    """Clear tokens on all auth handlers that support it (called on 401 response)."""
    for scheme_name, handler in _auth_handlers.items():
        if handler is not None and hasattr(handler, 'clear_token'):
            handler.clear_token()
            logging.info(f"Cleared token for auth scheme '{scheme_name}' after 401")

async def _get_auth_for_operation(operation_id: str) -> dict[str, dict[str, str]]:
    """Get authentication for specific operation (handles multi-auth with OR/AND logic).

    Args:
        operation_id: The operation ID (tool name) to get auth for

    Returns:
        Dictionary with 'headers', 'params', 'cookies', 'path_params' keys containing auth data
    """
    result: dict[str, dict[str, str]] = {"headers": {}, "params": {}, "cookies": {}, "path_params": {}}

    # Get auth requirements for this operation from auth module
    # Map structure: operation_id -> [[scheme1], [scheme2, scheme3]] (OR of AND groups)
    required_schemes = _auth.OPERATION_AUTH_MAP.get(operation_id)

    if required_schemes is None:
        # CRITICAL: Operation missing from OPERATION_AUTH_MAP
        # This indicates a bug in auth config generation - operation should be in map
        # Do NOT fall back to global security - this masks bugs and creates security gaps
        logging.error(
            f"SECURITY ERROR: Operation '{operation_id}' not found in OPERATION_AUTH_MAP. "
            f"This indicates a bug in auth config generation. "
            f"All operations should be explicitly mapped. "
            f"Proceeding with no authentication - REQUEST WILL LIKELY FAIL."
        )
        # Return empty auth (will likely fail at API, but surfaces the bug)
        return result

    # Sort OR groups by security priority (most secure first)
    # Each OR group is sorted internally by scheme priority
    def get_scheme_priority(scheme_name: str) -> int:
        """Get priority index for scheme (lower = higher priority)."""
        try:
            return AUTH_SCHEME_PRIORITY.index(scheme_name)
        except ValueError:
            # Unknown scheme - put at end
            return len(AUTH_SCHEME_PRIORITY)

    # Sort each OR group by priority, then sort OR groups by their best (lowest) priority
    sorted_schemes = []
    for scheme_list in required_schemes:
        # Sort schemes within AND group by priority (most secure first)
        sorted_group = sorted(scheme_list, key=get_scheme_priority)
        sorted_schemes.append(sorted_group)

    # Sort OR groups by the priority of their first (most secure) scheme
    sorted_schemes.sort(key=lambda group: get_scheme_priority(group[0]) if group else float('inf'))

    # Try each OR group in priority order (most secure first)
    for scheme_list in sorted_schemes:
        headers = {}
        params = {}
        cookies = {}
        path_params = {}
        all_succeeded = True

        # Handle AND group (multiple schemes in same list - all must succeed)
        for scheme_name in scheme_list:
            handler = _auth_handlers.get(scheme_name)
            if not handler:
                # Handler not configured (env vars missing)
                all_succeeded = False
                logging.debug(f"Auth scheme '{scheme_name}' not configured for {operation_id}")
                break

            try:
                # Try all injection methods (headers, params, cookies, path_params)
                # OAuth2 methods are async (token refresh/authorize); others are sync.
                import inspect as _inspect
                if hasattr(handler, 'get_auth_headers'):
                    _h = handler.get_auth_headers()
                    headers.update(await _h if _inspect.isawaitable(_h) else _h)
                if hasattr(handler, 'get_auth_params'):
                    _p = handler.get_auth_params()
                    params.update(await _p if _inspect.isawaitable(_p) else _p)
                if hasattr(handler, 'get_auth_cookies'):
                    _c = handler.get_auth_cookies()
                    cookies.update(await _c if _inspect.isawaitable(_c) else _c)
                if hasattr(handler, 'get_auth_path_params'):
                    _pp = handler.get_auth_path_params()
                    path_params.update(await _pp if _inspect.isawaitable(_pp) else _pp)
            except Exception as e:
                logging.debug(f"Auth scheme '{scheme_name}' failed for {operation_id}: {e}")
                all_succeeded = False
                break

        # If all schemes in AND group succeeded, use this auth
        if all_succeeded and (headers or params or cookies or path_params):
            result["headers"] = headers
            result["params"] = params
            result["cookies"] = cookies
            result["path_params"] = path_params
            logging.debug(f"Using auth for {operation_id}: schemes={scheme_list}")
            return result

    # No auth configured or all OR groups failed
    if required_schemes and required_schemes != [[]]:
        logging.warning(f"No configured auth handler found for {operation_id} (requires: {required_schemes})")

    return result

# ============================================================================
# FastMCP Server Initialization
# ============================================================================

mcp = FastMCP("Atlassian Jira", middleware=[_JsonCoercionMiddleware()])

# Tags: Issue custom field values (apps)
@mcp.tool()
async def update_custom_field_values(
    generate_changelog: bool | None = Field(None, alias="generateChangelog", description="Whether to generate a changelog entry for this update. Defaults to true if not specified."),
    updates: list[_models.MultipleCustomFieldValuesUpdate] | None = Field(None, description="Array of custom field value updates to apply. Each entry specifies a custom field and the issue(s) to update with their new values. Order is not significant."),
) -> dict[str, Any]:
    """Update the values of one or more custom fields across one or more issues. Each custom field and issue combination must be unique within the request. Only the app that owns the custom field can perform this operation."""

    # Construct request model with validation
    try:
        _request = _models.UpdateMultipleCustomFieldValuesRequest(
            query=_models.UpdateMultipleCustomFieldValuesRequestQuery(generate_changelog=generate_changelog),
            body=_models.UpdateMultipleCustomFieldValuesRequestBody(updates=updates)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_custom_field_values: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/app/field/value"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_custom_field_values")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_custom_field_values", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_custom_field_values",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue custom field values (apps)
@mcp.tool()
async def update_custom_field_value(
    field_id_or_key: str = Field(..., alias="fieldIdOrKey", description="The ID or key of the custom field to update (e.g., customfield_10010)."),
    generate_changelog: bool | None = Field(None, alias="generateChangelog", description="Whether to generate a changelog entry for this update. Defaults to true if not specified."),
    updates: list[_models.CustomFieldValueUpdate] | None = Field(None, description="An array of custom field update details specifying which issues to update and their new values."),
) -> dict[str, Any]:
    """Updates the value of a custom field across one or more issues. Only the app that owns the custom field can perform this operation."""

    # Construct request model with validation
    try:
        _request = _models.UpdateCustomFieldValueRequest(
            path=_models.UpdateCustomFieldValueRequestPath(field_id_or_key=field_id_or_key),
            query=_models.UpdateCustomFieldValueRequestQuery(generate_changelog=generate_changelog),
            body=_models.UpdateCustomFieldValueRequestBody(updates=updates)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_custom_field_value: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/app/field/{fieldIdOrKey}/value", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/app/field/{fieldIdOrKey}/value"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_custom_field_value")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_custom_field_value", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_custom_field_value",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue attachments
@mcp.tool()
async def download_attachment(
    id_: str = Field(..., alias="id", description="The unique identifier of the attachment to download."),
    redirect: bool | None = Field(None, description="Whether to follow HTTP redirects for the attachment download. Set to false if your client doesn't automatically follow redirects to avoid multiple requests. Defaults to true."),
) -> dict[str, Any]:
    """Download the full content of an attachment file. Supports partial downloads using HTTP Range headers to retrieve specific byte ranges. This operation can be accessed anonymously if you have the required project and issue permissions."""

    # Construct request model with validation
    try:
        _request = _models.GetAttachmentContentRequest(
            path=_models.GetAttachmentContentRequestPath(id_=id_),
            query=_models.GetAttachmentContentRequestQuery(redirect=redirect)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for download_attachment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/attachment/content/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/attachment/content/{id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("download_attachment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("download_attachment", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="download_attachment",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue attachments
@mcp.tool()
async def get_attachment_thumbnail(
    id_: str = Field(..., alias="id", description="The unique identifier of the attachment for which to retrieve the thumbnail."),
    redirect: bool | None = Field(None, description="Whether to return a redirect URL for the thumbnail instead of the image content directly. Set to false to avoid multiple requests if your client doesn't automatically follow redirects."),
    fallback_to_default: bool | None = Field(None, alias="fallbackToDefault", description="Whether to return a default placeholder thumbnail when the requested attachment thumbnail cannot be generated or found."),
    width: str | None = Field(None, description="The maximum width in pixels to scale the thumbnail to. The thumbnail will be scaled proportionally to fit within this width."),
    height: str | None = Field(None, description="The maximum height in pixels to scale the thumbnail to. The thumbnail will be scaled proportionally to fit within this height."),
) -> dict[str, Any]:
    """Retrieves a thumbnail image for an attachment. Supports optional scaling and fallback behavior when thumbnails are unavailable."""

    _width = _parse_int(width)
    _height = _parse_int(height)

    # Construct request model with validation
    try:
        _request = _models.GetAttachmentThumbnailRequest(
            path=_models.GetAttachmentThumbnailRequestPath(id_=id_),
            query=_models.GetAttachmentThumbnailRequestQuery(redirect=redirect, fallback_to_default=fallback_to_default, width=_width, height=_height)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_attachment_thumbnail: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/attachment/thumbnail/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/attachment/thumbnail/{id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_attachment_thumbnail")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_attachment_thumbnail", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_attachment_thumbnail",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue attachments
@mcp.tool()
async def get_attachment(id_: str = Field(..., alias="id", description="The unique identifier of the attachment whose metadata you want to retrieve.")) -> dict[str, Any]:
    """Retrieve metadata for an attachment, including details like filename, size, and creation date. The attachment content itself is not returned by this operation."""

    # Construct request model with validation
    try:
        _request = _models.GetAttachmentRequest(
            path=_models.GetAttachmentRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_attachment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/attachment/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/attachment/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_attachment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_attachment", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_attachment",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue attachments
@mcp.tool()
async def delete_attachment(id_: str = Field(..., alias="id", description="The unique identifier of the attachment to delete.")) -> dict[str, Any]:
    """Removes an attachment from an issue. Requires either permission to delete your own attachments or permission to delete any attachment in the project."""

    # Construct request model with validation
    try:
        _request = _models.RemoveAttachmentRequest(
            path=_models.RemoveAttachmentRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_attachment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/attachment/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/attachment/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_attachment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_attachment", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_attachment",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue attachments
@mcp.tool()
async def get_attachment_metadata_with_contents(id_: str = Field(..., alias="id", description="The unique identifier of the attachment to retrieve metadata for.")) -> dict[str, Any]:
    """Retrieve complete metadata for an attachment and its contents if it's an archive. Returns information about the attachment itself (ID, name) plus details about any files within supported archive formats like ZIP."""

    # Construct request model with validation
    try:
        _request = _models.ExpandAttachmentForHumansRequest(
            path=_models.ExpandAttachmentForHumansRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_attachment_metadata_with_contents: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/attachment/{id}/expand/human", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/attachment/{id}/expand/human"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_attachment_metadata_with_contents")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_attachment_metadata_with_contents", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_attachment_metadata_with_contents",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue attachments
@mcp.tool()
async def get_archive_contents_metadata(id_: str = Field(..., alias="id", description="The unique identifier of the attachment to expand and retrieve contents metadata for.")) -> dict[str, Any]:
    """Retrieve metadata for the contents of an archive attachment, such as files within a ZIP archive. Use this operation when processing attachment data programmatically without user presentation."""

    # Construct request model with validation
    try:
        _request = _models.ExpandAttachmentForMachinesRequest(
            path=_models.ExpandAttachmentForMachinesRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_archive_contents_metadata: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/attachment/{id}/expand/raw", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/attachment/{id}/expand/raw"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_archive_contents_metadata")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_archive_contents_metadata", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_archive_contents_metadata",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Avatars
@mcp.tool()
async def list_system_avatars(type_: Literal["issuetype", "project", "user", "priority"] = Field(..., alias="type", description="The category of avatars to retrieve. Must be one of: issuetype, project, user, or priority.")) -> dict[str, Any]:
    """Retrieves a list of system avatars filtered by type (issue type, project, user, or priority). This operation is publicly accessible and requires no authentication."""

    # Construct request model with validation
    try:
        _request = _models.GetAllSystemAvatarsRequest(
            path=_models.GetAllSystemAvatarsRequestPath(type_=type_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_system_avatars: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/avatar/{type}/system", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/avatar/{type}/system"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_system_avatars")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_system_avatars", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_system_avatars",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue bulk operations
@mcp.tool()
async def delete_issues_bulk(
    selected_issue_ids_or_keys: list[str] = Field(..., alias="selectedIssueIdsOrKeys", description="List of issue IDs or keys to delete. Can include issues from different projects and types. Order is not significant."),
    send_bulk_notification: bool | None = Field(None, alias="sendBulkNotification", description="Whether to send a bulk change notification email to users about the deletions. Enabled by default."),
) -> dict[str, Any]:
    """Submit a bulk delete request to remove multiple issues across projects in a single operation. You can delete up to 1,000 issues at once, with optional notification to affected users."""

    # Construct request model with validation
    try:
        _request = _models.SubmitBulkDeleteRequest(
            body=_models.SubmitBulkDeleteRequestBody(selected_issue_ids_or_keys=selected_issue_ids_or_keys, send_bulk_notification=send_bulk_notification)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_issues_bulk: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/bulk/issues/delete"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_issues_bulk")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_issues_bulk", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_issues_bulk",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue bulk operations
@mcp.tool()
async def list_bulk_editable_fields(
    issue_ids_or_keys: str = Field(..., alias="issueIdsOrKeys", description="One or more issue IDs or keys to determine which fields are eligible for bulk editing. Provide as a comma-separated list or array of values."),
    search_text: str | None = Field(None, alias="searchText", description="Optional text to filter the returned editable fields by name or description."),
) -> dict[str, Any]:
    """Retrieve a list of fields that are editable in bulk operations for the specified issues. Returns up to 50 fields per page, optionally filtered by search text."""

    # Construct request model with validation
    try:
        _request = _models.GetBulkEditableFieldsRequest(
            query=_models.GetBulkEditableFieldsRequestQuery(issue_ids_or_keys=issue_ids_or_keys, search_text=search_text)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_bulk_editable_fields: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/bulk/issues/fields"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_bulk_editable_fields")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_bulk_editable_fields", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_bulk_editable_fields",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue bulk operations
@mcp.tool()
async def bulk_edit_issues(
    edited_fields_input: _models.SubmitBulkEditBodyEditedFieldsInput = Field(..., alias="editedFieldsInput", description="An object containing the new values for each field being edited. The structure varies by field type, and field IDs must correspond to those specified in selectedActions."),
    selected_actions: list[str] = Field(..., alias="selectedActions", description="List of field IDs to be modified in the bulk edit operation. Each ID must match a field in editedFieldsInput and corresponds to a specific issue attribute being updated. Obtain available field IDs from the Bulk Edit Get Fields API."),
    selected_issue_ids_or_keys: list[str] = Field(..., alias="selectedIssueIdsOrKeys", description="List of issue IDs or keys to be edited, which may span multiple projects and issue types. Supports up to 1000 issues including subtasks per request."),
    send_bulk_notification: bool | None = Field(None, alias="sendBulkNotification", description="Whether to send bulk change notification emails to affected users about the updates. Defaults to true if not specified."),
) -> dict[str, Any]:
    """Simultaneously edit multiple issues across projects by specifying field values and target issues. Supports up to 1000 issues and 200 fields per request, with optional bulk notification to affected users."""

    # Construct request model with validation
    try:
        _request = _models.SubmitBulkEditRequest(
            body=_models.SubmitBulkEditRequestBody(edited_fields_input=edited_fields_input, selected_actions=selected_actions, selected_issue_ids_or_keys=selected_issue_ids_or_keys, send_bulk_notification=send_bulk_notification)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for bulk_edit_issues: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/bulk/issues/fields"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("bulk_edit_issues")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("bulk_edit_issues", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="bulk_edit_issues",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue bulk operations
@mcp.tool()
async def move_issues_bulk(
    send_bulk_notification: bool | None = Field(None, alias="sendBulkNotification", description="Whether to send a bulk notification email to users when issues are moved. Defaults to true if not specified."),
    target_to_sources_mapping: dict[str, _models.TargetToSourcesMapping] | None = Field(None, alias="targetToSourcesMapping", description="Mapping of destination configurations to source issues. Each mapping key combines destination project (ID or key), issue type ID, and optional parent (ID or key) in comma-separated format. The mapping defines field transformations and status mappings required for the move. Duplicate keys will be silently ignored without failing the operation."),
) -> dict[str, Any]:
    """Move multiple issues across projects in a single operation. Supports moving up to 1,000 issues (including subtasks) to a single destination project, issue type, and parent, with automatic field mapping and optional bulk notifications."""

    # Construct request model with validation
    try:
        _request = _models.SubmitBulkMoveRequest(
            body=_models.SubmitBulkMoveRequestBody(send_bulk_notification=send_bulk_notification, target_to_sources_mapping=target_to_sources_mapping)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for move_issues_bulk: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/bulk/issues/move"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("move_issues_bulk")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("move_issues_bulk", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="move_issues_bulk",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue bulk operations
@mcp.tool()
async def list_issue_transitions(issue_ids_or_keys: str = Field(..., alias="issueIdsOrKeys", description="Comma-separated list of issue IDs or keys to retrieve available transitions for. Supports up to 1,000 issues per request.")) -> dict[str, Any]:
    """Retrieve available transitions for specified issues that can be used in bulk transition operations. Returns transitions organized by workflow, including only those common across all specified issues that don't require additional field updates."""

    # Construct request model with validation
    try:
        _request = _models.GetAvailableTransitionsRequest(
            query=_models.GetAvailableTransitionsRequestQuery(issue_ids_or_keys=issue_ids_or_keys)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_issue_transitions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/bulk/issues/transition"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_issue_transitions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_issue_transitions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_issue_transitions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue bulk operations
@mcp.tool()
async def transition_issues_bulk(
    bulk_transition_inputs: list[_models.BulkTransitionSubmitInput] = Field(..., alias="bulkTransitionInputs", description="Array of issue transition objects, each containing an issue identifier and its corresponding transition ID. Issues must share compatible workflows for their specified transitions. Maximum of 1,000 issues per request."),
    send_bulk_notification: bool | None = Field(None, alias="sendBulkNotification", description="Whether to send bulk notification emails to affected users when issues are transitioned. Enabled by default."),
) -> dict[str, Any]:
    """Transition the status of multiple issues in a single operation. Submit up to 1,000 issues with their corresponding transition IDs to move them through your workflow states."""

    # Construct request model with validation
    try:
        _request = _models.SubmitBulkTransitionRequest(
            body=_models.SubmitBulkTransitionRequestBody(bulk_transition_inputs=bulk_transition_inputs, send_bulk_notification=send_bulk_notification)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for transition_issues_bulk: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/bulk/issues/transition"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("transition_issues_bulk")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("transition_issues_bulk", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="transition_issues_bulk",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue bulk operations
@mcp.tool()
async def unwatch_issues_bulk(selected_issue_ids_or_keys: list[str] = Field(..., alias="selectedIssueIdsOrKeys", description="List of issue IDs or keys to unwatch. You can include up to 1,000 issues from any projects or issue types in a single request.")) -> dict[str, Any]:
    """Remove your watch from multiple issues in a single operation. You can unwatch up to 1,000 issues across different projects and issue types."""

    # Construct request model with validation
    try:
        _request = _models.SubmitBulkUnwatchRequest(
            body=_models.SubmitBulkUnwatchRequestBody(selected_issue_ids_or_keys=selected_issue_ids_or_keys)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for unwatch_issues_bulk: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/bulk/issues/unwatch"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("unwatch_issues_bulk")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("unwatch_issues_bulk", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="unwatch_issues_bulk",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue bulk operations
@mcp.tool()
async def watch_issues(selected_issue_ids_or_keys: list[str] = Field(..., alias="selectedIssueIdsOrKeys", description="List of issue IDs or keys to watch, supporting up to 1,000 items per request. Issues can be from different projects and types. Provide either numeric IDs or string keys (e.g., PROJ-123).")) -> dict[str, Any]:
    """Add up to 1,000 issues to your watch list in a single bulk operation. Watched issues will appear in your notifications and dashboards."""

    # Construct request model with validation
    try:
        _request = _models.SubmitBulkWatchRequest(
            body=_models.SubmitBulkWatchRequestBody(selected_issue_ids_or_keys=selected_issue_ids_or_keys)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for watch_issues: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/bulk/issues/watch"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("watch_issues")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("watch_issues", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="watch_issues",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue bulk operations
@mcp.tool()
async def get_bulk_operation_progress(task_id: str = Field(..., alias="taskId", description="The unique identifier of the bulk operation task whose progress you want to check.")) -> dict[str, Any]:
    """Retrieve the current progress and status of a bulk issue operation. Returns real-time progress metrics while running, or final results upon completion. Task progress data is available for up to 14 days after creation."""

    # Construct request model with validation
    try:
        _request = _models.GetBulkOperationProgressRequest(
            path=_models.GetBulkOperationProgressRequestPath(task_id=task_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_bulk_operation_progress: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/bulk/queue/{taskId}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/bulk/queue/{taskId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_bulk_operation_progress")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_bulk_operation_progress", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_bulk_operation_progress",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issues
@mcp.tool()
async def fetch_issue_changelogs(
    issue_ids_or_keys: list[str] = Field(..., alias="issueIdsOrKeys", description="List of issue identifiers (IDs or keys) to fetch changelogs for. You can request changelogs for up to 1000 issues. At least one issue identifier is required.", min_length=1, max_length=1000),
    field_ids: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(None, alias="fieldIds", description="Optional list of field IDs to narrow changelog results to specific fields. You can filter by up to 10 fields.", min_length=0, max_length=10),
    max_results: str | None = Field(None, alias="maxResults", description="Maximum number of changelog items to return per page. Defaults to 1000 if not specified. Must be between 1 and 10000."),
) -> dict[str, Any]:
    """Retrieve change history for multiple issues in a paginated list, optionally filtered by specific fields. Results are sorted chronologically by changelog date and issue ID, starting from the oldest entries."""

    _max_results = _parse_int(max_results)

    # Construct request model with validation
    try:
        _request = _models.GetBulkChangelogsRequest(
            body=_models.GetBulkChangelogsRequestBody(field_ids=field_ids, issue_ids_or_keys=issue_ids_or_keys, max_results=_max_results)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for fetch_issue_changelogs: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/changelog/bulkfetch"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("fetch_issue_changelogs")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("fetch_issue_changelogs", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="fetch_issue_changelogs",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Classification levels
@mcp.tool()
async def list_classification_levels(
    status: Annotated[list[Literal["PUBLISHED", "ARCHIVED", "DRAFT"]], AfterValidator(_check_unique_items)] | None = Field(None, description="Optional filter to return only classification levels matching the specified statuses. Provide as an array of status values."),
    order_by: Literal["rank", "-rank", "+rank"] | None = Field(None, alias="orderBy", description="Optional field to sort results by rank. Use 'rank' for ascending order, '+rank' for ascending, or '-rank' for descending order. If not specified, results are returned unsorted."),
) -> dict[str, Any]:
    """Retrieves all available classification levels, optionally filtered by status and sorted by rank. No permissions are required to access this endpoint."""

    # Construct request model with validation
    try:
        _request = _models.GetAllUserDataClassificationLevelsRequest(
            query=_models.GetAllUserDataClassificationLevelsRequestQuery(status=status, order_by=order_by)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_classification_levels: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/classification-levels"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_classification_levels")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_classification_levels", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_classification_levels",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue comments
@mcp.tool()
async def list_comments(ids: Annotated[list[int], AfterValidator(_check_unique_items)] = Field(..., description="A list of comment IDs to retrieve. Specify up to 1000 IDs per request. Order is preserved in the response.")) -> dict[str, Any]:
    """Retrieve a paginated list of comments by their IDs. Returns comments where you have appropriate project browse permissions and any required issue-level security or visibility group/role permissions."""

    # Construct request model with validation
    try:
        _request = _models.GetCommentsByIdsRequest(
            body=_models.GetCommentsByIdsRequestBody(ids=ids)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_comments: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/comment/list"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_comments")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_comments", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_comments",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue comment properties
@mcp.tool()
async def list_comment_property_keys(comment_id: str = Field(..., alias="commentId", description="The unique identifier of the comment whose property keys you want to retrieve.")) -> dict[str, Any]:
    """Retrieves all property keys associated with a specific comment. Useful for discovering what custom properties have been set on a comment."""

    # Construct request model with validation
    try:
        _request = _models.GetCommentPropertyKeysRequest(
            path=_models.GetCommentPropertyKeysRequestPath(comment_id=comment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_comment_property_keys: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/comment/{commentId}/properties", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/comment/{commentId}/properties"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_comment_property_keys")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_comment_property_keys", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_comment_property_keys",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue comment properties
@mcp.tool()
async def get_comment_property(
    comment_id: str = Field(..., alias="commentId", description="The unique identifier of the comment from which to retrieve the property."),
    property_key: str = Field(..., alias="propertyKey", description="The identifier of the property whose value should be retrieved from the comment."),
) -> dict[str, Any]:
    """Retrieves the value of a specific property attached to a comment. Requires appropriate project and issue permissions, and respects any visibility restrictions on the comment."""

    # Construct request model with validation
    try:
        _request = _models.GetCommentPropertyRequest(
            path=_models.GetCommentPropertyRequestPath(comment_id=comment_id, property_key=property_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_comment_property: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/comment/{commentId}/properties/{propertyKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/comment/{commentId}/properties/{propertyKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_comment_property")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_comment_property", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_comment_property",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue comment properties
@mcp.tool()
async def delete_comment_property(
    comment_id: str = Field(..., alias="commentId", description="The unique identifier of the comment containing the property to delete."),
    property_key: str = Field(..., alias="propertyKey", description="The key identifying the custom property to remove from the comment."),
) -> dict[str, Any]:
    """Removes a custom property from a comment. Requires either Edit All Comments permission or Edit Own Comments permission if you created the comment."""

    # Construct request model with validation
    try:
        _request = _models.DeleteCommentPropertyRequest(
            path=_models.DeleteCommentPropertyRequestPath(comment_id=comment_id, property_key=property_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_comment_property: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/comment/{commentId}/properties/{propertyKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/comment/{commentId}/properties/{propertyKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_comment_property")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_comment_property", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_comment_property",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project components
@mcp.tool()
async def list_components(
    project_ids_or_keys: list[str] | None = Field(None, alias="projectIdsOrKeys", description="One or more project IDs or keys (case-sensitive) to filter components. If not provided, returns components from all accessible projects."),
    start_at: str | None = Field(None, alias="startAt", description="The zero-based index position to start returning results from, enabling pagination through large result sets. Defaults to 0 (first item)."),
    max_results: str | None = Field(None, alias="maxResults", description="The maximum number of components to return in a single page. Defaults to 50 items per page."),
    order_by: Literal["description", "-description", "+description", "name", "-name", "+name"] | None = Field(None, alias="orderBy", description="Sort results by component name or description. Use `name` or `description` for ascending order, prefix with `-` for descending order, or `+` for explicit ascending order."),
) -> dict[str, Any]:
    """Retrieve a paginated list of all components in specified projects, including global Compass components when applicable. Requires Browse Projects permission for the target project(s)."""

    _start_at = _parse_int(start_at)
    _max_results = _parse_int(max_results)

    # Construct request model with validation
    try:
        _request = _models.FindComponentsForProjectsRequest(
            query=_models.FindComponentsForProjectsRequestQuery(project_ids_or_keys=project_ids_or_keys, start_at=_start_at, max_results=_max_results, order_by=order_by)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_components: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/component"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_components")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_components", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_components",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project components
@mcp.tool()
async def create_component(
    assignee_type: Literal["PROJECT_DEFAULT", "COMPONENT_LEAD", "PROJECT_LEAD", "UNASSIGNED"] | None = Field(None, alias="assigneeType", description="Determines the default assignee for issues created with this component. Choose PROJECT_DEFAULT to use the project's default assignee, COMPONENT_LEAD to assign to the component lead, PROJECT_LEAD to assign to the project lead, or UNASSIGNED to leave issues unassigned. Defaults to PROJECT_DEFAULT if not specified."),
    description: str | None = Field(None, description="A brief text description of the component's purpose and scope. Optional and can be added or updated at any time."),
    name: str | None = Field(None, description="The unique name for the component in the project. Required when creating a component. Optional when updating a component. The maximum length is 255 characters."),
    project_id: str | None = Field(None, alias="projectId", description="The ID of the project the component is assigned to."),
) -> dict[str, Any]:
    """Create a new component in a project to serve as a container for organizing and grouping related issues. Requires project administration permissions."""

    _project_id = _parse_int(project_id)

    # Construct request model with validation
    try:
        _request = _models.CreateComponentRequest(
            body=_models.CreateComponentRequestBody(assignee_type=assignee_type, description=description, name=name, project_id=_project_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_component: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/component"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_component")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_component", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_component",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project components
@mcp.tool()
async def get_component(id_: str = Field(..., alias="id", description="The unique identifier of the component to retrieve.")) -> dict[str, Any]:
    """Retrieve detailed information about a specific component by its ID. Requires Browse projects permission for the project containing the component."""

    # Construct request model with validation
    try:
        _request = _models.GetComponentRequest(
            path=_models.GetComponentRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_component: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/component/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/component/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_component")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_component", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_component",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project components
@mcp.tool()
async def update_component(
    id_: str = Field(..., alias="id", description="The unique identifier of the component to update."),
    assignee_type: Literal["PROJECT_DEFAULT", "COMPONENT_LEAD", "PROJECT_LEAD", "UNASSIGNED"] | None = Field(None, alias="assigneeType", description="Determines who is assigned to issues created with this component. Choose from: PROJECT_DEFAULT (project's default assignee), COMPONENT_LEAD (component lead), PROJECT_LEAD (project lead), or UNASSIGNED (no assignee). Defaults to PROJECT_DEFAULT if not specified."),
    description: str | None = Field(None, description="A text description of the component's purpose and scope."),
) -> dict[str, Any]:
    """Updates an existing component in a project, overwriting any provided fields. Use an empty string for leadAccountId to remove the component lead."""

    # Construct request model with validation
    try:
        _request = _models.UpdateComponentRequest(
            path=_models.UpdateComponentRequestPath(id_=id_),
            body=_models.UpdateComponentRequestBody(assignee_type=assignee_type, description=description)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_component: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/component/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/component/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_component")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_component", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_component",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project components
@mcp.tool()
async def delete_component(
    id_: str = Field(..., alias="id", description="The unique identifier of the component to delete."),
    move_issues_to: str | None = Field(None, alias="moveIssuesTo", description="The unique identifier of a component to replace the deleted one. If not provided, issues associated with the deleted component will not be reassigned."),
) -> dict[str, Any]:
    """Deletes a component from a project. Optionally specify a replacement component to reassign any issues currently associated with the deleted component."""

    # Construct request model with validation
    try:
        _request = _models.DeleteComponentRequest(
            path=_models.DeleteComponentRequestPath(id_=id_),
            query=_models.DeleteComponentRequestQuery(move_issues_to=move_issues_to)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_component: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/component/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/component/{id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_component")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_component", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_component",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project components
@mcp.tool()
async def get_component_issue_counts(id_: str = Field(..., alias="id", description="The unique identifier of the component for which to retrieve issue counts.")) -> dict[str, Any]:
    """Retrieves the count of issues assigned to a specific component. This provides a summary of issue distribution for component management and reporting purposes."""

    # Construct request model with validation
    try:
        _request = _models.GetComponentRelatedIssuesRequest(
            path=_models.GetComponentRelatedIssuesRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_component_issue_counts: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/component/{id}/relatedIssueCounts", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/component/{id}/relatedIssueCounts"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_component_issue_counts")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_component_issue_counts", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_component_issue_counts",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue custom field options
@mcp.tool()
async def get_custom_field_option(id_: str = Field(..., alias="id", description="The unique identifier of the custom field option to retrieve.")) -> dict[str, Any]:
    """Retrieve a custom field option by ID, such as an option from a select list. This operation works only with options created in Jira or via the Issue custom field options API, and can be accessed anonymously with appropriate permissions."""

    # Construct request model with validation
    try:
        _request = _models.GetCustomFieldOptionRequest(
            path=_models.GetCustomFieldOptionRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_custom_field_option: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/customFieldOption/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/customFieldOption/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_custom_field_option")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_custom_field_option", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_custom_field_option",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Dashboards
@mcp.tool()
async def list_dashboards(
    filter_: Literal["my", "favourite"] | None = Field(None, alias="filter", description="Filter the dashboard list by ownership or favorite status. Use 'my' to show only dashboards you own, or 'favourite' to show only dashboards you've marked as favorites."),
    start_at: str | None = Field(None, alias="startAt", description="The starting position for pagination (zero-indexed). Use this to retrieve subsequent pages of results. Defaults to 0 if not specified."),
    max_results: str | None = Field(None, alias="maxResults", description="The maximum number of dashboards to return per page. Defaults to 20 if not specified."),
) -> dict[str, Any]:
    """Retrieve a list of dashboards owned by or shared with the user. Results can be filtered to show only favorite or owned dashboards, with support for pagination."""

    _start_at = _parse_int(start_at)
    _max_results = _parse_int(max_results)

    # Construct request model with validation
    try:
        _request = _models.GetAllDashboardsRequest(
            query=_models.GetAllDashboardsRequestQuery(filter_=filter_, start_at=_start_at, max_results=_max_results)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_dashboards: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/dashboard"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_dashboards")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_dashboards", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_dashboards",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Dashboards
@mcp.tool()
async def create_dashboard(
    edit_permissions: list[_models.SharePermission] = Field(..., alias="editPermissions", description="Required array specifying which users or groups can edit the dashboard and their permission levels."),
    name: str = Field(..., description="Required name for the dashboard. Used as the primary identifier and display label."),
    share_permissions: list[_models.SharePermission] = Field(..., alias="sharePermissions", description="Required array specifying which users or groups can view and access the dashboard and their permission levels."),
    description: str | None = Field(None, description="Optional text describing the dashboard's purpose and content."),
) -> dict[str, Any]:
    """Creates a new dashboard with specified name, description, and access permissions. The dashboard will be configured with edit and share permissions to control who can modify and access it."""

    # Construct request model with validation
    try:
        _request = _models.CreateDashboardRequest(
            body=_models.CreateDashboardRequestBody(description=description, edit_permissions=edit_permissions, name=name, share_permissions=share_permissions)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_dashboard: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/dashboard"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_dashboard")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_dashboard", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_dashboard",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Dashboards
@mcp.tool()
async def update_dashboards_bulk(
    action: Literal["changeOwner", "changePermission", "addPermission", "removePermission"] = Field(..., description="The type of bulk operation to perform: change the dashboard owner, modify permissions, add new permissions, or remove existing permissions."),
    entity_ids: Annotated[list[int], AfterValidator(_check_unique_items)] = Field(..., alias="entityIds", description="A list of dashboard IDs to be modified by the bulk operation. Maximum of 100 dashboard IDs per request."),
    change_owner_details: _models.BulkEditDashboardsBodyChangeOwnerDetails | None = Field(None, alias="changeOwnerDetails", description="Required when action is 'changeOwner'. Contains the details needed to transfer ownership of the dashboards to a new owner."),
    permission_details: _models.BulkEditDashboardsBodyPermissionDetails | None = Field(None, alias="permissionDetails", description="Required when action is 'changePermission', 'addPermission', or 'removePermission'. Specifies the permission settings to apply to the selected dashboards."),
) -> dict[str, Any]:
    """Perform bulk operations on multiple dashboards such as changing ownership or modifying permissions. You can update up to 100 dashboards in a single request. You must own the dashboards or have administrator privileges to make changes."""

    # Construct request model with validation
    try:
        _request = _models.BulkEditDashboardsRequest(
            body=_models.BulkEditDashboardsRequestBody(action=action, change_owner_details=change_owner_details, entity_ids=entity_ids, permission_details=permission_details)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_dashboards_bulk: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/dashboard/bulk/edit"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_dashboards_bulk")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_dashboards_bulk", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_dashboards_bulk",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Dashboards
@mcp.tool()
async def list_dashboard_gadgets() -> dict[str, Any]:
    """Retrieves a list of all available gadgets that can be added to dashboards. No authentication required."""

    # Extract parameters for API call
    _http_path = "/rest/api/3/dashboard/gadgets"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_dashboard_gadgets")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_dashboard_gadgets", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_dashboard_gadgets",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Dashboards
@mcp.tool()
async def search_dashboards(
    dashboard_name: str | None = Field(None, alias="dashboardName", description="Filter dashboards by name using case-insensitive partial matching."),
    project_id: str | None = Field(None, alias="projectId", description="Filter dashboards to only those shared with a specific project by its ID."),
    order_by: Literal["description", "-description", "+description", "favorite_count", "-favorite_count", "+favorite_count", "id", "-id", "+id", "is_favorite", "-is_favorite", "+is_favorite", "name", "-name", "+name", "owner", "-owner", "+owner"] | None = Field(None, alias="orderBy", description="Sort results by a field: description, favorite count, ID, favorite status, name, or owner. Prefix with `-` for descending order or `+` for ascending order. Defaults to sorting by name."),
    start_at: str | None = Field(None, alias="startAt", description="The starting position for pagination (zero-indexed). Defaults to 0."),
    max_results: str | None = Field(None, alias="maxResults", description="Maximum number of dashboards to return per page. Defaults to 50."),
    status: Literal["active", "archived", "deleted"] | None = Field(None, description="Filter dashboards by their status: active, archived, or deleted. Defaults to active."),
) -> dict[str, Any]:
    """Search for dashboards with optional filtering by name, project, and status. Returns a paginated list of dashboards accessible to the user based on ownership, group membership, project sharing, or public availability."""

    _project_id = _parse_int(project_id)
    _start_at = _parse_int(start_at)
    _max_results = _parse_int(max_results)

    # Construct request model with validation
    try:
        _request = _models.GetDashboardsPaginatedRequest(
            query=_models.GetDashboardsPaginatedRequestQuery(dashboard_name=dashboard_name, project_id=_project_id, order_by=order_by, start_at=_start_at, max_results=_max_results, status=status)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_dashboards: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/dashboard/search"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_dashboards")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_dashboards", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_dashboards",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Dashboards
@mcp.tool()
async def update_dashboard_gadget(
    dashboard_id: str = Field(..., alias="dashboardId", description="The unique identifier of the dashboard containing the gadget. Must be a positive integer."),
    gadget_id: str = Field(..., alias="gadgetId", description="The unique identifier of the gadget to update. Must be a positive integer."),
    color: str | None = Field(None, description="The visual color of the gadget. Choose from: blue, red, yellow, green, cyan, purple, gray, or white."),
    title: str | None = Field(None, description="The display title for the gadget shown on the dashboard."),
) -> dict[str, Any]:
    """Modify a gadget's appearance and position on a dashboard by updating its title, color, and layout properties."""

    _dashboard_id = _parse_int(dashboard_id)
    _gadget_id = _parse_int(gadget_id)

    # Construct request model with validation
    try:
        _request = _models.UpdateGadgetRequest(
            path=_models.UpdateGadgetRequestPath(dashboard_id=_dashboard_id, gadget_id=_gadget_id),
            body=_models.UpdateGadgetRequestBody(color=color, title=title)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_dashboard_gadget: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/dashboard/{dashboardId}/gadget/{gadgetId}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/dashboard/{dashboardId}/gadget/{gadgetId}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_dashboard_gadget")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_dashboard_gadget", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_dashboard_gadget",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Dashboards
@mcp.tool()
async def remove_gadget(
    dashboard_id: str = Field(..., alias="dashboardId", description="The unique identifier of the dashboard containing the gadget to remove. Must be a positive integer."),
    gadget_id: str = Field(..., alias="gadgetId", description="The unique identifier of the gadget to remove from the dashboard. Must be a positive integer."),
) -> dict[str, Any]:
    """Remove a gadget from a dashboard. When removed, other gadgets in the same column automatically shift up to fill the vacant position."""

    _dashboard_id = _parse_int(dashboard_id)
    _gadget_id = _parse_int(gadget_id)

    # Construct request model with validation
    try:
        _request = _models.RemoveGadgetRequest(
            path=_models.RemoveGadgetRequestPath(dashboard_id=_dashboard_id, gadget_id=_gadget_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_gadget: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/dashboard/{dashboardId}/gadget/{gadgetId}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/dashboard/{dashboardId}/gadget/{gadgetId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_gadget")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_gadget", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_gadget",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Dashboards
@mcp.tool()
async def list_dashboard_item_property_keys(
    dashboard_id: str = Field(..., alias="dashboardId", description="The unique identifier of the dashboard containing the item."),
    item_id: str = Field(..., alias="itemId", description="The unique identifier of the dashboard item whose property keys you want to retrieve."),
) -> dict[str, Any]:
    """Retrieves all property keys associated with a specific dashboard item. This operation allows you to discover what custom properties are available for a dashboard item without retrieving their values."""

    # Construct request model with validation
    try:
        _request = _models.GetDashboardItemPropertyKeysRequest(
            path=_models.GetDashboardItemPropertyKeysRequestPath(dashboard_id=dashboard_id, item_id=item_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_dashboard_item_property_keys: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/dashboard/{dashboardId}/items/{itemId}/properties", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/dashboard/{dashboardId}/items/{itemId}/properties"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_dashboard_item_property_keys")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_dashboard_item_property_keys", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_dashboard_item_property_keys",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Dashboards
@mcp.tool()
async def get_dashboard_item_property(
    dashboard_id: str = Field(..., alias="dashboardId", description="The unique identifier of the dashboard containing the item."),
    item_id: str = Field(..., alias="itemId", description="The unique identifier of the dashboard item (gadget) whose property you want to retrieve."),
    property_key: str = Field(..., alias="propertyKey", description="The key name of the property to retrieve from the dashboard item."),
) -> dict[str, Any]:
    """Retrieve a specific property value stored for a dashboard item. Dashboard items are gadgets that apps use to display user-specific information on dashboards, and properties store the item's content or configuration details."""

    # Construct request model with validation
    try:
        _request = _models.GetDashboardItemPropertyRequest(
            path=_models.GetDashboardItemPropertyRequestPath(dashboard_id=dashboard_id, item_id=item_id, property_key=property_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_dashboard_item_property: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/dashboard/{dashboardId}/items/{itemId}/properties/{propertyKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/dashboard/{dashboardId}/items/{itemId}/properties/{propertyKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_dashboard_item_property")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_dashboard_item_property", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_dashboard_item_property",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Dashboards
@mcp.tool()
async def remove_dashboard_item_property(
    dashboard_id: str = Field(..., alias="dashboardId", description="The unique identifier of the dashboard containing the item."),
    item_id: str = Field(..., alias="itemId", description="The unique identifier of the dashboard item whose property will be deleted."),
    property_key: str = Field(..., alias="propertyKey", description="The key identifying the specific property to delete from the dashboard item."),
) -> dict[str, Any]:
    """Removes a custom property from a dashboard item. Requires edit permission on the dashboard."""

    # Construct request model with validation
    try:
        _request = _models.DeleteDashboardItemPropertyRequest(
            path=_models.DeleteDashboardItemPropertyRequestPath(dashboard_id=dashboard_id, item_id=item_id, property_key=property_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_dashboard_item_property: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/dashboard/{dashboardId}/items/{itemId}/properties/{propertyKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/dashboard/{dashboardId}/items/{itemId}/properties/{propertyKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_dashboard_item_property")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_dashboard_item_property", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_dashboard_item_property",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Dashboards
@mcp.tool()
async def get_dashboard(id_: str = Field(..., alias="id", description="The unique identifier of the dashboard to retrieve.")) -> dict[str, Any]:
    """Retrieve a dashboard by its ID. The dashboard must be shared with the user, owned by the user, or the user must have Jira administration permissions to access it."""

    # Construct request model with validation
    try:
        _request = _models.GetDashboardRequest(
            path=_models.GetDashboardRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_dashboard: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/dashboard/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/dashboard/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_dashboard")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_dashboard", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_dashboard",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Dashboards
@mcp.tool()
async def update_dashboard(
    id_: str = Field(..., alias="id", description="The unique identifier of the dashboard to update."),
    edit_permissions: list[_models.SharePermission] = Field(..., alias="editPermissions", description="An array of permission objects that define who can edit the dashboard and their access level."),
    name: str = Field(..., description="The display name of the dashboard."),
    share_permissions: list[_models.SharePermission] = Field(..., alias="sharePermissions", description="An array of permission objects that define who can view and access the dashboard."),
    description: str | None = Field(None, description="A brief text description of the dashboard's purpose or content."),
) -> dict[str, Any]:
    """Update an existing dashboard by replacing all its details with the provided information. You must own the dashboard to update it."""

    # Construct request model with validation
    try:
        _request = _models.UpdateDashboardRequest(
            path=_models.UpdateDashboardRequestPath(id_=id_),
            body=_models.UpdateDashboardRequestBody(description=description, edit_permissions=edit_permissions, name=name, share_permissions=share_permissions)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_dashboard: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/dashboard/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/dashboard/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_dashboard")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_dashboard", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_dashboard",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Dashboards
@mcp.tool()
async def delete_dashboard(id_: str = Field(..., alias="id", description="The unique identifier of the dashboard to delete.")) -> dict[str, Any]:
    """Permanently deletes a dashboard. You must be the owner of the dashboard to delete it."""

    # Construct request model with validation
    try:
        _request = _models.DeleteDashboardRequest(
            path=_models.DeleteDashboardRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_dashboard: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/dashboard/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/dashboard/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_dashboard")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_dashboard", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_dashboard",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Dashboards
@mcp.tool()
async def duplicate_dashboard(
    id_: str = Field(..., alias="id", description="The unique identifier of the dashboard to copy."),
    edit_permissions: list[_models.SharePermission] = Field(..., alias="editPermissions", description="An array of user or group permissions that grants edit access to the dashboard. Specifies who can modify the dashboard after creation."),
    name: str = Field(..., description="The display name for the copied dashboard. This identifies the dashboard in lists and navigation."),
    share_permissions: list[_models.SharePermission] = Field(..., alias="sharePermissions", description="An array of user or group permissions that grants view and share access to the dashboard. Specifies who can view and redistribute access to the dashboard."),
    description: str | None = Field(None, description="Optional text describing the purpose or content of the copied dashboard."),
) -> dict[str, Any]:
    """Creates a copy of an existing dashboard with customizable name, description, and permissions. The source dashboard must be owned by or shared with the requesting user."""

    # Construct request model with validation
    try:
        _request = _models.CopyDashboardRequest(
            path=_models.CopyDashboardRequestPath(id_=id_),
            body=_models.CopyDashboardRequestBody(description=description, edit_permissions=edit_permissions, name=name, share_permissions=share_permissions)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for duplicate_dashboard: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/dashboard/{id}/copy", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/dashboard/{id}/copy"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("duplicate_dashboard")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("duplicate_dashboard", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="duplicate_dashboard",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issues
@mcp.tool()
async def list_events() -> dict[str, Any]:
    """Retrieve all issue events from your Jira instance. Requires Administer Jira global permission to access."""

    # Extract parameters for API call
    _http_path = "/rest/api/3/events"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_events")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_events", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_events",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Jira expressions
@mcp.tool()
async def evaluate_jira_expression(
    expression: str = Field(..., description="The Jira expression to evaluate as a string. Can reference context variables and perform operations like field extraction, filtering, and mapping (e.g., extracting issue keys, types, and linked issue IDs)."),
    context: _models.EvaluateJsisJiraExpressionBodyContext | None = Field(None, description="Optional context object that defines variables available to the expression, including built-in contexts (user, issue, issues, project, sprint, board, serviceDesk, customerRequest) and custom variables (user IDs, issue keys, JSON objects, or lists). Omit if using only automatic contexts."),
) -> dict[str, Any]:
    """Evaluates a Jira expression and returns its computed value using the enhanced search API for better performance and scalability. Supports flexible data retrieval with access to issues, projects, sprints, boards, and custom context variables."""

    # Construct request model with validation
    try:
        _request = _models.EvaluateJsisJiraExpressionRequest(
            body=_models.EvaluateJsisJiraExpressionRequestBody(context=context, expression=expression)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for evaluate_jira_expression: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/expression/evaluate"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("evaluate_jira_expression")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("evaluate_jira_expression", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="evaluate_jira_expression",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue fields
@mcp.tool()
async def list_fields() -> dict[str, Any]:
    """Retrieve all available issue fields in Jira, including system and custom fields. Returns fields based on global settings, screen configuration, and your project access permissions."""

    # Extract parameters for API call
    _http_path = "/rest/api/3/field"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_fields")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_fields", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_fields",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue fields
@mcp.tool()
async def list_fields_search(
    start_at: str | None = Field(None, alias="startAt", description="The starting position for pagination (zero-indexed). Defaults to 0 if not specified."),
    max_results: str | None = Field(None, alias="maxResults", description="The number of fields to return per page. Defaults to 50 if not specified."),
    order_by: Literal["contextsCount", "-contextsCount", "+contextsCount", "lastUsed", "-lastUsed", "+lastUsed", "name", "-name", "+name", "screensCount", "-screensCount", "+screensCount", "projectsCount", "-projectsCount", "+projectsCount"] | None = Field(None, alias="orderBy", description="Sort the results by field attribute: contextsCount (number of related contexts), lastUsed (date of last value change), name (field name), screensCount (number of related screens), or projectsCount (number of related projects). Prefix with '-' for descending order or '+' for ascending order."),
    project_ids: Annotated[list[int], AfterValidator(_check_unique_items)] | None = Field(None, alias="projectIds", description="Filter results to fields belonging only to the specified project IDs. Fields from projects you lack access to will be excluded. Provide as a comma-separated list of project identifiers."),
) -> dict[str, Any]:
    """Retrieve a paginated list of Jira fields, optionally filtered by field IDs, search query, or project IDs. Supports sorting by various field attributes and can be restricted to custom fields only."""

    _start_at = _parse_int(start_at)
    _max_results = _parse_int(max_results)

    # Construct request model with validation
    try:
        _request = _models.GetFieldsPaginatedRequest(
            query=_models.GetFieldsPaginatedRequestQuery(start_at=_start_at, max_results=_max_results, order_by=order_by, project_ids=project_ids)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_fields_search: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/field/search"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_fields_search")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_fields_search", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_fields_search",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue fields
@mcp.tool()
async def list_trashed_fields(
    start_at: str | None = Field(None, alias="startAt", description="The starting position for pagination (zero-indexed). Use this to retrieve subsequent pages of results. Defaults to 0."),
    max_results: str | None = Field(None, alias="maxResults", description="The number of fields to return per page. Defaults to 50 items per page."),
    order_by: str | None = Field(None, alias="orderBy", description="Sort the results by field name, the date the field was moved to trash, or the planned deletion date."),
) -> dict[str, Any]:
    """Retrieve a paginated list of custom fields that have been moved to trash. Results can be filtered by field name or description, and sorted by name, trash date, or planned deletion date. Requires Administer Jira global permission."""

    _start_at = _parse_int(start_at)
    _max_results = _parse_int(max_results)

    # Construct request model with validation
    try:
        _request = _models.GetTrashedFieldsPaginatedRequest(
            query=_models.GetTrashedFieldsPaginatedRequestQuery(start_at=_start_at, max_results=_max_results, order_by=order_by)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_trashed_fields: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/field/search/trashed"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_trashed_fields")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_trashed_fields", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_trashed_fields",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue custom field contexts
@mcp.tool()
async def list_custom_field_context_issue_type_mappings(
    field_id: str = Field(..., alias="fieldId", description="The unique identifier of the custom field for which to retrieve issue type mappings."),
    context_id: list[int] | None = Field(None, alias="contextId", description="Filter results to specific contexts by providing one or more context IDs. Omit to retrieve mappings for all contexts."),
    start_at: str | None = Field(None, alias="startAt", description="The zero-based index position to start returning results from, enabling pagination through large result sets."),
    max_results: str | None = Field(None, alias="maxResults", description="The maximum number of mappings to return per page. Defaults to 50 items if not specified."),
) -> dict[str, Any]:
    """Retrieve a paginated list of issue type mappings for a custom field across specified contexts. Results are ordered by context ID first, then by issue type ID."""

    _start_at = _parse_int(start_at)
    _max_results = _parse_int(max_results)

    # Construct request model with validation
    try:
        _request = _models.GetIssueTypeMappingsForContextsRequest(
            path=_models.GetIssueTypeMappingsForContextsRequestPath(field_id=field_id),
            query=_models.GetIssueTypeMappingsForContextsRequestQuery(context_id=context_id, start_at=_start_at, max_results=_max_results)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_custom_field_context_issue_type_mappings: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/field/{fieldId}/context/issuetypemapping", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/field/{fieldId}/context/issuetypemapping"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_custom_field_context_issue_type_mappings")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_custom_field_context_issue_type_mappings", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_custom_field_context_issue_type_mappings",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue custom field options
@mcp.tool()
async def list_custom_field_options(
    field_id: str = Field(..., alias="fieldId", description="The unique identifier of the custom field."),
    context_id: str = Field(..., alias="contextId", description="The unique identifier of the context associated with the custom field."),
    option_id: str | None = Field(None, alias="optionId", description="Filter results to a specific option by its unique identifier."),
    only_options: bool | None = Field(None, alias="onlyOptions", description="When enabled, returns only the direct options without cascading options."),
    start_at: str | None = Field(None, alias="startAt", description="The zero-based index position to start returning results from for pagination."),
    max_results: str | None = Field(None, alias="maxResults", description="The maximum number of options to return per page, up to 100 items."),
) -> dict[str, Any]:
    """Retrieve a paginated list of custom field options for a specific context, including both regular and cascading options in display order. Requires Jira administration or workflow edit permissions."""

    _context_id = _parse_int(context_id)
    _option_id = _parse_int(option_id)
    _start_at = _parse_int(start_at)
    _max_results = _parse_int(max_results)

    # Construct request model with validation
    try:
        _request = _models.GetOptionsForContextRequest(
            path=_models.GetOptionsForContextRequestPath(field_id=field_id, context_id=_context_id),
            query=_models.GetOptionsForContextRequestQuery(option_id=_option_id, only_options=only_options, start_at=_start_at, max_results=_max_results)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_custom_field_options: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/field/{fieldId}/context/{contextId}/option", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/field/{fieldId}/context/{contextId}/option"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_custom_field_options")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_custom_field_options", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_custom_field_options",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue custom field options
@mcp.tool()
async def create_custom_field_options(
    field_id: str = Field(..., alias="fieldId", description="The unique identifier of the custom field to which options will be added."),
    context_id: str = Field(..., alias="contextId", description="The unique identifier of the field context where options will be created. Must be a positive integer."),
    options: list[_models.CustomFieldOptionCreate] | None = Field(None, description="An array of option objects to create. Each option defines a select list choice, and for cascading select fields, can include nested cascading options. Order is preserved as provided."),
) -> dict[str, Any]:
    """Create options for a custom select field within a specific context. Supports cascading options for cascading select fields, with a maximum of 1000 options per request and 10000 total options per field."""

    _context_id = _parse_int(context_id)

    # Construct request model with validation
    try:
        _request = _models.CreateCustomFieldOptionRequest(
            path=_models.CreateCustomFieldOptionRequestPath(field_id=field_id, context_id=_context_id),
            body=_models.CreateCustomFieldOptionRequestBody(options=options)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_custom_field_options: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/field/{fieldId}/context/{contextId}/option", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/field/{fieldId}/context/{contextId}/option"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_custom_field_options")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_custom_field_options", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_custom_field_options",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue custom field options
@mcp.tool()
async def update_custom_field_options(
    field_id: str = Field(..., alias="fieldId", description="The unique identifier of the custom field to update options for."),
    context_id: str = Field(..., alias="contextId", description="The unique identifier of the context where the custom field options apply. Must be a valid 64-bit integer."),
    options: list[_models.CustomFieldOptionUpdate] | None = Field(None, description="An array of custom field option objects to update. Each object should contain the option details to be modified. If any option is not found, the entire operation fails and no options are updated."),
) -> dict[str, Any]:
    """Updates the available options for a custom field within a specific context. Only options with changed values are updated; unchanged options are ignored in the response. This operation works exclusively with select list options created in Jira or via the Issue custom field options API, not with options created by Connect apps."""

    _context_id = _parse_int(context_id)

    # Construct request model with validation
    try:
        _request = _models.UpdateCustomFieldOptionRequest(
            path=_models.UpdateCustomFieldOptionRequestPath(field_id=field_id, context_id=_context_id),
            body=_models.UpdateCustomFieldOptionRequestBody(options=options)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_custom_field_options: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/field/{fieldId}/context/{contextId}/option", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/field/{fieldId}/context/{contextId}/option"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_custom_field_options")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_custom_field_options", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_custom_field_options",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue custom field options
@mcp.tool()
async def reorder_custom_field_options(
    field_id: str = Field(..., alias="fieldId", description="The unique identifier of the custom field containing the options to reorder."),
    context_id: str = Field(..., alias="contextId", description="The unique identifier of the context in which the custom field options are defined."),
    custom_field_option_ids: list[str] = Field(..., alias="customFieldOptionIds", description="An ordered list of custom field option IDs that defines their new sequence. All IDs must be either custom field options or cascading options, but not a mix of both types."),
    after: str | None = Field(None, description="The ID of the custom field option or cascading option to place the moved options after. Required if `position` isn't provided."),
    position: Literal["First", "Last"] | None = Field(None, description="The position the custom field options should be moved to. Required if `after` isn't provided."),
) -> dict[str, Any]:
    """Reorder custom field options within a specific context. Rearranges the display order of custom field options or cascading options by specifying their desired sequence."""

    _context_id = _parse_int(context_id)

    # Construct request model with validation
    try:
        _request = _models.ReorderCustomFieldOptionsRequest(
            path=_models.ReorderCustomFieldOptionsRequestPath(field_id=field_id, context_id=_context_id),
            body=_models.ReorderCustomFieldOptionsRequestBody(custom_field_option_ids=custom_field_option_ids, after=after, position=position)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for reorder_custom_field_options: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/field/{fieldId}/context/{contextId}/option/move", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/field/{fieldId}/context/{contextId}/option/move"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("reorder_custom_field_options")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("reorder_custom_field_options", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="reorder_custom_field_options",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue custom field options
@mcp.tool()
async def delete_custom_field_option(
    field_id: str = Field(..., alias="fieldId", description="The unique identifier of the custom field containing the option to delete."),
    context_id: str = Field(..., alias="contextId", description="The unique identifier of the context from which the option should be deleted. This is a numeric ID."),
    option_id: str = Field(..., alias="optionId", description="The unique identifier of the option to delete. This is a numeric ID."),
) -> dict[str, Any]:
    """Deletes a custom field option from a specific context. Options with cascading options cannot be deleted until their cascading options are removed first."""

    _context_id = _parse_int(context_id)
    _option_id = _parse_int(option_id)

    # Construct request model with validation
    try:
        _request = _models.DeleteCustomFieldOptionRequest(
            path=_models.DeleteCustomFieldOptionRequestPath(field_id=field_id, context_id=_context_id, option_id=_option_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_custom_field_option: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/field/{fieldId}/context/{contextId}/option/{optionId}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/field/{fieldId}/context/{contextId}/option/{optionId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_custom_field_option")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_custom_field_option", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_custom_field_option",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Screens
@mcp.tool()
async def list_field_screens(
    field_id: str = Field(..., alias="fieldId", description="The unique identifier of the field to retrieve screens for."),
    start_at: str | None = Field(None, alias="startAt", description="The zero-based index where the paginated results should start. Defaults to 0 if not specified."),
    max_results: str | None = Field(None, alias="maxResults", description="The maximum number of screens to return per page. Defaults to 100 if not specified."),
) -> dict[str, Any]:
    """Retrieve a paginated list of all screens where a specific field is used. Requires Jira administrator permissions."""

    _start_at = _parse_int(start_at)
    _max_results = _parse_int(max_results)

    # Construct request model with validation
    try:
        _request = _models.GetScreensForFieldRequest(
            path=_models.GetScreensForFieldRequestPath(field_id=field_id),
            query=_models.GetScreensForFieldRequestQuery(start_at=_start_at, max_results=_max_results)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_field_screens: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/field/{fieldId}/screens", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/field/{fieldId}/screens"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_field_screens")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_field_screens", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_field_screens",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue custom field options (apps)
@mcp.tool()
async def list_field_options(
    field_key: str = Field(..., alias="fieldKey", description="The field key in the format app-key__field-key (e.g., example-add-on__example-issue-field). Find this value in the app's plugin descriptor or by running the Get fields operation."),
    start_at: str | None = Field(None, alias="startAt", description="The starting position for pagination, where 0 is the first item. Defaults to 0 if not specified."),
    max_results: str | None = Field(None, alias="maxResults", description="The maximum number of options to return per page. Defaults to 50 if not specified."),
) -> dict[str, Any]:
    """Retrieve a paginated list of all options available for a Connect app-provided select list issue field. This operation only works with field options added by Connect apps, not those created directly in Jira."""

    _start_at = _parse_int(start_at)
    _max_results = _parse_int(max_results)

    # Construct request model with validation
    try:
        _request = _models.GetAllIssueFieldOptionsRequest(
            path=_models.GetAllIssueFieldOptionsRequestPath(field_key=field_key),
            query=_models.GetAllIssueFieldOptionsRequestQuery(start_at=_start_at, max_results=_max_results)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_field_options: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/field/{fieldKey}/option", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/field/{fieldKey}/option"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_field_options")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_field_options", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_field_options",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue custom field options (apps)
@mcp.tool()
async def add_field_option(
    field_key: str = Field(..., alias="fieldKey", description="The unique identifier for the Connect app's custom field, formatted as app-key__field-key (e.g., example-add-on__example-issue-field). Find this value in the app's plugin descriptor or by calling Get fields."),
    value: str = Field(..., description="The display name for the new option as it will appear in Jira. This is the user-facing label for the select list option."),
) -> dict[str, Any]:
    """Add a new option to a Connect app's select list issue field. Each field supports up to 10,000 options, and requires Jira administrator permissions."""

    # Construct request model with validation
    try:
        _request = _models.CreateIssueFieldOptionRequest(
            path=_models.CreateIssueFieldOptionRequestPath(field_key=field_key),
            body=_models.CreateIssueFieldOptionRequestBody(value=value)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_field_option: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/field/{fieldKey}/option", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/field/{fieldKey}/option"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_field_option")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_field_option", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_field_option",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue custom field options (apps)
@mcp.tool()
async def list_field_option_suggestions(
    field_key: str = Field(..., alias="fieldKey", description="The field key in the format $(app-key)__$(field-key), such as example-add-on__example-issue-field. Find this value in the app's plugin descriptor or by calling Get fields."),
    start_at: str | None = Field(None, alias="startAt", description="The starting position for pagination, where 0 is the first item. Use this to retrieve subsequent pages of results."),
    max_results: str | None = Field(None, alias="maxResults", description="The maximum number of options to return per page. Defaults to 50 items."),
    project_id: str | None = Field(None, alias="projectId", description="Optionally filter results to show only options available in a specific project by providing its numeric ID."),
) -> dict[str, Any]:
    """Retrieve a paginated list of selectable options for a Connect app custom issue field that the user can view and select. This operation only works with field options added by Connect apps, not those created natively in Jira."""

    _start_at = _parse_int(start_at)
    _max_results = _parse_int(max_results)
    _project_id = _parse_int(project_id)

    # Construct request model with validation
    try:
        _request = _models.GetSelectableIssueFieldOptionsRequest(
            path=_models.GetSelectableIssueFieldOptionsRequestPath(field_key=field_key),
            query=_models.GetSelectableIssueFieldOptionsRequestQuery(start_at=_start_at, max_results=_max_results, project_id=_project_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_field_option_suggestions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/field/{fieldKey}/option/suggestions/edit", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/field/{fieldKey}/option/suggestions/edit"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_field_option_suggestions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_field_option_suggestions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_field_option_suggestions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue custom field options (apps)
@mcp.tool()
async def search_field_options(
    field_key: str = Field(..., alias="fieldKey", description="The field identifier in the format appKey__fieldKey (e.g., example-add-on__example-issue-field). Retrieve this value from the app's plugin descriptor or by calling Get fields."),
    start_at: str | None = Field(None, alias="startAt", description="The starting position for pagination (0-based index). Use this to retrieve subsequent pages of results."),
    max_results: str | None = Field(None, alias="maxResults", description="Maximum number of options to return per page. Defaults to 50 if not specified."),
    project_id: str | None = Field(None, alias="projectId", description="Restrict results to options available in a specific project. When omitted, returns options available across all projects."),
) -> dict[str, Any]:
    """Search for visible options in a Connect app custom select list field. Returns paginated results filtered by user permissions and optionally by project."""

    _start_at = _parse_int(start_at)
    _max_results = _parse_int(max_results)
    _project_id = _parse_int(project_id)

    # Construct request model with validation
    try:
        _request = _models.GetVisibleIssueFieldOptionsRequest(
            path=_models.GetVisibleIssueFieldOptionsRequestPath(field_key=field_key),
            query=_models.GetVisibleIssueFieldOptionsRequestQuery(start_at=_start_at, max_results=_max_results, project_id=_project_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_field_options: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/field/{fieldKey}/option/suggestions/search", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/field/{fieldKey}/option/suggestions/search"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_field_options")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_field_options", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_field_options",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue custom field options (apps)
@mcp.tool()
async def get_field_option(
    field_key: str = Field(..., alias="fieldKey", description="The field key in the format app-key__field-key (e.g., example-add-on__example-issue-field). Find this value in the app's plugin descriptor or by running Get fields to retrieve the key from field details."),
    option_id: str = Field(..., alias="optionId", description="The numeric ID of the option to retrieve. Must be a valid 64-bit integer."),
) -> dict[str, Any]:
    """Retrieve a specific option from a Connect app-provided select list issue field. This operation only works with field options added by Connect apps, not those created directly in Jira."""

    _option_id = _parse_int(option_id)

    # Construct request model with validation
    try:
        _request = _models.GetIssueFieldOptionRequest(
            path=_models.GetIssueFieldOptionRequestPath(field_key=field_key, option_id=_option_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_field_option: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/field/{fieldKey}/option/{optionId}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/field/{fieldKey}/option/{optionId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_field_option")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_field_option", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_field_option",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue custom field options (apps)
@mcp.tool()
async def replace_field_option(
    field_key: str = Field(..., alias="fieldKey", description="The field key in the format app-key__field-key (e.g., example-add-on__example-issue-field). Retrieve this value from the app's plugin descriptor or by calling Get fields."),
    option_id: str = Field(..., alias="optionId", description="The numeric ID of the select-list option to be deselected from all issues."),
    replace_with: str | None = Field(None, alias="replaceWith", description="The numeric ID of the option that will replace the deselected option. If not provided, the option is simply removed without replacement."),
    jql: str | None = Field(None, description="A JQL query that limits the operation to a specific set of issues (e.g., project=10000). If not provided, the operation applies to all issues with the option selected."),
    override_editable_flag: bool | None = Field(None, alias="overrideEditableFlag", description="Whether to override screen security to allow editing of uneditable fields. Only available to Connect and Forge app users with Administer Jira permission. Defaults to false."),
) -> dict[str, Any]:
    """Deselects a custom field select-list option from all issues where it is selected, optionally replacing it with a different option. This asynchronous operation works only with options added by Connect or Forge apps and can be scoped to specific issues using JQL."""

    _option_id = _parse_int(option_id)
    _replace_with = _parse_int(replace_with)

    # Construct request model with validation
    try:
        _request = _models.ReplaceIssueFieldOptionRequest(
            path=_models.ReplaceIssueFieldOptionRequestPath(field_key=field_key, option_id=_option_id),
            query=_models.ReplaceIssueFieldOptionRequestQuery(replace_with=_replace_with, jql=jql, override_editable_flag=override_editable_flag)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for replace_field_option: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/field/{fieldKey}/option/{optionId}/issue", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/field/{fieldKey}/option/{optionId}/issue"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("replace_field_option")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("replace_field_option", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="replace_field_option",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue fields
@mcp.tool()
async def delete_custom_field(id_: str = Field(..., alias="id", description="The unique identifier of the custom field to delete.")) -> dict[str, Any]:
    """Permanently deletes a custom field from Jira, whether it's in the trash or active. This is an asynchronous operation; use the location link in the response to track the deletion task status."""

    # Construct request model with validation
    try:
        _request = _models.DeleteCustomFieldRequest(
            path=_models.DeleteCustomFieldRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_custom_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/field/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/field/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_custom_field")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_custom_field", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_custom_field",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue fields
@mcp.tool()
async def restore_custom_field(id_: str = Field(..., alias="id", description="The unique identifier of the custom field to restore from trash.")) -> dict[str, Any]:
    """Restore a custom field from trash back to active use. Requires Administer Jira global permission."""

    # Construct request model with validation
    try:
        _request = _models.RestoreCustomFieldRequest(
            path=_models.RestoreCustomFieldRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for restore_custom_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/field/{id}/restore", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/field/{id}/restore"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("restore_custom_field")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("restore_custom_field", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="restore_custom_field",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue fields
@mcp.tool()
async def move_custom_field_to_trash(id_: str = Field(..., alias="id", description="The unique identifier of the custom field to move to trash.")) -> dict[str, Any]:
    """Move a custom field to trash, making it unavailable for use while preserving the option to permanently delete it later. Requires Administer Jira global permission."""

    # Construct request model with validation
    try:
        _request = _models.TrashCustomFieldRequest(
            path=_models.TrashCustomFieldRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for move_custom_field_to_trash: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/field/{id}/trash", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/field/{id}/trash"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("move_custom_field_to_trash")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("move_custom_field_to_trash", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="move_custom_field_to_trash",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Filters
@mcp.tool()
async def create_filter(
    name: str = Field(..., description="The display name for the filter. Must be unique across all filters in the Jira instance."),
    description: str | None = Field(None, description="A brief explanation of the filter's purpose and usage."),
    edit_permissions: list[_models.SharePermission] | None = Field(None, alias="editPermissions", description="Groups and projects that are granted permission to edit this filter. Specify as an array of group and project objects."),
    favourite: bool | None = Field(None, description="Whether to automatically mark this filter as a favorite for the current user."),
    jql: str | None = Field(None, description="The JQL (Jira Query Language) query that defines which issues the filter returns. For example: project = SSP AND issuetype = Bug."),
    share_permissions: list[_models.SharePermission] | None = Field(None, alias="sharePermissions", description="Groups and projects with whom this filter is shared. Specify as an array of group and project objects to control visibility and access."),
) -> dict[str, Any]:
    """Creates a new filter with a JQL query and optional sharing settings. The filter is shared according to default scope settings and is not automatically marked as a favorite."""

    # Construct request model with validation
    try:
        _request = _models.CreateFilterRequest(
            body=_models.CreateFilterRequestBody(description=description, edit_permissions=edit_permissions, favourite=favourite, jql=jql, name=name, share_permissions=share_permissions)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_filter: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/filter"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_filter")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_filter", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_filter",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Filter sharing
@mcp.tool()
async def get_default_share_scope() -> dict[str, Any]:
    """Retrieves the default sharing settings that apply to new filters and dashboards created by the authenticated user in Jira."""

    # Extract parameters for API call
    _http_path = "/rest/api/3/filter/defaultShareScope"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_default_share_scope")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_default_share_scope", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_default_share_scope",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Filters
@mcp.tool()
async def list_favorite_filters() -> dict[str, Any]:
    """Retrieves all visible favorite filters for the authenticated user. A filter is visible only if it's owned by the user, shared with a group they belong to, shared with a private project they can browse, shared with a public project, or shared publicly."""

    # Extract parameters for API call
    _http_path = "/rest/api/3/filter/favourite"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_favorite_filters")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_favorite_filters", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_favorite_filters",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Filters
@mcp.tool()
async def list_my_filters(include_favourites: bool | None = Field(None, alias="includeFavourites", description="When enabled, includes the user's favorite filters in the response alongside owned filters. Disabled by default.")) -> dict[str, Any]:
    """Retrieve filters owned by the authenticated user, with optional inclusion of their favorite filters. Favorite filters are only visible if they are owned by the user, shared with a group the user belongs to, shared with a private project the user can browse, shared with a public project, or shared publicly."""

    # Construct request model with validation
    try:
        _request = _models.GetMyFiltersRequest(
            query=_models.GetMyFiltersRequestQuery(include_favourites=include_favourites)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_my_filters: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/filter/my"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_my_filters")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_my_filters", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_my_filters",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Filters
@mcp.tool()
async def search_filters(
    filter_name: str | None = Field(None, alias="filterName", description="Partial filter name to search for using case-insensitive matching. Matching behavior depends on the isSubstringMatch parameter."),
    project_id: str | None = Field(None, alias="projectId", description="Filter results to only those shared with a specific project by its ID."),
    order_by: Literal["description", "-description", "+description", "favourite_count", "-favourite_count", "+favourite_count", "id", "-id", "+id", "is_favourite", "-is_favourite", "+is_favourite", "name", "-name", "+name", "owner", "-owner", "+owner", "is_shared", "-is_shared", "+is_shared"] | None = Field(None, alias="orderBy", description="Sort results by a field: name, description, ID, owner, favorite count, whether marked as favorite, or whether shared. Prefix with '-' for descending or '+' for ascending order."),
    start_at: str | None = Field(None, alias="startAt", description="Zero-based index for pagination, indicating which result to start from. Defaults to 0 for the first page."),
    max_results: str | None = Field(None, alias="maxResults", description="Maximum number of filters to return per page. Defaults to 50 results."),
    is_substring_match: bool | None = Field(None, alias="isSubstringMatch", description="When true, performs case-insensitive substring matching on the filter name. When false, uses full text search syntax. Defaults to false."),
) -> dict[str, Any]:
    """Search for filters with pagination support, returning filters based on ownership, sharing permissions, and optional search criteria. Only filters accessible to the authenticated user are returned."""

    _project_id = _parse_int(project_id)
    _start_at = _parse_int(start_at)
    _max_results = _parse_int(max_results)

    # Construct request model with validation
    try:
        _request = _models.GetFiltersPaginatedRequest(
            query=_models.GetFiltersPaginatedRequestQuery(filter_name=filter_name, project_id=_project_id, order_by=order_by, start_at=_start_at, max_results=_max_results, is_substring_match=is_substring_match)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_filters: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/filter/search"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_filters")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_filters", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_filters",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Filters
@mcp.tool()
async def get_filter(id_: str = Field(..., alias="id", description="The unique identifier of the filter to retrieve, specified as a 64-bit integer.")) -> dict[str, Any]:
    """Retrieve a filter by its ID. The filter is only returned if you have access to it through ownership, group sharing, project sharing, or public sharing."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.GetFilterRequest(
            path=_models.GetFilterRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_filter: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/filter/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/filter/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_filter")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_filter", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_filter",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Filters
@mcp.tool()
async def update_filter(
    id_: str = Field(..., alias="id", description="The unique identifier of the filter to update. Must be a valid 64-bit integer."),
    name: str = Field(..., description="The display name for the filter. Must be unique across all filters you own."),
    description: str | None = Field(None, description="A text description explaining the filter's purpose or usage."),
    edit_permissions: list[_models.SharePermission] | None = Field(None, alias="editPermissions", description="An array of groups and projects that are granted permission to edit this filter. Order and format are determined by the API's permission structure."),
    favourite: bool | None = Field(None, description="A boolean flag indicating whether this filter should be marked as a favorite in the user's filter list."),
    jql: str | None = Field(None, description="The JQL (Jira Query Language) query string that defines which issues this filter returns. For example: project = SSP AND issuetype = Bug."),
    share_permissions: list[_models.SharePermission] | None = Field(None, alias="sharePermissions", description="An array of groups and projects with whom this filter is shared. Order and format are determined by the API's permission structure."),
) -> dict[str, Any]:
    """Update an existing filter's configuration including name, description, JQL query, and sharing settings. You must own the filter to make changes."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.UpdateFilterRequest(
            path=_models.UpdateFilterRequestPath(id_=_id_),
            body=_models.UpdateFilterRequestBody(description=description, edit_permissions=edit_permissions, favourite=favourite, jql=jql, name=name, share_permissions=share_permissions)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_filter: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/filter/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/filter/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_filter")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_filter", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_filter",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Filters
@mcp.tool()
async def delete_filter(id_: str = Field(..., alias="id", description="The unique identifier of the filter to delete, specified as a 64-bit integer.")) -> dict[str, Any]:
    """Permanently delete a filter from Jira. Only the filter creator or users with Administer Jira permission can delete filters."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.DeleteFilterRequest(
            path=_models.DeleteFilterRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_filter: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/filter/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/filter/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_filter")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_filter", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_filter",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Filters
@mcp.tool()
async def list_filter_columns(id_: str = Field(..., alias="id", description="The unique identifier of the filter. Must be a valid 64-bit integer.")) -> dict[str, Any]:
    """Retrieves the columns configured for a filter, which are used when viewing filter results in List View with Columns set to Filter. Column details are only returned for filters you own, filters shared with your groups, or filters shared with projects you have access to."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.GetColumnsRequest(
            path=_models.GetColumnsRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_filter_columns: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/filter/{id}/columns", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/filter/{id}/columns"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_filter_columns")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_filter_columns", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_filter_columns",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Filters
@mcp.tool()
async def add_filter_to_favorites(id_: str = Field(..., alias="id", description="The unique identifier of the filter to add as a favorite. Must be a positive integer.")) -> dict[str, Any]:
    """Mark a filter as a favorite for the current user. You can only favorite filters you own, filters shared with your groups or projects, or publicly shared filters."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.SetFavouriteForFilterRequest(
            path=_models.SetFavouriteForFilterRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_filter_to_favorites: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/filter/{id}/favourite", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/filter/{id}/favourite"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_filter_to_favorites")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_filter_to_favorites", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_filter_to_favorites",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Filters
@mcp.tool()
async def remove_filter_favorite(id_: str = Field(..., alias="id", description="The unique identifier of the filter to remove from favorites, specified as a 64-bit integer.")) -> dict[str, Any]:
    """Remove a filter from the user's favorites list. This operation only removes filters that are currently visible to the user; filters that were favorited but subsequently made private cannot be removed through this operation."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.DeleteFavouriteForFilterRequest(
            path=_models.DeleteFavouriteForFilterRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_filter_favorite: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/filter/{id}/favourite", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/filter/{id}/favourite"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_filter_favorite")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_filter_favorite", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_filter_favorite",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Filters
@mcp.tool()
async def transfer_filter_ownership(
    id_: str = Field(..., alias="id", description="The unique identifier of the filter to transfer. This is a numeric ID that identifies the specific filter in your Jira instance."),
    account_id: str = Field(..., alias="accountId", description="The account ID of the new filter owner. This must be a valid Jira user account ID."),
) -> dict[str, Any]:
    """Transfer ownership of a filter to another user. The requesting user must own the filter or have Jira administrator permissions."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.ChangeFilterOwnerRequest(
            path=_models.ChangeFilterOwnerRequestPath(id_=_id_),
            body=_models.ChangeFilterOwnerRequestBody(account_id=account_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for transfer_filter_ownership: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/filter/{id}/owner", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/filter/{id}/owner"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("transfer_filter_ownership")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("transfer_filter_ownership", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="transfer_filter_ownership",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Filter sharing
@mcp.tool()
async def list_filter_permissions(id_: str = Field(..., alias="id", description="The unique identifier of the filter. Must be a positive integer.")) -> dict[str, Any]:
    """Retrieve all share permissions for a filter, including access granted to groups, projects, all logged-in users, or the public. Only returns permissions visible to the requesting user based on their access level."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.GetSharePermissionsRequest(
            path=_models.GetSharePermissionsRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_filter_permissions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/filter/{id}/permission", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/filter/{id}/permission"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_filter_permissions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_filter_permissions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_filter_permissions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Filter sharing
@mcp.tool()
async def grant_filter_share_permission(
    id_: str = Field(..., alias="id", description="The unique identifier of the filter to share. Must be a positive integer."),
    type_: Literal["user", "project", "group", "projectRole", "global", "authenticated"] = Field(..., alias="type", description="The recipient type for the share permission. Choose from: 'user' (share with individual user), 'group' (share with group), 'project' (share with project), 'projectRole' (share with project role), 'global' (share with all users including anonymous), or 'authenticated' (share with all logged-in users). Global and authenticated types override all existing permissions."),
    project_id: str | None = Field(None, alias="projectId", description="The project identifier to share the filter with. Required when type is set to 'project'."),
    project_role_id: str | None = Field(None, alias="projectRoleId", description="The project role identifier to share the filter with. Required when type is set to 'projectRole'; must be used together with projectId."),
    rights: str | None = Field(None, description="The access rights level for this share permission. Specified as a 32-bit integer representing the permission level."),
) -> dict[str, Any]:
    """Grant share permission for a filter to a user, group, project, or project role. Global or authenticated permissions will override all existing share permissions for the filter."""

    _id_ = _parse_int(id_)
    _rights = _parse_int(rights)

    # Construct request model with validation
    try:
        _request = _models.AddSharePermissionRequest(
            path=_models.AddSharePermissionRequestPath(id_=_id_),
            body=_models.AddSharePermissionRequestBody(project_id=project_id, project_role_id=project_role_id, rights=_rights, type_=type_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for grant_filter_share_permission: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/filter/{id}/permission", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/filter/{id}/permission"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("grant_filter_share_permission")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("grant_filter_share_permission", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="grant_filter_share_permission",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Filter sharing
@mcp.tool()
async def get_filter_share_permission(
    id_: str = Field(..., alias="id", description="The unique identifier of the filter. Must be a positive integer."),
    permission_id: str = Field(..., alias="permissionId", description="The unique identifier of the share permission to retrieve. Must be a positive integer."),
) -> dict[str, Any]:
    """Retrieves a specific share permission for a filter. Returns details about how a filter is shared with groups, projects, all logged-in users, or the public. This operation can be accessed anonymously, but only returns permissions for filters you own, are shared with your groups, or are in projects you can access."""

    _id_ = _parse_int(id_)
    _permission_id = _parse_int(permission_id)

    # Construct request model with validation
    try:
        _request = _models.GetSharePermissionRequest(
            path=_models.GetSharePermissionRequestPath(id_=_id_, permission_id=_permission_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_filter_share_permission: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/filter/{id}/permission/{permissionId}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/filter/{id}/permission/{permissionId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_filter_share_permission")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_filter_share_permission", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_filter_share_permission",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Filter sharing
@mcp.tool()
async def remove_filter_share_permission(
    id_: str = Field(..., alias="id", description="The unique identifier of the filter from which to remove the share permission. Must be a positive integer."),
    permission_id: str = Field(..., alias="permissionId", description="The unique identifier of the specific share permission to delete. Must be a positive integer."),
) -> dict[str, Any]:
    """Removes a share permission from a filter, restricting access for the specified user or group. Requires ownership of the filter and permission to access Jira."""

    _id_ = _parse_int(id_)
    _permission_id = _parse_int(permission_id)

    # Construct request model with validation
    try:
        _request = _models.DeleteSharePermissionRequest(
            path=_models.DeleteSharePermissionRequestPath(id_=_id_, permission_id=_permission_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_filter_share_permission: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/filter/{id}/permission/{permissionId}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/filter/{id}/permission/{permissionId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_filter_share_permission")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_filter_share_permission", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_filter_share_permission",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Groups
@mcp.tool()
async def create_group(name: str = Field(..., description="The name for the new group. This identifier is used to reference the group in Jira.")) -> dict[str, Any]:
    """Creates a new group in Jira. Requires site administration permissions to perform this action."""

    # Construct request model with validation
    try:
        _request = _models.CreateGroupRequest(
            body=_models.CreateGroupRequestBody(name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/group"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_group")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_group", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_group",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Groups
@mcp.tool()
async def delete_group(
    swap_group_id: str | None = Field(None, alias="swapGroupId", description="The ID of an existing group to receive the deleted group's restrictions. Only comments and worklogs are transferred. Omit this parameter if you want restrictions to be removed without transfer. Cannot be used together with the `swapGroup` parameter."),
    group_id: str | None = Field(None, alias="groupId", description="The ID of the group. This parameter cannot be used with the `groupname` parameter."),
) -> dict[str, Any]:
    """Permanently deletes a group from the system. Optionally transfer group restrictions to another group to preserve access to comments and worklogs; otherwise, these items become inaccessible after deletion."""

    # Construct request model with validation
    try:
        _request = _models.RemoveGroupRequest(
            query=_models.RemoveGroupRequestQuery(swap_group_id=swap_group_id, group_id=group_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/group"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_group")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_group", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_group",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Groups
@mcp.tool()
async def list_groups(
    start_at: str | None = Field(None, alias="startAt", description="The starting position for pagination, where 0 is the first group. Use this to navigate through large result sets."),
    max_results: str | None = Field(None, alias="maxResults", description="The number of groups to return per page. Defaults to 50 if not specified."),
    group_name: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(None, alias="groupName", description="Filter results by one or more group names. Specify multiple names to search for groups matching any of the provided names."),
    access_type: str | None = Field(None, alias="accessType", description="Filter groups by their access level within your Jira instance. Choose from site administrator, administrator, or standard user access levels."),
    application_key: str | None = Field(None, alias="applicationKey", description="Limit results to groups associated with a specific Jira product. Specify the product key to filter groups by their application context."),
) -> dict[str, Any]:
    """Retrieve a paginated list of groups from your Jira instance. Filter by group names, access level, or product application to find specific groups."""

    _start_at = _parse_int(start_at)
    _max_results = _parse_int(max_results)

    # Construct request model with validation
    try:
        _request = _models.BulkGetGroupsRequest(
            query=_models.BulkGetGroupsRequestQuery(start_at=_start_at, max_results=_max_results, group_name=group_name, access_type=access_type, application_key=application_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_groups: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/group/bulk"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_groups")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_groups", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_groups",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Groups
@mcp.tool()
async def list_group_members(
    include_inactive_users: bool | None = Field(None, alias="includeInactiveUsers", description="Whether to include inactive users in the results. Defaults to excluding inactive users."),
    start_at: str | None = Field(None, alias="startAt", description="The zero-based index where the result page should start. Use this for pagination to retrieve subsequent pages of results."),
    max_results: str | None = Field(None, alias="maxResults", description="The maximum number of users to return per page. Must be between 1 and 50 users."),
    group_id: str | None = Field(None, alias="groupId", description="The ID of the group. This parameter cannot be used with the `groupName` parameter."),
) -> dict[str, Any]:
    """Retrieve a paginated list of all users in a group. Users are ordered by username but usernames are not included in results for privacy reasons."""

    _start_at = _parse_int(start_at)
    _max_results = _parse_int(max_results)

    # Construct request model with validation
    try:
        _request = _models.GetUsersFromGroupRequest(
            query=_models.GetUsersFromGroupRequestQuery(include_inactive_users=include_inactive_users, start_at=_start_at, max_results=_max_results, group_id=group_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_group_members: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/group/member"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_group_members")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_group_members", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_group_members",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Groups
@mcp.tool()
async def add_user_to_group(
    group_id: str | None = Field(None, alias="groupId", description="The ID of the group. This parameter cannot be used with the `groupName` parameter."),
    account_id: str | None = Field(None, alias="accountId", description="The account ID of the user, which uniquely identifies the user across all Atlassian products. For example, *5b10ac8d82e05b22cc7d4ef5*.", max_length=128),
) -> dict[str, Any]:
    """Adds a user to a group in Jira. Requires site administration permissions to perform this operation."""

    # Construct request model with validation
    try:
        _request = _models.AddUserToGroupRequest(
            query=_models.AddUserToGroupRequestQuery(group_id=group_id),
            body=_models.AddUserToGroupRequestBody(account_id=account_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_user_to_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/group/user"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_user_to_group")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_user_to_group", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_user_to_group",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Groups
@mcp.tool()
async def search_groups(
    max_results: str | None = Field(None, alias="maxResults", description="Maximum number of groups to return in the results. Limited by the system's autocomplete configuration, typically capped at a system-defined threshold."),
    case_insensitive: bool | None = Field(None, alias="caseInsensitive", description="Whether the group name search should ignore case distinctions. Defaults to case-sensitive matching when not specified."),
) -> dict[str, Any]:
    """Search for groups by name to populate group picker suggestions. Returns matching groups with query terms highlighted in HTML, sorted alphabetically, along with a count summary. Requires Browse projects permission; anonymous users and those without permission receive empty results."""

    _max_results = _parse_int(max_results)

    # Construct request model with validation
    try:
        _request = _models.FindGroupsRequest(
            query=_models.FindGroupsRequestQuery(max_results=_max_results, case_insensitive=case_insensitive)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_groups: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/groups/picker"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_groups")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_groups", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_groups",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Group and user picker
@mcp.tool()
async def search_users_and_groups(
    query: str = Field(..., description="The search string to match against user display names, email addresses, and group names. User matches are case-insensitive; group matches are case-sensitive by default unless caseInsensitive is enabled."),
    max_results: str | None = Field(None, alias="maxResults", description="Maximum number of results to return per list (users and groups). Defaults to 50 items."),
    field_id: str | None = Field(None, alias="fieldId", description="The custom field ID to scope the search. When provided, results are filtered to users and groups with permissions for the specified field. Required to use projectId or issueTypeId filters."),
    project_id: list[str] | None = Field(None, alias="projectId", description="One or more project IDs to filter results. Returned users and groups must have permission to view all specified projects. Only applicable when fieldId is provided. Projects must be a subset of those enabled for the custom field."),
    issue_type_id: list[str] | None = Field(None, alias="issueTypeId", description="One or more issue type IDs to filter results. Returned users and groups must have permission to view all specified issue types. Supports special values like -1 (all standard types) and -2 (all subtask types). Only applicable when fieldId is provided."),
    case_insensitive: bool | None = Field(None, alias="caseInsensitive", description="Whether group name matching should be case-insensitive. Defaults to false (case-sensitive matching)."),
) -> dict[str, Any]:
    """Search for users and groups by name or email. Returns matching results with HTML-formatted highlights, useful for populating picker fields. Supports filtering by project, issue type, and custom field permissions."""

    _max_results = _parse_int(max_results)

    # Construct request model with validation
    try:
        _request = _models.FindUsersAndGroupsRequest(
            query=_models.FindUsersAndGroupsRequestQuery(query=query, max_results=_max_results, field_id=field_id, project_id=project_id, issue_type_id=issue_type_id, case_insensitive=case_insensitive)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_users_and_groups: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/groupuserpicker"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_users_and_groups")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_users_and_groups", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_users_and_groups",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issues
@mcp.tool()
async def create_issue(
    update_history: bool | None = Field(None, alias="updateHistory", description="Whether to add the project to your recently viewed projects list and track the issue type and request type in your project history for future create screen defaults. Defaults to false."),
    fields: dict[str, Any] | None = Field(None, description="List of issue screen fields to update, specifying the sub-field to update and its value for each field. This field provides a straightforward option when setting a sub-field. When multiple sub-fields or other operations are required, use `update`. Fields included in here cannot be included in `update`."),
    update: dict[str, list[_models.FieldUpdateOperation]] | None = Field(None, description="A Map containing the field field name and a list of operations to perform on the issue screen field. Note that fields included in here cannot be included in `fields`."),
) -> dict[str, Any]:
    """Create a new issue or subtask in a Jira project. Define the issue content using fields and optional workflow transitions, with field availability determined by the project's create issue metadata."""

    # Construct request model with validation
    try:
        _request = _models.CreateIssueRequest(
            query=_models.CreateIssueRequestQuery(update_history=update_history),
            body=_models.CreateIssueRequestBody(fields=fields, update=update)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_issue: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/issue"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_issue")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_issue", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_issue",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issues
@mcp.tool()
async def archive_issues_by_jql(jql: str | None = Field(None, description="JQL query string to select issues for archival. Only issues from software, service management, and business projects can be archived; subtasks must be archived through their parent issues.")) -> dict[str, Any]:
    """Asynchronously archive up to 100,000 issues matching a JQL query. Returns a task URL to monitor the archival progress. Requires Jira admin permissions and a Premium or Enterprise license."""

    # Construct request model with validation
    try:
        _request = _models.ArchiveIssuesAsyncRequest(
            body=_models.ArchiveIssuesAsyncRequestBody(jql=jql)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for archive_issues_by_jql: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/issue/archive"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("archive_issues_by_jql")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("archive_issues_by_jql", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="archive_issues_by_jql",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issues
@mcp.tool()
async def archive_issues(issue_ids_or_keys: list[str] | None = Field(None, alias="issueIdsOrKeys", description="Array of issue IDs or keys to archive (up to 1000 per request). Subtasks cannot be archived directly; archive them through their parent issues. Only issues from software, service management, and business projects can be archived.")) -> dict[str, Any]:
    """Archive up to 1000 issues by their ID or key in a single request. Returns details of successfully archived issues and any errors encountered. Requires Jira admin permissions and a Premium or Enterprise license."""

    # Construct request model with validation
    try:
        _request = _models.ArchiveIssuesRequest(
            body=_models.ArchiveIssuesRequestBody(issue_ids_or_keys=issue_ids_or_keys)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for archive_issues: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/issue/archive"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("archive_issues")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("archive_issues", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="archive_issues",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issues
@mcp.tool()
async def create_issues_bulk(issue_updates: list[_models.IssueUpdateDetails] | None = Field(None, alias="issueUpdates", description="Array of issue or subtask definitions to create. Each item specifies fields and updates for one issue. For subtasks, include the parent issue ID or key and set issueType to a subtask type. Order is preserved in processing.")) -> dict[str, Any]:
    """Create up to 50 issues and subtasks in bulk with optional workflow transitions and property assignments. Use the Get create issue metadata endpoint to determine available fields for your project."""

    # Construct request model with validation
    try:
        _request = _models.CreateIssuesRequest(
            body=_models.CreateIssuesRequestBody(issue_updates=issue_updates)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_issues_bulk: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/issue/bulk"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_issues_bulk")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_issues_bulk", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_issues_bulk",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issues
@mcp.tool()
async def fetch_issues(issue_ids_or_keys: list[str] = Field(..., alias="issueIdsOrKeys", description="Array of issue identifiers to fetch, accepting up to 100 items. You can mix issue IDs and keys in the same request (e.g., both numeric IDs and text keys like 'PROJ-123'). Results are returned in ascending ID order.")) -> dict[str, Any]:
    """Retrieve details for multiple issues by their IDs or keys in a single request. Supports up to 100 issues per request with case-insensitive matching and automatic detection of moved issues."""

    # Construct request model with validation
    try:
        _request = _models.BulkFetchIssuesRequest(
            body=_models.BulkFetchIssuesRequestBody(issue_ids_or_keys=issue_ids_or_keys)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for fetch_issues: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/issue/bulkfetch"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("fetch_issues")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("fetch_issues", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="fetch_issues",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issues
@mcp.tool()
async def list_issue_types_for_creation(
    project_id_or_key: str = Field(..., alias="projectIdOrKey", description="The project identifier, either the project ID or project key."),
    start_at: str | None = Field(None, alias="startAt", description="The starting position for pagination (zero-indexed). Defaults to 0 if not specified."),
    max_results: str | None = Field(None, alias="maxResults", description="The number of issue types to return per page, with a maximum of 200. Defaults to 50 if not specified."),
) -> dict[str, Any]:
    """Retrieve issue type metadata for a project to determine which issue types can be created and what fields are required. Use this information to populate requests when creating issues."""

    _start_at = _parse_int(start_at)
    _max_results = _parse_int(max_results)

    # Construct request model with validation
    try:
        _request = _models.GetCreateIssueMetaIssueTypesRequest(
            path=_models.GetCreateIssueMetaIssueTypesRequestPath(project_id_or_key=project_id_or_key),
            query=_models.GetCreateIssueMetaIssueTypesRequestQuery(start_at=_start_at, max_results=_max_results)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_issue_types_for_creation: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/issue/createmeta/{projectIdOrKey}/issuetypes", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/issue/createmeta/{projectIdOrKey}/issuetypes"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_issue_types_for_creation")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_issue_types_for_creation", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_issue_types_for_creation",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issues
@mcp.tool()
async def get_issue_creation_fields(
    project_id_or_key: str = Field(..., alias="projectIdOrKey", description="The project identifier, either the project ID or project key."),
    issue_type_id: str = Field(..., alias="issueTypeId", description="The ID of the issue type for which to retrieve creation field metadata."),
    start_at: str | None = Field(None, alias="startAt", description="The starting position for pagination, where 0 is the first item. Defaults to 0 if not specified."),
    max_results: str | None = Field(None, alias="maxResults", description="The maximum number of fields to return per page, up to 200. Defaults to 50 if not specified."),
) -> dict[str, Any]:
    """Retrieve the available fields and their metadata for creating issues of a specific type in a project. Use this information to populate requests when creating single or bulk issues."""

    _start_at = _parse_int(start_at)
    _max_results = _parse_int(max_results)

    # Construct request model with validation
    try:
        _request = _models.GetCreateIssueMetaIssueTypeIdRequest(
            path=_models.GetCreateIssueMetaIssueTypeIdRequestPath(project_id_or_key=project_id_or_key, issue_type_id=issue_type_id),
            query=_models.GetCreateIssueMetaIssueTypeIdRequestQuery(start_at=_start_at, max_results=_max_results)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_issue_creation_fields: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/issue/createmeta/{projectIdOrKey}/issuetypes/{issueTypeId}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/issue/createmeta/{projectIdOrKey}/issuetypes/{issueTypeId}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_issue_creation_fields")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_issue_creation_fields", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_issue_creation_fields",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issues
@mcp.tool()
async def list_issue_limit_violations(is_returning_keys: bool | None = Field(None, alias="isReturningKeys", description="Return issue keys (e.g., PROJ-123) instead of numeric issue IDs in the response. Defaults to false, which returns issue IDs.")) -> dict[str, Any]:
    """Retrieve all issues that are breaching or approaching per-issue limits in Jira. Requires Browse projects permission for the relevant projects or Administer Jira global permission for complete results."""

    # Construct request model with validation
    try:
        _request = _models.GetIssueLimitReportRequest(
            query=_models.GetIssueLimitReportRequestQuery(is_returning_keys=is_returning_keys)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_issue_limit_violations: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/issue/limit/report"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_issue_limit_violations")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_issue_limit_violations", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_issue_limit_violations",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue search
@mcp.tool()
async def search_issues_picker(
    current_jql: str | None = Field(None, alias="currentJQL", description="A JQL query that defines the pool of issues to search within. Note that username and userkey cannot be used for privacy reasons; use accountId instead."),
    current_issue_key: str | None = Field(None, alias="currentIssueKey", description="The key of an issue to exclude from the search results, typically the issue currently being viewed."),
    current_project_id: str | None = Field(None, alias="currentProjectId", description="The ID of a project to limit suggestions to issues belonging only to that project."),
    show_sub_tasks: bool | None = Field(None, alias="showSubTasks", description="Whether to include subtasks in the suggestions list."),
    show_sub_task_parent: bool | None = Field(None, alias="showSubTaskParent", description="When the excluded issue is a subtask, whether to include its parent issue in the suggestions if it matches the query."),
    query: str | None = Field(None, description="A string to match against text fields in the issue such as title, description, or comments."),
) -> dict[str, Any]:
    """Search for issues matching a query string to provide auto-completion suggestions. Returns matching issues from the user's history and from a filtered set defined by JQL."""

    # Construct request model with validation
    try:
        _request = _models.GetIssuePickerResourceRequest(
            query=_models.GetIssuePickerResourceRequestQuery(current_jql=current_jql, current_issue_key=current_issue_key, current_project_id=current_project_id, show_sub_tasks=show_sub_tasks, show_sub_task_parent=show_sub_task_parent, query=query)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_issues_picker: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/issue/picker"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_issues_picker")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_issues_picker", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_issues_picker",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue properties
@mcp.tool()
async def set_issue_properties_bulk(
    entities_ids: Annotated[list[int], AfterValidator(_check_unique_items)] | None = Field(None, alias="entitiesIds", description="List of issue IDs to update with the specified properties. Accepts between 1 and 10,000 issue identifiers.", min_length=1, max_length=10000),
    properties: dict[str, _models.JsonNode] | None = Field(None, description="A list of entity property keys and values.", min_length=1, max_length=10),
) -> dict[str, Any]:
    """Bulk set or update custom properties on multiple issues in a single transactional operation. Supports up to 10 properties and 10,000 issues, with each property value limited to 32,768 characters."""

    # Construct request model with validation
    try:
        _request = _models.BulkSetIssuesPropertiesListRequest(
            body=_models.BulkSetIssuesPropertiesListRequestBody(entities_ids=entities_ids, properties=properties)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for set_issue_properties_bulk: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/issue/properties"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("set_issue_properties_bulk")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("set_issue_properties_bulk", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="set_issue_properties_bulk",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue properties
@mcp.tool()
async def set_issue_properties_bulk_per_issue(issues: list[_models.IssueEntityPropertiesForMultiUpdate] | None = Field(None, description="A list of issues with their respective properties to set or update. Each entry should contain an issue ID and its associated property key-value pairs. Maximum of 100 issues per request, with up to 10 properties per issue.", min_length=1, max_length=100)) -> dict[str, Any]:
    """Bulk set or update custom properties on multiple issues. Supports up to 100 issues with up to 10 properties each in a single asynchronous request. Updates are non-transactional, so some entities may succeed while others fail."""

    # Construct request model with validation
    try:
        _request = _models.BulkSetIssuePropertiesByIssueRequest(
            body=_models.BulkSetIssuePropertiesByIssueRequestBody(issues=issues)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for set_issue_properties_bulk_per_issue: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/issue/properties/multi"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("set_issue_properties_bulk_per_issue")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("set_issue_properties_bulk_per_issue", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="set_issue_properties_bulk_per_issue",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue properties
@mcp.tool()
async def set_issue_property_bulk(
    property_key: str = Field(..., alias="propertyKey", description="The property key identifier. Maximum length is 255 characters."),
    expression: str | None = Field(None, description="A Jira expression to dynamically calculate the property value for each issue. The expression must return a JSON-serializable object (number, boolean, string, list, or map) with a JSON representation not exceeding 32,768 characters. Available context variables are `issue` and `user`. Either this or `value` should be specified, but not both."),
    filter_: _models.BulkSetIssuePropertyBodyFilter | None = Field(None, alias="filter", description="Filter criteria to identify which issues are eligible for update. Supports filtering by specific issue IDs, current property value, or property existence. Multiple criteria are combined with AND logic. Omit to update all issues where you have edit permission."),
    value: Any | None = Field(None, description="A static JSON value to set on the property. Must be a valid, non-empty JSON object with a maximum length of 32,768 characters. Either this or `expression` should be specified, but not both."),
) -> dict[str, Any]:
    """Bulk set a property on multiple issues using a constant value or Jira expression. The operation is transactional and asynchronous—either all eligible issues are updated or none are updated. Use the returned task location to monitor progress."""

    # Construct request model with validation
    try:
        _request = _models.BulkSetIssuePropertyRequest(
            path=_models.BulkSetIssuePropertyRequestPath(property_key=property_key),
            body=_models.BulkSetIssuePropertyRequestBody(expression=expression, filter_=filter_, value=value)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for set_issue_property_bulk: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/issue/properties/{propertyKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/issue/properties/{propertyKey}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("set_issue_property_bulk")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("set_issue_property_bulk", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="set_issue_property_bulk",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue properties
@mcp.tool()
async def delete_issue_property_bulk(
    property_key: str = Field(..., alias="propertyKey", description="The unique identifier of the property to delete from issues."),
    current_value: Any | None = Field(None, alias="currentValue", description="Optional filter to only delete the property from issues where it currently has this specific value."),
    entity_ids: Annotated[list[int], AfterValidator(_check_unique_items)] | None = Field(None, alias="entityIds", description="Optional list of specific issue IDs to target for deletion. If provided with currentValue, only issues matching both criteria are affected."),
) -> dict[str, Any]:
    """Bulk delete a property from multiple issues based on filter criteria. This operation is transactional and asynchronous—either the property is deleted from all matching issues or no changes are made if errors occur."""

    # Construct request model with validation
    try:
        _request = _models.BulkDeleteIssuePropertyRequest(
            path=_models.BulkDeleteIssuePropertyRequestPath(property_key=property_key),
            body=_models.BulkDeleteIssuePropertyRequestBody(current_value=current_value, entity_ids=entity_ids)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_issue_property_bulk: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/issue/properties/{propertyKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/issue/properties/{propertyKey}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_issue_property_bulk")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_issue_property_bulk", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_issue_property_bulk",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issues
@mcp.tool()
async def restore_issues(issue_ids_or_keys: list[str] | None = Field(None, alias="issueIdsOrKeys", description="Array of issue keys or issue IDs to restore. You can restore up to 1000 issues per request. Subtasks cannot be restored directly; restore their parent issues instead. Only applicable to software, service management, and business projects.")) -> dict[str, Any]:
    """Restore up to 1000 archived issues in a single request using their issue keys or IDs. Returns details of successfully restored issues and any errors encountered. Requires Jira admin permissions and a Premium or Enterprise license."""

    # Construct request model with validation
    try:
        _request = _models.UnarchiveIssuesRequest(
            body=_models.UnarchiveIssuesRequestBody(issue_ids_or_keys=issue_ids_or_keys)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for restore_issues: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/issue/unarchive"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("restore_issues")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("restore_issues", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="restore_issues",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue watchers
@mcp.tool()
async def check_watched_issues_bulk(issue_ids: list[str] = Field(..., alias="issueIds", description="A list of issue IDs to check the watched status for. The order of IDs in the list is preserved in the response.")) -> dict[str, Any]:
    """Check the watched status of multiple issues for the current user. Returns whether each issue is being watched, with invalid issue IDs returning a watched status of false."""

    # Construct request model with validation
    try:
        _request = _models.GetIsWatchingIssueBulkRequest(
            body=_models.GetIsWatchingIssueBulkRequestBody(issue_ids=issue_ids)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for check_watched_issues_bulk: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/issue/watching"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("check_watched_issues_bulk")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("check_watched_issues_bulk", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="check_watched_issues_bulk",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issues
@mcp.tool()
async def retrieve_issue(
    issue_id_or_key: str = Field(..., alias="issueIdOrKey", description="The unique identifier for the issue, either its numeric ID or alphanumeric key (e.g., PROJ-123). The search is case-insensitive and will locate moved issues."),
    update_history: bool | None = Field(None, alias="updateHistory", description="When enabled, adds the issue's project to your recently viewed projects list and updates the lastViewed field for JQL searches. Defaults to disabled."),
) -> dict[str, Any]:
    """Retrieve detailed information about a specific issue by its ID or key. The operation performs case-insensitive matching and checks for moved issues, returning the current issue details without redirects. Requires browse permission for the project and any applicable issue-level security permissions."""

    # Construct request model with validation
    try:
        _request = _models.GetIssueRequest(
            path=_models.GetIssueRequestPath(issue_id_or_key=issue_id_or_key),
            query=_models.GetIssueRequestQuery(update_history=update_history)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for retrieve_issue: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/issue/{issueIdOrKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/issue/{issueIdOrKey}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("retrieve_issue")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("retrieve_issue", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="retrieve_issue",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issues
@mcp.tool()
async def update_issue(
    issue_id_or_key: str = Field(..., alias="issueIdOrKey", description="The issue identifier, either the numeric ID or the issue key (e.g., PROJ-123)."),
    notify_users: bool | None = Field(None, alias="notifyUsers", description="Whether to send notification emails to all watchers about this update. Defaults to true; only users with Administer Jira or Administer project permissions can disable notifications."),
    override_editable_flag: bool | None = Field(None, alias="overrideEditableFlag", description="Whether to bypass screen security restrictions to allow editing of normally uneditable fields. Only available to Connect and Forge apps with Administer Jira global permission. Defaults to false."),
    return_issue: bool | None = Field(None, alias="returnIssue", description="Whether to include the updated issue in the response with the same format as the Get issue endpoint. Defaults to false."),
    fields: dict[str, Any] | None = Field(None, description="List of issue screen fields to update, specifying the sub-field to update and its value for each field. This field provides a straightforward option when setting a sub-field. When multiple sub-fields or other operations are required, use `update`. Fields included in here cannot be included in `update`."),
    update: dict[str, list[_models.FieldUpdateOperation]] | None = Field(None, description="A Map containing the field field name and a list of operations to perform on the issue screen field. Note that fields included in here cannot be included in `fields`."),
) -> dict[str, Any]:
    """Updates an issue's fields and properties. Use the Get edit issue metadata endpoint to determine which fields are editable. Note that issue transitions are not supported through this operation; use the Transition issue endpoint instead."""

    # Construct request model with validation
    try:
        _request = _models.EditIssueRequest(
            path=_models.EditIssueRequestPath(issue_id_or_key=issue_id_or_key),
            query=_models.EditIssueRequestQuery(notify_users=notify_users, override_editable_flag=override_editable_flag, return_issue=return_issue),
            body=_models.EditIssueRequestBody(fields=fields, update=update)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_issue: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/issue/{issueIdOrKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/issue/{issueIdOrKey}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_issue")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_issue", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_issue",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issues
@mcp.tool()
async def delete_issue(
    issue_id_or_key: str = Field(..., alias="issueIdOrKey", description="The unique identifier or key of the issue to delete (e.g., PROJ-123 or 10001)."),
    delete_subtasks: Literal["true", "false"] | None = Field(None, alias="deleteSubtasks", description="Whether to automatically delete all subtasks when the issue is deleted. Set to 'true' to delete subtasks along with the issue, or 'false' to prevent deletion if subtasks exist. Defaults to 'false'."),
) -> dict[str, Any]:
    """Permanently deletes an issue from the project. Subtasks must be handled explicitly—either delete them along with the issue or remove them first."""

    # Construct request model with validation
    try:
        _request = _models.DeleteIssueRequest(
            path=_models.DeleteIssueRequestPath(issue_id_or_key=issue_id_or_key),
            query=_models.DeleteIssueRequestQuery(delete_subtasks=delete_subtasks)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_issue: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/issue/{issueIdOrKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/issue/{issueIdOrKey}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_issue")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_issue", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_issue",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issues
@mcp.tool()
async def assign_issue(
    issue_id_or_key: str = Field(..., alias="issueIdOrKey", description="The issue identifier, either the numeric ID or the project key followed by issue number (e.g., PROJ-123)."),
    account_id: str | None = Field(None, alias="accountId", description="The account ID of the user, which uniquely identifies the user across all Atlassian products. For example, *5b10ac8d82e05b22cc7d4ef5*. Required in requests.", max_length=128),
) -> dict[str, Any]:
    """Assigns an issue to a user or removes the assignment. Use this operation when you have the Assign Issues permission but lack Edit Issues permission. You can assign to a specific user, the project's default assignee, or leave the issue unassigned."""

    # Construct request model with validation
    try:
        _request = _models.AssignIssueRequest(
            path=_models.AssignIssueRequestPath(issue_id_or_key=issue_id_or_key),
            body=_models.AssignIssueRequestBody(account_id=account_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for assign_issue: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/issue/{issueIdOrKey}/assignee", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/issue/{issueIdOrKey}/assignee"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("assign_issue")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("assign_issue", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="assign_issue",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue attachments
@mcp.tool()
async def attach_files(
    issue_id_or_key: str = Field(..., alias="issueIdOrKey", description="The issue identifier, either the numeric ID or the issue key (e.g., TEST-123)."),
    body: list[_models.MultipartFile] = Field(..., description="Array of files to attach. Each file is submitted as a multipart form field named 'file'. Multiple files can be attached in a single request."),
) -> dict[str, Any]:
    """Attach one or more files to a Jira issue. Files are uploaded as multipart form data and require the X-Atlassian-Token: no-check header."""

    # Construct request model with validation
    try:
        _request = _models.AddAttachmentRequest(
            path=_models.AddAttachmentRequestPath(issue_id_or_key=issue_id_or_key),
            body=_models.AddAttachmentRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for attach_files: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/issue/{issueIdOrKey}/attachments", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/issue/{issueIdOrKey}/attachments"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("attach_files")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("attach_files", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="attach_files",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: Issues
@mcp.tool()
async def list_issue_changelogs(
    issue_id_or_key: str = Field(..., alias="issueIdOrKey", description="The issue identifier, either the numeric ID or the human-readable key (e.g., PROJ-123)."),
    start_at: str | None = Field(None, alias="startAt", description="The starting position for pagination, where 0 represents the first changelog entry. Defaults to 0 if not specified."),
    max_results: str | None = Field(None, alias="maxResults", description="The number of changelog entries to return per page. Defaults to 100 if not specified."),
) -> dict[str, Any]:
    """Retrieve a paginated list of all changes made to an issue, sorted chronologically from oldest to newest. Requires browse permission for the project and any applicable issue-level security permissions."""

    _start_at = _parse_int(start_at)
    _max_results = _parse_int(max_results)

    # Construct request model with validation
    try:
        _request = _models.GetChangeLogsRequest(
            path=_models.GetChangeLogsRequestPath(issue_id_or_key=issue_id_or_key),
            query=_models.GetChangeLogsRequestQuery(start_at=_start_at, max_results=_max_results)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_issue_changelogs: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/issue/{issueIdOrKey}/changelog", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/issue/{issueIdOrKey}/changelog"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_issue_changelogs")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_issue_changelogs", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_issue_changelogs",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issues
@mcp.tool()
async def fetch_changelogs(
    issue_id_or_key: str = Field(..., alias="issueIdOrKey", description="The issue identifier, either the numeric ID or the human-readable key (e.g., PROJ-123). Used to locate the issue whose changelogs you want to retrieve."),
    changelog_ids: Annotated[list[int], AfterValidator(_check_unique_items)] = Field(..., alias="changelogIds", description="A list of changelog IDs to retrieve. Specify the exact IDs of the changelog entries you want to fetch; order is preserved in the response."),
) -> dict[str, Any]:
    """Retrieve specific changelogs for an issue by their IDs. Returns detailed change history records for the specified changelog identifiers."""

    # Construct request model with validation
    try:
        _request = _models.GetChangeLogsByIdsRequest(
            path=_models.GetChangeLogsByIdsRequestPath(issue_id_or_key=issue_id_or_key),
            body=_models.GetChangeLogsByIdsRequestBody(changelog_ids=changelog_ids)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for fetch_changelogs: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/issue/{issueIdOrKey}/changelog/list", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/issue/{issueIdOrKey}/changelog/list"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("fetch_changelogs")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("fetch_changelogs", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="fetch_changelogs",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue comments
@mcp.tool()
async def list_issue_comments(
    issue_id_or_key: str = Field(..., alias="issueIdOrKey", description="The issue identifier, either the numeric ID or the issue key (e.g., PROJ-123)."),
    start_at: str | None = Field(None, alias="startAt", description="The starting position for pagination (zero-indexed). Use this to retrieve subsequent pages of results."),
    max_results: str | None = Field(None, alias="maxResults", description="The maximum number of comments to return per page. Defaults to 100 if not specified."),
    order_by: Literal["created", "-created", "+created"] | None = Field(None, alias="orderBy", description="Sort comments by creation date. Use 'created' for ascending order, '-created' for descending order, or '+created' for ascending order."),
) -> dict[str, Any]:
    """Retrieve all comments for a specific issue, with support for pagination and sorting. Comments are filtered based on user permissions and visibility restrictions."""

    _start_at = _parse_int(start_at)
    _max_results = _parse_int(max_results)

    # Construct request model with validation
    try:
        _request = _models.GetCommentsRequest(
            path=_models.GetCommentsRequestPath(issue_id_or_key=issue_id_or_key),
            query=_models.GetCommentsRequestQuery(start_at=_start_at, max_results=_max_results, order_by=order_by)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_issue_comments: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/issue/{issueIdOrKey}/comment", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/issue/{issueIdOrKey}/comment"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_issue_comments")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_issue_comments", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_issue_comments",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue comments
@mcp.tool()
async def add_comment(
    issue_id_or_key: str = Field(..., alias="issueIdOrKey", description="The issue identifier, either the numeric ID or the project key followed by issue number (e.g., PROJ-123)."),
    body: Any | None = Field(None, description="The comment text formatted using Atlassian Document Format. This field supports rich text formatting including mentions, links, and other document elements."),
    visibility: _models.AddCommentBodyVisibility | None = Field(None, description="Restricts comment visibility to a specific group or role. When omitted, the comment is visible to all users with permission to view the issue."),
) -> dict[str, Any]:
    """Add a comment to a Jira issue. The comment can be formatted using Atlassian Document Format and optionally restricted to specific groups or roles."""

    # Construct request model with validation
    try:
        _request = _models.AddCommentRequest(
            path=_models.AddCommentRequestPath(issue_id_or_key=issue_id_or_key),
            body=_models.AddCommentRequestBody(body=body, visibility=visibility)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/issue/{issueIdOrKey}/comment", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/issue/{issueIdOrKey}/comment"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_comment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_comment", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_comment",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue comments
@mcp.tool()
async def get_comment(
    issue_id_or_key: str = Field(..., alias="issueIdOrKey", description="The issue identifier, which can be either the numeric issue ID or the issue key (e.g., PROJ-123)."),
    id_: str = Field(..., alias="id", description="The unique identifier of the comment to retrieve."),
) -> dict[str, Any]:
    """Retrieve a specific comment from an issue. Requires browse permissions on the project and any applicable issue-level security or comment visibility restrictions."""

    # Construct request model with validation
    try:
        _request = _models.GetCommentRequest(
            path=_models.GetCommentRequestPath(issue_id_or_key=issue_id_or_key, id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/issue/{issueIdOrKey}/comment/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/issue/{issueIdOrKey}/comment/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_comment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_comment", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_comment",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue comments
@mcp.tool()
async def update_comment(
    issue_id_or_key: str = Field(..., alias="issueIdOrKey", description="The issue identifier, either the numeric ID or the project key-based identifier (e.g., PROJ-123)."),
    id_: str = Field(..., alias="id", description="The unique identifier of the comment to update."),
    notify_users: bool | None = Field(None, alias="notifyUsers", description="Controls whether users are notified about the comment update. Defaults to true."),
    override_editable_flag: bool | None = Field(None, alias="overrideEditableFlag", description="Allows bypassing screen security restrictions to edit normally uneditable fields. Only available to administrators and Forge apps with admin privileges. Defaults to false."),
    body: Any | None = Field(None, description="The updated comment text formatted as Atlassian Document Format (ADF)."),
    visibility: _models.UpdateCommentBodyVisibility | None = Field(None, description="Restricts comment visibility to a specific group or role. Child comments inherit visibility from their parent and cannot be modified independently."),
) -> dict[str, Any]:
    """Updates an existing comment on an issue. Requires appropriate permissions to edit the comment and view the issue."""

    # Construct request model with validation
    try:
        _request = _models.UpdateCommentRequest(
            path=_models.UpdateCommentRequestPath(issue_id_or_key=issue_id_or_key, id_=id_),
            query=_models.UpdateCommentRequestQuery(notify_users=notify_users, override_editable_flag=override_editable_flag),
            body=_models.UpdateCommentRequestBody(body=body, visibility=visibility)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/issue/{issueIdOrKey}/comment/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/issue/{issueIdOrKey}/comment/{id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_comment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_comment", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_comment",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue comments
@mcp.tool()
async def delete_comment(
    issue_id_or_key: str = Field(..., alias="issueIdOrKey", description="The issue identifier, either the numeric ID or the project key followed by issue number (e.g., PROJ-123)."),
    id_: str = Field(..., alias="id", description="The unique identifier of the comment to delete."),
) -> dict[str, Any]:
    """Removes a comment from an issue. Requires appropriate permissions based on comment ownership and visibility restrictions."""

    # Construct request model with validation
    try:
        _request = _models.DeleteCommentRequest(
            path=_models.DeleteCommentRequestPath(issue_id_or_key=issue_id_or_key, id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/issue/{issueIdOrKey}/comment/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/issue/{issueIdOrKey}/comment/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_comment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_comment", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_comment",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issues
@mcp.tool()
async def get_issue_editable_fields(
    issue_id_or_key: str = Field(..., alias="issueIdOrKey", description="The issue identifier, either the numeric ID or the issue key (e.g., PROJ-123)."),
    override_editable_flag: bool | None = Field(None, alias="overrideEditableFlag", description="When enabled, returns non-editable fields by bypassing workflow editability checks. Only available to administrators. Defaults to false."),
) -> dict[str, Any]:
    """Retrieve the fields that are editable for a specific issue based on the user's permissions, screen configuration, and workflow state. Use this to determine which fields can be modified before submitting an edit request."""

    # Construct request model with validation
    try:
        _request = _models.GetEditIssueMetaRequest(
            path=_models.GetEditIssueMetaRequestPath(issue_id_or_key=issue_id_or_key),
            query=_models.GetEditIssueMetaRequestQuery(override_editable_flag=override_editable_flag)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_issue_editable_fields: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/issue/{issueIdOrKey}/editmeta", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/issue/{issueIdOrKey}/editmeta"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_issue_editable_fields")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_issue_editable_fields", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_issue_editable_fields",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issues
@mcp.tool()
async def send_issue_notification(
    issue_id_or_key: str = Field(..., alias="issueIdOrKey", description="The issue identifier, either the numeric ID or the issue key (e.g., PROJ-123)."),
    html_body: str | None = Field(None, alias="htmlBody", description="The HTML-formatted body content of the email notification. If provided, this takes precedence over plain text body for HTML-capable email clients."),
    restrict: _models.NotifyBodyRestrict | None = Field(None, description="Restricts notification delivery to users who have the specified permission level for the issue."),
    subject: str | None = Field(None, description="The subject line of the email notification. If not provided, defaults to the issue key and summary."),
    text_body: str | None = Field(None, alias="textBody", description="The plain text body content of the email notification. Used as fallback for email clients that don't support HTML."),
    to: _models.NotifyBodyTo | None = Field(None, description="The list of recipients who should receive the email notification for this issue."),
) -> dict[str, Any]:
    """Send an email notification for an issue and queue it for delivery. The notification can be customized with subject and body content, and optionally restricted to users with specific permissions."""

    # Construct request model with validation
    try:
        _request = _models.NotifyRequest(
            path=_models.NotifyRequestPath(issue_id_or_key=issue_id_or_key),
            body=_models.NotifyRequestBody(html_body=html_body, restrict=restrict, subject=subject, text_body=text_body, to=to)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for send_issue_notification: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/issue/{issueIdOrKey}/notify", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/issue/{issueIdOrKey}/notify"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("send_issue_notification")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("send_issue_notification", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="send_issue_notification",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue properties
@mcp.tool()
async def list_issue_property_keys(issue_id_or_key: str = Field(..., alias="issueIdOrKey", description="The issue identifier, which can be either the issue key (e.g., PROJ-123) or the numeric issue ID.")) -> dict[str, Any]:
    """Retrieves all property keys and their URLs associated with a specific issue. This allows you to discover what custom properties are stored on an issue."""

    # Construct request model with validation
    try:
        _request = _models.GetIssuePropertyKeysRequest(
            path=_models.GetIssuePropertyKeysRequestPath(issue_id_or_key=issue_id_or_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_issue_property_keys: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/issue/{issueIdOrKey}/properties", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/issue/{issueIdOrKey}/properties"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_issue_property_keys")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_issue_property_keys", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_issue_property_keys",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue properties
@mcp.tool()
async def get_issue_property(
    issue_id_or_key: str = Field(..., alias="issueIdOrKey", description="The issue identifier, which can be either the issue key (e.g., PROJ-123) or the numeric issue ID."),
    property_key: str = Field(..., alias="propertyKey", description="The unique identifier for the property to retrieve from the issue."),
) -> dict[str, Any]:
    """Retrieves a specific property value associated with an issue by its property key. Returns both the key and value of the requested issue property."""

    # Construct request model with validation
    try:
        _request = _models.GetIssuePropertyRequest(
            path=_models.GetIssuePropertyRequestPath(issue_id_or_key=issue_id_or_key, property_key=property_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_issue_property: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/issue/{issueIdOrKey}/properties/{propertyKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/issue/{issueIdOrKey}/properties/{propertyKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_issue_property")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_issue_property", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_issue_property",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue properties
@mcp.tool()
async def remove_issue_property(
    issue_id_or_key: str = Field(..., alias="issueIdOrKey", description="The issue identifier, either the issue key (e.g., PROJ-123) or the numeric issue ID."),
    property_key: str = Field(..., alias="propertyKey", description="The unique key identifying the property to delete from the issue."),
) -> dict[str, Any]:
    """Removes a custom property from an issue. Requires browse and edit permissions for the project, and issue-level security permission if configured."""

    # Construct request model with validation
    try:
        _request = _models.DeleteIssuePropertyRequest(
            path=_models.DeleteIssuePropertyRequestPath(issue_id_or_key=issue_id_or_key, property_key=property_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_issue_property: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/issue/{issueIdOrKey}/properties/{propertyKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/issue/{issueIdOrKey}/properties/{propertyKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_issue_property")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_issue_property", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_issue_property",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue remote links
@mcp.tool()
async def list_remote_issue_links(
    issue_id_or_key: str = Field(..., alias="issueIdOrKey", description="The issue identifier, either the numeric ID (e.g., 10000) or the issue key (e.g., PROJ-123)."),
    global_id: str | None = Field(None, alias="globalId", description="Optional global ID to retrieve a specific remote issue link. If omitted, all remote issue links for the issue are returned. URL-reserved characters in the global ID must be percent-encoded."),
) -> dict[str, Any]:
    """Retrieve remote issue links for an issue, optionally filtered by a specific global ID. Returns all linked remote issues or a single link matching the provided global ID."""

    # Construct request model with validation
    try:
        _request = _models.GetRemoteIssueLinksRequest(
            path=_models.GetRemoteIssueLinksRequestPath(issue_id_or_key=issue_id_or_key),
            query=_models.GetRemoteIssueLinksRequestQuery(global_id=global_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_remote_issue_links: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/issue/{issueIdOrKey}/remotelink", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/issue/{issueIdOrKey}/remotelink"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_remote_issue_links")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_remote_issue_links", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_remote_issue_links",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue remote links
@mcp.tool()
async def link_remote_issue(
    issue_id_or_key: str = Field(..., alias="issueIdOrKey", description="The Jira issue identifier, either the numeric ID or the issue key (e.g., PROJ-123)."),
    object_: _models.CreateOrUpdateRemoteIssueLinkBodyObject = Field(..., alias="object", description="Details about the item being linked to, including its URL, title, and other metadata from the remote system."),
    application: _models.CreateOrUpdateRemoteIssueLinkBodyApplication | None = Field(None, description="Details about the remote application containing the linked item, such as the application name or identifier (e.g., trello, confluence)."),
    global_id: str | None = Field(None, alias="globalId", description="A unique identifier for the remote item in the external system that enables updating or deleting the link using remote system details instead of the Jira record ID. Maximum length is 255 characters."),
    relationship: str | None = Field(None, description="A description of how the issue relates to the linked item. If not specified, defaults to 'links to'."),
) -> dict[str, Any]:
    """Creates or updates a remote issue link to connect an issue with an item in an external system. If a globalId is provided and a matching link exists, it updates the link; otherwise, it creates a new one."""

    # Construct request model with validation
    try:
        _request = _models.CreateOrUpdateRemoteIssueLinkRequest(
            path=_models.CreateOrUpdateRemoteIssueLinkRequestPath(issue_id_or_key=issue_id_or_key),
            body=_models.CreateOrUpdateRemoteIssueLinkRequestBody(application=application, global_id=global_id, object_=object_, relationship=relationship)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for link_remote_issue: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/issue/{issueIdOrKey}/remotelink", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/issue/{issueIdOrKey}/remotelink"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("link_remote_issue")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("link_remote_issue", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="link_remote_issue",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue remote links
@mcp.tool()
async def get_remote_link(
    issue_id_or_key: str = Field(..., alias="issueIdOrKey", description="The issue identifier, which can be either the numeric issue ID or the issue key (e.g., PROJECT-123)."),
    link_id: str = Field(..., alias="linkId", description="The unique identifier of the remote issue link to retrieve."),
) -> dict[str, Any]:
    """Retrieves a specific remote issue link for an issue. Requires issue linking to be enabled and appropriate project permissions."""

    # Construct request model with validation
    try:
        _request = _models.GetRemoteIssueLinkByIdRequest(
            path=_models.GetRemoteIssueLinkByIdRequestPath(issue_id_or_key=issue_id_or_key, link_id=link_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_remote_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/issue/{issueIdOrKey}/remotelink/{linkId}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/issue/{issueIdOrKey}/remotelink/{linkId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_remote_link")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_remote_link", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_remote_link",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue remote links
@mcp.tool()
async def update_remote_link(
    issue_id_or_key: str = Field(..., alias="issueIdOrKey", description="The issue identifier, either the numeric ID or the issue key (e.g., 'PROJ-123')."),
    link_id: str = Field(..., alias="linkId", description="The numeric ID of the remote issue link to update."),
    object_: _models.UpdateRemoteIssueLinkBodyObject = Field(..., alias="object", description="Details of the item being linked to, including its title, URL, and other relevant metadata from the remote system."),
    application: _models.UpdateRemoteIssueLinkBodyApplication | None = Field(None, description="Details of the remote application containing the linked item, such as Trello or Confluence."),
    global_id: str | None = Field(None, alias="globalId", description="A unique identifier for the remote item in its external system (maximum 255 characters). For example, in Confluence this might be formatted as 'appId=456&pageId=123'. Enables updating or deleting the link using remote system details instead of the Jira link ID."),
    relationship: str | None = Field(None, description="A description of the relationship between the issue and the linked item. If not provided, defaults to 'links to'."),
) -> dict[str, Any]:
    """Updates an existing remote issue link for a Jira issue. Unspecified fields in the request will be set to null. Requires issue linking to be enabled and appropriate project permissions."""

    # Construct request model with validation
    try:
        _request = _models.UpdateRemoteIssueLinkRequest(
            path=_models.UpdateRemoteIssueLinkRequestPath(issue_id_or_key=issue_id_or_key, link_id=link_id),
            body=_models.UpdateRemoteIssueLinkRequestBody(application=application, global_id=global_id, object_=object_, relationship=relationship)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_remote_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/issue/{issueIdOrKey}/remotelink/{linkId}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/issue/{issueIdOrKey}/remotelink/{linkId}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_remote_link")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_remote_link", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_remote_link",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue remote links
@mcp.tool()
async def delete_remote_link_by_id(
    issue_id_or_key: str = Field(..., alias="issueIdOrKey", description="The issue identifier, either the numeric ID (e.g., 10000) or the issue key (e.g., PROJ-123)."),
    link_id: str = Field(..., alias="linkId", description="The numeric ID of the remote issue link to delete (e.g., 10000)."),
) -> dict[str, Any]:
    """Removes a remote issue link from an issue. Requires issue linking to be enabled and appropriate project permissions including Browse projects, Edit issues, and Link issues."""

    # Construct request model with validation
    try:
        _request = _models.DeleteRemoteIssueLinkByIdRequest(
            path=_models.DeleteRemoteIssueLinkByIdRequestPath(issue_id_or_key=issue_id_or_key, link_id=link_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_remote_link_by_id: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/issue/{issueIdOrKey}/remotelink/{linkId}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/issue/{issueIdOrKey}/remotelink/{linkId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_remote_link_by_id")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_remote_link_by_id", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_remote_link_by_id",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issues
@mcp.tool()
async def list_issue_transitions_single(
    issue_id_or_key: str = Field(..., alias="issueIdOrKey", description="The issue identifier, either the numeric ID or the project key followed by issue number (e.g., PROJ-123)."),
    transition_id: str | None = Field(None, alias="transitionId", description="Optional ID of a specific transition to retrieve. When provided, only that transition is returned if it exists and is available."),
    include_unavailable_transitions: bool | None = Field(None, alias="includeUnavailableTransitions", description="Whether to include transitions that fail their conditions in the response. Defaults to false, returning only transitions that can currently be performed."),
) -> dict[str, Any]:
    """Retrieve available transitions for an issue based on its current status. Returns all possible transitions the user can perform, or a specific transition if requested. An empty list is returned if the requested transition doesn't exist or cannot be performed given the issue's current status."""

    # Construct request model with validation
    try:
        _request = _models.GetTransitionsRequest(
            path=_models.GetTransitionsRequestPath(issue_id_or_key=issue_id_or_key),
            query=_models.GetTransitionsRequestQuery(transition_id=transition_id, include_unavailable_transitions=include_unavailable_transitions)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_issue_transitions_single: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/issue/{issueIdOrKey}/transitions", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/issue/{issueIdOrKey}/transitions"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_issue_transitions_single")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_issue_transitions_single", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_issue_transitions_single",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issues
@mcp.tool()
async def transition_issue(
    issue_id_or_key: str = Field(..., alias="issueIdOrKey", description="The issue identifier, either the numeric ID or the project key followed by issue number (e.g., PROJ-123)."),
    transition: _models.DoTransitionBodyTransition | None = Field(None, description="Details of a transition. Required when performing a transition, optional when creating or editing an issue."),
    fields: dict[str, Any] | None = Field(None, description="List of issue screen fields to update, specifying the sub-field to update and its value for each field. This field provides a straightforward option when setting a sub-field. When multiple sub-fields or other operations are required, use `update`. Fields included in here cannot be included in `update`."),
    update: dict[str, list[_models.FieldUpdateOperation]] | None = Field(None, description="A Map containing the field field name and a list of operations to perform on the issue screen field. Note that fields included in here cannot be included in `fields`."),
) -> dict[str, Any]:
    """Move an issue to a new status by performing a transition. If the transition includes a screen, you can update issue fields as part of the transition."""

    # Construct request model with validation
    try:
        _request = _models.DoTransitionRequest(
            path=_models.DoTransitionRequestPath(issue_id_or_key=issue_id_or_key),
            body=_models.DoTransitionRequestBody(transition=transition, fields=fields, update=update)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for transition_issue: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/issue/{issueIdOrKey}/transitions", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/issue/{issueIdOrKey}/transitions"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("transition_issue")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("transition_issue", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="transition_issue",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue votes
@mcp.tool()
async def retrieve_issue_votes(issue_id_or_key: str = Field(..., alias="issueIdOrKey", description="The issue identifier, either the numeric ID or the project key followed by issue number (e.g., PROJ-123).")) -> dict[str, Any]:
    """Retrieve voting details for an issue, including vote count and voter information. Requires the voting feature to be enabled in Jira configuration and appropriate project permissions."""

    # Construct request model with validation
    try:
        _request = _models.GetVotesRequest(
            path=_models.GetVotesRequestPath(issue_id_or_key=issue_id_or_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for retrieve_issue_votes: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/issue/{issueIdOrKey}/votes", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/issue/{issueIdOrKey}/votes"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("retrieve_issue_votes")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("retrieve_issue_votes", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="retrieve_issue_votes",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue votes
@mcp.tool()
async def vote_issue(issue_id_or_key: str = Field(..., alias="issueIdOrKey", description="The issue identifier, either the numeric ID or the project key followed by issue number (e.g., PROJ-123).")) -> dict[str, Any]:
    """Register the user's vote on an issue. This action is equivalent to clicking the Vote button in Jira and requires voting to be enabled in Jira's general configuration."""

    # Construct request model with validation
    try:
        _request = _models.AddVoteRequest(
            path=_models.AddVoteRequestPath(issue_id_or_key=issue_id_or_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for vote_issue: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/issue/{issueIdOrKey}/votes", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/issue/{issueIdOrKey}/votes"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("vote_issue")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("vote_issue", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="vote_issue",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue votes
@mcp.tool()
async def remove_vote(issue_id_or_key: str = Field(..., alias="issueIdOrKey", description="The issue identifier, either the numeric ID or the project key followed by issue number (e.g., PROJ-123).")) -> dict[str, Any]:
    """Remove a user's vote from an issue, equivalent to clicking Unvote in Jira. Requires voting to be enabled in Jira's general configuration."""

    # Construct request model with validation
    try:
        _request = _models.RemoveVoteRequest(
            path=_models.RemoveVoteRequestPath(issue_id_or_key=issue_id_or_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_vote: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/issue/{issueIdOrKey}/votes", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/issue/{issueIdOrKey}/votes"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_vote")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_vote", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_vote",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue watchers
@mcp.tool()
async def list_issue_watchers(issue_id_or_key: str = Field(..., alias="issueIdOrKey", description="The issue identifier, either the numeric ID or the project key followed by issue number (e.g., PROJ-123).")) -> dict[str, Any]:
    """Retrieve the list of users watching an issue. Requires the 'Allow users to watch issues' option to be enabled in Jira's general configuration."""

    # Construct request model with validation
    try:
        _request = _models.GetIssueWatchersRequest(
            path=_models.GetIssueWatchersRequestPath(issue_id_or_key=issue_id_or_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_issue_watchers: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/issue/{issueIdOrKey}/watchers", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/issue/{issueIdOrKey}/watchers"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_issue_watchers")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_issue_watchers", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_issue_watchers",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue watchers
@mcp.tool()
async def add_issue_watcher(
    issue_id_or_key: str = Field(..., alias="issueIdOrKey", description="The issue identifier, either the numeric ID or the project key followed by issue number (e.g., PROJ-123)."),
    body: str = Field(..., description="The account ID of the user to add as a watcher. If omitted, the authenticated user making the request is added instead."),
) -> dict[str, Any]:
    """Add a user as a watcher to an issue. The user will receive notifications about changes to the issue. If no user is specified, the calling user is added as the watcher."""

    # Construct request model with validation
    try:
        _request = _models.AddWatcherRequest(
            path=_models.AddWatcherRequestPath(issue_id_or_key=issue_id_or_key),
            body=_models.AddWatcherRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_issue_watcher: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/issue/{issueIdOrKey}/watchers", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/issue/{issueIdOrKey}/watchers"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_issue_watcher")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_issue_watcher", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_issue_watcher",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue watchers
@mcp.tool()
async def remove_issue_watcher(
    issue_id_or_key: str = Field(..., alias="issueIdOrKey", description="The issue identifier, either the numeric ID or the project key followed by issue number (e.g., PROJ-123)."),
    account_id: str | None = Field(None, alias="accountId", description="The account ID of the user, which uniquely identifies the user across all Atlassian products. For example, *5b10ac8d82e05b22cc7d4ef5*. Required.", max_length=128),
) -> dict[str, Any]:
    """Remove a user from watching an issue. Requires the 'Allow users to watch issues' option to be enabled in Jira's general configuration."""

    # Construct request model with validation
    try:
        _request = _models.RemoveWatcherRequest(
            path=_models.RemoveWatcherRequestPath(issue_id_or_key=issue_id_or_key),
            query=_models.RemoveWatcherRequestQuery(account_id=account_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_issue_watcher: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/issue/{issueIdOrKey}/watchers", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/issue/{issueIdOrKey}/watchers"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_issue_watcher")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_issue_watcher", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_issue_watcher",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue worklogs
@mcp.tool()
async def list_issue_worklogs(
    issue_id_or_key: str = Field(..., alias="issueIdOrKey", description="The issue identifier, either the numeric ID or the project key (e.g., PROJ-123)."),
    start_at: str | None = Field(None, alias="startAt", description="The zero-based index for pagination, allowing you to retrieve results starting from a specific position in the list. Defaults to 0 (first page)."),
    max_results: str | None = Field(None, alias="maxResults", description="The maximum number of worklogs to return per page. Defaults to 5000 if not specified."),
    started_after: str | None = Field(None, alias="startedAfter", description="Filter to return only worklogs that started on or after this date and time, specified as a UNIX timestamp in milliseconds."),
    started_before: str | None = Field(None, alias="startedBefore", description="Filter to return only worklogs that started before this date and time, specified as a UNIX timestamp in milliseconds."),
) -> dict[str, Any]:
    """Retrieve time tracking worklogs for an issue, ordered chronologically from oldest to newest. Optionally filter worklogs by start date range using UNIX timestamps in milliseconds."""

    _start_at = _parse_int(start_at)
    _max_results = _parse_int(max_results)
    _started_after = _parse_int(started_after)
    _started_before = _parse_int(started_before)

    # Construct request model with validation
    try:
        _request = _models.GetIssueWorklogRequest(
            path=_models.GetIssueWorklogRequestPath(issue_id_or_key=issue_id_or_key),
            query=_models.GetIssueWorklogRequestQuery(start_at=_start_at, max_results=_max_results, started_after=_started_after, started_before=_started_before)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_issue_worklogs: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/issue/{issueIdOrKey}/worklog", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/issue/{issueIdOrKey}/worklog"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_issue_worklogs")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_issue_worklogs", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_issue_worklogs",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue worklogs
@mcp.tool()
async def record_worklog(
    issue_id_or_key: str = Field(..., alias="issueIdOrKey", description="The issue ID or key to record work against."),
    notify_users: bool | None = Field(None, alias="notifyUsers", description="Whether to notify users watching the issue via email about the worklog entry. Defaults to true."),
    adjust_estimate: Literal["new", "leave", "manual", "auto"] | None = Field(None, alias="adjustEstimate", description="How to adjust the issue's remaining time estimate: 'new' sets it to a specific value, 'leave' keeps it unchanged, 'manual' reduces it by a specified amount, or 'auto' reduces it by the time spent in this worklog. Defaults to 'auto'."),
    new_estimate: str | None = Field(None, alias="newEstimate", description="The new remaining time estimate for the issue when adjustEstimate is 'new'. Specify as days (e.g., 2d), hours (e.g., 3h), or minutes (e.g., 30m). Required only when adjustEstimate is 'new'."),
    reduce_by: str | None = Field(None, alias="reduceBy", description="The amount to reduce the issue's remaining estimate by when adjustEstimate is 'manual'. Specify as days (e.g., 2d), hours (e.g., 3h), or minutes (e.g., 30m). Required only when adjustEstimate is 'manual'."),
    override_editable_flag: bool | None = Field(None, alias="overrideEditableFlag", description="Whether to force adding the worklog even if the issue is not editable (e.g., closed). Only available to Connect and Forge app users with Administer Jira permission. Defaults to false."),
    comment: Any | None = Field(None, description="An optional comment about the worklog in Atlassian Document Format."),
    started: str | None = Field(None, description="The date and time when the work effort started, in ISO 8601 format. Required when creating a worklog."),
    visibility: _models.AddWorklogBodyVisibility | None = Field(None, description="Optional visibility restrictions for the worklog, such as restricting it to specific users or groups."),
    time_spent: str | None = Field(None, alias="timeSpent", description="The time spent working on the issue as days (\\#d), hours (\\#h), or minutes (\\#m or \\#). Required when creating a worklog if `timeSpentSeconds` isn't provided. Optional when updating a worklog. Cannot be provided if `timeSpentSecond` is provided."),
    time_spent_seconds: str | None = Field(None, alias="timeSpentSeconds", description="The time in seconds spent working on the issue. Required when creating a worklog if `timeSpent` isn't provided. Optional when updating a worklog. Cannot be provided if `timeSpent` is provided."),
) -> dict[str, Any]:
    """Record time spent working on an issue. Time tracking must be enabled in Jira for this operation to succeed. The worklog can optionally update the issue's remaining time estimate based on the time recorded."""

    _time_spent_seconds = _parse_int(time_spent_seconds)

    # Construct request model with validation
    try:
        _request = _models.AddWorklogRequest(
            path=_models.AddWorklogRequestPath(issue_id_or_key=issue_id_or_key),
            query=_models.AddWorklogRequestQuery(notify_users=notify_users, adjust_estimate=adjust_estimate, new_estimate=new_estimate, reduce_by=reduce_by, override_editable_flag=override_editable_flag),
            body=_models.AddWorklogRequestBody(comment=comment, started=started, visibility=visibility, time_spent=time_spent, time_spent_seconds=_time_spent_seconds)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for record_worklog: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/issue/{issueIdOrKey}/worklog", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/issue/{issueIdOrKey}/worklog"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("record_worklog")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("record_worklog", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="record_worklog",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue worklogs
@mcp.tool()
async def delete_worklogs(
    issue_id_or_key: str = Field(..., alias="issueIdOrKey", description="The issue ID or key identifying which issue to delete worklogs from."),
    ids: Annotated[list[int], AfterValidator(_check_unique_items)] = Field(..., description="A list of worklog IDs to delete. All worklogs must belong to the specified issue. Maximum of 5000 IDs per request."),
    adjust_estimate: Literal["leave", "auto"] | None = Field(None, alias="adjustEstimate", description="Controls how the issue's time estimate is updated after deletion. Use 'leave' to keep the estimate unchanged, or 'auto' to automatically reduce it by the total time spent across all deleted worklogs. Defaults to 'auto'."),
    override_editable_flag: bool | None = Field(None, alias="overrideEditableFlag", description="Set to true to force deletion of worklogs even if the issue is not editable (e.g., closed issues). Only available to Connect and Forge app users with admin permission. Defaults to false."),
) -> dict[str, Any]:
    """Permanently delete multiple worklogs from an issue. This experimental operation supports bulk deletion of up to 5000 worklogs at once, with no notifications sent to users. Time tracking must be enabled in Jira for this operation to succeed."""

    # Construct request model with validation
    try:
        _request = _models.BulkDeleteWorklogsRequest(
            path=_models.BulkDeleteWorklogsRequestPath(issue_id_or_key=issue_id_or_key),
            query=_models.BulkDeleteWorklogsRequestQuery(adjust_estimate=adjust_estimate, override_editable_flag=override_editable_flag),
            body=_models.BulkDeleteWorklogsRequestBody(ids=ids)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_worklogs: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/issue/{issueIdOrKey}/worklog", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/issue/{issueIdOrKey}/worklog"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_worklogs")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_worklogs", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_worklogs",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue worklogs
@mcp.tool()
async def move_worklogs(
    issue_id_or_key: str = Field(..., alias="issueIdOrKey", description="The issue ID or key of the source issue containing the worklogs to move."),
    adjust_estimate: Literal["leave", "auto"] | None = Field(None, alias="adjustEstimate", description="Determines how to update time estimates on both issues. Use 'leave' to keep estimates unchanged, or 'auto' to reduce the source issue estimate by the total time spent and increase the destination issue estimate accordingly. Defaults to 'auto'."),
    override_editable_flag: bool | None = Field(None, alias="overrideEditableFlag", description="When true, allows moving worklogs even if the source or destination issues are not editable (e.g., closed issues). Only available to Connect and Forge app users with admin permission. Defaults to false."),
    issue_id_or_key2: str | None = Field(None, alias="issueIdOrKey", description="The issue ID or key of the destination issue where worklogs will be moved to."),
    ids: Annotated[list[int], AfterValidator(_check_unique_items)] | None = Field(None, description="A list of worklog IDs to move. Maximum of 5000 worklogs per request. Worklogs with attachments or project role visibility restrictions cannot be moved."),
) -> dict[str, Any]:
    """Moves a list of worklogs from one issue to another. This experimental operation has limitations: maximum 5000 worklogs per request, no support for worklogs with attachments or project role restrictions, and no notifications, webhooks, or issue history are generated. Time tracking must be enabled in Jira."""

    # Construct request model with validation
    try:
        _request = _models.BulkMoveWorklogsRequest(
            path=_models.BulkMoveWorklogsRequestPath(issue_id_or_key=issue_id_or_key),
            query=_models.BulkMoveWorklogsRequestQuery(adjust_estimate=adjust_estimate, override_editable_flag=override_editable_flag),
            body=_models.BulkMoveWorklogsRequestBody(issue_id_or_key2=issue_id_or_key2, ids=ids)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for move_worklogs: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/issue/{issueIdOrKey}/worklog/move", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/issue/{issueIdOrKey}/worklog/move"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("move_worklogs")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("move_worklogs", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="move_worklogs",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue worklogs
@mcp.tool()
async def get_worklog(
    issue_id_or_key: str = Field(..., alias="issueIdOrKey", description="The issue identifier, either the numeric ID or the human-readable key (e.g., PROJ-123)."),
    id_: str = Field(..., alias="id", description="The unique identifier of the worklog entry to retrieve."),
) -> dict[str, Any]:
    """Retrieve a specific worklog entry for an issue. Time tracking must be enabled in Jira for this operation to succeed."""

    # Construct request model with validation
    try:
        _request = _models.GetWorklogRequest(
            path=_models.GetWorklogRequestPath(issue_id_or_key=issue_id_or_key, id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_worklog: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/issue/{issueIdOrKey}/worklog/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/issue/{issueIdOrKey}/worklog/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_worklog")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_worklog", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_worklog",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue worklogs
@mcp.tool()
async def update_worklog(
    issue_id_or_key: str = Field(..., alias="issueIdOrKey", description="The issue identifier, either the numeric ID or the project key (e.g., PROJ-123)."),
    id_: str = Field(..., alias="id", description="The unique identifier of the worklog entry to update."),
    notify_users: bool | None = Field(None, alias="notifyUsers", description="Whether to send email notifications to users watching the issue. Defaults to true."),
    adjust_estimate: Literal["new", "leave", "manual", "auto"] | None = Field(None, alias="adjustEstimate", description="How to adjust the issue's remaining time estimate: 'new' sets a specific value, 'leave' keeps it unchanged, or 'auto' adjusts it based on the difference in time spent. Defaults to 'auto'."),
    new_estimate: str | None = Field(None, alias="newEstimate", description="The new remaining time estimate for the issue when adjustEstimate is set to 'new'. Specify as days (d), hours (h), or minutes (m). Required only when adjustEstimate is 'new'."),
    override_editable_flag: bool | None = Field(None, alias="overrideEditableFlag", description="Whether to allow updating the worklog even if the issue is not editable (e.g., closed). Only available to Connect and Forge app users with Administer Jira permission. Defaults to false."),
    comment: Any | None = Field(None, description="A comment about the worklog in Atlassian Document Format. Optional for updates."),
    started: str | None = Field(None, description="The date and time when the worklog effort started, in ISO 8601 format. Optional when updating an existing worklog."),
    visibility: _models.UpdateWorklogBodyVisibility | None = Field(None, description="Visibility restrictions for the worklog, such as limiting access to specific groups or roles. Optional for updates."),
) -> dict[str, Any]:
    """Updates an existing worklog entry for an issue. Requires time tracking to be enabled in Jira and appropriate permissions to edit the worklog."""

    # Construct request model with validation
    try:
        _request = _models.UpdateWorklogRequest(
            path=_models.UpdateWorklogRequestPath(issue_id_or_key=issue_id_or_key, id_=id_),
            query=_models.UpdateWorklogRequestQuery(notify_users=notify_users, adjust_estimate=adjust_estimate, new_estimate=new_estimate, override_editable_flag=override_editable_flag),
            body=_models.UpdateWorklogRequestBody(comment=comment, started=started, visibility=visibility)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_worklog: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/issue/{issueIdOrKey}/worklog/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/issue/{issueIdOrKey}/worklog/{id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_worklog")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_worklog", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_worklog",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue worklogs
@mcp.tool()
async def remove_worklog(
    issue_id_or_key: str = Field(..., alias="issueIdOrKey", description="The issue identifier, either the numeric ID or the project key followed by issue number (e.g., PROJ-123)."),
    id_: str = Field(..., alias="id", description="The unique identifier of the worklog entry to delete."),
    notify_users: bool | None = Field(None, alias="notifyUsers", description="Whether to send email notifications to users watching the issue. Defaults to true."),
    adjust_estimate: Literal["new", "leave", "manual", "auto"] | None = Field(None, alias="adjustEstimate", description="How to adjust the issue's remaining time estimate after deletion. Use 'auto' to reduce by the deleted worklog's time, 'new' to set a specific value, 'manual' to increase by an amount, or 'leave' to keep unchanged. Defaults to 'auto'."),
    new_estimate: str | None = Field(None, alias="newEstimate", description="The new remaining time estimate for the issue when adjustEstimate is set to 'new'. Specify as a duration using days (d), hours (h), or minutes (m)."),
    increase_by: str | None = Field(None, alias="increaseBy", description="The amount to increase the remaining time estimate when adjustEstimate is set to 'manual'. Specify as a duration using days (d), hours (h), or minutes (m)."),
    override_editable_flag: bool | None = Field(None, alias="overrideEditableFlag", description="Whether to allow deletion even if the issue is not editable (e.g., closed or read-only). Only available to Connect and Forge app users with admin permission. Defaults to false."),
) -> dict[str, Any]:
    """Remove a worklog entry from an issue and optionally adjust the issue's time estimate. Requires time tracking to be enabled in Jira and appropriate permissions to delete worklogs."""

    # Construct request model with validation
    try:
        _request = _models.DeleteWorklogRequest(
            path=_models.DeleteWorklogRequestPath(issue_id_or_key=issue_id_or_key, id_=id_),
            query=_models.DeleteWorklogRequestQuery(notify_users=notify_users, adjust_estimate=adjust_estimate, new_estimate=new_estimate, increase_by=increase_by, override_editable_flag=override_editable_flag)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_worklog: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/issue/{issueIdOrKey}/worklog/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/issue/{issueIdOrKey}/worklog/{id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_worklog")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_worklog", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_worklog",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue worklog properties
@mcp.tool()
async def list_worklog_property_keys(
    issue_id_or_key: str = Field(..., alias="issueIdOrKey", description="The issue identifier, which can be either the numeric issue ID or the issue key (e.g., PROJECT-123)."),
    worklog_id: str = Field(..., alias="worklogId", description="The unique identifier of the worklog entry within the specified issue."),
) -> dict[str, Any]:
    """Retrieves all property keys associated with a specific worklog entry. Use this to discover what custom properties are available for a worklog before retrieving their values."""

    # Construct request model with validation
    try:
        _request = _models.GetWorklogPropertyKeysRequest(
            path=_models.GetWorklogPropertyKeysRequestPath(issue_id_or_key=issue_id_or_key, worklog_id=worklog_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_worklog_property_keys: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/issue/{issueIdOrKey}/worklog/{worklogId}/properties", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/issue/{issueIdOrKey}/worklog/{worklogId}/properties"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_worklog_property_keys")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_worklog_property_keys", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_worklog_property_keys",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue worklog properties
@mcp.tool()
async def get_worklog_property(
    issue_id_or_key: str = Field(..., alias="issueIdOrKey", description="The issue identifier, either the numeric ID or the human-readable key (e.g., PROJ-123)."),
    worklog_id: str = Field(..., alias="worklogId", description="The unique identifier of the worklog entry from which to retrieve the property."),
    property_key: str = Field(..., alias="propertyKey", description="The name of the property to retrieve from the worklog."),
) -> dict[str, Any]:
    """Retrieves a specific property value associated with a worklog entry. Requires appropriate project and issue permissions, plus any worklog visibility restrictions must be satisfied."""

    # Construct request model with validation
    try:
        _request = _models.GetWorklogPropertyRequest(
            path=_models.GetWorklogPropertyRequestPath(issue_id_or_key=issue_id_or_key, worklog_id=worklog_id, property_key=property_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_worklog_property: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/issue/{issueIdOrKey}/worklog/{worklogId}/properties/{propertyKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/issue/{issueIdOrKey}/worklog/{worklogId}/properties/{propertyKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_worklog_property")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_worklog_property", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_worklog_property",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue worklog properties
@mcp.tool()
async def remove_worklog_property(
    issue_id_or_key: str = Field(..., alias="issueIdOrKey", description="The issue identifier, either the numeric ID or the project key followed by issue number (e.g., PROJ-123)."),
    worklog_id: str = Field(..., alias="worklogId", description="The unique identifier of the worklog entry from which the property will be removed."),
    property_key: str = Field(..., alias="propertyKey", description="The identifier of the custom property to delete from the worklog."),
) -> dict[str, Any]:
    """Removes a custom property from a worklog entry. Requires appropriate project and worklog visibility permissions."""

    # Construct request model with validation
    try:
        _request = _models.DeleteWorklogPropertyRequest(
            path=_models.DeleteWorklogPropertyRequestPath(issue_id_or_key=issue_id_or_key, worklog_id=worklog_id, property_key=property_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_worklog_property: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/issue/{issueIdOrKey}/worklog/{worklogId}/properties/{propertyKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/issue/{issueIdOrKey}/worklog/{worklogId}/properties/{propertyKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_worklog_property")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_worklog_property", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_worklog_property",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue links
@mcp.tool()
async def create_issue_link(
    body: Any | None = Field(None, description="The comment text to add to the outward issue, formatted as Atlassian Document Format. Optional on creation."),
    visibility: _models.LinkIssuesBodyCommentVisibility | None = Field(None, description="The group or role to which the comment visibility is restricted. Optional; if omitted, the comment is visible to all users with permission to view the issue."),
    inward_issue_key: str | None = Field(None, alias="inwardIssueKey", description="The key of the inward (destination) issue. Required unless the issue ID is provided instead."),
    outward_issue_key: str | None = Field(None, alias="outwardIssueKey", description="The key of the outward (source) issue. Required unless the issue ID is provided instead."),
    id_: str | None = Field(None, alias="id", description="The ID of the issue link type and is used as follows:\n\n *  In the [ issueLink](#api-rest-api-3-issueLink-post) resource it is the type of issue link. Required on create when `name` isn't provided. Otherwise, read only.\n *  In the [ issueLinkType](#api-rest-api-3-issueLinkType-post) resource it is read only."),
    name: str | None = Field(None, description="The name of the issue link type and is used as follows:\n\n *  In the [ issueLink](#api-rest-api-3-issueLink-post) resource it is the type of issue link. Required on create when `id` isn't provided. Otherwise, read only.\n *  In the [ issueLinkType](#api-rest-api-3-issueLinkType-post) resource it is required on create and optional on update. Otherwise, read only."),
) -> dict[str, Any]:
    """Creates a link between two issues to indicate a relationship. Optionally adds a comment to the outward issue. Requires Issue Linking to be enabled on the site."""

    # Construct request model with validation
    try:
        _request = _models.LinkIssuesRequest(
            body=_models.LinkIssuesRequestBody(comment=_models.LinkIssuesRequestBodyComment(body=body, visibility=visibility) if any(v is not None for v in [body, visibility]) else None,
                inward_issue=_models.LinkIssuesRequestBodyInwardIssue(key=inward_issue_key) if any(v is not None for v in [inward_issue_key]) else None,
                outward_issue=_models.LinkIssuesRequestBodyOutwardIssue(key=outward_issue_key) if any(v is not None for v in [outward_issue_key]) else None,
                type_=_models.LinkIssuesRequestBodyType(id_=id_, name=name) if any(v is not None for v in [id_, name]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_issue_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/issueLink"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_issue_link")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_issue_link", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_issue_link",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue links
@mcp.tool()
async def get_issue_link(link_id: str = Field(..., alias="linkId", description="The unique identifier of the issue link to retrieve.")) -> dict[str, Any]:
    """Retrieves details about a specific issue link by its ID. Returns the link information if you have permission to view both linked issues."""

    # Construct request model with validation
    try:
        _request = _models.GetIssueLinkRequest(
            path=_models.GetIssueLinkRequestPath(link_id=link_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_issue_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/issueLink/{linkId}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/issueLink/{linkId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_issue_link")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_issue_link", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_issue_link",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue links
@mcp.tool()
async def remove_issue_link(link_id: str = Field(..., alias="linkId", description="The unique identifier of the issue link to delete.")) -> dict[str, Any]:
    """Removes a link between two issues. Requires browse and link issue permissions for the affected projects, and view access if issue-level security is configured."""

    # Construct request model with validation
    try:
        _request = _models.DeleteIssueLinkRequest(
            path=_models.DeleteIssueLinkRequestPath(link_id=link_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_issue_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/issueLink/{linkId}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/issueLink/{linkId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_issue_link")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_issue_link", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_issue_link",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue link types
@mcp.tool()
async def list_issue_link_types() -> dict[str, Any]:
    """Retrieves all available issue link types configured in the Jira instance. Requires issue linking to be enabled and the user to have Browse projects permission."""

    # Extract parameters for API call
    _http_path = "/rest/api/3/issueLinkType"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_issue_link_types")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_issue_link_types", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_issue_link_types",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue link types
@mcp.tool()
async def get_issue_link_type(issue_link_type_id: str = Field(..., alias="issueLinkTypeId", description="The unique identifier of the issue link type to retrieve.")) -> dict[str, Any]:
    """Retrieves the details of a specific issue link type by its ID. Requires issue linking to be enabled on the site and the user to have Browse projects permission."""

    # Construct request model with validation
    try:
        _request = _models.GetIssueLinkTypeRequest(
            path=_models.GetIssueLinkTypeRequestPath(issue_link_type_id=issue_link_type_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_issue_link_type: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/issueLinkType/{issueLinkTypeId}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/issueLinkType/{issueLinkTypeId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_issue_link_type")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_issue_link_type", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_issue_link_type",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue link types
@mcp.tool()
async def delete_issue_link_type(issue_link_type_id: str = Field(..., alias="issueLinkTypeId", description="The unique identifier of the issue link type to delete.")) -> dict[str, Any]:
    """Permanently deletes an issue link type from your Jira instance. Requires issue linking to be enabled and Administer Jira global permission."""

    # Construct request model with validation
    try:
        _request = _models.DeleteIssueLinkTypeRequest(
            path=_models.DeleteIssueLinkTypeRequestPath(issue_link_type_id=issue_link_type_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_issue_link_type: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/issueLinkType/{issueLinkTypeId}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/issueLinkType/{issueLinkTypeId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_issue_link_type")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_issue_link_type", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_issue_link_type",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issues
@mcp.tool()
async def export_archived_issues(
    date_after: str = Field(..., alias="dateAfter", description="Include only issues archived on or after this date. Specify in YYYY-MM-DD format."),
    date_before: str = Field(..., alias="dateBefore", description="Include only issues archived on or before this date. Specify in YYYY-MM-DD format."),
    archived_by: list[str] | None = Field(None, alias="archivedBy", description="Filter results to include only issues archived by specific user account IDs. Provide as a list of account identifiers."),
    issue_types: list[str] | None = Field(None, alias="issueTypes", description="Filter results to include only issues of specified issue type IDs. Provide as a list of type identifiers."),
    projects: list[str] | None = Field(None, description="Filter results to include only issues from specified project keys. Provide as a list of project key identifiers."),
    reporters: list[str] | None = Field(None, description="Filter results to include only issues reported by specific user account IDs. Provide as a list of account identifiers."),
) -> dict[str, Any]:
    """Export archived issues to a CSV file for download. An admin can filter archived issues by date range, project, issue type, reporter, or archival user, and will receive an email with a download link upon completion."""

    # Construct request model with validation
    try:
        _request = _models.ExportArchivedIssuesRequest(
            body=_models.ExportArchivedIssuesRequestBody(archived_by=archived_by, issue_types=issue_types, projects=projects, reporters=reporters,
                archived_date_range=_models.ExportArchivedIssuesRequestBodyArchivedDateRange(date_after=date_after, date_before=date_before))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for export_archived_issues: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/issues/archive/export"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("export_archived_issues")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("export_archived_issues", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="export_archived_issues",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue types
@mcp.tool()
async def list_issue_types() -> dict[str, Any]:
    """Retrieve all issue types available to the authenticated user. The returned issue types depend on the user's permissions: administrators see all types, users with project browse permissions see types for those projects, and anonymous users see types for projects with anonymous browse access."""

    # Extract parameters for API call
    _http_path = "/rest/api/3/issuetype"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_issue_types")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_issue_types", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_issue_types",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue types
@mcp.tool()
async def list_issue_types_project(
    project_id: str = Field(..., alias="projectId", description="The numeric identifier of the project. This is a 64-bit integer that uniquely identifies the project in your Jira instance."),
    level: str | None = Field(None, description="Optional filter to retrieve issue types at a specific hierarchy level: use -1 for Subtasks, 0 for Base issue types, or 1 for Epics. Omit this parameter to retrieve all issue types regardless of level."),
) -> dict[str, Any]:
    """Retrieves all issue types available for a specific project, optionally filtered by type hierarchy level (Subtask, Base, or Epic)."""

    _project_id = _parse_int(project_id)
    _level = _parse_int(level)

    # Construct request model with validation
    try:
        _request = _models.GetIssueTypesForProjectRequest(
            query=_models.GetIssueTypesForProjectRequestQuery(project_id=_project_id, level=_level)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_issue_types_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/issuetype/project"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_issue_types_project")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_issue_types_project", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_issue_types_project",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue types
@mcp.tool()
async def get_issue_type(id_: str = Field(..., alias="id", description="The unique identifier of the issue type to retrieve.")) -> dict[str, Any]:
    """Retrieves detailed information about a specific issue type by its ID. Requires either Browse projects permission in an associated project or Jira administrator access."""

    # Construct request model with validation
    try:
        _request = _models.GetIssueTypeRequest(
            path=_models.GetIssueTypeRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_issue_type: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/issuetype/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/issuetype/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_issue_type")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_issue_type", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_issue_type",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue types
@mcp.tool()
async def delete_issue_type(
    id_: str = Field(..., alias="id", description="The unique identifier of the issue type to delete."),
    alternative_issue_type_id: str | None = Field(None, alias="alternativeIssueTypeId", description="The unique identifier of the issue type to use as a replacement for any issues currently using the deleted type. Required if the issue type being deleted is in use."),
) -> dict[str, Any]:
    """Deletes an issue type from your Jira instance. If the issue type is currently in use, all associated issues are automatically reassigned to a replacement issue type that you specify."""

    # Construct request model with validation
    try:
        _request = _models.DeleteIssueTypeRequest(
            path=_models.DeleteIssueTypeRequestPath(id_=id_),
            query=_models.DeleteIssueTypeRequestQuery(alternative_issue_type_id=alternative_issue_type_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_issue_type: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/issuetype/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/issuetype/{id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_issue_type")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_issue_type", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_issue_type",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue types
@mcp.tool()
async def list_alternative_issue_types(id_: str = Field(..., alias="id", description="The unique identifier of the issue type for which to find compatible alternatives.")) -> dict[str, Any]:
    """Retrieve a list of issue types that can replace a given issue type. The alternatives are those sharing the same workflow scheme, field configuration scheme, and screen scheme."""

    # Construct request model with validation
    try:
        _request = _models.GetAlternativeIssueTypesRequest(
            path=_models.GetAlternativeIssueTypesRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_alternative_issue_types: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/issuetype/{id}/alternatives", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/issuetype/{id}/alternatives"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_alternative_issue_types")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_alternative_issue_types", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_alternative_issue_types",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue types
@mcp.tool()
async def upload_issue_type_avatar(
    id_: str = Field(..., alias="id", description="The unique identifier of the issue type to which the avatar will be assigned."),
    size: str = Field(..., description="The width and height in pixels of the square crop region. This determines the size of the cropped area before resizing."),
    x: str | None = Field(None, description="The horizontal pixel position of the top-left corner of the crop region. Defaults to 0 if not specified."),
    y: str | None = Field(None, description="The vertical pixel position of the top-left corner of the crop region. Defaults to 0 if not specified."),
) -> dict[str, Any]:
    """Upload and set a custom avatar image for an issue type. The image is automatically cropped to a square and resized into multiple formats (16x16, 24x24, 32x32, 48x48 pixels). Requires Administer Jira global permission."""

    _size = _parse_int(size)
    _x = _parse_int(x)
    _y = _parse_int(y)

    # Construct request model with validation
    try:
        _request = _models.CreateIssueTypeAvatarRequest(
            path=_models.CreateIssueTypeAvatarRequestPath(id_=id_),
            query=_models.CreateIssueTypeAvatarRequestQuery(x=_x, y=_y, size=_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for upload_issue_type_avatar: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/issuetype/{id}/avatar2", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/issuetype/{id}/avatar2"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("upload_issue_type_avatar")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("upload_issue_type_avatar", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="upload_issue_type_avatar",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue type properties
@mcp.tool()
async def list_issue_type_property_keys(issue_type_id: str = Field(..., alias="issueTypeId", description="The unique identifier of the issue type whose property keys you want to retrieve.")) -> dict[str, Any]:
    """Retrieves all property keys stored on a specific issue type. Property keys are identifiers for custom data attached to the issue type entity."""

    # Construct request model with validation
    try:
        _request = _models.GetIssueTypePropertyKeysRequest(
            path=_models.GetIssueTypePropertyKeysRequestPath(issue_type_id=issue_type_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_issue_type_property_keys: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/issuetype/{issueTypeId}/properties", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/issuetype/{issueTypeId}/properties"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_issue_type_property_keys")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_issue_type_property_keys", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_issue_type_property_keys",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue type properties
@mcp.tool()
async def get_issue_type_property(
    issue_type_id: str = Field(..., alias="issueTypeId", description="The unique identifier of the issue type whose property you want to retrieve."),
    property_key: str = Field(..., alias="propertyKey", description="The key identifying which property to retrieve. Use the list issue type property keys operation to discover available property keys for an issue type."),
) -> dict[str, Any]:
    """Retrieves a specific property value stored on an issue type by its key. Returns both the key and value of the requested issue type property."""

    # Construct request model with validation
    try:
        _request = _models.GetIssueTypePropertyRequest(
            path=_models.GetIssueTypePropertyRequestPath(issue_type_id=issue_type_id, property_key=property_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_issue_type_property: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/issuetype/{issueTypeId}/properties/{propertyKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/issuetype/{issueTypeId}/properties/{propertyKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_issue_type_property")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_issue_type_property", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_issue_type_property",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue type schemes
@mcp.tool()
async def list_issue_type_schemes(
    start_at: str | None = Field(None, alias="startAt", description="The starting position for pagination, where 0 is the first item. Use this to retrieve subsequent pages of results."),
    max_results: str | None = Field(None, alias="maxResults", description="The number of issue type schemes to return per page. Defaults to 50 items per page."),
    order_by: Literal["name", "-name", "+name", "id", "-id", "+id"] | None = Field(None, alias="orderBy", description="Sort results by issue type scheme name or ID, with optional ascending (+) or descending (-) direction. Defaults to sorting by ID."),
    query_string: str | None = Field(None, alias="queryString", description="Filter results by performing a case-insensitive partial match against issue type scheme names."),
) -> dict[str, Any]:
    """Retrieve a paginated list of issue type schemes used in classic Jira projects. Requires Administer Jira global permission."""

    _start_at = _parse_int(start_at)
    _max_results = _parse_int(max_results)

    # Construct request model with validation
    try:
        _request = _models.GetAllIssueTypeSchemesRequest(
            query=_models.GetAllIssueTypeSchemesRequestQuery(start_at=_start_at, max_results=_max_results, order_by=order_by, query_string=query_string)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_issue_type_schemes: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/issuetypescheme"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_issue_type_schemes")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_issue_type_schemes", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_issue_type_schemes",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue type schemes
@mcp.tool()
async def list_issue_type_schemes_for_projects(
    project_id: Annotated[list[int], AfterValidator(_check_unique_items)] = Field(..., alias="projectId", description="One or more project IDs to filter schemes by. Provide multiple IDs as an ampersand-separated list in the query string."),
    start_at: str | None = Field(None, alias="startAt", description="The starting position for pagination, where 0 represents the first item. Use this to navigate through large result sets."),
    max_results: str | None = Field(None, alias="maxResults", description="The number of results to return per page. Defaults to 50 items if not specified."),
) -> dict[str, Any]:
    """Retrieve issue type schemes used by specified projects in classic Jira instances. Returns a paginated list showing which projects use each scheme."""

    _start_at = _parse_int(start_at)
    _max_results = _parse_int(max_results)

    # Construct request model with validation
    try:
        _request = _models.GetIssueTypeSchemeForProjectsRequest(
            query=_models.GetIssueTypeSchemeForProjectsRequestQuery(start_at=_start_at, max_results=_max_results, project_id=project_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_issue_type_schemes_for_projects: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/issuetypescheme/project"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_issue_type_schemes_for_projects")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_issue_type_schemes_for_projects", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_issue_type_schemes_for_projects",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: JQL
@mcp.tool()
async def list_jql_autocomplete_data() -> dict[str, Any]:
    """Retrieve JQL field and function reference data for building and validating JQL queries programmatically. Returns comprehensive metadata including field definitions, available functions, and reserved words to support dynamic query construction."""

    # Extract parameters for API call
    _http_path = "/rest/api/3/jql/autocompletedata"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_jql_autocomplete_data")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_jql_autocomplete_data", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_jql_autocomplete_data",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: JQL
@mcp.tool()
async def list_jql_autocomplete_data_filtered(
    include_collapsed_fields: bool | None = Field(None, alias="includeCollapsedFields", description="Include collapsed fields that allow searches across multiple fields with the same name and type. Disabled by default."),
    project_ids: list[int] | None = Field(None, alias="projectIds", description="Filter returned field details by one or more project IDs. Invalid project IDs are ignored; system fields are always included regardless of this filter."),
) -> dict[str, Any]:
    """Retrieve JQL field and function reference data to support programmatic query building and validation. Returns system fields always, with optional filtering by project and support for collapsed fields that enable cross-field searches."""

    # Construct request model with validation
    try:
        _request = _models.GetAutoCompletePostRequest(
            body=_models.GetAutoCompletePostRequestBody(include_collapsed_fields=include_collapsed_fields, project_ids=project_ids)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_jql_autocomplete_data_filtered: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/jql/autocompletedata"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_jql_autocomplete_data_filtered")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_jql_autocomplete_data_filtered", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_jql_autocomplete_data_filtered",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: JQL
@mcp.tool()
async def get_jql_autocomplete_suggestions(
    field_name: str | None = Field(None, alias="fieldName", description="The JQL field name to get suggestions for (e.g., 'reporter'). Required to initiate any suggestion query."),
    field_value: str | None = Field(None, alias="fieldValue", description="Partial field value entered by the user to filter suggestions. When provided with fieldName, returns values containing this text."),
    predicate_name: str | None = Field(None, alias="predicateName", description="The CHANGED operator predicate name for which to generate suggestions. Valid values are 'by', 'from', or 'to'. Use with fieldName to get predicate-specific suggestions."),
    predicate_value: str | None = Field(None, alias="predicateValue", description="Partial predicate value entered by the user to filter suggestions. When provided with predicateName and fieldName, returns predicate values containing this text."),
) -> dict[str, Any]:
    """Retrieve JQL search autocomplete suggestions for a field, optionally filtered by field value or predicate criteria. Use this to populate autocomplete dropdowns when users are constructing JQL queries."""

    # Construct request model with validation
    try:
        _request = _models.GetFieldAutoCompleteForQueryStringRequest(
            query=_models.GetFieldAutoCompleteForQueryStringRequestQuery(field_name=field_name, field_value=field_value, predicate_name=predicate_name, predicate_value=predicate_value)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_jql_autocomplete_suggestions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/jql/autocompletedata/suggestions"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_jql_autocomplete_suggestions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_jql_autocomplete_suggestions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_jql_autocomplete_suggestions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue search
@mcp.tool()
async def filter_issues_by_jql(
    issue_ids: Annotated[list[int], AfterValidator(_check_unique_items)] = Field(..., alias="issueIds", description="A list of issue IDs to evaluate against the JQL queries. Each ID must correspond to an issue the user has permission to view."),
    jqls: list[str] = Field(..., description="A list of JQL (Jira Query Language) queries to match against the provided issues. Each query is evaluated independently for each issue."),
) -> dict[str, Any]:
    """Evaluate whether specified issues match one or more JQL queries. Returns matching results for each issue-query combination, respecting project permissions and issue-level security."""

    # Construct request model with validation
    try:
        _request = _models.MatchIssuesRequest(
            body=_models.MatchIssuesRequestBody(issue_ids=issue_ids, jqls=jqls)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for filter_issues_by_jql: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/jql/match"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("filter_issues_by_jql")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("filter_issues_by_jql", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="filter_issues_by_jql",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: JQL
@mcp.tool()
async def validate_jql_queries(
    validation: Literal["strict", "warn", "none"] = Field(..., description="Validation mode that determines how strictly to validate queries and what to return on errors. Use 'strict' to reject malformed queries entirely, 'warn' to return structure even if errors exist, or 'none' to skip validation and only check syntax."),
    queries: list[str] = Field(..., description="One or more JQL query strings to parse and validate. Each query is processed independently.", min_length=1),
) -> dict[str, Any]:
    """Validates and parses JQL (Jira Query Language) queries to check syntax and structure. Returns parsed query details based on the specified validation mode."""

    # Construct request model with validation
    try:
        _request = _models.ParseJqlQueriesRequest(
            query=_models.ParseJqlQueriesRequestQuery(validation=validation),
            body=_models.ParseJqlQueriesRequestBody(queries=queries)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for validate_jql_queries: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/jql/parse"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("validate_jql_queries")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("validate_jql_queries", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="validate_jql_queries",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Labels
@mcp.tool()
async def list_labels(
    start_at: str | None = Field(None, alias="startAt", description="The starting position for pagination, where 0 represents the first item. Use this to skip earlier results and navigate through pages."),
    max_results: str | None = Field(None, alias="maxResults", description="The maximum number of labels to return in a single page, with a default of 1000 items per page."),
) -> dict[str, Any]:
    """Retrieve a paginated list of all available labels in the system. Use pagination parameters to control which results are returned."""

    _start_at = _parse_int(start_at)
    _max_results = _parse_int(max_results)

    # Construct request model with validation
    try:
        _request = _models.GetAllLabelsRequest(
            query=_models.GetAllLabelsRequestQuery(start_at=_start_at, max_results=_max_results)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_labels: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/label"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_labels")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_labels", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_labels",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Permissions
@mcp.tool()
async def check_permissions(
    project_id: str | None = Field(None, alias="projectId", description="The project ID to check permissions within. When provided, project-level permissions are evaluated for this specific project."),
    issue_id: str | None = Field(None, alias="issueId", description="The issue ID to check permissions within. When provided, permissions are evaluated in the context of this specific issue, with issue-based permissions determined by the user's relationship to the issue."),
    permissions: str | None = Field(None, description="A comma-separated list of permission keys to check (required when querying specific permissions). Use the Get all permissions operation to discover available permission keys."),
    comment_id: str | None = Field(None, alias="commentId", description="The comment ID to check permissions within. Only the BROWSE_PROJECTS permission is supported for comment context. When provided, the user must have both permission to browse the comment and the project permission for the comment's parent issue."),
) -> dict[str, Any]:
    """Check which permissions the authenticated or anonymous user has in a specific context (global, project, issue, or comment). Permissions are evaluated based on the user's roles and the context provided, with issue-based permissions determined by the user's relationship to that issue."""

    # Construct request model with validation
    try:
        _request = _models.GetMyPermissionsRequest(
            query=_models.GetMyPermissionsRequestQuery(project_id=project_id, issue_id=issue_id, permissions=permissions, comment_id=comment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for check_permissions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/mypermissions"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("check_permissions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("check_permissions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="check_permissions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Myself
@mcp.tool()
async def get_user_preference(key: str = Field(..., description="The preference key to retrieve (e.g., jira.user.locale, jira.user.timezone, user.notifications.watcher). Note that some keys like jira.user.locale and jira.user.timezone are deprecated; use the user management API instead to manage timezone and locale.")) -> dict[str, Any]:
    """Retrieves a specific preference value for the current user. Use this to fetch user settings like notifications, locale, or timezone preferences."""

    # Construct request model with validation
    try:
        _request = _models.GetPreferenceRequest(
            query=_models.GetPreferenceRequestQuery(key=key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_user_preference: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/mypreferences"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_user_preference")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_user_preference", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_user_preference",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Myself
@mcp.tool()
async def get_locale() -> dict[str, Any]:
    """Retrieves the locale preference for the current user. If no preference is set, returns the browser locale detected from the Accept-Language header, or the site default locale if no match is found. This operation can be accessed anonymously."""

    # Extract parameters for API call
    _http_path = "/rest/api/3/mypreferences/locale"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_locale")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_locale", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_locale",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Myself
@mcp.tool()
async def get_current_user() -> dict[str, Any]:
    """Retrieves the profile and account details of the currently authenticated user in Jira. This operation requires valid Jira access permissions."""

    # Extract parameters for API call
    _http_path = "/rest/api/3/myself"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_current_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_current_user", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_current_user",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue notification schemes
@mcp.tool()
async def list_notification_scheme_project_mappings(
    start_at: str | None = Field(None, alias="startAt", description="The starting position for pagination, where 0 represents the first item. Use this to navigate through pages of results."),
    max_results: str | None = Field(None, alias="maxResults", description="The number of items to return per page. Defaults to 50 items if not specified."),
    notification_scheme_id: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(None, alias="notificationSchemeId", description="One or more notification scheme IDs to filter the results. Only mappings for these schemes will be returned."),
    project_id: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(None, alias="projectId", description="One or more project IDs to filter the results. Only mappings for these projects will be returned."),
) -> dict[str, Any]:
    """Retrieve a paginated list of projects and their assigned notification schemes. Filter results by specific notification scheme IDs or project IDs, or retrieve all mappings. Only company-managed projects are supported."""

    # Construct request model with validation
    try:
        _request = _models.GetNotificationSchemeToProjectMappingsRequest(
            query=_models.GetNotificationSchemeToProjectMappingsRequestQuery(start_at=start_at, max_results=max_results, notification_scheme_id=notification_scheme_id, project_id=project_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_notification_scheme_project_mappings: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/notificationscheme/project"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_notification_scheme_project_mappings")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_notification_scheme_project_mappings", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_notification_scheme_project_mappings",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Permissions
@mcp.tool()
async def list_permissions() -> dict[str, Any]:
    """Retrieve all available permissions in the system, including global permissions, project-specific permissions, and permissions added by installed plugins. This operation is accessible without authentication."""

    # Extract parameters for API call
    _http_path = "/rest/api/3/permissions"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_permissions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_permissions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_permissions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Permissions
@mcp.tool()
async def check_permissions_bulk(
    global_permissions: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(None, alias="globalPermissions", description="List of global permission keys to check. Only permissions included in this list will be evaluated for the user."),
    project_permissions: Annotated[list[_models.BulkProjectPermissions], AfterValidator(_check_unique_items)] | None = Field(None, alias="projectPermissions", description="Project and issue-specific permissions to check. For each permission, specify the projects and issues to validate access against. Up to 1000 projects and 1000 issues can be checked per request; invalid IDs are ignored."),
) -> dict[str, Any]:
    """Verify which global and project permissions a user has, optionally checking access to specific projects and issues. Returns granted permissions and accessible resources for the specified user or the authenticated user if no account ID is provided."""

    # Construct request model with validation
    try:
        _request = _models.GetBulkPermissionsRequest(
            body=_models.GetBulkPermissionsRequestBody(global_permissions=global_permissions, project_permissions=project_permissions)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for check_permissions_bulk: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/permissions/check"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("check_permissions_bulk")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("check_permissions_bulk", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="check_permissions_bulk",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Permissions
@mcp.tool()
async def list_permitted_projects(permissions: list[str] = Field(..., description="A list of permission keys to filter projects by. Only projects where the user has all specified permissions will be returned. Permission keys should be provided as strings in the array.")) -> dict[str, Any]:
    """Retrieve all projects where the authenticated user has been granted specific permissions. This operation helps identify which projects a user can access based on their assigned permission keys."""

    # Construct request model with validation
    try:
        _request = _models.GetPermittedProjectsRequest(
            body=_models.GetPermittedProjectsRequestBody(permissions=permissions)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_permitted_projects: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/permissions/project"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_permitted_projects")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_permitted_projects", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_permitted_projects",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Plans
@mcp.tool()
async def list_plans(
    include_trashed: bool | None = Field(None, alias="includeTrashed", description="Include trashed plans in the results. By default, only active plans are returned."),
    include_archived: bool | None = Field(None, alias="includeArchived", description="Include archived plans in the results. By default, only active plans are returned."),
    max_results: str | None = Field(None, alias="maxResults", description="Maximum number of plans to return per page. Must be between 1 and 50, defaults to 50."),
) -> dict[str, Any]:
    """Retrieve a paginated list of plans. Requires Jira administrator permissions. Optionally filter results to include trashed or archived plans."""

    _max_results = _parse_int(max_results)

    # Construct request model with validation
    try:
        _request = _models.GetPlansRequest(
            query=_models.GetPlansRequestQuery(include_trashed=include_trashed, include_archived=include_archived, max_results=_max_results)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_plans: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/plans/plan"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_plans")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_plans", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_plans",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Plans
@mcp.tool()
async def create_plan(
    issue_sources: Annotated[list[_models.CreateIssueSourceRequest], AfterValidator(_check_unique_items)] = Field(..., alias="issueSources", description="The issue sources that populate the plan. This determines which issues are included and must be specified as an array of source identifiers or configurations."),
    name: str = Field(..., description="The name of the plan. Must be between 1 and 255 characters.", min_length=1, max_length=255),
    scheduling: _models.CreatePlanBodyScheduling = Field(..., description="Scheduling configuration for the plan, including timeline and release dates. Specifies how issues are scheduled within the plan."),
    cross_project_releases: Annotated[list[_models.CreateCrossProjectReleaseRequest], AfterValidator(_check_unique_items)] | None = Field(None, alias="crossProjectReleases", description="List of cross-project releases to include in the plan. Allows the plan to span multiple projects."),
    custom_fields: Annotated[list[_models.CreateCustomFieldRequest], AfterValidator(_check_unique_items)] | None = Field(None, alias="customFields", description="Custom fields to associate with the plan. Specify as an array of field configurations."),
    exclusion_rules: _models.CreatePlanBodyExclusionRules | None = Field(None, alias="exclusionRules", description="Rules that define which issues should be excluded from the plan based on specified criteria."),
    permissions: Annotated[list[_models.CreatePermissionRequest], AfterValidator(_check_unique_items)] | None = Field(None, description="Access control settings that define which users or groups can view or modify the plan."),
) -> dict[str, Any]:
    """Creates a new plan in Jira with specified issue sources, scheduling configuration, and optional cross-project releases and custom fields. Requires Administer Jira global permission."""

    # Construct request model with validation
    try:
        _request = _models.CreatePlanRequest(
            body=_models.CreatePlanRequestBody(cross_project_releases=cross_project_releases, custom_fields=custom_fields, exclusion_rules=exclusion_rules, issue_sources=issue_sources, name=name, permissions=permissions, scheduling=scheduling)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_plan: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/plans/plan"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_plan")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_plan", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_plan",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Plans
@mcp.tool()
async def retrieve_plan(plan_id: str = Field(..., alias="planId", description="The unique identifier of the plan to retrieve, specified as a 64-bit integer.")) -> dict[str, Any]:
    """Retrieves detailed information about a specific plan by its ID. Requires Jira administrator permissions."""

    _plan_id = _parse_int(plan_id)

    # Construct request model with validation
    try:
        _request = _models.GetPlanRequest(
            path=_models.GetPlanRequestPath(plan_id=_plan_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for retrieve_plan: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/plans/plan/{planId}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/plans/plan/{planId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("retrieve_plan")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("retrieve_plan", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="retrieve_plan",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Plans
@mcp.tool()
async def update_plan(
    plan_id: str = Field(..., alias="planId", description="The unique identifier of the plan to update. Must be a positive integer."),
    body: dict[str, Any] = Field(..., description="JSON Patch document (RFC 6902) containing one or more operations to update plan properties. Each operation specifies an action (add, replace, remove), a JSON pointer path to the target property, and the new value. Supports updates to: name, leadAccountId, scheduling (estimation type, start/end dates, inferred dates, dependencies), issueSources, exclusionRules, crossProjectReleases, customFields, and permissions."),
) -> dict[str, Any]:
    """Updates plan details including name, lead account, scheduling configuration, issue sources, exclusion rules, cross-project releases, custom fields, and permissions using JSON Patch operations. Requires Administer Jira global permission."""

    _plan_id = _parse_int(plan_id)

    # Construct request model with validation
    try:
        _request = _models.UpdatePlanRequest(
            path=_models.UpdatePlanRequestPath(plan_id=_plan_id),
            body=_models.UpdatePlanRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_plan: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/plans/plan/{planId}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/plans/plan/{planId}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/json-patch+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_plan")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_plan", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_plan",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json-patch+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Plans
@mcp.tool()
async def archive_plan(plan_id: str = Field(..., alias="planId", description="The unique identifier of the plan to archive, specified as a 64-bit integer.")) -> dict[str, Any]:
    """Archives a plan, removing it from active use while preserving its data. Requires Administer Jira global permission."""

    _plan_id = _parse_int(plan_id)

    # Construct request model with validation
    try:
        _request = _models.ArchivePlanRequest(
            path=_models.ArchivePlanRequestPath(plan_id=_plan_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for archive_plan: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/plans/plan/{planId}/archive", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/plans/plan/{planId}/archive"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("archive_plan")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("archive_plan", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="archive_plan",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Plans
@mcp.tool()
async def duplicate_plan(
    plan_id: str = Field(..., alias="planId", description="The unique identifier of the plan to duplicate. Must be a valid 64-bit integer."),
    name: str = Field(..., description="The name for the duplicated plan. This will be the display name of the new plan copy."),
) -> dict[str, Any]:
    """Creates a duplicate copy of an existing plan with a new name. Requires Administer Jira global permission."""

    _plan_id = _parse_int(plan_id)

    # Construct request model with validation
    try:
        _request = _models.DuplicatePlanRequest(
            path=_models.DuplicatePlanRequestPath(plan_id=_plan_id),
            body=_models.DuplicatePlanRequestBody(name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for duplicate_plan: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/plans/plan/{planId}/duplicate", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/plans/plan/{planId}/duplicate"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("duplicate_plan")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("duplicate_plan", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="duplicate_plan",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Teams in plan
@mcp.tool()
async def list_plan_teams(
    plan_id: str = Field(..., alias="planId", description="The unique identifier of the plan for which to retrieve teams."),
    max_results: str | None = Field(None, alias="maxResults", description="The maximum number of teams to return per page, up to a maximum of 50. Defaults to 50 if not specified."),
) -> dict[str, Any]:
    """Retrieve a paginated list of all teams associated with a plan, including both plan-only teams and Atlassian teams. Requires Administer Jira global permission."""

    _plan_id = _parse_int(plan_id)
    _max_results = _parse_int(max_results)

    # Construct request model with validation
    try:
        _request = _models.GetTeamsRequest(
            path=_models.GetTeamsRequestPath(plan_id=_plan_id),
            query=_models.GetTeamsRequestQuery(max_results=_max_results)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_plan_teams: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/plans/plan/{planId}/team", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/plans/plan/{planId}/team"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_plan_teams")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_plan_teams", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_plan_teams",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Teams in plan
@mcp.tool()
async def add_team_to_plan(
    plan_id: str = Field(..., alias="planId", description="The unique identifier of the plan to which the team will be added."),
    id_: str = Field(..., alias="id", description="The unique identifier of the Atlassian team to add to the plan."),
    planning_style: Literal["Scrum", "Kanban"] = Field(..., alias="planningStyle", description="The planning methodology for the team: either Scrum for sprint-based planning or Kanban for continuous flow."),
    capacity: float | None = Field(None, description="The team's capacity allocation for the plan, expressed as a numeric value."),
    issue_source_id: str | None = Field(None, alias="issueSourceId", description="The identifier of the issue source that will supply work items for this team's planning."),
    sprint_length: str | None = Field(None, alias="sprintLength", description="The duration of sprints in days for Scrum-based teams."),
) -> dict[str, Any]:
    """Adds an existing Atlassian team to a plan and configures their planning settings including capacity, planning methodology, and sprint configuration."""

    _plan_id = _parse_int(plan_id)
    _issue_source_id = _parse_int(issue_source_id)
    _sprint_length = _parse_int(sprint_length)

    # Construct request model with validation
    try:
        _request = _models.AddAtlassianTeamRequest(
            path=_models.AddAtlassianTeamRequestPath(plan_id=_plan_id),
            body=_models.AddAtlassianTeamRequestBody(capacity=capacity, id_=id_, issue_source_id=_issue_source_id, planning_style=planning_style, sprint_length=_sprint_length)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_team_to_plan: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/plans/plan/{planId}/team/atlassian", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/plans/plan/{planId}/team/atlassian"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_team_to_plan")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_team_to_plan", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_team_to_plan",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Teams in plan
@mcp.tool()
async def get_team(
    plan_id: str = Field(..., alias="planId", description="The unique identifier of the plan containing the team. Must be a valid 64-bit integer."),
    atlassian_team_id: str = Field(..., alias="atlassianTeamId", description="The unique identifier of the Atlassian team whose planning settings should be retrieved."),
) -> dict[str, Any]:
    """Retrieve planning settings and configuration for an Atlassian team within a specific plan. Requires Administer Jira global permission."""

    _plan_id = _parse_int(plan_id)

    # Construct request model with validation
    try:
        _request = _models.GetAtlassianTeamRequest(
            path=_models.GetAtlassianTeamRequestPath(plan_id=_plan_id, atlassian_team_id=atlassian_team_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_team: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/plans/plan/{planId}/team/atlassian/{atlassianTeamId}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/plans/plan/{planId}/team/atlassian/{atlassianTeamId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_team")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_team", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_team",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Teams in plan
@mcp.tool()
async def update_team_planning_settings(
    plan_id: str = Field(..., alias="planId", description="The unique identifier of the plan containing the team. Must be a positive integer."),
    atlassian_team_id: str = Field(..., alias="atlassianTeamId", description="The unique identifier of the Atlassian team to update within the plan."),
    body: dict[str, Any] = Field(..., description="JSON Patch operations array specifying the updates to apply. Each operation must include 'op' (replace/add/remove), 'path' (e.g., /planningStyle, /sprintLength, /capacity, /issueSourceId), and 'value' for replace/add operations. Array order is not significant for add operations; retrieve the current team configuration to determine existing element positions."),
) -> dict[str, Any]:
    """Modify planning configuration for an Atlassian team within a plan, including planning style, issue source, sprint length, and capacity settings. Uses JSON Patch format for updates."""

    _plan_id = _parse_int(plan_id)

    # Construct request model with validation
    try:
        _request = _models.UpdateAtlassianTeamRequest(
            path=_models.UpdateAtlassianTeamRequestPath(plan_id=_plan_id, atlassian_team_id=atlassian_team_id),
            body=_models.UpdateAtlassianTeamRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_team_planning_settings: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/plans/plan/{planId}/team/atlassian/{atlassianTeamId}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/plans/plan/{planId}/team/atlassian/{atlassianTeamId}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/json-patch+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_team_planning_settings")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_team_planning_settings", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_team_planning_settings",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json-patch+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Teams in plan
@mcp.tool()
async def remove_team_from_plan(
    plan_id: str = Field(..., alias="planId", description="The unique identifier of the plan from which the team will be removed. Must be a valid 64-bit integer."),
    atlassian_team_id: str = Field(..., alias="atlassianTeamId", description="The unique identifier of the Atlassian team to remove from the plan."),
) -> dict[str, Any]:
    """Remove an Atlassian team from a plan and delete their associated planning settings. Requires Administer Jira global permission."""

    _plan_id = _parse_int(plan_id)

    # Construct request model with validation
    try:
        _request = _models.RemoveAtlassianTeamRequest(
            path=_models.RemoveAtlassianTeamRequestPath(plan_id=_plan_id, atlassian_team_id=atlassian_team_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_team_from_plan: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/plans/plan/{planId}/team/atlassian/{atlassianTeamId}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/plans/plan/{planId}/team/atlassian/{atlassianTeamId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_team_from_plan")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_team_from_plan", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_team_from_plan",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Teams in plan
@mcp.tool()
async def create_plan_only_team(
    plan_id: str = Field(..., alias="planId", description="The unique identifier of the plan to which the team will be added."),
    name: str = Field(..., description="The name of the plan-only team. Must be between 1 and 255 characters.", min_length=1, max_length=255),
    planning_style: Literal["Scrum", "Kanban"] = Field(..., alias="planningStyle", description="The planning methodology for the team. Must be either 'Scrum' for sprint-based planning or 'Kanban' for continuous flow."),
    capacity: float | None = Field(None, description="The team's capacity allocation for planning purposes, expressed as a decimal number."),
    issue_source_id: str | None = Field(None, alias="issueSourceId", description="The unique identifier of the issue source that will supply work items to this plan-only team."),
    member_account_ids: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(None, alias="memberAccountIds", description="A list of Jira account IDs for the team members to be added to this plan-only team."),
    sprint_length: str | None = Field(None, alias="sprintLength", description="The duration of sprints for this team, specified in days. Only applicable when using Scrum planning style."),
) -> dict[str, Any]:
    """Creates a plan-only team within a Jira plan and configures their planning settings, including capacity, members, and sprint configuration. Requires Administer Jira global permission."""

    _plan_id = _parse_int(plan_id)
    _issue_source_id = _parse_int(issue_source_id)
    _sprint_length = _parse_int(sprint_length)

    # Construct request model with validation
    try:
        _request = _models.CreatePlanOnlyTeamRequest(
            path=_models.CreatePlanOnlyTeamRequestPath(plan_id=_plan_id),
            body=_models.CreatePlanOnlyTeamRequestBody(capacity=capacity, issue_source_id=_issue_source_id, member_account_ids=member_account_ids, name=name, planning_style=planning_style, sprint_length=_sprint_length)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_plan_only_team: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/plans/plan/{planId}/team/planonly", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/plans/plan/{planId}/team/planonly"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_plan_only_team")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_plan_only_team", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_plan_only_team",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Teams in plan
@mcp.tool()
async def get_plan_only_team(
    plan_id: str = Field(..., alias="planId", description="The unique identifier of the plan containing the team. Must be a positive integer."),
    plan_only_team_id: str = Field(..., alias="planOnlyTeamId", description="The unique identifier of the plan-only team whose settings you want to retrieve. Must be a positive integer."),
) -> dict[str, Any]:
    """Retrieve planning settings and configuration for a specific plan-only team within a plan. Requires Jira administrator permissions."""

    _plan_id = _parse_int(plan_id)
    _plan_only_team_id = _parse_int(plan_only_team_id)

    # Construct request model with validation
    try:
        _request = _models.GetPlanOnlyTeamRequest(
            path=_models.GetPlanOnlyTeamRequestPath(plan_id=_plan_id, plan_only_team_id=_plan_only_team_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_plan_only_team: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/plans/plan/{planId}/team/planonly/{planOnlyTeamId}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/plans/plan/{planId}/team/planonly/{planOnlyTeamId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_plan_only_team")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_plan_only_team", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_plan_only_team",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Teams in plan
@mcp.tool()
async def update_plan_team(
    plan_id: str = Field(..., alias="planId", description="The unique identifier of the plan containing the team. Must be a positive integer."),
    plan_only_team_id: str = Field(..., alias="planOnlyTeamId", description="The unique identifier of the plan-only team to update. Must be a positive integer."),
    body: dict[str, Any] = Field(..., description="JSON Patch operations array specifying the updates to apply. Each operation must include 'op' (replace, add, remove), 'path' (target field), and 'value' (for replace/add operations). Note that add operations do not respect array indexes; retrieve the team first to determine current array order."),
) -> dict[str, Any]:
    """Update planning settings for a plan-only team, including name, planning style, issue source, sprint length, capacity, and team members. Uses JSON Patch format to specify changes."""

    _plan_id = _parse_int(plan_id)
    _plan_only_team_id = _parse_int(plan_only_team_id)

    # Construct request model with validation
    try:
        _request = _models.UpdatePlanOnlyTeamRequest(
            path=_models.UpdatePlanOnlyTeamRequestPath(plan_id=_plan_id, plan_only_team_id=_plan_only_team_id),
            body=_models.UpdatePlanOnlyTeamRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_plan_team: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/plans/plan/{planId}/team/planonly/{planOnlyTeamId}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/plans/plan/{planId}/team/planonly/{planOnlyTeamId}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/json-patch+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_plan_team")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_plan_team", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_plan_team",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json-patch+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Teams in plan
@mcp.tool()
async def remove_plan_only_team(
    plan_id: str = Field(..., alias="planId", description="The unique identifier of the plan containing the team to be removed. Must be a positive integer."),
    plan_only_team_id: str = Field(..., alias="planOnlyTeamId", description="The unique identifier of the plan-only team to delete. Must be a positive integer."),
) -> dict[str, Any]:
    """Removes a plan-only team from a plan and deletes their associated planning settings. Requires Jira administrator permissions."""

    _plan_id = _parse_int(plan_id)
    _plan_only_team_id = _parse_int(plan_only_team_id)

    # Construct request model with validation
    try:
        _request = _models.DeletePlanOnlyTeamRequest(
            path=_models.DeletePlanOnlyTeamRequestPath(plan_id=_plan_id, plan_only_team_id=_plan_only_team_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_plan_only_team: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/plans/plan/{planId}/team/planonly/{planOnlyTeamId}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/plans/plan/{planId}/team/planonly/{planOnlyTeamId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_plan_only_team")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_plan_only_team", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_plan_only_team",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Plans
@mcp.tool()
async def trash_plan(plan_id: str = Field(..., alias="planId", description="The unique identifier of the plan to move to trash. Must be a valid 64-bit integer.")) -> dict[str, Any]:
    """Move a plan to trash, removing it from active use. Requires Administer Jira global permission."""

    _plan_id = _parse_int(plan_id)

    # Construct request model with validation
    try:
        _request = _models.TrashPlanRequest(
            path=_models.TrashPlanRequestPath(plan_id=_plan_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for trash_plan: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/plans/plan/{planId}/trash", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/plans/plan/{planId}/trash"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("trash_plan")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("trash_plan", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="trash_plan",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue priorities
@mcp.tool()
async def get_priority(id_: str = Field(..., alias="id", description="The unique identifier of the issue priority to retrieve.")) -> dict[str, Any]:
    """Retrieve details of a specific issue priority in Jira. Returns the priority configuration including its name, description, and other metadata."""

    # Construct request model with validation
    try:
        _request = _models.GetPriorityRequest(
            path=_models.GetPriorityRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_priority: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/priority/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/priority/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_priority")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_priority", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_priority",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue priorities
@mcp.tool()
async def remove_priority(id_: str = Field(..., alias="id", description="The unique identifier of the priority to delete.")) -> dict[str, Any]:
    """Removes an issue priority from the Jira instance. This is an asynchronous operation; check the returned location link to monitor task status."""

    # Construct request model with validation
    try:
        _request = _models.DeletePriorityRequest(
            path=_models.DeletePriorityRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_priority: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/priority/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/priority/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_priority")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_priority", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_priority",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Priority schemes
@mcp.tool()
async def list_available_priorities(
    scheme_id: str = Field(..., alias="schemeId", description="The unique identifier of the priority scheme for which to retrieve available priorities."),
    start_at: str | None = Field(None, alias="startAt", description="The starting position for pagination, where 0 represents the first item. Use this to navigate through large result sets."),
    max_results: str | None = Field(None, alias="maxResults", description="The number of priorities to return per page. Defaults to 50 items if not specified."),
) -> dict[str, Any]:
    """Retrieves a paginated list of priorities that can be added to a specific priority scheme. Use this to discover which priorities are available for assignment within your priority scheme."""

    # Construct request model with validation
    try:
        _request = _models.GetAvailablePrioritiesByPrioritySchemeRequest(
            query=_models.GetAvailablePrioritiesByPrioritySchemeRequestQuery(start_at=start_at, max_results=max_results, scheme_id=scheme_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_available_priorities: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/priorityscheme/priorities/available"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_available_priorities")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_available_priorities", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_available_priorities",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Priority schemes
@mcp.tool()
async def list_priorities(
    scheme_id: str = Field(..., alias="schemeId", description="The unique identifier of the priority scheme from which to retrieve priorities."),
    start_at: str | None = Field(None, alias="startAt", description="The zero-based index position to start returning results from, enabling pagination through large result sets. Defaults to 0 if not specified."),
    max_results: str | None = Field(None, alias="maxResults", description="The maximum number of priorities to return in a single page of results. Defaults to 50 if not specified."),
) -> dict[str, Any]:
    """Retrieves a paginated list of priorities configured in a specific priority scheme. Use this to fetch all available priorities for a given scheme with optional pagination control."""

    # Construct request model with validation
    try:
        _request = _models.GetPrioritiesByPrioritySchemeRequest(
            path=_models.GetPrioritiesByPrioritySchemeRequestPath(scheme_id=scheme_id),
            query=_models.GetPrioritiesByPrioritySchemeRequestQuery(start_at=start_at, max_results=max_results)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_priorities: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/priorityscheme/{schemeId}/priorities", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/priorityscheme/{schemeId}/priorities"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_priorities")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_priorities", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_priorities",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def create_project(
    key: str = Field(..., description="A unique project identifier consisting of 1-10 uppercase alphanumeric characters, starting with a letter. This key is used in issue keys (e.g., PROJ-123) and cannot be changed after creation."),
    name: str = Field(..., description="The display name of the project, which appears in the Jira interface and project listings."),
    assignee_type: Literal["PROJECT_LEAD", "UNASSIGNED"] | None = Field(None, alias="assigneeType", description="Determines who is automatically assigned to newly created issues in this project. Choose PROJECT_LEAD to assign to the project lead, or UNASSIGNED to leave issues unassigned by default."),
    avatar_id: str | None = Field(None, alias="avatarId", description="The numeric ID of the avatar image to display for this project. Retrieve available avatar IDs from the project avatars endpoint."),
    category_id: str | None = Field(None, alias="categoryId", description="The numeric ID of the project category for organizational grouping. Retrieve available category IDs using the Get all project categories operation."),
    description: str | None = Field(None, description="A brief text description of the project's purpose and scope."),
    field_scheme: str | None = Field(None, alias="fieldScheme", description="The numeric ID of the field scheme that defines which custom and standard fields are available in this project. Cannot be combined with projectTemplateKey. Retrieve available field scheme IDs using the Get field schemes operation."),
    issue_security_scheme: str | None = Field(None, alias="issueSecurityScheme", description="The numeric ID of the issue security scheme that controls visibility and access permissions for issues. Retrieve available scheme IDs using the Get issue security schemes operation."),
    issue_type_scheme: str | None = Field(None, alias="issueTypeScheme", description="The numeric ID of the issue type scheme that defines which issue types are available in this project. Cannot be combined with projectTemplateKey. Retrieve available scheme IDs using the Get all issue type schemes operation."),
    issue_type_screen_scheme: str | None = Field(None, alias="issueTypeScreenScheme", description="The numeric ID of the issue type screen scheme that maps issue types to their corresponding screens. Cannot be combined with projectTemplateKey. Retrieve available scheme IDs using the Get all issue type screen schemes operation."),
    notification_scheme: str | None = Field(None, alias="notificationScheme", description="The numeric ID of the notification scheme that defines how team members are notified of project events. Retrieve available scheme IDs using the Get notification schemes operation."),
    permission_scheme: str | None = Field(None, alias="permissionScheme", description="The numeric ID of the permission scheme that controls user access and actions within the project. Retrieve available scheme IDs using the Get all permission schemes operation."),
    project_template_key: Literal["com.pyxis.greenhopper.jira:gh-simplified-agility-kanban", "com.pyxis.greenhopper.jira:gh-simplified-agility-scrum", "com.pyxis.greenhopper.jira:gh-simplified-basic", "com.pyxis.greenhopper.jira:gh-simplified-kanban-classic", "com.pyxis.greenhopper.jira:gh-simplified-scrum-classic", "com.pyxis.greenhopper.jira:gh-cross-team-template", "com.pyxis.greenhopper.jira:gh-cross-team-planning-template", "com.atlassian.servicedesk:simplified-it-service-management", "com.atlassian.servicedesk:simplified-it-service-management-basic", "com.atlassian.servicedesk:simplified-it-service-management-operations", "com.atlassian.servicedesk:simplified-general-service-desk", "com.atlassian.servicedesk:simplified-internal-service-desk", "com.atlassian.servicedesk:simplified-external-service-desk", "com.atlassian.servicedesk:simplified-hr-service-desk", "com.atlassian.servicedesk:simplified-facilities-service-desk", "com.atlassian.servicedesk:simplified-legal-service-desk", "com.atlassian.servicedesk:simplified-marketing-service-desk", "com.atlassian.servicedesk:simplified-finance-service-desk", "com.atlassian.servicedesk:simplified-analytics-service-desk", "com.atlassian.servicedesk:simplified-design-service-desk", "com.atlassian.servicedesk:simplified-sales-service-desk", "com.atlassian.servicedesk:simplified-halp-service-desk", "com.atlassian.servicedesk:next-gen-it-service-desk", "com.atlassian.servicedesk:next-gen-hr-service-desk", "com.atlassian.servicedesk:next-gen-legal-service-desk", "com.atlassian.servicedesk:next-gen-marketing-service-desk", "com.atlassian.servicedesk:next-gen-facilities-service-desk", "com.atlassian.servicedesk:next-gen-general-service-desk", "com.atlassian.servicedesk:next-gen-analytics-service-desk", "com.atlassian.servicedesk:next-gen-finance-service-desk", "com.atlassian.servicedesk:next-gen-design-service-desk", "com.atlassian.servicedesk:next-gen-sales-service-desk", "com.atlassian.jira-core-project-templates:jira-core-simplified-content-management", "com.atlassian.jira-core-project-templates:jira-core-simplified-document-approval", "com.atlassian.jira-core-project-templates:jira-core-simplified-lead-tracking", "com.atlassian.jira-core-project-templates:jira-core-simplified-process-control", "com.atlassian.jira-core-project-templates:jira-core-simplified-procurement", "com.atlassian.jira-core-project-templates:jira-core-simplified-project-management", "com.atlassian.jira-core-project-templates:jira-core-simplified-recruitment", "com.atlassian.jira-core-project-templates:jira-core-simplified-task-", "com.atlassian.jcs:customer-service-management"] | None = Field(None, alias="projectTemplateKey", description="A predefined project configuration template that sets up workflows, issue types, and screens. The template type must match the projectTypeKey (e.g., software templates for software projects). Cannot be combined with fieldScheme, issueTypeScheme, issueTypeScreenScheme, or workflowScheme."),
    url: str | None = Field(None, description="A URL pointing to project documentation, guidelines, or related resources."),
    workflow_scheme: str | None = Field(None, alias="workflowScheme", description="The numeric ID of the workflow scheme that defines the issue lifecycle and transitions for this project. Cannot be combined with projectTemplateKey. Retrieve available scheme IDs using the Get all workflow schemes operation."),
) -> dict[str, Any]:
    """Creates a new Jira project based on a project type template (business, software, service_desk, or customer_service). Requires Administer Jira global permission and a unique project key."""

    _avatar_id = _parse_int(avatar_id)
    _category_id = _parse_int(category_id)
    _field_scheme = _parse_int(field_scheme)
    _issue_security_scheme = _parse_int(issue_security_scheme)
    _issue_type_scheme = _parse_int(issue_type_scheme)
    _issue_type_screen_scheme = _parse_int(issue_type_screen_scheme)
    _notification_scheme = _parse_int(notification_scheme)
    _permission_scheme = _parse_int(permission_scheme)
    _workflow_scheme = _parse_int(workflow_scheme)

    # Construct request model with validation
    try:
        _request = _models.CreateProjectRequest(
            body=_models.CreateProjectRequestBody(assignee_type=assignee_type, avatar_id=_avatar_id, category_id=_category_id, description=description, field_scheme=_field_scheme, issue_security_scheme=_issue_security_scheme, issue_type_scheme=_issue_type_scheme, issue_type_screen_scheme=_issue_type_screen_scheme, key=key, name=name, notification_scheme=_notification_scheme, permission_scheme=_permission_scheme, project_template_key=project_template_key, url=url, workflow_scheme=_workflow_scheme)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/project"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_project")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_project", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_project",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project templates
@mcp.tool()
async def create_project_from_template(
    details: _models.CreateProjectWithCustomTemplateBodyDetails | None = Field(None, description="Project details: name, description, access level, assignee type, avatar, category, language, URL, and other project-level settings."),
    template: _models.CreateProjectWithCustomTemplateBodyTemplate | None = Field(None, description="Project template configuration: boards, field schemes, issue types, notification schemes, permission schemes, roles, security levels, workflows, and their mappings."),
) -> dict[str, Any]:
    """Creates a new Jira project based on a custom template with specified capabilities. This asynchronous operation configures project details, workflows, permissions, fields, and other components. Requires Jira Enterprise edition and Administer Jira global permission."""

    # Construct request model with validation
    try:
        _request = _models.CreateProjectWithCustomTemplateRequest(
            body=_models.CreateProjectWithCustomTemplateRequestBody(details=details, template=template)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_project_from_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/project-template"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_project_from_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_project_from_template", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_project_from_template",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def list_recent_projects() -> dict[str, Any]:
    """Retrieve up to 20 projects recently viewed by the user, filtered to show only those the user has permission to access. This operation can be used anonymously and respects project-level and global permissions."""

    # Extract parameters for API call
    _http_path = "/rest/api/3/project/recent"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_recent_projects")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_recent_projects", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_recent_projects",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def list_projects(
    start_at: str | None = Field(None, alias="startAt", description="The starting position for pagination (zero-indexed). Use this to retrieve subsequent pages of results."),
    max_results: str | None = Field(None, alias="maxResults", description="Maximum number of projects to return per page, capped at 100. Values exceeding 100 will be automatically limited to 100."),
    order_by: Literal["category", "-category", "+category", "key", "-key", "+key", "name", "-name", "+name", "owner", "-owner", "+owner", "issueCount", "-issueCount", "+issueCount", "lastIssueUpdatedDate", "-lastIssueUpdatedDate", "+lastIssueUpdatedDate", "archivedDate", "+archivedDate", "-archivedDate", "deletedDate", "+deletedDate", "-deletedDate"] | None = Field(None, alias="orderBy", description="Sort results by a specific field: category, issue count, project key, last issue update time, project name, project owner/lead, archived date, or deleted date. Prefix with `-` for descending order or `+` for ascending order. Defaults to sorting by project key."),
    keys: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(None, description="Filter results to include only specific projects by their keys. Provide up to 50 project keys as a comma-separated list."),
    type_key: str | None = Field(None, alias="typeKey", description="Filter results by project type. Accepts comma-separated values: `business`, `service_desk`, or `software`."),
    category_id: str | None = Field(None, alias="categoryId", description="Filter results by project category ID. Retrieve available category IDs using the Get all project categories operation."),
    action: Literal["view", "browse", "edit", "create"] | None = Field(None, description="Filter results by the user's permission level on projects: `view` (has browse or admin permissions), `browse` (has browse permission), `edit` (has admin permission), or `create` (can create issues). Defaults to `view`."),
    status: list[Literal["live", "archived", "deleted"]] | None = Field(None, description="Filter results by project status: `live` for active projects, `archived` for archived projects, or `deleted` for projects in the recycle bin. This is an experimental feature."),
    property_query: str | None = Field(None, alias="propertyQuery", description="Search projects by custom property values using dot-notation syntax. Enclose property keys in square brackets to support keys containing dots or equals signs. This is an experimental feature."),
) -> dict[str, Any]:
    """Retrieve a paginated list of projects visible to the user based on their permissions. Supports filtering by project keys, type, category, and status, with flexible sorting options."""

    _start_at = _parse_int(start_at)
    _max_results = _parse_int(max_results)
    _category_id = _parse_int(category_id)

    # Construct request model with validation
    try:
        _request = _models.SearchProjectsRequest(
            query=_models.SearchProjectsRequestQuery(start_at=_start_at, max_results=_max_results, order_by=order_by, keys=keys, type_key=type_key, category_id=_category_id, action=action, status=status, property_query=property_query)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_projects: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/project/search"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_projects")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_projects", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_projects",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project types
@mcp.tool()
async def list_project_types() -> dict[str, Any]:
    """Retrieves all available project types in the Jira instance, including both licensed and unlicensed types. This operation requires no authentication and can be accessed anonymously."""

    # Extract parameters for API call
    _http_path = "/rest/api/3/project/type"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_project_types")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_project_types", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_project_types",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project types
@mcp.tool()
async def list_accessible_project_types() -> dict[str, Any]:
    """Retrieve all project types available with valid licenses in your Jira instance. Use this to discover which project type options are available for creating new projects."""

    # Extract parameters for API call
    _http_path = "/rest/api/3/project/type/accessible"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_accessible_project_types")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_accessible_project_types", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_accessible_project_types",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project types
@mcp.tool()
async def get_project_type(project_type_key: Literal["software", "service_desk", "business", "product_discovery"] = Field(..., alias="projectTypeKey", description="The unique identifier for the project type. Must be one of the following: software, service_desk, business, or product_discovery.")) -> dict[str, Any]:
    """Retrieve detailed information about a specific project type by its key. This operation is publicly accessible and requires no authentication or permissions."""

    # Construct request model with validation
    try:
        _request = _models.GetProjectTypeByKeyRequest(
            path=_models.GetProjectTypeByKeyRequestPath(project_type_key=project_type_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_project_type: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/project/type/{projectTypeKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/project/type/{projectTypeKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_project_type")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_project_type", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_project_type",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project types
@mcp.tool()
async def get_accessible_project_type(project_type_key: Literal["software", "service_desk", "business", "product_discovery"] = Field(..., alias="projectTypeKey", description="The unique identifier for the project type. Must be one of the four supported project types: software, service_desk, business, or product_discovery.")) -> dict[str, Any]:
    """Retrieves a project type if it is accessible to the authenticated user. Returns project type details for the specified project type key."""

    # Construct request model with validation
    try:
        _request = _models.GetAccessibleProjectTypeByKeyRequest(
            path=_models.GetAccessibleProjectTypeByKeyRequestPath(project_type_key=project_type_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_accessible_project_type: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/project/type/{projectTypeKey}/accessible", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/project/type/{projectTypeKey}/accessible"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_accessible_project_type")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_accessible_project_type", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_accessible_project_type",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def get_project(project_id_or_key: str = Field(..., alias="projectIdOrKey", description="The unique identifier for the project, either as the project ID (numeric) or project key (case-sensitive alphanumeric code). Project keys are typically short uppercase abbreviations like 'PROJ'.")) -> dict[str, Any]:
    """Retrieve detailed information about a specific project, including its configuration and metadata. Requires Browse projects permission for the target project."""

    # Construct request model with validation
    try:
        _request = _models.GetProjectRequest(
            path=_models.GetProjectRequestPath(project_id_or_key=project_id_or_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/project/{projectIdOrKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/project/{projectIdOrKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_project")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_project", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_project",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def update_project(
    project_id_or_key: str = Field(..., alias="projectIdOrKey", description="The project identifier, either the numeric project ID or the project key (case-sensitive)."),
    assignee_type: Literal["PROJECT_LEAD", "UNASSIGNED"] | None = Field(None, alias="assigneeType", description="The default assignee type for newly created issues in this project. Choose between the project lead or unassigned."),
    avatar_id: str | None = Field(None, alias="avatarId", description="The numeric ID of the avatar image to display for this project."),
    category_id: str | None = Field(None, alias="categoryId", description="The numeric ID of the project category. Use the Get all project categories operation to find available category IDs, or set to -1 to remove the category."),
    description: str | None = Field(None, description="A brief description of the project's purpose and scope."),
    issue_security_scheme: str | None = Field(None, alias="issueSecurityScheme", description="The numeric ID of the issue security scheme that controls issue visibility and access permissions. Use the Get issue security schemes operation to find available scheme IDs."),
    notification_scheme: str | None = Field(None, alias="notificationScheme", description="The numeric ID of the notification scheme that defines how project members are notified of events. Use the Get notification schemes operation to find available scheme IDs."),
    permission_scheme: str | None = Field(None, alias="permissionScheme", description="The numeric ID of the permission scheme that defines user roles and permissions. Use the Get all permission schemes operation to find available scheme IDs."),
    released_project_keys: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(None, alias="releasedProjectKeys", description="An array of previous project keys to release from the current project. Released keys must belong to the current project and cannot include the current project key."),
    url: str | None = Field(None, description="A URL pointing to project documentation or related information."),
) -> dict[str, Any]:
    """Update project details including name, description, avatar, category, and associated schemes. All parameters are optional; only included fields will be updated while omitted ones remain unchanged."""

    _avatar_id = _parse_int(avatar_id)
    _category_id = _parse_int(category_id)
    _issue_security_scheme = _parse_int(issue_security_scheme)
    _notification_scheme = _parse_int(notification_scheme)
    _permission_scheme = _parse_int(permission_scheme)

    # Construct request model with validation
    try:
        _request = _models.UpdateProjectRequest(
            path=_models.UpdateProjectRequestPath(project_id_or_key=project_id_or_key),
            body=_models.UpdateProjectRequestBody(assignee_type=assignee_type, avatar_id=_avatar_id, category_id=_category_id, description=description, issue_security_scheme=_issue_security_scheme, notification_scheme=_notification_scheme, permission_scheme=_permission_scheme, released_project_keys=released_project_keys, url=url)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/project/{projectIdOrKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/project/{projectIdOrKey}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_project")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_project", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_project",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def delete_project(
    project_id_or_key: str = Field(..., alias="projectIdOrKey", description="The unique identifier for the project, either the numeric project ID or the project key (case-sensitive)."),
    enable_undo: bool | None = Field(None, alias="enableUndo", description="Whether to move the project to the Jira recycle bin for later restoration instead of permanently deleting it. Defaults to true."),
) -> dict[str, Any]:
    """Permanently delete a Jira project. Archived projects must be restored before deletion. Requires Jira administrator permissions."""

    # Construct request model with validation
    try:
        _request = _models.DeleteProjectRequest(
            path=_models.DeleteProjectRequestPath(project_id_or_key=project_id_or_key),
            query=_models.DeleteProjectRequestQuery(enable_undo=enable_undo)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/project/{projectIdOrKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/project/{projectIdOrKey}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_project")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_project", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_project",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def archive_project(project_id_or_key: str = Field(..., alias="projectIdOrKey", description="The unique identifier for the project, either the project ID (numeric) or project key (case-sensitive alphanumeric code).")) -> dict[str, Any]:
    """Archive a project to prevent further modifications while preserving its data. Archived projects cannot be deleted directly; restore the project first if deletion is needed."""

    # Construct request model with validation
    try:
        _request = _models.ArchiveProjectRequest(
            path=_models.ArchiveProjectRequestPath(project_id_or_key=project_id_or_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for archive_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/project/{projectIdOrKey}/archive", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/project/{projectIdOrKey}/archive"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("archive_project")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("archive_project", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="archive_project",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project avatars
@mcp.tool()
async def set_project_avatar(
    project_id_or_key: str = Field(..., alias="projectIdOrKey", description="The project identifier, either the numeric project ID or the case-sensitive project key."),
    id_: str = Field(..., alias="id", description="The unique identifier of the avatar image to display. This avatar must have been previously uploaded to the project."),
) -> dict[str, Any]:
    """Sets the avatar image displayed for a project. The avatar must first be uploaded using the load project avatar operation before it can be set as the displayed avatar."""

    # Construct request model with validation
    try:
        _request = _models.UpdateProjectAvatarRequest(
            path=_models.UpdateProjectAvatarRequestPath(project_id_or_key=project_id_or_key),
            body=_models.UpdateProjectAvatarRequestBody(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for set_project_avatar: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/project/{projectIdOrKey}/avatar", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/project/{projectIdOrKey}/avatar"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("set_project_avatar")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("set_project_avatar", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="set_project_avatar",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project avatars
@mcp.tool()
async def remove_project_avatar(
    project_id_or_key: str = Field(..., alias="projectIdOrKey", description="The project identifier, either the numeric project ID or the case-sensitive project key."),
    id_: str = Field(..., alias="id", description="The numeric identifier of the avatar to delete. Must be a valid 64-bit integer."),
) -> dict[str, Any]:
    """Remove a custom avatar from a project. Only custom avatars can be deleted; system-provided avatars are protected and cannot be removed. Requires Administer projects permission."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.DeleteProjectAvatarRequest(
            path=_models.DeleteProjectAvatarRequestPath(project_id_or_key=project_id_or_key, id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_project_avatar: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/project/{projectIdOrKey}/avatar/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/project/{projectIdOrKey}/avatar/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_project_avatar")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_project_avatar", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_project_avatar",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project avatars
@mcp.tool()
async def upload_project_avatar(
    project_id_or_key: str = Field(..., alias="projectIdOrKey", description="The project identifier, either the numeric project ID or the case-sensitive project key."),
    x: str | None = Field(None, description="The X coordinate (in pixels) of the top-left corner of the crop region. Defaults to 0 if not specified."),
    y: str | None = Field(None, description="The Y coordinate (in pixels) of the top-left corner of the crop region. Defaults to 0 if not specified."),
    size: str | None = Field(None, description="The side length (in pixels) of the square crop region. Defaults to 0, which uses the smaller of the image's height or width."),
) -> dict[str, Any]:
    """Upload and process an image file as a project avatar. The image is automatically cropped to a square and resized into multiple formats (16x16, 24x24, 32x32, 48x48). Requires the Administer projects permission."""

    _x = _parse_int(x)
    _y = _parse_int(y)
    _size = _parse_int(size)

    # Construct request model with validation
    try:
        _request = _models.CreateProjectAvatarRequest(
            path=_models.CreateProjectAvatarRequestPath(project_id_or_key=project_id_or_key),
            query=_models.CreateProjectAvatarRequestQuery(x=_x, y=_y, size=_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for upload_project_avatar: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/project/{projectIdOrKey}/avatar2", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/project/{projectIdOrKey}/avatar2"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("upload_project_avatar")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("upload_project_avatar", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="upload_project_avatar",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project avatars
@mcp.tool()
async def list_project_avatars(project_id_or_key: str = Field(..., alias="projectIdOrKey", description="The project identifier, either the numeric project ID or the case-sensitive project key.")) -> dict[str, Any]:
    """Retrieves all avatars available for a project, organized into system-provided and custom avatar groups. Requires browse project permission and can be accessed anonymously."""

    # Construct request model with validation
    try:
        _request = _models.GetAllProjectAvatarsRequest(
            path=_models.GetAllProjectAvatarsRequestPath(project_id_or_key=project_id_or_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_project_avatars: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/project/{projectIdOrKey}/avatars", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/project/{projectIdOrKey}/avatars"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_project_avatars")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_project_avatars", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_project_avatars",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project classification levels
@mcp.tool()
async def get_project_classification(project_id_or_key: str = Field(..., alias="projectIdOrKey", description="The unique identifier for the project, either as the numeric project ID or the project key (which is case-sensitive).")) -> dict[str, Any]:
    """Retrieve the default data classification level assigned to a project. This determines the default sensitivity or confidentiality level for issues and data within the project."""

    # Construct request model with validation
    try:
        _request = _models.GetDefaultProjectClassificationRequest(
            path=_models.GetDefaultProjectClassificationRequestPath(project_id_or_key=project_id_or_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_project_classification: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/project/{projectIdOrKey}/classification-level/default", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/project/{projectIdOrKey}/classification-level/default"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_project_classification")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_project_classification", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_project_classification",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project components
@mcp.tool()
async def list_project_components(
    project_id_or_key: str = Field(..., alias="projectIdOrKey", description="The project identifier, either the project ID or project key (case-sensitive)."),
    start_at: str | None = Field(None, alias="startAt", description="The zero-based index where the result page begins. Use this to navigate through paginated results."),
    max_results: str | None = Field(None, alias="maxResults", description="The maximum number of components to return per page. Defaults to 50 items."),
    order_by: Literal["description", "-description", "+description", "issueCount", "-issueCount", "+issueCount", "lead", "-lead", "+lead", "name", "-name", "+name"] | None = Field(None, alias="orderBy", description="Sort results by component attribute: name, description, issue count, or project lead. Prefix with `-` for descending or `+` for ascending order."),
    component_source: Literal["jira", "compass", "auto"] | None = Field(None, alias="componentSource", description="The component source to return: `jira` for Jira components, `compass` for Compass components, or `auto` to return Compass components if available, otherwise Jira components."),
) -> dict[str, Any]:
    """Retrieve a paginated list of all components in a project. Returns Jira components by default, or Compass components if configured. Requires Browse Projects permission."""

    _start_at = _parse_int(start_at)
    _max_results = _parse_int(max_results)

    # Construct request model with validation
    try:
        _request = _models.GetProjectComponentsPaginatedRequest(
            path=_models.GetProjectComponentsPaginatedRequestPath(project_id_or_key=project_id_or_key),
            query=_models.GetProjectComponentsPaginatedRequestQuery(start_at=_start_at, max_results=_max_results, order_by=order_by, component_source=component_source)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_project_components: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/project/{projectIdOrKey}/component", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/project/{projectIdOrKey}/component"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_project_components")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_project_components", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_project_components",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project components
@mcp.tool()
async def get_project_components_all(
    project_id_or_key: str = Field(..., alias="projectIdOrKey", description="The project identifier, either the project ID or project key (case-sensitive)."),
    component_source: Literal["jira", "compass", "auto"] | None = Field(None, alias="componentSource", description="The source of components to return: use 'jira' for Jira components (default), 'compass' for Compass components, or 'auto' to return Compass components if available, otherwise Jira components."),
) -> dict[str, Any]:
    """Retrieves all components in a project, including Compass components if the project is opted into Compass. Requires Browse Projects permission and can be accessed anonymously."""

    # Construct request model with validation
    try:
        _request = _models.GetProjectComponentsRequest(
            path=_models.GetProjectComponentsRequestPath(project_id_or_key=project_id_or_key),
            query=_models.GetProjectComponentsRequestQuery(component_source=component_source)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_project_components_all: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/project/{projectIdOrKey}/components", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/project/{projectIdOrKey}/components"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_project_components_all")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_project_components_all", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_project_components_all",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def delete_project_async(project_id_or_key: str = Field(..., alias="projectIdOrKey", description="The project identifier, either the numeric project ID or the project key (case-sensitive).")) -> dict[str, Any]:
    """Asynchronously delete a project. The operation is transactional—if any part fails, the project remains unchanged. Monitor the returned task location to track deletion progress."""

    # Construct request model with validation
    try:
        _request = _models.DeleteProjectAsynchronouslyRequest(
            path=_models.DeleteProjectAsynchronouslyRequestPath(project_id_or_key=project_id_or_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_project_async: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/project/{projectIdOrKey}/delete", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/project/{projectIdOrKey}/delete"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_project_async")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_project_async", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_project_async",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project features
@mcp.tool()
async def list_project_features(project_id_or_key: str = Field(..., alias="projectIdOrKey", description="The unique identifier or key of the project. You can use either the numeric project ID or the case-sensitive project key to identify the project.")) -> dict[str, Any]:
    """Retrieves all available features for a specified project. Features represent optional capabilities or modules that can be enabled or configured within the project."""

    # Construct request model with validation
    try:
        _request = _models.GetFeaturesForProjectRequest(
            path=_models.GetFeaturesForProjectRequestPath(project_id_or_key=project_id_or_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_project_features: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/project/{projectIdOrKey}/features", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/project/{projectIdOrKey}/features"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_project_features")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_project_features", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_project_features",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project properties
@mcp.tool()
async def list_project_property_keys(project_id_or_key: str = Field(..., alias="projectIdOrKey", description="The project identifier, either the numeric project ID or the project key (which is case-sensitive).")) -> dict[str, Any]:
    """Retrieves all property keys stored for a specific project. Property keys are identifiers for custom data associated with the project."""

    # Construct request model with validation
    try:
        _request = _models.GetProjectPropertyKeysRequest(
            path=_models.GetProjectPropertyKeysRequestPath(project_id_or_key=project_id_or_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_project_property_keys: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/project/{projectIdOrKey}/properties", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/project/{projectIdOrKey}/properties"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_project_property_keys")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_project_property_keys", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_project_property_keys",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project properties
@mcp.tool()
async def get_project_property(
    project_id_or_key: str = Field(..., alias="projectIdOrKey", description="The project identifier, either the numeric project ID or the project key (case-sensitive)."),
    property_key: str = Field(..., alias="propertyKey", description="The key identifying the project property to retrieve. Use the list project property keys operation to discover available property keys for a project."),
) -> dict[str, Any]:
    """Retrieves the value of a specific project property by its key. Requires Browse Projects permission for the project containing the property."""

    # Construct request model with validation
    try:
        _request = _models.GetProjectPropertyRequest(
            path=_models.GetProjectPropertyRequestPath(project_id_or_key=project_id_or_key, property_key=property_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_project_property: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/project/{projectIdOrKey}/properties/{propertyKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/project/{projectIdOrKey}/properties/{propertyKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_project_property")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_project_property", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_project_property",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project properties
@mcp.tool()
async def remove_project_property(
    project_id_or_key: str = Field(..., alias="projectIdOrKey", description="The project identifier, either the numeric project ID or the project key (case-sensitive)."),
    property_key: str = Field(..., alias="propertyKey", description="The key identifying the project property to delete. Retrieve available property keys using the list project properties operation."),
) -> dict[str, Any]:
    """Removes a custom property from a project. Requires Administer Jira global permission or Administer Projects permission for the target project."""

    # Construct request model with validation
    try:
        _request = _models.DeleteProjectPropertyRequest(
            path=_models.DeleteProjectPropertyRequestPath(project_id_or_key=project_id_or_key, property_key=property_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_project_property: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/project/{projectIdOrKey}/properties/{propertyKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/project/{projectIdOrKey}/properties/{propertyKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_project_property")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_project_property", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_project_property",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def restore_project(project_id_or_key: str = Field(..., alias="projectIdOrKey", description="The project identifier, either the numeric project ID or the project key (case sensitive).")) -> dict[str, Any]:
    """Restore a project that has been archived or moved to the Jira recycle bin. Requires Administer Jira global permission for Company managed projects, or Administer Jira global permission or Administer projects project permission for Team managed projects."""

    # Construct request model with validation
    try:
        _request = _models.RestoreRequest(
            path=_models.RestoreRequestPath(project_id_or_key=project_id_or_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for restore_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/project/{projectIdOrKey}/restore", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/project/{projectIdOrKey}/restore"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("restore_project")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("restore_project", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="restore_project",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project roles
@mcp.tool()
async def list_project_roles(project_id_or_key: str = Field(..., alias="projectIdOrKey", description="The project identifier, either the numeric project ID or the project key (which is case-sensitive).")) -> dict[str, Any]:
    """Retrieve all project roles available for a specific project, including their names and API endpoints. Project roles are shared across all projects in Jira Cloud."""

    # Construct request model with validation
    try:
        _request = _models.GetProjectRolesRequest(
            path=_models.GetProjectRolesRequestPath(project_id_or_key=project_id_or_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_project_roles: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/project/{projectIdOrKey}/role", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/project/{projectIdOrKey}/role"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_project_roles")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_project_roles", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_project_roles",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project roles
@mcp.tool()
async def get_project_role(
    project_id_or_key: str = Field(..., alias="projectIdOrKey", description="The project identifier, either the numeric project ID or the project key (case-sensitive)."),
    id_: str = Field(..., alias="id", description="The numeric ID of the project role to retrieve. Use the get_project_roles operation to discover available project role IDs."),
    exclude_inactive_users: bool | None = Field(None, alias="excludeInactiveUsers", description="When enabled, filters out inactive users from the returned actors list. Defaults to false, including all users."),
) -> dict[str, Any]:
    """Retrieve a project role's details and the list of actors (users and groups) assigned to it within a specific project. The actors are returned sorted by display name."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.GetProjectRoleRequest(
            path=_models.GetProjectRoleRequestPath(project_id_or_key=project_id_or_key, id_=_id_),
            query=_models.GetProjectRoleRequestQuery(exclude_inactive_users=exclude_inactive_users)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_project_role: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/project/{projectIdOrKey}/role/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/project/{projectIdOrKey}/role/{id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_project_role")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_project_role", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_project_role",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project role actors
@mcp.tool()
async def add_project_role_actors(
    project_id_or_key: str = Field(..., alias="projectIdOrKey", description="The project identifier, either the numeric project ID or the project key (case-sensitive string)."),
    id_: str = Field(..., alias="id", description="The numeric ID of the project role to add actors to. Retrieve available project role IDs using the get_project_roles operation."),
    user: list[str] | None = Field(None, description="An array of user account IDs to add to the project role. Each entry should be a valid user account ID string."),
) -> dict[str, Any]:
    """Adds actors (users or groups) to a project role. Use this to grant role-based permissions to additional actors in a project."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.AddActorUsersRequest(
            path=_models.AddActorUsersRequestPath(project_id_or_key=project_id_or_key, id_=_id_),
            body=_models.AddActorUsersRequestBody(user=user)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_project_role_actors: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/project/{projectIdOrKey}/role/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/project/{projectIdOrKey}/role/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_project_role_actors")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_project_role_actors", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_project_role_actors",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project role actors
@mcp.tool()
async def replace_project_role_actors(
    project_id_or_key: str = Field(..., alias="projectIdOrKey", description="The project identifier, either the numeric project ID or the project key (case-sensitive string)."),
    id_: str = Field(..., alias="id", description="The numeric ID of the project role to modify. Retrieve available project role IDs using the get all project roles operation."),
    categorised_actors: dict[str, list[str]] | None = Field(None, alias="categorisedActors", description="The actors to assign to the project role, replacing all current assignments. Specify groups by ID (recommended) or name, and users by account ID. Use the appropriate actor type key (atlassian-group-role-actor-id, atlassian-group-role-actor, or atlassian-user-role-actor) with an array of identifiers."),
) -> dict[str, Any]:
    """Replace all actors assigned to a project role. This operation overwrites the existing actor list entirely; to add actors without removing existing ones, use the add actors operation instead."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.SetActorsRequest(
            path=_models.SetActorsRequestPath(project_id_or_key=project_id_or_key, id_=_id_),
            body=_models.SetActorsRequestBody(categorised_actors=categorised_actors)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for replace_project_role_actors: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/project/{projectIdOrKey}/role/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/project/{projectIdOrKey}/role/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("replace_project_role_actors")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("replace_project_role_actors", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="replace_project_role_actors",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project role actors
@mcp.tool()
async def remove_actor_from_project_role(
    project_id_or_key: str = Field(..., alias="projectIdOrKey", description="The project identifier, either the numeric project ID or the project key (case-sensitive)."),
    id_: str = Field(..., alias="id", description="The numeric ID of the project role. Retrieve available project role IDs using the get all project roles operation."),
    user: str | None = Field(None, description="The user account ID of the actor to remove from the project role. If omitted, the operation will fail as a user must be specified for removal."),
) -> dict[str, Any]:
    """Remove an actor (user) from a project role. Requires project administration permissions or global Jira administration rights."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.DeleteActorRequest(
            path=_models.DeleteActorRequestPath(project_id_or_key=project_id_or_key, id_=_id_),
            query=_models.DeleteActorRequestQuery(user=user)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_actor_from_project_role: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/project/{projectIdOrKey}/role/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/project/{projectIdOrKey}/role/{id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_actor_from_project_role")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_actor_from_project_role", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_actor_from_project_role",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project roles
@mcp.tool()
async def list_project_roles_with_details(
    project_id_or_key: str = Field(..., alias="projectIdOrKey", description="The project identifier, either the numeric project ID or the project key (case-sensitive)."),
    current_member: bool | None = Field(None, alias="currentMember", description="Filter roles to show only those assigned to the current user. Defaults to false to return all roles."),
    exclude_other_service_roles: bool | None = Field(None, alias="excludeOtherServiceRoles", description="Exclude service management roles that don't apply to the project type. Defaults to false to include all roles."),
) -> dict[str, Any]:
    """Retrieve all project roles and their details for a specific project. Project roles are shared across all projects in the Jira instance."""

    # Construct request model with validation
    try:
        _request = _models.GetProjectRoleDetailsRequest(
            path=_models.GetProjectRoleDetailsRequestPath(project_id_or_key=project_id_or_key),
            query=_models.GetProjectRoleDetailsRequestQuery(current_member=current_member, exclude_other_service_roles=exclude_other_service_roles)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_project_roles_with_details: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/project/{projectIdOrKey}/roledetails", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/project/{projectIdOrKey}/roledetails"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_project_roles_with_details")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_project_roles_with_details", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_project_roles_with_details",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def list_project_statuses(project_id_or_key: str = Field(..., alias="projectIdOrKey", description="The project identifier, either the numeric project ID or the project key (which is case-sensitive). Use the key for human-readable references or the ID for programmatic consistency.")) -> dict[str, Any]:
    """Retrieves all valid statuses for a project, organized by issue type. Each issue type within the project has its own set of valid statuses that can be used for workflow transitions."""

    # Construct request model with validation
    try:
        _request = _models.GetAllStatusesRequest(
            path=_models.GetAllStatusesRequestPath(project_id_or_key=project_id_or_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_project_statuses: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/project/{projectIdOrKey}/statuses", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/project/{projectIdOrKey}/statuses"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_project_statuses")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_project_statuses", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_project_statuses",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project versions
@mcp.tool()
async def list_project_versions(
    project_id_or_key: str = Field(..., alias="projectIdOrKey", description="The project identifier, either the numeric project ID or the project key (case-sensitive)."),
    start_at: str | None = Field(None, alias="startAt", description="The zero-based index where the paginated results should start. Defaults to 0 for the first page."),
    max_results: str | None = Field(None, alias="maxResults", description="The maximum number of versions to return per page. Defaults to 50 items."),
    order_by: Literal["description", "-description", "+description", "name", "-name", "+name", "releaseDate", "-releaseDate", "+releaseDate", "sequence", "-sequence", "+sequence", "startDate", "-startDate", "+startDate"] | None = Field(None, alias="orderBy", description="Sort the results by a specific field: description, name, releaseDate (oldest first), sequence (UI order), or startDate (oldest first). Prefix with '-' for descending order or '+' for ascending order."),
    status: str | None = Field(None, description="Filter versions by status using a comma-separated list. Valid statuses are: released, unreleased, and archived."),
) -> dict[str, Any]:
    """Retrieve a paginated list of all versions in a project. Use this operation when you need to browse versions with pagination control; for a complete unpaginated list, use the alternative get_project_versions operation instead."""

    _start_at = _parse_int(start_at)
    _max_results = _parse_int(max_results)

    # Construct request model with validation
    try:
        _request = _models.GetProjectVersionsPaginatedRequest(
            path=_models.GetProjectVersionsPaginatedRequestPath(project_id_or_key=project_id_or_key),
            query=_models.GetProjectVersionsPaginatedRequestQuery(start_at=_start_at, max_results=_max_results, order_by=order_by, status=status)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_project_versions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/project/{projectIdOrKey}/version", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/project/{projectIdOrKey}/version"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_project_versions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_project_versions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_project_versions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project versions
@mcp.tool()
async def list_project_versions_all(project_id_or_key: str = Field(..., alias="projectIdOrKey", description="The unique identifier for the project, either as the project ID (numeric) or project key (case-sensitive alphanumeric code).")) -> dict[str, Any]:
    """Retrieves all versions for a specified project in a single non-paginated response. Use this operation when you need the complete list of versions; for paginated results, use the paginated versions endpoint instead."""

    # Construct request model with validation
    try:
        _request = _models.GetProjectVersionsRequest(
            path=_models.GetProjectVersionsRequestPath(project_id_or_key=project_id_or_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_project_versions_all: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/project/{projectIdOrKey}/versions", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/project/{projectIdOrKey}/versions"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_project_versions_all")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_project_versions_all", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_project_versions_all",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project email
@mcp.tool()
async def get_project_email(project_id: str = Field(..., alias="projectId", description="The unique identifier of the project. Must be a positive integer.")) -> dict[str, Any]:
    """Retrieves the sender email address configured for a project. This email is used as the from address for project notifications and communications."""

    _project_id = _parse_int(project_id)

    # Construct request model with validation
    try:
        _request = _models.GetProjectEmailRequest(
            path=_models.GetProjectEmailRequestPath(project_id=_project_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_project_email: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/project/{projectId}/email", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/project/{projectId}/email"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_project_email")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_project_email", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_project_email",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def get_issue_type_hierarchy(project_id: str = Field(..., alias="projectId", description="The numeric identifier of the project for which to retrieve the issue type hierarchy.")) -> dict[str, Any]:
    """Retrieve the issue type hierarchy for a next-gen project, which defines the structural levels of issue types (Epic, Story/Task/Bug, and Subtask) and their relationships. Requires Browse projects permission."""

    _project_id = _parse_int(project_id)

    # Construct request model with validation
    try:
        _request = _models.GetHierarchyRequest(
            path=_models.GetHierarchyRequestPath(project_id=_project_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_issue_type_hierarchy: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/project/{projectId}/hierarchy", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/project/{projectId}/hierarchy"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_issue_type_hierarchy")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_issue_type_hierarchy", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_issue_type_hierarchy",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project permission schemes
@mcp.tool()
async def list_security_levels_project(project_key_or_id: str = Field(..., alias="projectKeyOrId", description="The project identifier, either the project key (case-sensitive) or the project ID.")) -> dict[str, Any]:
    """Retrieve all issue security levels available in a project that the authenticated user can access. Security levels are only returned for users with the Set Issue Security permission."""

    # Construct request model with validation
    try:
        _request = _models.GetSecurityLevelsForProjectRequest(
            path=_models.GetSecurityLevelsForProjectRequestPath(project_key_or_id=project_key_or_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_security_levels_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/project/{projectKeyOrId}/securitylevel", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/project/{projectKeyOrId}/securitylevel"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_security_levels_project")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_security_levels_project", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_security_levels_project",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project categories
@mcp.tool()
async def list_project_categories() -> dict[str, Any]:
    """Retrieves all available project categories in Jira. Use this to populate category selections or understand the complete category taxonomy."""

    # Extract parameters for API call
    _http_path = "/rest/api/3/projectCategory"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_project_categories")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_project_categories", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_project_categories",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project categories
@mcp.tool()
async def create_project_category(
    description: str | None = Field(None, description="Optional text describing the purpose and scope of this project category."),
    name: str | None = Field(None, description="The name of the project category. Required on create, optional on update."),
) -> dict[str, Any]:
    """Creates a new project category in Jira. Requires Administer Jira global permission."""

    # Construct request model with validation
    try:
        _request = _models.CreateProjectCategoryRequest(
            body=_models.CreateProjectCategoryRequestBody(description=description, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_project_category: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/projectCategory"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_project_category")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_project_category", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_project_category",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project categories
@mcp.tool()
async def get_project_category(id_: str = Field(..., alias="id", description="The unique identifier of the project category as a 64-bit integer.")) -> dict[str, Any]:
    """Retrieve a specific project category by its ID. Returns the category details for use in project organization and filtering."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.GetProjectCategoryByIdRequest(
            path=_models.GetProjectCategoryByIdRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_project_category: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/projectCategory/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/projectCategory/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_project_category")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_project_category", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_project_category",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project categories
@mcp.tool()
async def update_project_category(
    id_: str = Field(..., alias="id", description="The unique identifier of the project category to update. This is a numeric ID that identifies which category to modify."),
    description: str | None = Field(None, description="The new description text for the project category. This field is optional and can be used to update the category's descriptive information."),
) -> dict[str, Any]:
    """Updates an existing project category with new metadata. Requires Jira administrator permissions to perform this action."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.UpdateProjectCategoryRequest(
            path=_models.UpdateProjectCategoryRequestPath(id_=_id_),
            body=_models.UpdateProjectCategoryRequestBody(description=description)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_project_category: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/projectCategory/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/projectCategory/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_project_category")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_project_category", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_project_category",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project categories
@mcp.tool()
async def delete_project_category(id_: str = Field(..., alias="id", description="The unique identifier of the project category to delete, specified as a 64-bit integer.")) -> dict[str, Any]:
    """Permanently deletes a project category from Jira. Requires Administer Jira global permission."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.RemoveProjectCategoryRequest(
            path=_models.RemoveProjectCategoryRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_project_category: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/projectCategory/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/projectCategory/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_project_category")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_project_category", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_project_category",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue fields
@mcp.tool()
async def list_project_fields(
    project_id: list[int] = Field(..., alias="projectId", description="One or more project IDs to retrieve fields for. Only fields available to these projects will be returned."),
    work_type_id: list[int] = Field(..., alias="workTypeId", description="One or more work type (issue type) IDs to retrieve fields for. Only fields applicable to these work types will be returned."),
    start_at: str | None = Field(None, alias="startAt", description="The starting position for pagination (zero-indexed). Use this to retrieve subsequent pages of results."),
    max_results: str | None = Field(None, alias="maxResults", description="The number of fields to return per page. Must be between 1 and 100 items."),
    field_id: list[str] | None = Field(None, alias="fieldId", description="Optional list of specific field IDs to retrieve. If omitted, all available fields for the project and work type combination are returned."),
) -> dict[str, Any]:
    """Retrieve available fields for specified projects and work types. Returns a paginated list of fields that are applicable to the given project and work type combination, with optional filtering by specific field IDs."""

    _start_at = _parse_int(start_at)
    _max_results = _parse_int(max_results)

    # Construct request model with validation
    try:
        _request = _models.GetProjectFieldsRequest(
            query=_models.GetProjectFieldsRequestQuery(start_at=_start_at, max_results=_max_results, project_id=project_id, work_type_id=work_type_id, field_id=field_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_project_fields: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/projects/fields"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_project_fields")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_project_fields", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_project_fields",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project key and name validation
@mcp.tool()
async def validate_project_key() -> dict[str, Any]:
    """Validates a project key to ensure it is a properly formatted string and is not already in use by another project. Use this to verify key availability before creating a new project."""

    # Extract parameters for API call
    _http_path = "/rest/api/3/projectvalidate/key"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("validate_project_key")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("validate_project_key", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="validate_project_key",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project key and name validation
@mcp.tool()
async def validate_project_key_generate() -> dict[str, Any]:
    """Validates a project key and generates a valid random alternative if the provided key is invalid or already in use. No authentication required."""

    # Extract parameters for API call
    _http_path = "/rest/api/3/projectvalidate/validProjectKey"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("validate_project_key_generate")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("validate_project_key_generate", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="validate_project_key_generate",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project key and name validation
@mcp.tool()
async def validate_project_name(name: str = Field(..., description="The desired project name to validate for availability.")) -> dict[str, Any]:
    """Validates whether a project name is available. Returns the provided name if unused, attempts to generate an alternative name by appending a sequence number if the name is taken, or returns an error if no valid alternative can be generated."""

    # Construct request model with validation
    try:
        _request = _models.GetValidProjectNameRequest(
            query=_models.GetValidProjectNameRequestQuery(name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for validate_project_name: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/projectvalidate/validProjectName"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("validate_project_name")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("validate_project_name", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="validate_project_name",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue redaction
@mcp.tool()
async def redact_issue_fields(redactions: Annotated[list[_models.SingleRedactionRequest], AfterValidator(_check_unique_items)] | None = Field(None, description="Array of field redaction specifications defining which issue fields should have their data redacted. Each item specifies the field identifier and redaction parameters.")) -> dict[str, Any]:
    """Submit an asynchronous job to redact sensitive data from specified issue fields. Use the returned job ID to poll the redaction status."""

    # Construct request model with validation
    try:
        _request = _models.RedactRequest(
            body=_models.RedactRequestBody(redactions=redactions)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for redact_issue_fields: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/redact"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("redact_issue_fields")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("redact_issue_fields", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="redact_issue_fields",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue resolutions
@mcp.tool()
async def list_resolutions(
    start_at: str | None = Field(None, alias="startAt", description="The starting position for pagination, where 0 represents the first item. Use this to navigate through pages of results."),
    max_results: str | None = Field(None, alias="maxResults", description="The number of resolutions to return per page. Defaults to 50 items if not specified."),
    only_default: bool | None = Field(None, alias="onlyDefault", description="When enabled, returns only default resolutions. If specific resolution IDs are provided and none are marked as default, an empty page is returned. Only applies to company-managed projects."),
) -> dict[str, Any]:
    """Retrieve a paginated list of issue resolutions, optionally filtered by resolution IDs or default status. Useful for populating resolution dropdowns or validating resolution values in Jira."""

    # Construct request model with validation
    try:
        _request = _models.SearchResolutionsRequest(
            query=_models.SearchResolutionsRequestQuery(start_at=start_at, max_results=max_results, only_default=only_default)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_resolutions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/resolution/search"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_resolutions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_resolutions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_resolutions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue resolutions
@mcp.tool()
async def get_resolution(id_: str = Field(..., alias="id", description="The unique identifier of the resolution value to retrieve.")) -> dict[str, Any]:
    """Retrieve the details of a specific issue resolution value by its ID. This returns metadata about how an issue can be resolved in Jira."""

    # Construct request model with validation
    try:
        _request = _models.GetResolutionRequest(
            path=_models.GetResolutionRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_resolution: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/resolution/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/resolution/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_resolution")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_resolution", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_resolution",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue resolutions
@mcp.tool()
async def update_resolution(
    id_: str = Field(..., alias="id", description="The unique identifier of the issue resolution to update."),
    name: str = Field(..., description="The name of the resolution. Must be unique across all resolutions and limited to 60 characters maximum.", max_length=60),
    description: str | None = Field(None, description="The description of the resolution. Limited to 255 characters maximum.", max_length=255),
) -> dict[str, Any]:
    """Updates an existing issue resolution in Jira. Requires Administer Jira global permission to perform this action."""

    # Construct request model with validation
    try:
        _request = _models.UpdateResolutionRequest(
            path=_models.UpdateResolutionRequestPath(id_=id_),
            body=_models.UpdateResolutionRequestBody(description=description, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_resolution: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/resolution/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/resolution/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_resolution")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_resolution", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_resolution",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue resolutions
@mcp.tool()
async def delete_resolution(
    id_: str = Field(..., alias="id", description="The unique identifier of the issue resolution to delete."),
    replace_with: str = Field(..., alias="replaceWith", description="The unique identifier of the issue resolution that will replace the deleted one for all affected issues. This parameter is required to ensure no issues are left without a resolution."),
) -> dict[str, Any]:
    """Deletes an issue resolution from Jira. All issues currently using the deleted resolution will be reassigned to the specified replacement resolution. This is an asynchronous operation; check the returned task location to monitor completion status."""

    # Construct request model with validation
    try:
        _request = _models.DeleteResolutionRequest(
            path=_models.DeleteResolutionRequestPath(id_=id_),
            query=_models.DeleteResolutionRequestQuery(replace_with=replace_with)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_resolution: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/resolution/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/resolution/{id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_resolution")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_resolution", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_resolution",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project roles
@mcp.tool()
async def list_project_roles_global() -> dict[str, Any]:
    """Retrieve all project roles available in the Jira instance, including their details and default actors. Project roles are used globally across all projects for permission schemes, notifications, issue security, and workflow conditions."""

    # Extract parameters for API call
    _http_path = "/rest/api/3/role"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_project_roles_global")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_project_roles_global", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_project_roles_global",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project roles
@mcp.tool()
async def get_project_role_global(id_: str = Field(..., alias="id", description="The unique identifier of the project role as a 64-bit integer. Retrieve available project role IDs using the list project roles operation.")) -> dict[str, Any]:
    """Retrieve the details of a specific project role, including its default actors sorted by display name. Requires Jira administrator permissions."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.GetProjectRoleByIdRequest(
            path=_models.GetProjectRoleByIdRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_project_role_global: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/role/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/role/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_project_role_global")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_project_role_global", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_project_role_global",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project roles
@mcp.tool()
async def update_project_role(
    id_: str = Field(..., alias="id", description="The unique identifier of the project role to update. This is a 64-bit integer that can be obtained from the list of all project roles."),
    description: str | None = Field(None, description="The new description for the project role. This field is optional for partial updates and will only be applied if the name is not provided in the same request."),
) -> dict[str, Any]:
    """Partially update a project role by modifying either its name or description. Note that only one field can be updated per request; if both are provided, only the name will be updated."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.PartialUpdateProjectRoleRequest(
            path=_models.PartialUpdateProjectRoleRequestPath(id_=_id_),
            body=_models.PartialUpdateProjectRoleRequestBody(description=description)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_project_role: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/role/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/role/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_project_role")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_project_role", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_project_role",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project roles
@mcp.tool()
async def update_project_role_full(
    id_: str = Field(..., alias="id", description="The unique identifier of the project role to update. This is a numeric ID that can be retrieved from the list of all project roles."),
    description: str | None = Field(None, description="The new description for the project role. This field is required when fully updating a project role."),
    name: str | None = Field(None, description="The name of the project role. Must be unique. Cannot begin or end with whitespace. The maximum length is 255 characters. Required when creating a project role. Optional when partially updating a project role."),
) -> dict[str, Any]:
    """Fully update a project role by replacing its name and description. Both name and description are required for this operation."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.FullyUpdateProjectRoleRequest(
            path=_models.FullyUpdateProjectRoleRequestPath(id_=_id_),
            body=_models.FullyUpdateProjectRoleRequestBody(description=description, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_project_role_full: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/role/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/role/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_project_role_full")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_project_role_full", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_project_role_full",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project roles
@mcp.tool()
async def delete_project_role(
    id_: str = Field(..., alias="id", description="The unique identifier of the project role to delete. Retrieve available project role IDs using the list project roles operation."),
    swap: str | None = Field(None, description="The unique identifier of a project role to replace the deleted role across all schemes, workflows, worklogs, and comments. Required if the role being deleted is currently in use."),
) -> dict[str, Any]:
    """Deletes a project role from your Jira instance. If the role is currently in use, you must specify a replacement role to reassign its associations in schemes, workflows, worklogs, and comments."""

    _id_ = _parse_int(id_)
    _swap = _parse_int(swap)

    # Construct request model with validation
    try:
        _request = _models.DeleteProjectRoleRequest(
            path=_models.DeleteProjectRoleRequestPath(id_=_id_),
            query=_models.DeleteProjectRoleRequestQuery(swap=_swap)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_project_role: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/role/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/role/{id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_project_role")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_project_role", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_project_role",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Screens
@mcp.tool()
async def list_screen_fields(screen_id: str = Field(..., alias="screenId", description="The unique identifier of the screen. Must be a positive integer.")) -> dict[str, Any]:
    """Retrieve all fields available to be added to a screen tab. This helps identify which fields can be configured for a specific screen layout."""

    _screen_id = _parse_int(screen_id)

    # Construct request model with validation
    try:
        _request = _models.GetAvailableScreenFieldsRequest(
            path=_models.GetAvailableScreenFieldsRequestPath(screen_id=_screen_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_screen_fields: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/screens/{screenId}/availableFields", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/screens/{screenId}/availableFields"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_screen_fields")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_screen_fields", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_screen_fields",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue search
@mcp.tool()
async def count_issues(jql: str | None = Field(None, description="A JQL query expression to filter issues. The query must include at least one search restriction (bounded query) for performance reasons.")) -> dict[str, Any]:
    """Get an estimated count of issues matching a JQL query. Returns a fast approximate count for issues the user has permission to view; note that recent updates may not be immediately reflected."""

    # Construct request model with validation
    try:
        _request = _models.CountIssuesRequest(
            body=_models.CountIssuesRequestBody(jql=jql)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for count_issues: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/search/approximate-count"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("count_issues")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("count_issues", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="count_issues",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue search
@mcp.tool()
async def search_issues(
    jql: str | None = Field(None, description="A JQL expression to filter issues. Must include a search restriction (bounded query) for performance—for example, filtering by project, assignee, or status. The orderBy clause supports a maximum of 7 fields. Unbounded queries like 'order by key desc' are not permitted."),
    max_results: str | None = Field(None, alias="maxResults", description="Maximum number of issues to return per page, up to 5000. The API may return fewer items when many fields or properties are requested. Defaults to 50 items per page."),
    reconcile_issues: list[int] | None = Field(None, alias="reconcileIssues", description="List of up to 50 issue IDs to reconcile with search results for stronger consistency guarantees. Use this when read-after-write consistency is critical. The same list should be included across all paginated requests."),
) -> dict[str, Any]:
    """Search for issues using JQL (Jira Query Language) with optional read-after-write consistency reconciliation. Results reflect issues where you have browse permissions on the containing project and any applicable issue-level security permissions."""

    _max_results = _parse_int(max_results)

    # Construct request model with validation
    try:
        _request = _models.SearchAndReconsileIssuesUsingJqlRequest(
            query=_models.SearchAndReconsileIssuesUsingJqlRequestQuery(jql=jql, max_results=_max_results, reconcile_issues=reconcile_issues)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_issues: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/search/jql"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_issues")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_issues", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_issues",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue search
@mcp.tool()
async def search_issues_jql(
    jql: str | None = Field(None, description="A JQL expression to filter issues. Must include at least one search restriction (e.g., assignee, project, status) to be considered bounded. The orderBy clause supports a maximum of 7 fields."),
    max_results: str | None = Field(None, alias="maxResults", description="Maximum number of issues to return per page, up to 5000. Defaults to 50 items per page. Actual results may be fewer when requesting many fields."),
    reconcile_issues: list[int] | None = Field(None, alias="reconcileIssues", description="List of up to 50 issue IDs to reconcile with search results for stronger consistency guarantees. Use the same list across all paginated requests to ensure consistency."),
) -> dict[str, Any]:
    """Search for issues using JQL with optional read-after-write consistency reconciliation. Requires a bounded query with at least one search restriction for optimal performance."""

    _max_results = _parse_int(max_results)

    # Construct request model with validation
    try:
        _request = _models.SearchAndReconsileIssuesUsingJqlPostRequest(
            body=_models.SearchAndReconsileIssuesUsingJqlPostRequestBody(jql=jql, max_results=_max_results, reconcile_issues=reconcile_issues)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_issues_jql: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/search/jql"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_issues_jql")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_issues_jql", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_issues_jql",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue security level
@mcp.tool()
async def get_security_level(id_: str = Field(..., alias="id", description="The unique identifier of the issue security level to retrieve.")) -> dict[str, Any]:
    """Retrieve detailed information about a specific issue security level. Use this to get security level properties after obtaining the level ID from the issue security scheme."""

    # Construct request model with validation
    try:
        _request = _models.GetIssueSecurityLevelRequest(
            path=_models.GetIssueSecurityLevelRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_security_level: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/securitylevel/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/securitylevel/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_security_level")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_security_level", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_security_level",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Workflow statuses
@mcp.tool()
async def list_statuses() -> dict[str, Any]:
    """Retrieves all statuses associated with active workflows in Jira. This operation is useful for understanding the available status values that can be assigned to issues across your projects."""

    # Extract parameters for API call
    _http_path = "/rest/api/3/status"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_statuses")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_statuses", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_statuses",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Workflow statuses
@mcp.tool()
async def get_status(id_or_name: str = Field(..., alias="idOrName", description="The unique identifier or display name of the status. Using the status ID is preferred when the name may not be unique across your instance.")) -> dict[str, Any]:
    """Retrieve a status associated with an active workflow by its ID or name. If multiple statuses share the same name, the first match is returned; using the status ID is recommended for precise identification."""

    # Construct request model with validation
    try:
        _request = _models.GetStatusRequest(
            path=_models.GetStatusRequestPath(id_or_name=id_or_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/status/{idOrName}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/status/{idOrName}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_status")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_status", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_status",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Workflow status categories
@mcp.tool()
async def list_status_categories() -> dict[str, Any]:
    """Retrieves all available status categories in Jira. Status categories group statuses by their workflow state (e.g., To Do, In Progress, Done)."""

    # Extract parameters for API call
    _http_path = "/rest/api/3/statuscategory"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_status_categories")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_status_categories", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_status_categories",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Workflow status categories
@mcp.tool()
async def get_status_category(id_or_key: str = Field(..., alias="idOrKey", description="The unique identifier or key of the status category to retrieve.")) -> dict[str, Any]:
    """Retrieve a status category by its ID or key. Status categories are used to group and organize statuses in Jira workflows."""

    # Construct request model with validation
    try:
        _request = _models.GetStatusCategoryRequest(
            path=_models.GetStatusCategoryRequestPath(id_or_key=id_or_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_status_category: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/statuscategory/{idOrKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/statuscategory/{idOrKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_status_category")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_status_category", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_status_category",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Status
@mcp.tool()
async def list_statuses_bulk(id_: list[str] = Field(..., alias="id", description="One or more status IDs to retrieve. Provide between 1 and 50 IDs in a single request.")) -> dict[str, Any]:
    """Retrieve detailed information for one or more statuses by their IDs. Useful for fetching status configurations needed for workflow operations or validation."""

    # Construct request model with validation
    try:
        _request = _models.GetStatusesByIdRequest(
            query=_models.GetStatusesByIdRequestQuery(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_statuses_bulk: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/statuses"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_statuses_bulk")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_statuses_bulk", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_statuses_bulk",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Status
@mcp.tool()
async def delete_statuses(id_: list[str] = Field(..., alias="id", description="One or more status IDs to delete. Provide between 1 and 50 IDs in a single request.")) -> dict[str, Any]:
    """Permanently delete one or more statuses by their IDs. Requires either Administer projects or Administer Jira permission."""

    # Construct request model with validation
    try:
        _request = _models.DeleteStatusesByIdRequest(
            query=_models.DeleteStatusesByIdRequestQuery(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_statuses: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/statuses"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_statuses")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_statuses", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_statuses",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Status
@mcp.tool()
async def list_statuses_by_name(
    name: list[str] = Field(..., description="One or more status names to retrieve. Provide between 1 and 50 names as an ampersand-separated list."),
    project_id: str | None = Field(None, alias="projectId", description="Optional project ID to scope the status lookup to a specific project. Omit or use null to retrieve global statuses."),
) -> dict[str, Any]:
    """Retrieve a list of statuses by their names. Supports bulk lookup of up to 50 status names, optionally scoped to a specific project or global statuses."""

    # Construct request model with validation
    try:
        _request = _models.GetStatusesByNameRequest(
            query=_models.GetStatusesByNameRequestQuery(name=name, project_id=project_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_statuses_by_name: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/statuses/byNames"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_statuses_by_name")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_statuses_by_name", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_statuses_by_name",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Status
@mcp.tool()
async def search_statuses(
    project_id: str | None = Field(None, alias="projectId", description="The project ID to filter statuses to a specific project, or omit to search global statuses."),
    start_at: str | None = Field(None, alias="startAt", description="The starting position for pagination (zero-indexed). Defaults to 0 if not specified."),
    max_results: str | None = Field(None, alias="maxResults", description="The maximum number of statuses to return per page. Defaults to 200 if not specified."),
    search_string: str | None = Field(None, alias="searchString", description="A search term to match against status names. Omit or leave empty to return all statuses in the search scope. Limited to 255 characters.", max_length=255),
    status_category: str | None = Field(None, alias="statusCategory", description="Filter results by status category: TODO, IN_PROGRESS, or DONE. Omit to include all categories."),
) -> dict[str, Any]:
    """Search for statuses by name or project, returning paginated results. Requires project administration or Jira administration permissions."""

    _start_at = _parse_int(start_at)
    _max_results = _parse_int(max_results)

    # Construct request model with validation
    try:
        _request = _models.SearchRequest(
            query=_models.SearchRequestQuery(project_id=project_id, start_at=_start_at, max_results=_max_results, search_string=search_string, status_category=status_category)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_statuses: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/statuses/search"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_statuses")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_statuses", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_statuses",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Status
@mcp.tool()
async def list_issue_type_usages(
    status_id: str = Field(..., alias="statusId", description="The unique identifier of the status to query for issue type usage."),
    project_id: str = Field(..., alias="projectId", description="The unique identifier of the project to filter issue type usages."),
    max_results: str | None = Field(None, alias="maxResults", description="The maximum number of results to return per page. Must be between 1 and 200, defaults to 50 if not specified."),
) -> dict[str, Any]:
    """Retrieves the issue types currently using a specific status within a project. Returns paginated results showing which issue types are associated with the given status."""

    _max_results = _parse_int(max_results)

    # Construct request model with validation
    try:
        _request = _models.GetProjectIssueTypeUsagesForStatusRequest(
            path=_models.GetProjectIssueTypeUsagesForStatusRequestPath(status_id=status_id, project_id=project_id),
            query=_models.GetProjectIssueTypeUsagesForStatusRequestQuery(max_results=_max_results)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_issue_type_usages: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/statuses/{statusId}/project/{projectId}/issueTypeUsages", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/statuses/{statusId}/project/{projectId}/issueTypeUsages"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_issue_type_usages")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_issue_type_usages", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_issue_type_usages",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Status
@mcp.tool()
async def list_project_usages_by_status(
    status_id: str = Field(..., alias="statusId", description="The unique identifier of the status to query for project usage."),
    max_results: str | None = Field(None, alias="maxResults", description="The maximum number of results to return per page. Must be between 1 and 200, defaults to 50 results."),
) -> dict[str, Any]:
    """Retrieves a paginated list of projects that use a specific status. Useful for understanding status adoption and impact across your Jira instance."""

    _max_results = _parse_int(max_results)

    # Construct request model with validation
    try:
        _request = _models.GetProjectUsagesForStatusRequest(
            path=_models.GetProjectUsagesForStatusRequestPath(status_id=status_id),
            query=_models.GetProjectUsagesForStatusRequestQuery(max_results=_max_results)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_project_usages_by_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/statuses/{statusId}/projectUsages", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/statuses/{statusId}/projectUsages"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_project_usages_by_status")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_project_usages_by_status", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_project_usages_by_status",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Status
@mcp.tool()
async def list_workflow_usages_by_status(
    status_id: str = Field(..., alias="statusId", description="The unique identifier of the status for which to retrieve workflow usages."),
    max_results: str | None = Field(None, alias="maxResults", description="The maximum number of workflow results to return per page. Must be between 1 and 200, with a default of 50 results."),
) -> dict[str, Any]:
    """Retrieve a paginated list of workflows that use a specific status. This helps identify which workflows are affected by changes to a given status."""

    _max_results = _parse_int(max_results)

    # Construct request model with validation
    try:
        _request = _models.GetWorkflowUsagesForStatusRequest(
            path=_models.GetWorkflowUsagesForStatusRequestPath(status_id=status_id),
            query=_models.GetWorkflowUsagesForStatusRequestQuery(max_results=_max_results)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_workflow_usages_by_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/statuses/{statusId}/workflowUsages", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/statuses/{statusId}/workflowUsages"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_workflow_usages_by_status")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_workflow_usages_by_status", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_workflow_usages_by_status",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tasks
@mcp.tool()
async def get_task(task_id: str = Field(..., alias="taskId", description="The unique identifier of the task to retrieve status and results for.")) -> dict[str, Any]:
    """Retrieve the status and results of a long-running asynchronous task. Once completed, returns the JSON response applicable to the task; details are retained for 14 days."""

    # Construct request model with validation
    try:
        _request = _models.GetTaskRequest(
            path=_models.GetTaskRequestPath(task_id=task_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_task: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/task/{taskId}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/task/{taskId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_task")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_task", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_task",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tasks
@mcp.tool()
async def cancel_task(task_id: str = Field(..., alias="taskId", description="The unique identifier of the task to cancel.")) -> dict[str, Any]:
    """Cancels an active task in Jira. Requires either Jira administrator permissions or creator status of the task."""

    # Construct request model with validation
    try:
        _request = _models.CancelTaskRequest(
            path=_models.CancelTaskRequestPath(task_id=task_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for cancel_task: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/task/{taskId}/cancel", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/task/{taskId}/cancel"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("cancel_task")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("cancel_task", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="cancel_task",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Avatars
@mcp.tool()
async def list_avatars(
    type_: Literal["project", "issuetype", "priority"] = Field(..., alias="type", description="The category of avatar to retrieve: project, issue type, or priority."),
    entity_id: str = Field(..., alias="entityId", description="The unique identifier of the entity (project, issue type, or priority) associated with the avatars."),
) -> dict[str, Any]:
    """Retrieves all available avatars (system and custom) for a project, issue type, or priority. Supports anonymous access for system and priority avatars, with permission checks for custom project and issue type avatars."""

    # Construct request model with validation
    try:
        _request = _models.GetAvatarsRequest(
            path=_models.GetAvatarsRequestPath(type_=type_, entity_id=entity_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_avatars: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/universal_avatar/type/{type}/owner/{entityId}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/universal_avatar/type/{type}/owner/{entityId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_avatars")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_avatars", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_avatars",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Avatars
@mcp.tool()
async def upload_avatar(
    type_: Literal["project", "issuetype", "priority"] = Field(..., alias="type", description="The category of entity receiving the avatar. Must be one of: project, issuetype, or priority."),
    entity_id: str = Field(..., alias="entityId", description="The unique identifier of the entity (project, issue type, or priority) that will use this avatar."),
    size: str = Field(..., description="The width and height (in pixels) of the square crop region. The cropped area is extracted from the uploaded image starting at the specified X and Y coordinates."),
    x: str | None = Field(None, description="The X coordinate (in pixels) of the top-left corner of the crop region. Defaults to 0 if not specified."),
    y: str | None = Field(None, description="The Y coordinate (in pixels) of the top-left corner of the crop region. Defaults to 0 if not specified."),
) -> dict[str, Any]:
    """Upload a custom avatar image for a project, issue type, or priority. The image is automatically cropped to a square and resized into multiple formats (16x16, 24x24, 32x32, 48x48 pixels). Requires Administer Jira global permission."""

    _size = _parse_int(size)
    _x = _parse_int(x)
    _y = _parse_int(y)

    # Construct request model with validation
    try:
        _request = _models.StoreAvatarRequest(
            path=_models.StoreAvatarRequestPath(type_=type_, entity_id=entity_id),
            query=_models.StoreAvatarRequestQuery(x=_x, y=_y, size=_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for upload_avatar: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/universal_avatar/type/{type}/owner/{entityId}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/universal_avatar/type/{type}/owner/{entityId}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("upload_avatar")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("upload_avatar", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="upload_avatar",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Avatars
@mcp.tool()
async def delete_avatar(
    type_: Literal["project", "issuetype", "priority"] = Field(..., alias="type", description="The category of object the avatar belongs to: project, issue type, or priority."),
    owning_object_id: str = Field(..., alias="owningObjectId", description="The unique identifier of the project, issue type, or priority that owns the avatar."),
    id_: str = Field(..., alias="id", description="The unique numeric identifier of the avatar to delete."),
) -> dict[str, Any]:
    """Permanently removes a custom avatar from a project, issue type, or priority. Requires Jira administrator permissions."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.DeleteAvatarRequest(
            path=_models.DeleteAvatarRequestPath(type_=type_, owning_object_id=owning_object_id, id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_avatar: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/universal_avatar/type/{type}/owner/{owningObjectId}/avatar/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/universal_avatar/type/{type}/owner/{owningObjectId}/avatar/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_avatar")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_avatar", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_avatar",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Avatars
@mcp.tool()
async def get_avatar_image_by_avatar_id(
    type_: Literal["issuetype", "project", "priority"] = Field(..., alias="type", description="The avatar category: either 'issuetype' for issue type avatars, 'project' for project avatars, or 'priority' for priority avatars."),
    id_: str = Field(..., alias="id", description="The unique identifier of the avatar to retrieve."),
    size: Literal["xsmall", "small", "medium", "large", "xlarge"] | None = Field(None, description="The desired image size: 'xsmall', 'small', 'medium', 'large', or 'xlarge'. If omitted, the default size is returned."),
    format_: Literal["png", "svg"] | None = Field(None, alias="format", description="The image format to return: either 'png' or 'svg'. If omitted, the avatar's original format is returned."),
) -> dict[str, Any]:
    """Retrieves an avatar image for a project, issue type, or priority by ID. Returns the image in the requested size and format, or defaults to the original if not specified."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.GetAvatarImageByIdRequest(
            path=_models.GetAvatarImageByIdRequestPath(type_=type_, id_=_id_),
            query=_models.GetAvatarImageByIdRequestQuery(size=size, format_=format_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_avatar_image_by_avatar_id: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/universal_avatar/view/type/{type}/avatar/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/universal_avatar/view/type/{type}/avatar/{id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_avatar_image_by_avatar_id")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_avatar_image_by_avatar_id", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_avatar_image_by_avatar_id",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Avatars
@mcp.tool()
async def get_avatar_image_by_entity(
    type_: Literal["issuetype", "project", "priority"] = Field(..., alias="type", description="The avatar type to retrieve: either 'issuetype', 'project', or 'priority'."),
    entity_id: str = Field(..., alias="entityId", description="The unique identifier of the entity (project or issue type) that owns the avatar."),
    size: Literal["xsmall", "small", "medium", "large", "xlarge"] | None = Field(None, description="The desired avatar image size: xsmall, small, medium, large, or xlarge. Defaults to the original size if not specified."),
    format_: Literal["png", "svg"] | None = Field(None, alias="format", description="The image format to return: either 'png' or 'svg'. Defaults to the original content format if not specified."),
) -> dict[str, Any]:
    """Retrieves the avatar image for a project, issue type, or priority in the specified size and format. This operation can be accessed anonymously, though custom avatars may require project browse permissions."""

    # Construct request model with validation
    try:
        _request = _models.GetAvatarImageByOwnerRequest(
            path=_models.GetAvatarImageByOwnerRequestPath(type_=type_, entity_id=entity_id),
            query=_models.GetAvatarImageByOwnerRequestQuery(size=size, format_=format_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_avatar_image_by_entity: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/universal_avatar/view/type/{type}/owner/{entityId}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/universal_avatar/view/type/{type}/owner/{entityId}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_avatar_image_by_entity")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_avatar_image_by_entity", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_avatar_image_by_entity",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Users
@mcp.tool()
async def get_user(account_id: str | None = Field(None, alias="accountId", description="The account ID of the user, which uniquely identifies the user across all Atlassian products. For example, *5b10ac8d82e05b22cc7d4ef5*. Required.", max_length=128)) -> dict[str, Any]:
    """Retrieve a user's profile information from Jira. Privacy controls are applied based on the user's preferences, which may hide sensitive details like email addresses."""

    # Construct request model with validation
    try:
        _request = _models.GetUserRequest(
            query=_models.GetUserRequestQuery(account_id=account_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/user"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_user", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_user",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Users
@mcp.tool()
async def create_user(
    email_address: str = Field(..., alias="emailAddress", description="The email address for the new user. This serves as the unique identifier for the user account."),
    products: Annotated[list[str], AfterValidator(_check_unique_items)] = Field(..., description="An array of products the user should have access to. Valid options include jira-core, jira-servicedesk, jira-product-discovery, and jira-software. Pass an empty array to create a user without any product access."),
) -> dict[str, Any]:
    """Creates a new user in Jira with specified product access. Returns 201 if the user is created or already exists with access, or 400 if the user exists without access. Requires Administer Jira global permission and organization admin status."""

    # Construct request model with validation
    try:
        _request = _models.CreateUserRequest(
            body=_models.CreateUserRequestBody(email_address=email_address, products=products)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/user"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_user", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_user",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Users
@mcp.tool()
async def delete_user(account_id: str = Field(..., alias="accountId", description="The unique account ID that identifies the user across all Atlassian products. This is a string identifier up to 128 characters long (for example, 5b10ac8d82e05b22cc7d4ef5).", max_length=128)) -> dict[str, Any]:
    """Permanently removes a user from Jira's user base. Note that this operation only deletes the user's Jira account and does not affect their Atlassian account."""

    # Construct request model with validation
    try:
        _request = _models.RemoveUserRequest(
            query=_models.RemoveUserRequestQuery(account_id=account_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/user"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_user", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_user",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: User search
@mcp.tool()
async def list_assignable_users_multiproject(
    project_keys: str = Field(..., alias="projectKeys", description="Comma-separated list of project keys (case-sensitive) to search for assignable users. At least one project key is required."),
    start_at: str | None = Field(None, alias="startAt", description="Zero-based index for pagination to specify which result page to return. Defaults to 0 if not provided."),
    max_results: str | None = Field(None, alias="maxResults", description="Maximum number of users to return per page. Defaults to 50 if not provided."),
) -> dict[str, Any]:
    """Retrieve users who can be assigned issues across one or more projects. Results are filtered based on user attributes and privacy settings, and may return fewer users than requested due to pagination constraints."""

    _start_at = _parse_int(start_at)
    _max_results = _parse_int(max_results)

    # Construct request model with validation
    try:
        _request = _models.FindBulkAssignableUsersRequest(
            query=_models.FindBulkAssignableUsersRequestQuery(project_keys=project_keys, start_at=_start_at, max_results=_max_results)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_assignable_users_multiproject: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/user/assignable/multiProjectSearch"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_assignable_users_multiproject")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_assignable_users_multiproject", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_assignable_users_multiproject",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: User search
@mcp.tool()
async def list_assignable_users(
    issue_id: str | None = Field(None, alias="issueId", description="The issue ID to check assignability against. Required unless issueKey or project is specified."),
    start_at: str | None = Field(None, alias="startAt", description="The starting position for pagination (zero-indexed). Defaults to 0 for the first page."),
    max_results: str | None = Field(None, alias="maxResults", description="Maximum number of users to return per page. Defaults to 50. Note: the operation may return fewer users than requested, as it filters results to only assignable users."),
    action_descriptor_id: str | None = Field(None, alias="actionDescriptorId", description="The workflow transition ID to check assignability during a state change. Use with issueKey or issueId to validate users for a specific transition."),
    account_type: list[str] | None = Field(None, alias="accountType", description="Filter results by account type (e.g., atlassian, app, customer). Specify as a comma-separated list if multiple types are needed."),
) -> dict[str, Any]:
    """Retrieve a list of users who can be assigned to an issue, optionally filtered by project, issue, or workflow transition. Use this to populate assignee dropdowns or validate user assignment eligibility."""

    _start_at = _parse_int(start_at)
    _max_results = _parse_int(max_results)
    _action_descriptor_id = _parse_int(action_descriptor_id)

    # Construct request model with validation
    try:
        _request = _models.FindAssignableUsersRequest(
            query=_models.FindAssignableUsersRequestQuery(issue_id=issue_id, start_at=_start_at, max_results=_max_results, action_descriptor_id=_action_descriptor_id, account_type=account_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_assignable_users: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/user/assignable/search"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_assignable_users")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_assignable_users", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_assignable_users",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Users
@mcp.tool()
async def list_users_by_account_ids(
    account_id: list[str] = Field(..., alias="accountId", description="One or more user account IDs to retrieve. Specify multiple account IDs to fetch multiple users in a single request. Each account ID must not exceed 128 characters.", max_length=128),
    start_at: str | None = Field(None, alias="startAt", description="The starting position for pagination, where 0 is the first user. Use this to navigate through pages of results."),
    max_results: str | None = Field(None, alias="maxResults", description="The number of users to return per page. Defaults to 10 if not specified."),
) -> dict[str, Any]:
    """Retrieve a paginated list of Jira users by their account IDs. Requires permission to access Jira."""

    _start_at = _parse_int(start_at)
    _max_results = _parse_int(max_results)

    # Construct request model with validation
    try:
        _request = _models.BulkGetUsersRequest(
            query=_models.BulkGetUsersRequestQuery(start_at=_start_at, max_results=_max_results, account_id=account_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_users_by_account_ids: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/user/bulk"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_users_by_account_ids")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_users_by_account_ids", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_users_by_account_ids",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Users
@mcp.tool()
async def list_user_account_ids(
    start_at: str | None = Field(None, alias="startAt", description="The starting position for pagination, where 0 represents the first item. Use this to retrieve subsequent pages of results."),
    max_results: str | None = Field(None, alias="maxResults", description="The maximum number of user results to return in a single page. Defaults to 10 items per page."),
    key: list[str] | None = Field(None, description="Key of a user. To specify multiple users, pass multiple copies of this parameter. For example, `key=fred&key=barney`. Required if `username` isn't provided. Cannot be provided if `username` is present."),
    username: list[str] | None = Field(None, description="Username of a user. To specify multiple users, pass multiple copies of this parameter. For example, `username=fred&username=barney`. Required if `key` isn't provided. Cannot be provided if `key` is present."),
) -> dict[str, Any]:
    """Retrieve account IDs for specified users by their key or username. This operation supports pagination and is useful for migrating or bulk-processing user data."""

    _start_at = _parse_int(start_at)
    _max_results = _parse_int(max_results)

    # Construct request model with validation
    try:
        _request = _models.BulkGetUsersMigrationRequest(
            query=_models.BulkGetUsersMigrationRequestQuery(start_at=_start_at, max_results=_max_results, key=key, username=username)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_user_account_ids: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/user/bulk/migration"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_user_account_ids")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_user_account_ids", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_user_account_ids",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Users
@mcp.tool()
async def list_user_default_columns() -> dict[str, Any]:
    """Retrieves the default issue table columns configured for a user. Returns the calling user's column preferences unless an account ID is specified, which requires Jira administration permissions."""

    # Extract parameters for API call
    _http_path = "/rest/api/3/user/columns"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_user_default_columns")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_user_default_columns", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_user_default_columns",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Users
@mcp.tool()
async def list_user_groups(account_id: str = Field(..., alias="accountId", description="The unique account ID of the user across all Atlassian products (up to 128 characters).", max_length=128)) -> dict[str, Any]:
    """Retrieve all groups that a user belongs to. Requires Browse users and groups global permission."""

    # Construct request model with validation
    try:
        _request = _models.GetUserGroupsRequest(
            query=_models.GetUserGroupsRequestQuery(account_id=account_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_user_groups: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/user/groups"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_user_groups")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_user_groups", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_user_groups",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: User search
@mcp.tool()
async def search_users_by_permissions(
    permissions: str = Field(..., description="Comma-separated list of permission identifiers to filter users. Use permission keys from the Jira permissions API, custom project permissions from Connect apps, or deprecated permission constants like BROWSE, CREATE_ISSUE, or PROJECT_ADMIN."),
    start_at: str | None = Field(None, alias="startAt", description="Zero-based index for pagination to specify which result page to retrieve. Defaults to 0 for the first page."),
    max_results: str | None = Field(None, alias="maxResults", description="Maximum number of users to return per page, up to 50 results. Defaults to 50. Note that the actual number returned may be fewer due to search filtering."),
    project_key: str | None = Field(None, alias="projectKey", description="The project key for the project (case sensitive)."),
    issue_key: str | None = Field(None, alias="issueKey", description="The issue key for the issue."),
) -> dict[str, Any]:
    """Search for users who have specific permissions in a project or issue and match optional search criteria. Returns matching users with privacy controls applied based on user preferences."""

    _start_at = _parse_int(start_at)
    _max_results = _parse_int(max_results)

    # Construct request model with validation
    try:
        _request = _models.FindUsersWithAllPermissionsRequest(
            query=_models.FindUsersWithAllPermissionsRequestQuery(permissions=permissions, start_at=_start_at, max_results=_max_results, project_key=project_key, issue_key=issue_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_users_by_permissions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/user/permission/search"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_users_by_permissions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_users_by_permissions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_users_by_permissions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: User search
@mcp.tool()
async def search_users_picker(
    query: str = Field(..., description="Search query matched against user attributes such as displayName and emailAddress. Supports prefix matching, so partial names and email prefixes will return relevant results."),
    max_results: str | None = Field(None, alias="maxResults", description="Maximum number of users to return in the results, up to 1000. Defaults to 50 if not specified. The total count of matched users is provided separately."),
    exclude_account_ids: list[str] | None = Field(None, alias="excludeAccountIds", description="List of user account IDs to exclude from search results. Accepts comma-separated or ampersand-separated format for multiple IDs."),
) -> dict[str, Any]:
    """Search for users by matching query terms against user attributes like display name and email address. Returns matching users with highlighted query matches in HTML format, with optional filtering to exclude specific users."""

    _max_results = _parse_int(max_results)

    # Construct request model with validation
    try:
        _request = _models.FindUsersForPickerRequest(
            query=_models.FindUsersForPickerRequestQuery(query=query, max_results=_max_results, exclude_account_ids=exclude_account_ids)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_users_picker: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/user/picker"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_users_picker")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_users_picker", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_users_picker",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: User properties
@mcp.tool()
async def list_user_property_keys(account_id: str | None = Field(None, alias="accountId", description="The account ID of the user, which uniquely identifies the user across all Atlassian products. For example, *5b10ac8d82e05b22cc7d4ef5*.", max_length=128)) -> dict[str, Any]:
    """Retrieves all property keys associated with a user. These are custom properties stored at the user level, distinct from Jira user profile properties."""

    # Construct request model with validation
    try:
        _request = _models.GetUserPropertyKeysRequest(
            query=_models.GetUserPropertyKeysRequestQuery(account_id=account_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_user_property_keys: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/user/properties"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_user_property_keys")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_user_property_keys", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_user_property_keys",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: User properties
@mcp.tool()
async def get_user_property(
    property_key: str = Field(..., alias="propertyKey", description="The unique identifier for the user property you want to retrieve."),
    account_id: str | None = Field(None, alias="accountId", description="The account ID of the user, which uniquely identifies the user across all Atlassian products. For example, *5b10ac8d82e05b22cc7d4ef5*.", max_length=128),
) -> dict[str, Any]:
    """Retrieves the value of a specific property associated with a user account. Requires either Jira administrator permissions to access any user's properties, or standard Jira access to retrieve properties from your own user record."""

    # Construct request model with validation
    try:
        _request = _models.GetUserPropertyRequest(
            path=_models.GetUserPropertyRequestPath(property_key=property_key),
            query=_models.GetUserPropertyRequestQuery(account_id=account_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_user_property: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/user/properties/{propertyKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/user/properties/{propertyKey}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_user_property")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_user_property", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_user_property",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: User properties
@mcp.tool()
async def remove_user_property(property_key: str = Field(..., alias="propertyKey", description="The unique identifier for the user property to delete. This key must match an existing property on the user's profile.")) -> dict[str, Any]:
    """Removes a custom property from a user's profile. Requires either Jira administrator permissions to delete properties from any user, or standard Jira access to delete properties from your own user record."""

    # Construct request model with validation
    try:
        _request = _models.DeleteUserPropertyRequest(
            path=_models.DeleteUserPropertyRequestPath(property_key=property_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_user_property: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/user/properties/{propertyKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/user/properties/{propertyKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_user_property")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_user_property", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_user_property",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: User search
@mcp.tool()
async def search_users(
    start_at: str | None = Field(None, alias="startAt", description="The starting position for paginated results, where 0 is the first user. Use this to retrieve subsequent pages of results."),
    max_results: str | None = Field(None, alias="maxResults", description="The number of users to return per page. Defaults to 50 users per page."),
    property_: str | None = Field(None, alias="property", description="A property query string to filter users by custom properties using dot notation for nested values (e.g., `propertykey.nested.field=value`). Required unless `accountId` or `query` is specified."),
    query: str | None = Field(None, description="A query string that is matched against user attributes ( `displayName`, and `emailAddress`) to find relevant users. The string can match the prefix of the attribute's value. For example, *query=john* matches a user with a `displayName` of *John Smith* and a user with an `emailAddress` of *johnson@example.com*. Required, unless `accountId` or `property` is specified."),
    account_id: str | None = Field(None, alias="accountId", description="A query string that is matched exactly against a user `accountId`. Required, unless `query` or `property` is specified.", max_length=128),
) -> dict[str, Any]:
    """Search for active users by name or property. Returns matching users with privacy controls applied based on user preferences. Requires Browse users and groups permission; anonymous calls return empty results."""

    _start_at = _parse_int(start_at)
    _max_results = _parse_int(max_results)

    # Construct request model with validation
    try:
        _request = _models.FindUsersRequest(
            query=_models.FindUsersRequestQuery(start_at=_start_at, max_results=_max_results, property_=property_, query=query, account_id=account_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_users: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/user/search"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_users")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_users", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_users",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: User search
@mcp.tool()
async def search_users_query(
    query: str = Field(..., description="A structured query string to filter users. Supports queries like 'is assignee of PROJ', 'is reporter of (PROJ-1, PROJ-2)', or custom property matching with AND/OR operators for complex filters."),
    start_at: str | None = Field(None, alias="startAt", description="The zero-based index where the result page begins. Use this to paginate through results in combination with maxResults."),
    max_results: str | None = Field(None, alias="maxResults", description="The maximum number of users to return per page. Defaults to 100 if not specified."),
) -> dict[str, Any]:
    """Search for users using structured queries based on their involvement with issues, projects, or custom properties. Returns a paginated list of matching user details."""

    _start_at = _parse_int(start_at)
    _max_results = _parse_int(max_results)

    # Construct request model with validation
    try:
        _request = _models.FindUsersByQueryRequest(
            query=_models.FindUsersByQueryRequestQuery(query=query, start_at=_start_at, max_results=_max_results)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_users_query: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/user/search/query"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_users_query")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_users_query", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_users_query",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: User search
@mcp.tool()
async def search_users_by_query(
    query: str = Field(..., description="A structured query string using statements like 'is assignee of PROJ', 'is reporter of (PROJ-1, PROJ-2)', or property matching syntax. Multiple statements can be combined with AND/OR operators to create complex queries."),
    start_at: str | None = Field(None, alias="startAt", description="The zero-based index where the result page begins. Use this to paginate through results in combination with maxResult."),
    max_result: str | None = Field(None, alias="maxResult", description="The maximum number of user keys to return per page, up to 100 items. Defaults to 100 if not specified."),
) -> dict[str, Any]:
    """Search for users using structured query syntax to find assignees, reporters, watchers, voters, commenters, or transitioners of specific issues, or match users by custom properties. Returns a paginated list of user keys matching the query criteria."""

    _start_at = _parse_int(start_at)
    _max_result = _parse_int(max_result)

    # Construct request model with validation
    try:
        _request = _models.FindUserKeysByQueryRequest(
            query=_models.FindUserKeysByQueryRequestQuery(query=query, start_at=_start_at, max_result=_max_result)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_users_by_query: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/user/search/query/key"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_users_by_query")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_users_by_query", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_users_by_query",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: User search
@mcp.tool()
async def search_browsable_users(
    start_at: str | None = Field(None, alias="startAt", description="The starting position for pagination, where 0 is the first user. Use this to retrieve subsequent pages of results."),
    max_results: str | None = Field(None, alias="maxResults", description="The maximum number of users to return per page, up to 50 by default. The operation may return fewer results if fewer users match the search criteria."),
    query: str | None = Field(None, description="A query string that is matched against user attributes, such as `displayName` and `emailAddress`, to find relevant users. The string can match the prefix of the attribute's value. For example, *query=john* matches a user with a `displayName` of *John Smith* and a user with an `emailAddress` of *johnson@example.com*. Required, unless `accountId` is specified."),
    project_key: str | None = Field(None, alias="projectKey", description="The project key for the project (case sensitive). Required, unless `issueKey` is specified."),
    issue_key: str | None = Field(None, alias="issueKey", description="The issue key for the issue. Required, unless `projectKey` is specified."),
) -> dict[str, Any]:
    """Search for users who have permission to browse issues and match the given search criteria. Results can be filtered by a specific issue or project, with privacy controls applied based on user preferences."""

    _start_at = _parse_int(start_at)
    _max_results = _parse_int(max_results)

    # Construct request model with validation
    try:
        _request = _models.FindUsersWithBrowsePermissionRequest(
            query=_models.FindUsersWithBrowsePermissionRequestQuery(start_at=_start_at, max_results=_max_results, query=query, project_key=project_key, issue_key=issue_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_browsable_users: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/user/viewissue/search"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_browsable_users")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_browsable_users", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_browsable_users",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Users
@mcp.tool()
async def list_users_default(
    start_at: str | None = Field(None, alias="startAt", description="The zero-based index position to start returning results from. Use this to paginate through large result sets."),
    max_results: str | None = Field(None, alias="maxResults", description="The maximum number of users to return per request, up to a limit of 1000. Defaults to 50 if not specified."),
) -> dict[str, Any]:
    """Retrieves a paginated list of all users in the Jira instance, including active, inactive, and previously deleted users with Atlassian accounts. Response data is filtered based on user privacy preferences."""

    _start_at = _parse_int(start_at)
    _max_results = _parse_int(max_results)

    # Construct request model with validation
    try:
        _request = _models.GetAllUsersDefaultRequest(
            query=_models.GetAllUsersDefaultRequestQuery(start_at=_start_at, max_results=_max_results)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_users_default: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/users"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_users_default")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_users_default", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_users_default",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Users
@mcp.tool()
async def list_users(
    start_at: str | None = Field(None, alias="startAt", description="The zero-based index position to start returning results from, enabling pagination through large user lists. Defaults to 0 if not specified."),
    max_results: str | None = Field(None, alias="maxResults", description="The maximum number of users to return per request, capped at 1000. Defaults to 50 if not specified."),
) -> dict[str, Any]:
    """Retrieves a paginated list of all users in the Jira instance, including active, inactive, and previously deleted users with Atlassian accounts. Response visibility is filtered based on user privacy preferences."""

    _start_at = _parse_int(start_at)
    _max_results = _parse_int(max_results)

    # Construct request model with validation
    try:
        _request = _models.GetAllUsersRequest(
            query=_models.GetAllUsersRequestQuery(start_at=_start_at, max_results=_max_results)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_users: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/users/search"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_users")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_users", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_users",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project versions
@mcp.tool()
async def create_version(
    archived: bool | None = Field(None, description="Whether the version should be marked as archived. Defaults to false if not specified."),
    description: str | None = Field(None, description="A text description of the version, up to 16,384 bytes in length."),
    driver: str | None = Field(None, description="The Atlassian account ID of the person responsible for driving this version's development."),
    move_unfixed_issues_to: str | None = Field(None, alias="moveUnfixedIssuesTo", description="The URL of the version to which unfixed issues should be moved when this version is released. Only applicable when updating a version."),
    project_id: str | None = Field(None, alias="projectId", description="The ID of the project to which this version belongs. Required when creating a version."),
    release_date: str | None = Field(None, alias="releaseDate", description="The date when the version is released, specified in ISO 8601 format (yyyy-mm-dd)."),
    released: bool | None = Field(None, description="Whether the version has been released. Once released, subsequent release requests are ignored. Only applicable when updating a version."),
    start_date: str | None = Field(None, alias="startDate", description="The date when work on the version begins, specified in ISO 8601 format (yyyy-mm-dd)."),
    name: str | None = Field(None, description="The unique name of the version. Required when creating a version. Optional when updating a version. The maximum length is 255 characters."),
) -> dict[str, Any]:
    """Creates a new project version in Jira. Requires the project ID and appropriate permissions to administer the project."""

    _project_id = _parse_int(project_id)

    # Construct request model with validation
    try:
        _request = _models.CreateVersionRequest(
            body=_models.CreateVersionRequestBody(archived=archived, description=description, driver=driver, move_unfixed_issues_to=move_unfixed_issues_to, project_id=_project_id, release_date=release_date, released=released, start_date=start_date, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_version: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/version"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_version")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_version", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_version",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project versions
@mcp.tool()
async def get_version(id_: str = Field(..., alias="id", description="The unique identifier of the version to retrieve.")) -> dict[str, Any]:
    """Retrieve details for a specific project version by its ID. This operation can be accessed anonymously and requires Browse projects permission for the project containing the version."""

    # Construct request model with validation
    try:
        _request = _models.GetVersionRequest(
            path=_models.GetVersionRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_version: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/version/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/version/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_version")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_version", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_version",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project versions
@mcp.tool()
async def update_version(
    id_: str = Field(..., alias="id", description="The unique identifier of the version to update."),
    archived: bool | None = Field(None, description="Set whether this version is archived. Archived versions are typically hidden from active workflows."),
    description: str | None = Field(None, description="A text description of the version. Maximum length is 16,384 bytes."),
    driver: str | None = Field(None, description="The Atlassian account ID of the person responsible for this version."),
    move_unfixed_issues_to: str | None = Field(None, alias="moveUnfixedIssuesTo", description="The URI of another version to automatically move all unfixed issues to when this version is released. Only applicable during updates, not creation."),
    project_id: str | None = Field(None, alias="projectId", description="The ID of the project this version belongs to. Only used during version creation; ignored when updating."),
    release_date: str | None = Field(None, alias="releaseDate", description="The date when this version is released, specified in ISO 8601 format (yyyy-mm-dd)."),
    released: bool | None = Field(None, description="Set whether this version is released. Once released, subsequent release requests are ignored."),
    start_date: str | None = Field(None, alias="startDate", description="The date when work on this version begins, specified in ISO 8601 format (yyyy-mm-dd)."),
) -> dict[str, Any]:
    """Updates an existing project version with new metadata such as release dates, status, and driver assignment. Requires Administer Jira global permission or Administer Projects permission for the target project."""

    _project_id = _parse_int(project_id)

    # Construct request model with validation
    try:
        _request = _models.UpdateVersionRequest(
            path=_models.UpdateVersionRequestPath(id_=id_),
            body=_models.UpdateVersionRequestBody(archived=archived, description=description, driver=driver, move_unfixed_issues_to=move_unfixed_issues_to, project_id=_project_id, release_date=release_date, released=released, start_date=start_date)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_version: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/version/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/version/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_version")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_version", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_version",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project versions
@mcp.tool()
async def merge_versions(
    id_: str = Field(..., alias="id", description="The ID of the version to delete. This version will be removed after all its issues are reassigned to the target version."),
    move_issues_to: str = Field(..., alias="moveIssuesTo", description="The ID of the version to merge into. All issues currently assigned to the source version will be reassigned to this version."),
) -> dict[str, Any]:
    """Merges two project versions by deleting the source version and reassigning all issues from it to the target version. Requires Administer Jira or Administer Projects permission."""

    # Construct request model with validation
    try:
        _request = _models.MergeVersionsRequest(
            path=_models.MergeVersionsRequestPath(id_=id_, move_issues_to=move_issues_to)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for merge_versions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/version/{id}/mergeto/{moveIssuesTo}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/version/{id}/mergeto/{moveIssuesTo}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("merge_versions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("merge_versions", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="merge_versions",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project versions
@mcp.tool()
async def reorder_version(
    id_: str = Field(..., alias="id", description="The unique identifier of the version to reorder."),
    after: str | None = Field(None, description="The URL (self link) of the version after which to place the moved version. Cannot be used with `position`."),
    position: Literal["Earlier", "Later", "First", "Last"] | None = Field(None, description="An absolute position in which to place the moved version. Cannot be used with `after`."),
) -> dict[str, Any]:
    """Changes the sequence position of a version within its project, affecting how versions are displayed in Jira. Requires browse permissions on the project containing the version."""

    # Construct request model with validation
    try:
        _request = _models.MoveVersionRequest(
            path=_models.MoveVersionRequestPath(id_=id_),
            body=_models.MoveVersionRequestBody(after=after, position=position)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for reorder_version: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/version/{id}/move", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/version/{id}/move"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("reorder_version")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("reorder_version", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="reorder_version",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project versions
@mcp.tool()
async def count_version_related_issues(id_: str = Field(..., alias="id", description="The unique identifier of the version for which to retrieve related issue counts.")) -> dict[str, Any]:
    """Retrieves counts of issues related to a specific version, including issues where the version is set as a fix version, affected version, or in a custom version field. Requires Browse projects permission for the project containing the version."""

    # Construct request model with validation
    try:
        _request = _models.GetVersionRelatedIssuesRequest(
            path=_models.GetVersionRelatedIssuesRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for count_version_related_issues: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/version/{id}/relatedIssueCounts", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/version/{id}/relatedIssueCounts"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("count_version_related_issues")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("count_version_related_issues", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="count_version_related_issues",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project versions
@mcp.tool()
async def list_related_work(id_: str = Field(..., alias="id", description="The unique identifier of the version for which to retrieve related work items.")) -> dict[str, Any]:
    """Retrieves all related work items associated with a specific version. Requires Browse projects permission for the project containing the version."""

    # Construct request model with validation
    try:
        _request = _models.GetRelatedWorkRequest(
            path=_models.GetRelatedWorkRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_related_work: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/version/{id}/relatedwork", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/version/{id}/relatedwork"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_related_work")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_related_work", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_related_work",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project versions
@mcp.tool()
async def create_related_work(
    id_: str = Field(..., alias="id", description="The unique identifier of the version to which the related work will be linked."),
    category: str = Field(..., description="The category classification for the related work item."),
    title: str | None = Field(None, description="The display title or name of the related work item."),
    url: str | None = Field(None, description="The web address pointing to the related work item. Required for all related work types except native release notes, which will have a null URL. Must be a valid URI format."),
) -> dict[str, Any]:
    """Creates a generic related work item linked to a specific version. The related work ID is automatically generated and does not need to be provided."""

    # Construct request model with validation
    try:
        _request = _models.CreateRelatedWorkRequest(
            path=_models.CreateRelatedWorkRequestPath(id_=id_),
            body=_models.CreateRelatedWorkRequestBody(category=category, title=title, url=url)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_related_work: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/version/{id}/relatedwork", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/version/{id}/relatedwork"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_related_work")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_related_work", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_related_work",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project versions
@mcp.tool()
async def update_related_work(
    id_: str = Field(..., alias="id", description="The unique identifier of the version containing the related work to update."),
    category: str = Field(..., description="The classification type of the related work (e.g., generic link, release note)."),
    title: str | None = Field(None, description="The display name or title for the related work."),
    url: str | None = Field(None, description="The web address pointing to the related work resource. Required for all related work types except native release notes, which use null."),
    related_work_id: str | None = Field(None, alias="relatedWorkId", description="The id of the related work. For the native release note related work item, this will be null, and Rest API does not support updating it."),
) -> dict[str, Any]:
    """Updates an existing related work item for a version. Only generic link related works can be modified through this API; archived version-related works cannot be edited."""

    # Construct request model with validation
    try:
        _request = _models.UpdateRelatedWorkRequest(
            path=_models.UpdateRelatedWorkRequestPath(id_=id_),
            body=_models.UpdateRelatedWorkRequestBody(category=category, title=title, url=url, related_work_id=related_work_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_related_work: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/version/{id}/relatedwork", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/version/{id}/relatedwork"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_related_work")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_related_work", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_related_work",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project versions
@mcp.tool()
async def delete_and_replace_version(
    id_: str = Field(..., alias="id", description="The unique identifier of the version to delete. Must be a valid version ID from the target project."),
    custom_field_replacement_list: list[_models.CustomFieldReplacement] | None = Field(None, alias="customFieldReplacementList", description="An optional array of mappings to reassign custom fields containing the deleted version. Each mapping specifies a custom field ID and the replacement version ID to use. All replacement versions must belong to the same project as the deleted version and cannot be the version being deleted."),
) -> dict[str, Any]:
    """Deletes a project version and optionally reassigns issues to alternative versions. Issues referencing the deleted version in fixVersion, affectedVersion, or version picker custom fields will be updated with the provided replacements or cleared if no alternatives are specified."""

    # Construct request model with validation
    try:
        _request = _models.DeleteAndReplaceVersionRequest(
            path=_models.DeleteAndReplaceVersionRequestPath(id_=id_),
            body=_models.DeleteAndReplaceVersionRequestBody(custom_field_replacement_list=custom_field_replacement_list)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_and_replace_version: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/version/{id}/removeAndSwap", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/version/{id}/removeAndSwap"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_and_replace_version")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_and_replace_version", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_and_replace_version",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project versions
@mcp.tool()
async def get_version_unresolved_issues(id_: str = Field(..., alias="id", description="The unique identifier of the version for which to retrieve issue counts.")) -> dict[str, Any]:
    """Retrieves the count of total and unresolved issues for a specific project version. Useful for tracking version completion status and identifying outstanding work."""

    # Construct request model with validation
    try:
        _request = _models.GetVersionUnresolvedIssuesRequest(
            path=_models.GetVersionUnresolvedIssuesRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_version_unresolved_issues: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/version/{id}/unresolvedIssueCount", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/version/{id}/unresolvedIssueCount"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_version_unresolved_issues")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_version_unresolved_issues", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_version_unresolved_issues",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project versions
@mcp.tool()
async def delete_related_work(
    version_id: str = Field(..., alias="versionId", description="The unique identifier of the version containing the related work to be deleted."),
    related_work_id: str = Field(..., alias="relatedWorkId", description="The unique identifier of the related work item to remove."),
) -> dict[str, Any]:
    """Removes a related work item from a specific version. Requires permissions to resolve and edit issues in the project containing the version."""

    # Construct request model with validation
    try:
        _request = _models.DeleteRelatedWorkRequest(
            path=_models.DeleteRelatedWorkRequestPath(version_id=version_id, related_work_id=related_work_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_related_work: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/version/{versionId}/relatedwork/{relatedWorkId}", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/version/{versionId}/relatedwork/{relatedWorkId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_related_work")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_related_work", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_related_work",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Workflows
@mcp.tool()
async def list_workflow_history(workflow_id: str | None = Field(None, alias="workflowId", description="The unique identifier of the workflow whose history you want to retrieve.")) -> dict[str, Any]:
    """Retrieves workflow history entries for a specified workflow, showing past changes and events. Note that historical data is only available for the last 60 days and entries before October 30th, 2025 are not accessible."""

    # Construct request model with validation
    try:
        _request = _models.ListWorkflowHistoryRequest(
            body=_models.ListWorkflowHistoryRequestBody(workflow_id=workflow_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_workflow_history: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/workflow/history/list"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_workflow_history")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_workflow_history", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_workflow_history",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Workflows
@mcp.tool()
async def list_workflow_issue_type_usages(
    workflow_id: str = Field(..., alias="workflowId", description="The unique identifier of the workflow to query for issue type usage."),
    project_id: str = Field(..., alias="projectId", description="The unique identifier of the project in which to find issue type usages."),
    max_results: str | None = Field(None, alias="maxResults", description="The maximum number of issue types to return per page. Must be between 1 and 200, defaults to 50 if not specified."),
) -> dict[str, Any]:
    """Retrieve the issue types within a project that are currently using a specified workflow. Returns paginated results of issue type assignments."""

    _project_id = _parse_int(project_id)
    _max_results = _parse_int(max_results)

    # Construct request model with validation
    try:
        _request = _models.GetWorkflowProjectIssueTypeUsagesRequest(
            path=_models.GetWorkflowProjectIssueTypeUsagesRequestPath(workflow_id=workflow_id, project_id=_project_id),
            query=_models.GetWorkflowProjectIssueTypeUsagesRequestQuery(max_results=_max_results)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_workflow_issue_type_usages: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/workflow/{workflowId}/project/{projectId}/issueTypeUsages", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/workflow/{workflowId}/project/{projectId}/issueTypeUsages"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_workflow_issue_type_usages")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_workflow_issue_type_usages", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_workflow_issue_type_usages",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Workflows
@mcp.tool()
async def list_workflow_projects(
    workflow_id: str = Field(..., alias="workflowId", description="The unique identifier of the workflow to query for project usage."),
    max_results: str | None = Field(None, alias="maxResults", description="The maximum number of projects to return per page, between 1 and 200. Defaults to 50 if not specified."),
) -> dict[str, Any]:
    """Retrieve a paginated list of projects that use a specified workflow. Useful for understanding workflow adoption and impact across your Jira instance."""

    _max_results = _parse_int(max_results)

    # Construct request model with validation
    try:
        _request = _models.GetProjectUsagesForWorkflowRequest(
            path=_models.GetProjectUsagesForWorkflowRequestPath(workflow_id=workflow_id),
            query=_models.GetProjectUsagesForWorkflowRequestQuery(max_results=_max_results)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_workflow_projects: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/workflow/{workflowId}/projectUsages", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/workflow/{workflowId}/projectUsages"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_workflow_projects")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_workflow_projects", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_workflow_projects",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Workflows
@mcp.tool()
async def list_workflow_capabilities(
    workflow_id: str | None = Field(None, alias="workflowId", description="The unique identifier of the workflow. Use this to retrieve capabilities for a specific workflow by ID."),
    project_id: str | None = Field(None, alias="projectId", description="The unique identifier of the project. Use this with issueTypeId as an alternative to workflowId to identify the workflow by project context."),
    issue_type_id: str | None = Field(None, alias="issueTypeId", description="The unique identifier of the issue type. Use this with projectId as an alternative to workflowId to identify the workflow by issue type context."),
) -> dict[str, Any]:
    """Retrieve available workflow capabilities including rules, scope, and project types. Requires either a workflow ID or a project and issue type ID pair to identify the target workflow."""

    # Construct request model with validation
    try:
        _request = _models.WorkflowCapabilitiesRequest(
            query=_models.WorkflowCapabilitiesRequestQuery(workflow_id=workflow_id, project_id=project_id, issue_type_id=issue_type_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_workflow_capabilities: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/workflows/capabilities"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_workflow_capabilities")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_workflow_capabilities", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_workflow_capabilities",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Workflows
@mcp.tool()
async def get_workflow_default_editor() -> dict[str, Any]:
    """Retrieve the user's default workflow editor preference, which can be either the new editor or the legacy editor."""

    # Extract parameters for API call
    _http_path = "/rest/api/3/workflows/defaultEditor"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_workflow_default_editor")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_workflow_default_editor", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_workflow_default_editor",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Workflows
@mcp.tool()
async def preview_workflows(
    project_id: str = Field(..., alias="projectId", description="The project ID for permission validation and workflow association. Required to identify the project context and enforce access controls."),
    issue_type_ids: list[str] | None = Field(None, alias="issueTypeIds", description="List of issue type IDs to filter workflows. Specify up to 25 issue type IDs; at least one lookup criterion (issueTypeIds, workflowNames, or workflowIds) is required.", min_length=0, max_length=25),
) -> dict[str, Any]:
    """Retrieve a read-only preview of workflows for a specified project. Returns workflow configuration details filtered by issue types, project permissions, and lookup criteria."""

    # Construct request model with validation
    try:
        _request = _models.ReadWorkflowPreviewsRequest(
            body=_models.ReadWorkflowPreviewsRequestBody(issue_type_ids=issue_type_ids, project_id=project_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for preview_workflows: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/workflows/preview"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("preview_workflows")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("preview_workflows", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="preview_workflows",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Workflow scheme project associations
@mcp.tool()
async def list_workflow_schemes_by_projects(project_id: Annotated[list[int], AfterValidator(_check_unique_items)] = Field(..., alias="projectId", description="One or more project IDs to retrieve associated workflow schemes for. Provide between 1 and 100 project IDs; non-existent or team-managed projects are ignored without error.", min_length=1, max_length=100)) -> dict[str, Any]:
    """Retrieves the workflow schemes associated with specified projects, showing which projects are linked to each scheme. Team-managed and non-existent projects are silently ignored. The Default Workflow Scheme is returned without an ID."""

    # Construct request model with validation
    try:
        _request = _models.GetWorkflowSchemeProjectAssociationsRequest(
            query=_models.GetWorkflowSchemeProjectAssociationsRequestQuery(project_id=project_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_workflow_schemes_by_projects: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/workflowscheme/project"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_workflow_schemes_by_projects")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_workflow_schemes_by_projects", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_workflow_schemes_by_projects",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Workflow schemes
@mcp.tool()
async def list_workflow_scheme_projects(
    workflow_scheme_id: str = Field(..., alias="workflowSchemeId", description="The unique identifier of the workflow scheme for which to retrieve associated projects."),
    max_results: str | None = Field(None, alias="maxResults", description="The maximum number of projects to return per page, between 1 and 200. Defaults to 50 if not specified."),
) -> dict[str, Any]:
    """Retrieve a paginated list of projects that are currently using a specified workflow scheme."""

    _max_results = _parse_int(max_results)

    # Construct request model with validation
    try:
        _request = _models.GetProjectUsagesForWorkflowSchemeRequest(
            path=_models.GetProjectUsagesForWorkflowSchemeRequestPath(workflow_scheme_id=workflow_scheme_id),
            query=_models.GetProjectUsagesForWorkflowSchemeRequestQuery(max_results=_max_results)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_workflow_scheme_projects: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rest/api/3/workflowscheme/{workflowSchemeId}/projectUsages", _request.path.model_dump(by_alias=True)) if _request.path else "/rest/api/3/workflowscheme/{workflowSchemeId}/projectUsages"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_workflow_scheme_projects")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_workflow_scheme_projects", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_workflow_scheme_projects",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue worklogs
@mcp.tool()
async def list_deleted_worklogs(since: str | None = Field(None, description="The UNIX timestamp in milliseconds marking the start of the deletion window. Only worklogs deleted after this timestamp are returned. Defaults to 0 (epoch start) if not specified.")) -> dict[str, Any]:
    """Retrieve a paginated list of worklog IDs and deletion timestamps for worklogs deleted after a specified date and time. Results are ordered from oldest to youngest, with up to 1000 worklogs per page."""

    _since = _parse_int(since)

    # Construct request model with validation
    try:
        _request = _models.GetIdsOfWorklogsDeletedSinceRequest(
            query=_models.GetIdsOfWorklogsDeletedSinceRequestQuery(since=_since)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_deleted_worklogs: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/worklog/deleted"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_deleted_worklogs")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_deleted_worklogs", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_deleted_worklogs",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue worklogs
@mcp.tool()
async def get_worklogs(ids: Annotated[list[int], AfterValidator(_check_unique_items)] = Field(..., description="A list of worklog IDs to retrieve. Only worklogs that are viewable by all users or where you have project role or group permissions will be returned, up to a maximum of 1000 items.")) -> dict[str, Any]:
    """Retrieve detailed worklog information for a specified list of worklog IDs. Returns up to 1000 worklogs where you have permission to view them."""

    # Construct request model with validation
    try:
        _request = _models.GetWorklogsForIdsRequest(
            body=_models.GetWorklogsForIdsRequestBody(ids=ids)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_worklogs: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/worklog/list"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_worklogs")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_worklogs", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_worklogs",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Issue worklogs
@mcp.tool()
async def list_worklogs_modified_since(since: str | None = Field(None, description="The UNIX timestamp in milliseconds marking the start of the time range. Only worklogs updated after this timestamp are returned. Defaults to 0 (epoch start) if not specified. Note: worklogs updated during the minute immediately preceding the request are excluded.")) -> dict[str, Any]:
    """Retrieve a paginated list of worklog IDs and their update timestamps for all worklogs modified after a specified date and time. Results are ordered from oldest to youngest, with a maximum of 1000 worklogs per page."""

    _since = _parse_int(since)

    # Construct request model with validation
    try:
        _request = _models.GetIdsOfWorklogsModifiedSinceRequest(
            query=_models.GetIdsOfWorklogsModifiedSinceRequestQuery(since=_since)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_worklogs_modified_since: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rest/api/3/worklog/updated"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_worklogs_modified_since")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_worklogs_modified_since", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_worklogs_modified_since",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# ============================================================================
# Schema Optimization
# ============================================================================

def _optimize_tool_schemas() -> None:
    """Simplify anyOf nullable wrappers in tool schemas for LLM token efficiency.

    Pydantic generates {"anyOf": [{"type": "T"}, {"type": "null"}], "default": null}
    for `T | None = None` params. Both Anthropic and OpenAI recommend the simpler
    {"type": "T"} with the param outside `required` for optimal tool-calling accuracy
    and minimal token overhead. Runtime validation is unaffected — Python signatures
    retain the `T | None` annotation.
    """
    from fastmcp.tools import Tool as _ToolCls
    # v3: _local_provider._components, v2: _tool_manager._tools
    _src = getattr(mcp, "_local_provider", None)
    if _src is not None:
        _tools = [v for v in _src._components.values() if isinstance(v, _ToolCls)]
    else:
        _tools = list(mcp._tool_manager._tools.values())  # type: ignore[attr-defined]
    for _tool in _tools:
        _simplify_schema(_tool.parameters)

def _simplify_schema(schema: dict) -> None:
    """Walk a JSON Schema dict and collapse anyOf-nullable patterns in place.

    Also removes discriminator objects anywhere in the tree: after FastMCP's
    DereferenceRefsMiddleware inlines $ref entries, discriminator.mapping values
    point to $defs that no longer exist. The discriminator is redundant — each
    variant already identifies itself via Literal constants on the discriminant
    field, so MCP clients and LLMs don't need the mapping.
    """
    schema.pop("discriminator", None)
    for _def_schema in schema.get("$defs", {}).values():
        _simplify_schema(_def_schema)
    _props = schema.get("properties", {})
    _required = set(schema.get("required", []))
    for _name, _prop in _props.items():
        if "anyOf" in _prop:
            _non_null = [b for b in _prop["anyOf"] if b.get("type") != "null"]
            if len(_non_null) == 1:
                _desc = _prop.get("description")
                _prop.clear()
                _prop.update(_non_null[0])
                if _desc:
                    _prop["description"] = _desc
                _required.discard(_name)
        _simplify_schema(_prop)
    if _required:
        schema["required"] = sorted(_required)
    elif "required" in schema:
        del schema["required"]
    for _key in ("anyOf", "oneOf"):
        for _branch in schema.get(_key, []):
            if isinstance(_branch, dict):
                _simplify_schema(_branch)

_optimize_tool_schemas()

# ============================================================================
# Environment Validation
# ============================================================================

def validate_environment() -> None:
    """Validate required environment variables at startup."""
    errors: list[str] = []
    warnings: list[str] = []

    required_vars: list[tuple[str, str, str | None]] = [
    ]

    for var_name, description, default in required_vars:
        value = os.getenv(var_name, default)
        if not value:
            errors.append(f"  - {var_name}: {description}")

    if errors:
        print("=" * 70, file=sys.stderr)
        print("ERROR: Missing required environment variables", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        for error in errors:
            print(error, file=sys.stderr)
        print("\nServer startup aborted. Set required variables and restart.", file=sys.stderr)
        print("\nExample:", file=sys.stderr)
        print("  python atlassian_jira_server.py", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        sys.exit(1)

    _validate_port()
    _validate_timeout()
    _validate_rate_limit()

    logger = logging.getLogger(__name__)
    logger.info("Environment validation passed")
    for warning in warnings:
        logger.warning(warning)

def _validate_port() -> None:
    port_str = os.getenv('PORT')
    if not port_str:
        return  # Optional, has CLI default

    port: int
    try:
        port = int(port_str)
    except ValueError:
        print("=" * 70, file=sys.stderr)
        print("ERROR: Invalid PORT value", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        print(f"  Got: {port_str}", file=sys.stderr)
        print("\nPORT must be an integer between 1 and 65535", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        sys.exit(1)

    if port < 1 or port > 65535:
        print("=" * 70, file=sys.stderr)
        print("ERROR: PORT out of valid range", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        print(f"  Got: {port}", file=sys.stderr)
        print("\nPORT must be between 1 and 65535", file=sys.stderr)
        print("  Common ports: 8000, 8080, 3000", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        sys.exit(1)

def _validate_timeout() -> None:
    timeout_str = os.getenv('API_TIMEOUT')
    if not timeout_str:
        return  # Optional, has default

    timeout: int
    try:
        timeout = int(timeout_str)
    except ValueError:
        print("=" * 70, file=sys.stderr)
        print("ERROR: Invalid API_TIMEOUT value", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        print(f"  Got: {timeout_str}", file=sys.stderr)
        print("\nAPI_TIMEOUT must be a positive integer (seconds)", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        sys.exit(1)

    if timeout < 1 or timeout > 3600:
        print("=" * 70, file=sys.stderr)
        print("ERROR: API_TIMEOUT out of reasonable range", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        print(f"  Got: {timeout} seconds", file=sys.stderr)
        print("\nAPI_TIMEOUT must be between 1 and 3600 seconds (1 hour max)", file=sys.stderr)
        print("  Recommended: 30 (most APIs), 60 (slower APIs), 300 (long operations)", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        sys.exit(1)

def _validate_rate_limit() -> None:
    rate_str = os.getenv('RATE_LIMIT')
    if not rate_str:
        return  # Optional, has default

    try:
        rate = float(rate_str)
    except ValueError:
        print("=" * 70, file=sys.stderr)
        print("ERROR: Invalid RATE_LIMIT value", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        print(f"  Got: {rate_str}", file=sys.stderr)
        print("\nRATE_LIMIT must be a positive number (requests per second)", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        sys.exit(1)

    if rate <= 0:
        print("=" * 70, file=sys.stderr)
        print("ERROR: RATE_LIMIT must be positive", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        print(f"  Got: {rate}", file=sys.stderr)
        print("\nRATE_LIMIT must be greater than 0", file=sys.stderr)
        print("  Recommended: 1-100 requests/second depending on API limits", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        sys.exit(1)

# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """CLI entry point with runtime transport selection."""

    validate_environment()

    parser = argparse.ArgumentParser(description="Atlassian Jira MCP Server")

    parser.add_argument(
        '--transport',
        choices=['stdio', 'sse', 'streamable-http'],
        default='stdio',
        help='Transport protocol: stdio (default, for Claude Code), sse (remote capable), streamable-http (production)'
    )
    parser.add_argument(
        '--host',
        default='0.0.0.0',  # noqa: S104
        help='Host address for HTTP transports (default: 0.0.0.0)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='Port for HTTP transports (default: 8000)'
    )
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default=LOG_LEVEL,
        help='Logging level (default: from LOG_LEVEL env var, or INFO)'
    )
    parser.add_argument(
        '--retry',
        action='store_true',
        help='Enable automatic retry with exponential backoff (default: enabled)'
    )
    parser.add_argument(
        '--no-retry',
        action='store_true',
        help='Disable automatic retry'
    )
    parser.add_argument(
        '--max-retries',
        type=int,
        default=MAX_RETRIES,
        help='Maximum retry attempts (default: from MAX_RETRIES env var, or 3)'
    )
    parser.add_argument(
        '--retry-base-delay',
        type=int,
        default=RETRY_BACKOFF_FACTOR,
        help='Base delay for exponential backoff in seconds (default: from RETRY_BACKOFF_FACTOR env var, or 2)'
    )
    parser.add_argument(
        '--retry-max-delay',
        type=int,
        default=60,
        help='Maximum retry delay in seconds (default: 60)'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=None,
        help='API request timeout in seconds (default: 30, or API_TIMEOUT env var)'
    )
    parser.add_argument(
        '--rate-limiting',
        choices=['disabled', 'local'],
        default='local',
        help='Rate limiting mode: disabled (default) or local (in-memory token bucket)'
    )
    parser.add_argument(
        '--rate-limit',
        type=int,
        default=RATE_LIMIT_REQUESTS_PER_SECOND,
        help='Rate limit in requests per second (default: from RATE_LIMIT_REQUESTS_PER_SECOND env var, or 10)'
    )
    parser.add_argument(
        '--burst',
        type=int,
        help='Burst capacity for rate limiter (default: 2x rate-limit)'
    )
    parser.add_argument(
        '--circuit-breaker',
        action='store_true',
        help='Enable circuit breaker to prevent cascading failures'
    )
    parser.add_argument(
        '--circuit-breaker-failure-threshold',
        type=int,
        default=CIRCUIT_BREAKER_FAILURE_THRESHOLD,
        help='Failures before opening circuit (default: from CIRCUIT_BREAKER_FAILURE_THRESHOLD env var, or 5)'
    )
    parser.add_argument(
        '--circuit-breaker-timeout',
        type=float,
        default=CIRCUIT_BREAKER_TIMEOUT_SECONDS,
        help='Seconds before recovery attempt (default: from CIRCUIT_BREAKER_TIMEOUT_SECONDS env var, or 60.0)'
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    logger = logging.getLogger(__name__)
    logger.info("Starting Atlassian Jira MCP Server")
    logger.info(f"Transport: {args.transport}")

    global retry_config, rate_limiter, circuit_breaker, DEFAULT_TIMEOUT

    if args.timeout is not None:
        DEFAULT_TIMEOUT = args.timeout
    else:
        timeout_env = os.getenv('API_TIMEOUT')
        if timeout_env:
            try:
                DEFAULT_TIMEOUT = int(timeout_env)
            except ValueError:
                logger.warning(f"Invalid API_TIMEOUT '{timeout_env}', using default {DEFAULT_TIMEOUT}s")
    logger.info(f"Timeout: {DEFAULT_TIMEOUT}s")

    if not args.no_retry:
        retry_config = RetryConfig(
            max_attempts=args.max_retries,
            base_delay=args.retry_base_delay,
            max_delay=args.retry_max_delay
        )
        logger.info(
            f"Retry: Enabled (max attempts: {retry_config.max_attempts}, "
            f"base delay: {retry_config.base_delay}s, max delay: {retry_config.max_delay}s)"
        )
    else:
        logger.info("Retry: Disabled")

    rate_limiting_mode = args.rate_limiting

    if rate_limiting_mode == 'disabled':
        rate_limiter = None
        logger.info("Rate limiting: Disabled")
    elif rate_limiting_mode == 'local':
        rate_limit = args.rate_limit if args.rate_limit else 10.0
        burst = args.burst if args.burst else int(rate_limit * 2)
        rate_limiter = TokenBucket(rate=rate_limit, capacity=burst)
        logger.info(f"Rate limiting: Local (rate: {rate_limit} req/sec, burst: {burst})")
    else:
        logger.warning(f"Unknown rate limiting mode: {rate_limiting_mode}, disabling")
        rate_limiter = None

    if args.circuit_breaker:
        cb_config = CircuitBreakerConfig(
            failure_threshold=args.circuit_breaker_failure_threshold,
            timeout=args.circuit_breaker_timeout
        )
        circuit_breaker = CircuitBreaker(cb_config)
        logger.info(
            f"Circuit breaker: Enabled (failure threshold: {cb_config.failure_threshold}, "
            f"timeout: {cb_config.timeout}s)"
        )
    else:
        logger.info("Circuit breaker: Disabled")
    try:
        if args.transport == 'stdio':
            logger.info("Using stdio transport")
            mcp.run()
        elif args.transport == 'sse':
            logger.info(f"Using SSE transport on http://{args.host}:{args.port}")
            mcp.run(transport='sse', host=args.host, port=args.port)
        elif args.transport == 'streamable-http':
            logger.info(f"Using Streamable HTTP transport on http://{args.host}:{args.port}")
            mcp.run(transport='streamable-http', host=args.host, port=args.port)

    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()

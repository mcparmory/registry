#!/usr/bin/env python3
"""
LaunchDarkly REST API MCP Server

API Info:
- API License: Apache 2.0 (https://www.apache.org/licenses/LICENSE-2.0)
- Contact: LaunchDarkly Technical Support Team <support@launchdarkly.com> (https://support.launchdarkly.com)

Generated: 2026-04-09 17:25:42 UTC
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
from typing import Any, Literal, overload

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
from pydantic import Field

BASE_URL = os.getenv("BASE_URL", "https://app.launchdarkly.com")
SERVER_NAME = "LaunchDarkly REST API"
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
    'ApiKey',
]

# Initialize authentication handlers at server startup
_auth_handlers: dict[str, Any] = {}
try:
    _auth_handlers["ApiKey"] = _auth.APIKeyAuth(env_var="API_KEY", location="header", param_name="Authorization")
    logging.info("Authentication configured: ApiKey")
except ValueError as e:
    # Extract credential names from error message (first sentence before "Leave empty")
    error_msg = str(e).split("Leave empty")[0].strip()
    logging.warning(f"Credentials for ApiKey not configured: {error_msg}")
    _auth_handlers["ApiKey"] = None

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

mcp = FastMCP("LaunchDarkly REST API", middleware=[_JsonCoercionMiddleware()])

# Tags: Relay Proxy configurations
@mcp.tool()
async def list_relay_proxy_configs() -> dict[str, Any]:
    """Retrieve all Relay Proxy configurations currently configured in your account. Use this to view existing proxy setups and their settings."""

    # Extract parameters for API call
    _http_path = "/api/v2/account/relay-auto-configs"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_relay_proxy_configs")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_relay_proxy_configs", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_relay_proxy_configs",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Relay Proxy configurations
@mcp.tool()
async def create_relay_proxy_config(
    name: str = Field(..., description="A human-readable name for this Relay Proxy configuration. Used to identify and manage the configuration."),
    policy: list[_models.Statement] = Field(..., description="An inline policy array that defines which environments and projects this Relay Proxy should include or exclude. Policy items are evaluated in order to determine scope. Refer to the inline policy documentation for syntax and structure."),
) -> dict[str, Any]:
    """Create a new Relay Proxy configuration that controls which environments and projects the Relay Proxy should include or exclude."""

    # Construct request model with validation
    try:
        _request = _models.PostRelayAutoConfigRequest(
            body=_models.PostRelayAutoConfigRequestBody(name=name, policy=policy)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_relay_proxy_config: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v2/account/relay-auto-configs"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_relay_proxy_config")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_relay_proxy_config", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_relay_proxy_config",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Relay Proxy configurations
@mcp.tool()
async def get_relay_proxy_config(id_: str = Field(..., alias="id", description="The unique identifier of the relay auto config to retrieve.")) -> dict[str, Any]:
    """Retrieve a single Relay Proxy auto configuration by its unique identifier. Use this to fetch detailed settings for a specific relay proxy configuration."""

    # Construct request model with validation
    try:
        _request = _models.GetRelayProxyConfigRequest(
            path=_models.GetRelayProxyConfigRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_relay_proxy_config: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/account/relay-auto-configs/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/account/relay-auto-configs/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_relay_proxy_config")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_relay_proxy_config", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_relay_proxy_config",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Relay Proxy configurations
@mcp.tool()
async def update_relay_auto_config(
    id_: str = Field(..., alias="id", description="The unique identifier of the Relay Proxy configuration to update."),
    patch: list[_models.PatchOperation] = Field(..., description="An array of JSON patch operations (RFC 6902) or JSON merge patch operations (RFC 7386) describing the changes to apply to the configuration."),
) -> dict[str, Any]:
    """Update a Relay Proxy configuration using JSON patch or JSON merge patch operations. Changes are applied incrementally to the specified configuration."""

    # Construct request model with validation
    try:
        _request = _models.PatchRelayAutoConfigRequest(
            path=_models.PatchRelayAutoConfigRequestPath(id_=id_),
            body=_models.PatchRelayAutoConfigRequestBody(patch=patch)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_relay_auto_config: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/account/relay-auto-configs/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/account/relay-auto-configs/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_relay_auto_config")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_relay_auto_config", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_relay_auto_config",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Relay Proxy configurations
@mcp.tool()
async def delete_relay_auto_config(id_: str = Field(..., alias="id", description="The unique identifier of the relay auto config to delete. This is a string value that uniquely identifies the configuration within your account.")) -> dict[str, Any]:
    """Delete a Relay Proxy auto-configuration by its unique identifier. This operation permanently removes the specified relay auto config from your account."""

    # Construct request model with validation
    try:
        _request = _models.DeleteRelayAutoConfigRequest(
            path=_models.DeleteRelayAutoConfigRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_relay_auto_config: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/account/relay-auto-configs/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/account/relay-auto-configs/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_relay_auto_config")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_relay_auto_config", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_relay_auto_config",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Relay Proxy configurations
@mcp.tool()
async def reset_relay_auto_config(
    id_: str = Field(..., alias="id", description="The unique identifier of the Relay Proxy configuration to reset."),
    expiry: str | None = Field(None, description="Optional Unix epoch time in milliseconds when the old configuration key should expire. If not provided, the old key expires immediately upon reset."),
) -> dict[str, Any]:
    """Generate a new secret key for a Relay Proxy configuration, optionally setting an expiration time for the previous key before it becomes invalid."""

    _expiry = _parse_int(expiry)

    # Construct request model with validation
    try:
        _request = _models.ResetRelayAutoConfigRequest(
            path=_models.ResetRelayAutoConfigRequestPath(id_=id_),
            query=_models.ResetRelayAutoConfigRequestQuery(expiry=_expiry)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for reset_relay_auto_config: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/account/relay-auto-configs/{id}/reset", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/account/relay-auto-configs/{id}/reset"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("reset_relay_auto_config")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("reset_relay_auto_config", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="reset_relay_auto_config",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Applications (beta)
@mcp.tool()
async def list_applications() -> dict[str, Any]:
    """Retrieve a list of all applications. Optionally expand the response to include additional details such as flags evaluated by each application."""

    # Extract parameters for API call
    _http_path = "/api/v2/applications"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_applications")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_applications", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_applications",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Applications (beta)
@mcp.tool()
async def get_application(application_key: str = Field(..., alias="applicationKey", description="The unique identifier for the application. This is a string value that uniquely identifies the application within your LaunchDarkly workspace.")) -> dict[str, Any]:
    """Retrieve a LaunchDarkly application by its unique application key. Optionally expand the response to include evaluated flags and other application details."""

    # Construct request model with validation
    try:
        _request = _models.GetApplicationRequest(
            path=_models.GetApplicationRequestPath(application_key=application_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_application: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/applications/{applicationKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/applications/{applicationKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_application")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_application", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_application",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Applications (beta)
@mcp.tool()
async def update_application(
    application_key: str = Field(..., alias="applicationKey", description="The unique identifier for the application to update."),
    body: list[_models.PatchOperation] = Field(..., description="An array of JSON Patch operations describing the changes to apply. Each operation must include 'op' (the operation type), 'path' (the field to modify), and 'value' (the new value for replace operations). Supported paths include '/description' and '/kind'."),
) -> dict[str, Any]:
    """Update an application's description and kind fields using JSON Patch format. Specify changes as an array of patch operations following RFC 6902 standard."""

    # Construct request model with validation
    try:
        _request = _models.PatchApplicationRequest(
            path=_models.PatchApplicationRequestPath(application_key=application_key),
            body=_models.PatchApplicationRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_application: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/applications/{applicationKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/applications/{applicationKey}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_application")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_application", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_application",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Applications (beta)
@mcp.tool()
async def delete_application(application_key: str = Field(..., alias="applicationKey", description="The unique identifier for the application to delete. This is a string value that uniquely identifies the application within the system.")) -> dict[str, Any]:
    """Permanently delete an application by its unique key. This action cannot be undone and will remove all associated data."""

    # Construct request model with validation
    try:
        _request = _models.DeleteApplicationRequest(
            path=_models.DeleteApplicationRequestPath(application_key=application_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_application: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/applications/{applicationKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/applications/{applicationKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_application")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_application", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_application",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Applications (beta)
@mcp.tool()
async def list_application_versions(application_key: str = Field(..., alias="applicationKey", description="The unique identifier for the application. This string key is used to look up and retrieve all versions belonging to that specific application.")) -> dict[str, Any]:
    """Retrieve all versions for a specific application identified by its application key. Returns a list of version records associated with the application in the account."""

    # Construct request model with validation
    try:
        _request = _models.GetApplicationVersionsRequest(
            path=_models.GetApplicationVersionsRequestPath(application_key=application_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_application_versions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/applications/{applicationKey}/versions", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/applications/{applicationKey}/versions"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_application_versions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_application_versions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_application_versions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Applications (beta)
@mcp.tool()
async def update_application_version(
    application_key: str = Field(..., alias="applicationKey", description="The unique identifier for the application being modified."),
    version_key: str = Field(..., alias="versionKey", description="The unique identifier for the specific application version to update."),
    body: list[_models.PatchOperation] = Field(..., description="A JSON Patch array describing the changes to apply. Each operation must specify an `op` (operation type like 'replace'), `path` (the field to modify), and `value` (the new value). Multiple operations can be included in a single request."),
) -> dict[str, Any]:
    """Update an application version using JSON Patch operations. Currently supports updating the `supported` field to enable or disable the version."""

    # Construct request model with validation
    try:
        _request = _models.PatchApplicationVersionRequest(
            path=_models.PatchApplicationVersionRequestPath(application_key=application_key, version_key=version_key),
            body=_models.PatchApplicationVersionRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_application_version: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/applications/{applicationKey}/versions/{versionKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/applications/{applicationKey}/versions/{versionKey}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_application_version")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_application_version", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_application_version",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Applications (beta)
@mcp.tool()
async def delete_application_version(
    application_key: str = Field(..., alias="applicationKey", description="The unique identifier for the application containing the version to delete."),
    version_key: str = Field(..., alias="versionKey", description="The unique identifier for the specific application version to delete."),
) -> dict[str, Any]:
    """Permanently delete a specific version of an application. This operation removes the version and all associated data."""

    # Construct request model with validation
    try:
        _request = _models.DeleteApplicationVersionRequest(
            path=_models.DeleteApplicationVersionRequestPath(application_key=application_key, version_key=version_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_application_version: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/applications/{applicationKey}/versions/{versionKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/applications/{applicationKey}/versions/{versionKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_application_version")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_application_version", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_application_version",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Approvals
@mcp.tool()
async def list_approval_requests() -> dict[str, Any]:
    """Retrieve all approval requests with support for filtering by assignee, requestor, resource, status, and review status. Optionally expand the response to include related flag, project, and environment details."""

    # Extract parameters for API call
    _http_path = "/api/v2/approval-requests"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_approval_requests")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_approval_requests", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_approval_requests",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Approvals
@mcp.tool()
async def create_approval_request(
    resource_id: str = Field(..., alias="resourceId", description="The resource identifier in the format proj/projKey:env/envKey:flag/flagKey (or equivalent for AI Configs and segments). Specifies which resource the approval request applies to."),
    description: str = Field(..., description="A brief summary of the requested changes. This helps reviewers understand the intent of the approval request."),
    instructions: list[_models.Instruction] = Field(..., description="An ordered list of semantic patch instructions to apply when the approval is granted. Instructions vary by resource type: use addVariation, removeVariation, updateVariation, or updateDefaultVariation for flags; refer to AI Config or segment patch documentation for other resource types."),
    integration_config: dict[str, Any] | None = Field(None, alias="integrationConfig", description="Optional object containing additional fields for third-party approval system integrations. Field requirements are defined in the manifest.json of the specific integration being used."),
) -> dict[str, Any]:
    """Create an approval request for changes to a feature flag, AI Config, or segment. The request includes semantic patch instructions that will be applied upon approval."""

    # Construct request model with validation
    try:
        _request = _models.PostApprovalRequest(
            body=_models.PostApprovalRequestBody(resource_id=resource_id, description=description, instructions=instructions, integration_config=integration_config)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_approval_request: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v2/approval-requests"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_approval_request")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_approval_request", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_approval_request",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Approvals
@mcp.tool()
async def get_approval_request(id_: str = Field(..., alias="id", description="The unique identifier of the approval request to retrieve.")) -> dict[str, Any]:
    """Retrieve a specific approval request by its ID. Optionally expand the response to include related resources such as environments, flags, projects, or resource details."""

    # Construct request model with validation
    try:
        _request = _models.GetApprovalRequest(
            path=_models.GetApprovalRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_approval_request: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/approval-requests/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/approval-requests/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_approval_request")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_approval_request", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_approval_request",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Approvals (beta)
@mcp.tool()
async def update_approval_request(
    id_: str = Field(..., alias="id", description="The unique identifier of the approval request to update."),
    instructions: list[_models.Instruction] = Field(..., description="An array of semantic patch instructions to apply. Each instruction specifies an operation (addReviewers or updateDescription) with its required parameters. At least one instruction must be provided."),
) -> dict[str, Any]:
    """Update an approval request using semantic patch instructions. Supports adding reviewers or updating the request description through a structured instruction format."""

    # Construct request model with validation
    try:
        _request = _models.PatchApprovalRequest(
            path=_models.PatchApprovalRequestPath(id_=id_),
            body=_models.PatchApprovalRequestBody(instructions=instructions)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_approval_request: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/approval-requests/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/approval-requests/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_approval_request")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_approval_request", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_approval_request",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Approvals
@mcp.tool()
async def delete_approval_request(id_: str = Field(..., alias="id", description="The unique identifier of the approval request to delete.")) -> dict[str, Any]:
    """Permanently delete an approval request by its ID. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteApprovalRequest(
            path=_models.DeleteApprovalRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_approval_request: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/approval-requests/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/approval-requests/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_approval_request")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_approval_request", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_approval_request",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Approvals
@mcp.tool()
async def apply_approval_request(id_: str = Field(..., alias="id", description="The unique identifier of the approval request to apply. This is a string value that identifies which approval request should be executed.")) -> dict[str, Any]:
    """Execute an approval request that has been approved. This operation finalizes the approval workflow for any approval request type."""

    # Construct request model with validation
    try:
        _request = _models.PostApprovalRequestApplyRequest(
            path=_models.PostApprovalRequestApplyRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for apply_approval_request: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/approval-requests/{id}/apply", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/approval-requests/{id}/apply"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("apply_approval_request")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("apply_approval_request", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="apply_approval_request",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Approvals
@mcp.tool()
async def submit_approval_request_review(
    id_: str = Field(..., alias="id", description="The unique identifier of the approval request being reviewed."),
    kind: Literal["approve", "comment", "decline"] | None = Field(None, description="The type of review action to perform: 'approve' to accept the changes, 'decline' to reject them, or 'comment' to provide feedback without making a final decision."),
) -> dict[str, Any]:
    """Submit a review decision on an approval request by approving, declining, or adding a comment to the proposed changes."""

    # Construct request model with validation
    try:
        _request = _models.PostApprovalRequestReviewRequest(
            path=_models.PostApprovalRequestReviewRequestPath(id_=id_),
            body=_models.PostApprovalRequestReviewRequestBody(kind=kind)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for submit_approval_request_review: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/approval-requests/{id}/reviews", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/approval-requests/{id}/reviews"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("submit_approval_request_review")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("submit_approval_request_review", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="submit_approval_request_review",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Audit log
@mcp.tool()
async def list_audit_log_entries(
    q: str | None = Field(None, description="Full or partial resource name to search for in audit logs. Supports text-based matching across resource identifiers."),
    spec: str | None = Field(None, description="Resource specifier to filter results by specific resources or resource collections. Use LaunchDarkly resource specifier syntax to target particular resource types or instances."),
) -> dict[str, Any]:
    """Retrieve audit log entries with optional filtering by date ranges, resource specifiers, or full-text search. Use resource specifier syntax to target specific resources or collections."""

    # Construct request model with validation
    try:
        _request = _models.GetAuditLogEntriesRequest(
            query=_models.GetAuditLogEntriesRequestQuery(q=q, spec=spec)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_audit_log_entries: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v2/auditlog"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_audit_log_entries")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_audit_log_entries", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_audit_log_entries",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Audit log
@mcp.tool()
async def search_audit_log_entries(
    q: str | None = Field(None, description="Full-text search query to filter audit log entries by resource name or partial matches. Searches across resource names and related metadata."),
    body: list[_models.StatementPost] | None = Field(None, description="Array of resource specifiers to restrict results to specific resources or resource collections. Use LaunchDarkly resource specifier syntax to target particular entities (e.g., projects, environments, flags). Order is not significant."),
) -> dict[str, Any]:
    """Search audit log entries by full-text query and resource specifiers. Filter results by date ranges and resource types using query parameters and request body constraints."""

    # Construct request model with validation
    try:
        _request = _models.PostAuditLogEntriesRequest(
            query=_models.PostAuditLogEntriesRequestQuery(q=q),
            body=_models.PostAuditLogEntriesRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_audit_log_entries: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v2/auditlog"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_audit_log_entries")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_audit_log_entries", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_audit_log_entries",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Audit log
@mcp.tool()
async def get_audit_log_entry(id_: str = Field(..., alias="id", description="The unique identifier of the audit log entry to retrieve.")) -> dict[str, Any]:
    """Retrieve a detailed audit log entry with full change history. Returns comprehensive metadata including the previous and current versions of the modified entity, plus the JSON patch or semantic patch that was applied."""

    # Construct request model with validation
    try:
        _request = _models.GetAuditLogEntryRequest(
            path=_models.GetAuditLogEntryRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_audit_log_entry: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/auditlog/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/auditlog/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_audit_log_entry")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_audit_log_entry", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_audit_log_entry",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Other
@mcp.tool()
async def get_caller_identity() -> dict[str, Any]:
    """Retrieve information about the identity used to authenticate the current API request, including details about the session cookie, API token, SDK keys, or other credentials."""

    # Extract parameters for API call
    _http_path = "/api/v2/caller-identity"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_caller_identity")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_caller_identity", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_caller_identity",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Code references
@mcp.tool()
async def list_extinctions(
    repo_name: str | None = Field(None, alias="repoName", description="Filter results to extinctions in a specific repository by name."),
    branch_name: str | None = Field(None, alias="branchName", description="Filter results to extinctions in a specific branch. If not specified, only the default branch is queried."),
    proj_key: str | None = Field(None, alias="projKey", description="Filter results to extinctions in a specific project by project key."),
    from_: str | None = Field(None, alias="from", description="Filter results to extinctions after a specific point in time, expressed as a Unix epoch timestamp in milliseconds. Must be used together with the `to` parameter."),
    to: str | None = Field(None, description="Filter results to extinctions before a specific point in time, expressed as a Unix epoch timestamp in milliseconds. Must be used together with the `from` parameter."),
) -> dict[str, Any]:
    """Retrieve a list of all extinction events, which are created when all code references to a flag are removed. Filter results by repository, branch, project, or commit time window to find specific extinctions."""

    _from_ = _parse_int(from_)
    _to = _parse_int(to)

    # Construct request model with validation
    try:
        _request = _models.GetExtinctionsRequest(
            query=_models.GetExtinctionsRequestQuery(repo_name=repo_name, branch_name=branch_name, proj_key=proj_key, from_=_from_, to=_to)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_extinctions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v2/code-refs/extinctions"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_extinctions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_extinctions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_extinctions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Code references
@mcp.tool()
async def list_repositories(
    with_branches: str | None = Field(None, alias="withBranches", description="Include branch metadata in the response. Set to any value to enable this option."),
    with_references_for_default_branch: str | None = Field(None, alias="withReferencesForDefaultBranch", description="Include branch metadata and code references for the default git branch in the response. Set to any value to enable this option."),
    proj_key: str | None = Field(None, alias="projKey", description="Filter code reference results to a specific LaunchDarkly project by providing its project key."),
) -> dict[str, Any]:
    """Retrieve a list of connected repositories with optional branch metadata and code references. Filter results by project key to scope code references to a specific LaunchDarkly project."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesRequest(
            query=_models.GetRepositoriesRequestQuery(with_branches=with_branches, with_references_for_default_branch=with_references_for_default_branch, proj_key=proj_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_repositories: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v2/code-refs/repositories"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_repositories")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_repositories", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_repositories",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Code references
@mcp.tool()
async def create_repository(
    name: str = Field(..., description="The name of the repository (e.g., 'LaunchDarkly-Docs'). Used as the unique identifier for this repository."),
    source_link: str | None = Field(None, alias="sourceLink", description="A URL where the repository can be accessed (e.g., a GitHub repository URL). Provides a direct link to the repository source."),
    commit_url_template: str | None = Field(None, alias="commitUrlTemplate", description="A URL template for constructing links to specific commits. Use the placeholder ${sha} to represent the commit hash (e.g., 'https://github.com/launchdarkly/LaunchDarkly-Docs/commit/${sha}')."),
    hunk_url_template: str | None = Field(None, alias="hunkUrlTemplate", description="A URL template for constructing links to specific code hunks or lines. Use placeholders ${sha} for commit hash, ${filePath} for file path, and ${lineNumber} for line number (e.g., 'https://github.com/launchdarkly/LaunchDarkly-Docs/blob/${sha}/${filePath}#L${lineNumber}')."),
    default_branch: str | None = Field(None, alias="defaultBranch", description="The repository's default branch name. Defaults to 'main' if not specified (e.g., 'main', 'master', or 'develop')."),
) -> dict[str, Any]:
    """Create a new code repository for tracking feature flag references. Optionally provide URLs for accessing the repository and constructing links to specific commits and code hunks."""

    # Construct request model with validation
    try:
        _request = _models.PostRepositoryRequest(
            body=_models.PostRepositoryRequestBody(name=name, source_link=source_link, commit_url_template=commit_url_template, hunk_url_template=hunk_url_template, default_branch=default_branch)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_repository: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v2/code-refs/repositories"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_repository")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_repository", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_repository",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Code references
@mcp.tool()
async def get_repository(repo: str = Field(..., description="The name of the repository to retrieve. This is a string identifier that uniquely identifies the repository within the system.")) -> dict[str, Any]:
    """Retrieve a single repository by its name. Use this to fetch detailed information about a specific code repository tracked in the system."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoryRequest(
            path=_models.GetRepositoryRequestPath(repo=repo)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_repository: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/code-refs/repositories/{repo}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/code-refs/repositories/{repo}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_repository")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_repository", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_repository",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Code references
@mcp.tool()
async def update_repository(
    repo: str = Field(..., description="The name of the repository to update. This identifier is used to locate the specific repository in the system."),
    body: list[_models.PatchOperation] = Field(..., description="An array of patch operations describing the changes to apply. Each operation should specify an action (op), a JSON pointer path (path), and the new value (value) where applicable. Operations are processed in the order provided."),
) -> dict[str, Any]:
    """Update a repository's settings using JSON patch or JSON merge patch operations. Changes are applied according to RFC 6902 or RFC 7386 standards."""

    # Construct request model with validation
    try:
        _request = _models.PatchRepositoryRequest(
            path=_models.PatchRepositoryRequestPath(repo=repo),
            body=_models.PatchRepositoryRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_repository: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/code-refs/repositories/{repo}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/code-refs/repositories/{repo}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_repository")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_repository", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_repository",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Code references
@mcp.tool()
async def delete_repository(repo: str = Field(..., description="The name of the repository to delete. Must be a valid string identifier.")) -> dict[str, Any]:
    """Permanently delete a repository and all associated code references. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteRepositoryRequest(
            path=_models.DeleteRepositoryRequestPath(repo=repo)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_repository: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/code-refs/repositories/{repo}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/code-refs/repositories/{repo}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_repository")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_repository", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_repository",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Code references
@mcp.tool()
async def delete_branches(
    repo: str = Field(..., description="The name of the repository from which branches will be deleted."),
    body: list[str] = Field(..., description="An array of branch names to delete. Each item should be a string representing a branch name. Order is not significant."),
) -> dict[str, Any]:
    """Asynchronously delete multiple branches from a repository. Returns a task that processes the branch deletions in the background."""

    # Construct request model with validation
    try:
        _request = _models.DeleteBranchesRequest(
            path=_models.DeleteBranchesRequestPath(repo=repo),
            body=_models.DeleteBranchesRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_branches: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/code-refs/repositories/{repo}/branch-delete-tasks", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/code-refs/repositories/{repo}/branch-delete-tasks"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_branches")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_branches", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_branches",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Code references
@mcp.tool()
async def list_branches(repo: str = Field(..., description="The name of the repository to list branches from. This is a required identifier that specifies which repository's branches to retrieve.")) -> dict[str, Any]:
    """Retrieve a list of all branches in the specified repository. Use this to discover available branches for code references and analysis."""

    # Construct request model with validation
    try:
        _request = _models.GetBranchesRequest(
            path=_models.GetBranchesRequestPath(repo=repo)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_branches: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/code-refs/repositories/{repo}/branches", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/code-refs/repositories/{repo}/branches"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_branches")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_branches", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_branches",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Code references
@mcp.tool()
async def get_branch(
    repo: str = Field(..., description="The name of the repository containing the branch."),
    branch: str = Field(..., description="The name of the branch to retrieve, URL-encoded to handle special characters in branch names."),
    proj_key: str | None = Field(None, alias="projKey", description="Optional project key to scope the branch lookup to a specific project within the repository."),
) -> dict[str, Any]:
    """Retrieve detailed information about a specific branch within a repository, optionally filtered to a particular project."""

    # Construct request model with validation
    try:
        _request = _models.GetBranchRequest(
            path=_models.GetBranchRequestPath(repo=repo, branch=branch),
            query=_models.GetBranchRequestQuery(proj_key=proj_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_branch: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/code-refs/repositories/{repo}/branches/{branch}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/code-refs/repositories/{repo}/branches/{branch}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_branch")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_branch", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_branch",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Code references
@mcp.tool()
async def upsert_branch(
    repo: str = Field(..., description="The name of the repository where the branch exists or will be created."),
    branch: str = Field(..., description="The branch name as it appears in the URL, URL-encoded if it contains special characters."),
    name: str = Field(..., description="The human-readable branch name (e.g., 'main', 'develop'). This is the actual branch identifier."),
    head: str = Field(..., description="A commit identifier representing the current HEAD of the branch, typically a commit SHA hash."),
    sync_time: str = Field(..., alias="syncTime", description="A Unix timestamp (in milliseconds or seconds as int64) indicating when this branch was last synchronized with the source."),
    references: list[_models.ReferenceRep] | None = Field(None, description="An optional array of flag references discovered on this branch. Order and format depend on the flag reference structure used by the system."),
) -> dict[str, Any]:
    """Create a new branch or update an existing branch in a repository. Use this to sync branch metadata including the current HEAD commit and last sync timestamp."""

    _sync_time = _parse_int(sync_time)

    # Construct request model with validation
    try:
        _request = _models.PutBranchRequest(
            path=_models.PutBranchRequestPath(repo=repo, branch=branch),
            body=_models.PutBranchRequestBody(name=name, head=head, sync_time=_sync_time, references=references)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for upsert_branch: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/code-refs/repositories/{repo}/branches/{branch}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/code-refs/repositories/{repo}/branches/{branch}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("upsert_branch")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("upsert_branch", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="upsert_branch",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Code references
@mcp.tool()
async def create_extinction_event(
    repo: str = Field(..., description="The repository name where the extinction event will be created."),
    branch: str = Field(..., description="The branch name, URL-encoded, where the extinction event applies."),
    body: list[_models.Extinction] = Field(..., description="Array of extinction event objects defining the code references and metadata for the extinction event."),
) -> dict[str, Any]:
    """Create a new extinction event for a specific branch in a repository. Extinction events track code reference removals or deprecations."""

    # Construct request model with validation
    try:
        _request = _models.PostExtinctionRequest(
            path=_models.PostExtinctionRequestPath(repo=repo, branch=branch),
            body=_models.PostExtinctionRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_extinction_event: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/code-refs/repositories/{repo}/branches/{branch}/extinction-events", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/code-refs/repositories/{repo}/branches/{branch}/extinction-events"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_extinction_event")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_extinction_event", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_extinction_event",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Code references
@mcp.tool()
async def list_code_reference_statistics() -> dict[str, Any]:
    """Retrieve code reference statistics and repository links for all projects that have code references configured."""

    # Extract parameters for API call
    _http_path = "/api/v2/code-refs/statistics"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_code_reference_statistics")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_code_reference_statistics", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_code_reference_statistics",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Code references
@mcp.tool()
async def get_code_references_statistics(project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project. Used to scope the statistics query to a specific project.")) -> dict[str, Any]:
    """Retrieve code reference statistics for flags in a project, showing the number of references to flag keys across repositories in the default branch. Optionally filter results to a single flag using the flagKey query parameter."""

    # Construct request model with validation
    try:
        _request = _models.GetStatisticsRequest(
            path=_models.GetStatisticsRequestPath(project_key=project_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_code_references_statistics: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/code-refs/statistics/{projectKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/code-refs/statistics/{projectKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_code_references_statistics")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_code_references_statistics", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_code_references_statistics",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Data Export destinations
@mcp.tool()
async def list_destinations() -> dict[str, Any]:
    """Retrieve all Data Export destinations configured across your projects and environments. This provides a comprehensive view of where your data is being exported."""

    # Extract parameters for API call
    _http_path = "/api/v2/destinations"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_destinations")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_destinations", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_destinations",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Data Export destinations
@mcp.tool()
async def generate_warehouse_destination_key_pair(
    proj_key: str = Field(..., alias="projKey", description="The unique identifier for the project containing the destination configuration."),
    env_key: str = Field(..., alias="envKey", description="The unique identifier for the environment within the project where the warehouse destination is configured."),
) -> dict[str, Any]:
    """Generate a public-private key pair for authenticating Data Export operations to a Snowflake warehouse destination. This enables secure credential-based access without storing passwords."""

    # Construct request model with validation
    try:
        _request = _models.PostGenerateProjectEnvWarehouseDestinationKeyPairRequest(
            path=_models.PostGenerateProjectEnvWarehouseDestinationKeyPairRequestPath(proj_key=proj_key, env_key=env_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for generate_warehouse_destination_key_pair: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/destinations/projects/{projKey}/environments/{envKey}/generate-warehouse-destination-key-pair", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/destinations/projects/{projKey}/environments/{envKey}/generate-warehouse-destination-key-pair"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("generate_warehouse_destination_key_pair")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("generate_warehouse_destination_key_pair", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="generate_warehouse_destination_key_pair",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Data Export destinations
@mcp.tool()
async def create_data_export_destination(
    project_key: str = Field(..., alias="projectKey", description="The project key that uniquely identifies the LaunchDarkly project where the destination will be created."),
    environment_key: str = Field(..., alias="environmentKey", description="The environment key that uniquely identifies the environment within the project where the destination will be created."),
    name: str | None = Field(None, description="A human-readable name for the Data Export destination. This name appears in the LaunchDarkly UI for easy identification."),
    kind: Literal["google-pubsub", "kinesis", "mparticle", "segment", "azure-event-hubs", "snowflake-v2", "databricks", "bigquery", "redshift"] | None = Field(None, description="The type of Data Export destination. Choose from: google-pubsub, kinesis, mparticle, segment, azure-event-hubs, snowflake-v2, databricks, bigquery, or redshift. Each type requires specific configuration fields."),
    config: Any | None = Field(None, description="An object containing the configuration parameters required for your chosen destination type. Required fields vary: Azure Event Hubs needs namespace, name, policyName, and policyKey; Google Pub/Sub needs project and topic; Kinesis needs region, roleArn, and streamName; mParticle needs apiKey, secret, userIdentity, and anonymousUserIdentity; Segment needs writeKey; Snowflake needs publicKey and snowflakeHostAddress."),
    on: bool | None = Field(None, description="Whether the Data Export destination is active and exporting events. When true, events are streamed to the destination; when false, the destination is paused. Displayed as the integration status in the LaunchDarkly UI."),
) -> dict[str, Any]:
    """Create a new Data Export destination to stream LaunchDarkly events to external platforms. Configuration requirements vary by destination type (e.g., Azure Event Hubs, Google Pub/Sub, Kinesis, mParticle, Segment, Snowflake, Databricks, BigQuery, or Redshift)."""

    # Construct request model with validation
    try:
        _request = _models.PostDestinationRequest(
            path=_models.PostDestinationRequestPath(project_key=project_key, environment_key=environment_key),
            body=_models.PostDestinationRequestBody(name=name, kind=kind, config=config, on=on)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_data_export_destination: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/destinations/{projectKey}/{environmentKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/destinations/{projectKey}/{environmentKey}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_data_export_destination")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_data_export_destination", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_data_export_destination",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Data Export destinations
@mcp.tool()
async def get_destination(
    project_key: str = Field(..., alias="projectKey", description="The project key that identifies which project contains the destination."),
    environment_key: str = Field(..., alias="environmentKey", description="The environment key that identifies which environment within the project contains the destination."),
    id_: str = Field(..., alias="id", description="The unique identifier of the Data Export destination to retrieve."),
) -> dict[str, Any]:
    """Retrieve a single Data Export destination by its ID within a specific project and environment."""

    # Construct request model with validation
    try:
        _request = _models.GetDestinationRequest(
            path=_models.GetDestinationRequestPath(project_key=project_key, environment_key=environment_key, id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_destination: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/destinations/{projectKey}/{environmentKey}/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/destinations/{projectKey}/{environmentKey}/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_destination")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_destination", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_destination",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Data Export destinations
@mcp.tool()
async def update_destination(
    project_key: str = Field(..., alias="projectKey", description="The project key that contains the destination."),
    environment_key: str = Field(..., alias="environmentKey", description="The environment key where the destination is configured."),
    id_: str = Field(..., alias="id", description="The unique identifier of the Data Export destination to update."),
    body: list[_models.PatchOperation] = Field(..., description="An array of patch operations following RFC 6902 (JSON Patch) or RFC 7386 (JSON Merge Patch) format. Each operation specifies an action (op), target path (path), and new value (value) for the destination configuration."),
) -> dict[str, Any]:
    """Update a Data Export destination using JSON patch or JSON merge patch operations. Specify the changes you want to apply to the destination configuration."""

    # Construct request model with validation
    try:
        _request = _models.PatchDestinationRequest(
            path=_models.PatchDestinationRequestPath(project_key=project_key, environment_key=environment_key, id_=id_),
            body=_models.PatchDestinationRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_destination: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/destinations/{projectKey}/{environmentKey}/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/destinations/{projectKey}/{environmentKey}/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_destination")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_destination", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_destination",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Data Export destinations
@mcp.tool()
async def delete_destination(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the destination to delete."),
    environment_key: str = Field(..., alias="environmentKey", description="The unique identifier for the environment within the project where the destination exists."),
    id_: str = Field(..., alias="id", description="The unique identifier of the Data Export destination to delete."),
) -> dict[str, Any]:
    """Permanently delete a Data Export destination from a specific project and environment. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteDestinationRequest(
            path=_models.DeleteDestinationRequestPath(project_key=project_key, environment_key=environment_key, id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_destination: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/destinations/{projectKey}/{environmentKey}/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/destinations/{projectKey}/{environmentKey}/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_destination")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_destination", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_destination",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Feature flags
@mcp.tool()
async def get_feature_flag_status_across_environments(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the feature flag. This is a required string key that identifies which project's flags to query."),
    feature_flag_key: str = Field(..., alias="featureFlagKey", description="The unique identifier for the specific feature flag whose status you want to retrieve. This is a required string key that identifies the flag within the project."),
    env: str | None = Field(None, description="Optional filter to retrieve flag status for a specific environment only. If omitted, the response includes status across all environments in the project."),
) -> dict[str, Any]:
    """Retrieve the current status and configuration of a feature flag across all environments or a specific environment. Use this to check whether a flag is enabled, its targeting rules, and rollout percentages in your deployment pipeline."""

    # Construct request model with validation
    try:
        _request = _models.GetFeatureFlagStatusAcrossEnvironmentsRequest(
            path=_models.GetFeatureFlagStatusAcrossEnvironmentsRequestPath(project_key=project_key, feature_flag_key=feature_flag_key),
            query=_models.GetFeatureFlagStatusAcrossEnvironmentsRequestQuery(env=env)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_feature_flag_status_across_environments: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/flag-status/{projectKey}/{featureFlagKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/flag-status/{projectKey}/{featureFlagKey}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_feature_flag_status_across_environments")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_feature_flag_status_across_environments", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_feature_flag_status_across_environments",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Feature flags
@mcp.tool()
async def list_feature_flag_statuses(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the feature flags."),
    environment_key: str = Field(..., alias="environmentKey", description="The unique identifier for the environment within the project."),
) -> dict[str, Any]:
    """Retrieve the status of all feature flags in a specific project and environment, including their current state (new, active, inactive, or launched) and last request timestamp."""

    # Construct request model with validation
    try:
        _request = _models.GetFeatureFlagStatusesRequest(
            path=_models.GetFeatureFlagStatusesRequestPath(project_key=project_key, environment_key=environment_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_feature_flag_statuses: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/flag-statuses/{projectKey}/{environmentKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/flag-statuses/{projectKey}/{environmentKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_feature_flag_statuses")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_feature_flag_statuses", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_feature_flag_statuses",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Feature flags
@mcp.tool()
async def get_feature_flag_status(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the feature flag."),
    environment_key: str = Field(..., alias="environmentKey", description="The unique identifier for the environment in which to check the feature flag status."),
    feature_flag_key: str = Field(..., alias="featureFlagKey", description="The unique identifier for the feature flag whose status you want to retrieve."),
) -> dict[str, Any]:
    """Retrieve the current status of a specific feature flag within a given project and environment. This includes whether the flag is enabled or disabled and any associated targeting rules."""

    # Construct request model with validation
    try:
        _request = _models.GetFeatureFlagStatusRequest(
            path=_models.GetFeatureFlagStatusRequestPath(project_key=project_key, environment_key=environment_key, feature_flag_key=feature_flag_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_feature_flag_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/flag-statuses/{projectKey}/{environmentKey}/{featureFlagKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/flag-statuses/{projectKey}/{environmentKey}/{featureFlagKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_feature_flag_status")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_feature_flag_status", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_feature_flag_status",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Feature flags
@mcp.tool()
async def list_feature_flags(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the feature flags."),
    env: str | None = Field(None, description="Filter flag configurations to a specific environment (e.g., 'production', 'staging'). Required when using environment-specific filters like `evaluated` or `targetingModifiedDate` sorting."),
    summary: bool | None = Field(None, description="Set to `0` to include detailed flag configuration including prerequisites, targets, and rules for each environment. By default, these details are excluded for performance."),
) -> dict[str, Any]:
    """Retrieve all feature flags in a project with optional filtering by environment, tags, and other criteria. Supports pagination, sorting, and field expansion to optimize response payload and performance."""

    # Construct request model with validation
    try:
        _request = _models.GetFeatureFlagsRequest(
            path=_models.GetFeatureFlagsRequestPath(project_key=project_key),
            query=_models.GetFeatureFlagsRequestQuery(env=env, summary=summary)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_feature_flags: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/flags/{projectKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/flags/{projectKey}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_feature_flags")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_feature_flags", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_feature_flags",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Feature flags
@mcp.tool()
async def create_feature_flag(
    project_key: str = Field(..., alias="projectKey", description="The project key that uniquely identifies the project where the feature flag will be created."),
    name: str = Field(..., description="A human-readable name for the feature flag to display in the UI."),
    key: str = Field(..., description="A unique identifier for the flag used in your application code. Must be distinct within the project."),
    using_environment_id: bool = Field(..., alias="usingEnvironmentId", description="Enable or disable availability for client-side SDKs. Defaults to false."),
    using_mobile_key: bool = Field(..., alias="usingMobileKey", description="Enable or disable availability for mobile SDKs. Defaults to true."),
    on_variation: int = Field(..., alias="onVariation", description="The index of the variation to serve when targeting is enabled. Must correspond to a valid variation index."),
    off_variation: int = Field(..., alias="offVariation", description="The index of the variation to serve when targeting is disabled. Must correspond to a valid variation index."),
    clone: str | None = Field(None, description="Optional key of an existing feature flag to clone. Cloning copies the full targeting configuration across all environments, including on/off state, to the new flag."),
    variations: list[_models.Variation] | None = Field(None, description="Array of possible flag variations with unique values. If omitted, defaults to two boolean variations: true and false. Order matters as variations are referenced by index."),
    temporary: bool | None = Field(None, description="Mark the flag as temporary (intended for short-term use). Defaults to true."),
    tags: list[str] | None = Field(None, description="Array of tags to organize and categorize the feature flag. Defaults to an empty array."),
    custom_properties: dict[str, _models.CustomProperty] | None = Field(None, alias="customProperties", description="Custom metadata as key-value pairs where each key maps to a name and array of values. Typically used for integration-related data."),
    purpose: Literal["migration", "holdout"] | None = Field(None, description="The intended purpose of the flag. Use 'migration' for migration flags (which auto-generate variations based on stage count) or 'holdout' for holdout flags."),
    initial_prerequisites: list[_models.FlagPrerequisitePost] | None = Field(None, alias="initialPrerequisites", description="Array of prerequisite flags that must be satisfied before this flag is evaluated in all environments."),
    is_flag_on: bool | None = Field(None, alias="isFlagOn", description="Automatically enable the flag across all environments upon creation. Defaults to false."),
) -> dict[str, Any]:
    """Create a feature flag in a project with customizable variations, targeting defaults, and optional migration settings. Supports cloning existing flags and configuring SDK availability."""

    # Construct request model with validation
    try:
        _request = _models.PostFeatureFlagRequest(
            path=_models.PostFeatureFlagRequestPath(project_key=project_key),
            query=_models.PostFeatureFlagRequestQuery(clone=clone),
            body=_models.PostFeatureFlagRequestBody(name=name, key=key, variations=variations, temporary=temporary, tags=tags, custom_properties=custom_properties, purpose=purpose, initial_prerequisites=initial_prerequisites, is_flag_on=is_flag_on,
                client_side_availability=_models.PostFeatureFlagRequestBodyClientSideAvailability(using_environment_id=using_environment_id, using_mobile_key=using_mobile_key),
                defaults=_models.PostFeatureFlagRequestBodyDefaults(on_variation=on_variation, off_variation=off_variation))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_feature_flag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/flags/{projectKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/flags/{projectKey}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_feature_flag")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_feature_flag", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_feature_flag",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Feature flags
@mcp.tool()
async def get_feature_flag(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the feature flag."),
    feature_flag_key: str = Field(..., alias="featureFlagKey", description="The unique identifier for the feature flag to retrieve."),
    env: str | None = Field(None, description="Optional environment filter to restrict returned configurations to a specific environment (e.g., 'production'). Omit to retrieve all environments."),
) -> dict[str, Any]:
    """Retrieve a single feature flag by its key, with configurations for all environments by default. Use the `env` parameter to filter results to specific environments for faster responses and smaller payloads."""

    # Construct request model with validation
    try:
        _request = _models.GetFeatureFlagRequest(
            path=_models.GetFeatureFlagRequestPath(project_key=project_key, feature_flag_key=feature_flag_key),
            query=_models.GetFeatureFlagRequestQuery(env=env)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_feature_flag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/flags/{projectKey}/{featureFlagKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/flags/{projectKey}/{featureFlagKey}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_feature_flag")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_feature_flag", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_feature_flag",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Feature flags
@mcp.tool()
async def update_feature_flag(
    project_key: str = Field(..., alias="projectKey", description="The project key that identifies the LaunchDarkly project containing the feature flag."),
    feature_flag_key: str = Field(..., alias="featureFlagKey", description="The feature flag key used to identify the flag in your application code."),
    patch: list[_models.PatchOperation] = Field(..., description="Array of patch operations describing the changes to apply. Use semantic patch format (with Content-Type header domain-model=launchdarkly.semanticpatch), JSON patch (RFC 6902), or JSON merge patch (RFC 7386) format. Order of operations is significant."),
    ignore_conflicts: bool | None = Field(None, alias="ignoreConflicts", description="If true, applies the patch even if it conflicts with pending scheduled changes or approval requests. Use to override validation checks."),
    dry_run: bool | None = Field(None, alias="dryRun", description="If true, validates the patch and returns a preview of the flag after changes without persisting them. Useful for testing changes before applying."),
) -> dict[str, Any]:
    """Perform a partial update to a feature flag using semantic patch, JSON patch, or JSON merge patch. Supports targeting rules, variations, prerequisites, flag settings, and lifecycle management across environments."""

    # Construct request model with validation
    try:
        _request = _models.PatchFeatureFlagRequest(
            path=_models.PatchFeatureFlagRequestPath(project_key=project_key, feature_flag_key=feature_flag_key),
            query=_models.PatchFeatureFlagRequestQuery(ignore_conflicts=ignore_conflicts, dry_run=dry_run),
            body=_models.PatchFeatureFlagRequestBody(patch=patch)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_feature_flag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/flags/{projectKey}/{featureFlagKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/flags/{projectKey}/{featureFlagKey}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_feature_flag")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_feature_flag", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_feature_flag",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Feature flags
@mcp.tool()
async def delete_feature_flag(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the feature flag."),
    feature_flag_key: str = Field(..., alias="featureFlagKey", description="The unique key that identifies the feature flag in your codebase. This is the identifier you reference when evaluating the flag in your application."),
) -> dict[str, Any]:
    """Permanently delete a feature flag across all environments. This operation cannot be undone, so only use it for flags your application no longer references in code."""

    # Construct request model with validation
    try:
        _request = _models.DeleteFeatureFlagRequest(
            path=_models.DeleteFeatureFlagRequestPath(project_key=project_key, feature_flag_key=feature_flag_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_feature_flag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/flags/{projectKey}/{featureFlagKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/flags/{projectKey}/{featureFlagKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_feature_flag")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_feature_flag", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_feature_flag",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Feature flags
@mcp.tool()
async def copy_feature_flag_between_environments(
    project_key: str = Field(..., alias="projectKey", description="The project key that identifies which project contains the feature flag."),
    feature_flag_key: str = Field(..., alias="featureFlagKey", description="The feature flag key that uniquely identifies the flag within the project."),
    source_key: str = Field(..., alias="sourceKey", description="The environment key of the source environment to copy flag settings from."),
    target_key: str = Field(..., alias="targetKey", description="The environment key of the target environment to copy flag settings to."),
    current_version: int | None = Field(None, alias="currentVersion", description="Optional flag version number. When provided, the copy operation only succeeds if the target environment's current flag version matches this value, enabling optimistic locking to prevent concurrent modification conflicts."),
    included_actions: list[Literal["updateOn", "updateRules", "updateFallthrough", "updateOffVariation", "updatePrerequisites", "updateTargets", "updateFlagConfigMigrationSettings"]] | None = Field(None, alias="includedActions", description="Optional list of specific flag changes to copy (e.g., 'updateOn'). Use this to copy only selected changes rather than the entire flag configuration. Cannot be combined with excludedActions; if neither is provided, all flag changes are copied."),
) -> dict[str, Any]:
    """Copy feature flag configuration from a source environment to a target environment. This Enterprise-only operation supports selective copying of flag changes and optimistic locking via version matching."""

    # Construct request model with validation
    try:
        _request = _models.CopyFeatureFlagRequest(
            path=_models.CopyFeatureFlagRequestPath(project_key=project_key, feature_flag_key=feature_flag_key),
            body=_models.CopyFeatureFlagRequestBody(included_actions=included_actions,
                source=_models.CopyFeatureFlagRequestBodySource(key=source_key),
                target=_models.CopyFeatureFlagRequestBodyTarget(key=target_key, current_version=current_version))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for copy_feature_flag_between_environments: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/flags/{projectKey}/{featureFlagKey}/copy", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/flags/{projectKey}/{featureFlagKey}/copy"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("copy_feature_flag_between_environments")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("copy_feature_flag_between_environments", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="copy_feature_flag_between_environments",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Feature flags
@mcp.tool()
async def list_expiring_context_targets(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the feature flag."),
    environment_key: str = Field(..., alias="environmentKey", description="The unique identifier for the environment where the feature flag is configured."),
    feature_flag_key: str = Field(..., alias="featureFlagKey", description="The unique identifier for the feature flag whose expiring context targets should be retrieved."),
) -> dict[str, Any]:
    """Retrieve a list of context targets scheduled for removal from a feature flag. This helps identify and manage temporary targeting rules that are approaching their expiration date."""

    # Construct request model with validation
    try:
        _request = _models.GetExpiringContextTargetsRequest(
            path=_models.GetExpiringContextTargetsRequestPath(project_key=project_key, environment_key=environment_key, feature_flag_key=feature_flag_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_expiring_context_targets: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/flags/{projectKey}/{featureFlagKey}/expiring-targets/{environmentKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/flags/{projectKey}/{featureFlagKey}/expiring-targets/{environmentKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_expiring_context_targets")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_expiring_context_targets", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_expiring_context_targets",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Feature flags
@mcp.tool()
async def update_expiring_context_targets(
    project_key: str = Field(..., alias="projectKey", description="The project key that contains the feature flag. A string identifier for the LaunchDarkly project."),
    environment_key: str = Field(..., alias="environmentKey", description="The environment key where the feature flag targeting applies. A string identifier for the specific environment."),
    feature_flag_key: str = Field(..., alias="featureFlagKey", description="The feature flag key to update expiring targets for. A string identifier for the feature flag."),
    instructions: list[_models.Instruction] = Field(..., description="An array of semantic patch instructions to execute. Each instruction must specify a `kind` (addExpiringTarget, updateExpiringTarget, or removeExpiringTarget), the target context via `contextKey` and `contextKind`, the `variationId` to target, and for add/update operations, a `value` representing the Unix millisecond timestamp for removal. Instructions are processed in order."),
) -> dict[str, Any]:
    """Schedule, update, or remove the date when a context will be automatically removed from individual targeting on a feature flag. Use semantic patch instructions to add expiration dates, modify existing ones, or cancel scheduled removals."""

    # Construct request model with validation
    try:
        _request = _models.PatchExpiringTargetsRequest(
            path=_models.PatchExpiringTargetsRequestPath(project_key=project_key, environment_key=environment_key, feature_flag_key=feature_flag_key),
            body=_models.PatchExpiringTargetsRequestBody(instructions=instructions)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_expiring_context_targets: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/flags/{projectKey}/{featureFlagKey}/expiring-targets/{environmentKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/flags/{projectKey}/{featureFlagKey}/expiring-targets/{environmentKey}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_expiring_context_targets")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_expiring_context_targets", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_expiring_context_targets",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Feature flags
@mcp.tool()
async def list_expiring_user_targets_for_feature_flag(
    project_key: str = Field(..., alias="projectKey", description="The project key that identifies the LaunchDarkly project containing the feature flag."),
    environment_key: str = Field(..., alias="environmentKey", description="The environment key that specifies which environment's feature flag targeting data to retrieve."),
    feature_flag_key: str = Field(..., alias="featureFlagKey", description="The feature flag key that identifies which flag's expiring user targets to list."),
) -> dict[str, Any]:
    """Retrieve a list of user targets scheduled for removal from a feature flag in a specific environment. Note: This endpoint is deprecated; use list_expiring_context_targets_for_feature_flag instead after upgrading to context-based SDKs."""

    # Construct request model with validation
    try:
        _request = _models.GetExpiringUserTargetsRequest(
            path=_models.GetExpiringUserTargetsRequestPath(project_key=project_key, environment_key=environment_key, feature_flag_key=feature_flag_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_expiring_user_targets_for_feature_flag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/flags/{projectKey}/{featureFlagKey}/expiring-user-targets/{environmentKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/flags/{projectKey}/{featureFlagKey}/expiring-user-targets/{environmentKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_expiring_user_targets_for_feature_flag")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_expiring_user_targets_for_feature_flag", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_expiring_user_targets_for_feature_flag",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Feature flags
@mcp.tool()
async def schedule_user_target_removal_on_flag(
    project_key: str = Field(..., alias="projectKey", description="The project key that contains the feature flag."),
    environment_key: str = Field(..., alias="environmentKey", description="The environment key where the feature flag is configured."),
    feature_flag_key: str = Field(..., alias="featureFlagKey", description="The feature flag key to update expiring user targets for."),
    instructions: list[_models.Instruction] = Field(..., description="Array of semantic patch instructions to add, update, or remove user target removal dates. Each instruction must specify a kind (addExpireUserTargetDate, updateExpireUserTargetDate, or removeExpireUserTargetDate), the userKey to target, and the variationId. For add and update operations, include value as a Unix timestamp in milliseconds. The update operation supports an optional version parameter to ensure consistency."),
) -> dict[str, Any]:
    """Schedule, update, or remove a removal date for a user from a feature flag's individual targeting. Use semantic patch instructions to manage when LaunchDarkly will stop serving a specific variation to targeted users."""

    # Construct request model with validation
    try:
        _request = _models.PatchExpiringUserTargetsRequest(
            path=_models.PatchExpiringUserTargetsRequestPath(project_key=project_key, environment_key=environment_key, feature_flag_key=feature_flag_key),
            body=_models.PatchExpiringUserTargetsRequestBody(instructions=instructions)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for schedule_user_target_removal_on_flag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/flags/{projectKey}/{featureFlagKey}/expiring-user-targets/{environmentKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/flags/{projectKey}/{featureFlagKey}/expiring-user-targets/{environmentKey}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("schedule_user_target_removal_on_flag")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("schedule_user_target_removal_on_flag", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="schedule_user_target_removal_on_flag",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Flag triggers
@mcp.tool()
async def list_flag_triggers(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the feature flag."),
    environment_key: str = Field(..., alias="environmentKey", description="The unique identifier for the environment where the flag triggers are configured."),
    feature_flag_key: str = Field(..., alias="featureFlagKey", description="The unique identifier for the feature flag whose triggers you want to retrieve."),
) -> dict[str, Any]:
    """Retrieve all triggers configured for a feature flag in a specific environment. Triggers define automated workflows that respond to flag changes."""

    # Construct request model with validation
    try:
        _request = _models.GetTriggerWorkflowsRequest(
            path=_models.GetTriggerWorkflowsRequestPath(project_key=project_key, environment_key=environment_key, feature_flag_key=feature_flag_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_flag_triggers: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/flags/{projectKey}/{featureFlagKey}/triggers/{environmentKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/flags/{projectKey}/{featureFlagKey}/triggers/{environmentKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_flag_triggers")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_flag_triggers", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_flag_triggers",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Flag triggers
@mcp.tool()
async def create_flag_trigger(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier of the project containing the feature flag."),
    environment_key: str = Field(..., alias="environmentKey", description="The unique identifier of the environment where the trigger will be active."),
    feature_flag_key: str = Field(..., alias="featureFlagKey", description="The unique identifier of the feature flag that will be triggered."),
    integration_key: str = Field(..., alias="integrationKey", description="The unique identifier of the integration that will activate this trigger. Use 'generic-trigger' for integrations that are not explicitly supported by the system."),
    instructions: list[_models.Instruction] | None = Field(None, description="An array containing a single object that specifies the action to perform when the trigger is activated. The object must have a 'kind' field set to either 'turnFlagOn' or 'turnFlagOff' to control the flag's state."),
) -> dict[str, Any]:
    """Create a new trigger for a feature flag that automatically performs an action (such as turning the flag on or off) when activated by an integrated system."""

    # Construct request model with validation
    try:
        _request = _models.CreateTriggerWorkflowRequest(
            path=_models.CreateTriggerWorkflowRequestPath(project_key=project_key, environment_key=environment_key, feature_flag_key=feature_flag_key),
            body=_models.CreateTriggerWorkflowRequestBody(instructions=instructions, integration_key=integration_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_flag_trigger: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/flags/{projectKey}/{featureFlagKey}/triggers/{environmentKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/flags/{projectKey}/{featureFlagKey}/triggers/{environmentKey}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_flag_trigger")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_flag_trigger", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_flag_trigger",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Flag triggers
@mcp.tool()
async def get_trigger_workflow_by_id(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the feature flag and trigger."),
    feature_flag_key: str = Field(..., alias="featureFlagKey", description="The unique identifier for the feature flag that contains the trigger."),
    environment_key: str = Field(..., alias="environmentKey", description="The unique identifier for the environment in which the trigger operates."),
    id_: str = Field(..., alias="id", description="The unique identifier of the specific flag trigger to retrieve."),
) -> dict[str, Any]:
    """Retrieve a specific flag trigger by its ID within a feature flag, project, and environment context. Use this to fetch detailed configuration and status of an individual trigger workflow."""

    # Construct request model with validation
    try:
        _request = _models.GetTriggerWorkflowByIdRequest(
            path=_models.GetTriggerWorkflowByIdRequestPath(project_key=project_key, feature_flag_key=feature_flag_key, environment_key=environment_key, id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_trigger_workflow_by_id: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/flags/{projectKey}/{featureFlagKey}/triggers/{environmentKey}/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/flags/{projectKey}/{featureFlagKey}/triggers/{environmentKey}/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_trigger_workflow_by_id")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_trigger_workflow_by_id", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_trigger_workflow_by_id",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Flag triggers
@mcp.tool()
async def update_flag_trigger(
    project_key: str = Field(..., alias="projectKey", description="The project key that contains the feature flag."),
    environment_key: str = Field(..., alias="environmentKey", description="The environment key where the trigger is configured."),
    feature_flag_key: str = Field(..., alias="featureFlagKey", description="The feature flag key associated with this trigger."),
    id_: str = Field(..., alias="id", description="The unique identifier of the flag trigger to update."),
    instructions: list[_models.Instruction] | None = Field(None, description="An array of semantic patch instructions to apply. Each instruction is an object with a `kind` field specifying the operation: `replaceTriggerActionInstructions` (with `value` array of actions like `turnFlagOn` or `turnFlagOff`), `cycleTriggerUrl`, `disableTrigger`, or `enableTrigger`. Instructions are applied in order."),
) -> dict[str, Any]:
    """Update a flag trigger's configuration using semantic patch instructions. Supports actions like enabling/disabling the trigger, replacing trigger actions, or cycling the trigger URL."""

    # Construct request model with validation
    try:
        _request = _models.PatchTriggerWorkflowRequest(
            path=_models.PatchTriggerWorkflowRequestPath(project_key=project_key, environment_key=environment_key, feature_flag_key=feature_flag_key, id_=id_),
            body=_models.PatchTriggerWorkflowRequestBody(instructions=instructions)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_flag_trigger: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/flags/{projectKey}/{featureFlagKey}/triggers/{environmentKey}/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/flags/{projectKey}/{featureFlagKey}/triggers/{environmentKey}/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_flag_trigger")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_flag_trigger", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_flag_trigger",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Flag triggers
@mcp.tool()
async def delete_trigger_for_flag(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the feature flag."),
    environment_key: str = Field(..., alias="environmentKey", description="The unique identifier for the environment where the flag trigger is configured."),
    feature_flag_key: str = Field(..., alias="featureFlagKey", description="The unique identifier for the feature flag associated with this trigger."),
    id_: str = Field(..., alias="id", description="The unique identifier of the flag trigger to delete."),
) -> dict[str, Any]:
    """Delete a specific flag trigger by its ID. This removes the trigger configuration that automates flag state changes based on defined conditions."""

    # Construct request model with validation
    try:
        _request = _models.DeleteTriggerWorkflowRequest(
            path=_models.DeleteTriggerWorkflowRequestPath(project_key=project_key, environment_key=environment_key, feature_flag_key=feature_flag_key, id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_trigger_for_flag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/flags/{projectKey}/{featureFlagKey}/triggers/{environmentKey}/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/flags/{projectKey}/{featureFlagKey}/triggers/{environmentKey}/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_trigger_for_flag")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_trigger_for_flag", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_trigger_for_flag",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Releases (beta)
@mcp.tool()
async def get_release_by_flag_key(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the flag."),
    flag_key: str = Field(..., alias="flagKey", description="The unique identifier for the feature flag within the project."),
) -> dict[str, Any]:
    """Retrieve the currently active release associated with a specific feature flag. Returns release metadata if an active release exists for the flag."""

    # Construct request model with validation
    try:
        _request = _models.GetReleaseByFlagKeyRequest(
            path=_models.GetReleaseByFlagKeyRequestPath(project_key=project_key, flag_key=flag_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_release_by_flag_key: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/flags/{projectKey}/{flagKey}/release", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/flags/{projectKey}/{flagKey}/release"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_release_by_flag_key")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_release_by_flag_key", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_release_by_flag_key",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Releases (beta)
@mcp.tool()
async def update_release_phase_status_by_flag_key(
    project_key: str = Field(..., alias="projectKey", description="The project key that contains the flag. A string identifier for the project."),
    flag_key: str = Field(..., alias="flagKey", description="The flag key identifying which flag's release to update. A string identifier for the flag."),
    body: list[_models.PatchOperation] = Field(..., description="A JSON patch array specifying the phase status changes. Each patch object must contain an 'op' field set to 'replace', a 'path' field pointing to a phase's complete status (e.g., '/phases/0/complete'), and a 'value' field set to true or false. Array order matters—use the index to target specific phases."),
) -> dict[str, Any]:
    """Update the completion status of a release phase for a flag in a legacy release pipeline. Use JSON patch format to mark specific phases as complete or incomplete by their array index."""

    # Construct request model with validation
    try:
        _request = _models.PatchReleaseByFlagKeyRequest(
            path=_models.PatchReleaseByFlagKeyRequestPath(project_key=project_key, flag_key=flag_key),
            body=_models.PatchReleaseByFlagKeyRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_release_phase_status_by_flag_key: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/flags/{projectKey}/{flagKey}/release", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/flags/{projectKey}/{flagKey}/release"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_release_phase_status_by_flag_key")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_release_phase_status_by_flag_key", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_release_phase_status_by_flag_key",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Releases (beta)
@mcp.tool()
async def delete_release_for_flag(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the flag. Used to scope the operation to the correct project context."),
    flag_key: str = Field(..., alias="flagKey", description="The unique identifier for the feature flag from which the release will be deleted. Must correspond to an existing flag within the specified project."),
) -> dict[str, Any]:
    """Removes a release associated with a feature flag. This operation permanently deletes the release record from the specified flag within a project."""

    # Construct request model with validation
    try:
        _request = _models.DeleteReleaseByFlagKeyRequest(
            path=_models.DeleteReleaseByFlagKeyRequestPath(project_key=project_key, flag_key=flag_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_release_for_flag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/flags/{projectKey}/{flagKey}/release", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/flags/{projectKey}/{flagKey}/release"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_release_for_flag")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_release_for_flag", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_release_for_flag",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Integration audit log subscriptions
@mcp.tool()
async def list_audit_subscriptions_by_integration(integration_key: str = Field(..., alias="integrationKey", description="The unique identifier for the integration whose audit log subscriptions you want to retrieve.")) -> dict[str, Any]:
    """Retrieve all audit log subscriptions associated with a specific integration. Use this to view which audit events are being monitored for a given integration."""

    # Construct request model with validation
    try:
        _request = _models.GetSubscriptionsRequest(
            path=_models.GetSubscriptionsRequestPath(integration_key=integration_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_audit_subscriptions_by_integration: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/integrations/{integrationKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/integrations/{integrationKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_audit_subscriptions_by_integration")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_audit_subscriptions_by_integration", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_audit_subscriptions_by_integration",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Integration audit log subscriptions
@mcp.tool()
async def get_audit_log_subscription(
    integration_key: str = Field(..., alias="integrationKey", description="The unique identifier for the integration. This key determines which integration context the subscription belongs to."),
    id_: str = Field(..., alias="id", description="The unique identifier of the audit log subscription to retrieve."),
) -> dict[str, Any]:
    """Retrieve a specific audit log subscription by its ID within a given integration. Use this to fetch details about an existing subscription configuration."""

    # Construct request model with validation
    try:
        _request = _models.GetSubscriptionByIdRequest(
            path=_models.GetSubscriptionByIdRequestPath(integration_key=integration_key, id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_audit_log_subscription: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/integrations/{integrationKey}/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/integrations/{integrationKey}/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_audit_log_subscription")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_audit_log_subscription", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_audit_log_subscription",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Integration audit log subscriptions
@mcp.tool()
async def update_audit_log_subscription(
    integration_key: str = Field(..., alias="integrationKey", description="The unique identifier for the integration containing the audit log subscription."),
    id_: str = Field(..., alias="id", description="The unique identifier of the audit log subscription to update."),
    body: list[_models.PatchOperation] = Field(..., description="An array of JSON Patch operations describing the changes to apply. Each operation must include 'op' (the operation type), 'path' (the JSON pointer to the target field), and 'value' (the new value for replace/add operations)."),
) -> dict[str, Any]:
    """Update an audit log subscription configuration using JSON Patch operations. Specify the changes you want to apply to the subscription settings."""

    # Construct request model with validation
    try:
        _request = _models.UpdateSubscriptionRequest(
            path=_models.UpdateSubscriptionRequestPath(integration_key=integration_key, id_=id_),
            body=_models.UpdateSubscriptionRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_audit_log_subscription: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/integrations/{integrationKey}/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/integrations/{integrationKey}/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_audit_log_subscription")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_audit_log_subscription", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_audit_log_subscription",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Integration audit log subscriptions
@mcp.tool()
async def delete_audit_log_subscription(
    integration_key: str = Field(..., alias="integrationKey", description="The unique identifier for the integration from which the subscription will be deleted."),
    id_: str = Field(..., alias="id", description="The unique identifier of the audit log subscription to delete."),
) -> dict[str, Any]:
    """Remove an audit log subscription from an integration. This permanently deletes the subscription and stops audit log collection for the specified integration."""

    # Construct request model with validation
    try:
        _request = _models.DeleteSubscriptionRequest(
            path=_models.DeleteSubscriptionRequestPath(integration_key=integration_key, id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_audit_log_subscription: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/integrations/{integrationKey}/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/integrations/{integrationKey}/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_audit_log_subscription")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_audit_log_subscription", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_audit_log_subscription",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Account members
@mcp.tool()
async def list_members() -> dict[str, Any]:
    """Retrieve a paginated list of account members with support for filtering by query, role, ID, email, team membership, and activity status. Optionally expand the response to include custom roles and role attributes."""

    # Extract parameters for API call
    _http_path = "/api/v2/members"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_members")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_members", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_members",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Account members
@mcp.tool()
async def invite_members(body: list[_models.NewMemberForm] = Field(..., description="Array of member objects to invite. Each object must include an email field and either a role field (base role name) or customRoles field (custom or preset role key). Some roles may require roleAttributes for scope specification. Maximum 50 members per request. The request fails entirely if any member data is invalid or if email addresses conflict with existing members in this account or others, or if duplicates exist within the request itself.")) -> dict[str, Any]:
    """Invite one or more new members to join an account via email. Each member receives an invitation and must have a valid email address with either a base role (reader, writer, admin, owner/admin, no_access) or a custom role key. Up to 50 members can be invited per request; the entire request fails if any member's data is invalid or conflicts with existing members."""

    # Construct request model with validation
    try:
        _request = _models.PostMembersRequest(
            body=_models.PostMembersRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for invite_members: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v2/members"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("invite_members")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("invite_members", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="invite_members",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Account members
@mcp.tool()
async def update_members_bulk(instructions: list[_models.Instruction] = Field(..., description="Array of semantic patch instructions defining the bulk update operations. Each instruction object must include a `kind` field specifying the operation type (replaceMembersRoles, replaceAllMembersRoles, replaceMembersCustomRoles, replaceAllMembersCustomRoles, or replaceMembersRoleAttributes) along with required parameters for that operation type. Instructions are processed sequentially.")) -> dict[str, Any]:
    """Perform bulk updates to member roles and custom roles using semantic patch instructions. Supports targeted updates to specific members or filtered bulk updates across all members (Enterprise feature)."""

    # Construct request model with validation
    try:
        _request = _models.PatchMembersRequest(
            body=_models.PatchMembersRequestBody(instructions=instructions)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_members_bulk: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v2/members"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_members_bulk")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_members_bulk", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_members_bulk",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Account members
@mcp.tool()
async def get_member(id_: str = Field(..., alias="id", description="The member ID as a string. Use the reserved value `me` to retrieve the caller's own member information instead of specifying a numeric ID.")) -> dict[str, Any]:
    """Retrieve a single account member by ID. Use the reserved value `me` to get the caller's own member information. Optionally expand the response to include custom role details and role attributes."""

    # Construct request model with validation
    try:
        _request = _models.GetMemberRequest(
            path=_models.GetMemberRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_member: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/members/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/members/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_member")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_member", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_member",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Account members
@mcp.tool()
async def update_member(
    id_: str = Field(..., alias="id", description="The unique identifier of the member to update."),
    body: list[_models.PatchOperation] = Field(..., description="A JSON Patch array describing the changes to apply. Each patch object must contain an operation (add, remove, replace, etc.), a path (e.g., '/role' or '/customRoles/0'), and a value. Use array index notation to modify role arrays: use '/0' to prepend, '/-' to append, or a specific index to modify an existing position."),
) -> dict[str, Any]:
    """Update an account member's role or custom roles using JSON Patch format. Changes are applied to the member object, though IdP-managed accounts may be overridden by the Identity Provider shortly after."""

    # Construct request model with validation
    try:
        _request = _models.PatchMemberRequest(
            path=_models.PatchMemberRequestPath(id_=id_),
            body=_models.PatchMemberRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_member: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/members/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/members/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_member")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_member", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_member",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Account members
@mcp.tool()
async def delete_member(id_: str = Field(..., alias="id", description="The unique identifier of the member to delete")) -> dict[str, Any]:
    """Remove an account member by their ID. This operation will fail if SCIM provisioning is enabled for the account."""

    # Construct request model with validation
    try:
        _request = _models.DeleteMemberRequest(
            path=_models.DeleteMemberRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_member: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/members/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/members/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_member")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_member", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_member",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Account members
@mcp.tool()
async def add_member_to_teams(
    id_: str = Field(..., alias="id", description="The unique identifier of the member to add to teams."),
    team_keys: list[str] = Field(..., alias="teamKeys", description="An array of team keys identifying which teams the member should be added to. Provide one or more team keys as strings in the array."),
) -> dict[str, Any]:
    """Add a single member to one or more teams. The member will be granted access to all specified teams."""

    # Construct request model with validation
    try:
        _request = _models.PostMemberTeamsRequest(
            path=_models.PostMemberTeamsRequestPath(id_=id_),
            body=_models.PostMemberTeamsRequestBody(team_keys=team_keys)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_member_to_teams: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/members/{id}/teams", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/members/{id}/teams"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_member_to_teams")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_member_to_teams", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_member_to_teams",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Metrics
@mcp.tool()
async def list_metrics(project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project. Used to scope the metrics query to a specific project.")) -> dict[str, Any]:
    """Retrieve all metrics for a specified project with support for filtering by various criteria (data sources, event types, tags, usage context) and optional expansion of related experiment counts."""

    # Construct request model with validation
    try:
        _request = _models.GetMetricsRequest(
            path=_models.GetMetricsRequestPath(project_key=project_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_metrics: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/metrics/{projectKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/metrics/{projectKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_metrics")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_metrics", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_metrics",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Metrics
@mcp.tool()
async def create_metric(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project where the metric will be created."),
    key: str = Field(..., description="A unique identifier for the metric, used as a reference key in your codebase (e.g., 'metric-key-123abc')."),
    data_source_key: str = Field(..., alias="dataSourceKey", description="The unique identifier for the data source that will provide events for this metric."),
    kind: Literal["pageview", "click", "custom"] = Field(..., description="The type of event this metric tracks: 'pageview' for page views, 'click' for user clicks, or 'custom' for application-defined events."),
    type_: str = Field(..., alias="type", description="The filter type: 'contextAttribute' to filter on user context attributes, 'eventProperty' to filter on event properties, or 'group' to filter on group membership."),
    op: str = Field(..., description="The comparison operator to apply (e.g., 'in', 'equals', 'contains'). Determines how values are matched against the filter."),
    values: list[Any] = Field(..., description="An array of values to match against the filter. For numeric values, do not exceed 14 decimal places (e.g., ['JP'] for country filtering)."),
    negate: bool = Field(..., description="Set to true to invert the filter logic (e.g., 'in' becomes 'not in'). Defaults to false."),
    name: str | None = Field(None, description="A human-readable name for the metric to display in the UI (e.g., 'Example metric')."),
    data_source_name: str | None = Field(None, alias="dataSourceName", description="The human-readable name of the data source providing events for this metric."),
    selector: str | None = Field(None, description="One or more CSS selectors identifying the elements to track. Required only for click metrics (e.g., '.dropdown-toggle')."),
    urls: list[_models.UrlPost] | None = Field(None, description="One or more target URLs to track. Required for click and pageview metrics. Specify as an array of URL strings."),
    is_numeric: bool | None = Field(None, alias="isNumeric", description="For custom metrics only: set to true to track numeric value changes against a baseline, or false to track conversions when users take an action."),
    unit: str | None = Field(None, description="The unit of measurement for numeric custom metrics (e.g., 'orders', 'revenue'). Only applicable when tracking numeric values."),
    event_key: str | None = Field(None, alias="eventKey", description="The event key identifier used in your application code to trigger this metric. Required for custom conversion and numeric metrics (e.g., 'Order placed')."),
    success_criteria: Literal["HigherThanBaseline", "LowerThanBaseline"] | None = Field(None, alias="successCriteria", description="Success criteria for numeric custom metrics: 'HigherThanBaseline' if increases are favorable, 'LowerThanBaseline' if decreases are favorable. Optional for conversion metrics."),
    tags: list[str] | None = Field(None, description="An array of tags to organize and categorize the metric (e.g., ['example-tag'])."),
    randomization_units: list[str] | None = Field(None, alias="randomizationUnits", description="An array of randomization units allowed for this metric (e.g., ['user']). Determines how experiment variations are assigned."),
    disabled: bool | None = Field(None, description="Set to true to disable automatic default values for missing unit events during result calculation. Defaults to false."),
    value: float | None = Field(None, description="The default numeric value applied to missing unit events when disabled is false. Currently only 0 is supported."),
    environment_key: str | None = Field(None, alias="environmentKey", description="The environment key associated with this metric (e.g., 'production', 'staging')."),
    integration_key: str | None = Field(None, alias="integrationKey", description="The integration key for connecting this metric to an external data source or service."),
    attribute: str | None = Field(None, description="The name of the context attribute or event property to filter on (e.g., 'country'). Not applicable for group-type filters."),
    trace_query: str | None = Field(None, alias="traceQuery", description="A trace query to identify relevant traces for this metric (e.g., 'service.name = \"checkout\"'). Required only for trace metrics."),
    trace_value_location: str | None = Field(None, alias="traceValueLocation", description="The location within a trace to extract numeric values from (e.g., 'duration'). Required only for numeric trace metrics."),
) -> dict[str, Any]:
    """Create a new metric in a specified project to track user interactions or custom events. The metric structure varies based on the kind (pageview, click, or custom) and whether it measures conversions or numeric values."""

    # Construct request model with validation
    try:
        _request = _models.PostMetricRequest(
            path=_models.PostMetricRequestPath(project_key=project_key),
            body=_models.PostMetricRequestBody(key=key, name=name, kind=kind, selector=selector, urls=urls, is_numeric=is_numeric, unit=unit, event_key=event_key, success_criteria=success_criteria, tags=tags, randomization_units=randomization_units, trace_query=trace_query, trace_value_location=trace_value_location,
                data_source=_models.PostMetricRequestBodyDataSource(key=data_source_key, name=data_source_name, environment_key=environment_key, integration_key=integration_key),
                event_default=_models.PostMetricRequestBodyEventDefault(disabled=disabled, value=value) if any(v is not None for v in [disabled, value]) else None,
                filters=_models.PostMetricRequestBodyFilters(type_=type_, attribute=attribute, op=op, values=values, negate=negate))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_metric: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/metrics/{projectKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/metrics/{projectKey}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_metric")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_metric", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_metric",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Metrics
@mcp.tool()
async def get_metric(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the LaunchDarkly project containing the metric."),
    metric_key: str = Field(..., alias="metricKey", description="The unique identifier for the metric to retrieve."),
    version_id: str | None = Field(None, alias="versionId", description="The specific version ID of the metric to retrieve. If omitted, returns the current version. Use comma-separated values in the expand query parameter to include experiments, experimentCount, metricGroups, or metricGroupCount in the response."),
) -> dict[str, Any]:
    """Retrieve detailed information about a specific metric in a LaunchDarkly project. Optionally expand the response to include related experiments and metric groups."""

    # Construct request model with validation
    try:
        _request = _models.GetMetricRequest(
            path=_models.GetMetricRequestPath(project_key=project_key, metric_key=metric_key),
            query=_models.GetMetricRequestQuery(version_id=version_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_metric: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/metrics/{projectKey}/{metricKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/metrics/{projectKey}/{metricKey}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_metric")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_metric", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_metric",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Metrics
@mcp.tool()
async def update_metric(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the metric."),
    metric_key: str = Field(..., alias="metricKey", description="The unique identifier for the metric to update."),
    body: list[_models.PatchOperation] = Field(..., description="An array of JSON Patch operations describing the changes to apply. Each operation must include 'op' (the operation type such as 'replace', 'add', or 'remove'), 'path' (the JSON pointer to the target property), and 'value' (the new value, required for 'replace' and 'add' operations)."),
) -> dict[str, Any]:
    """Update a metric using JSON Patch operations. Specify the changes you want to make to the metric's properties such as name, description, or other attributes."""

    # Construct request model with validation
    try:
        _request = _models.PatchMetricRequest(
            path=_models.PatchMetricRequestPath(project_key=project_key, metric_key=metric_key),
            body=_models.PatchMetricRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_metric: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/metrics/{projectKey}/{metricKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/metrics/{projectKey}/{metricKey}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_metric")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_metric", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_metric",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Metrics
@mcp.tool()
async def delete_metric(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the metric to delete."),
    metric_key: str = Field(..., alias="metricKey", description="The unique identifier for the metric to delete."),
) -> dict[str, Any]:
    """Permanently delete a metric from a project by its key. This operation removes the metric and all associated data."""

    # Construct request model with validation
    try:
        _request = _models.DeleteMetricRequest(
            path=_models.DeleteMetricRequestPath(project_key=project_key, metric_key=metric_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_metric: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/metrics/{projectKey}/{metricKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/metrics/{projectKey}/{metricKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_metric")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_metric", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_metric",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: OAuth2 Clients
@mcp.tool()
async def list_oauth_clients() -> dict[str, Any]:
    """Retrieve all OAuth 2.0 clients registered with your account. Use this to view and manage your application integrations."""

    # Extract parameters for API call
    _http_path = "/api/v2/oauth/clients"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_oauth_clients")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_oauth_clients", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_oauth_clients",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: OAuth2 Clients
@mcp.tool()
async def get_oauth_client_by_id(client_id: str = Field(..., alias="clientId", description="The unique identifier of the OAuth 2.0 client to retrieve.")) -> dict[str, Any]:
    """Retrieve a registered OAuth 2.0 client by its unique client ID. Use this to fetch detailed configuration and metadata for a specific OAuth client application."""

    # Construct request model with validation
    try:
        _request = _models.GetOAuthClientByIdRequest(
            path=_models.GetOAuthClientByIdRequestPath(client_id=client_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_oauth_client_by_id: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/oauth/clients/{clientId}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/oauth/clients/{clientId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_oauth_client_by_id")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_oauth_client_by_id", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_oauth_client_by_id",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: OAuth2 Clients
@mcp.tool()
async def update_oauth_client(
    client_id: str = Field(..., alias="clientId", description="The unique identifier of the OAuth 2.0 client to update."),
    body: list[_models.PatchOperation] = Field(..., description="A JSON Patch array describing the changes to apply. Each operation must specify an operation type (op), a JSON pointer path, and a value. Supported paths are /name, /description, and /redirectUri."),
) -> dict[str, Any]:
    """Update an OAuth 2.0 client's configuration using JSON Patch operations. Only the client name, description, and redirect URI can be modified."""

    # Construct request model with validation
    try:
        _request = _models.PatchOAuthClientRequest(
            path=_models.PatchOAuthClientRequestPath(client_id=client_id),
            body=_models.PatchOAuthClientRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_oauth_client: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/oauth/clients/{clientId}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/oauth/clients/{clientId}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_oauth_client")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_oauth_client", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_oauth_client",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: OAuth2 Clients
@mcp.tool()
async def delete_oauth_client(client_id: str = Field(..., alias="clientId", description="The unique identifier of the OAuth 2.0 client to delete.")) -> dict[str, Any]:
    """Permanently delete an OAuth 2.0 client application by its unique identifier. This action cannot be undone and will invalidate all tokens issued to this client."""

    # Construct request model with validation
    try:
        _request = _models.DeleteOAuthClientRequest(
            path=_models.DeleteOAuthClientRequestPath(client_id=client_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_oauth_client: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/oauth/clients/{clientId}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/oauth/clients/{clientId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_oauth_client")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_oauth_client", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_oauth_client",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def list_projects() -> dict[str, Any]:
    """Retrieve a paginated list of projects with support for filtering by name, tags, or keys, and sorting by name or creation date. Results are limited to 20 projects per page by default; use pagination links to navigate through additional pages."""

    # Extract parameters for API call
    _http_path = "/api/v2/projects"
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
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def create_project(
    name: str = Field(..., description="A human-friendly display name for the project (e.g., 'My Project')."),
    key: str = Field(..., description="A unique identifier for the project used in code references (e.g., 'project-key-123abc'). Must be unique within your account."),
    using_environment_id: bool = Field(..., alias="usingEnvironmentId", description="Enable or disable availability of this project for client-side SDKs."),
    using_mobile_key: bool = Field(..., alias="usingMobileKey", description="Enable or disable availability of this project for mobile SDKs."),
    tags: list[str] | None = Field(None, description="Optional list of tags to organize and categorize the project (e.g., ['ops'])."),
    environments: list[_models.EnvironmentPost] | None = Field(None, description="Optional list of environments to create for this project. If omitted, default environments will be created automatically."),
    case: Literal["camelCase", "upperCamelCase", "snakeCase", "kebabCase", "constantCase"] | None = Field(None, description="Optional casing convention to enforce for new flag keys in this project. Choose from: camelCase, upperCamelCase, snakeCase, kebabCase, or constantCase."),
    prefix: str | None = Field(None, description="Optional prefix to enforce for all new flag keys in this project (e.g., 'enable-')."),
) -> dict[str, Any]:
    """Create a new project with a unique key and name. Configure SDK availability, naming conventions, and initial environments for the project."""

    # Construct request model with validation
    try:
        _request = _models.PostProjectRequest(
            body=_models.PostProjectRequestBody(name=name, key=key, tags=tags, environments=environments,
                default_client_side_availability=_models.PostProjectRequestBodyDefaultClientSideAvailability(using_environment_id=using_environment_id, using_mobile_key=using_mobile_key),
                naming_convention=_models.PostProjectRequestBodyNamingConvention(case=case, prefix=prefix) if any(v is not None for v in [case, prefix]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v2/projects"
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

# Tags: Projects
@mcp.tool()
async def get_project(project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project. Used to specify which project to retrieve.")) -> dict[str, Any]:
    """Retrieve a single project by its key. Optionally expand the response to include related resources such as environments."""

    # Construct request model with validation
    try:
        _request = _models.GetProjectRequest(
            path=_models.GetProjectRequestPath(project_key=project_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}"
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
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project to update."),
    body: list[_models.PatchOperation] = Field(..., description="An array of JSON Patch operations describing the changes to apply. Each operation must specify an operation type (add, remove, replace, etc.), a JSON Pointer path to the target field, and a value where applicable. For array fields, use numeric indices or `/-` to append to the end."),
) -> dict[str, Any]:
    """Update a project using JSON Patch operations. Supports modifying project fields including adding, removing, or replacing values. Array fields like tags are automatically deduplicated and sorted alphabetically."""

    # Construct request model with validation
    try:
        _request = _models.PatchProjectRequest(
            path=_models.PatchProjectRequestPath(project_key=project_key),
            body=_models.PatchProjectRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_project")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_project", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_project",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def delete_project(project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project to delete. This is a string value that uniquely identifies the project within your account.")) -> dict[str, Any]:
    """Permanently delete a project and all its associated environments and feature flags. This operation cannot be undone and will fail if the project is the last one in the account."""

    # Construct request model with validation
    try:
        _request = _models.DeleteProjectRequest(
            path=_models.DeleteProjectRequestPath(project_key=project_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}"
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
        headers=_http_headers,
    )

    return _response_data

# Tags: Contexts
@mcp.tool()
async def list_context_kinds_by_project(project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project. This is a string-based key that distinguishes the project within your LaunchDarkly workspace.")) -> dict[str, Any]:
    """Retrieve all context kinds configured for a specific project. Context kinds define the types of contextual information that can be associated with feature flags and experiments in the project."""

    # Construct request model with validation
    try:
        _request = _models.GetContextKindsByProjectKeyRequest(
            path=_models.GetContextKindsByProjectKeyRequestPath(project_key=project_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_context_kinds_by_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/context-kinds", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/context-kinds"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_context_kinds_by_project")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_context_kinds_by_project", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_context_kinds_by_project",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Contexts
@mcp.tool()
async def update_context_kind(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the context kind."),
    key: str = Field(..., description="The unique identifier for the context kind to create or update."),
    name: str = Field(..., description="The display name for the context kind (e.g., 'organization'). This is the human-readable label used to identify the context kind."),
    archived: bool | None = Field(None, description="Whether the context kind is archived. Archived context kinds cannot be used for targeting. Defaults to false if not specified."),
) -> dict[str, Any]:
    """Create or update a context kind within a project. If the context kind exists, only the provided fields will be updated; otherwise, a new context kind will be created."""

    # Construct request model with validation
    try:
        _request = _models.PutContextKindRequest(
            path=_models.PutContextKindRequestPath(project_key=project_key, key=key),
            body=_models.PutContextKindRequestBody(name=name, archived=archived)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_context_kind: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/context-kinds/{key}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/context-kinds/{key}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_context_kind")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_context_kind", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_context_kind",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Environments
@mcp.tool()
async def list_environments_by_project(project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project. Used to scope the environment list to a specific project.")) -> dict[str, Any]:
    """Retrieve a paginated list of environments for a specified project, with support for filtering by name/key and tags, and sorting by creation date, criticality, or name."""

    # Construct request model with validation
    try:
        _request = _models.GetEnvironmentsByProjectRequest(
            path=_models.GetEnvironmentsByProjectRequestPath(project_key=project_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_environments_by_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/environments", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/environments"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_environments_by_project")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_environments_by_project", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_environments_by_project",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Environments
@mcp.tool()
async def create_environment(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project where the environment will be created."),
    name: str = Field(..., description="A human-readable name for the environment (e.g., 'Production', 'Staging', 'Development')."),
    key: str = Field(..., description="A project-unique identifier for the environment, used in API calls and SDKs (e.g., 'prod', 'staging', 'dev')."),
    color: str = Field(..., description="A hex color code (without '#') to visually distinguish this environment in the LaunchDarkly UI (e.g., 'F5A623' for orange)."),
    source_key: str | None = Field(None, alias="sourceKey", description="Optional: The key of an existing environment to clone configuration from, including flags and segments."),
    default_ttl: int | None = Field(None, alias="defaultTtl", description="Optional: The default cache duration in minutes for the PHP SDK to store feature flag rules locally. Reduces API calls but may delay flag updates."),
    secure_mode: bool | None = Field(None, alias="secureMode", description="Optional: When enabled, prevents client-side SDK users from viewing flag variations assigned to other users, enhancing security for sensitive environments."),
    default_track_events: bool | None = Field(None, alias="defaultTrackEvents", description="Optional: When enabled, automatically tracks detailed event data for newly created feature flags in this environment."),
    confirm_changes: bool | None = Field(None, alias="confirmChanges", description="Optional: When enabled, requires explicit confirmation in the UI before applying any flag or segment changes in this environment."),
    require_comments: bool | None = Field(None, alias="requireComments", description="Optional: When enabled, requires users to provide comments explaining the reason for any flag or segment changes made via the UI."),
    tags: list[str] | None = Field(None, description="Optional: An array of tags to categorize and organize the environment (e.g., ['ops', 'production'], ['team:backend'])."),
    critical: bool | None = Field(None, description="Optional: Marks this environment as critical, which may trigger additional safeguards or notifications for changes."),
) -> dict[str, Any]:
    """Create a new environment within a project. Specify the environment name, unique key, UI color, and optional settings like caching TTL, secure mode, and change approval requirements. Note: approval settings cannot be configured during creation and must be updated separately."""

    # Construct request model with validation
    try:
        _request = _models.PostEnvironmentRequest(
            path=_models.PostEnvironmentRequestPath(project_key=project_key),
            body=_models.PostEnvironmentRequestBody(name=name, key=key, color=color, default_ttl=default_ttl, secure_mode=secure_mode, default_track_events=default_track_events, confirm_changes=confirm_changes, require_comments=require_comments, tags=tags, critical=critical,
                source=_models.PostEnvironmentRequestBodySource(key=source_key) if any(v is not None for v in [source_key]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_environment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/environments", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/environments"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_environment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_environment", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_environment",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Environments
@mcp.tool()
async def get_environment(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the environment."),
    environment_key: str = Field(..., alias="environmentKey", description="The unique identifier for the environment to retrieve."),
) -> dict[str, Any]:
    """Retrieve a specific environment within a project. Returns environment configuration including approval settings when the approvals feature is enabled."""

    # Construct request model with validation
    try:
        _request = _models.GetEnvironmentRequest(
            path=_models.GetEnvironmentRequestPath(project_key=project_key, environment_key=environment_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_environment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/environments/{environmentKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/environments/{environmentKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_environment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_environment", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_environment",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Environments
@mcp.tool()
async def update_environment(
    project_key: str = Field(..., alias="projectKey", description="The project key that identifies which project contains the environment to update."),
    environment_key: str = Field(..., alias="environmentKey", description="The environment key that identifies which environment within the project to update."),
    body: list[_models.PatchOperation] = Field(..., description="A JSON Patch array describing the changes to apply. Each operation specifies an action (op), target path, and value. For array fields, append the index to the path (e.g., `/fieldName/0` to prepend). Only `canReviewOwnRequest`, `canApplyDeclinedChanges`, `minNumApprovals`, `required`, and `requiredApprovalTags` approval settings are editable; do not set both `required` and `requiredApprovalTags` simultaneously."),
) -> dict[str, Any]:
    """Update an environment's configuration using JSON Patch operations. Supports modifying fields including approval settings, comments requirements, and array-based properties."""

    # Construct request model with validation
    try:
        _request = _models.PatchEnvironmentRequest(
            path=_models.PatchEnvironmentRequestPath(project_key=project_key, environment_key=environment_key),
            body=_models.PatchEnvironmentRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_environment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/environments/{environmentKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/environments/{environmentKey}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_environment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_environment", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_environment",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Environments
@mcp.tool()
async def delete_environment(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the environment to delete."),
    environment_key: str = Field(..., alias="environmentKey", description="The unique identifier for the environment to delete."),
) -> dict[str, Any]:
    """Permanently delete an environment from a project by its key. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteEnvironmentRequest(
            path=_models.DeleteEnvironmentRequestPath(project_key=project_key, environment_key=environment_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_environment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/environments/{environmentKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/environments/{environmentKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_environment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_environment", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_environment",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Environments
@mcp.tool()
async def reset_environment_sdk_key(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the environment."),
    environment_key: str = Field(..., alias="environmentKey", description="The unique identifier for the environment whose SDK key should be reset."),
    expiry: str | None = Field(None, description="Optional grace period for the old SDK key expiration, specified in UNIX milliseconds. If not provided, the old key expires immediately. This allows clients using the old key to transition to the new key without service interruption."),
) -> dict[str, Any]:
    """Reset an environment's SDK key and optionally specify when the old key should expire. During the expiry grace period, both the old and new SDK keys remain valid, allowing for seamless client migration."""

    _expiry = _parse_int(expiry)

    # Construct request model with validation
    try:
        _request = _models.ResetEnvironmentSdkKeyRequest(
            path=_models.ResetEnvironmentSdkKeyRequestPath(project_key=project_key, environment_key=environment_key),
            query=_models.ResetEnvironmentSdkKeyRequestQuery(expiry=_expiry)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for reset_environment_sdk_key: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/environments/{environmentKey}/apiKey", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/environments/{environmentKey}/apiKey"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("reset_environment_sdk_key")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("reset_environment_sdk_key", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="reset_environment_sdk_key",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Contexts
@mcp.tool()
async def list_context_attribute_names(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the environment."),
    environment_key: str = Field(..., alias="environmentKey", description="The unique identifier for the environment within the project."),
) -> dict[str, Any]:
    """Retrieve all available context attribute names for a specific environment within a project. This returns the list of attributes that can be used to define user context in feature flag evaluations."""

    # Construct request model with validation
    try:
        _request = _models.GetContextAttributeNamesRequest(
            path=_models.GetContextAttributeNamesRequestPath(project_key=project_key, environment_key=environment_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_context_attribute_names: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/environments/{environmentKey}/context-attributes", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/environments/{environmentKey}/context-attributes"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_context_attribute_names")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_context_attribute_names", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_context_attribute_names",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Contexts
@mcp.tool()
async def get_context_attribute_values(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the context attribute."),
    environment_key: str = Field(..., alias="environmentKey", description="The unique identifier for the environment within the project where the context attribute values are stored."),
    attribute_name: str = Field(..., alias="attributeName", description="The name of the context attribute for which to retrieve values."),
) -> dict[str, Any]:
    """Retrieve all values associated with a specific context attribute within a project environment. Use this to discover what values have been recorded or are available for a given attribute name."""

    # Construct request model with validation
    try:
        _request = _models.GetContextAttributeValuesRequest(
            path=_models.GetContextAttributeValuesRequestPath(project_key=project_key, environment_key=environment_key, attribute_name=attribute_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_context_attribute_values: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/environments/{environmentKey}/context-attributes/{attributeName}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/environments/{environmentKey}/context-attributes/{attributeName}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_context_attribute_values")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_context_attribute_values", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_context_attribute_values",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Contexts
@mcp.tool()
async def search_context_instances(
    project_key: str = Field(..., alias="projectKey", description="The project key that identifies which project contains the context instances to search."),
    environment_key: str = Field(..., alias="environmentKey", description="The environment key that identifies which environment within the project to search."),
    continuation_token: str | None = Field(None, alias="continuationToken", description="Pagination token for retrieving subsequent result pages. Use the `next` link from previous responses when available, or provide a continuation token to fetch results after a specific sort value."),
    include_total_count: bool | None = Field(None, alias="includeTotalCount", description="Whether to include the total count of all matching context instances in the response (defaults to true)."),
    limit: int | None = Field(None, description="Maximum number of context instances to return in a single response, between 1 and 50 items (defaults to 20)."),
    sort: str | None = Field(None, description="Field to sort results by. Use `ts` for ascending timestamp order or `-ts` for descending timestamp order."),
    filter_: str | None = Field(None, alias="filter", description="Filter expression to narrow results by context attributes. Supports nested filter syntax for querying kindKeys, timestamps, and other context properties. See LaunchDarkly filtering documentation for syntax details."),
) -> dict[str, Any]:
    """Search for context instances within a specific project and environment using filters, sorting, and pagination. Supports advanced filtering syntax for querying context data across your application."""

    # Construct request model with validation
    try:
        _request = _models.SearchContextInstancesRequest(
            path=_models.SearchContextInstancesRequestPath(project_key=project_key, environment_key=environment_key),
            query=_models.SearchContextInstancesRequestQuery(continuation_token=continuation_token, include_total_count=include_total_count),
            body=_models.SearchContextInstancesRequestBody(limit=limit, sort=sort, filter_=filter_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_context_instances: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/environments/{environmentKey}/context-instances/search", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/environments/{environmentKey}/context-instances/search"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_context_instances")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_context_instances", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_context_instances",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Contexts
@mcp.tool()
async def get_context_instance(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the context instance."),
    environment_key: str = Field(..., alias="environmentKey", description="The unique identifier for the environment within the project."),
    id_: str = Field(..., alias="id", description="The unique identifier of the context instance to retrieve."),
    include_total_count: bool | None = Field(None, alias="includeTotalCount", description="Whether to include the total count of matching context instances in the response. Defaults to true if not specified."),
) -> dict[str, Any]:
    """Retrieve a specific context instance by its ID within a project and environment. Returns detailed information about the context instance configuration."""

    # Construct request model with validation
    try:
        _request = _models.GetContextInstancesRequest(
            path=_models.GetContextInstancesRequestPath(project_key=project_key, environment_key=environment_key, id_=id_),
            query=_models.GetContextInstancesRequestQuery(include_total_count=include_total_count)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_context_instance: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/environments/{environmentKey}/context-instances/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/environments/{environmentKey}/context-instances/{id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_context_instance")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_context_instance", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_context_instance",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Contexts
@mcp.tool()
async def delete_context_instance(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the context instance to delete."),
    environment_key: str = Field(..., alias="environmentKey", description="The unique identifier for the environment within the project where the context instance is located."),
    id_: str = Field(..., alias="id", description="The unique identifier of the context instance to delete."),
) -> dict[str, Any]:
    """Delete a specific context instance by its ID within a project environment. This operation permanently removes the context instance and cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteContextInstancesRequest(
            path=_models.DeleteContextInstancesRequestPath(project_key=project_key, environment_key=environment_key, id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_context_instance: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/environments/{environmentKey}/context-instances/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/environments/{environmentKey}/context-instances/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_context_instance")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_context_instance", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_context_instance",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Contexts
@mcp.tool()
async def search_contexts(
    project_key: str = Field(..., alias="projectKey", description="The project key that identifies the LaunchDarkly project containing the environment to search."),
    environment_key: str = Field(..., alias="environmentKey", description="The environment key that identifies the specific environment within the project where contexts will be searched."),
    include_total_count: bool | None = Field(None, alias="includeTotalCount", description="Whether to include the total count of all matching contexts in the response. Defaults to true if not specified."),
    limit: int | None = Field(None, description="Maximum number of contexts to return in the response. Accepts values up to 50, with a default of 20 if not specified."),
    sort: str | None = Field(None, description="Field to sort results by. Use 'ts' for ascending chronological order or '-ts' for descending order by timestamp."),
    filter_: str | None = Field(None, alias="filter", description="Filter expression to narrow results by context attributes and kinds. Supports multiple conditions using operators like 'startsWith' and 'anyOf', separated by commas."),
) -> dict[str, Any]:
    """Search for contexts in a LaunchDarkly environment using filters, sorting, and pagination. Supports advanced filtering by context attributes and kinds to find specific contexts matching your criteria."""

    # Construct request model with validation
    try:
        _request = _models.SearchContextsRequest(
            path=_models.SearchContextsRequestPath(project_key=project_key, environment_key=environment_key),
            query=_models.SearchContextsRequestQuery(include_total_count=include_total_count),
            body=_models.SearchContextsRequestBody(limit=limit, sort=sort, filter_=filter_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_contexts: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/environments/{environmentKey}/contexts/search", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/environments/{environmentKey}/contexts/search"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_contexts")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_contexts", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_contexts",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Context settings
@mcp.tool()
async def update_flag_setting_for_context(
    project_key: str = Field(..., alias="projectKey", description="The project key that contains the feature flag."),
    environment_key: str = Field(..., alias="environmentKey", description="The environment key where the flag setting applies."),
    context_kind: str = Field(..., alias="contextKind", description="The context kind (e.g., 'user', 'organization') that categorizes the context."),
    context_key: str = Field(..., alias="contextKey", description="The unique identifier for the context within its kind."),
    feature_flag_key: str = Field(..., alias="featureFlagKey", description="The key of the feature flag to update."),
    setting: Any | None = Field(None, description="The variation value to assign to this context. Must match the flag's variation type (e.g., true/false for boolean flags, a string value for string flags). Omit or set to null to remove the context's flag setting."),
) -> dict[str, Any]:
    """Set or clear a feature flag's variation value for a specific context. Omit or set `setting` to null to erase the current setting; otherwise, provide a variation value matching the flag's type (e.g., boolean, string)."""

    # Construct request model with validation
    try:
        _request = _models.PutContextFlagSettingRequest(
            path=_models.PutContextFlagSettingRequestPath(project_key=project_key, environment_key=environment_key, context_kind=context_kind, context_key=context_key, feature_flag_key=feature_flag_key),
            body=_models.PutContextFlagSettingRequestBody(setting=setting)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_flag_setting_for_context: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/environments/{environmentKey}/contexts/{contextKind}/{contextKey}/flags/{featureFlagKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/environments/{environmentKey}/contexts/{contextKind}/{contextKey}/flags/{featureFlagKey}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_flag_setting_for_context")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_flag_setting_for_context", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_flag_setting_for_context",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Contexts
@mcp.tool()
async def get_context(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the context."),
    environment_key: str = Field(..., alias="environmentKey", description="The unique identifier for the environment within the project."),
    kind: str = Field(..., description="The category or type of context (e.g., 'user', 'organization', 'device')."),
    key: str = Field(..., description="The unique identifier for the specific context instance within its kind."),
    include_total_count: bool | None = Field(None, alias="includeTotalCount", description="Whether to include the total count of matching contexts in the response. Defaults to true if not specified."),
) -> dict[str, Any]:
    """Retrieve a specific context by its kind and key within a project environment. Contexts are used to segment user data and targeting rules."""

    # Construct request model with validation
    try:
        _request = _models.GetContextsRequest(
            path=_models.GetContextsRequestPath(project_key=project_key, environment_key=environment_key, kind=kind, key=key),
            query=_models.GetContextsRequestQuery(include_total_count=include_total_count)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_context: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/environments/{environmentKey}/contexts/{kind}/{key}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/environments/{environmentKey}/contexts/{kind}/{key}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_context")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_context", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_context",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Experiments
@mcp.tool()
async def list_experiments(
    project_key: str = Field(..., alias="projectKey", description="The project key that identifies the LaunchDarkly project containing the experiments."),
    environment_key: str = Field(..., alias="environmentKey", description="The environment key that identifies the specific environment within the project where experiments are located."),
    lifecycle_state: str | None = Field(None, alias="lifecycleState", description="A comma-separated list specifying which experiment states to include in results. Valid values are `archived`, `active`, or both. Defaults to returning only active experiments if not specified."),
) -> dict[str, Any]:
    """Retrieve all experiments in an environment with optional filtering by flag, metric, or iteration status, and optional expansion of related data such as iterations, metrics, treatments, and analysis configuration."""

    # Construct request model with validation
    try:
        _request = _models.GetExperimentsRequest(
            path=_models.GetExperimentsRequestPath(project_key=project_key, environment_key=environment_key),
            query=_models.GetExperimentsRequestQuery(lifecycle_state=lifecycle_state)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_experiments: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/environments/{environmentKey}/experiments", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/environments/{environmentKey}/experiments"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_experiments")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_experiments", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_experiments",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Experiments
@mcp.tool()
async def create_experiment(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the LaunchDarkly project where the experiment will be created."),
    environment_key: str = Field(..., alias="environmentKey", description="The unique identifier for the environment within the project where the experiment will run."),
    name: str = Field(..., description="A human-readable name for the experiment that describes its purpose."),
    key: str = Field(..., description="A unique identifier for the experiment, used in API calls and references. Must be URL-safe."),
    hypothesis: str = Field(..., description="A clear statement of the expected outcome or business hypothesis being tested by this experiment."),
    metrics: list[_models.MetricInput] = Field(..., description="Array of metric objects defining which metrics will be measured and analyzed for this experiment. Each metric specifies how success is measured."),
    treatments: list[_models.TreatmentInput] = Field(..., description="Array of treatment objects defining the variations being tested. Each treatment corresponds to a feature flag variation."),
    flags: dict[str, _models.FlagInput] = Field(..., description="Object containing the feature flag key and targeting rules that determine which users see which variations in this iteration."),
    can_reshuffle_traffic: bool | None = Field(None, alias="canReshuffleTraffic", description="Whether traffic can be reassigned to different variations when audience size changes. Defaults to true, allowing dynamic reallocation."),
    primary_single_metric_key: str | None = Field(None, alias="primarySingleMetricKey", description="The key of the primary metric to analyze. Either this or `primaryFunnelKey` must be specified, but not both."),
    primary_funnel_key: str | None = Field(None, alias="primaryFunnelKey", description="The key of the primary funnel group (multi-step metric) to analyze. Either this or `primarySingleMetricKey` must be specified, but not both."),
    randomization_unit: str | None = Field(None, alias="randomizationUnit", description="The unit used to consistently assign users to variations (e.g., 'user', 'account', 'organization'). Defaults to 'user'."),
    reallocation_frequency_millis: int | None = Field(None, alias="reallocationFrequencyMillis", description="For multi-armed bandit experiments, the frequency in milliseconds at which traffic allocation is automatically rebalanced across variations based on performance."),
    covariate_id: str | None = Field(None, alias="covariateId", description="The identifier of an uploaded covariate CSV file used to adjust analysis for known variables that may affect results."),
    attributes: list[str] | None = Field(None, description="Array of attribute names (e.g., 'country', 'device', 'os') that can be used to segment and analyze experiment results by user characteristics."),
    holdout_id: str | None = Field(None, alias="holdoutId", description="The identifier of a holdout group to exclude from the experiment while measuring their metrics separately for comparison."),
    tags: list[str] | None = Field(None, description="Array of tags for organizing and categorizing the experiment for easier discovery and management."),
    methodology: Literal["bayesian", "frequentist", "export_only"] | None = Field(None, description="The statistical methodology for analyzing results: 'bayesian' (default) uses probability-based analysis, 'frequentist' uses traditional hypothesis testing, or 'export_only' for external analysis."),
    bayesian_threshold: str | None = Field(None, alias="bayesianThreshold", description="For Bayesian analysis, the probability threshold (as a percentage) for determining if a variation is likely better than the baseline. Higher values require stronger evidence."),
    significance_threshold: str | None = Field(None, alias="significanceThreshold", description="For Frequentist analysis, the significance threshold (as a percentage) for statistical significance. Typical values are 5 for 95% confidence."),
    test_direction: str | None = Field(None, alias="testDirection", description="For Frequentist analysis, whether the test is one-sided (directional) or two-sided (non-directional) when comparing variations to baseline."),
    multiple_comparison_correction_method: Literal["bonferroni", "benjamini-hochberg"] | None = Field(None, alias="multipleComparisonCorrectionMethod", description="Method to correct for multiple comparisons in Frequentist analysis: 'bonferroni' is conservative, 'benjamini-hochberg' is less conservative."),
    multiple_comparison_correction_scope: Literal["variations", "variations-and-metrics", "metrics"] | None = Field(None, alias="multipleComparisonCorrectionScope", description="Scope of multiple comparison correction: 'variations' corrects across variations only, 'metrics' corrects across metrics only, or 'variations-and-metrics' corrects across both."),
    sequential_testing_enabled: bool | None = Field(None, alias="sequentialTestingEnabled", description="Whether to enable sequential testing for Frequentist analysis, allowing results to be checked at interim points rather than only at the end."),
    data_source: Literal["launchdarkly", "snowflake"] | None = Field(None, alias="dataSource", description="The source system for metric data analysis: 'launchdarkly' (default) uses LaunchDarkly's event data, 'snowflake' or 'databricks' connect to external data warehouses."),
) -> dict[str, Any]:
    """Create a new experiment in a LaunchDarkly project environment. After creation, you must create an iteration and update the experiment with the `startIteration` instruction to run it."""

    # Construct request model with validation
    try:
        _request = _models.CreateExperimentRequest(
            path=_models.CreateExperimentRequestPath(project_key=project_key, environment_key=environment_key),
            body=_models.CreateExperimentRequestBody(name=name, key=key, holdout_id=holdout_id, tags=tags, methodology=methodology, data_source=data_source,
                iteration=_models.CreateExperimentRequestBodyIteration(hypothesis=hypothesis, can_reshuffle_traffic=can_reshuffle_traffic, metrics=metrics, primary_single_metric_key=primary_single_metric_key, primary_funnel_key=primary_funnel_key, treatments=treatments, flags=flags, randomization_unit=randomization_unit, reallocation_frequency_millis=reallocation_frequency_millis, covariate_id=covariate_id, attributes=attributes),
                analysis_config=_models.CreateExperimentRequestBodyAnalysisConfig(bayesian_threshold=bayesian_threshold, significance_threshold=significance_threshold, test_direction=test_direction, multiple_comparison_correction_method=multiple_comparison_correction_method, multiple_comparison_correction_scope=multiple_comparison_correction_scope, sequential_testing_enabled=sequential_testing_enabled) if any(v is not None for v in [bayesian_threshold, significance_threshold, test_direction, multiple_comparison_correction_method, multiple_comparison_correction_scope, sequential_testing_enabled]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_experiment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/environments/{environmentKey}/experiments", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/environments/{environmentKey}/experiments"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_experiment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_experiment", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_experiment",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Experiments
@mcp.tool()
async def get_experiment(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the LaunchDarkly project containing the experiment."),
    environment_key: str = Field(..., alias="environmentKey", description="The unique identifier for the environment where the experiment is running."),
    experiment_key: str = Field(..., alias="experimentKey", description="The unique identifier for the experiment to retrieve. Use the optional `expand` query parameter to include additional fields such as previousIterations, draftIteration, secondaryMetrics, treatments, or analysisConfig in the response."),
) -> dict[str, Any]:
    """Retrieve detailed information about a specific experiment in a LaunchDarkly project environment. Optionally expand the response to include iterations, metrics, treatments, and analysis configuration."""

    # Construct request model with validation
    try:
        _request = _models.GetExperimentRequest(
            path=_models.GetExperimentRequestPath(project_key=project_key, environment_key=environment_key, experiment_key=experiment_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_experiment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/environments/{environmentKey}/experiments/{experimentKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/environments/{environmentKey}/experiments/{experimentKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_experiment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_experiment", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_experiment",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Experiments
@mcp.tool()
async def update_experiment(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the experiment."),
    environment_key: str = Field(..., alias="environmentKey", description="The unique identifier for the environment where the experiment exists."),
    experiment_key: str = Field(..., alias="experimentKey", description="The unique identifier for the experiment to update."),
    instructions: list[_models.Instruction] = Field(..., description="An array of semantic patch instructions to apply to the experiment. Each instruction is an object with a `kind` field specifying the operation (updateName, updateDescription, startIteration, stopIteration, archiveExperiment, or restoreExperiment) and optional parameters like `value`, `changeJustification`, `winningTreatmentId`, or `winningReason` depending on the instruction type."),
) -> dict[str, Any]:
    """Update an experiment using semantic patch instructions. Supports operations like renaming, updating descriptions, managing iterations, and archiving experiments."""

    # Construct request model with validation
    try:
        _request = _models.PatchExperimentRequest(
            path=_models.PatchExperimentRequestPath(project_key=project_key, environment_key=environment_key, experiment_key=experiment_key),
            body=_models.PatchExperimentRequestBody(instructions=instructions)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_experiment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/environments/{environmentKey}/experiments/{experimentKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/environments/{environmentKey}/experiments/{experimentKey}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_experiment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_experiment", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_experiment",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Follow flags
@mcp.tool()
async def list_flag_followers_by_project_environment(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the flags and environment."),
    environment_key: str = Field(..., alias="environmentKey", description="The unique identifier for the environment within the project where you want to retrieve flag followers."),
) -> dict[str, Any]:
    """Retrieve all followers across feature flags within a specific project and environment. This returns the list of users or teams monitoring flag changes in that environment."""

    # Construct request model with validation
    try:
        _request = _models.GetFollowersByProjEnvRequest(
            path=_models.GetFollowersByProjEnvRequestPath(project_key=project_key, environment_key=environment_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_flag_followers_by_project_environment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/environments/{environmentKey}/followers", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/environments/{environmentKey}/followers"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_flag_followers_by_project_environment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_flag_followers_by_project_environment", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_flag_followers_by_project_environment",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Environments
@mcp.tool()
async def reset_mobile_key_for_environment(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the environment."),
    environment_key: str = Field(..., alias="environmentKey", description="The unique identifier for the environment whose mobile SDK key should be reset."),
) -> dict[str, Any]:
    """Reset an environment's mobile SDK key, immediately expiring the previous key. This operation generates a new mobile key for the specified environment within a project."""

    # Construct request model with validation
    try:
        _request = _models.ResetEnvironmentMobileKeyRequest(
            path=_models.ResetEnvironmentMobileKeyRequestPath(project_key=project_key, environment_key=environment_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for reset_mobile_key_for_environment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/environments/{environmentKey}/mobileKey", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/environments/{environmentKey}/mobileKey"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("reset_mobile_key_for_environment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("reset_mobile_key_for_environment", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="reset_mobile_key_for_environment",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Segments
@mcp.tool()
async def evaluate_context_instance_segment_memberships(
    project_key: str = Field(..., alias="projectKey", description="The project key that identifies the LaunchDarkly project. This is a string identifier used to scope the operation within your workspace."),
    environment_key: str = Field(..., alias="environmentKey", description="The environment key that identifies the specific environment within the project. This determines which segment definitions and rules are evaluated."),
    body: dict[str, Any] = Field(..., description="The context instance to evaluate. Must include a unique key identifier, a kind (e.g., 'user', 'organization'), and any custom attributes relevant to segment rules (e.g., name, jobFunction, address). The structure supports nested objects for complex attributes."),
) -> dict[str, Any]:
    """Evaluate which segments a context instance belongs to based on its attributes. Provide a context instance with its key, kind, and custom attributes to retrieve membership status across all segments in the environment."""

    # Construct request model with validation
    try:
        _request = _models.GetContextInstanceSegmentsMembershipByEnvRequest(
            path=_models.GetContextInstanceSegmentsMembershipByEnvRequestPath(project_key=project_key, environment_key=environment_key),
            body=_models.GetContextInstanceSegmentsMembershipByEnvRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for evaluate_context_instance_segment_memberships: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/environments/{environmentKey}/segments/evaluate", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/environments/{environmentKey}/segments/evaluate"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("evaluate_context_instance_segment_memberships")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("evaluate_context_instance_segment_memberships", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="evaluate_context_instance_segment_memberships",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Experiments
@mcp.tool()
async def get_experimentation_settings(project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project whose experimentation settings you want to retrieve.")) -> dict[str, Any]:
    """Retrieve the current experimentation settings configured for a specific project. This includes all active experimentation policies and configurations."""

    # Construct request model with validation
    try:
        _request = _models.GetExperimentationSettingsRequest(
            path=_models.GetExperimentationSettingsRequestPath(project_key=project_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_experimentation_settings: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/experimentation-settings", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/experimentation-settings"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_experimentation_settings")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_experimentation_settings", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_experimentation_settings",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Experiments
@mcp.tool()
async def update_experimentation_settings(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project whose experimentation settings should be updated."),
    randomization_units: list[_models.RandomizationUnitInput] = Field(..., alias="randomizationUnits", description="An array of randomization units that are permitted for experiments in this project. Each unit defines how experiment subjects are randomly assigned to variations."),
) -> dict[str, Any]:
    """Update the experimentation settings for a project, including the randomization units that are allowed for running experiments."""

    # Construct request model with validation
    try:
        _request = _models.PutExperimentationSettingsRequest(
            path=_models.PutExperimentationSettingsRequestPath(project_key=project_key),
            body=_models.PutExperimentationSettingsRequestBody(randomization_units=randomization_units)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_experimentation_settings: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/experimentation-settings", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/experimentation-settings"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_experimentation_settings")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_experimentation_settings", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_experimentation_settings",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Experiments
@mcp.tool()
async def list_experiments_project(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project from which to retrieve experiments."),
    lifecycle_state: str | None = Field(None, alias="lifecycleState", description="Filter experiments by lifecycle state using a comma-separated list. Valid values are `active`, `archived`, or both. Defaults to `active` experiments only if not specified."),
) -> dict[str, Any]:
    """Retrieve a list of experiments across all environments in a project, optionally filtered by lifecycle state (active, archived, or both)."""

    # Construct request model with validation
    try:
        _request = _models.GetExperimentsAnyEnvRequest(
            path=_models.GetExperimentsAnyEnvRequestPath(project_key=project_key),
            query=_models.GetExperimentsAnyEnvRequestQuery(lifecycle_state=lifecycle_state)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_experiments_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/experiments", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/experiments"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_experiments_project")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_experiments_project", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_experiments_project",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def get_flag_defaults_for_project(project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project. Used to scope the flag defaults to a specific project.")) -> dict[str, Any]:
    """Retrieve the default flag settings configured for a specific project. These defaults apply to feature flags within the project unless overridden at a more granular level."""

    # Construct request model with validation
    try:
        _request = _models.GetFlagDefaultsByProjectRequest(
            path=_models.GetFlagDefaultsByProjectRequestPath(project_key=project_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_flag_defaults_for_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/flag-defaults", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/flag-defaults"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_flag_defaults_for_project")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_flag_defaults_for_project", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_flag_defaults_for_project",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def update_flag_defaults_for_project(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project where flag defaults will be applied."),
    tags: list[str] = Field(..., description="A list of default tag labels to automatically assign to each new flag created in this project. Tags help organize and categorize flags."),
    temporary: bool = Field(..., description="Whether newly created flags should be marked as temporary by default, indicating they are intended for short-term use."),
    true_display_name: str = Field(..., alias="trueDisplayName", description="The display name shown in the LaunchDarkly UI for the true variation of flags (e.g., 'On', 'Enabled', 'True')."),
    false_display_name: str = Field(..., alias="falseDisplayName", description="The display name shown in the LaunchDarkly UI for the false variation of flags (e.g., 'Off', 'Disabled', 'False')."),
    true_description: str = Field(..., alias="trueDescription", description="A description explaining the purpose or behavior of the true variation, displayed in the LaunchDarkly UI."),
    false_description: str = Field(..., alias="falseDescription", description="A description explaining the purpose or behavior of the false variation, displayed in the LaunchDarkly UI."),
    on_variation: int = Field(..., alias="onVariation", description="The index (0 or 1) of the variation to serve when flag targeting is enabled and no rules match the target."),
    off_variation: int = Field(..., alias="offVariation", description="The index (0 or 1) of the variation to serve when flag targeting is disabled."),
    using_mobile_key: bool = Field(..., alias="usingMobileKey", description="Whether flags should be available to mobile SDKs by default."),
    using_environment_id: bool = Field(..., alias="usingEnvironmentId", description="Whether flags should be available to client-side SDKs by default."),
) -> dict[str, Any]:
    """Set default configuration values for all feature flags created in a project, including naming conventions, targeting behavior, and SDK availability."""

    # Construct request model with validation
    try:
        _request = _models.PutFlagDefaultsByProjectRequest(
            path=_models.PutFlagDefaultsByProjectRequestPath(project_key=project_key),
            body=_models.PutFlagDefaultsByProjectRequestBody(tags=tags, temporary=temporary,
                boolean_defaults=_models.PutFlagDefaultsByProjectRequestBodyBooleanDefaults(true_display_name=true_display_name, false_display_name=false_display_name, true_description=true_description, false_description=false_description, on_variation=on_variation, off_variation=off_variation),
                default_client_side_availability=_models.PutFlagDefaultsByProjectRequestBodyDefaultClientSideAvailability(using_mobile_key=using_mobile_key, using_environment_id=using_environment_id))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_flag_defaults_for_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/flag-defaults", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/flag-defaults"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_flag_defaults_for_project")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_flag_defaults_for_project", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_flag_defaults_for_project",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def update_flag_defaults_for_project_partial(
    project_key: str = Field(..., alias="projectKey", description="The project key that uniquely identifies the project containing the flag defaults to update."),
    body: list[_models.PatchOperation] = Field(..., description="An array of patch operations following RFC 6902 (JSON Patch) or RFC 7386 (JSON Merge Patch) format, specifying the changes to apply to the flag defaults."),
) -> dict[str, Any]:
    """Update flag defaults for a project using JSON patch or JSON merge patch operations. This allows you to modify default flag configurations applied across the project."""

    # Construct request model with validation
    try:
        _request = _models.PatchFlagDefaultsByProjectRequest(
            path=_models.PatchFlagDefaultsByProjectRequestPath(project_key=project_key),
            body=_models.PatchFlagDefaultsByProjectRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_flag_defaults_for_project_partial: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/flag-defaults", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/flag-defaults"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_flag_defaults_for_project_partial")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_flag_defaults_for_project_partial", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_flag_defaults_for_project_partial",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Approvals
@mcp.tool()
async def list_approval_requests_for_flag(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the feature flag."),
    feature_flag_key: str = Field(..., alias="featureFlagKey", description="The unique identifier for the feature flag to retrieve approval requests for."),
    environment_key: str = Field(..., alias="environmentKey", description="The unique identifier for the environment in which to list approval requests."),
) -> dict[str, Any]:
    """Retrieve all pending approval requests for a feature flag in a specific environment. Use this to review changes awaiting approval before they can be deployed."""

    # Construct request model with validation
    try:
        _request = _models.GetApprovalsForFlagRequest(
            path=_models.GetApprovalsForFlagRequestPath(project_key=project_key, feature_flag_key=feature_flag_key, environment_key=environment_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_approval_requests_for_flag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/flags/{featureFlagKey}/environments/{environmentKey}/approval-requests", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/flags/{featureFlagKey}/environments/{environmentKey}/approval-requests"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_approval_requests_for_flag")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_approval_requests_for_flag", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_approval_requests_for_flag",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Approvals
@mcp.tool()
async def create_approval_request_for_feature_flag(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the LaunchDarkly project containing the feature flag."),
    feature_flag_key: str = Field(..., alias="featureFlagKey", description="The unique identifier for the feature flag that requires approval for changes."),
    environment_key: str = Field(..., alias="environmentKey", description="The unique identifier for the environment where the flag changes will be applied."),
    description: str = Field(..., description="A concise summary of the requested changes to the feature flag, helping reviewers understand the intent of the approval request."),
    instructions: list[_models.Instruction] = Field(..., description="An ordered list of semantic patch instructions that define the exact changes to apply to the feature flag. Instructions must follow the semantic patch format documented in the feature flag update API."),
    execution_date: str | None = Field(None, alias="executionDate", description="Optional Unix timestamp (in milliseconds) specifying when the approval request instructions should be automatically executed. If omitted, execution occurs immediately upon approval."),
    operating_on_id: str | None = Field(None, alias="operatingOnId", description="The ID of an existing scheduled change, required only if your instructions modify or delete a previously scheduled change to the flag."),
    integration_config: dict[str, Any] | None = Field(None, alias="integrationConfig", description="Optional custom fields for third-party approval system integrations. Field definitions are provided in the integration's manifest.json file in the LaunchDarkly integration framework repository."),
) -> dict[str, Any]:
    """Submit an approval request to modify a feature flag in a specific environment. The request includes semantic patch instructions that will be applied upon approval, with optional scheduling and third-party integration metadata."""

    _execution_date = _parse_int(execution_date)

    # Construct request model with validation
    try:
        _request = _models.PostApprovalRequestForFlagRequest(
            path=_models.PostApprovalRequestForFlagRequestPath(project_key=project_key, feature_flag_key=feature_flag_key, environment_key=environment_key),
            body=_models.PostApprovalRequestForFlagRequestBody(description=description, instructions=instructions, execution_date=_execution_date, operating_on_id=operating_on_id, integration_config=integration_config)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_approval_request_for_feature_flag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/flags/{featureFlagKey}/environments/{environmentKey}/approval-requests", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/flags/{featureFlagKey}/environments/{environmentKey}/approval-requests"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_approval_request_for_feature_flag")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_approval_request_for_feature_flag", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_approval_request_for_feature_flag",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Approvals
@mcp.tool()
async def create_flag_copy_approval_request(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the feature flag."),
    feature_flag_key: str = Field(..., alias="featureFlagKey", description="The unique identifier for the feature flag whose configuration will be copied."),
    environment_key: str = Field(..., alias="environmentKey", description="The unique identifier for the target environment where the flag configuration will be copied to."),
    description: str = Field(..., description="A brief summary explaining the purpose of this configuration copy request (e.g., 'copy flag settings to another environment')."),
    key: str = Field(..., description="The unique identifier for the source environment from which the flag configuration will be copied."),
    included_actions: list[Literal["updateOn", "updateFallthrough", "updateOffVariation", "updateRules", "updateTargets", "updatePrerequisites"]] | None = Field(None, alias="includedActions", description="Optional list of specific flag changes to copy from source to target environment (e.g., 'updateOn'). You may specify either included or excluded actions, but not both. If omitted, all flag changes will be copied."),
) -> dict[str, Any]:
    """Create an approval request to copy a feature flag's configuration from a source environment to a target environment. This allows controlled promotion of flag settings across your deployment environments."""

    # Construct request model with validation
    try:
        _request = _models.PostFlagCopyConfigApprovalRequest(
            path=_models.PostFlagCopyConfigApprovalRequestPath(project_key=project_key, feature_flag_key=feature_flag_key, environment_key=environment_key),
            body=_models.PostFlagCopyConfigApprovalRequestBody(description=description, included_actions=included_actions,
                source=_models.PostFlagCopyConfigApprovalRequestBodySource(key=key))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_flag_copy_approval_request: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/flags/{featureFlagKey}/environments/{environmentKey}/approval-requests-flag-copy", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/flags/{featureFlagKey}/environments/{environmentKey}/approval-requests-flag-copy"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_flag_copy_approval_request")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_flag_copy_approval_request", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_flag_copy_approval_request",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Approvals
@mcp.tool()
async def get_approval_request_for_flag(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the feature flag."),
    feature_flag_key: str = Field(..., alias="featureFlagKey", description="The unique identifier for the feature flag associated with this approval request."),
    environment_key: str = Field(..., alias="environmentKey", description="The unique identifier for the environment where the approval request applies."),
    id_: str = Field(..., alias="id", description="The unique identifier for the specific approval request to retrieve."),
) -> dict[str, Any]:
    """Retrieve a specific approval request for a feature flag in a given environment. Use this to check the status and details of a pending or completed approval workflow."""

    # Construct request model with validation
    try:
        _request = _models.GetApprovalForFlagRequest(
            path=_models.GetApprovalForFlagRequestPath(project_key=project_key, feature_flag_key=feature_flag_key, environment_key=environment_key, id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_approval_request_for_flag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/flags/{featureFlagKey}/environments/{environmentKey}/approval-requests/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/flags/{featureFlagKey}/environments/{environmentKey}/approval-requests/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_approval_request_for_flag")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_approval_request_for_flag", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_approval_request_for_flag",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Approvals
@mcp.tool()
async def delete_approval_request_for_flag(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the feature flag."),
    feature_flag_key: str = Field(..., alias="featureFlagKey", description="The unique identifier for the feature flag associated with the approval request."),
    environment_key: str = Field(..., alias="environmentKey", description="The unique identifier for the environment where the approval request applies."),
    id_: str = Field(..., alias="id", description="The unique identifier of the approval request to delete."),
) -> dict[str, Any]:
    """Delete a pending approval request for a feature flag in a specific environment. This removes the approval workflow, preventing further review or approval actions on the request."""

    # Construct request model with validation
    try:
        _request = _models.DeleteApprovalRequestForFlagRequest(
            path=_models.DeleteApprovalRequestForFlagRequestPath(project_key=project_key, feature_flag_key=feature_flag_key, environment_key=environment_key, id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_approval_request_for_flag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/flags/{featureFlagKey}/environments/{environmentKey}/approval-requests/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/flags/{featureFlagKey}/environments/{environmentKey}/approval-requests/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_approval_request_for_flag")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_approval_request_for_flag", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_approval_request_for_flag",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Approvals
@mcp.tool()
async def apply_approval_request_for_flag(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the feature flag."),
    feature_flag_key: str = Field(..., alias="featureFlagKey", description="The unique identifier for the feature flag associated with the approval request."),
    environment_key: str = Field(..., alias="environmentKey", description="The unique identifier for the environment where the approval request will be applied."),
    id_: str = Field(..., alias="id", description="The unique identifier for the approval request to apply. The request must have been previously approved before it can be applied."),
) -> dict[str, Any]:
    """Apply an approval request that has been approved for a feature flag in a specific environment. This executes the changes specified in the approval request."""

    # Construct request model with validation
    try:
        _request = _models.PostApprovalRequestApplyForFlagRequest(
            path=_models.PostApprovalRequestApplyForFlagRequestPath(project_key=project_key, feature_flag_key=feature_flag_key, environment_key=environment_key, id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for apply_approval_request_for_flag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/flags/{featureFlagKey}/environments/{environmentKey}/approval-requests/{id}/apply", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/flags/{featureFlagKey}/environments/{environmentKey}/approval-requests/{id}/apply"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("apply_approval_request_for_flag")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("apply_approval_request_for_flag", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="apply_approval_request_for_flag",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Approvals
@mcp.tool()
async def review_approval_request_for_flag(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the feature flag."),
    feature_flag_key: str = Field(..., alias="featureFlagKey", description="The unique identifier for the feature flag being reviewed."),
    environment_key: str = Field(..., alias="environmentKey", description="The unique identifier for the environment where the approval request applies."),
    id_: str = Field(..., alias="id", description="The unique identifier for the approval request being reviewed."),
    kind: Literal["approve", "comment", "decline"] | None = Field(None, description="The type of review action: approve to accept the changes, decline to reject them, or comment to provide feedback without a final decision."),
) -> dict[str, Any]:
    """Submit a review decision on a pending approval request for a feature flag, either approving, declining, or commenting on the proposed changes."""

    # Construct request model with validation
    try:
        _request = _models.PostApprovalRequestReviewForFlagRequest(
            path=_models.PostApprovalRequestReviewForFlagRequestPath(project_key=project_key, feature_flag_key=feature_flag_key, environment_key=environment_key, id_=id_),
            body=_models.PostApprovalRequestReviewForFlagRequestBody(kind=kind)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for review_approval_request_for_flag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/flags/{featureFlagKey}/environments/{environmentKey}/approval-requests/{id}/reviews", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/flags/{featureFlagKey}/environments/{environmentKey}/approval-requests/{id}/reviews"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("review_approval_request_for_flag")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("review_approval_request_for_flag", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="review_approval_request_for_flag",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Follow flags
@mcp.tool()
async def list_flag_followers(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the feature flag."),
    feature_flag_key: str = Field(..., alias="featureFlagKey", description="The unique identifier for the feature flag whose followers you want to retrieve."),
    environment_key: str = Field(..., alias="environmentKey", description="The unique identifier for the environment in which to retrieve flag followers."),
) -> dict[str, Any]:
    """Retrieve a list of team members who are following a specific feature flag within a project and environment. This helps identify who is monitoring changes to the flag."""

    # Construct request model with validation
    try:
        _request = _models.GetFlagFollowersRequest(
            path=_models.GetFlagFollowersRequestPath(project_key=project_key, feature_flag_key=feature_flag_key, environment_key=environment_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_flag_followers: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/flags/{featureFlagKey}/environments/{environmentKey}/followers", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/flags/{featureFlagKey}/environments/{environmentKey}/followers"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_flag_followers")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_flag_followers", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_flag_followers",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Follow flags
@mcp.tool()
async def add_flag_follower(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the feature flag."),
    feature_flag_key: str = Field(..., alias="featureFlagKey", description="The unique identifier for the feature flag to follow."),
    environment_key: str = Field(..., alias="environmentKey", description="The unique identifier for the environment where the flag follower relationship applies."),
    member_id: str = Field(..., alias="memberId", description="The unique identifier of the team member to add as a follower. Members with reader-level permissions can only add themselves, while higher-privileged members can add any team member."),
) -> dict[str, Any]:
    """Subscribe a team member to receive updates about a feature flag's changes in a specific project and environment. Members with reader roles can only add themselves as followers."""

    # Construct request model with validation
    try:
        _request = _models.PutFlagFollowerRequest(
            path=_models.PutFlagFollowerRequestPath(project_key=project_key, feature_flag_key=feature_flag_key, environment_key=environment_key, member_id=member_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_flag_follower: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/flags/{featureFlagKey}/environments/{environmentKey}/followers/{memberId}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/flags/{featureFlagKey}/environments/{environmentKey}/followers/{memberId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_flag_follower")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_flag_follower", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_flag_follower",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Follow flags
@mcp.tool()
async def remove_flag_follower(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the feature flag."),
    feature_flag_key: str = Field(..., alias="featureFlagKey", description="The unique identifier for the feature flag from which to remove the follower."),
    environment_key: str = Field(..., alias="environmentKey", description="The unique identifier for the environment where the flag follower relationship exists."),
    member_id: str = Field(..., alias="memberId", description="The unique identifier of the member to remove as a follower. Members with reader roles can only remove themselves; other roles can remove any member."),
) -> dict[str, Any]:
    """Remove a member as a follower of a feature flag in a specific project and environment. Members with reader roles can only remove themselves as followers."""

    # Construct request model with validation
    try:
        _request = _models.DeleteFlagFollowerRequest(
            path=_models.DeleteFlagFollowerRequestPath(project_key=project_key, feature_flag_key=feature_flag_key, environment_key=environment_key, member_id=member_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_flag_follower: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/flags/{featureFlagKey}/environments/{environmentKey}/followers/{memberId}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/flags/{featureFlagKey}/environments/{environmentKey}/followers/{memberId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_flag_follower")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_flag_follower", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_flag_follower",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Scheduled changes
@mcp.tool()
async def list_scheduled_changes_for_flag(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the feature flag."),
    feature_flag_key: str = Field(..., alias="featureFlagKey", description="The unique identifier for the feature flag whose scheduled changes you want to retrieve."),
    environment_key: str = Field(..., alias="environmentKey", description="The unique identifier for the environment in which to list scheduled changes for the feature flag."),
) -> dict[str, Any]:
    """Retrieve all scheduled changes pending application to a feature flag in a specific environment. This shows future modifications that will be automatically applied at their scheduled times."""

    # Construct request model with validation
    try:
        _request = _models.GetFlagConfigScheduledChangesRequest(
            path=_models.GetFlagConfigScheduledChangesRequestPath(project_key=project_key, feature_flag_key=feature_flag_key, environment_key=environment_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_scheduled_changes_for_flag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/flags/{featureFlagKey}/environments/{environmentKey}/scheduled-changes", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/flags/{featureFlagKey}/environments/{environmentKey}/scheduled-changes"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_scheduled_changes_for_flag")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_scheduled_changes_for_flag", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_scheduled_changes_for_flag",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Scheduled changes
@mcp.tool()
async def create_scheduled_changes_for_flag(
    project_key: str = Field(..., alias="projectKey", description="The project key that contains the feature flag."),
    feature_flag_key: str = Field(..., alias="featureFlagKey", description="The feature flag key to schedule changes for."),
    environment_key: str = Field(..., alias="environmentKey", description="The environment key where the scheduled changes will be applied."),
    execution_date: str = Field(..., alias="executionDate", description="Unix timestamp (milliseconds) indicating when the scheduled changes should be executed."),
    instructions: list[_models.Instruction] = Field(..., description="Array containing a single object with `kind: \"scheduled_action\"` and semantic patch instructions. Supported instructions are the same as those available when updating a feature flag directly."),
    ignore_conflicts: bool | None = Field(None, alias="ignoreConflicts", description="If true, the operation succeeds even when these instructions conflict with existing scheduled changes. If false (default), the operation fails on conflicts."),
) -> dict[str, Any]:
    """Schedule semantic patch instructions to be applied to a feature flag at a specified future date. Optionally allow the operation to succeed even if scheduled changes conflict with existing ones."""

    _execution_date = _parse_int(execution_date)

    # Construct request model with validation
    try:
        _request = _models.PostFlagConfigScheduledChangesRequest(
            path=_models.PostFlagConfigScheduledChangesRequestPath(project_key=project_key, feature_flag_key=feature_flag_key, environment_key=environment_key),
            query=_models.PostFlagConfigScheduledChangesRequestQuery(ignore_conflicts=ignore_conflicts),
            body=_models.PostFlagConfigScheduledChangesRequestBody(execution_date=_execution_date, instructions=instructions)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_scheduled_changes_for_flag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/flags/{featureFlagKey}/environments/{environmentKey}/scheduled-changes", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/flags/{featureFlagKey}/environments/{environmentKey}/scheduled-changes"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_scheduled_changes_for_flag")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_scheduled_changes_for_flag", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_scheduled_changes_for_flag",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Scheduled changes
@mcp.tool()
async def get_scheduled_change_for_feature_flag(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the feature flag."),
    feature_flag_key: str = Field(..., alias="featureFlagKey", description="The unique identifier for the feature flag associated with the scheduled change."),
    environment_key: str = Field(..., alias="environmentKey", description="The unique identifier for the environment where the scheduled change will be applied."),
    id_: str = Field(..., alias="id", description="The unique identifier for the scheduled change to retrieve."),
) -> dict[str, Any]:
    """Retrieve a specific scheduled change that will be applied to a feature flag in a given environment. Use this to inspect the details of a pending flag modification by its ID."""

    # Construct request model with validation
    try:
        _request = _models.GetFeatureFlagScheduledChangeRequest(
            path=_models.GetFeatureFlagScheduledChangeRequestPath(project_key=project_key, feature_flag_key=feature_flag_key, environment_key=environment_key, id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_scheduled_change_for_feature_flag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/flags/{featureFlagKey}/environments/{environmentKey}/scheduled-changes/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/flags/{featureFlagKey}/environments/{environmentKey}/scheduled-changes/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_scheduled_change_for_feature_flag")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_scheduled_change_for_feature_flag", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_scheduled_change_for_feature_flag",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Scheduled changes
@mcp.tool()
async def update_scheduled_flag_change(
    project_key: str = Field(..., alias="projectKey", description="The project key that contains the feature flag."),
    feature_flag_key: str = Field(..., alias="featureFlagKey", description="The feature flag key for which the scheduled change applies."),
    environment_key: str = Field(..., alias="environmentKey", description="The environment key where the scheduled change is configured."),
    id_: str = Field(..., alias="id", description="The unique identifier of the scheduled change to update."),
    instructions: list[_models.Instruction] = Field(..., description="An array of semantic patch instructions to apply. Each instruction is an object with a `kind` field specifying the operation (deleteScheduledChange, replaceScheduledChangesInstructions, or updateScheduledChangesExecutionDate). Some instructions require a `value` field with the new data."),
    ignore_conflicts: bool | None = Field(None, alias="ignoreConflicts", description="Set to `true` to allow the update even if new instructions conflict with existing scheduled changes, or `false` to reject conflicting updates. Defaults to `false`."),
) -> dict[str, Any]:
    """Update a scheduled flag change by replacing its instructions or execution date using semantic patch operations. Supports deleting the scheduled change, modifying its execution time, or changing the flag actions to be performed."""

    # Construct request model with validation
    try:
        _request = _models.PatchFlagConfigScheduledChangeRequest(
            path=_models.PatchFlagConfigScheduledChangeRequestPath(project_key=project_key, feature_flag_key=feature_flag_key, environment_key=environment_key, id_=id_),
            query=_models.PatchFlagConfigScheduledChangeRequestQuery(ignore_conflicts=ignore_conflicts),
            body=_models.PatchFlagConfigScheduledChangeRequestBody(instructions=instructions)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_scheduled_flag_change: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/flags/{featureFlagKey}/environments/{environmentKey}/scheduled-changes/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/flags/{featureFlagKey}/environments/{environmentKey}/scheduled-changes/{id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_scheduled_flag_change")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_scheduled_flag_change", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_scheduled_flag_change",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Scheduled changes
@mcp.tool()
async def delete_scheduled_flag_changes(
    project_key: str = Field(..., alias="projectKey", description="The project key that contains the feature flag. Used to scope the operation to a specific project."),
    feature_flag_key: str = Field(..., alias="featureFlagKey", description="The feature flag key identifying which flag's scheduled changes should be deleted."),
    environment_key: str = Field(..., alias="environmentKey", description="The environment key specifying which environment's scheduled changes workflow should be removed."),
    id_: str = Field(..., alias="id", description="The unique identifier of the scheduled changes workflow to delete."),
) -> dict[str, Any]:
    """Delete a scheduled changes workflow for a feature flag in a specific environment. This removes the pending scheduled changes and cancels any automation associated with the workflow."""

    # Construct request model with validation
    try:
        _request = _models.DeleteFlagConfigScheduledChangesRequest(
            path=_models.DeleteFlagConfigScheduledChangesRequestPath(project_key=project_key, feature_flag_key=feature_flag_key, environment_key=environment_key, id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_scheduled_flag_changes: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/flags/{featureFlagKey}/environments/{environmentKey}/scheduled-changes/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/flags/{featureFlagKey}/environments/{environmentKey}/scheduled-changes/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_scheduled_flag_changes")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_scheduled_flag_changes", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_scheduled_flag_changes",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Workflows
@mcp.tool()
async def list_workflows_for_feature_flag(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the feature flag."),
    feature_flag_key: str = Field(..., alias="featureFlagKey", description="The unique identifier for the feature flag whose workflows you want to retrieve."),
    environment_key: str = Field(..., alias="environmentKey", description="The unique identifier for the environment in which to retrieve workflows."),
    status: str | None = Field(None, description="Filter workflows by their current status. Supported values are `active` (ongoing workflows), `completed` (finished workflows), and `failed` (workflows that encountered errors). Omit to retrieve workflows of all statuses."),
) -> dict[str, Any]:
    """Retrieve all workflows associated with a feature flag in a specific environment. Optionally filter results by workflow status to view active, completed, or failed workflows."""

    # Construct request model with validation
    try:
        _request = _models.GetWorkflowsRequest(
            path=_models.GetWorkflowsRequestPath(project_key=project_key, feature_flag_key=feature_flag_key, environment_key=environment_key),
            query=_models.GetWorkflowsRequestQuery(status=status)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_workflows_for_feature_flag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/flags/{featureFlagKey}/environments/{environmentKey}/workflows", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/flags/{featureFlagKey}/environments/{environmentKey}/workflows"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_workflows_for_feature_flag")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_workflows_for_feature_flag", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_workflows_for_feature_flag",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Workflows
@mcp.tool()
async def get_custom_workflow(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the feature flag and workflow."),
    feature_flag_key: str = Field(..., alias="featureFlagKey", description="The unique identifier for the feature flag that contains the workflow."),
    environment_key: str = Field(..., alias="environmentKey", description="The unique identifier for the environment in which the workflow operates."),
    workflow_id: str = Field(..., alias="workflowId", description="The unique identifier of the specific workflow to retrieve."),
) -> dict[str, Any]:
    """Retrieve a specific custom workflow by its ID within a feature flag's environment. Use this to inspect workflow configuration, status, and details."""

    # Construct request model with validation
    try:
        _request = _models.GetCustomWorkflowRequest(
            path=_models.GetCustomWorkflowRequestPath(project_key=project_key, feature_flag_key=feature_flag_key, environment_key=environment_key, workflow_id=workflow_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_custom_workflow: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/flags/{featureFlagKey}/environments/{environmentKey}/workflows/{workflowId}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/flags/{featureFlagKey}/environments/{environmentKey}/workflows/{workflowId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_custom_workflow")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_custom_workflow", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_custom_workflow",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Workflows
@mcp.tool()
async def delete_workflow(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the feature flag."),
    feature_flag_key: str = Field(..., alias="featureFlagKey", description="The unique identifier for the feature flag that contains the workflow to delete."),
    environment_key: str = Field(..., alias="environmentKey", description="The unique identifier for the environment where the workflow is configured."),
    workflow_id: str = Field(..., alias="workflowId", description="The unique identifier for the workflow to delete."),
) -> dict[str, Any]:
    """Remove a workflow from a feature flag in a specific environment. This permanently deletes the workflow and its associated configuration."""

    # Construct request model with validation
    try:
        _request = _models.DeleteWorkflowRequest(
            path=_models.DeleteWorkflowRequestPath(project_key=project_key, feature_flag_key=feature_flag_key, environment_key=environment_key, workflow_id=workflow_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_workflow: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/flags/{featureFlagKey}/environments/{environmentKey}/workflows/{workflowId}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/flags/{featureFlagKey}/environments/{environmentKey}/workflows/{workflowId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_workflow")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_workflow", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_workflow",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Feature flags
@mcp.tool()
async def get_migration_safety_issues(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the feature flag."),
    flag_key: str = Field(..., alias="flagKey", description="The unique identifier for the feature flag being evaluated for migration safety."),
    environment_key: str = Field(..., alias="environmentKey", description="The unique identifier for the environment in which the flag changes would be applied."),
    instructions: list[_models.Instruction] = Field(..., description="An array of semantic patch instructions that describe the flag modifications to evaluate. Use the same instruction format as standard flag update operations. Order matters—instructions are applied sequentially."),
) -> dict[str, Any]:
    """Analyzes a feature flag patch and returns any migration safety issues that would result from applying those changes. Use this to validate flag modifications before deployment."""

    # Construct request model with validation
    try:
        _request = _models.PostMigrationSafetyIssuesRequest(
            path=_models.PostMigrationSafetyIssuesRequestPath(project_key=project_key, flag_key=flag_key, environment_key=environment_key),
            body=_models.PostMigrationSafetyIssuesRequestBody(instructions=instructions)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_migration_safety_issues: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/flags/{flagKey}/environments/{environmentKey}/migration-safety-issues", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/flags/{flagKey}/environments/{environmentKey}/migration-safety-issues"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_migration_safety_issues")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_migration_safety_issues", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_migration_safety_issues",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Releases (beta)
@mcp.tool()
async def add_flag_to_release_pipeline(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the flag."),
    flag_key: str = Field(..., alias="flagKey", description="The unique identifier for the flag to be added to the release pipeline."),
    release_pipeline_key: str = Field(..., alias="releasePipelineKey", description="The unique identifier of the release pipeline to attach the flag to."),
    release_variation_id: str | None = Field(None, alias="releaseVariationId", description="The variation to release across all phases of the pipeline. If not specified, the default variation will be used."),
) -> dict[str, Any]:
    """Adds a flag to a release pipeline, optionally specifying which variation to release across all phases. This initiates the flag's progression through the release pipeline's defined stages."""

    # Construct request model with validation
    try:
        _request = _models.CreateReleaseForFlagRequest(
            path=_models.CreateReleaseForFlagRequestPath(project_key=project_key, flag_key=flag_key),
            body=_models.CreateReleaseForFlagRequestBody(release_variation_id=release_variation_id, release_pipeline_key=release_pipeline_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_flag_to_release_pipeline: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/flags/{flagKey}/release", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/flags/{flagKey}/release"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_flag_to_release_pipeline")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_flag_to_release_pipeline", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_flag_to_release_pipeline",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Releases (beta)
@mcp.tool()
async def update_release_phase_status(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the feature flag release."),
    flag_key: str = Field(..., alias="flagKey", description="The unique identifier for the feature flag whose release phase should be updated."),
    phase_id: str = Field(..., alias="phaseId", description="The unique identifier for the specific phase within the release whose status should be updated."),
    status: str | None = Field(None, description="The new execution status to assign to the phase, controlling its progression through the release lifecycle."),
    audiences: list[_models.ReleaserAudienceConfigInput] | None = Field(None, description="An ordered list of audience configurations to apply when initializing the phase. Each item specifies targeting rules and rollout parameters for that audience segment."),
) -> dict[str, Any]:
    """Update the execution status of a specific phase within a feature flag release. Use this to advance phases through their lifecycle and configure audience targeting for phase initialization."""

    # Construct request model with validation
    try:
        _request = _models.UpdatePhaseStatusRequest(
            path=_models.UpdatePhaseStatusRequestPath(project_key=project_key, flag_key=flag_key, phase_id=phase_id),
            body=_models.UpdatePhaseStatusRequestBody(status=status, audiences=audiences)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_release_phase_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/flags/{flagKey}/release/phases/{phaseId}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/flags/{flagKey}/release/phases/{phaseId}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_release_phase_status")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_release_phase_status", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_release_phase_status",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Layers
@mcp.tool()
async def list_layers(project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project. This string value is used to scope the layer collection to a specific project.")) -> dict[str, Any]:
    """Retrieve all layers for a specified project. Returns a collection of layer resources associated with the given project."""

    # Construct request model with validation
    try:
        _request = _models.GetLayersRequest(
            path=_models.GetLayersRequestPath(project_key=project_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_layers: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/layers", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/layers"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_layers")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_layers", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_layers",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Layers
@mcp.tool()
async def create_layer(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project where the layer will be created."),
    key: str = Field(..., description="A unique identifier for the layer, typically in kebab-case format (e.g., 'checkout-flow'). This key is used to reference the layer in API calls and must be distinct within the project."),
    name: str = Field(..., description="A human-readable name for the layer that describes its purpose (e.g., 'Checkout Flow'). This is displayed in the UI and should be clear and descriptive."),
    description: str = Field(..., description="A detailed description explaining the layer's purpose and scope within the application. This helps team members understand what experiments belong in this layer."),
) -> dict[str, Any]:
    """Create a new layer within a project to enable mutually-exclusive traffic allocation across experiments. Experiments running in the same layer will have their traffic split exclusively among them."""

    # Construct request model with validation
    try:
        _request = _models.CreateLayerRequest(
            path=_models.CreateLayerRequestPath(project_key=project_key),
            body=_models.CreateLayerRequestBody(key=key, name=name, description=description)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_layer: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/layers", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/layers"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_layer")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_layer", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_layer",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Layers
@mcp.tool()
async def update_layer(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the layer."),
    layer_key: str = Field(..., alias="layerKey", description="The unique identifier for the layer to update."),
    instructions: list[_models.Instruction] = Field(..., description="An array of semantic patch instructions defining the updates to apply. Each instruction object must include a `kind` field specifying the operation type (updateName, updateDescription, updateExperimentReservation, or removeExperiment), along with any required parameters for that instruction type."),
    environment_key: str | None = Field(None, alias="environmentKey", description="The environment key for environment-specific updates, such as modifying experiment traffic reservations. Required when updating experiment reservations."),
) -> dict[str, Any]:
    """Modify a layer's properties or experiment traffic reservations using semantic patch instructions. Supports updating layer name/description or managing traffic reservations for experiments within the layer."""

    # Construct request model with validation
    try:
        _request = _models.UpdateLayerRequest(
            path=_models.UpdateLayerRequestPath(project_key=project_key, layer_key=layer_key),
            body=_models.UpdateLayerRequestBody(environment_key=environment_key, instructions=instructions)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_layer: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/layers/{layerKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/layers/{layerKey}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_layer")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_layer", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_layer",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Metrics (beta)
@mcp.tool()
async def list_metric_groups(project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project. Used to scope the metric groups to a specific project.")) -> dict[str, Any]:
    """Retrieve all metric groups for a project. Supports filtering by experiment status, connections, kind, maintainers, and fuzzy search; results can be sorted by name, creation date, or connection count."""

    # Construct request model with validation
    try:
        _request = _models.GetMetricGroupsRequest(
            path=_models.GetMetricGroupsRequestPath(project_key=project_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_metric_groups: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/metric-groups", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/metric-groups"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_metric_groups")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_metric_groups", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_metric_groups",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Metrics (beta)
@mcp.tool()
async def create_metric_group(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier of the project where the metric group will be created."),
    name: str = Field(..., description="A human-readable name for the metric group that appears in the UI and reports."),
    kind: Literal["funnel", "standard"] = Field(..., description="The classification type for the metric group: 'standard' for a regular collection of metrics, or 'funnel' for a sequential progression of steps."),
    maintainer_id: str = Field(..., alias="maintainerId", description="The ID of the team member responsible for maintaining and managing this metric group."),
    tags: list[str] = Field(..., description="One or more tags to categorize and organize the metric group for easier discovery and filtering."),
    metrics: list[_models.MetricInMetricGroupInput] = Field(..., description="An ordered list of metrics to include in the group. The order is significant and determines the sequence in which metrics are displayed and processed."),
    key: str | None = Field(None, description="A unique identifier for the metric group used in API references and integrations. If not provided, one will be auto-generated."),
) -> dict[str, Any]:
    """Create a new metric group within a project to organize and track related metrics. Metric groups can be configured as standard collections or funnel-type progressions."""

    # Construct request model with validation
    try:
        _request = _models.CreateMetricGroupRequest(
            path=_models.CreateMetricGroupRequestPath(project_key=project_key),
            body=_models.CreateMetricGroupRequestBody(key=key, name=name, kind=kind, maintainer_id=maintainer_id, tags=tags, metrics=metrics)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_metric_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/metric-groups", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/metric-groups"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_metric_group")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_metric_group", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_metric_group",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Metrics (beta)
@mcp.tool()
async def get_metric_group(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the metric group."),
    metric_group_key: str = Field(..., alias="metricGroupKey", description="The unique identifier for the metric group to retrieve."),
) -> dict[str, Any]:
    """Retrieve detailed information about a specific metric group within a project. Optionally expand the response to include associated experiments or experiment counts."""

    # Construct request model with validation
    try:
        _request = _models.GetMetricGroupRequest(
            path=_models.GetMetricGroupRequestPath(project_key=project_key, metric_group_key=metric_group_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_metric_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/metric-groups/{metricGroupKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/metric-groups/{metricGroupKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_metric_group")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_metric_group", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_metric_group",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Metrics (beta)
@mcp.tool()
async def update_metric_group(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the metric group."),
    metric_group_key: str = Field(..., alias="metricGroupKey", description="The unique identifier for the metric group to be updated."),
    body: list[_models.PatchOperation] = Field(..., description="An array of JSON Patch operations (RFC 6902) specifying the changes to apply. Each operation must include 'op' (the operation type such as 'replace', 'add', or 'remove'), 'path' (the JSON pointer to the target property), and 'value' (the new value, required for 'replace' and 'add' operations)."),
) -> dict[str, Any]:
    """Update a metric group using JSON Patch operations. Apply one or more changes to a metric group's properties by specifying the operation type, target path, and new value."""

    # Construct request model with validation
    try:
        _request = _models.PatchMetricGroupRequest(
            path=_models.PatchMetricGroupRequestPath(project_key=project_key, metric_group_key=metric_group_key),
            body=_models.PatchMetricGroupRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_metric_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/metric-groups/{metricGroupKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/metric-groups/{metricGroupKey}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_metric_group")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_metric_group", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_metric_group",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Metrics (beta)
@mcp.tool()
async def delete_metric_group(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the metric group to delete."),
    metric_group_key: str = Field(..., alias="metricGroupKey", description="The unique identifier for the metric group to delete."),
) -> dict[str, Any]:
    """Permanently delete a metric group from a project by its key. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteMetricGroupRequest(
            path=_models.DeleteMetricGroupRequestPath(project_key=project_key, metric_group_key=metric_group_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_metric_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/metric-groups/{metricGroupKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/metric-groups/{metricGroupKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_metric_group")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_metric_group", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_metric_group",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Release pipelines (beta)
@mcp.tool()
async def list_release_pipelines(project_key: str = Field(..., alias="projectKey", description="The project key that identifies which project's release pipelines to retrieve.")) -> dict[str, Any]:
    """Retrieve all release pipelines for a project. Supports filtering by pipeline attributes (key, name, description) and environment."""

    # Construct request model with validation
    try:
        _request = _models.GetAllReleasePipelinesRequest(
            path=_models.GetAllReleasePipelinesRequestPath(project_key=project_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_release_pipelines: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/release-pipelines", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/release-pipelines"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_release_pipelines")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_release_pipelines", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_release_pipelines",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Release pipelines (beta)
@mcp.tool()
async def create_release_pipeline(
    project_key: str = Field(..., alias="projectKey", description="The project key that uniquely identifies the project where the release pipeline will be created."),
    key: str = Field(..., description="A unique identifier for this release pipeline within the project (e.g., 'standard-pipeline'). Used to reference the pipeline in API calls and configurations."),
    name: str = Field(..., description="A human-readable name for the release pipeline (e.g., 'Standard Pipeline'). Displayed in the UI and used for identification."),
    phases: list[_models.CreatePhaseInput] = Field(..., description="An ordered array of phase objects that define logical groupings of environments. Each phase shares attributes for coordinating feature rollouts across its environments."),
    tags: list[str] | None = Field(None, description="An optional list of tags to categorize and organize the release pipeline (e.g., ['example-tag']). Useful for filtering and searching pipelines."),
    is_project_default: bool | None = Field(None, alias="isProjectDefault", description="Optional boolean flag. When true, sets this pipeline as the default for the project. If not specified, only the first pipeline created becomes the default."),
    is_legacy: bool | None = Field(None, alias="isLegacy", description="Optional boolean flag. When true, enables this pipeline for Release Automation features. Controls whether the pipeline participates in automated release workflows."),
) -> dict[str, Any]:
    """Create a new release pipeline for a project. The first pipeline created automatically becomes the default; subsequent pipelines can be set as default via the project update API. Projects support up to 20 release pipelines."""

    # Construct request model with validation
    try:
        _request = _models.PostReleasePipelineRequest(
            path=_models.PostReleasePipelineRequestPath(project_key=project_key),
            body=_models.PostReleasePipelineRequestBody(key=key, name=name, phases=phases, tags=tags, is_project_default=is_project_default, is_legacy=is_legacy)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_release_pipeline: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/release-pipelines", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/release-pipelines"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_release_pipeline")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_release_pipeline", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_release_pipeline",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Release pipelines (beta)
@mcp.tool()
async def get_release_pipeline_by_key(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the release pipeline."),
    pipeline_key: str = Field(..., alias="pipelineKey", description="The unique identifier for the release pipeline to retrieve."),
) -> dict[str, Any]:
    """Retrieve a specific release pipeline within a project using its unique key identifier. This operation returns the complete pipeline configuration and metadata."""

    # Construct request model with validation
    try:
        _request = _models.GetReleasePipelineByKeyRequest(
            path=_models.GetReleasePipelineByKeyRequestPath(project_key=project_key, pipeline_key=pipeline_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_release_pipeline_by_key: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/release-pipelines/{pipelineKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/release-pipelines/{pipelineKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_release_pipeline_by_key")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_release_pipeline_by_key", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_release_pipeline_by_key",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Release pipelines (beta)
@mcp.tool()
async def update_release_pipeline(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the release pipeline."),
    pipeline_key: str = Field(..., alias="pipelineKey", description="The unique identifier for the release pipeline to be updated."),
    name: str = Field(..., description="The display name for the release pipeline (e.g., 'Standard Pipeline'). Used to identify the pipeline in the UI and reports."),
    phases: list[_models.CreatePhaseInput] = Field(..., description="An ordered array of deployment phases, where each phase represents a logical grouping of one or more environments that share attributes for rolling out changes. Phase order determines the sequence of deployments."),
    tags: list[str] | None = Field(None, description="An optional array of tags for categorizing and filtering the release pipeline (e.g., ['example-tag']). Tags help organize pipelines by team, environment type, or other attributes."),
) -> dict[str, Any]:
    """Updates an existing release pipeline with new configuration, including its name, deployment phases, and optional tags for organization and filtering."""

    # Construct request model with validation
    try:
        _request = _models.PutReleasePipelineRequest(
            path=_models.PutReleasePipelineRequestPath(project_key=project_key, pipeline_key=pipeline_key),
            body=_models.PutReleasePipelineRequestBody(name=name, phases=phases, tags=tags)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_release_pipeline: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/release-pipelines/{pipelineKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/release-pipelines/{pipelineKey}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_release_pipeline")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_release_pipeline", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_release_pipeline",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Release pipelines (beta)
@mcp.tool()
async def delete_release_pipeline(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the release pipeline."),
    pipeline_key: str = Field(..., alias="pipelineKey", description="The unique identifier for the release pipeline to delete."),
) -> dict[str, Any]:
    """Deletes a release pipeline from a project. Note that the default release pipeline cannot be deleted; if you need to remove it, first create and set a different pipeline as default."""

    # Construct request model with validation
    try:
        _request = _models.DeleteReleasePipelineRequest(
            path=_models.DeleteReleasePipelineRequestPath(project_key=project_key, pipeline_key=pipeline_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_release_pipeline: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/release-pipelines/{pipelineKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/release-pipelines/{pipelineKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_release_pipeline")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_release_pipeline", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_release_pipeline",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Release pipelines (beta)
@mcp.tool()
async def list_release_progressions_for_pipeline(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the release pipeline."),
    pipeline_key: str = Field(..., alias="pipelineKey", description="The unique identifier for the release pipeline whose release progressions you want to retrieve."),
) -> dict[str, Any]:
    """Retrieve the progression status of all releases across all feature flags within a specified release pipeline. This provides a comprehensive view of how releases are advancing through the pipeline."""

    # Construct request model with validation
    try:
        _request = _models.GetAllReleaseProgressionsForReleasePipelineRequest(
            path=_models.GetAllReleaseProgressionsForReleasePipelineRequestPath(project_key=project_key, pipeline_key=pipeline_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_release_progressions_for_pipeline: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/release-pipelines/{pipelineKey}/releases", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/release-pipelines/{pipelineKey}/releases"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_release_progressions_for_pipeline")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_release_progressions_for_pipeline", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_release_progressions_for_pipeline",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom roles
@mcp.tool()
async def list_custom_roles() -> dict[str, Any]:
    """Retrieve all custom roles available in your LaunchDarkly organization, including project-specific roles, organization-wide roles, and LaunchDarkly-provided preset roles. Base roles are excluded from this list."""

    # Extract parameters for API call
    _http_path = "/api/v2/roles"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_custom_roles")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_custom_roles", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_custom_roles",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom roles
@mcp.tool()
async def get_custom_role(custom_role_key: str = Field(..., alias="customRoleKey", description="The unique identifier for the custom role, specified as either the custom role key or its ID.")) -> dict[str, Any]:
    """Retrieve a single custom role by its unique key or ID. Use this to fetch detailed information about a specific custom role in your organization."""

    # Construct request model with validation
    try:
        _request = _models.GetCustomRoleRequest(
            path=_models.GetCustomRoleRequestPath(custom_role_key=custom_role_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_custom_role: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/roles/{customRoleKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/roles/{customRoleKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_custom_role")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_custom_role", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_custom_role",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom roles
@mcp.tool()
async def update_custom_role(
    custom_role_key: str = Field(..., alias="customRoleKey", description="The unique identifier key for the custom role to update."),
    patch: list[_models.PatchOperation] = Field(..., description="An array of JSON patch operations (RFC 6902) or JSON merge patch (RFC 7386) representing the changes to apply. To modify the policy array, use path `/policy` followed by an array index (`/0` for beginning, `/-` for end), or specify other role properties to update."),
) -> dict[str, Any]:
    """Update a custom role using JSON patch or JSON merge patch operations. Supports modifying role policies by specifying the desired changes as a patch document."""

    # Construct request model with validation
    try:
        _request = _models.PatchCustomRoleRequest(
            path=_models.PatchCustomRoleRequestPath(custom_role_key=custom_role_key),
            body=_models.PatchCustomRoleRequestBody(patch=patch)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_custom_role: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/roles/{customRoleKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/roles/{customRoleKey}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_custom_role")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_custom_role", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_custom_role",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom roles
@mcp.tool()
async def delete_custom_role(custom_role_key: str = Field(..., alias="customRoleKey", description="The unique identifier for the custom role to delete. This is a string value that uniquely identifies the role within the system.")) -> dict[str, Any]:
    """Permanently delete a custom role by its unique key. This action removes the role and any associated permissions from the system."""

    # Construct request model with validation
    try:
        _request = _models.DeleteCustomRoleRequest(
            path=_models.DeleteCustomRoleRequestPath(custom_role_key=custom_role_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_custom_role: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/roles/{customRoleKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/roles/{customRoleKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_custom_role")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_custom_role", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_custom_role",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Segments
@mcp.tool()
async def list_segments(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the LaunchDarkly project containing the segments."),
    environment_key: str = Field(..., alias="environmentKey", description="The unique identifier for the environment within the project from which to retrieve segments."),
) -> dict[str, Any]:
    """Retrieve all segments in a project environment, including rule-based, list-based, and synced segments. Supports filtering by tags, keys, segment type, external sync status, and fuzzy search across segment metadata."""

    # Construct request model with validation
    try:
        _request = _models.GetSegmentsRequest(
            path=_models.GetSegmentsRequestPath(project_key=project_key, environment_key=environment_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_segments: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/segments/{projectKey}/{environmentKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/segments/{projectKey}/{environmentKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_segments")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_segments", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_segments",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Segments
@mcp.tool()
async def create_segment(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the LaunchDarkly project where the segment will be created."),
    environment_key: str = Field(..., alias="environmentKey", description="The unique identifier for the environment within the project where the segment will be created."),
    name: str = Field(..., description="A human-readable name for the segment that describes its purpose or audience."),
    key: str = Field(..., description="A unique identifier for the segment used in code and API references. Must be distinct within the project."),
    tags: list[str] | None = Field(None, description="Optional labels to organize and categorize the segment for easier management and filtering."),
    unbounded: bool | None = Field(None, description="Set to true to create a big segment for handling more than 15,000 individual targets; false for standard segments with rule-based or smaller list-based criteria."),
    unbounded_context_kind: str | None = Field(None, alias="unboundedContextKind", description="For big segments, specifies the context kind (e.g., 'device', 'user') that the segment targets. Required when creating a big segment."),
) -> dict[str, Any]:
    """Create a new segment in a LaunchDarkly project environment. Segments can be standard (rule-based or small list-based) or big segments (large list-based or synced) for targeting contexts."""

    # Construct request model with validation
    try:
        _request = _models.PostSegmentRequest(
            path=_models.PostSegmentRequestPath(project_key=project_key, environment_key=environment_key),
            body=_models.PostSegmentRequestBody(name=name, key=key, tags=tags, unbounded=unbounded, unbounded_context_kind=unbounded_context_kind)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_segment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/segments/{projectKey}/{environmentKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/segments/{projectKey}/{environmentKey}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_segment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_segment", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_segment",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Segments
@mcp.tool()
async def get_segment(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the segment."),
    environment_key: str = Field(..., alias="environmentKey", description="The unique identifier for the environment within the project."),
    segment_key: str = Field(..., alias="segmentKey", description="The unique identifier for the segment to retrieve."),
) -> dict[str, Any]:
    """Retrieve a single segment by its key. Segments can be rule-based, list-based, or synced; big segments include larger list-based and synced segments with additional metadata fields."""

    # Construct request model with validation
    try:
        _request = _models.GetSegmentRequest(
            path=_models.GetSegmentRequestPath(project_key=project_key, environment_key=environment_key, segment_key=segment_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_segment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/segments/{projectKey}/{environmentKey}/{segmentKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/segments/{projectKey}/{environmentKey}/{segmentKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_segment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_segment", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_segment",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Segments
@mcp.tool()
async def update_segment(
    project_key: str = Field(..., alias="projectKey", description="The project key that contains the segment to update."),
    environment_key: str = Field(..., alias="environmentKey", description="The environment key where the segment exists."),
    segment_key: str = Field(..., alias="segmentKey", description="The segment key identifying which segment to update."),
    patch: list[_models.PatchOperation] = Field(..., description="The patch instructions as a JSON array. Use semantic patch (with `domain-model=launchdarkly.semanticpatch` header) for segment-specific operations like managing targets and rules, or standard JSON patch/merge patch for direct field modifications. Semantic patch requires `environmentKey` and `instructions` properties; JSON patch uses standard RFC 6902 operations."),
    dry_run: bool | None = Field(None, alias="dryRun", description="When true, validates the patch and returns a preview of the updated segment without persisting changes."),
) -> dict[str, Any]:
    """Update a segment using semantic patch, JSON patch, or JSON merge patch. Supports modifications to segment metadata, targeting rules, individual targets, and big segment operations."""

    # Construct request model with validation
    try:
        _request = _models.PatchSegmentRequest(
            path=_models.PatchSegmentRequestPath(project_key=project_key, environment_key=environment_key, segment_key=segment_key),
            query=_models.PatchSegmentRequestQuery(dry_run=dry_run),
            body=_models.PatchSegmentRequestBody(patch=patch)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_segment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/segments/{projectKey}/{environmentKey}/{segmentKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/segments/{projectKey}/{environmentKey}/{segmentKey}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_segment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_segment", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_segment",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Segments
@mcp.tool()
async def delete_segment(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the segment to delete."),
    environment_key: str = Field(..., alias="environmentKey", description="The unique identifier for the environment within the project where the segment exists."),
    segment_key: str = Field(..., alias="segmentKey", description="The unique identifier for the segment to delete."),
) -> dict[str, Any]:
    """Permanently delete a segment from a specific project and environment. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteSegmentRequest(
            path=_models.DeleteSegmentRequestPath(project_key=project_key, environment_key=environment_key, segment_key=segment_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_segment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/segments/{projectKey}/{environmentKey}/{segmentKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/segments/{projectKey}/{environmentKey}/{segmentKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_segment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_segment", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_segment",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Segments
@mcp.tool()
async def update_big_segment_context_targets(
    project_key: str = Field(..., alias="projectKey", description="The project key that identifies the LaunchDarkly project containing the segment."),
    environment_key: str = Field(..., alias="environmentKey", description="The environment key that identifies the specific environment within the project."),
    segment_key: str = Field(..., alias="segmentKey", description="The segment key that uniquely identifies the big segment to update."),
    included_add: list[str] | None = Field(None, alias="includedAdd", description="Array of context identifiers to add to the segment's included list. Order is not significant."),
    excluded_add: list[str] | None = Field(None, alias="excludedAdd", description="Array of context identifiers to add to the segment's excluded list. Order is not significant."),
    included_remove: list[str] | None = Field(None, alias="includedRemove", description="Array of context identifiers to remove from the segment's included list. Order is not significant."),
    excluded_remove: list[str] | None = Field(None, alias="excludedRemove", description="Array of context identifiers to remove from the segment's excluded list. Order is not significant."),
) -> dict[str, Any]:
    """Update which contexts are included in or excluded from a big segment. Big segments support larger list-based and synced segments, unlike standard segments which are not supported by this operation."""

    # Construct request model with validation
    try:
        _request = _models.UpdateBigSegmentContextTargetsRequest(
            path=_models.UpdateBigSegmentContextTargetsRequestPath(project_key=project_key, environment_key=environment_key, segment_key=segment_key),
            body=_models.UpdateBigSegmentContextTargetsRequestBody(included=_models.UpdateBigSegmentContextTargetsRequestBodyIncluded(add=included_add, remove=included_remove) if any(v is not None for v in [included_add, included_remove]) else None,
                excluded=_models.UpdateBigSegmentContextTargetsRequestBodyExcluded(add=excluded_add, remove=excluded_remove) if any(v is not None for v in [excluded_add, excluded_remove]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_big_segment_context_targets: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/segments/{projectKey}/{environmentKey}/{segmentKey}/contexts", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/segments/{projectKey}/{environmentKey}/{segmentKey}/contexts"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_big_segment_context_targets")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_big_segment_context_targets", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_big_segment_context_targets",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Segments
@mcp.tool()
async def get_segment_membership_for_context(
    project_key: str = Field(..., alias="projectKey", description="The project key that identifies which project contains the segment."),
    environment_key: str = Field(..., alias="environmentKey", description="The environment key that identifies which environment to query for segment membership."),
    segment_key: str = Field(..., alias="segmentKey", description="The segment key that identifies the big segment to check membership against."),
    context_key: str = Field(..., alias="contextKey", description="The context key that identifies the specific context whose membership status you want to retrieve."),
) -> dict[str, Any]:
    """Check whether a specific context is included or excluded from a big segment. Big segments support larger list-based and synced segments, but not standard segments."""

    # Construct request model with validation
    try:
        _request = _models.GetSegmentMembershipForContextRequest(
            path=_models.GetSegmentMembershipForContextRequestPath(project_key=project_key, environment_key=environment_key, segment_key=segment_key, context_key=context_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_segment_membership_for_context: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/segments/{projectKey}/{environmentKey}/{segmentKey}/contexts/{contextKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/segments/{projectKey}/{environmentKey}/{segmentKey}/contexts/{contextKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_segment_membership_for_context")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_segment_membership_for_context", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_segment_membership_for_context",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Segments
@mcp.tool()
async def create_big_segment_export(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the LaunchDarkly project containing the segment to export."),
    environment_key: str = Field(..., alias="environmentKey", description="The unique identifier for the environment within the project where the segment exists."),
    segment_key: str = Field(..., alias="segmentKey", description="The unique identifier for the big segment to export."),
) -> dict[str, Any]:
    """Initiates an export process for a large segment (synced or list-based) containing more than 15,000 entries. The export runs asynchronously and can be monitored for completion status."""

    # Construct request model with validation
    try:
        _request = _models.CreateBigSegmentExportRequest(
            path=_models.CreateBigSegmentExportRequestPath(project_key=project_key, environment_key=environment_key, segment_key=segment_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_big_segment_export: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/segments/{projectKey}/{environmentKey}/{segmentKey}/exports", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/segments/{projectKey}/{environmentKey}/{segmentKey}/exports"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_big_segment_export")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_big_segment_export", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_big_segment_export",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Segments
@mcp.tool()
async def get_big_segment_export(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the LaunchDarkly project containing the segment."),
    environment_key: str = Field(..., alias="environmentKey", description="The unique identifier for the environment within the project where the segment is defined."),
    segment_key: str = Field(..., alias="segmentKey", description="The unique identifier for the segment being exported."),
    export_id: str = Field(..., alias="exportID", description="The unique identifier for the specific export process to retrieve information about."),
) -> dict[str, Any]:
    """Retrieve the status and details of a big segment export process for a synced or list-based segment containing more than 15,000 entries."""

    # Construct request model with validation
    try:
        _request = _models.GetBigSegmentExportRequest(
            path=_models.GetBigSegmentExportRequestPath(project_key=project_key, environment_key=environment_key, segment_key=segment_key, export_id=export_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_big_segment_export: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/segments/{projectKey}/{environmentKey}/{segmentKey}/exports/{exportID}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/segments/{projectKey}/{environmentKey}/{segmentKey}/exports/{exportID}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_big_segment_export")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_big_segment_export", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_big_segment_export",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Segments
@mcp.tool()
async def create_big_segment_import(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the segment."),
    environment_key: str = Field(..., alias="environmentKey", description="The unique identifier for the environment within the project."),
    segment_key: str = Field(..., alias="segmentKey", description="The unique identifier for the big segment to import data into."),
    file_: str | None = Field(None, alias="file", description="A CSV file containing the segment keys to import. Each row should contain one key entry."),
    mode: str | None = Field(None, description="The import strategy: use `merge` to add new entries while preserving existing ones, or `replace` to overwrite all existing entries with the imported data."),
    wait_on_approvals: bool | None = Field(None, alias="waitOnApprovals", description="If true, the import process will pause and wait for any required approvals before processing the data."),
) -> dict[str, Any]:
    """Initiate an import process for a big segment to add or replace list-based segment entries. This operation supports importing large datasets with more than 15,000 entries from a CSV file."""

    # Construct request model with validation
    try:
        _request = _models.CreateBigSegmentImportRequest(
            path=_models.CreateBigSegmentImportRequestPath(project_key=project_key, environment_key=environment_key, segment_key=segment_key),
            body=_models.CreateBigSegmentImportRequestBody(file_=file_, mode=mode, wait_on_approvals=wait_on_approvals)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_big_segment_import: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/segments/{projectKey}/{environmentKey}/{segmentKey}/imports", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/segments/{projectKey}/{environmentKey}/{segmentKey}/imports"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_big_segment_import")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_big_segment_import", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_big_segment_import",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: Segments
@mcp.tool()
async def get_big_segment_import(
    project_key: str = Field(..., alias="projectKey", description="The project key that identifies which project contains the segment being imported."),
    environment_key: str = Field(..., alias="environmentKey", description="The environment key that identifies which environment contains the segment being imported."),
    segment_key: str = Field(..., alias="segmentKey", description="The segment key that identifies the specific big segment associated with this import."),
    import_id: str = Field(..., alias="importID", description="The import ID that uniquely identifies the specific import process to retrieve status and details for."),
) -> dict[str, Any]:
    """Retrieve detailed information about an in-progress or completed big segment import process. Big segments support list-based imports with more than 15,000 entries."""

    # Construct request model with validation
    try:
        _request = _models.GetBigSegmentImportRequest(
            path=_models.GetBigSegmentImportRequestPath(project_key=project_key, environment_key=environment_key, segment_key=segment_key, import_id=import_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_big_segment_import: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/segments/{projectKey}/{environmentKey}/{segmentKey}/imports/{importID}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/segments/{projectKey}/{environmentKey}/{segmentKey}/imports/{importID}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_big_segment_import")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_big_segment_import", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_big_segment_import",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Segments
@mcp.tool()
async def update_big_segment_user_targets(
    project_key: str = Field(..., alias="projectKey", description="The project key that identifies which project contains the segment."),
    environment_key: str = Field(..., alias="environmentKey", description="The environment key that identifies which environment the segment belongs to."),
    segment_key: str = Field(..., alias="segmentKey", description="The segment key that uniquely identifies the big segment to update."),
    included_add: list[str] | None = Field(None, alias="includedAdd", description="Array of user context identifiers to add to the segment's included targets. Order is not significant."),
    excluded_add: list[str] | None = Field(None, alias="excludedAdd", description="Array of user context identifiers to add to the segment's excluded targets. Order is not significant."),
    included_remove: list[str] | None = Field(None, alias="includedRemove", description="Array of user context identifiers to remove from the segment's included targets. Order is not significant."),
    excluded_remove: list[str] | None = Field(None, alias="excludedRemove", description="Array of user context identifiers to remove from the segment's excluded targets. Order is not significant."),
) -> dict[str, Any]:
    """Modify user context targets included or excluded in a big segment. Use this operation to add or remove users from list-based or synced segments, which support larger audiences than standard segments."""

    # Construct request model with validation
    try:
        _request = _models.UpdateBigSegmentTargetsRequest(
            path=_models.UpdateBigSegmentTargetsRequestPath(project_key=project_key, environment_key=environment_key, segment_key=segment_key),
            body=_models.UpdateBigSegmentTargetsRequestBody(included=_models.UpdateBigSegmentTargetsRequestBodyIncluded(add=included_add, remove=included_remove) if any(v is not None for v in [included_add, included_remove]) else None,
                excluded=_models.UpdateBigSegmentTargetsRequestBodyExcluded(add=excluded_add, remove=excluded_remove) if any(v is not None for v in [excluded_add, excluded_remove]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_big_segment_user_targets: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/segments/{projectKey}/{environmentKey}/{segmentKey}/users", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/segments/{projectKey}/{environmentKey}/{segmentKey}/users"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_big_segment_user_targets")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_big_segment_user_targets", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_big_segment_user_targets",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Segments
@mcp.tool()
async def get_user_segment_membership(
    project_key: str = Field(..., alias="projectKey", description="The project key that contains the segment."),
    environment_key: str = Field(..., alias="environmentKey", description="The environment key where the segment membership is evaluated."),
    segment_key: str = Field(..., alias="segmentKey", description="The big segment key to check membership for."),
    user_key: str = Field(..., alias="userKey", description="The user key to check for membership in the segment."),
) -> dict[str, Any]:
    """Check whether a user is included or excluded from a big segment. This operation only works with big segments, not standard segments."""

    # Construct request model with validation
    try:
        _request = _models.GetSegmentMembershipForUserRequest(
            path=_models.GetSegmentMembershipForUserRequestPath(project_key=project_key, environment_key=environment_key, segment_key=segment_key, user_key=user_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_user_segment_membership: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/segments/{projectKey}/{environmentKey}/{segmentKey}/users/{userKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/segments/{projectKey}/{environmentKey}/{segmentKey}/users/{userKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_user_segment_membership")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_user_segment_membership", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_user_segment_membership",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Segments
@mcp.tool()
async def list_expiring_targets_for_segment(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the segment."),
    environment_key: str = Field(..., alias="environmentKey", description="The unique identifier for the environment where the segment's expiring targets are managed."),
    segment_key: str = Field(..., alias="segmentKey", description="The unique identifier for the segment whose expiring context targets you want to retrieve."),
) -> dict[str, Any]:
    """Retrieve a list of context targets within a segment that are scheduled for removal. This helps identify which targets will be automatically deleted from the segment."""

    # Construct request model with validation
    try:
        _request = _models.GetExpiringTargetsForSegmentRequest(
            path=_models.GetExpiringTargetsForSegmentRequestPath(project_key=project_key, environment_key=environment_key, segment_key=segment_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_expiring_targets_for_segment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/segments/{projectKey}/{segmentKey}/expiring-targets/{environmentKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/segments/{projectKey}/{segmentKey}/expiring-targets/{environmentKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_expiring_targets_for_segment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_expiring_targets_for_segment", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_expiring_targets_for_segment",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Segments
@mcp.tool()
async def update_segment_expiring_targets(
    project_key: str = Field(..., alias="projectKey", description="The project key that contains the segment. Used to identify which project's segment configuration to modify."),
    environment_key: str = Field(..., alias="environmentKey", description="The environment key where the segment targeting applies. Specifies which environment's segment expiration rules to update."),
    segment_key: str = Field(..., alias="segmentKey", description="The segment key identifying which segment's expiring targets to modify."),
    instructions: list[_models.PatchSegmentExpiringTargetInstruction] = Field(..., description="Array of semantic patch instructions defining the changes to apply. Each instruction must specify a kind (addExpiringTarget, updateExpiringTarget, or removeExpiringTarget), the target type (included or excluded), context key, context kind, and for add/update operations, an expiration timestamp in Unix milliseconds. Instructions are processed sequentially and partial failures return status 200 with errors listed in the response."),
) -> dict[str, Any]:
    """Schedule or modify expiration dates for context targets within a segment using semantic patch instructions. Supports adding, updating, or removing scheduled expirations for included or excluded contexts."""

    # Construct request model with validation
    try:
        _request = _models.PatchExpiringTargetsForSegmentRequest(
            path=_models.PatchExpiringTargetsForSegmentRequestPath(project_key=project_key, environment_key=environment_key, segment_key=segment_key),
            body=_models.PatchExpiringTargetsForSegmentRequestBody(instructions=instructions)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_segment_expiring_targets: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/segments/{projectKey}/{segmentKey}/expiring-targets/{environmentKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/segments/{projectKey}/{segmentKey}/expiring-targets/{environmentKey}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_segment_expiring_targets")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_segment_expiring_targets", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_segment_expiring_targets",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Segments
@mcp.tool()
async def list_expiring_user_targets_for_segment(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the LaunchDarkly project containing the segment."),
    environment_key: str = Field(..., alias="environmentKey", description="The unique identifier for the environment within the project where the segment is defined."),
    segment_key: str = Field(..., alias="segmentKey", description="The unique identifier for the segment whose expiring user targets should be retrieved."),
) -> dict[str, Any]:
    """Retrieve a list of user targets scheduled for removal from a specific segment. Note: This endpoint is deprecated; use list_expiring_targets_for_segment instead after upgrading to context-based SDKs."""

    # Construct request model with validation
    try:
        _request = _models.GetExpiringUserTargetsForSegmentRequest(
            path=_models.GetExpiringUserTargetsForSegmentRequestPath(project_key=project_key, environment_key=environment_key, segment_key=segment_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_expiring_user_targets_for_segment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/segments/{projectKey}/{segmentKey}/expiring-user-targets/{environmentKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/segments/{projectKey}/{segmentKey}/expiring-user-targets/{environmentKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_expiring_user_targets_for_segment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_expiring_user_targets_for_segment", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_expiring_user_targets_for_segment",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Segments
@mcp.tool()
async def update_expiring_user_targets_for_segment(
    project_key: str = Field(..., alias="projectKey", description="The project key that contains the segment. Used to identify which project's segment to update."),
    environment_key: str = Field(..., alias="environmentKey", description="The environment key where the segment targeting applies. Specifies which environment's user targets should be modified."),
    segment_key: str = Field(..., alias="segmentKey", description="The segment key identifying which segment's user target expirations to update."),
    instructions: list[_models.PatchSegmentInstruction] = Field(..., description="Array of semantic patch instructions defining the changes to apply. Each instruction must specify a kind (addExpireUserTargetDate, updateExpireUserTargetDate, or removeExpireUserTargetDate), targetType (included or excluded), userKey, and optionally a value (Unix milliseconds for expiration date) or version number. Instructions are processed in order."),
) -> dict[str, Any]:
    """Update expiration dates for users targeted in a segment using semantic patch instructions. This endpoint manages when LaunchDarkly will automatically remove users from segment targeting."""

    # Construct request model with validation
    try:
        _request = _models.PatchExpiringUserTargetsForSegmentRequest(
            path=_models.PatchExpiringUserTargetsForSegmentRequestPath(project_key=project_key, environment_key=environment_key, segment_key=segment_key),
            body=_models.PatchExpiringUserTargetsForSegmentRequestBody(instructions=instructions)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_expiring_user_targets_for_segment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/segments/{projectKey}/{segmentKey}/expiring-user-targets/{environmentKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/segments/{projectKey}/{segmentKey}/expiring-user-targets/{environmentKey}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_expiring_user_targets_for_segment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_expiring_user_targets_for_segment", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_expiring_user_targets_for_segment",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Teams
@mcp.tool()
async def list_teams() -> dict[str, Any]:
    """Retrieve a paginated list of teams with optional filtering and field expansion. By default returns the first 20 teams; use pagination links and the limit parameter to navigate through results."""

    # Extract parameters for API call
    _http_path = "/api/v2/teams"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_teams")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_teams", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_teams",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Teams
@mcp.tool()
async def create_team(
    key: str = Field(..., description="Unique identifier for the team. Used to reference the team in API calls and must be URL-safe."),
    name: str = Field(..., description="Human-readable name for the team. This is displayed in the LaunchDarkly UI and should be descriptive."),
    custom_role_keys: list[str] | None = Field(None, alias="customRoleKeys", description="List of custom role keys to assign to the team, granting access to those roles. Provide as an array of role key strings."),
    member_i_ds: list[str] | None = Field(None, alias="memberIDs", description="Array of member IDs to add to the team upon creation. Each ID should be a valid LaunchDarkly member identifier."),
    permission_grants: list[_models.PermissionGrantInput] | None = Field(None, alias="permissionGrants", description="Array of permission grants that define specific actions the team can perform without requiring a custom role. Each grant specifies an action and resource scope."),
    role_attributes: dict[str, _models.RoleAttributeValues] | None = Field(None, alias="roleAttributes", description="Object containing role attributes as key-value pairs. Attributes provide additional context or metadata for the team's roles."),
) -> dict[str, Any]:
    """Create a new team in LaunchDarkly with optional members, custom roles, and permission grants. Supports expanding the response to include members, roles, projects, and maintainers."""

    # Construct request model with validation
    try:
        _request = _models.PostTeamRequest(
            body=_models.PostTeamRequestBody(custom_role_keys=custom_role_keys, key=key, member_i_ds=member_i_ds, name=name, permission_grants=permission_grants, role_attributes=role_attributes)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_team: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v2/teams"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_team")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_team", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_team",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Teams
@mcp.tool()
async def get_team(team_key: str = Field(..., alias="teamKey", description="The unique identifier for the team. Use this key to fetch the specific team's details.")) -> dict[str, Any]:
    """Retrieve a team by its unique key. Optionally expand the response to include members, roles, role attributes, projects, or maintainers."""

    # Construct request model with validation
    try:
        _request = _models.GetTeamRequest(
            path=_models.GetTeamRequestPath(team_key=team_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_team: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/teams/{teamKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/teams/{teamKey}"
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

# Tags: Teams
@mcp.tool()
async def update_team(
    team_key: str = Field(..., alias="teamKey", description="The unique identifier for the team to update. Use the team key value returned from team listing operations."),
    instructions: list[_models.Instruction] = Field(..., description="An array of semantic patch instruction objects that specify the updates to apply. Each instruction object must include a `kind` field indicating the operation type (e.g., addMembers, updateName, removeCustomRoles) and any required parameters for that operation. Multiple instructions are processed sequentially."),
) -> dict[str, Any]:
    """Perform a partial update to a team using semantic patch instructions. Supports operations like adding/removing members, updating team metadata, managing custom roles, and configuring permission grants."""

    # Construct request model with validation
    try:
        _request = _models.PatchTeamRequest(
            path=_models.PatchTeamRequestPath(team_key=team_key),
            body=_models.PatchTeamRequestBody(instructions=instructions)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_team: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/teams/{teamKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/teams/{teamKey}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_team")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_team", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_team",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Teams
@mcp.tool()
async def delete_team(team_key: str = Field(..., alias="teamKey", description="The unique identifier for the team to delete. This is a string value that uniquely identifies the team within your LaunchDarkly organization.")) -> dict[str, Any]:
    """Permanently delete a team by its key. This action cannot be undone and will remove the team from your LaunchDarkly account."""

    # Construct request model with validation
    try:
        _request = _models.DeleteTeamRequest(
            path=_models.DeleteTeamRequestPath(team_key=team_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_team: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/teams/{teamKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/teams/{teamKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_team")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_team", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_team",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Teams
@mcp.tool()
async def list_team_maintainers(team_key: str = Field(..., alias="teamKey", description="The unique identifier for the team whose maintainers you want to retrieve.")) -> dict[str, Any]:
    """Retrieve the list of maintainers assigned to a specific team. Maintainers have elevated permissions to manage team settings and members."""

    # Construct request model with validation
    try:
        _request = _models.GetTeamMaintainersRequest(
            path=_models.GetTeamMaintainersRequestPath(team_key=team_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_team_maintainers: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/teams/{teamKey}/maintainers", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/teams/{teamKey}/maintainers"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_team_maintainers")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_team_maintainers", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_team_maintainers",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Teams
@mcp.tool()
async def add_members_to_team(
    team_key: str = Field(..., alias="teamKey", description="The unique identifier for the team. Used to route the request to the correct team."),
    file_: str | None = Field(None, alias="file", description="A CSV file containing email addresses in the first column (headers optional). LaunchDarkly ignores additional columns. File must not exceed 25MB and must contain at least one valid email address belonging to a LaunchDarkly organization member."),
) -> dict[str, Any]:
    """Add multiple team members to an existing team by uploading a CSV file containing email addresses. The operation validates all entries before adding any members—a single invalid entry prevents all additions."""

    # Construct request model with validation
    try:
        _request = _models.PostTeamMembersRequest(
            path=_models.PostTeamMembersRequestPath(team_key=team_key),
            body=_models.PostTeamMembersRequestBody(file_=file_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_members_to_team: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/teams/{teamKey}/members", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/teams/{teamKey}/members"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_members_to_team")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_members_to_team", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_members_to_team",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: Teams
@mcp.tool()
async def list_team_roles(team_key: str = Field(..., alias="teamKey", description="The unique identifier for the team whose roles you want to retrieve.")) -> dict[str, Any]:
    """Retrieve all custom roles assigned to a specific team. Custom roles define granular permissions for team members within LaunchDarkly."""

    # Construct request model with validation
    try:
        _request = _models.GetTeamRolesRequest(
            path=_models.GetTeamRolesRequestPath(team_key=team_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_team_roles: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/teams/{teamKey}/roles", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/teams/{teamKey}/roles"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_team_roles")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_team_roles", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_team_roles",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Workflow templates
@mcp.tool()
async def list_workflow_templates(
    summary: bool | None = Field(None, description="Return lightweight template summaries instead of full template objects. When true, returns only essential metadata; when false or omitted, returns complete template details."),
    search: str | None = Field(None, description="Filter templates by searching for a substring within template names or descriptions. The search is case-sensitive and matches partial strings."),
) -> dict[str, Any]:
    """Retrieve workflow templates for your account with optional filtering and summary mode. Use the summary parameter to get lightweight template metadata or the search parameter to filter templates by name or description."""

    # Construct request model with validation
    try:
        _request = _models.GetWorkflowTemplatesRequest(
            query=_models.GetWorkflowTemplatesRequestQuery(summary=summary, search=search)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_workflow_templates: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v2/templates"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_workflow_templates")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_workflow_templates", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_workflow_templates",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Access tokens
@mcp.tool()
async def get_token(id_: str = Field(..., alias="id", description="The unique identifier of the access token to retrieve.")) -> dict[str, Any]:
    """Retrieve a single access token by its unique identifier. Use this to fetch details about a specific token for inspection or validation purposes."""

    # Construct request model with validation
    try:
        _request = _models.GetTokenRequest(
            path=_models.GetTokenRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_token: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/tokens/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/tokens/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_token")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_token", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_token",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Access tokens
@mcp.tool()
async def update_token(
    id_: str = Field(..., alias="id", description="The unique identifier of the access token to update."),
    body: list[_models.PatchOperation] = Field(..., description="An array of JSON Patch operations describing the changes to apply. Each operation must include 'op' (the operation type), 'path' (the token property to modify), and 'value' (the new value for replace operations). Operations are applied in order."),
) -> dict[str, Any]:
    """Update an access token's settings using JSON Patch operations. Specify the changes you want to make (such as modifying the role) in RFC 6902 patch format."""

    # Construct request model with validation
    try:
        _request = _models.PatchTokenRequest(
            path=_models.PatchTokenRequestPath(id_=id_),
            body=_models.PatchTokenRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_token: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/tokens/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/tokens/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_token")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_token", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_token",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Access tokens
@mcp.tool()
async def delete_token(id_: str = Field(..., alias="id", description="The unique identifier of the access token to delete. This is a string value that uniquely identifies the token in the system.")) -> dict[str, Any]:
    """Permanently delete an access token by its ID. This operation removes the token immediately, invalidating any authentication attempts using it."""

    # Construct request model with validation
    try:
        _request = _models.DeleteTokenRequest(
            path=_models.DeleteTokenRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_token: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/tokens/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/tokens/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_token")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_token", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_token",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Access tokens
@mcp.tool()
async def reset_token(
    id_: str = Field(..., alias="id", description="The unique identifier of the access token to reset."),
    expiry: str | None = Field(None, description="Optional Unix epoch time in milliseconds when the old token key should expire. If not provided, the old key expires immediately upon reset."),
) -> dict[str, Any]:
    """Generate a new secret key for an access token, optionally setting an expiration time for the old key. Use this to rotate credentials while maintaining token validity."""

    _expiry = _parse_int(expiry)

    # Construct request model with validation
    try:
        _request = _models.ResetTokenRequest(
            path=_models.ResetTokenRequestPath(id_=id_),
            query=_models.ResetTokenRequestQuery(expiry=_expiry)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for reset_token: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/tokens/{id}/reset", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/tokens/{id}/reset"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("reset_token")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("reset_token", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="reset_token",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Account usage (beta)
@mcp.tool()
async def get_events_usage_by_type(
    type_: str = Field(..., alias="type", description="The event category to retrieve usage data for. Must be either 'received' (events received by the system) or 'published' (events published by the system)."),
    from_: str | None = Field(None, alias="from", description="ISO 8601 timestamp marking the start of the requested data range. If not provided, defaults to 24 hours before the 'to' timestamp."),
    to: str | None = Field(None, description="ISO 8601 timestamp marking the end of the requested data range. If not provided, defaults to the current time."),
) -> dict[str, Any]:
    """Retrieve time-series data showing how many times a flag was evaluated and which variation resulted from each evaluation. Data granularity automatically adjusts based on age: minutely for the past 2 hours, hourly for the past 2 days, and daily for older data."""

    # Construct request model with validation
    try:
        _request = _models.GetEventsUsageRequest(
            path=_models.GetEventsUsageRequestPath(type_=type_),
            query=_models.GetEventsUsageRequestQuery(from_=from_, to=to)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_events_usage_by_type: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/usage/events/{type}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/usage/events/{type}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_events_usage_by_type")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_events_usage_by_type", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_events_usage_by_type",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Webhooks
@mcp.tool()
async def list_webhooks() -> dict[str, Any]:
    """Retrieve a complete list of all configured webhooks for the account. Use this to view all active webhook endpoints and their configurations."""

    # Extract parameters for API call
    _http_path = "/api/v2/webhooks"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_webhooks")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_webhooks", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_webhooks",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Webhooks
@mcp.tool()
async def get_webhook(id_: str = Field(..., alias="id", description="The unique identifier of the webhook to retrieve.")) -> dict[str, Any]:
    """Retrieve a single webhook by its unique identifier. Use this to fetch detailed information about a specific webhook configuration."""

    # Construct request model with validation
    try:
        _request = _models.GetWebhookRequest(
            path=_models.GetWebhookRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_webhook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/webhooks/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/webhooks/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_webhook")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_webhook", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_webhook",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Webhooks
@mcp.tool()
async def update_webhook(
    id_: str = Field(..., alias="id", description="The unique identifier of the webhook to update."),
    body: list[_models.PatchOperation] = Field(..., description="An array of JSON Patch operations describing the changes to apply. Each operation must include an 'op' field (e.g., 'replace'), a 'path' field indicating which property to modify, and a 'value' field with the new value."),
) -> dict[str, Any]:
    """Update a webhook's configuration using JSON Patch operations. Specify the changes you want to make (such as enabling/disabling the webhook) as an array of patch operations."""

    # Construct request model with validation
    try:
        _request = _models.PatchWebhookRequest(
            path=_models.PatchWebhookRequestPath(id_=id_),
            body=_models.PatchWebhookRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_webhook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/webhooks/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/webhooks/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_webhook")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_webhook", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_webhook",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Webhooks
@mcp.tool()
async def delete_webhook(id_: str = Field(..., alias="id", description="The unique identifier of the webhook to delete. This is a string value that uniquely identifies the webhook in the system.")) -> dict[str, Any]:
    """Permanently delete a webhook by its ID. This action cannot be undone and will stop all event notifications from being sent to the webhook's configured endpoint."""

    # Construct request model with validation
    try:
        _request = _models.DeleteWebhookRequest(
            path=_models.DeleteWebhookRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_webhook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/webhooks/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/webhooks/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_webhook")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_webhook", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_webhook",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tags
@mcp.tool()
async def list_tags(
    kind: list[str] | None = Field(None, description="Filter tags by resource type. Accepts multiple types including flag, project, environment, segment, metric, metric-data-source, aiconfig, and view. If not specified, returns tags of all types."),
    pre: str | None = Field(None, description="Return only tags that begin with the specified prefix string."),
    archived: bool | None = Field(None, description="Include or exclude archived tags in the results. When true, returns archived tags; when false or omitted, returns only active tags."),
    as_of: str | None = Field(None, alias="asOf", description="Retrieve tags as they existed at a specific point in time, specified in ISO 8601 format. Defaults to the current time if not provided."),
) -> dict[str, Any]:
    """Retrieve a list of tags, optionally filtered by resource type, prefix, or archived status, and as of a specific point in time."""

    # Construct request model with validation
    try:
        _request = _models.GetTagsRequest(
            query=_models.GetTagsRequestQuery(kind=kind, pre=pre, archived=archived, as_of=as_of)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_tags: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v2/tags"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_tags")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_tags", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_tags",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: AI Configs
@mcp.tool()
async def get_ai_config_targeting(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the AI Config."),
    config_key: str = Field(..., alias="configKey", description="The unique identifier for the AI Config whose targeting configuration should be retrieved."),
) -> dict[str, Any]:
    """Retrieve the targeting configuration for a specific AI Config. Returns the targeting rules and criteria that determine which users or contexts this AI Config applies to."""

    # Construct request model with validation
    try:
        _request = _models.GetAiConfigTargetingRequest(
            path=_models.GetAiConfigTargetingRequestPath(project_key=project_key, config_key=config_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_ai_config_targeting: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/ai-configs/{configKey}/targeting", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/ai-configs/{configKey}/targeting"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_ai_config_targeting")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_ai_config_targeting", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_ai_config_targeting",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: AI Configs
@mcp.tool()
async def update_ai_config_targeting(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the LaunchDarkly project containing the AI Config."),
    config_key: str = Field(..., alias="configKey", description="The unique identifier for the AI Config to update."),
    environment_key: str = Field(..., alias="environmentKey", description="The unique identifier for the LaunchDarkly environment where the AI Config targeting applies."),
    instructions: list[dict[str, Any]] = Field(..., description="An array of semantic patch instructions that define the targeting changes to apply. Each instruction must include a `kind` property specifying the operation type (e.g., addRule, addClauses, removeTargets) and relevant parameters for that operation. Instructions are processed in order."),
) -> dict[str, Any]:
    """Update an AI Config's targeting rules, variations, and rollouts using semantic patch instructions. Supports adding/removing rules and clauses, managing individual context targets, and configuring percentage-based rollouts."""

    # Construct request model with validation
    try:
        _request = _models.PatchAiConfigTargetingRequest(
            path=_models.PatchAiConfigTargetingRequestPath(project_key=project_key, config_key=config_key),
            body=_models.PatchAiConfigTargetingRequestBody(environment_key=environment_key, instructions=instructions)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_ai_config_targeting: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/ai-configs/{configKey}/targeting", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/ai-configs/{configKey}/targeting"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_ai_config_targeting")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_ai_config_targeting", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_ai_config_targeting",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: AI Configs
@mcp.tool()
async def list_ai_configs(project_key: str = Field(..., alias="projectKey", description="The unique identifier of the project. Use the project key (e.g., 'default') to specify which project's AI Configs to retrieve.")) -> dict[str, Any]:
    """Retrieve all AI Configs available in a specified project. Returns a list of AI configuration objects that define AI behavior and settings for the project."""

    # Construct request model with validation
    try:
        _request = _models.GetAiConfigsRequest(
            path=_models.GetAiConfigsRequestPath(project_key=project_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_ai_configs: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/ai-configs", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/ai-configs"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_ai_configs")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_ai_configs", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_ai_configs",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: AI Configs
@mcp.tool()
async def create_ai_config(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier of the project where the AI Config will be created."),
    key: str = Field(..., description="A unique identifier for the AI Config within the project, used for referencing and management."),
    default_variation_key: str = Field(..., alias="defaultVariationKey", description="A unique identifier for the default variation of this AI Config."),
    name: str = Field(..., description="The display name of the AI Config."),
    default_variation_name: str = Field(..., alias="defaultVariationName", description="The display name of the default variation."),
    description: str | None = Field(None, description="Optional description of the AI Config to provide context about its purpose and usage."),
    mode: Literal["agent", "completion", "judge"] | None = Field(None, description="The operational mode of the AI Config. Choose 'completion' for standard text generation, 'agent' for agentic behavior with instructions, or 'judge' for evaluation purposes. Defaults to 'completion'."),
    tags: list[str] | None = Field(None, description="Optional array of tags for categorizing and organizing the AI Config."),
    instructions: str | None = Field(None, description="Instructions for agent behavior. Only applicable and returned when the mode is set to 'agent'."),
    messages: list[_models.Message] | None = Field(None, description="Optional array of messages that define the conversation context or system prompts for the AI Config."),
    model_config_key: str | None = Field(None, alias="modelConfigKey", description="Optional reference to a model configuration key that specifies the underlying model settings and parameters."),
    judges: list[_models.JudgeAttachment] | None = Field(None, description="Optional array of judges attached to this variation for evaluation purposes. When provided, this replaces all existing judge attachments; an empty array removes all judges."),
    evaluation_metric_key: str | None = Field(None, alias="evaluationMetricKey", description="Optional key referencing an evaluation metric to assess the performance of this AI Config."),
    is_inverted: bool | None = Field(None, alias="isInverted", description="Optional boolean flag indicating whether the evaluation metric is inverted, meaning lower values indicate better performance when set to true."),
) -> dict[str, Any]:
    """Create a new AI Config within a project to define AI model behavior, variations, and evaluation criteria. Supports multiple modes (completion, agent, or judge) with customizable instructions, messages, and evaluation metrics."""

    # Construct request model with validation
    try:
        _request = _models.PostAiConfigRequest(
            path=_models.PostAiConfigRequestPath(project_key=project_key),
            body=_models.PostAiConfigRequestBody(description=description, key=key, mode=mode, name=name, tags=tags, evaluation_metric_key=evaluation_metric_key, is_inverted=is_inverted,
                default_variation=_models.PostAiConfigRequestBodyDefaultVariation(
                    key=default_variation_key, name=default_variation_name, instructions=instructions, messages=messages, model_config_key=model_config_key,
                    judge_configuration=_models.PostAiConfigRequestBodyDefaultVariationJudgeConfiguration(judges=judges) if any(v is not None for v in [judges]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_ai_config: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/ai-configs", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/ai-configs"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_ai_config")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_ai_config", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_ai_config",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: AI Configs
@mcp.tool()
async def get_ai_config(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the AI configuration."),
    config_key: str = Field(..., alias="configKey", description="The unique identifier for the specific AI configuration to retrieve."),
) -> dict[str, Any]:
    """Retrieve a specific AI configuration by its project and configuration keys. Use this to fetch detailed settings and properties for a particular AI config within a project."""

    # Construct request model with validation
    try:
        _request = _models.GetAiConfigRequest(
            path=_models.GetAiConfigRequestPath(project_key=project_key, config_key=config_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_ai_config: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/ai-configs/{configKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/ai-configs/{configKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_ai_config")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_ai_config", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_ai_config",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: AI Configs
@mcp.tool()
async def update_ai_config(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the AI Config to update."),
    config_key: str = Field(..., alias="configKey", description="The unique identifier for the AI Config to update."),
    name: str | None = Field(None, description="The new name for the AI Config."),
    tags: list[str] | None = Field(None, description="A list of tags to associate with the AI Config. Tags are used for organization and filtering."),
    evaluation_metric_key: str | None = Field(None, alias="evaluationMetricKey", description="The unique identifier of the evaluation metric to use for assessing this AI Config's performance."),
    is_inverted: bool | None = Field(None, alias="isInverted", description="Set to true if the evaluation metric is inverted, meaning lower values indicate better performance. Set to false if higher values are better."),
) -> dict[str, Any]:
    """Update an existing AI Config by modifying specific fields. Only the fields included in the request body will be updated; other fields remain unchanged."""

    # Construct request model with validation
    try:
        _request = _models.PatchAiConfigRequest(
            path=_models.PatchAiConfigRequestPath(project_key=project_key, config_key=config_key),
            body=_models.PatchAiConfigRequestBody(name=name, tags=tags, evaluation_metric_key=evaluation_metric_key, is_inverted=is_inverted)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_ai_config: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/ai-configs/{configKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/ai-configs/{configKey}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_ai_config")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_ai_config", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_ai_config",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: AI Configs
@mcp.tool()
async def delete_ai_config(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier of the project containing the AI Config. Use 'default' for the default project or specify a custom project key."),
    config_key: str = Field(..., alias="configKey", description="The unique identifier of the AI Config to delete."),
) -> dict[str, Any]:
    """Permanently delete an AI Config from a project. This operation removes the configuration and cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteAiConfigRequest(
            path=_models.DeleteAiConfigRequestPath(project_key=project_key, config_key=config_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_ai_config: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/ai-configs/{configKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/ai-configs/{configKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_ai_config")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_ai_config", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_ai_config",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: AI Configs
@mcp.tool()
async def create_ai_config_variation(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier of the project containing the AI Config."),
    config_key: str = Field(..., alias="configKey", description="The unique identifier of the AI Config for which to create a variation."),
    key: str = Field(..., description="The unique identifier for this variation within the AI Config."),
    name: str = Field(..., description="A human-readable name for this variation to distinguish it from other variations of the same AI Config."),
    instructions: str | None = Field(None, description="Instructions for the agent behavior. Only applicable and returned for agent-type variations."),
    messages: list[_models.Message] | None = Field(None, description="Array of message objects defining the conversation or prompt structure for this variation. Order and format depend on the model type."),
    model_config_key: str | None = Field(None, alias="modelConfigKey", description="Optional reference to a model configuration key. If provided, uses a predefined model configuration; otherwise, model details must be specified in the request body."),
    judges: list[_models.JudgeAttachment] | None = Field(None, description="List of judge configurations for evaluating this variation. When provided, replaces all existing judges; an empty array removes all judge attachments."),
) -> dict[str, Any]:
    """Create a new variation for an AI Config, specifying model configuration, instructions, and optional judges for evaluation."""

    # Construct request model with validation
    try:
        _request = _models.PostAiConfigVariationRequest(
            path=_models.PostAiConfigVariationRequestPath(project_key=project_key, config_key=config_key),
            body=_models.PostAiConfigVariationRequestBody(instructions=instructions, key=key, messages=messages, name=name, model_config_key=model_config_key,
                judge_configuration=_models.PostAiConfigVariationRequestBodyJudgeConfiguration(judges=judges) if any(v is not None for v in [judges]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_ai_config_variation: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/ai-configs/{configKey}/variations", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/ai-configs/{configKey}/variations"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_ai_config_variation")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_ai_config_variation", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_ai_config_variation",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: AI Configs
@mcp.tool()
async def get_ai_config_variation(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the AI Config. Use 'default' for the default project."),
    config_key: str = Field(..., alias="configKey", description="The unique identifier for the AI Config within the project. Use 'default' for the default configuration."),
    variation_key: str = Field(..., alias="variationKey", description="The unique identifier for the specific variation within the AI Config. Use 'default' for the default variation."),
) -> dict[str, Any]:
    """Retrieve a specific AI Config variation by its key, including all versions associated with that variation."""

    # Construct request model with validation
    try:
        _request = _models.GetAiConfigVariationRequest(
            path=_models.GetAiConfigVariationRequestPath(project_key=project_key, config_key=config_key, variation_key=variation_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_ai_config_variation: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/ai-configs/{configKey}/variations/{variationKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/ai-configs/{configKey}/variations/{variationKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_ai_config_variation")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_ai_config_variation", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_ai_config_variation",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: AI Configs
@mcp.tool()
async def update_ai_config_variation(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the AI Config."),
    config_key: str = Field(..., alias="configKey", description="The unique identifier for the AI Config containing the variation to update."),
    variation_key: str = Field(..., alias="variationKey", description="The unique identifier for the variation to update."),
    instructions: str | None = Field(None, description="Instructions that guide the agent's behavior when this AI Config operates in agent mode."),
    messages: list[_models.Message] | None = Field(None, description="Array of message objects defining the conversation structure. Each message has a role (e.g., 'system', 'user', 'assistant') and content text. Order matters and represents the conversation sequence."),
    model_config_key: str | None = Field(None, alias="modelConfigKey", description="The unique identifier for the model configuration to use with this variation."),
    name: str | None = Field(None, description="A human-readable name for this variation."),
    state: str | None = Field(None, description="The lifecycle state of the variation. Must be either 'archived' to hide the variation or 'published' to make it active."),
    judges: list[_models.JudgeAttachment] | None = Field(None, description="Array of judge objects that evaluate this variation's performance. Replaces all existing judges; provide an empty array to remove all judge attachments."),
) -> dict[str, Any]:
    """Update an existing AI Config variation by modifying its properties. Changes create a new version of the variation while preserving the original."""

    # Construct request model with validation
    try:
        _request = _models.PatchAiConfigVariationRequest(
            path=_models.PatchAiConfigVariationRequestPath(project_key=project_key, config_key=config_key, variation_key=variation_key),
            body=_models.PatchAiConfigVariationRequestBody(instructions=instructions, messages=messages, model_config_key=model_config_key, name=name, state=state,
                judge_configuration=_models.PatchAiConfigVariationRequestBodyJudgeConfiguration(judges=judges) if any(v is not None for v in [judges]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_ai_config_variation: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/ai-configs/{configKey}/variations/{variationKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/ai-configs/{configKey}/variations/{variationKey}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_ai_config_variation")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_ai_config_variation", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_ai_config_variation",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: AI Configs
@mcp.tool()
async def delete_ai_config_variation(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the AI Config."),
    config_key: str = Field(..., alias="configKey", description="The unique identifier for the AI Config whose variation should be deleted."),
    variation_key: str = Field(..., alias="variationKey", description="The unique identifier for the specific variation to delete."),
) -> dict[str, Any]:
    """Permanently delete a specific variation of an AI Config. This removes the variation and all its associated data from the project."""

    # Construct request model with validation
    try:
        _request = _models.DeleteAiConfigVariationRequest(
            path=_models.DeleteAiConfigVariationRequestPath(project_key=project_key, config_key=config_key, variation_key=variation_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_ai_config_variation: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/ai-configs/{configKey}/variations/{variationKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/ai-configs/{configKey}/variations/{variationKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_ai_config_variation")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_ai_config_variation", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_ai_config_variation",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: AI Configs
@mcp.tool()
async def get_ai_config_quick_stats(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the AI Configs. This key determines which project's statistics will be retrieved."),
    env: str = Field(..., description="The environment key that filters which metrics are included in the results. Only statistics from this specific environment will be returned."),
) -> dict[str, Any]:
    """Retrieve aggregate quick statistics for AI Configs within a specific project and environment. Returns metrics summarizing AI Config usage and performance for the specified environment."""

    # Construct request model with validation
    try:
        _request = _models.GetAiConfigQuickStatsRequest(
            path=_models.GetAiConfigQuickStatsRequestPath(project_key=project_key),
            query=_models.GetAiConfigQuickStatsRequestQuery(env=env)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_ai_config_quick_stats: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/ai-configs/quick-stats", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/ai-configs/quick-stats"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_ai_config_quick_stats")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_ai_config_quick_stats", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_ai_config_quick_stats",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: AI Configs
@mcp.tool()
async def get_ai_config_metrics(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the AI Config."),
    config_key: str = Field(..., alias="configKey", description="The unique identifier for the AI Config whose metrics should be retrieved."),
    from_: int = Field(..., alias="from", description="The start of the metrics time range as milliseconds since epoch (inclusive). Use this to define the beginning of your analysis period."),
    to: int = Field(..., description="The end of the metrics time range as milliseconds since epoch (exclusive). The time range between `from` and `to` cannot exceed 100 days."),
    env: str = Field(..., description="The environment key to filter metrics by. Only metrics collected in this specific environment will be included in the results."),
) -> dict[str, Any]:
    """Retrieve usage and performance metrics for a specific AI Config within a defined time range and environment. Metrics are aggregated for the specified period to help monitor AI Config performance and usage patterns."""

    # Construct request model with validation
    try:
        _request = _models.GetAiConfigMetricsRequest(
            path=_models.GetAiConfigMetricsRequestPath(project_key=project_key, config_key=config_key),
            query=_models.GetAiConfigMetricsRequestQuery(from_=from_, to=to, env=env)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_ai_config_metrics: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/ai-configs/{configKey}/metrics", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/ai-configs/{configKey}/metrics"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_ai_config_metrics")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_ai_config_metrics", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_ai_config_metrics",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: AI Configs
@mcp.tool()
async def get_ai_config_metrics_by_variation(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the AI Config."),
    config_key: str = Field(..., alias="configKey", description="The unique identifier for the AI Config whose metrics you want to retrieve."),
    from_: int = Field(..., alias="from", description="The start of the time range for metrics, specified as milliseconds since epoch (inclusive)."),
    to: int = Field(..., description="The end of the time range for metrics, specified as milliseconds since epoch (exclusive). The time range cannot span more than 100 days."),
    env: str = Field(..., description="The environment key to filter metrics. Only metrics from this specific environment will be included in the results."),
) -> dict[str, Any]:
    """Retrieve usage and performance metrics for an AI Config segmented by variation. Results are filtered to a specific time range and environment."""

    # Construct request model with validation
    try:
        _request = _models.GetAiConfigMetricsByVariationRequest(
            path=_models.GetAiConfigMetricsByVariationRequestPath(project_key=project_key, config_key=config_key),
            query=_models.GetAiConfigMetricsByVariationRequestQuery(from_=from_, to=to, env=env)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_ai_config_metrics_by_variation: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/ai-configs/{configKey}/metrics-by-variation", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/ai-configs/{configKey}/metrics-by-variation"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_ai_config_metrics_by_variation")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_ai_config_metrics_by_variation", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_ai_config_metrics_by_variation",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: AI Configs
@mcp.tool()
async def add_restricted_models(
    project_key: str = Field(..., alias="projectKey", description="The project key that identifies which project's restricted model list to update. Use the project key from your LaunchDarkly workspace (e.g., 'default')."),
    keys: list[str] = Field(..., description="An array of AI model keys to add to the restricted list. Each key must be a valid model key returned by the List AI model configs endpoint. Duplicate keys in the array will be deduplicated."),
) -> dict[str, Any]:
    """Add one or more AI models to the restricted list for a project. Restricted models cannot be used in AI configurations for that project. Model keys are obtained from the List AI model configs endpoint."""

    # Construct request model with validation
    try:
        _request = _models.PostRestrictedModelsRequest(
            path=_models.PostRestrictedModelsRequestPath(project_key=project_key),
            body=_models.PostRestrictedModelsRequestBody(keys=keys)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_restricted_models: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/ai-configs/model-configs/restricted", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/ai-configs/model-configs/restricted"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_restricted_models")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_restricted_models", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_restricted_models",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: AI Configs
@mcp.tool()
async def remove_restricted_models(
    project_key: str = Field(..., alias="projectKey", description="The project identifier (e.g., 'default') that contains the restricted model list to modify."),
    keys: list[str] = Field(..., description="An array of model keys to remove from the restricted list. Each key identifies a specific model to unrestrict."),
) -> dict[str, Any]:
    """Remove one or more AI models from the project's restricted list by their keys. This allows previously restricted models to be used again in the project."""

    # Construct request model with validation
    try:
        _request = _models.DeleteRestrictedModelsRequest(
            path=_models.DeleteRestrictedModelsRequestPath(project_key=project_key),
            body=_models.DeleteRestrictedModelsRequestBody(keys=keys)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_restricted_models: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/ai-configs/model-configs/restricted", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/ai-configs/model-configs/restricted"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_restricted_models")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_restricted_models", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_restricted_models",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: AI Configs
@mcp.tool()
async def list_model_configs(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project (e.g., 'default'). This determines which project's model configurations are returned."),
    restricted: bool | None = Field(None, description="When set to true, returns only model configurations that are restricted. Omit or set to false to return all configurations."),
) -> dict[str, Any]:
    """Retrieve all AI model configurations for a specified project. Optionally filter to show only restricted models."""

    # Construct request model with validation
    try:
        _request = _models.ListModelConfigsRequest(
            path=_models.ListModelConfigsRequestPath(project_key=project_key),
            query=_models.ListModelConfigsRequestQuery(restricted=restricted)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_model_configs: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/ai-configs/model-configs", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/ai-configs/model-configs"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_model_configs")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_model_configs", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_model_configs",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: AI Configs
@mcp.tool()
async def create_model_config(
    project_key: str = Field(..., alias="projectKey", description="The project identifier where this model configuration will be created (e.g., 'default')."),
    name: str = Field(..., description="A human-readable display name for the model that will appear in the UI."),
    key: str = Field(..., description="A unique identifier key for this model configuration within the project, used for internal references and API calls."),
    id_: str = Field(..., alias="id", description="The model identifier recognized by the third-party provider (e.g., 'gpt-4', 'claude-3-opus'). This is the identifier sent to the provider's API."),
    icon: str | None = Field(None, description="An optional icon identifier or URL to visually represent this model in the UI."),
    provider: str | None = Field(None, description="The AI service provider for this model (e.g., 'openai', 'anthropic', 'google'). Determines how requests are routed and authenticated."),
    params: dict[str, Any] | None = Field(None, description="Optional object containing provider-specific parameters and configuration settings for this model."),
    custom_params: dict[str, Any] | None = Field(None, alias="customParams", description="Optional object for custom parameters specific to your implementation or use case."),
    tags: list[str] | None = Field(None, description="Optional array of tags for categorizing and organizing this model configuration."),
    cost_per_input_token: float | None = Field(None, alias="costPerInputToken", description="The cost in USD per input token for this model, used for tracking and billing calculations."),
    cost_per_output_token: float | None = Field(None, alias="costPerOutputToken", description="The cost in USD per output token for this model, used for tracking and billing calculations."),
) -> dict[str, Any]:
    """Create a new AI model configuration for your project. This configuration defines model identity, provider details, and cost metrics for use across AI features in your project."""

    # Construct request model with validation
    try:
        _request = _models.PostModelConfigRequest(
            path=_models.PostModelConfigRequestPath(project_key=project_key),
            body=_models.PostModelConfigRequestBody(name=name, key=key, id_=id_, icon=icon, provider=provider, params=params, custom_params=custom_params, tags=tags, cost_per_input_token=cost_per_input_token, cost_per_output_token=cost_per_output_token)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_model_config: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/ai-configs/model-configs", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/ai-configs/model-configs"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_model_config")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_model_config", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_model_config",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: AI Configs
@mcp.tool()
async def get_model_config(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the model configuration. Typically 'default' for standard projects."),
    model_config_key: str = Field(..., alias="modelConfigKey", description="The unique identifier for the AI model configuration to retrieve. Typically 'default' for the standard model configuration."),
) -> dict[str, Any]:
    """Retrieve a specific AI model configuration by its unique key within a project. Use this to fetch detailed settings and parameters for a configured AI model."""

    # Construct request model with validation
    try:
        _request = _models.GetModelConfigRequest(
            path=_models.GetModelConfigRequestPath(project_key=project_key, model_config_key=model_config_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_model_config: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/ai-configs/model-configs/{modelConfigKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/ai-configs/model-configs/{modelConfigKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_model_config")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_model_config", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_model_config",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: AI Configs
@mcp.tool()
async def delete_model_config(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier of the project containing the model config. Use 'default' for the default project or specify a custom project key."),
    model_config_key: str = Field(..., alias="modelConfigKey", description="The unique identifier of the AI model configuration to delete."),
) -> dict[str, Any]:
    """Permanently delete an AI model configuration from a project. This operation removes the specified model config and cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteModelConfigRequest(
            path=_models.DeleteModelConfigRequestPath(project_key=project_key, model_config_key=model_config_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_model_config: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/ai-configs/model-configs/{modelConfigKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/ai-configs/model-configs/{modelConfigKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_model_config")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_model_config", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_model_config",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: AI Configs
@mcp.tool()
async def list_ai_tools(project_key: str = Field(..., alias="projectKey", description="The unique identifier of the project containing the AI tools to retrieve.")) -> dict[str, Any]:
    """Retrieve all AI tools available in a specific project. Returns a complete list of configured AI tools that can be used within the project."""

    # Construct request model with validation
    try:
        _request = _models.ListAiToolsRequest(
            path=_models.ListAiToolsRequestPath(project_key=project_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_ai_tools: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/ai-tools", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/ai-tools"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_ai_tools")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_ai_tools", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_ai_tools",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: AI Configs
@mcp.tool()
async def create_ai_tool(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier of the project where the AI tool will be created."),
    key: str = Field(..., description="The unique identifier for the AI tool within the project. Used to reference this tool in subsequent operations."),
    schema_: dict[str, Any] = Field(..., alias="schema", description="A JSON Schema object that defines the tool's input parameters and their constraints. This schema is sent to the LLM to describe what inputs the tool accepts and how to invoke it."),
    custom_parameters: dict[str, Any] | None = Field(None, alias="customParameters", description="Optional object containing custom metadata and configuration settings for application-level use. These values are not exposed to the LLM and are used only by your application logic."),
) -> dict[str, Any]:
    """Create a new AI tool within a project that defines custom functionality for LLM consumption. The tool's parameters are specified via JSON Schema, with optional custom metadata for application-level configuration."""

    # Construct request model with validation
    try:
        _request = _models.PostAiToolRequest(
            path=_models.PostAiToolRequestPath(project_key=project_key),
            body=_models.PostAiToolRequestBody(key=key, schema_=schema_, custom_parameters=custom_parameters)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_ai_tool: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/ai-tools", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/ai-tools"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_ai_tool")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_ai_tool", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_ai_tool",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: AI Configs
@mcp.tool()
async def list_ai_tool_versions(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier of the project containing the AI tool."),
    tool_key: str = Field(..., alias="toolKey", description="The unique identifier of the AI tool for which to retrieve versions."),
) -> dict[str, Any]:
    """Retrieve all versions of a specific AI tool within a project. Returns a list of version records for the identified tool."""

    # Construct request model with validation
    try:
        _request = _models.ListAiToolVersionsRequest(
            path=_models.ListAiToolVersionsRequestPath(project_key=project_key, tool_key=tool_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_ai_tool_versions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/ai-tools/{toolKey}/versions", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/ai-tools/{toolKey}/versions"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_ai_tool_versions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_ai_tool_versions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_ai_tool_versions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: AI Configs
@mcp.tool()
async def get_ai_tool(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the AI tool."),
    tool_key: str = Field(..., alias="toolKey", description="The unique identifier for the AI tool to retrieve."),
) -> dict[str, Any]:
    """Retrieve a specific AI tool by its project and tool identifiers. Use this operation to fetch detailed information about a configured AI tool within a project."""

    # Construct request model with validation
    try:
        _request = _models.GetAiToolRequest(
            path=_models.GetAiToolRequestPath(project_key=project_key, tool_key=tool_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_ai_tool: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/ai-tools/{toolKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/ai-tools/{toolKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_ai_tool")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_ai_tool", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_ai_tool",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: AI Configs
@mcp.tool()
async def update_ai_tool(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the AI tool."),
    tool_key: str = Field(..., alias="toolKey", description="The unique identifier for the AI tool to be updated."),
    schema_: dict[str, Any] | None = Field(None, alias="schema", description="A JSON Schema object that defines the tool's input parameters and their constraints for LLM consumption. This schema is used by language models to understand how to invoke the tool correctly."),
    custom_parameters: dict[str, Any] | None = Field(None, alias="customParameters", description="Custom metadata and configuration settings for application-level use. These parameters are not exposed to or used by the LLM, allowing you to store tool-specific application logic and settings."),
) -> dict[str, Any]:
    """Update an existing AI tool's configuration, including its parameter schema for LLM consumption and custom application-level settings."""

    # Construct request model with validation
    try:
        _request = _models.PatchAiToolRequest(
            path=_models.PatchAiToolRequestPath(project_key=project_key, tool_key=tool_key),
            body=_models.PatchAiToolRequestBody(schema_=schema_, custom_parameters=custom_parameters)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_ai_tool: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/ai-tools/{toolKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/ai-tools/{toolKey}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_ai_tool")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_ai_tool", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_ai_tool",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: AI Configs
@mcp.tool()
async def delete_ai_tool(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier of the project containing the AI tool to delete."),
    tool_key: str = Field(..., alias="toolKey", description="The unique identifier of the AI tool to delete."),
) -> dict[str, Any]:
    """Permanently delete an AI tool from a project. This action cannot be undone and will remove the tool and all associated configurations."""

    # Construct request model with validation
    try:
        _request = _models.DeleteAiToolRequest(
            path=_models.DeleteAiToolRequestPath(project_key=project_key, tool_key=tool_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_ai_tool: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/ai-tools/{toolKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/ai-tools/{toolKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_ai_tool")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_ai_tool", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_ai_tool",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: AI Configs
@mcp.tool()
async def list_prompt_snippets(project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the prompt snippets to retrieve.")) -> dict[str, Any]:
    """Retrieve all prompt snippets available in a specific project. Prompt snippets are reusable text templates used to configure AI behavior and responses."""

    # Construct request model with validation
    try:
        _request = _models.ListPromptSnippetsRequest(
            path=_models.ListPromptSnippetsRequestPath(project_key=project_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_prompt_snippets: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/ai-configs/prompt-snippets", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/ai-configs/prompt-snippets"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_prompt_snippets")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_prompt_snippets", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_prompt_snippets",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: AI Configs
@mcp.tool()
async def create_prompt_snippet(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project where the prompt snippet will be created."),
    key: str = Field(..., description="A unique key identifier for the prompt snippet within the project, used for referencing the snippet in configurations."),
    name: str = Field(..., description="A human-readable name for the prompt snippet to help identify its purpose."),
    text: str = Field(..., description="The text content of the prompt snippet that will be stored and reused in AI configurations."),
) -> dict[str, Any]:
    """Create a new prompt snippet within a project to store reusable AI prompt text for use in AI configurations."""

    # Construct request model with validation
    try:
        _request = _models.PostPromptSnippetRequest(
            path=_models.PostPromptSnippetRequestPath(project_key=project_key),
            body=_models.PostPromptSnippetRequestBody(key=key, name=name, text=text)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_prompt_snippet: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/ai-configs/prompt-snippets", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/ai-configs/prompt-snippets"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_prompt_snippet")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_prompt_snippet", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_prompt_snippet",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: AI Configs
@mcp.tool()
async def get_prompt_snippet(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the prompt snippet."),
    snippet_key: str = Field(..., alias="snippetKey", description="The unique identifier for the prompt snippet to retrieve."),
) -> dict[str, Any]:
    """Retrieve a specific prompt snippet by its unique key within a project. Use this to fetch the full details of a saved prompt snippet for use in AI configurations."""

    # Construct request model with validation
    try:
        _request = _models.GetPromptSnippetRequest(
            path=_models.GetPromptSnippetRequestPath(project_key=project_key, snippet_key=snippet_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_prompt_snippet: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/ai-configs/prompt-snippets/{snippetKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/ai-configs/prompt-snippets/{snippetKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_prompt_snippet")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_prompt_snippet", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_prompt_snippet",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: AI Configs
@mcp.tool()
async def update_prompt_snippet(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier of the project containing the prompt snippet."),
    snippet_key: str = Field(..., alias="snippetKey", description="The unique identifier of the prompt snippet to update."),
    name: str | None = Field(None, description="The display name for the prompt snippet. If provided, updates the snippet's name."),
    text: str | None = Field(None, description="The text content of the prompt snippet. If provided, updates the snippet's template text."),
) -> dict[str, Any]:
    """Update an existing prompt snippet in a project, creating a new version with the modified content or metadata."""

    # Construct request model with validation
    try:
        _request = _models.PatchPromptSnippetRequest(
            path=_models.PatchPromptSnippetRequestPath(project_key=project_key, snippet_key=snippet_key),
            body=_models.PatchPromptSnippetRequestBody(name=name, text=text)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_prompt_snippet: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/ai-configs/prompt-snippets/{snippetKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/ai-configs/prompt-snippets/{snippetKey}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_prompt_snippet")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_prompt_snippet", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_prompt_snippet",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: AI Configs
@mcp.tool()
async def delete_prompt_snippet(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier of the project containing the prompt snippet to delete."),
    snippet_key: str = Field(..., alias="snippetKey", description="The unique identifier of the prompt snippet to delete."),
) -> dict[str, Any]:
    """Delete an existing prompt snippet from a project's AI configuration. This operation permanently removes the specified prompt snippet and cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeletePromptSnippetRequest(
            path=_models.DeletePromptSnippetRequestPath(project_key=project_key, snippet_key=snippet_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_prompt_snippet: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/ai-configs/prompt-snippets/{snippetKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/ai-configs/prompt-snippets/{snippetKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_prompt_snippet")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_prompt_snippet", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_prompt_snippet",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: AI Configs
@mcp.tool()
async def list_prompt_snippet_references(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the prompt snippet."),
    snippet_key: str = Field(..., alias="snippetKey", description="The unique identifier for the prompt snippet whose references you want to list."),
) -> dict[str, Any]:
    """Retrieve all AI Config variations that currently reference a specific prompt snippet, helping you understand where a snippet is being used across your project."""

    # Construct request model with validation
    try:
        _request = _models.ListPromptSnippetReferencesRequest(
            path=_models.ListPromptSnippetReferencesRequestPath(project_key=project_key, snippet_key=snippet_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_prompt_snippet_references: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/ai-configs/prompt-snippets/{snippetKey}/references", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/ai-configs/prompt-snippets/{snippetKey}/references"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_prompt_snippet_references")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_prompt_snippet_references", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_prompt_snippet_references",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: AI Configs
@mcp.tool()
async def list_agent_graphs(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the agent graphs to list."),
    ld_api_version: Literal["beta"] = Field(..., alias="LD-API-Version", description="The API version to use for this request. Must be set to 'beta'."),
) -> dict[str, Any]:
    """Retrieve all agent graphs in a project with their metadata. Returns graph information without edge data for efficient listing."""

    # Construct request model with validation
    try:
        _request = _models.ListAgentGraphsRequest(
            path=_models.ListAgentGraphsRequestPath(project_key=project_key),
            header=_models.ListAgentGraphsRequestHeader(ld_api_version=ld_api_version)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_agent_graphs: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/agent-graphs", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/agent-graphs"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_agent_graphs")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_agent_graphs", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_agent_graphs",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: AI Configs
@mcp.tool()
async def create_agent_graph(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier of the project where the agent graph will be created."),
    ld_api_version: Literal["beta"] = Field(..., alias="LD-API-Version", description="The API version to use for this request. Currently only 'beta' is supported."),
    key: str = Field(..., description="A unique identifier for the agent graph within the project. Must be distinct from other graphs in the same project."),
    name: str = Field(..., description="A human-readable display name for the agent graph."),
    root_config_key: str | None = Field(None, alias="rootConfigKey", description="The AI Config key that serves as the root node of the graph. Required if edges are provided; omit both this and edges to create a metadata-only graph."),
    edges: list[_models.AgentGraphEdgePost] | None = Field(None, description="An array of edges defining connections between nodes in the graph. Each edge specifies the relationship between two nodes. Required if rootConfigKey is provided; both must be present together or both omitted."),
) -> dict[str, Any]:
    """Create a new agent graph within a project. The graph can be initialized with a root configuration node and edges, or created as metadata-only if neither is provided."""

    # Construct request model with validation
    try:
        _request = _models.PostAgentGraphRequest(
            path=_models.PostAgentGraphRequestPath(project_key=project_key),
            header=_models.PostAgentGraphRequestHeader(ld_api_version=ld_api_version),
            body=_models.PostAgentGraphRequestBody(key=key, name=name, root_config_key=root_config_key, edges=edges)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_agent_graph: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/agent-graphs", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/agent-graphs"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_agent_graph")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_agent_graph", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_agent_graph",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: AI Configs
@mcp.tool()
async def get_agent_graph(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the agent graph."),
    graph_key: str = Field(..., alias="graphKey", description="The unique identifier for the agent graph to retrieve."),
    ld_api_version: Literal["beta"] = Field(..., alias="LD-API-Version", description="The API version to use for this request. Currently only the beta version is supported."),
) -> dict[str, Any]:
    """Retrieve a specific agent graph by its key, including all its edges and configuration details."""

    # Construct request model with validation
    try:
        _request = _models.GetAgentGraphRequest(
            path=_models.GetAgentGraphRequestPath(project_key=project_key, graph_key=graph_key),
            header=_models.GetAgentGraphRequestHeader(ld_api_version=ld_api_version)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_agent_graph: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/agent-graphs/{graphKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/agent-graphs/{graphKey}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_agent_graph")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_agent_graph", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_agent_graph",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: AI Configs
@mcp.tool()
async def update_agent_graph(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the agent graph."),
    graph_key: str = Field(..., alias="graphKey", description="The unique identifier for the agent graph to update."),
    ld_api_version: Literal["beta"] = Field(..., alias="LD-API-Version", description="The API version to use for this request. Must be set to 'beta'."),
    name: str | None = Field(None, description="A human-readable name for the agent graph. Use this to provide a descriptive label for the graph."),
    root_config_key: str | None = Field(None, alias="rootConfigKey", description="The AI Config key designating the root node of the graph. When provided, edges must also be included in the same request, and both will completely replace existing values."),
    edges: list[_models.AgentGraphEdge] | None = Field(None, description="An ordered array of edges defining the graph structure and connections between nodes. When provided, rootConfigKey must also be included in the same request, and both will completely replace all existing edges."),
) -> dict[str, Any]:
    """Update an existing agent graph by modifying its configuration. Provide only the fields you want to change; unspecified fields retain their current values. If updating the root node or graph structure, both rootConfigKey and edges must be provided together as they are treated as a complete replacement."""

    # Construct request model with validation
    try:
        _request = _models.PatchAgentGraphRequest(
            path=_models.PatchAgentGraphRequestPath(project_key=project_key, graph_key=graph_key),
            header=_models.PatchAgentGraphRequestHeader(ld_api_version=ld_api_version),
            body=_models.PatchAgentGraphRequestBody(name=name, root_config_key=root_config_key, edges=edges)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_agent_graph: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/agent-graphs/{graphKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/agent-graphs/{graphKey}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_agent_graph")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_agent_graph", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_agent_graph",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: AI Configs
@mcp.tool()
async def delete_agent_graph(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the agent graph to delete."),
    graph_key: str = Field(..., alias="graphKey", description="The unique identifier for the agent graph to delete."),
    ld_api_version: Literal["beta"] = Field(..., alias="LD-API-Version", description="The API version to use for this request. Must be set to 'beta'."),
) -> dict[str, Any]:
    """Permanently delete an agent graph and all of its associated edges from a project. This operation cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteAgentGraphRequest(
            path=_models.DeleteAgentGraphRequestPath(project_key=project_key, graph_key=graph_key),
            header=_models.DeleteAgentGraphRequestHeader(ld_api_version=ld_api_version)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_agent_graph: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/agent-graphs/{graphKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/agent-graphs/{graphKey}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_agent_graph")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_agent_graph", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_agent_graph",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: AI Configs
@mcp.tool()
async def list_agent_optimizations(project_key: str = Field(..., alias="projectKey", description="The unique identifier of the project containing the agent optimizations to retrieve.")) -> dict[str, Any]:
    """Retrieve all agent optimizations configured for a specific project. Returns a list of optimization settings and configurations applied to agents within the project."""

    # Construct request model with validation
    try:
        _request = _models.ListAgentOptimizationsRequest(
            path=_models.ListAgentOptimizationsRequestPath(project_key=project_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_agent_optimizations: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/agent-optimizations", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/agent-optimizations"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_agent_optimizations")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_agent_optimizations", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_agent_optimizations",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: AI Configs
@mcp.tool()
async def create_agent_optimization(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier of the project where the agent optimization will be created."),
    key: str = Field(..., description="A unique key to identify this agent optimization configuration within the project."),
    ai_config_key: str = Field(..., alias="aiConfigKey", description="The key of the AI configuration that this optimization applies to."),
    max_attempts: int = Field(..., alias="maxAttempts", description="The maximum number of attempts the agent should make when trying to meet acceptance criteria. Must be a positive integer."),
    judge_model: str = Field(..., alias="judgeModel", description="The key of the model to use as the judge for evaluating agent performance against acceptance criteria."),
    model_choices: list[str] | None = Field(None, alias="modelChoices", description="An optional list of AI model identifiers to evaluate and compare during optimization. Order may indicate priority or evaluation sequence."),
    variable_choices: list[dict[str, Any]] | None = Field(None, alias="variableChoices", description="An optional list of variable configurations that the agent can choose from or adjust during optimization. Order may indicate priority or evaluation sequence."),
    acceptance_statements: list[_models.AgentOptimizationAcceptanceStatement] | None = Field(None, alias="acceptanceStatements", description="An optional list of acceptance criteria statements that define successful agent behavior. The agent must satisfy these conditions within the maximum attempts."),
    judges: list[_models.AgentOptimizationJudge] | None = Field(None, description="An optional list of judge configurations or identifiers used to evaluate agent responses. Multiple judges can provide consensus evaluation."),
    user_input_options: list[str] | None = Field(None, alias="userInputOptions", description="An optional list of user input options or scenarios that the agent should handle during optimization testing."),
    ground_truth_responses: list[str] | None = Field(None, alias="groundTruthResponses", description="An optional list of expected or reference responses used to measure agent accuracy and performance against ground truth."),
    metric_key: str | None = Field(None, alias="metricKey", description="An optional key referencing a specific metric to track and optimize for during the agent optimization process."),
) -> dict[str, Any]:
    """Create a new agent optimization configuration within a project to define how an AI agent should be evaluated and optimized using specified models, judges, and acceptance criteria."""

    # Construct request model with validation
    try:
        _request = _models.PostAgentOptimizationRequest(
            path=_models.PostAgentOptimizationRequestPath(project_key=project_key),
            body=_models.PostAgentOptimizationRequestBody(key=key, ai_config_key=ai_config_key, max_attempts=max_attempts, model_choices=model_choices, judge_model=judge_model, variable_choices=variable_choices, acceptance_statements=acceptance_statements, judges=judges, user_input_options=user_input_options, ground_truth_responses=ground_truth_responses, metric_key=metric_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_agent_optimization: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/agent-optimizations", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/agent-optimizations"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_agent_optimization")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_agent_optimization", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_agent_optimization",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: AI Configs
@mcp.tool()
async def get_agent_optimization(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the agent optimization."),
    optimization_key: str = Field(..., alias="optimizationKey", description="The unique identifier for the specific agent optimization to retrieve."),
) -> dict[str, Any]:
    """Retrieve a specific agent optimization configuration by its unique key within a project. Use this to inspect the details and settings of an existing optimization."""

    # Construct request model with validation
    try:
        _request = _models.GetAgentOptimizationRequest(
            path=_models.GetAgentOptimizationRequestPath(project_key=project_key, optimization_key=optimization_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_agent_optimization: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/agent-optimizations/{optimizationKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/agent-optimizations/{optimizationKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_agent_optimization")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_agent_optimization", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_agent_optimization",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: AI Configs
@mcp.tool()
async def update_agent_optimization(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier of the project containing the agent optimization."),
    optimization_key: str = Field(..., alias="optimizationKey", description="The unique identifier of the agent optimization to update."),
    max_attempts: int | None = Field(None, alias="maxAttempts", description="The maximum number of attempts allowed for the agent during optimization execution."),
    model_choices: list[str] | None = Field(None, alias="modelChoices", description="An ordered list of model identifiers to evaluate during optimization. Order may affect evaluation priority."),
    judge_model: str | None = Field(None, alias="judgeModel", description="The model identifier to use as a judge for evaluating agent performance against acceptance criteria."),
    variable_choices: list[dict[str, Any]] | None = Field(None, alias="variableChoices", description="An ordered list of variable configurations to test during optimization. Order may affect evaluation sequence."),
    acceptance_statements: list[_models.AgentOptimizationAcceptanceStatement] | None = Field(None, alias="acceptanceStatements", description="A list of acceptance criteria statements that define successful agent behavior. Each statement should clearly specify expected outcomes."),
    judges: list[_models.AgentOptimizationJudge] | None = Field(None, description="A list of judge configurations or identifiers used to evaluate agent responses. Multiple judges can be specified for consensus-based evaluation."),
    user_input_options: list[str] | None = Field(None, alias="userInputOptions", description="A list of user input options or scenarios to test during optimization. Defines the range of inputs the agent should handle."),
    ground_truth_responses: list[str] | None = Field(None, alias="groundTruthResponses", description="A list of ground truth responses corresponding to test inputs. Used as reference standards for evaluating agent accuracy."),
    metric_key: str | None = Field(None, alias="metricKey", description="The identifier of the metric to optimize against. Specifies which performance metric should be the primary optimization target."),
) -> dict[str, Any]:
    """Update an existing agent optimization configuration for a project. This operation creates a new version of the optimization with the provided changes."""

    # Construct request model with validation
    try:
        _request = _models.PatchAgentOptimizationRequest(
            path=_models.PatchAgentOptimizationRequestPath(project_key=project_key, optimization_key=optimization_key),
            body=_models.PatchAgentOptimizationRequestBody(max_attempts=max_attempts, model_choices=model_choices, judge_model=judge_model, variable_choices=variable_choices, acceptance_statements=acceptance_statements, judges=judges, user_input_options=user_input_options, ground_truth_responses=ground_truth_responses, metric_key=metric_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_agent_optimization: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/agent-optimizations/{optimizationKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/agent-optimizations/{optimizationKey}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_agent_optimization")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_agent_optimization", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_agent_optimization",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: AI Configs
@mcp.tool()
async def delete_agent_optimization(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier of the project containing the agent optimization to delete."),
    optimization_key: str = Field(..., alias="optimizationKey", description="The unique identifier of the agent optimization to delete."),
) -> dict[str, Any]:
    """Permanently delete an agent optimization configuration from a project. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteAgentOptimizationRequest(
            path=_models.DeleteAgentOptimizationRequestPath(project_key=project_key, optimization_key=optimization_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_agent_optimization: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/agent-optimizations/{optimizationKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/agent-optimizations/{optimizationKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_agent_optimization")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_agent_optimization", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_agent_optimization",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Announcements
@mcp.tool()
async def list_announcements(status: Literal["active", "inactive", "scheduled"] | None = Field(None, description="Filter announcements by their current status: active (published and visible), inactive (unpublished), or scheduled (queued for future publication).")) -> dict[str, Any]:
    """Retrieve a list of announcements filtered by their publication status. Use this to fetch active, inactive, or scheduled announcements for display or management purposes."""

    # Construct request model with validation
    try:
        _request = _models.GetAnnouncementsPublicRequest(
            query=_models.GetAnnouncementsPublicRequestQuery(status=status)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_announcements: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v2/announcements"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_announcements")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_announcements", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_announcements",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Announcements
@mcp.tool()
async def create_announcement(
    is_dismissible: bool = Field(..., alias="isDismissible", description="Whether users can dismiss this announcement from their view. Set to true to allow users to close the announcement, or false to make it persistent."),
    title: str = Field(..., description="A concise headline for the announcement (e.g., 'System Maintenance Notice'). This is the primary text users see first."),
    message: str = Field(..., description="The full announcement message body. Supports markdown formatting for emphasis, links, and structure. Use this to provide detailed information about the announcement."),
    start_time: str = Field(..., alias="startTime", description="The Unix timestamp in milliseconds when the announcement becomes visible to users. This marks the start of the announcement's active period."),
    severity: Literal["info", "warning", "critical"] = Field(..., description="The urgency level of the announcement. Use 'info' for general notices, 'warning' for important alerts, or 'critical' for urgent system issues requiring immediate attention."),
    end_time: str | None = Field(None, alias="endTime", description="The Unix timestamp in milliseconds when the announcement stops being displayed to users. If omitted, the announcement remains active indefinitely after the start time."),
) -> dict[str, Any]:
    """Create a new announcement to notify users about system events, maintenance, or important updates. The announcement will be displayed to users during the specified time window."""

    _start_time = _parse_int(start_time)
    _end_time = _parse_int(end_time)

    # Construct request model with validation
    try:
        _request = _models.CreateAnnouncementPublicRequest(
            body=_models.CreateAnnouncementPublicRequestBody(is_dismissible=is_dismissible, title=title, message=message, start_time=_start_time, end_time=_end_time, severity=severity)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_announcement: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v2/announcements"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_announcement")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_announcement", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_announcement",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Announcements
@mcp.tool()
async def update_announcement(
    announcement_id: str = Field(..., alias="announcementId", description="The unique identifier of the announcement to update, provided as a numeric string (e.g., '1234567890')."),
    body: list[_models.AnnouncementPatchOperation] = Field(..., description="An array of patch operations to apply to the announcement. Each operation specifies how to modify the announcement's properties."),
) -> dict[str, Any]:
    """Update an existing announcement by applying a series of changes. Specify the announcement to modify using its ID and provide the updates as an array of patch operations."""

    # Construct request model with validation
    try:
        _request = _models.UpdateAnnouncementPublicRequest(
            path=_models.UpdateAnnouncementPublicRequestPath(announcement_id=announcement_id),
            body=_models.UpdateAnnouncementPublicRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_announcement: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/announcements/{announcementId}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/announcements/{announcementId}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_announcement")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_announcement", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_announcement",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Announcements
@mcp.tool()
async def delete_announcement(announcement_id: str = Field(..., alias="announcementId", description="The unique identifier of the announcement to delete, provided as a numeric string (e.g., '1234567890').")) -> dict[str, Any]:
    """Permanently delete an announcement by its ID. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteAnnouncementPublicRequest(
            path=_models.DeleteAnnouncementPublicRequestPath(announcement_id=announcement_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_announcement: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/announcements/{announcementId}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/announcements/{announcementId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_announcement")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_announcement", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_announcement",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Approvals (beta)
@mcp.tool()
async def update_approval_request_settings_for_project_environment(
    project_key: str = Field(..., alias="projectKey", description="The project key that uniquely identifies the project containing the approval settings."),
    ld_api_version: Literal["beta"] = Field(..., alias="LD-API-Version", description="API version identifier. Must be set to 'beta' for this endpoint."),
    environment_key: str = Field(..., alias="environmentKey", description="The environment key that identifies which environment these approval settings apply to."),
    resource_kind: str = Field(..., alias="resourceKind", description="The type of resource these approval settings apply to."),
    auto_apply_approved_changes: bool | None = Field(None, alias="autoApplyApprovedChanges", description="Enable automatic application of changes once all required reviewers have approved them. Only applicable when using third-party approval services."),
    bypass_approvals_for_pending_changes: bool | None = Field(None, alias="bypassApprovalsForPendingChanges", description="Skip the approval process for changes that are currently pending review."),
    can_apply_declined_changes: bool | None = Field(None, alias="canApplyDeclinedChanges", description="Allow applying changes if at least one reviewer has approved, regardless of other reviewers' decisions."),
    can_review_own_request: bool | None = Field(None, alias="canReviewOwnRequest", description="Permit the person who created an approval request to also approve and apply their own change."),
    min_num_approvals: str | None = Field(None, alias="minNumApprovals", description="The number of approvals required before a change can be applied. Must be between 1 and 5 inclusive."),
    required: bool | None = Field(None, description="Whether approval is mandatory for changes in this environment."),
    required_approval_tags: list[str] | None = Field(None, alias="requiredApprovalTags", description="List of flag tags that trigger approval requirements. When specified, only flags with these tags require approval; otherwise all flags require approval."),
    service_config: dict[str, Any] | None = Field(None, alias="serviceConfig", description="Custom configuration object specific to the approval service being used."),
    service_kind: str | None = Field(None, alias="serviceKind", description="The approval service provider to use for managing approvals (e.g., 'launchdarkly' for native approvals)."),
    service_kind_configuration_id: str | None = Field(None, alias="serviceKindConfigurationId", description="Integration configuration ID for a custom approval service. This is an Enterprise-only feature and identifies which custom integration to use."),
) -> dict[str, Any]:
    """Update approval request settings for a specific environment within a project. Configure approval requirements, reviewer permissions, and integration settings for flag change approvals."""

    _min_num_approvals = _parse_int(min_num_approvals)

    # Construct request model with validation
    try:
        _request = _models.PatchApprovalRequestSettingsRequest(
            path=_models.PatchApprovalRequestSettingsRequestPath(project_key=project_key),
            header=_models.PatchApprovalRequestSettingsRequestHeader(ld_api_version=ld_api_version),
            body=_models.PatchApprovalRequestSettingsRequestBody(auto_apply_approved_changes=auto_apply_approved_changes, bypass_approvals_for_pending_changes=bypass_approvals_for_pending_changes, can_apply_declined_changes=can_apply_declined_changes, can_review_own_request=can_review_own_request, environment_key=environment_key, min_num_approvals=_min_num_approvals, required=required, required_approval_tags=required_approval_tags, resource_kind=resource_kind, service_config=service_config, service_kind=service_kind, service_kind_configuration_id=service_kind_configuration_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_approval_request_settings_for_project_environment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/approval-requests/projects/{projectKey}/settings", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/approval-requests/projects/{projectKey}/settings"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_approval_request_settings_for_project_environment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_approval_request_settings_for_project_environment", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_approval_request_settings_for_project_environment",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Views (beta)
@mcp.tool()
async def list_views(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project. Use 'default' for the default project or specify a custom project key."),
    ld_api_version: Literal["beta"] = Field(..., alias="LD-API-Version", description="API version specification. Must be set to 'beta' to access this endpoint."),
) -> dict[str, Any]:
    """Retrieve all views available in a specified project. Views are saved configurations or perspectives for organizing and displaying project data."""

    # Construct request model with validation
    try:
        _request = _models.GetViewsRequest(
            path=_models.GetViewsRequestPath(project_key=project_key),
            header=_models.GetViewsRequestHeader(ld_api_version=ld_api_version)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_views: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/views", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/views"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_views")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_views", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_views",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Views (beta)
@mcp.tool()
async def create_view(
    project_key: str = Field(..., alias="projectKey", description="The project key that uniquely identifies the project where the view will be created (e.g., 'default')."),
    ld_api_version: Literal["beta"] = Field(..., alias="LD-API-Version", description="The API version to use for this request. Currently only 'beta' is supported."),
    key: str = Field(..., description="A unique identifier for the view within the project. This key is used to reference the view in API calls and must be distinct from other views in the same project."),
    name: str = Field(..., description="A human-readable display name for the view that appears in the user interface."),
    generate_sdk_keys: bool | None = Field(None, alias="generateSdkKeys", description="Whether to automatically generate SDK keys associated with this view. Defaults to false if not specified."),
    tags: list[str] | None = Field(None, description="An optional list of tags to categorize and organize the view. Tags help with filtering and searching views."),
) -> dict[str, Any]:
    """Create a new view within a specified project. Views are used to organize and filter feature flags and other resources within your LaunchDarkly project."""

    # Construct request model with validation
    try:
        _request = _models.CreateViewRequest(
            path=_models.CreateViewRequestPath(project_key=project_key),
            header=_models.CreateViewRequestHeader(ld_api_version=ld_api_version),
            body=_models.CreateViewRequestBody(key=key, name=name, generate_sdk_keys=generate_sdk_keys, tags=tags)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_view: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/views", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/views"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_view")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_view", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_view",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Views (beta)
@mcp.tool()
async def get_view(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the view (e.g., 'default')."),
    view_key: str = Field(..., alias="viewKey", description="The unique identifier for the view to retrieve (e.g., 'my-view')."),
    ld_api_version: Literal["beta"] = Field(..., alias="LD-API-Version", description="The API version to use for this request. Must be set to 'beta'."),
) -> dict[str, Any]:
    """Retrieve a specific view by its project and view keys. Returns the view configuration and metadata for the specified view."""

    # Construct request model with validation
    try:
        _request = _models.GetViewRequest(
            path=_models.GetViewRequestPath(project_key=project_key, view_key=view_key),
            header=_models.GetViewRequestHeader(ld_api_version=ld_api_version)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_view: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/views/{viewKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/views/{viewKey}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_view")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_view", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_view",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Views (beta)
@mcp.tool()
async def update_view(
    project_key: str = Field(..., alias="projectKey", description="The project key that contains the view. Use the project identifier (e.g., 'default')."),
    view_key: str = Field(..., alias="viewKey", description="The view key that identifies which view to update (e.g., 'my-view')."),
    ld_api_version: Literal["beta"] = Field(..., alias="LD-API-Version", description="API version specification. Must be set to 'beta' for this endpoint."),
    name: str | None = Field(None, description="A human-readable name for the view. This is the display name users will see."),
    generate_sdk_keys: bool | None = Field(None, alias="generateSdkKeys", description="Whether to automatically generate SDK keys for this view. Set to true to enable SDK key generation."),
    tags: list[str] | None = Field(None, description="Tags to associate with this view for organization and filtering. Provide as an array of tag strings."),
    archived: bool | None = Field(None, description="Whether the view is archived. Set to true to archive the view, or false to unarchive it."),
) -> dict[str, Any]:
    """Update an existing view by replacing specified fields. Provide a JSON object containing only the fields you want to modify; unchanged fields retain their current values."""

    # Construct request model with validation
    try:
        _request = _models.UpdateViewRequest(
            path=_models.UpdateViewRequestPath(project_key=project_key, view_key=view_key),
            header=_models.UpdateViewRequestHeader(ld_api_version=ld_api_version),
            body=_models.UpdateViewRequestBody(name=name, generate_sdk_keys=generate_sdk_keys, tags=tags, archived=archived)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_view: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/views/{viewKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/views/{viewKey}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_view")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_view", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_view",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Views (beta)
@mcp.tool()
async def delete_view(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier of the project containing the view. Use the project key (e.g., 'default') to specify which project to access."),
    view_key: str = Field(..., alias="viewKey", description="The unique identifier of the view to delete. Specify the view key (e.g., 'my-view') to target the exact view for deletion."),
    ld_api_version: Literal["beta"] = Field(..., alias="LD-API-Version", description="The API version to use for this request. Must be set to 'beta' for this endpoint."),
) -> dict[str, Any]:
    """Permanently delete a specific view from a project by its key. This operation removes the view and cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteViewRequest(
            path=_models.DeleteViewRequestPath(project_key=project_key, view_key=view_key),
            header=_models.DeleteViewRequestHeader(ld_api_version=ld_api_version)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_view: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/views/{viewKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/views/{viewKey}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_view")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_view", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_view",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Views (beta)
@mcp.tool()
async def link_resources_to_view(
    project_key: str = Field(..., alias="projectKey", description="The project key that contains the view. Use the project identifier (e.g., 'default')."),
    view_key: str = Field(..., alias="viewKey", description="The view key where resources will be linked. Use the view identifier (e.g., 'my-view')."),
    resource_type: Literal["flags", "segments"] = Field(..., alias="resourceType", description="The type of resource to link. Must be either 'flags' or 'segments'."),
    ld_api_version: Literal["beta"] = Field(..., alias="LD-API-Version", description="The API version for this endpoint. Must be 'beta'."),
    body: _models.ViewLinkRequestKeys | _models.ViewLinkRequestSegmentIdentifiers | _models.ViewLinkRequestFilter = Field(..., description="Request body containing resource keys and/or filters to link. For flags, you can filter by maintainerId, maintainerTeamKey, tags, state, or query. For segments, you can filter by tags, query, or unbounded status."),
) -> dict[str, Any]:
    """Link one or multiple resources (flags or segments) to a view using resource keys, filters, or both. When both keys and filters are provided, resources matching either condition are linked."""

    # Construct request model with validation
    try:
        _request = _models.LinkResourceRequest(
            path=_models.LinkResourceRequestPath(project_key=project_key, view_key=view_key, resource_type=resource_type),
            header=_models.LinkResourceRequestHeader(ld_api_version=ld_api_version),
            body=_models.LinkResourceRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for link_resources_to_view: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/views/{viewKey}/link/{resourceType}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/views/{viewKey}/link/{resourceType}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("link_resources_to_view")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("link_resources_to_view", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="link_resources_to_view",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Views (beta)
@mcp.tool()
async def delete_view_resource_links(
    project_key: str = Field(..., alias="projectKey", description="The project key that contains the view. Use the project identifier (e.g., 'default')."),
    view_key: str = Field(..., alias="viewKey", description="The view key from which to unlink resources. Use the view identifier (e.g., 'my-view')."),
    resource_type: Literal["flags", "segments"] = Field(..., alias="resourceType", description="The type of resource to unlink: either 'flags' for feature flags or 'segments' for audience segments."),
    ld_api_version: Literal["beta"] = Field(..., alias="LD-API-Version", description="API version identifier. Must be set to 'beta' for this endpoint."),
    body: _models.ViewLinkRequestKeys | _models.ViewLinkRequestSegmentIdentifiers | _models.ViewLinkRequestFilter = Field(..., description="Request body containing the resource identifiers to unlink. For flags, provide flag keys; for segments, provide segment IDs."),
) -> dict[str, Any]:
    """Remove one or multiple linked resources (feature flags or segments) from a view. Specify the resource type and provide the identifiers to unlink."""

    # Construct request model with validation
    try:
        _request = _models.UnlinkResourceRequest(
            path=_models.UnlinkResourceRequestPath(project_key=project_key, view_key=view_key, resource_type=resource_type),
            header=_models.UnlinkResourceRequestHeader(ld_api_version=ld_api_version),
            body=_models.UnlinkResourceRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_view_resource_links: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/views/{viewKey}/link/{resourceType}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/views/{viewKey}/link/{resourceType}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_view_resource_links")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_view_resource_links", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_view_resource_links",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Views (beta)
@mcp.tool()
async def list_linked_resources_for_view(
    project_key: str = Field(..., alias="projectKey", description="The project key that identifies the project containing the view. Use the project's unique identifier (e.g., 'default')."),
    view_key: str = Field(..., alias="viewKey", description="The view key that identifies the specific view within the project. Use the view's unique identifier (e.g., 'my-view')."),
    resource_type: Literal["flags", "segments"] = Field(..., alias="resourceType", description="The type of linked resource to retrieve. Must be either 'flags' for feature flags or 'segments' for user segments."),
    ld_api_version: Literal["beta"] = Field(..., alias="LD-API-Version", description="The API version for this endpoint. Must be set to 'beta' to access this operation."),
    query: str | None = Field(None, description="Optional case-insensitive search filter that matches against the resource key and resource name. Leave empty to retrieve all linked resources without filtering."),
) -> dict[str, Any]:
    """Retrieve all linked resources of a specified type (flags or segments) associated with a given view within a project. Optionally filter results using a case-insensitive search query."""

    # Construct request model with validation
    try:
        _request = _models.GetLinkedResourcesRequest(
            path=_models.GetLinkedResourcesRequestPath(project_key=project_key, view_key=view_key, resource_type=resource_type),
            query=_models.GetLinkedResourcesRequestQuery(query=query),
            header=_models.GetLinkedResourcesRequestHeader(ld_api_version=ld_api_version)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_linked_resources_for_view: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/views/{viewKey}/linked/{resourceType}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/views/{viewKey}/linked/{resourceType}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_linked_resources_for_view")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_linked_resources_for_view", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_linked_resources_for_view",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Views (beta)
@mcp.tool()
async def list_linked_views_for_resource(
    project_key: str = Field(..., alias="projectKey", description="The project key that contains the resource. Typically 'default' for standard projects."),
    resource_type: Literal["flags", "segments"] = Field(..., alias="resourceType", description="The type of resource to retrieve linked views for. Must be either 'flags' or 'segments'."),
    resource_key: str = Field(..., alias="resourceKey", description="The unique identifier for the resource. For flags, use the flag key. For segments, use the segment ID."),
    ld_api_version: Literal["beta"] = Field(..., alias="LD-API-Version", description="The API version to use for this request. Currently supports 'beta' version."),
    environment_id: str | None = Field(None, alias="environmentId", description="The environment ID where the resource exists. Required when resourceType is 'segments'; optional for flags."),
) -> dict[str, Any]:
    """Retrieve all views linked to a specific resource (flag or segment). Use the resource key for flags and segment ID for segments to identify the target resource."""

    # Construct request model with validation
    try:
        _request = _models.GetLinkedViewsRequest(
            path=_models.GetLinkedViewsRequestPath(project_key=project_key, resource_type=resource_type, resource_key=resource_key),
            query=_models.GetLinkedViewsRequestQuery(environment_id=environment_id),
            header=_models.GetLinkedViewsRequestHeader(ld_api_version=ld_api_version)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_linked_views_for_resource: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/view-associations/{resourceType}/{resourceKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/view-associations/{resourceType}/{resourceKey}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_linked_views_for_resource")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_linked_views_for_resource", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_linked_views_for_resource",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Release policies (beta)
@mcp.tool()
async def list_release_policies(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project (e.g., 'default')."),
    ld_api_version: Literal["beta"] = Field(..., alias="LD-API-Version", description="The API version to use for this endpoint; must be set to 'beta'."),
    exclude_default: bool | None = Field(None, alias="excludeDefault", description="Set to true to exclude the default release policy from the results; when false or omitted, the default policy is included if an environment filter is present."),
) -> dict[str, Any]:
    """Retrieve a list of release policies for a specified project with optional filtering to exclude the default policy."""

    # Construct request model with validation
    try:
        _request = _models.GetReleasePoliciesRequest(
            path=_models.GetReleasePoliciesRequestPath(project_key=project_key),
            query=_models.GetReleasePoliciesRequestQuery(exclude_default=exclude_default),
            header=_models.GetReleasePoliciesRequestHeader(ld_api_version=ld_api_version)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_release_policies: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/release-policies", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/release-policies"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_release_policies")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_release_policies", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_release_policies",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Release policies (beta)
@mcp.tool()
async def reorder_release_policies(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project whose release policies should be reordered. Use the project key assigned during project creation (e.g., 'default')."),
    ld_api_version: Literal["beta"] = Field(..., alias="LD-API-Version", description="The API version to use for this operation. Currently only the beta version is available."),
    body: list[str] = Field(..., description="An ordered array of release policy keys that defines the new execution sequence. The order of keys in this array determines the order in which policies are evaluated and applied."),
) -> dict[str, Any]:
    """Reorder the release policies for a project by specifying their desired sequence. This operation updates the policy execution order without modifying individual policy configurations."""

    # Construct request model with validation
    try:
        _request = _models.PostReleasePoliciesOrderRequest(
            path=_models.PostReleasePoliciesOrderRequestPath(project_key=project_key),
            header=_models.PostReleasePoliciesOrderRequestHeader(ld_api_version=ld_api_version),
            body=_models.PostReleasePoliciesOrderRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for reorder_release_policies: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/release-policies/order", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/release-policies/order"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("reorder_release_policies")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("reorder_release_policies", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="reorder_release_policies",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Release policies (beta)
@mcp.tool()
async def get_release_policy(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project (e.g., 'default'). This scopes the release policy lookup to a specific project."),
    policy_key: str = Field(..., alias="policyKey", description="The unique identifier for the release policy within the project (e.g., 'production-release'). This specifies which policy to retrieve."),
    ld_api_version: Literal["beta"] = Field(..., alias="LD-API-Version", description="The API version to use for this request. Must be set to 'beta' to access this endpoint."),
) -> dict[str, Any]:
    """Retrieve a specific release policy by its key within a project. Use this to fetch detailed configuration and settings for a named release policy."""

    # Construct request model with validation
    try:
        _request = _models.GetReleasePolicyRequest(
            path=_models.GetReleasePolicyRequestPath(project_key=project_key, policy_key=policy_key),
            header=_models.GetReleasePolicyRequestHeader(ld_api_version=ld_api_version)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_release_policy: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/release-policies/{policyKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/release-policies/{policyKey}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_release_policy")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_release_policy", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_release_policy",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Release policies (beta)
@mcp.tool()
async def update_release_policy(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the release policy."),
    policy_key: str = Field(..., alias="policyKey", description="The unique human-readable identifier for the release policy to update."),
    ld_api_version: Literal["beta"] = Field(..., alias="LD-API-Version", description="API version specification; must be set to 'beta' for this endpoint."),
    release_method: Literal["guarded-release", "progressive-release"] = Field(..., alias="releaseMethod", description="The release strategy for this policy: 'guarded-release' for controlled rollouts with validation gates, or 'progressive-release' for gradual percentage-based rollouts."),
    name: str = Field(..., description="A human-readable name for the release policy, up to 256 characters. Used for display and identification in the UI.", max_length=256),
    environment_keys: list[str] | None = Field(None, alias="environmentKeys", description="Optional list of environment keys where this policy applies (e.g., production, staging). If specified, the policy is scoped to these environments only."),
    flag_tag_keys: list[str] | None = Field(None, alias="flagTagKeys", description="Optional list of flag tag keys to which this policy applies. If specified, the policy only affects flags with these tags."),
    min_sample_size: int | None = Field(None, alias="minSampleSize", description="Optional minimum number of samples (observations) required before the system can make a release decision. Helps ensure statistical significance."),
    rollback_on_regression: bool | None = Field(None, alias="rollbackOnRegression", description="Optional flag to automatically roll back the release if a regression is detected in monitored metrics."),
    metric_keys: list[str] | None = Field(None, alias="metricKeys", description="Optional list of metric keys to monitor during release (e.g., http-errors, latency). These metrics inform release decisions and rollback triggers."),
    metric_group_keys: list[str] | None = Field(None, alias="metricGroupKeys", description="Optional list of metric group keys to monitor during release. Groups allow monitoring multiple related metrics together."),
    guarded_release_config_stages: list[_models.ReleasePolicyStage] | None = Field(None, alias="guardedReleaseConfigStages", description="Optional array of release stages for guarded-release policies, defining sequential validation gates and approval requirements."),
    progressive_release_config_stages: list[_models.ReleasePolicyStage] | None = Field(None, alias="progressiveReleaseConfigStages", description="Optional array of release stages for progressive-release policies, defining percentage-based rollout increments and timing."),
) -> dict[str, Any]:
    """Update an existing release policy for a project, configuring how feature flags are released across environments with optional metrics-based validation and rollback controls."""

    # Construct request model with validation
    try:
        _request = _models.PutReleasePolicyRequest(
            path=_models.PutReleasePolicyRequestPath(project_key=project_key, policy_key=policy_key),
            header=_models.PutReleasePolicyRequestHeader(ld_api_version=ld_api_version),
            body=_models.PutReleasePolicyRequestBody(release_method=release_method, name=name,
                scope=_models.PutReleasePolicyRequestBodyScope(environment_keys=environment_keys, flag_tag_keys=flag_tag_keys) if any(v is not None for v in [environment_keys, flag_tag_keys]) else None,
                guarded_release_config=_models.PutReleasePolicyRequestBodyGuardedReleaseConfig(min_sample_size=min_sample_size, rollback_on_regression=rollback_on_regression, metric_keys=metric_keys, metric_group_keys=metric_group_keys, stages=guarded_release_config_stages) if any(v is not None for v in [min_sample_size, rollback_on_regression, metric_keys, metric_group_keys, guarded_release_config_stages]) else None,
                progressive_release_config=_models.PutReleasePolicyRequestBodyProgressiveReleaseConfig(stages=progressive_release_config_stages) if any(v is not None for v in [progressive_release_config_stages]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_release_policy: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/release-policies/{policyKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/release-policies/{policyKey}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_release_policy")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_release_policy", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_release_policy",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Release policies (beta)
@mcp.tool()
async def delete_release_policy(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project containing the release policy (e.g., 'default')."),
    policy_key: str = Field(..., alias="policyKey", description="The human-readable identifier for the release policy to delete (e.g., 'production-release')."),
    ld_api_version: Literal["beta"] = Field(..., alias="LD-API-Version", description="The API version to use for this operation. Must be set to 'beta'."),
) -> dict[str, Any]:
    """Permanently delete a release policy from a project. This action cannot be undone and will remove all associated policy configurations."""

    # Construct request model with validation
    try:
        _request = _models.DeleteReleasePolicyRequest(
            path=_models.DeleteReleasePolicyRequestPath(project_key=project_key, policy_key=policy_key),
            header=_models.DeleteReleasePolicyRequestHeader(ld_api_version=ld_api_version)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_release_policy: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/projects/{projectKey}/release-policies/{policyKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/projects/{projectKey}/release-policies/{policyKey}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_release_policy")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_release_policy", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_release_policy",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Insights charts (beta)
@mcp.tool()
async def get_deployment_frequency_chart(
    project_key: str | None = Field(None, alias="projectKey", description="The project key to filter deployment frequency data for a specific project."),
    environment_key: str | None = Field(None, alias="environmentKey", description="The environment key to filter deployment frequency data for a specific environment."),
    application_key: str | None = Field(None, alias="applicationKey", description="Comma-separated list of application keys to filter deployment frequency data across multiple applications."),
    from_: str | None = Field(None, alias="from", description="Start of the time range as a Unix timestamp in milliseconds. Defaults to 7 days ago if not specified."),
    to: str | None = Field(None, description="End of the time range as a Unix timestamp in milliseconds. Defaults to the current time if not specified."),
    bucket_type: str | None = Field(None, alias="bucketType", description="Type of time bucket for aggregating data: `rolling` (continuous window), `hour` (hourly intervals), or `day` (daily intervals). Defaults to `rolling`."),
    bucket_ms: str | None = Field(None, alias="bucketMs", description="Duration of intervals for the x-axis in milliseconds. Defaults to one day (86400000 milliseconds). Adjust to control granularity of the chart data."),
    group_by: str | None = Field(None, alias="groupBy", description="Dimension to group deployment frequency data by: `application` (per application) or `kind` (by deployment type)."),
) -> dict[str, Any]:
    """Retrieve deployment frequency chart data for engineering insights, showing how often deployments occur across your infrastructure. Optionally expand the response to include detailed metrics related to deployment frequency."""

    _bucket_ms = _parse_int(bucket_ms)

    # Construct request model with validation
    try:
        _request = _models.GetDeploymentFrequencyChartRequest(
            query=_models.GetDeploymentFrequencyChartRequestQuery(project_key=project_key, environment_key=environment_key, application_key=application_key, from_=from_, to=to, bucket_type=bucket_type, bucket_ms=_bucket_ms, group_by=group_by)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_deployment_frequency_chart: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v2/engineering-insights/charts/deployments/frequency"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_deployment_frequency_chart")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_deployment_frequency_chart", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_deployment_frequency_chart",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Insights charts (beta)
@mcp.tool()
async def get_stale_flags_chart(
    project_key: str = Field(..., alias="projectKey", description="The project key that identifies which project to retrieve stale flags data for."),
    environment_key: str = Field(..., alias="environmentKey", description="The environment key that identifies which environment within the project to retrieve stale flags data for."),
    application_key: str | None = Field(None, alias="applicationKey", description="Optional comma-separated list of application keys to filter stale flags data to specific applications."),
    group_by: str | None = Field(None, alias="groupBy", description="Optional property to group the stale flags results by. Currently supports grouping by maintainer to organize flags by their responsible team members."),
) -> dict[str, Any]:
    """Retrieve stale flags chart data for engineering insights, showing flag health metrics across a project and environment. Optionally expand the response to include detailed metrics and group results by maintainer."""

    # Construct request model with validation
    try:
        _request = _models.GetStaleFlagsChartRequest(
            query=_models.GetStaleFlagsChartRequestQuery(project_key=project_key, environment_key=environment_key, application_key=application_key, group_by=group_by)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_stale_flags_chart: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v2/engineering-insights/charts/flags/stale"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_stale_flags_chart")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_stale_flags_chart", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_stale_flags_chart",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Insights charts (beta)
@mcp.tool()
async def get_flag_status_chart(
    project_key: str = Field(..., alias="projectKey", description="The project key that identifies which project's flag data to retrieve."),
    environment_key: str = Field(..., alias="environmentKey", description="The environment key that specifies which environment's flag statuses to chart."),
    application_key: str | None = Field(None, alias="applicationKey", description="Optional comma-separated list of application keys to filter the flag status data to specific applications."),
) -> dict[str, Any]:
    """Retrieve flag status chart data for a specific project and environment, optionally filtered by applications. This provides observability into flag health and status distribution across your infrastructure."""

    # Construct request model with validation
    try:
        _request = _models.GetFlagStatusChartRequest(
            query=_models.GetFlagStatusChartRequestQuery(project_key=project_key, environment_key=environment_key, application_key=application_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_flag_status_chart: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v2/engineering-insights/charts/flags/status"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_flag_status_chart")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_flag_status_chart", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_flag_status_chart",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Insights charts (beta)
@mcp.tool()
async def get_lead_time_chart(
    project_key: str = Field(..., alias="projectKey", description="The project key that identifies which project's lead time data to retrieve."),
    environment_key: str | None = Field(None, alias="environmentKey", description="Optional environment key to filter lead time data to a specific environment within the project."),
    application_key: str | None = Field(None, alias="applicationKey", description="Optional comma-separated list of application keys to filter the chart data to specific applications."),
    from_: str | None = Field(None, alias="from", description="Optional Unix timestamp in milliseconds marking the start of the time range. Defaults to 7 days before the end time if not specified."),
    to: str | None = Field(None, description="Optional Unix timestamp in milliseconds marking the end of the time range. Defaults to the current time if not specified."),
    bucket_type: str | None = Field(None, alias="bucketType", description="Optional bucket type for aggregating data points. Choose from: `rolling` (continuous window), `hour` (hourly intervals), or `day` (daily intervals). Defaults to `rolling`."),
    bucket_ms: str | None = Field(None, alias="bucketMs", description="Optional duration in milliseconds for each interval on the x-axis. Defaults to one day (86400000 milliseconds). Only applies when bucketType is `hour` or `day`."),
    group_by: str | None = Field(None, alias="groupBy", description="Optional dimension for grouping chart data. Choose from: `application` (group by application) or `stage` (group by deployment stage). Defaults to `stage`."),
) -> dict[str, Any]:
    """Retrieve lead time chart data for engineering insights, showing deployment frequency metrics across specified time periods and grouping dimensions."""

    _from_ = _parse_int(from_)
    _to = _parse_int(to)
    _bucket_ms = _parse_int(bucket_ms)

    # Construct request model with validation
    try:
        _request = _models.GetLeadTimeChartRequest(
            query=_models.GetLeadTimeChartRequestQuery(project_key=project_key, environment_key=environment_key, application_key=application_key, from_=_from_, to=_to, bucket_type=bucket_type, bucket_ms=_bucket_ms, group_by=group_by)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_lead_time_chart: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v2/engineering-insights/charts/lead-time"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_lead_time_chart")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_lead_time_chart", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_lead_time_chart",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Insights charts (beta)
@mcp.tool()
async def get_release_frequency_chart(
    project_key: str = Field(..., alias="projectKey", description="The project key that identifies which project's release data to retrieve."),
    environment_key: str = Field(..., alias="environmentKey", description="The environment key that identifies which environment's release data to retrieve."),
    application_key: str | None = Field(None, alias="applicationKey", description="Comma-separated list of application keys to filter results to specific applications. Omit to include all applications."),
    has_experiments: bool | None = Field(None, alias="hasExperiments", description="Filter results to releases associated with experiments (true) or releases without experiments (false). Omit to include all releases regardless of experiment association."),
    global_: str | None = Field(None, alias="global", description="Filter to include or exclude global events. Use 'include' to show global events or 'exclude' to hide them. Defaults to 'include'."),
    group_by: str | None = Field(None, alias="groupBy", description="Group results by a property such as 'impact' to organize the chart data. Omit for ungrouped results."),
    from_: str | None = Field(None, alias="from", description="Start of the time range as a Unix timestamp in milliseconds. Defaults to 7 days before the 'to' timestamp if not specified."),
    to: str | None = Field(None, description="End of the time range as a Unix timestamp in milliseconds. Defaults to the current time if not specified."),
    bucket_type: str | None = Field(None, alias="bucketType", description="Time interval bucketing strategy: 'rolling' for continuous aggregation, 'hour' for hourly buckets, or 'day' for daily buckets. Defaults to 'rolling'."),
    bucket_ms: str | None = Field(None, alias="bucketMs", description="Duration of each time interval bucket in milliseconds. Defaults to one day (86400000 milliseconds). Only applies when bucketType is not 'rolling'."),
) -> dict[str, Any]:
    """Retrieve release frequency chart data for a project and environment, with optional filtering by application, experiment association, and time range. Results can be grouped by impact and bucketed into time intervals for visualization."""

    _bucket_ms = _parse_int(bucket_ms)

    # Construct request model with validation
    try:
        _request = _models.GetReleaseFrequencyChartRequest(
            query=_models.GetReleaseFrequencyChartRequestQuery(project_key=project_key, environment_key=environment_key, application_key=application_key, has_experiments=has_experiments, global_=global_, group_by=group_by, from_=from_, to=to, bucket_type=bucket_type, bucket_ms=_bucket_ms)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_release_frequency_chart: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v2/engineering-insights/charts/releases/frequency"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_release_frequency_chart")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_release_frequency_chart", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_release_frequency_chart",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Insights deployments (beta)
@mcp.tool()
async def create_deployment_event(
    project_key: str = Field(..., alias="projectKey", description="The project key that identifies which LaunchDarkly project this deployment belongs to."),
    environment_key: str = Field(..., alias="environmentKey", description="The environment key (e.g., production, staging) where the deployment occurred."),
    application_key: str = Field(..., alias="applicationKey", description="The application key that identifies the service or component being deployed. LaunchDarkly automatically creates a new application record for each unique key. Typically matches your GitHub repository name."),
    version: str = Field(..., description="The version identifier for this deployment. Use at least the first seven characters of the commit SHA or a git tag. Only alphanumeric characters, periods, hyphens, and underscores are allowed."),
    event_type: Literal["started", "failed", "finished", "custom"] = Field(..., alias="eventType", description="The type of deployment event being recorded. Choose from: 'started' (deployment beginning), 'finished' (deployment completed successfully), 'failed' (deployment failed), or 'custom' (for other event types)."),
    application_kind: Literal["server", "browser", "mobile"] | None = Field(None, alias="applicationKind", description="The type of application being deployed. Defaults to 'server' if not specified. Choose from: server, browser, or mobile."),
    event_metadata: dict[str, Any] | None = Field(None, alias="eventMetadata", description="Optional JSON object with event-specific metadata such as build system version or other contextual information about this particular event."),
    deployment_metadata: dict[str, Any] | None = Field(None, alias="deploymentMetadata", description="Optional JSON object with deployment-wide metadata such as build number or other information relevant to the entire deployment."),
) -> dict[str, Any]:
    """Record a deployment event for an application to track deployment lifecycle and metrics in engineering insights. Events can mark deployment start, completion, failure, or custom milestones."""

    # Construct request model with validation
    try:
        _request = _models.CreateDeploymentEventRequest(
            body=_models.CreateDeploymentEventRequestBody(project_key=project_key, environment_key=environment_key, application_key=application_key, application_kind=application_kind, version=version, event_type=event_type, event_metadata=event_metadata, deployment_metadata=deployment_metadata)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_deployment_event: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v2/engineering-insights/deployment-events"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_deployment_event")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_deployment_event", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_deployment_event",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Insights deployments (beta)
@mcp.tool()
async def list_deployments(
    project_key: str = Field(..., alias="projectKey", description="The project key that identifies which project to query deployments for."),
    environment_key: str = Field(..., alias="environmentKey", description="The environment key that identifies which environment to query deployments for."),
    application_key: str | None = Field(None, alias="applicationKey", description="Comma-separated list of application keys to filter deployments by specific applications. Omit to include all applications."),
    from_: str | None = Field(None, alias="from", description="Unix timestamp in milliseconds marking the start of the time range. Defaults to 7 days before the current time if not specified."),
    to: str | None = Field(None, description="Unix timestamp in milliseconds marking the end of the time range. Defaults to the current time if not specified."),
    kind: str | None = Field(None, description="Filter deployments by deployment kind (e.g., 'blue-green', 'canary'). Omit to include all kinds."),
    status: str | None = Field(None, description="Filter deployments by deployment status (e.g., 'active', 'completed'). Omit to include all statuses."),
) -> dict[str, Any]:
    """Retrieve a list of deployments for a specific project and environment, with optional filtering by application, time range, kind, and status. Supports expansion to include associated pull requests and flag references."""

    _from_ = _parse_int(from_)
    _to = _parse_int(to)

    # Construct request model with validation
    try:
        _request = _models.GetDeploymentsRequest(
            query=_models.GetDeploymentsRequestQuery(project_key=project_key, environment_key=environment_key, application_key=application_key, from_=_from_, to=_to, kind=kind, status=status)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_deployments: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v2/engineering-insights/deployments"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_deployments")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_deployments", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_deployments",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Insights deployments (beta)
@mcp.tool()
async def get_deployment(deployment_id: str = Field(..., alias="deploymentID", description="The unique identifier of the deployment to retrieve. This ID is provided in the `id` field when listing deployments.")) -> dict[str, Any]:
    """Retrieve a specific deployment by its ID. Optionally expand the response to include associated pull requests and flag references."""

    # Construct request model with validation
    try:
        _request = _models.GetDeploymentRequest(
            path=_models.GetDeploymentRequestPath(deployment_id=deployment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_deployment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/engineering-insights/deployments/{deploymentID}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/engineering-insights/deployments/{deploymentID}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_deployment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_deployment", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_deployment",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Insights deployments (beta)
@mcp.tool()
async def update_deployment(
    deployment_id: str = Field(..., alias="deploymentID", description="The unique identifier of the deployment to update. This ID is returned in the `id` field when listing deployments."),
    body: list[_models.PatchOperation] = Field(..., description="An array of JSON Patch operations (RFC 6902) describing the changes to apply. Each operation must include `op` (the operation type), `path` (the property to modify), and `value` (the new value for replace operations). Operations are applied in order."),
) -> dict[str, Any]:
    """Update a deployment's properties using JSON Patch operations. Specify the deployment by ID and provide an array of patch operations to modify its state."""

    # Construct request model with validation
    try:
        _request = _models.UpdateDeploymentRequest(
            path=_models.UpdateDeploymentRequestPath(deployment_id=deployment_id),
            body=_models.UpdateDeploymentRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_deployment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/engineering-insights/deployments/{deploymentID}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/engineering-insights/deployments/{deploymentID}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_deployment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_deployment", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_deployment",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Insights flag events (beta)
@mcp.tool()
async def list_flag_events(
    project_key: str = Field(..., alias="projectKey", description="The project key that identifies which project to query for flag events."),
    environment_key: str = Field(..., alias="environmentKey", description="The environment key that identifies which environment within the project to query for flag events."),
    application_key: str | None = Field(None, alias="applicationKey", description="Comma-separated list of application keys to filter events by specific applications."),
    query: str | None = Field(None, description="Filter events by flag key using a search query string."),
    impact_size: str | None = Field(None, alias="impactSize", description="Filter events by the magnitude of user impact: `none` (no change), `small` (less than 20% change), `medium` (20-80% change), or `large` (more than 80% change)."),
    has_experiments: bool | None = Field(None, alias="hasExperiments", description="Filter to show only events associated with experiments (`true`) or events without experiments (`false`)."),
    global_: str | None = Field(None, alias="global", description="Include or exclude global events from results. Defaults to `include`. Valid options are `include` or `exclude`."),
    from_: str | None = Field(None, alias="from", description="Unix timestamp in milliseconds marking the start of the time range. Defaults to 7 days ago if not specified."),
    to: str | None = Field(None, description="Unix timestamp in milliseconds marking the end of the time range. Defaults to the current time if not specified."),
) -> dict[str, Any]:
    """Retrieve a list of flag events for a specific project and environment, with optional filtering by application, flag key, impact size, and experiment association. Supports expanding the response to include experiment details."""

    _from_ = _parse_int(from_)
    _to = _parse_int(to)

    # Construct request model with validation
    try:
        _request = _models.GetFlagEventsRequest(
            query=_models.GetFlagEventsRequestQuery(project_key=project_key, environment_key=environment_key, application_key=application_key, query=query, impact_size=impact_size, has_experiments=has_experiments, global_=global_, from_=_from_, to=_to)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_flag_events: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v2/engineering-insights/flag-events"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_flag_events")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_flag_events", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_flag_events",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Insights scores (beta)
@mcp.tool()
async def create_insight_group(
    name: str = Field(..., description="A human-readable name for the insight group (e.g., 'Production - All Apps'). Used for display and identification in the UI."),
    key: str = Field(..., description="A unique identifier key for the insight group in kebab-case format (e.g., 'default-production-all-apps'). Used for API references and internal lookups."),
    project_key: str = Field(..., alias="projectKey", description="The project key that this insight group belongs to. Determines which project's data and configuration the group operates within."),
    environment_key: str = Field(..., alias="environmentKey", description="The environment key (e.g., 'production', 'staging') that this insight group monitors. Scopes insights to a specific deployment environment."),
    application_keys: list[str] | None = Field(None, alias="applicationKeys", description="Optional list of application keys to include in this insight group (e.g., ['billing-service', 'inventory-service']). If omitted, the group will automatically include data from all applications in the specified project and environment."),
) -> dict[str, Any]:
    """Create a new insight group to organize and monitor engineering insights across a specific project and environment. Optionally scope the group to specific applications."""

    # Construct request model with validation
    try:
        _request = _models.CreateInsightGroupRequest(
            body=_models.CreateInsightGroupRequestBody(name=name, key=key, project_key=project_key, environment_key=environment_key, application_keys=application_keys)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_insight_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v2/engineering-insights/insights/group"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_insight_group")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_insight_group", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_insight_group",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Insights scores (beta)
@mcp.tool()
async def list_insight_groups(query: str | None = Field(None, description="Filter the insight groups list by group name. Supports partial string matching to find groups by name.")) -> dict[str, Any]:
    """Retrieve a list of insight groups for which you are collecting engineering insights. Optionally filter by group name and expand the response to include scores, environment details, or metadata indicators."""

    # Construct request model with validation
    try:
        _request = _models.GetInsightGroupsRequest(
            query=_models.GetInsightGroupsRequestQuery(query=query)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_insight_groups: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v2/engineering-insights/insights/groups"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_insight_groups")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_insight_groups", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_insight_groups",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Insights scores (beta)
@mcp.tool()
async def get_insight_group(insight_group_key: str = Field(..., alias="insightGroupKey", description="The unique identifier for the insight group to retrieve.")) -> dict[str, Any]:
    """Retrieve a specific insight group by its key, with optional expansion to include scoring details and environment associations used in engineering insights metrics."""

    # Construct request model with validation
    try:
        _request = _models.GetInsightGroupRequest(
            path=_models.GetInsightGroupRequestPath(insight_group_key=insight_group_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_insight_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/engineering-insights/insights/groups/{insightGroupKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/engineering-insights/insights/groups/{insightGroupKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_insight_group")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_insight_group", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_insight_group",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Insights scores (beta)
@mcp.tool()
async def update_insight_group(
    insight_group_key: str = Field(..., alias="insightGroupKey", description="The unique identifier for the insight group to update."),
    body: list[_models.PatchOperation] = Field(..., description="A JSON Patch document (RFC 6902) describing the updates to apply. Each operation must include 'op' (the operation type), 'path' (the JSON pointer to the field), and 'value' (the new value for replace operations). Common operations include 'replace' to change field values."),
) -> dict[str, Any]:
    """Update an insight group using JSON Patch operations. Specify the changes you want to make (such as renaming the group) via a JSON Patch document following RFC 6902 standards."""

    # Construct request model with validation
    try:
        _request = _models.PatchInsightGroupRequest(
            path=_models.PatchInsightGroupRequestPath(insight_group_key=insight_group_key),
            body=_models.PatchInsightGroupRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_insight_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/engineering-insights/insights/groups/{insightGroupKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/engineering-insights/insights/groups/{insightGroupKey}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_insight_group")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_insight_group", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_insight_group",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Insights scores (beta)
@mcp.tool()
async def delete_insight_group(insight_group_key: str = Field(..., alias="insightGroupKey", description="The unique identifier for the insight group to delete. This is a string value that uniquely identifies the insight group within the system.")) -> dict[str, Any]:
    """Permanently delete an insight group by its unique key. This operation removes the insight group and all associated data."""

    # Construct request model with validation
    try:
        _request = _models.DeleteInsightGroupRequest(
            path=_models.DeleteInsightGroupRequestPath(insight_group_key=insight_group_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_insight_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/engineering-insights/insights/groups/{insightGroupKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/engineering-insights/insights/groups/{insightGroupKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_insight_group")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_insight_group", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_insight_group",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Insights scores (beta)
@mcp.tool()
async def get_insights_scores(
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project. Required to scope the insights scores to a specific project."),
    environment_key: str = Field(..., alias="environmentKey", description="The unique identifier for the environment within the project. Required to retrieve environment-specific insight metrics."),
    application_key: str | None = Field(None, alias="applicationKey", description="Optional comma-separated list of application identifiers to filter insights scores to specific applications. When omitted, scores for all applications in the environment are returned."),
) -> dict[str, Any]:
    """Retrieve engineering insights scores for a specified project and environment, optionally filtered by one or more applications. This data powers engineering insights metrics dashboards and performance analysis views."""

    # Construct request model with validation
    try:
        _request = _models.GetInsightsScoresRequest(
            query=_models.GetInsightsScoresRequestQuery(project_key=project_key, environment_key=environment_key, application_key=application_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_insights_scores: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v2/engineering-insights/insights/scores"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_insights_scores")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_insights_scores", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_insights_scores",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Insights pull requests (beta)
@mcp.tool()
async def list_pull_requests(
    project_key: str = Field(..., alias="projectKey", description="The project key that identifies which project's pull requests to retrieve."),
    environment_key: str | None = Field(None, alias="environmentKey", description="The environment key, required only when sorting results by lead time metrics."),
    application_key: str | None = Field(None, alias="applicationKey", description="Filter results to pull requests deployed to specific applications. Provide as a comma-separated list of application keys."),
    status: str | None = Field(None, description="Filter results by pull request status. Valid options are: open, merged, closed, or deployed."),
    query: str | None = Field(None, description="Search pull requests by title or author name. Performs a text match against these fields."),
    from_: str | None = Field(None, alias="from", description="Start of the date range as a Unix timestamp in milliseconds. Defaults to 7 days before the end date if not specified."),
    to: str | None = Field(None, description="End of the date range as a Unix timestamp in milliseconds. Defaults to the current time if not specified."),
) -> dict[str, Any]:
    """Retrieve a list of pull requests for a project with optional filtering by status, application, date range, and search terms. Supports expanding the response to include deployment details, flag references, and lead time metrics."""

    # Construct request model with validation
    try:
        _request = _models.GetPullRequestsRequest(
            query=_models.GetPullRequestsRequestQuery(project_key=project_key, environment_key=environment_key, application_key=application_key, status=status, query=query, from_=from_, to=to)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_pull_requests: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v2/engineering-insights/pull-requests"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_pull_requests")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_pull_requests", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_pull_requests",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Insights repositories (beta)
@mcp.tool()
async def list_repositories_insights() -> dict[str, Any]:
    """Retrieve a list of repositories integrated with LaunchDarkly's engineering insights. Optionally expand the response to include associated project details for each repository."""

    # Extract parameters for API call
    _http_path = "/api/v2/engineering-insights/repositories"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_repositories_insights")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_repositories_insights", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_repositories_insights",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Insights repositories (beta)
@mcp.tool()
async def associate_repositories_with_projects(mappings: list[_models.InsightsRepositoryProject] = Field(..., description="Array of repository-to-project mappings. Each mapping object should specify which repository associates with which project. Order is preserved and processed sequentially.")) -> dict[str, Any]:
    """Create or update associations between repositories and projects. Use this operation to map one or more repositories to their corresponding projects for engineering insights tracking."""

    # Construct request model with validation
    try:
        _request = _models.AssociateRepositoriesAndProjectsRequest(
            body=_models.AssociateRepositoriesAndProjectsRequestBody(mappings=mappings)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for associate_repositories_with_projects: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v2/engineering-insights/repositories/projects"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("associate_repositories_with_projects")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("associate_repositories_with_projects", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="associate_repositories_with_projects",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Insights repositories (beta)
@mcp.tool()
async def remove_repository_project_association(
    repository_key: str = Field(..., alias="repositoryKey", description="The unique identifier for the repository from which the project association will be removed."),
    project_key: str = Field(..., alias="projectKey", description="The unique identifier for the project to be disassociated from the repository."),
) -> dict[str, Any]:
    """Remove the association between a repository and a project in engineering insights. This operation disassociates the specified project from the given repository."""

    # Construct request model with validation
    try:
        _request = _models.DeleteRepositoryProjectRequest(
            path=_models.DeleteRepositoryProjectRequestPath(repository_key=repository_key, project_key=project_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_repository_project_association: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v2/engineering-insights/repositories/{repositoryKey}/projects/{projectKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v2/engineering-insights/repositories/{repositoryKey}/projects/{projectKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_repository_project_association")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_repository_project_association", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_repository_project_association",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
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
        print("  python launch_darkly_rest_api_server.py", file=sys.stderr)
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

    parser = argparse.ArgumentParser(description="LaunchDarkly REST API MCP Server")

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
    logger.info("Starting LaunchDarkly REST API MCP Server")
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

#!/usr/bin/env python3
"""
E2B MCP Server
Generated: 2026-04-14 18:20:03 UTC
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

BASE_URL = os.getenv("BASE_URL", "https://api.e2b.app")
SERVER_NAME = "E2B"
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

def _serialize_query(params: dict[str, Any], styles: dict[str, tuple[str, bool]]) -> dict[str, Any]:
    """Serialize query params per OAS style/explode rules."""
    result: dict[str, Any] = {}
    for key, value in params.items():
        if key not in styles:
            result[key] = value
            continue
        style, explode = styles[key]
        if isinstance(value, list):
            if style == "pipeDelimited":
                result[key] = "|".join(str(v) for v in value)
            elif style == "spaceDelimited":
                result[key] = " ".join(str(v) for v in value)
            elif not explode:
                result[key] = ",".join(str(v) for v in value)
            else:
                result[key] = value
        elif isinstance(value, dict):
            if style == "deepObject":
                for k, v in value.items():
                    result[f"{key}[{k}]"] = v
            elif not explode:
                result[key] = ",".join(f"{k},{v}" for k, v in value.items())
            else:
                result.update(value)
        else:
            result[key] = value
    return result

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
    'AccessTokenAuth',
    'ApiKeyAuth',
    'Supabase1TokenAuth',
    'Supabase2TeamAuth',
    'AdminTokenAuth',
]

# Initialize authentication handlers at server startup
_auth_handlers: dict[str, Any] = {}
try:
    _auth_handlers["AccessTokenAuth"] = _auth.BearerTokenAuth(env_var="BEARER_TOKEN", token_format="Bearer")
    logging.info("Authentication configured: AccessTokenAuth")
except ValueError as e:
    # Extract credential names from error message (first sentence before "Leave empty")
    error_msg = str(e).split("Leave empty")[0].strip()
    logging.warning(f"Credentials for AccessTokenAuth not configured: {error_msg}")
    _auth_handlers["AccessTokenAuth"] = None
try:
    _auth_handlers["ApiKeyAuth"] = _auth.APIKeyAuth(env_var="API_KEY_AUTH", location="header", param_name="X-API-Key")
    logging.info("Authentication configured: ApiKeyAuth")
except ValueError as e:
    # Extract credential names from error message (first sentence before "Leave empty")
    error_msg = str(e).split("Leave empty")[0].strip()
    logging.warning(f"Credentials for ApiKeyAuth not configured: {error_msg}")
    _auth_handlers["ApiKeyAuth"] = None
try:
    _auth_handlers["Supabase1TokenAuth"] = _auth.APIKeyAuth(env_var="SUPABASE1_TOKEN_AUTH_API_KEY", location="header", param_name="X-Supabase-Token")
    logging.info("Authentication configured: Supabase1TokenAuth")
except ValueError as e:
    # Extract credential names from error message (first sentence before "Leave empty")
    error_msg = str(e).split("Leave empty")[0].strip()
    logging.warning(f"Credentials for Supabase1TokenAuth not configured: {error_msg}")
    _auth_handlers["Supabase1TokenAuth"] = None
try:
    _auth_handlers["Supabase2TeamAuth"] = _auth.APIKeyAuth(env_var="SUPABASE2_TEAM_AUTH_API_KEY", location="header", param_name="X-Supabase-Team")
    logging.info("Authentication configured: Supabase2TeamAuth")
except ValueError as e:
    # Extract credential names from error message (first sentence before "Leave empty")
    error_msg = str(e).split("Leave empty")[0].strip()
    logging.warning(f"Credentials for Supabase2TeamAuth not configured: {error_msg}")
    _auth_handlers["Supabase2TeamAuth"] = None
try:
    _auth_handlers["AdminTokenAuth"] = _auth.APIKeyAuth(env_var="ADMIN_TOKEN_AUTH_API_KEY", location="header", param_name="X-Admin-Token")
    logging.info("Authentication configured: AdminTokenAuth")
except ValueError as e:
    # Extract credential names from error message (first sentence before "Leave empty")
    error_msg = str(e).split("Leave empty")[0].strip()
    logging.warning(f"Credentials for AdminTokenAuth not configured: {error_msg}")
    _auth_handlers["AdminTokenAuth"] = None

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

mcp = FastMCP("E2B", middleware=[_JsonCoercionMiddleware()])

# Tags: auth
@mcp.tool()
async def list_teams() -> dict[str, Any]:
    """Retrieve a list of all teams in the system. Use this operation to discover available teams for management or assignment purposes."""

    # Extract parameters for API call
    _http_path = "/teams"
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

# Tags: auth
@mcp.tool()
async def get_team_metrics(
    team_id: str = Field(..., alias="teamID", description="The unique identifier of the team for which to retrieve metrics."),
    start: str | None = Field(None, description="Unix timestamp in seconds marking the start of the metrics interval. If omitted, defaults to the beginning of the current period."),
    end: str | None = Field(None, description="Unix timestamp in seconds marking the end of the metrics interval. If omitted, defaults to the current time."),
) -> dict[str, Any]:
    """Retrieve performance and activity metrics for a specific team over an optional time interval. If no time range is specified, returns metrics for the current period."""

    _start = _parse_int(start)
    _end = _parse_int(end)

    # Construct request model with validation
    try:
        _request = _models.GetTeamsMetricsRequest(
            path=_models.GetTeamsMetricsRequestPath(team_id=team_id),
            query=_models.GetTeamsMetricsRequestQuery(start=_start, end=_end)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_team_metrics: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/teams/{teamID}/metrics", _request.path.model_dump(by_alias=True)) if _request.path else "/teams/{teamID}/metrics"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_team_metrics")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_team_metrics", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_team_metrics",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: auth
@mcp.tool()
async def get_team_metrics_maximum(
    team_id: str = Field(..., alias="teamID", description="The unique identifier of the team for which to retrieve metrics."),
    metric: Literal["concurrent_sandboxes", "sandbox_start_rate"] = Field(..., description="The specific metric to retrieve the maximum value for during the interval."),
    start: str | None = Field(None, description="Unix timestamp in seconds marking the start of the interval. If omitted, metrics from the earliest available data are included."),
    end: str | None = Field(None, description="Unix timestamp in seconds marking the end of the interval. If omitted, metrics up to the current time are included."),
) -> dict[str, Any]:
    """Retrieve the maximum value for a specified metric within a given time interval for a team. Useful for understanding peak performance or resource utilization."""

    _start = _parse_int(start)
    _end = _parse_int(end)

    # Construct request model with validation
    try:
        _request = _models.GetTeamsMetricsMaxRequest(
            path=_models.GetTeamsMetricsMaxRequestPath(team_id=team_id),
            query=_models.GetTeamsMetricsMaxRequestQuery(start=_start, end=_end, metric=metric)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_team_metrics_maximum: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/teams/{teamID}/metrics/max", _request.path.model_dump(by_alias=True)) if _request.path else "/teams/{teamID}/metrics/max"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_team_metrics_maximum")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_team_metrics_maximum", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_team_metrics_maximum",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: sandboxes
@mcp.tool()
async def create_sandbox(
    template_id: str = Field(..., alias="templateID", description="The unique identifier of the template to use for creating the sandbox."),
    enabled: bool = Field(..., description="Enable automatic resumption of the sandbox when it enters a paused state."),
    allow_public_traffic: bool | None = Field(None, alias="allowPublicTraffic", description="Control whether sandbox URLs are publicly accessible or require authentication to access."),
    allow_out: list[str] | None = Field(None, alias="allowOut", description="List of CIDR blocks or IP addresses permitted for outbound traffic. Allowed addresses take precedence over denied addresses when both are specified."),
    deny_out: list[str] | None = Field(None, alias="denyOut", description="List of CIDR blocks or IP addresses blocked from outbound traffic."),
    metadata: Any | None = Field(None, description="Custom metadata to attach to the sandbox for tracking and organization purposes."),
    env_vars: Any | None = Field(None, alias="envVars", description="Environment variables to inject into the sandbox runtime environment."),
    mcp: dict[str, Any] | None = Field(None, description="Model Context Protocol (MCP) configuration settings for the sandbox."),
    volume_mounts: list[_models.SandboxVolumeMount] | None = Field(None, alias="volumeMounts", description="Volume mounts to attach to the sandbox, enabling access to external storage or data sources."),
) -> dict[str, Any]:
    """Create a new sandbox instance from a specified template. The sandbox can be configured with network policies, environment variables, and storage mounts."""

    # Construct request model with validation
    try:
        _request = _models.PostSandboxesRequest(
            body=_models.PostSandboxesRequestBody(template_id=template_id, metadata=metadata, env_vars=env_vars, mcp=mcp, volume_mounts=volume_mounts,
                auto_resume=_models.PostSandboxesRequestBodyAutoResume(enabled=enabled),
                network=_models.PostSandboxesRequestBodyNetwork(allow_public_traffic=allow_public_traffic, allow_out=allow_out, deny_out=deny_out) if any(v is not None for v in [allow_public_traffic, allow_out, deny_out]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_sandbox: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/sandboxes"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_sandbox")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_sandbox", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_sandbox",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: sandboxes
@mcp.tool()
async def list_sandboxes(
    metadata: str | None = Field(None, description="Filter sandboxes by metadata key-value pairs. Use URL encoding for both keys and values (e.g., user=abc&app=prod)."),
    state: list[Literal["running", "paused"]] | None = Field(None, description="Filter sandboxes by one or more states. Provide as an array of state values."),
    limit: str | None = Field(None, description="Maximum number of sandboxes to return per page. Must be between 1 and 100."),
) -> dict[str, Any]:
    """Retrieve a list of all sandboxes with optional filtering by metadata and state. Results are paginated with a configurable limit."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetV2SandboxesRequest(
            query=_models.GetV2SandboxesRequestQuery(metadata=metadata, state=state, limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_sandboxes: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v2/sandboxes"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_query = _serialize_query(_http_query, {
        "state": ("form", False),
    })
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_sandboxes")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_sandboxes", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_sandboxes",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: sandboxes
@mcp.tool()
async def list_sandbox_metrics(sandbox_ids: Annotated[list[str], AfterValidator(_check_unique_items)] = Field(..., description="One or more sandbox IDs to retrieve metrics for. Provide as a comma-separated list of sandbox identifiers.", max_length=100)) -> dict[str, Any]:
    """Retrieve performance and usage metrics for specified sandboxes. Supports querying multiple sandboxes in a single request."""

    # Construct request model with validation
    try:
        _request = _models.GetSandboxesMetricsRequest(
            query=_models.GetSandboxesMetricsRequestQuery(sandbox_ids=sandbox_ids)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_sandbox_metrics: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/sandboxes/metrics"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_query = _serialize_query(_http_query, {
        "sandbox_ids": ("form", False),
    })
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_sandbox_metrics")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_sandbox_metrics", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_sandbox_metrics",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: sandboxes
@mcp.tool()
async def list_sandbox_logs(
    sandbox_id: str = Field(..., alias="sandboxID", description="The unique identifier of the sandbox for which to retrieve logs."),
    cursor: str | None = Field(None, description="Starting timestamp in milliseconds from which logs should be returned. Use this to paginate through results or retrieve logs after a specific point in time."),
    limit: str | None = Field(None, description="Maximum number of log entries to return in a single response."),
    direction: Literal["forward", "backward"] | None = Field(None, description="Order in which logs should be returned relative to the cursor timestamp."),
) -> dict[str, Any]:
    """Retrieve logs from a specific sandbox with optional filtering by time range and result limit. Logs can be returned in forward or backward chronological order."""

    _cursor = _parse_int(cursor)
    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetV2SandboxesLogsRequest(
            path=_models.GetV2SandboxesLogsRequestPath(sandbox_id=sandbox_id),
            query=_models.GetV2SandboxesLogsRequestQuery(cursor=_cursor, limit=_limit, direction=direction)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_sandbox_logs: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/sandboxes/{sandboxID}/logs", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/sandboxes/{sandboxID}/logs"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_sandbox_logs")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_sandbox_logs", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_sandbox_logs",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: sandboxes
@mcp.tool()
async def get_sandbox(sandbox_id: str = Field(..., alias="sandboxID", description="The unique identifier of the sandbox to retrieve.")) -> dict[str, Any]:
    """Retrieve a specific sandbox by its unique identifier. Use this operation to fetch detailed information about a sandbox environment."""

    # Construct request model with validation
    try:
        _request = _models.GetSandboxesBySandboxIdRequest(
            path=_models.GetSandboxesBySandboxIdRequestPath(sandbox_id=sandbox_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_sandbox: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/sandboxes/{sandboxID}", _request.path.model_dump(by_alias=True)) if _request.path else "/sandboxes/{sandboxID}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_sandbox")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_sandbox", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_sandbox",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: sandboxes
@mcp.tool()
async def terminate_sandbox(sandbox_id: str = Field(..., alias="sandboxID", description="The unique identifier of the sandbox to terminate.")) -> dict[str, Any]:
    """Terminate and remove a sandbox environment by its ID. This operation permanently deletes the sandbox and all associated resources."""

    # Construct request model with validation
    try:
        _request = _models.DeleteSandboxesRequest(
            path=_models.DeleteSandboxesRequestPath(sandbox_id=sandbox_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for terminate_sandbox: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/sandboxes/{sandboxID}", _request.path.model_dump(by_alias=True)) if _request.path else "/sandboxes/{sandboxID}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("terminate_sandbox")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("terminate_sandbox", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="terminate_sandbox",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: sandboxes
@mcp.tool()
async def get_sandbox_metrics(
    sandbox_id: str = Field(..., alias="sandboxID", description="The unique identifier of the sandbox for which to retrieve metrics."),
    start: str | None = Field(None, description="Unix timestamp in seconds marking the beginning of the metrics collection interval. If omitted, metrics are retrieved from the earliest available data."),
    end: str | None = Field(None, description="Unix timestamp in seconds marking the end of the metrics collection interval. If omitted, metrics are retrieved up to the current time."),
) -> dict[str, Any]:
    """Retrieve performance and resource metrics for a specific sandbox over an optional time interval. Metrics are aggregated between the specified start and end timestamps."""

    _start = _parse_int(start)
    _end = _parse_int(end)

    # Construct request model with validation
    try:
        _request = _models.GetSandboxesBySandboxIdMetricsRequest(
            path=_models.GetSandboxesBySandboxIdMetricsRequestPath(sandbox_id=sandbox_id),
            query=_models.GetSandboxesBySandboxIdMetricsRequestQuery(start=_start, end=_end)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_sandbox_metrics: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/sandboxes/{sandboxID}/metrics", _request.path.model_dump(by_alias=True)) if _request.path else "/sandboxes/{sandboxID}/metrics"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_sandbox_metrics")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_sandbox_metrics", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_sandbox_metrics",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: sandboxes
@mcp.tool()
async def pause_sandbox(sandbox_id: str = Field(..., alias="sandboxID", description="The unique identifier of the sandbox to pause.")) -> dict[str, Any]:
    """Pause an active sandbox to temporarily suspend its execution and resource consumption. The sandbox can be resumed later without losing its state."""

    # Construct request model with validation
    try:
        _request = _models.PostSandboxesPauseRequest(
            path=_models.PostSandboxesPauseRequestPath(sandbox_id=sandbox_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for pause_sandbox: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/sandboxes/{sandboxID}/pause", _request.path.model_dump(by_alias=True)) if _request.path else "/sandboxes/{sandboxID}/pause"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("pause_sandbox")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("pause_sandbox", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="pause_sandbox",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: sandboxes
@mcp.tool()
async def connect_sandbox(
    sandbox_id: str = Field(..., alias="sandboxID", description="The unique identifier of the sandbox to connect to."),
    timeout: str = Field(..., description="The number of seconds from the current time until the sandbox should automatically expire. Must be a non-negative value."),
) -> dict[str, Any]:
    """Establish a connection to a sandbox and extend its time-to-live. If the sandbox is paused, it will be automatically resumed."""

    _timeout = _parse_int(timeout)

    # Construct request model with validation
    try:
        _request = _models.PostSandboxesConnectRequest(
            path=_models.PostSandboxesConnectRequestPath(sandbox_id=sandbox_id),
            body=_models.PostSandboxesConnectRequestBody(timeout=_timeout)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for connect_sandbox: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/sandboxes/{sandboxID}/connect", _request.path.model_dump(by_alias=True)) if _request.path else "/sandboxes/{sandboxID}/connect"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("connect_sandbox")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("connect_sandbox", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="connect_sandbox",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: sandboxes
@mcp.tool()
async def set_sandbox_timeout(
    sandbox_id: str = Field(..., alias="sandboxID", description="The unique identifier of the sandbox to configure."),
    timeout: str = Field(..., description="The number of seconds from the current time until the sandbox should automatically expire. Must be a non-negative integer."),
) -> dict[str, Any]:
    """Set the expiration time for a sandbox by specifying a timeout duration in seconds from the current request time. Calling this operation multiple times resets the sandbox's time-to-live (TTL), with each call using the current timestamp as the new starting point."""

    _timeout = _parse_int(timeout)

    # Construct request model with validation
    try:
        _request = _models.PostSandboxesTimeoutRequest(
            path=_models.PostSandboxesTimeoutRequestPath(sandbox_id=sandbox_id),
            body=_models.PostSandboxesTimeoutRequestBody(timeout=_timeout)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for set_sandbox_timeout: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/sandboxes/{sandboxID}/timeout", _request.path.model_dump(by_alias=True)) if _request.path else "/sandboxes/{sandboxID}/timeout"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("set_sandbox_timeout")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("set_sandbox_timeout", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="set_sandbox_timeout",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: sandboxes
@mcp.tool()
async def refresh_sandbox(
    sandbox_id: str = Field(..., alias="sandboxID", description="The unique identifier of the sandbox to refresh."),
    duration: int | None = Field(None, description="The duration in seconds to extend the sandbox's time to live. If not specified, a default duration will be applied.", ge=0, le=3600),
) -> dict[str, Any]:
    """Extend the time to live of an active sandbox by refreshing it. Optionally specify a custom duration to keep the sandbox alive."""

    # Construct request model with validation
    try:
        _request = _models.PostSandboxesRefreshesRequest(
            path=_models.PostSandboxesRefreshesRequestPath(sandbox_id=sandbox_id),
            body=_models.PostSandboxesRefreshesRequestBody(duration=duration)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for refresh_sandbox: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/sandboxes/{sandboxID}/refreshes", _request.path.model_dump(by_alias=True)) if _request.path else "/sandboxes/{sandboxID}/refreshes"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("refresh_sandbox")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("refresh_sandbox", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="refresh_sandbox",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: sandboxes
@mcp.tool()
async def create_sandbox_snapshot(
    sandbox_id: str = Field(..., alias="sandboxID", description="The unique identifier of the sandbox from which to create the snapshot."),
    name: str | None = Field(None, description="Optional name for the snapshot. If a snapshot with this name already exists, a new build will be assigned to the existing snapshot instead of creating a new one."),
) -> dict[str, Any]:
    """Create a persistent snapshot of the sandbox's current state that can be used to create new sandboxes and persists beyond the original sandbox's lifetime."""

    # Construct request model with validation
    try:
        _request = _models.PostSandboxesSnapshotsRequest(
            path=_models.PostSandboxesSnapshotsRequestPath(sandbox_id=sandbox_id),
            body=_models.PostSandboxesSnapshotsRequestBody(name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_sandbox_snapshot: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/sandboxes/{sandboxID}/snapshots", _request.path.model_dump(by_alias=True)) if _request.path else "/sandboxes/{sandboxID}/snapshots"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_sandbox_snapshot")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_sandbox_snapshot", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_sandbox_snapshot",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: snapshots
@mcp.tool()
async def list_snapshots(
    sandbox_id: str | None = Field(None, alias="sandboxID", description="Filter results to snapshots created from a specific sandbox ID."),
    limit: str | None = Field(None, description="Number of snapshots to return per page. Useful for paginating through large result sets."),
) -> dict[str, Any]:
    """Retrieve all snapshots for your team, with optional filtering by source sandbox and pagination support."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetSnapshotsRequest(
            query=_models.GetSnapshotsRequestQuery(sandbox_id=sandbox_id, limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_snapshots: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/snapshots"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_snapshots")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_snapshots", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_snapshots",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: templates
@mcp.tool()
async def create_template(
    name: str | None = Field(None, description="Name of the template. Optionally include a version tag using colon separator (e.g., 'my-template:v1'). If a tag is provided in the name, it will be added to the tags array automatically."),
    tags: list[str] | None = Field(None, description="Tags to assign to the template for organization and categorization. Tags help identify and group related templates."),
    cpu_count: str | None = Field(None, alias="cpuCount", description="Number of CPU cores to allocate to the sandbox. Must be at least 1 core."),
    memory_mb: str | None = Field(None, alias="memoryMB", description="Memory to allocate to the sandbox in mebibytes (MiB). Must be at least 128 MiB."),
) -> dict[str, Any]:
    """Create a new template with optional resource specifications and organizational tags. Templates define sandbox configurations for reproducible environments."""

    _cpu_count = _parse_int(cpu_count)
    _memory_mb = _parse_int(memory_mb)

    # Construct request model with validation
    try:
        _request = _models.PostV3TemplatesRequest(
            body=_models.PostV3TemplatesRequestBody(name=name, tags=tags, cpu_count=_cpu_count, memory_mb=_memory_mb)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/templates"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_template", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_template",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: templates
@mcp.tool()
async def get_template_files_upload_link(
    template_id: str = Field(..., alias="templateID", description="The unique identifier of the template for which to retrieve the files upload link."),
    hash_: str = Field(..., alias="hash", description="The cryptographic hash that identifies the specific version or snapshot of the template files to retrieve."),
) -> dict[str, Any]:
    """Retrieve a download link for a tar archive containing the build layer files associated with a specific template. The link is generated based on the template ID and file hash."""

    # Construct request model with validation
    try:
        _request = _models.GetTemplatesFilesRequest(
            path=_models.GetTemplatesFilesRequestPath(template_id=template_id, hash_=hash_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_template_files_upload_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/templates/{templateID}/files/{hash}", _request.path.model_dump(by_alias=True)) if _request.path else "/templates/{templateID}/files/{hash}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_template_files_upload_link")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_template_files_upload_link", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_template_files_upload_link",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: templates
@mcp.tool()
async def list_templates(team_id: str | None = Field(None, alias="teamID", description="Filter templates to a specific team. If omitted, returns templates accessible to all teams or the default scope.")) -> dict[str, Any]:
    """Retrieve all templates available in the system, optionally filtered by a specific team. Use this to discover and display template options for users."""

    # Construct request model with validation
    try:
        _request = _models.GetTemplatesRequest(
            query=_models.GetTemplatesRequestQuery(team_id=team_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_templates: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/templates"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_templates")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_templates", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_templates",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: templates
@mcp.tool()
async def list_template_builds(
    template_id: str = Field(..., alias="templateID", description="The unique identifier of the template for which to retrieve builds."),
    limit: str | None = Field(None, description="The maximum number of builds to return in a single page of results. Defaults to 100 if not specified."),
) -> dict[str, Any]:
    """Retrieve all builds associated with a specific template. Use pagination to control the number of results returned per page."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetTemplatesByTemplateIdRequest(
            path=_models.GetTemplatesByTemplateIdRequestPath(template_id=template_id),
            query=_models.GetTemplatesByTemplateIdRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_template_builds: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/templates/{templateID}", _request.path.model_dump(by_alias=True)) if _request.path else "/templates/{templateID}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_template_builds")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_template_builds", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_template_builds",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: templates
@mcp.tool()
async def delete_template(template_id: str = Field(..., alias="templateID", description="The unique identifier of the template to delete.")) -> dict[str, Any]:
    """Permanently delete a template by its ID. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteTemplatesRequest(
            path=_models.DeleteTemplatesRequestPath(template_id=template_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/templates/{templateID}", _request.path.model_dump(by_alias=True)) if _request.path else "/templates/{templateID}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_template", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_template",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: templates
@mcp.tool()
async def start_template_build(
    template_id: str = Field(..., alias="templateID", description="The unique identifier of the template to build."),
    build_id: str = Field(..., alias="buildID", description="The unique identifier for this specific build execution."),
    from_template: str | None = Field(None, alias="fromTemplate", description="Optional template ID to use as a base for this template build, allowing inheritance of template configuration."),
    from_image_registry: Annotated[_models.AwsRegistry | _models.GcpRegistry | _models.GeneralRegistry, Field(discriminator="type_")] | None = Field(None, alias="fromImageRegistry", description="Optional image registry configuration for sourcing or pushing build artifacts."),
    force: bool | None = Field(None, description="Whether to bypass cache and force the entire build to execute from scratch."),
    steps: list[_models.TemplateStep] | None = Field(None, description="Ordered list of build steps to execute. Each step represents a discrete build operation performed sequentially."),
    start_cmd: str | None = Field(None, alias="startCmd", description="Command to execute within the template after the build completes, typically used to start services or initialize the environment."),
    ready_cmd: str | None = Field(None, alias="readyCmd", description="Command to execute after the build to verify the template is ready and operational, used for health checks or readiness validation."),
) -> dict[str, Any]:
    """Initiate a build process for a specific template. This operation executes the build with optional customization including base template selection, build steps, and post-build commands."""

    # Construct request model with validation
    try:
        _request = _models.PostV2TemplatesBuildsRequest(
            path=_models.PostV2TemplatesBuildsRequestPath(template_id=template_id, build_id=build_id),
            body=_models.PostV2TemplatesBuildsRequestBody(from_template=from_template, from_image_registry=from_image_registry, force=force, steps=steps, start_cmd=start_cmd, ready_cmd=ready_cmd)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for start_template_build: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/templates/{templateID}/builds/{buildID}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/templates/{templateID}/builds/{buildID}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("start_template_build")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("start_template_build", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="start_template_build",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: templates
@mcp.tool()
async def update_template(
    template_id: str = Field(..., alias="templateID", description="The unique identifier of the template to update."),
    public: bool | None = Field(None, description="Controls template visibility. When true, the template is accessible to anyone; when false, it is restricted to team members only."),
) -> dict[str, Any]:
    """Update an existing template's properties, such as its visibility settings. Modify template accessibility to be public or restricted to team members only."""

    # Construct request model with validation
    try:
        _request = _models.PatchV2TemplatesRequest(
            path=_models.PatchV2TemplatesRequestPath(template_id=template_id),
            body=_models.PatchV2TemplatesRequestBody(public=public)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/templates/{templateID}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/templates/{templateID}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_template", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_template",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: templates
@mcp.tool()
async def get_template_build_status(
    template_id: str = Field(..., alias="templateID", description="The unique identifier of the template containing the build."),
    build_id: str = Field(..., alias="buildID", description="The unique identifier of the build whose status should be retrieved."),
    logs_offset: str | None = Field(None, alias="logsOffset", description="The starting index for build logs to return. Use this to paginate through large log sets."),
    limit: str | None = Field(None, description="The maximum number of build logs to return in the response. Useful for controlling response size and pagination."),
    level: Literal["debug", "info", "warn", "error"] | None = Field(None, description="Filter logs by severity level. Returns only logs matching the specified level or higher priority."),
) -> dict[str, Any]:
    """Retrieve the current status and build logs for a specific template build. Returns build information with optional log filtering by offset, limit, and severity level."""

    _logs_offset = _parse_int(logs_offset)
    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetTemplatesBuildsStatusRequest(
            path=_models.GetTemplatesBuildsStatusRequestPath(template_id=template_id, build_id=build_id),
            query=_models.GetTemplatesBuildsStatusRequestQuery(logs_offset=_logs_offset, limit=_limit, level=level)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_template_build_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/templates/{templateID}/builds/{buildID}/status", _request.path.model_dump(by_alias=True)) if _request.path else "/templates/{templateID}/builds/{buildID}/status"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_template_build_status")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_template_build_status", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_template_build_status",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: templates
@mcp.tool()
async def list_template_build_logs(
    template_id: str = Field(..., alias="templateID", description="The unique identifier of the template containing the build."),
    build_id: str = Field(..., alias="buildID", description="The unique identifier of the build whose logs should be retrieved."),
    cursor: str | None = Field(None, description="Starting point for log retrieval specified as a Unix timestamp in milliseconds. Logs returned will be from this timestamp onward (or backward, depending on direction)."),
    limit: str | None = Field(None, description="Maximum number of log entries to return in a single response."),
    direction: Literal["forward", "backward"] | None = Field(None, description="Order in which log entries should be returned relative to the cursor timestamp."),
    level: Literal["debug", "info", "warn", "error"] | None = Field(None, description="Filter logs by severity level. Only entries matching the specified level will be returned."),
    source: Literal["temporary", "persistent"] | None = Field(None, description="Filter logs by their storage source. Temporary logs are transient, while persistent logs are retained long-term."),
) -> dict[str, Any]:
    """Retrieve logs from a template build execution. Supports filtering by log level and source, with pagination and directional traversal of log entries."""

    _cursor = _parse_int(cursor)
    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetTemplatesBuildsLogsRequest(
            path=_models.GetTemplatesBuildsLogsRequestPath(template_id=template_id, build_id=build_id),
            query=_models.GetTemplatesBuildsLogsRequestQuery(cursor=_cursor, limit=_limit, direction=direction, level=level, source=source)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_template_build_logs: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/templates/{templateID}/builds/{buildID}/logs", _request.path.model_dump(by_alias=True)) if _request.path else "/templates/{templateID}/builds/{buildID}/logs"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_template_build_logs")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_template_build_logs", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_template_build_logs",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: tags
@mcp.tool()
async def assign_template_tags(
    target: str = Field(..., description="The target template specified in 'name:tag' format, where name is the template identifier and tag is the specific build version."),
    tags: list[str] = Field(..., description="Array of tags to assign to the template. Tags are applied in the order provided and can be used for categorization and filtering."),
) -> dict[str, Any]:
    """Assign one or more tags to a specific template build. Tags help organize and categorize templates for easier discovery and management."""

    # Construct request model with validation
    try:
        _request = _models.PostTemplatesTagsRequest(
            body=_models.PostTemplatesTagsRequestBody(target=target, tags=tags)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for assign_template_tags: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/templates/tags"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("assign_template_tags")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("assign_template_tags", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="assign_template_tags",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: tags
@mcp.tool()
async def remove_template_tags(
    name: str = Field(..., description="The name of the template from which tags will be removed."),
    tags: list[str] = Field(..., description="An array of tag names to remove from the template. Order is not significant."),
) -> dict[str, Any]:
    """Remove one or more tags from a specific template. This operation allows bulk deletion of tags associated with a template."""

    # Construct request model with validation
    try:
        _request = _models.DeleteTemplatesTagsRequest(
            body=_models.DeleteTemplatesTagsRequestBody(name=name, tags=tags)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_template_tags: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/templates/tags"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_template_tags")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_template_tags", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_template_tags",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: tags
@mcp.tool()
async def list_template_tags(template_id: str = Field(..., alias="templateID", description="The unique identifier of the template for which to retrieve tags.")) -> dict[str, Any]:
    """Retrieve all tags associated with a specific template. Tags are used to categorize and organize templates for easier discovery and management."""

    # Construct request model with validation
    try:
        _request = _models.GetTemplatesTagsRequest(
            path=_models.GetTemplatesTagsRequestPath(template_id=template_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_template_tags: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/templates/{templateID}/tags", _request.path.model_dump(by_alias=True)) if _request.path else "/templates/{templateID}/tags"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_template_tags")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_template_tags", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_template_tags",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: templates
@mcp.tool()
async def check_template_alias(alias: str = Field(..., description="The unique identifier or name of the template to check for existence.")) -> dict[str, Any]:
    """Verify whether a template with the specified alias exists in the system."""

    # Construct request model with validation
    try:
        _request = _models.GetTemplatesAliasesRequest(
            path=_models.GetTemplatesAliasesRequestPath(alias=alias)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for check_template_alias: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/templates/aliases/{alias}", _request.path.model_dump(by_alias=True)) if _request.path else "/templates/aliases/{alias}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("check_template_alias")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("check_template_alias", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="check_template_alias",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: admin
@mcp.tool()
async def list_nodes() -> dict[str, Any]:
    """Retrieve a list of all available nodes in the system. Use this operation to discover and monitor all nodes."""

    # Extract parameters for API call
    _http_path = "/nodes"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_nodes")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_nodes", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_nodes",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: admin
@mcp.tool()
async def get_node(
    node_id: str = Field(..., alias="nodeID", description="The unique identifier of the node to retrieve."),
    cluster_id: str | None = Field(None, alias="clusterID", description="The cluster to which the node belongs. Use this to scope the node lookup to a specific cluster."),
) -> dict[str, Any]:
    """Retrieve detailed information about a specific node, optionally filtered by cluster membership."""

    # Construct request model with validation
    try:
        _request = _models.GetNodesByNodeIdRequest(
            path=_models.GetNodesByNodeIdRequestPath(node_id=node_id),
            query=_models.GetNodesByNodeIdRequestQuery(cluster_id=cluster_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_node: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/nodes/{nodeID}", _request.path.model_dump(by_alias=True)) if _request.path else "/nodes/{nodeID}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_node")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_node", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_node",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: admin
@mcp.tool()
async def update_node_status(
    node_id: str = Field(..., alias="nodeID", description="The unique identifier of the node to update."),
    status: Literal["ready", "draining", "connecting", "unhealthy"] = Field(..., description="The desired operational status for the node. Determines how the node handles workloads and cluster participation."),
    cluster_id: str | None = Field(None, alias="clusterID", description="The unique identifier of the cluster containing the node. Required to scope the node operation within the correct cluster context."),
) -> dict[str, Any]:
    """Update the operational status of a node within a cluster. This operation allows you to transition a node between different states such as ready, draining, connecting, or unhealthy."""

    # Construct request model with validation
    try:
        _request = _models.PostNodesRequest(
            path=_models.PostNodesRequestPath(node_id=node_id),
            body=_models.PostNodesRequestBody(cluster_id=cluster_id, status=status)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_node_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/nodes/{nodeID}", _request.path.model_dump(by_alias=True)) if _request.path else "/nodes/{nodeID}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_node_status")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_node_status", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_node_status",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: admin
@mcp.tool()
async def terminate_team_sandboxes(team_id: str = Field(..., alias="teamID", description="The unique identifier of the team whose sandboxes should be terminated.")) -> dict[str, Any]:
    """Terminates all active sandboxes for a specified team. This operation will immediately stop and remove all sandbox instances associated with the team."""

    # Construct request model with validation
    try:
        _request = _models.PostAdminTeamsSandboxesKillRequest(
            path=_models.PostAdminTeamsSandboxesKillRequestPath(team_id=team_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for terminate_team_sandboxes: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/teams/{teamID}/sandboxes/kill", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/teams/{teamID}/sandboxes/kill"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("terminate_team_sandboxes")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("terminate_team_sandboxes", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="terminate_team_sandboxes",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: access-tokens
@mcp.tool()
async def create_access_token(name: str = Field(..., description="A descriptive name for the access token to help identify its purpose or associated application.")) -> dict[str, Any]:
    """Create a new access token for API authentication. The token can be used to authorize requests to protected endpoints."""

    # Construct request model with validation
    try:
        _request = _models.PostAccessTokensRequest(
            body=_models.PostAccessTokensRequestBody(name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_access_token: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/access-tokens"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_access_token")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_access_token", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_access_token",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: access-tokens
@mcp.tool()
async def revoke_access_token(access_token_id: str = Field(..., alias="accessTokenID", description="The unique identifier of the access token to revoke and delete.")) -> dict[str, Any]:
    """Revoke and delete an access token, immediately invalidating it for future API requests."""

    # Construct request model with validation
    try:
        _request = _models.DeleteAccessTokensRequest(
            path=_models.DeleteAccessTokensRequestPath(access_token_id=access_token_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for revoke_access_token: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/access-tokens/{accessTokenID}", _request.path.model_dump(by_alias=True)) if _request.path else "/access-tokens/{accessTokenID}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("revoke_access_token")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("revoke_access_token", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="revoke_access_token",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: api-keys
@mcp.tool()
async def list_api_keys() -> dict[str, Any]:
    """Retrieve all API keys associated with your team. Use this to view and manage authentication credentials for API access."""

    # Extract parameters for API call
    _http_path = "/api-keys"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_api_keys")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_api_keys", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_api_keys",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: api-keys
@mcp.tool()
async def create_api_key(name: str = Field(..., description="A descriptive name for the API key to help identify its purpose or associated application.")) -> dict[str, Any]:
    """Create a new API key for your team to authenticate API requests. The key can be used to access team resources and data."""

    # Construct request model with validation
    try:
        _request = _models.PostApiKeysRequest(
            body=_models.PostApiKeysRequestBody(name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_api_key: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api-keys"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_api_key")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_api_key", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_api_key",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: api-keys
@mcp.tool()
async def update_api_key(
    api_key_id: str = Field(..., alias="apiKeyID", description="The unique identifier of the API key to update."),
    name: str = Field(..., description="The new name for the API key. Use a descriptive name to identify the key's purpose or associated application."),
) -> dict[str, Any]:
    """Update the name of a team API key. Allows you to rename an existing API key for better organization and identification."""

    # Construct request model with validation
    try:
        _request = _models.PatchApiKeysRequest(
            path=_models.PatchApiKeysRequestPath(api_key_id=api_key_id),
            body=_models.PatchApiKeysRequestBody(name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_api_key: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api-keys/{apiKeyID}", _request.path.model_dump(by_alias=True)) if _request.path else "/api-keys/{apiKeyID}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_api_key")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_api_key", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_api_key",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: api-keys
@mcp.tool()
async def delete_api_key(api_key_id: str = Field(..., alias="apiKeyID", description="The unique identifier of the API key to delete.")) -> dict[str, Any]:
    """Permanently delete a team API key. This action cannot be undone and will invalidate any requests using this key."""

    # Construct request model with validation
    try:
        _request = _models.DeleteApiKeysRequest(
            path=_models.DeleteApiKeysRequestPath(api_key_id=api_key_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_api_key: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api-keys/{apiKeyID}", _request.path.model_dump(by_alias=True)) if _request.path else "/api-keys/{apiKeyID}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_api_key")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_api_key", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_api_key",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: volumes
@mcp.tool()
async def list_volumes() -> dict[str, Any]:
    """Retrieve all volumes available to the team. This operation returns a complete list of storage volumes with their metadata and configuration details."""

    # Extract parameters for API call
    _http_path = "/volumes"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_volumes")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_volumes", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_volumes",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: volumes
@mcp.tool()
async def create_volume(name: str = Field(..., description="The name identifier for the volume. Must contain only letters, numbers, hyphens, and underscores.", pattern="^[a-zA-Z0-9_-]+$")) -> dict[str, Any]:
    """Create a new team volume for storing and organizing data. The volume name must be unique within the team and follow alphanumeric naming conventions."""

    # Construct request model with validation
    try:
        _request = _models.PostVolumesRequest(
            body=_models.PostVolumesRequestBody(name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_volume: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/volumes"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_volume")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_volume", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_volume",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: volumes
@mcp.tool()
async def get_volume(volume_id: str = Field(..., alias="volumeID", description="The unique identifier of the volume to retrieve.")) -> dict[str, Any]:
    """Retrieve detailed information about a specific team volume by its unique identifier."""

    # Construct request model with validation
    try:
        _request = _models.GetVolumesByVolumeIdRequest(
            path=_models.GetVolumesByVolumeIdRequestPath(volume_id=volume_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_volume: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/volumes/{volumeID}", _request.path.model_dump(by_alias=True)) if _request.path else "/volumes/{volumeID}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_volume")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_volume", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_volume",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: volumes
@mcp.tool()
async def delete_volume(volume_id: str = Field(..., alias="volumeID", description="The unique identifier of the volume to delete.")) -> dict[str, Any]:
    """Permanently delete a team volume by its ID. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteVolumesRequest(
            path=_models.DeleteVolumesRequestPath(volume_id=volume_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_volume: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/volumes/{volumeID}", _request.path.model_dump(by_alias=True)) if _request.path else "/volumes/{volumeID}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_volume")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_volume", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_volume",
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
        print("  python e2b_server.py", file=sys.stderr)
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

    parser = argparse.ArgumentParser(description="E2B MCP Server")

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
    logger.info("Starting E2B MCP Server")
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

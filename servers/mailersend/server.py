#!/usr/bin/env python3
"""
MailerSend MCP Server
Generated: 2026-04-09 18:53:38 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

import argparse
import asyncio
import collections
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

# Server variables (from OpenAPI spec, overridable via SERVER_* env vars)
_SERVER_VARS = {
    "protocol": os.getenv("SERVER_PROTOCOL", "https"),
    "host": os.getenv("SERVER_HOST", "api.mailersend.com"),
}
BASE_URL = os.getenv("BASE_URL", "{protocol}://{host}/v1".format_map(collections.defaultdict(str, _SERVER_VARS)))
SERVER_NAME = "MailerSend"
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
    'bearerAuth',
]

# Initialize authentication handlers at server startup
_auth_handlers: dict[str, Any] = {}
try:
    _auth_handlers["bearerAuth"] = _auth.BearerTokenAuth(env_var="BEARER_TOKEN", token_format="Bearer")
    logging.info("Authentication configured: bearerAuth")
except ValueError as e:
    # Extract credential names from error message (first sentence before "Leave empty")
    error_msg = str(e).split("Leave empty")[0].strip()
    logging.warning(f"Credentials for bearerAuth not configured: {error_msg}")
    _auth_handlers["bearerAuth"] = None

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

mcp = FastMCP("MailerSend", middleware=[_JsonCoercionMiddleware()])

# Tags: Email
@mcp.tool()
async def send_email(
    email: str = Field(..., description="The sender's email address in standard email format (e.g., info@yourdomain.com). This address will appear as the 'From' field in the email."),
    to: list[_models.EmailTo] = Field(..., description="Array of recipient email addresses. Each address should be in standard email format. At least one recipient is required."),
    subject: str = Field(..., description="The email subject line. Provide a clear, concise subject that summarizes the email content (e.g., 'Hello Client')."),
    text: str = Field(..., description="The email message body as plain text. Include the main content and any relevant information for the recipient (e.g., 'This is just a friendly hello from your friends.')."),
    name: str | None = Field(None, description="The sender's display name or organization name that appears alongside the email address (e.g., 'Company Name'). Optional; if omitted, only the email address will be displayed."),
) -> dict[str, Any]:
    """Send an email message from a specified sender address to one or more recipients. Use this operation to deliver transactional or notification emails with a subject line and message body."""

    # Construct request model with validation
    try:
        _request = _models.SendAnEmailRequest(
            body=_models.SendAnEmailRequestBody(to=to, subject=subject, text=text,
                from_=_models.SendAnEmailRequestBodyFrom(email=email, name=name))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for send_email: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/email"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("send_email")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("send_email", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="send_email",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Email
@mcp.tool()
async def send_bulk_emails(body: list[_models.SendEmailRequest] = Field(..., description="Array of email objects to send. Each object should contain recipient, subject, and message content. Order is preserved for processing.")) -> dict[str, Any]:
    """Send multiple emails in a single batch request. Accepts an array of email configurations to be processed and delivered."""

    # Construct request model with validation
    try:
        _request = _models.SendBulkEmailsRequest(
            body=_models.SendBulkEmailsRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for send_bulk_emails: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/bulk-email"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("send_bulk_emails")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("send_bulk_emails", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="send_bulk_emails",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Email
@mcp.tool()
async def get_bulk_email_status(bulk_email_id: str = Field(..., description="The unique identifier of the bulk email campaign whose status you want to retrieve.")) -> dict[str, Any]:
    """Retrieve the current status and details of a bulk email campaign. Use this to check delivery progress, completion state, and any associated metrics for a specific bulk email operation."""

    # Construct request model with validation
    try:
        _request = _models.GetBulkEmailStatusRequest(
            path=_models.GetBulkEmailStatusRequestPath(bulk_email_id=bulk_email_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_bulk_email_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/bulk-email/{bulk_email_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/bulk-email/{bulk_email_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_bulk_email_status")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_bulk_email_status", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_bulk_email_status",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Activity
@mcp.tool()
async def list_activities_for_domain(
    domain_id: str = Field(..., description="The unique identifier of the domain for which to retrieve activities."),
    date_from: str = Field(..., description="The start of the activity time range as a Unix timestamp in UTC. Activities on or after this date will be included."),
    date_to: str = Field(..., description="The end of the activity time range as a Unix timestamp in UTC. Activities on or before this date will be included."),
) -> dict[str, Any]:
    """Retrieve a list of activities for a specific domain within a given time range. Results are filtered by start and end dates in UTC."""

    _date_from = _parse_int(date_from)
    _date_to = _parse_int(date_to)

    # Construct request model with validation
    try:
        _request = _models.GetListOfActivitiesRequest(
            path=_models.GetListOfActivitiesRequestPath(domain_id=domain_id),
            query=_models.GetListOfActivitiesRequestQuery(date_from=_date_from, date_to=_date_to)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_activities_for_domain: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/activity/{domain_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/activity/{domain_id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_activities_for_domain")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_activities_for_domain", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_activities_for_domain",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Activity
@mcp.tool()
async def get_activity(activity_id: str = Field(..., description="The unique identifier of the activity to retrieve.")) -> dict[str, Any]:
    """Retrieve detailed information about a specific activity by its unique identifier."""

    # Construct request model with validation
    try:
        _request = _models.GetSingleActivityRequest(
            path=_models.GetSingleActivityRequestPath(activity_id=activity_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_activity: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/activities/{activity_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/activities/{activity_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_activity")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_activity", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_activity",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Analytics
@mcp.tool()
async def get_activity_data_by_date_range(
    date_from: str = Field(..., description="Start of the date range as a Unix timestamp (seconds since epoch). Must be earlier than or equal to date_to."),
    date_to: str = Field(..., description="End of the date range as a Unix timestamp (seconds since epoch). Must be later than or equal to date_from."),
    events: list[str] = Field(..., description="List of event types to include in the results. Specify which activity events to retrieve (e.g., user_login, page_view, transaction). Order may affect result grouping or filtering behavior."),
) -> dict[str, Any]:
    """Retrieves activity data for a specified date range. Returns analytics events that occurred between the provided start and end timestamps."""

    _date_from = _parse_int(date_from)
    _date_to = _parse_int(date_to)

    # Construct request model with validation
    try:
        _request = _models.GetActivityDataByDateRequest(
            query=_models.GetActivityDataByDateRequestQuery(date_from=_date_from, date_to=_date_to, events=events)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_activity_data_by_date_range: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/analytics/date"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_activity_data_by_date_range")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_activity_data_by_date_range", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_activity_data_by_date_range",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Analytics
@mcp.tool()
async def list_opens_by_country(
    date_from: str = Field(..., description="Start of the date range as a Unix timestamp (seconds since epoch). Defines the beginning of the analytics period to query."),
    date_to: str = Field(..., description="End of the date range as a Unix timestamp (seconds since epoch). Defines the end of the analytics period to query. Must be equal to or after date_from."),
) -> dict[str, Any]:
    """Retrieve email open metrics aggregated by country for a specified date range. Returns open counts and statistics grouped by geographic location."""

    _date_from = _parse_int(date_from)
    _date_to = _parse_int(date_to)

    # Construct request model with validation
    try:
        _request = _models.GetOpensByCountryRequest(
            query=_models.GetOpensByCountryRequestQuery(date_from=_date_from, date_to=_date_to)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_opens_by_country: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/analytics/country"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_opens_by_country")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_opens_by_country", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_opens_by_country",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Analytics
@mcp.tool()
async def list_opens_by_user_agent(
    date_from: str = Field(..., description="Start of the time range as a Unix timestamp (seconds since epoch). This defines the beginning of the analytics period to query."),
    date_to: str = Field(..., description="End of the time range as a Unix timestamp (seconds since epoch). This defines the end of the analytics period to query."),
) -> dict[str, Any]:
    """Retrieves analytics data showing the number of opens grouped by user-agent within a specified time range. Use this to understand which browsers, devices, and applications are opening your content."""

    _date_from = _parse_int(date_from)
    _date_to = _parse_int(date_to)

    # Construct request model with validation
    try:
        _request = _models.GetOpensByUserAgentRequest(
            query=_models.GetOpensByUserAgentRequestQuery(date_from=_date_from, date_to=_date_to)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_opens_by_user_agent: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/analytics/ua-name"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_opens_by_user_agent")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_opens_by_user_agent", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_opens_by_user_agent",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Analytics
@mcp.tool()
async def get_opens_by_reading_environment(
    date_from: str = Field(..., description="Start of the date range as a Unix timestamp (seconds since epoch). This defines the beginning of the analytics period to query."),
    date_to: str = Field(..., description="End of the date range as a Unix timestamp (seconds since epoch). This defines the end of the analytics period to query."),
) -> dict[str, Any]:
    """Retrieves analytics data on content opens segmented by reading environment (e.g., web, mobile, app). Results are filtered by the specified date range."""

    _date_from = _parse_int(date_from)
    _date_to = _parse_int(date_to)

    # Construct request model with validation
    try:
        _request = _models.GetOpensByReadingEnvironmentRequest(
            query=_models.GetOpensByReadingEnvironmentRequestQuery(date_from=_date_from, date_to=_date_to)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_opens_by_reading_environment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/analytics/ua-type"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_opens_by_reading_environment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_opens_by_reading_environment", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_opens_by_reading_environment",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Domains
@mcp.tool()
async def list_domains() -> dict[str, Any]:
    """Retrieve a complete list of all domains available in the system. Use this operation to discover and enumerate domains for management or reference purposes."""

    # Extract parameters for API call
    _http_path = "/domains"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_domains")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_domains", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_domains",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Domains
@mcp.tool()
async def create_domain(name: str = Field(..., description="The fully-qualified domain name to register (e.g., domain.com). Must be a valid domain format.")) -> dict[str, Any]:
    """Register a new domain in the system. The domain name should be a valid fully-qualified domain name (e.g., domain.com)."""

    # Construct request model with validation
    try:
        _request = _models.AddADomainRequest(
            body=_models.AddADomainRequestBody(name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_domain: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/domains"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_domain")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_domain", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_domain",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Domains
@mcp.tool()
async def get_domain(domain_id: str = Field(..., description="The unique identifier of the domain to retrieve.")) -> dict[str, Any]:
    """Retrieve detailed information about a specific domain by its ID. Returns the domain's configuration, status, and metadata."""

    # Construct request model with validation
    try:
        _request = _models.GetSingleDomainRequest(
            path=_models.GetSingleDomainRequestPath(domain_id=domain_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_domain: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/domains/{domain_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/domains/{domain_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_domain")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_domain", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_domain",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Domains
@mcp.tool()
async def delete_domain(domain_id: str = Field(..., description="The unique identifier of the domain to delete.")) -> dict[str, Any]:
    """Permanently delete a domain and remove it from the system. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteADomainRequest(
            path=_models.DeleteADomainRequestPath(domain_id=domain_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_domain: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/domains/{domain_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/domains/{domain_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_domain")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_domain", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_domain",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Domains
@mcp.tool()
async def list_recipients_for_domain(domain_id: str = Field(..., description="The unique identifier of the domain for which to retrieve recipients.")) -> dict[str, Any]:
    """Retrieve all recipients associated with a specific domain. This returns the list of email recipients configured for the given domain."""

    # Construct request model with validation
    try:
        _request = _models.GetRecipientsForADomainRequest(
            path=_models.GetRecipientsForADomainRequestPath(domain_id=domain_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_recipients_for_domain: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/domains/{domain_id}/recipients", _request.path.model_dump(by_alias=True)) if _request.path else "/domains/{domain_id}/recipients"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_recipients_for_domain")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_recipients_for_domain", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_recipients_for_domain",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Domains
@mcp.tool()
async def update_domain_settings(
    domain_id: str = Field(..., description="The unique identifier of the domain whose settings should be updated."),
    track_content: bool | None = Field(None, description="Enable or disable content tracking for this domain. When enabled, the system will monitor and record domain content activity."),
) -> dict[str, Any]:
    """Update configuration settings for a specific domain. Allows modification of domain-level preferences including content tracking behavior."""

    # Construct request model with validation
    try:
        _request = _models.UpdateDomainSettingsRequest(
            path=_models.UpdateDomainSettingsRequestPath(domain_id=domain_id),
            body=_models.UpdateDomainSettingsRequestBody(track_content=track_content)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_domain_settings: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/domains/{domain_id}/settings", _request.path.model_dump(by_alias=True)) if _request.path else "/domains/{domain_id}/settings"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_domain_settings")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_domain_settings", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_domain_settings",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Domains
@mcp.tool()
async def list_dns_records(domain_id: str = Field(..., description="The unique identifier of the domain for which to retrieve DNS records.")) -> dict[str, Any]:
    """Retrieve all DNS records configured for a specific domain. Returns a collection of DNS records including their types, values, and configuration details."""

    # Construct request model with validation
    try:
        _request = _models.GetDnsRecordsRequest(
            path=_models.GetDnsRecordsRequestPath(domain_id=domain_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_dns_records: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/domains/{domain_id}/dns-records", _request.path.model_dump(by_alias=True)) if _request.path else "/domains/{domain_id}/dns-records"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_dns_records")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_dns_records", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_dns_records",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Domains
@mcp.tool()
async def get_domain_verification_status(domain_id: str = Field(..., description="The unique identifier of the domain whose verification status you want to check.")) -> dict[str, Any]:
    """Retrieve the current verification status of a domain, including whether it has been successfully verified and any relevant verification details."""

    # Construct request model with validation
    try:
        _request = _models.GetVerificationStatusRequest(
            path=_models.GetVerificationStatusRequestPath(domain_id=domain_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_domain_verification_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/domains/{domain_id}/verify", _request.path.model_dump(by_alias=True)) if _request.path else "/domains/{domain_id}/verify"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_domain_verification_status")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_domain_verification_status", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_domain_verification_status",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Sender Identities
@mcp.tool()
async def list_sender_identities() -> dict[str, Any]:
    """Retrieve a list of all configured sender identities available for sending messages or emails from this account."""

    # Extract parameters for API call
    _http_path = "/identities"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_sender_identities")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_sender_identities", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_sender_identities",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Sender Identities
@mcp.tool()
async def create_sender_identity(
    domain_id: str = Field(..., description="The unique identifier of your domain where this sender identity will be registered."),
    email: str = Field(..., description="The email address for this sender identity. Must be a valid email format (e.g., user@example.com)."),
    name: str = Field(..., description="The display name associated with this sender identity, shown to recipients when emails are sent (e.g., 'John Smith' or 'Support Team')."),
) -> dict[str, Any]:
    """Register a new sender identity for your domain, enabling you to send emails from a specific email address with an associated display name."""

    # Construct request model with validation
    try:
        _request = _models.AddASenderIdentityRequest(
            body=_models.AddASenderIdentityRequestBody(domain_id=domain_id, email=email, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_sender_identity: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/identities"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_sender_identity")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_sender_identity", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_sender_identity",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Sender Identities
@mcp.tool()
async def get_sender_identity(identity_id: str = Field(..., description="The unique identifier of the sender identity to retrieve.")) -> dict[str, Any]:
    """Retrieve detailed information about a specific sender identity by its ID. Use this to view configuration and settings for an individual sender identity."""

    # Construct request model with validation
    try:
        _request = _models.GetSingleSenderIdentityRequest(
            path=_models.GetSingleSenderIdentityRequestPath(identity_id=identity_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_sender_identity: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/identities/{identity_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/identities/{identity_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_sender_identity")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_sender_identity", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_sender_identity",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Sender Identities
@mcp.tool()
async def update_sender_identity(
    identity_id: str = Field(..., description="The unique identifier of the sender identity to update."),
    name: str | None = Field(None, description="The new display name for the sender identity. This is how the identity will be presented in outgoing messages."),
) -> dict[str, Any]:
    """Update the configuration of an existing sender identity, such as its display name. This allows you to modify how your sender identity appears in outgoing communications."""

    # Construct request model with validation
    try:
        _request = _models.UpdateASenderIdentityRequest(
            path=_models.UpdateASenderIdentityRequestPath(identity_id=identity_id),
            body=_models.UpdateASenderIdentityRequestBody(name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_sender_identity: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/identities/{identity_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/identities/{identity_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_sender_identity")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_sender_identity", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_sender_identity",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Sender Identities
@mcp.tool()
async def delete_sender_identity(identity_id: str = Field(..., description="The unique identifier of the sender identity to delete. This ID must correspond to an existing sender identity in your account.")) -> dict[str, Any]:
    """Permanently delete a sender identity from your account. Once deleted, this identity can no longer be used to send messages."""

    # Construct request model with validation
    try:
        _request = _models.DeleteASenderIdentityRequest(
            path=_models.DeleteASenderIdentityRequestPath(identity_id=identity_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_sender_identity: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/identities/{identity_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/identities/{identity_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_sender_identity")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_sender_identity", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_sender_identity",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Sender Identities
@mcp.tool()
async def get_sender_identity_by_email(client_email_com: str = Field(..., alias="clientemail.com", description="The email address of the sender identity to retrieve. Must be a valid email format.")) -> dict[str, Any]:
    """Retrieve a single sender identity by its email address. Use this to look up configuration and details for a specific sender."""

    # Construct request model with validation
    try:
        _request = _models.GetSingleSenderIdentityByEmailRequest(
            path=_models.GetSingleSenderIdentityByEmailRequestPath(client_email_com=client_email_com)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_sender_identity_by_email: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/identities/email/{client@email.com}", _request.path.model_dump(by_alias=True)) if _request.path else "/identities/email/{client@email.com}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_sender_identity_by_email")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_sender_identity_by_email", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_sender_identity_by_email",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Sender Identities
@mcp.tool()
async def update_sender_identity_by_email(
    client_email_com: str = Field(..., alias="clientemail.com", description="The email address of the sender identity to update. Must be a valid email format."),
    name: str | None = Field(None, description="The new display name for the sender identity. Optional field to customize how the sender appears in outgoing communications."),
) -> dict[str, Any]:
    """Update the configuration of a sender identity using its email address. Allows modification of sender identity properties such as the display name."""

    # Construct request model with validation
    try:
        _request = _models.UpdateASenderIdentityByEmailRequest(
            path=_models.UpdateASenderIdentityByEmailRequestPath(client_email_com=client_email_com),
            body=_models.UpdateASenderIdentityByEmailRequestBody(name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_sender_identity_by_email: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/identities/email/{client@email.com}", _request.path.model_dump(by_alias=True)) if _request.path else "/identities/email/{client@email.com}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_sender_identity_by_email")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_sender_identity_by_email", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_sender_identity_by_email",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Sender Identities
@mcp.tool()
async def delete_sender_identity_by_email(client_email_com: str = Field(..., alias="clientemail.com", description="The email address of the sender identity to delete. Must be a valid email format.")) -> dict[str, Any]:
    """Permanently delete a sender identity from your account using its email address. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteASenderIdentityByEmailRequest(
            path=_models.DeleteASenderIdentityByEmailRequestPath(client_email_com=client_email_com)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_sender_identity_by_email: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/identities/email/{client@email.com}", _request.path.model_dump(by_alias=True)) if _request.path else "/identities/email/{client@email.com}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_sender_identity_by_email")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_sender_identity_by_email", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_sender_identity_by_email",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Inbound Routing
@mcp.tool()
async def list_inbound_routes() -> dict[str, Any]:
    """Retrieve a list of all configured inbound routes. Use this to view routing rules for incoming messages or requests."""

    # Extract parameters for API call
    _http_path = "/inbound"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_inbound_routes")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_inbound_routes", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_inbound_routes",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Inbound Routing
@mcp.tool()
async def get_inbound_route(inbound_id: str = Field(..., description="The unique identifier of the inbound route to retrieve.")) -> dict[str, Any]:
    """Retrieve the configuration and details of a specific inbound route by its ID. Use this to view routing rules, destination settings, and other properties of an individual inbound route."""

    # Construct request model with validation
    try:
        _request = _models.GetSingleInboundRouteRequest(
            path=_models.GetSingleInboundRouteRequestPath(inbound_id=inbound_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_inbound_route: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/inbound/{inbound_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/inbound/{inbound_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_inbound_route")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_inbound_route", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_inbound_route",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Inbound Routing
@mcp.tool()
async def update_inbound_route(
    inbound_id: str = Field(..., description="The unique identifier of the inbound route to update. This ID is required to target the specific route for modification."),
    name: str | None = Field(None, description="A human-readable name for the inbound route to help identify its purpose or destination."),
    domain_enabled: bool | None = Field(None, description="Enable or disable domain-based routing for this inbound route. When enabled, the route processes domain-specific logic."),
    inbound_priority: int | None = Field(None, description="The priority level for this route when multiple routes could match the same inbound request. Lower numbers indicate higher priority and are evaluated first."),
    match_filter_type: str | None = Field(None, alias="match_filterType", description="The type of matching filter to apply. Use 'match_all' to process all requests, or specify a more restrictive filter type to target specific request patterns."),
    catch_filter_type: str | None = Field(None, alias="catch_filterType", description="The type of catch filter to apply as a fallback. Use 'catch_all' to handle requests that don't match other filters, or specify a more specific filter type."),
    forwards: list[_models.UpdateAnInboundRouteBodyForwardsItem] | None = Field(None, description="An ordered list of forwarding destinations where matched inbound requests should be routed. The order determines the sequence in which destinations are attempted."),
) -> dict[str, Any]:
    """Update configuration settings for an inbound route, including its name, domain enablement, priority, and filtering rules. Changes take effect immediately for new incoming requests matching this route."""

    # Construct request model with validation
    try:
        _request = _models.UpdateAnInboundRouteRequest(
            path=_models.UpdateAnInboundRouteRequestPath(inbound_id=inbound_id),
            body=_models.UpdateAnInboundRouteRequestBody(name=name, domain_enabled=domain_enabled, inbound_priority=inbound_priority, forwards=forwards,
                match_filter=_models.UpdateAnInboundRouteRequestBodyMatchFilter(type_=match_filter_type) if any(v is not None for v in [match_filter_type]) else None,
                catch_filter=_models.UpdateAnInboundRouteRequestBodyCatchFilter(type_=catch_filter_type) if any(v is not None for v in [catch_filter_type]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_inbound_route: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/inbound/{inbound_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/inbound/{inbound_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_inbound_route")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_inbound_route", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_inbound_route",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Inbound Routing
@mcp.tool()
async def delete_inbound_route(inbound_id: str = Field(..., description="The unique identifier of the inbound route to delete. This must be a valid inbound route ID that exists in the system.")) -> dict[str, Any]:
    """Permanently delete an inbound route by its ID. This action cannot be undone and will remove all routing rules associated with the specified inbound route."""

    # Construct request model with validation
    try:
        _request = _models.DeleteAnInboundRouteRequest(
            path=_models.DeleteAnInboundRouteRequestPath(inbound_id=inbound_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_inbound_route: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/inbound/{inbound_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/inbound/{inbound_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_inbound_route")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_inbound_route", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_inbound_route",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Messages
@mcp.tool()
async def list_messages() -> dict[str, Any]:
    """Retrieve a list of all messages. Use this operation to fetch messages for display, filtering, or further processing."""

    # Extract parameters for API call
    _http_path = "/messages"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_messages")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_messages", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_messages",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Messages
@mcp.tool()
async def get_message(message_id: str = Field(..., description="The unique identifier of the message to retrieve.")) -> dict[str, Any]:
    """Retrieve detailed information for a specific message by its ID. Returns the complete message data including content, metadata, and timestamps."""

    # Construct request model with validation
    try:
        _request = _models.GetInformationForSingleMessageRequest(
            path=_models.GetInformationForSingleMessageRequestPath(message_id=message_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_message: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/messages/{message_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/messages/{message_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_message")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_message", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_message",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Scheduled Messages
@mcp.tool()
async def list_scheduled_messages() -> dict[str, Any]:
    """Retrieve all scheduled messages that are queued for future delivery. Use this to view pending message schedules and their delivery status."""

    # Extract parameters for API call
    _http_path = "/message-schedules"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_scheduled_messages")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_scheduled_messages", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_scheduled_messages",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Scheduled Messages
@mcp.tool()
async def get_scheduled_message(message_id: str = Field(..., description="The unique identifier of the scheduled message to retrieve.")) -> dict[str, Any]:
    """Retrieve the details of a single scheduled message by its ID, including its content, schedule, and delivery status."""

    # Construct request model with validation
    try:
        _request = _models.GetSingleScheduledMessageRequest(
            path=_models.GetSingleScheduledMessageRequestPath(message_id=message_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_scheduled_message: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/message-schedules/{message_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/message-schedules/{message_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_scheduled_message")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_scheduled_message", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_scheduled_message",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Scheduled Messages
@mcp.tool()
async def delete_scheduled_message(message_id: str = Field(..., description="The unique identifier of the scheduled message to delete.")) -> dict[str, Any]:
    """Permanently delete a scheduled message by its ID, preventing it from being sent at its scheduled time."""

    # Construct request model with validation
    try:
        _request = _models.DeleteScheduledMessageRequest(
            path=_models.DeleteScheduledMessageRequestPath(message_id=message_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_scheduled_message: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/message-schedules/{message_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/message-schedules/{message_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_scheduled_message")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_scheduled_message", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_scheduled_message",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Suppressions
@mcp.tool()
async def list_blocklist_recipients() -> dict[str, Any]:
    """Retrieve all recipients currently on the blocklist suppression list. This list contains email addresses that have been suppressed from receiving communications."""

    # Extract parameters for API call
    _http_path = "/suppressions/blocklist"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_blocklist_recipients")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_blocklist_recipients", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_blocklist_recipients",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Suppressions
@mcp.tool()
async def add_blocklist_recipients(
    domain_id: str = Field(..., description="The unique identifier for the domain to which blocklist recipients will be added."),
    recipients: list[str] = Field(..., description="An array of email recipient addresses to add to the blocklist. Each item should be a valid email address string."),
) -> dict[str, Any]:
    """Add one or more email recipients to the blocklist suppression list for a specific domain. Blocklisted recipients will not receive emails sent through this domain."""

    # Construct request model with validation
    try:
        _request = _models.AddBlocklistRecipientsRequest(
            body=_models.AddBlocklistRecipientsRequestBody(domain_id=domain_id, recipients=recipients)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_blocklist_recipients: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/suppressions/blocklist"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_blocklist_recipients")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_blocklist_recipients", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_blocklist_recipients",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Suppressions
@mcp.tool()
async def delete_blocklist_recipients(all_: bool | None = Field(None, alias="all", description="When set to true, removes all recipients from the blocklist. Omit or set to false to delete only specified recipients.")) -> dict[str, Any]:
    """Remove recipients from the blocklist suppression list. Use the all parameter to delete all blocklisted recipients at once, or omit it to delete specific recipients via request body."""

    # Construct request model with validation
    try:
        _request = _models.DeleteBlocklistRecipientsRequest(
            body=_models.DeleteBlocklistRecipientsRequestBody(all_=all_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_blocklist_recipients: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/suppressions/blocklist"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_blocklist_recipients")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_blocklist_recipients", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_blocklist_recipients",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Suppressions
@mcp.tool()
async def list_hard_bounces_recipients() -> dict[str, Any]:
    """Retrieve all recipients from the hard bounces suppression list. This list contains email addresses that have permanently failed delivery and should not receive future messages."""

    # Extract parameters for API call
    _http_path = "/suppressions/hard-bounces"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_hard_bounces_recipients")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_hard_bounces_recipients", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_hard_bounces_recipients",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Suppressions
@mcp.tool()
async def add_recipients_to_hard_bounces_suppression(
    domain_id: str = Field(..., description="The unique identifier of the domain to which the hard bounce suppression list applies."),
    recipients: list[str] = Field(..., description="An array of email recipient addresses to add to the hard bounces suppression list. Each item should be a valid email address string."),
) -> dict[str, Any]:
    """Add one or more email recipients to the hard bounces suppression list for a specific domain. Hard-bounced addresses will be suppressed from future email sends to prevent delivery failures."""

    # Construct request model with validation
    try:
        _request = _models.AddHardBouncesRecipientsRequest(
            body=_models.AddHardBouncesRecipientsRequestBody(domain_id=domain_id, recipients=recipients)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_recipients_to_hard_bounces_suppression: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/suppressions/hard-bounces"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_recipients_to_hard_bounces_suppression")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_recipients_to_hard_bounces_suppression", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_recipients_to_hard_bounces_suppression",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Suppressions
@mcp.tool()
async def delete_hard_bounces_recipients(all_: bool | None = Field(None, alias="all", description="When set to true, removes all recipients from the hard bounces suppression list. Omit this parameter to remove specific recipients instead.")) -> dict[str, Any]:
    """Remove recipients from the hard bounces suppression list. Set the all parameter to true to clear all hard bounced addresses, or omit it to remove specific recipients."""

    # Construct request model with validation
    try:
        _request = _models.DeleteHardBouncesRecipientsRequest(
            body=_models.DeleteHardBouncesRecipientsRequestBody(all_=all_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_hard_bounces_recipients: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/suppressions/hard-bounces"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_hard_bounces_recipients")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_hard_bounces_recipients", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_hard_bounces_recipients",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Suppressions
@mcp.tool()
async def list_spam_complaint_recipients() -> dict[str, Any]:
    """Retrieve all email addresses that have been added to the spam complaints suppression list, preventing future sends to these recipients."""

    # Extract parameters for API call
    _http_path = "/suppressions/spam-complaints"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_spam_complaint_recipients")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_spam_complaint_recipients", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_spam_complaint_recipients",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Suppressions
@mcp.tool()
async def add_spam_complaints_recipients(
    domain_id: str = Field(..., description="The unique identifier of the domain to which spam complaint suppressions will be applied."),
    recipients: list[str] = Field(..., description="A list of email addresses to add to the spam complaints suppression list. Each item should be a valid email address string."),
) -> dict[str, Any]:
    """Add one or more email recipients to the spam complaints suppression list for a specific domain. Suppressed recipients will not receive emails sent through this domain."""

    # Construct request model with validation
    try:
        _request = _models.AddSpamComplaintsRecipientsRequest(
            body=_models.AddSpamComplaintsRecipientsRequestBody(domain_id=domain_id, recipients=recipients)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_spam_complaints_recipients: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/suppressions/spam-complaints"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_spam_complaints_recipients")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_spam_complaints_recipients", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_spam_complaints_recipients",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Suppressions
@mcp.tool()
async def delete_spam_complaints_recipients(all_: bool | None = Field(None, alias="all", description="When set to true, removes all recipients from the spam complaints suppression list. Omit or set to false to delete only specified recipients.")) -> dict[str, Any]:
    """Remove recipients from the spam complaints suppression list. Use the 'all' parameter to delete all recipients at once, or omit it to delete specific recipients via request body."""

    # Construct request model with validation
    try:
        _request = _models.DeleteSpamComplaintsRecipientsRequest(
            body=_models.DeleteSpamComplaintsRecipientsRequestBody(all_=all_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_spam_complaints_recipients: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/suppressions/spam-complaints"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_spam_complaints_recipients")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_spam_complaints_recipients", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_spam_complaints_recipients",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Suppressions
@mcp.tool()
async def list_unsubscribed_recipients() -> dict[str, Any]:
    """Retrieve all recipients from the unsubscribes suppression list. This list contains email addresses that have opted out of communications and should not receive messages."""

    # Extract parameters for API call
    _http_path = "/suppressions/unsubscribes"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_unsubscribed_recipients")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_unsubscribed_recipients", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_unsubscribed_recipients",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Suppressions
@mcp.tool()
async def add_unsubscribe_recipients(
    domain_id: str = Field(..., description="The unique identifier for the domain to which the unsubscribe recipients will be added."),
    recipients: list[str] = Field(..., description="A list of email recipients to add to the unsubscribes suppression list. Each item should be a valid email address."),
) -> dict[str, Any]:
    """Add one or more email recipients to the unsubscribes suppression list for a specific domain, preventing them from receiving future messages."""

    # Construct request model with validation
    try:
        _request = _models.AddUnsubscribesRecipientsRequest(
            body=_models.AddUnsubscribesRecipientsRequestBody(domain_id=domain_id, recipients=recipients)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_unsubscribe_recipients: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/suppressions/unsubscribes"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_unsubscribe_recipients")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_unsubscribe_recipients", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_unsubscribe_recipients",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Suppressions
@mcp.tool()
async def delete_unsubscribed_recipients(all_: bool | None = Field(None, alias="all", description="When set to true, removes all recipients from the unsubscribes suppression list. Omit or set to false to perform targeted removals.")) -> dict[str, Any]:
    """Remove recipients from the unsubscribes suppression list. Set the all parameter to true to clear all unsubscribed recipients at once."""

    # Construct request model with validation
    try:
        _request = _models.DeleteUnsubscribesRecipientsRequest(
            body=_models.DeleteUnsubscribesRecipientsRequestBody(all_=all_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_unsubscribed_recipients: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/suppressions/unsubscribes"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_unsubscribed_recipients")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_unsubscribed_recipients", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_unsubscribed_recipients",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Recipients
@mcp.tool()
async def list_recipients() -> dict[str, Any]:
    """Retrieve a list of all recipients available in the system. Use this to view recipient configurations and details for message delivery or communication purposes."""

    # Extract parameters for API call
    _http_path = "/recipients"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_recipients")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_recipients", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_recipients",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Recipients
@mcp.tool()
async def get_recipient(recipient_id: str = Field(..., description="The unique identifier of the recipient to retrieve.")) -> dict[str, Any]:
    """Retrieve detailed information for a specific recipient by their unique identifier."""

    # Construct request model with validation
    try:
        _request = _models.GetSingleRecipientRequest(
            path=_models.GetSingleRecipientRequestPath(recipient_id=recipient_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_recipient: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/recipients/{recipient_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/recipients/{recipient_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_recipient")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_recipient", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_recipient",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Recipients
@mcp.tool()
async def delete_recipient(recipient_id: str = Field(..., description="The unique identifier of the recipient to delete.")) -> dict[str, Any]:
    """Permanently delete a recipient from the system. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteARecipientRequest(
            path=_models.DeleteARecipientRequestPath(recipient_id=recipient_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_recipient: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/recipients/{recipient_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/recipients/{recipient_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_recipient")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_recipient", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_recipient",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Templates
@mcp.tool()
async def list_templates() -> dict[str, Any]:
    """Retrieve all available templates. Use this to discover template options for your workflows or integrations."""

    # Extract parameters for API call
    _http_path = "/templates"
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
        headers=_http_headers,
    )

    return _response_data

# Tags: Webhooks
@mcp.tool()
async def list_webhooks(domain_id: str = Field(..., description="The unique identifier of the domain for which to retrieve webhooks.")) -> dict[str, Any]:
    """Retrieve all webhooks configured for a specific domain. Returns a list of webhook configurations including their endpoints, event subscriptions, and status."""

    # Construct request model with validation
    try:
        _request = _models.GetListOfWebhooksRequest(
            query=_models.GetListOfWebhooksRequestQuery(domain_id=domain_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_webhooks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/webhooks"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
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
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Webhooks
@mcp.tool()
async def get_webhook(webhook_id: str = Field(..., description="The unique identifier of the webhook to retrieve.")) -> dict[str, Any]:
    """Retrieve the details of a specific webhook by its ID. Returns the webhook configuration including its URL, events, and status."""

    # Construct request model with validation
    try:
        _request = _models.GetAWebhookRequest(
            path=_models.GetAWebhookRequestPath(webhook_id=webhook_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_webhook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/webhooks/{webhook_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/webhooks/{webhook_id}"
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
async def delete_webhook(webhook_id: str = Field(..., description="The unique identifier of the webhook to delete.")) -> dict[str, Any]:
    """Permanently delete a webhook by its ID. This action cannot be undone and will stop all event notifications to the webhook's configured endpoint."""

    # Construct request model with validation
    try:
        _request = _models.DeleteAWebhookRequest(
            path=_models.DeleteAWebhookRequestPath(webhook_id=webhook_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_webhook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/webhooks/{webhook_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/webhooks/{webhook_id}"
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

# Tags: Email Verification
@mcp.tool()
async def verify_email(email: str = Field(..., description="The email address to verify. Must be a valid email format (e.g., user@domain.com).")) -> dict[str, Any]:
    """Verify the validity and deliverability of an email address. This operation checks whether the provided email address is properly formatted and active."""

    # Construct request model with validation
    try:
        _request = _models.VerifyAnEmailRequest(
            body=_models.VerifyAnEmailRequestBody(email=email)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for verify_email: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/email-verification/verify"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("verify_email")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("verify_email", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="verify_email",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Email Verification
@mcp.tool()
async def list_email_verification_lists() -> dict[str, Any]:
    """Retrieve all email verification lists available in the system. Use this to view existing verification lists and their configurations."""

    # Extract parameters for API call
    _http_path = "/email-verification"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_email_verification_lists")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_email_verification_lists", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_email_verification_lists",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Email Verification
@mcp.tool()
async def create_email_verification_list(
    name: str = Field(..., description="A descriptive name for the email verification list (e.g., 'List'). Used to identify and organize verification batches."),
    emails: list[str] = Field(..., description="An array of email addresses to include in the verification list. Each item should be a valid email address string."),
) -> dict[str, Any]:
    """Create a new email verification list with a name and set of email addresses to verify. This list can be used to batch-process email validation across multiple addresses."""

    # Construct request model with validation
    try:
        _request = _models.CreateAnEmailVerificationListRequest(
            body=_models.CreateAnEmailVerificationListRequestBody(name=name, emails=emails)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_email_verification_list: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/email-verification"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_email_verification_list")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_email_verification_list", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_email_verification_list",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Email Verification
@mcp.tool()
async def get_email_verification_list(email_verification_id: str = Field(..., description="The unique identifier of the email verification list to retrieve.")) -> dict[str, Any]:
    """Retrieve a single email verification list by its unique identifier. Use this to fetch details about a specific email verification list for review or further processing."""

    # Construct request model with validation
    try:
        _request = _models.GetSingleEmailVerificationListRequest(
            path=_models.GetSingleEmailVerificationListRequestPath(email_verification_id=email_verification_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_email_verification_list: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/email-verification/{email_verification_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/email-verification/{email_verification_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_email_verification_list")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_email_verification_list", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_email_verification_list",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Email Verification
@mcp.tool()
async def verify_email_verification_list(email_verification_id: str = Field(..., description="The unique identifier of the email verification list to verify. This ID references a specific list that will be processed and validated.")) -> dict[str, Any]:
    """Verify an email verification list by its ID. This operation processes and validates the email addresses in the specified verification list."""

    # Construct request model with validation
    try:
        _request = _models.VerifyAnEmailVerificationListRequest(
            path=_models.VerifyAnEmailVerificationListRequestPath(email_verification_id=email_verification_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for verify_email_verification_list: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/email-verification/{email_verification_id}/verify", _request.path.model_dump(by_alias=True)) if _request.path else "/email-verification/{email_verification_id}/verify"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("verify_email_verification_list")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("verify_email_verification_list", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="verify_email_verification_list",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Email Verification
@mcp.tool()
async def list_email_verification_results(email_verification_id: str = Field(..., description="The unique identifier of the email verification list for which to retrieve results.")) -> dict[str, Any]:
    """Retrieve the verification results for a completed email verification list. Returns detailed status and outcome information for each email address that was processed."""

    # Construct request model with validation
    try:
        _request = _models.GetEmailVerificationListResultsRequest(
            path=_models.GetEmailVerificationListResultsRequestPath(email_verification_id=email_verification_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_email_verification_results: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/email-verification/{email_verification_id}/results", _request.path.model_dump(by_alias=True)) if _request.path else "/email-verification/{email_verification_id}/results"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_email_verification_results")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_email_verification_results", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_email_verification_results",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tokens
@mcp.tool()
async def update_token_status(
    token_id: str = Field(..., description="The unique identifier of the token whose status you want to update."),
    status: Literal["pause", "active"] = Field(..., description="The desired operational status for the token. Set to 'active' to enable the token or 'pause' to temporarily disable it."),
) -> dict[str, Any]:
    """Update the operational status of a token by pausing or activating it. Use this to control whether a token is currently active or temporarily paused."""

    # Construct request model with validation
    try:
        _request = _models.UpdateATokenSettingsRequest(
            path=_models.UpdateATokenSettingsRequestPath(token_id=token_id),
            body=_models.UpdateATokenSettingsRequestBody(status=status)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_token_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/token/{token_id}/settings", _request.path.model_dump(by_alias=True)) if _request.path else "/token/{token_id}/settings"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_token_status")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_token_status", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_token_status",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tokens
@mcp.tool()
async def delete_token(token_id: str = Field(..., description="The unique identifier of the token to delete.")) -> dict[str, Any]:
    """Permanently delete a token by its ID. This action cannot be undone and will immediately invalidate the token for all future requests."""

    # Construct request model with validation
    try:
        _request = _models.DeleteATokenRequest(
            path=_models.DeleteATokenRequestPath(token_id=token_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_token: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/token/{token_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/token/{token_id}"
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

# Tags: Users
@mcp.tool()
async def list_users() -> dict[str, Any]:
    """Retrieve a complete list of all users in the system. Returns user records with their associated metadata and details."""

    # Extract parameters for API call
    _http_path = "/users"
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
        headers=_http_headers,
    )

    return _response_data

# Tags: Users
@mcp.tool()
async def get_user(user_id: str = Field(..., description="The unique identifier of the user to retrieve.")) -> dict[str, Any]:
    """Retrieve a single user by their unique identifier. Returns the user's profile information and details."""

    # Construct request model with validation
    try:
        _request = _models.GetOneUserRequest(
            path=_models.GetOneUserRequestPath(user_id=user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/users/{user_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/users/{user_id}"
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
        headers=_http_headers,
    )

    return _response_data

# Tags: Users
@mcp.tool()
async def update_user_role(
    user_id: str = Field(..., description="The unique identifier of the user whose role should be updated."),
    role: str = Field(..., description="The new role to assign to the user. Valid roles include Admin and other predefined role types supported by the system."),
) -> dict[str, Any]:
    """Update the role assignment for a specific user. This operation allows you to change a user's access level or permissions by assigning them a new role (e.g., Admin)."""

    # Construct request model with validation
    try:
        _request = _models.UpdateUserRequest(
            path=_models.UpdateUserRequestPath(user_id=user_id),
            body=_models.UpdateUserRequestBody(role=role)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_user_role: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/users/{user_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/users/{user_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_user_role")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_user_role", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_user_role",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Users
@mcp.tool()
async def delete_user(user_id: str = Field(..., description="The unique identifier of the user to delete. This must be a valid user ID that exists in the system.")) -> dict[str, Any]:
    """Permanently delete a user account and all associated data from the system. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteAUserRequest(
            path=_models.DeleteAUserRequestPath(user_id=user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/users/{user_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/users/{user_id}"
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
        headers=_http_headers,
    )

    return _response_data

# Tags: SMS
@mcp.tool()
async def send_sms(
    from_: str = Field(..., alias="from", description="The sender's phone number in E.164 format (e.g., +19191234567). This is the number that will appear as the message source."),
    to: list[str] = Field(..., description="Array of recipient phone numbers in E.164 format. Each number will receive the message independently."),
    text: str = Field(..., description="The message content as a string. Supports template variables (e.g., {{name}}) that will be replaced with values from the personalization array for each recipient."),
    personalization: list[_models.SendAnSmsBodyPersonalizationItem] | None = Field(None, description="Optional array of personalization objects that map template variables to recipient-specific values. Used to customize message content for each recipient based on template variables in the text parameter."),
) -> dict[str, Any]:
    """Send an SMS message to one or more recipients with optional personalization support. Supports template variables for dynamic content customization."""

    # Construct request model with validation
    try:
        _request = _models.SendAnSmsRequest(
            body=_models.SendAnSmsRequestBody(from_=from_, to=to, text=text, personalization=personalization)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for send_sms: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/sms"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("send_sms")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("send_sms", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="send_sms",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: SMS Phone Numbers
@mcp.tool()
async def list_sms_phone_numbers() -> dict[str, Any]:
    """Retrieve a list of all SMS phone numbers available in your account. Use this to view phone numbers configured for sending and receiving SMS messages."""

    # Extract parameters for API call
    _http_path = "/sms-numbers"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_sms_phone_numbers")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_sms_phone_numbers", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_sms_phone_numbers",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: SMS Phone Numbers
@mcp.tool()
async def get_sms_phone_number(sms_number_id: str = Field(..., description="The unique identifier of the SMS phone number to retrieve.")) -> dict[str, Any]:
    """Retrieve details for a specific SMS phone number by its ID. Returns the phone number configuration and associated metadata."""

    # Construct request model with validation
    try:
        _request = _models.GetAnSmsPhoneNumberRequest(
            path=_models.GetAnSmsPhoneNumberRequestPath(sms_number_id=sms_number_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_sms_phone_number: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/sms-numbers/{sms_number_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/sms-numbers/{sms_number_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_sms_phone_number")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_sms_phone_number", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_sms_phone_number",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: SMS Phone Numbers
@mcp.tool()
async def update_sms_phone_number_pause_status(
    sms_number_id: str = Field(..., description="The unique identifier of the SMS phone number to update."),
    paused: bool = Field(..., description="Set to true to pause the SMS phone number (disable message sending), or false to resume it."),
) -> dict[str, Any]:
    """Update the pause status of an SMS phone number. Use this to temporarily disable or re-enable an SMS phone number for sending messages."""

    # Construct request model with validation
    try:
        _request = _models.UpdateSingleSmsPhoneNumberRequest(
            path=_models.UpdateSingleSmsPhoneNumberRequestPath(sms_number_id=sms_number_id),
            body=_models.UpdateSingleSmsPhoneNumberRequestBody(paused=paused)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_sms_phone_number_pause_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/sms-numbers/{sms_number_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/sms-numbers/{sms_number_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_sms_phone_number_pause_status")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_sms_phone_number_pause_status", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_sms_phone_number_pause_status",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: SMS Phone Numbers
@mcp.tool()
async def delete_sms_number(sms_number_id: str = Field(..., description="The unique identifier of the SMS phone number to delete.")) -> dict[str, Any]:
    """Permanently delete an SMS phone number from your account. This action cannot be undone and will remove the number from all associated configurations."""

    # Construct request model with validation
    try:
        _request = _models.DeleteAnSmsPhoneNumberRequest(
            path=_models.DeleteAnSmsPhoneNumberRequestPath(sms_number_id=sms_number_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_sms_number: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/sms-numbers/{sms_number_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/sms-numbers/{sms_number_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_sms_number")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_sms_number", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_sms_number",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: SMS Messages
@mcp.tool()
async def list_sms_messages() -> dict[str, Any]:
    """Retrieve a list of all SMS messages. Use this operation to fetch SMS message records from the system."""

    # Extract parameters for API call
    _http_path = "/sms-messages"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_sms_messages")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_sms_messages", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_sms_messages",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: SMS Messages
@mcp.tool()
async def get_sms_message(sms_message_id: str = Field(..., description="The unique identifier of the SMS message to retrieve.")) -> dict[str, Any]:
    """Retrieve a specific SMS message by its unique identifier. Returns the full message details including content, sender, recipient, timestamp, and delivery status."""

    # Construct request model with validation
    try:
        _request = _models.GetAnSmsMessageRequest(
            path=_models.GetAnSmsMessageRequestPath(sms_message_id=sms_message_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_sms_message: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/sms-messages/{sms_message_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/sms-messages/{sms_message_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_sms_message")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_sms_message", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_sms_message",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: SMS Activity
@mcp.tool()
async def list_sms_activities() -> dict[str, Any]:
    """Retrieve a list of all SMS activities. Use this to view the history and status of SMS messages sent through the system."""

    # Extract parameters for API call
    _http_path = "/sms-activity"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_sms_activities")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_sms_activities", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_sms_activities",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: SMS Activity
@mcp.tool()
async def get_sms_message_activity(sms_message_id: str = Field(..., description="The unique identifier of the SMS message whose activity you want to retrieve.")) -> dict[str, Any]:
    """Retrieve the activity history and delivery status for a specific SMS message. This includes details about message processing, delivery attempts, and any related events."""

    # Construct request model with validation
    try:
        _request = _models.GetActivityOfSingleSmsMessageRequest(
            path=_models.GetActivityOfSingleSmsMessageRequestPath(sms_message_id=sms_message_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_sms_message_activity: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/sms-activity/{sms_message_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/sms-activity/{sms_message_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_sms_message_activity")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_sms_message_activity", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_sms_message_activity",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: SMS Recipients
@mcp.tool()
async def list_sms_recipients() -> dict[str, Any]:
    """Retrieve a list of all SMS recipients configured in the system. Use this to view and manage contacts eligible for SMS communications."""

    # Extract parameters for API call
    _http_path = "/sms-recipients"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_sms_recipients")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_sms_recipients", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_sms_recipients",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: SMS Recipients
@mcp.tool()
async def get_sms_recipient(sms_recipient_id: str = Field(..., description="The unique identifier of the SMS recipient to retrieve.")) -> dict[str, Any]:
    """Retrieve detailed information about a specific SMS recipient by their unique identifier."""

    # Construct request model with validation
    try:
        _request = _models.GetAnSmsRecipientRequest(
            path=_models.GetAnSmsRecipientRequestPath(sms_recipient_id=sms_recipient_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_sms_recipient: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/sms-recipients/{sms_recipient_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/sms-recipients/{sms_recipient_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_sms_recipient")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_sms_recipient", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_sms_recipient",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: SMS Recipients
@mcp.tool()
async def update_sms_recipient_status(
    sms_recipient_id: str = Field(..., description="The unique identifier of the SMS recipient whose status you want to update."),
    status: Literal["opt_out", "active"] = Field(..., description="The new subscription status for the recipient. Set to 'active' to enable SMS communications or 'opt_out' to disable them."),
) -> dict[str, Any]:
    """Update the subscription status of an SMS recipient. Use this to activate a recipient or mark them as opted out from SMS communications."""

    # Construct request model with validation
    try:
        _request = _models.UpdateSingleSmsRecipientRequest(
            path=_models.UpdateSingleSmsRecipientRequestPath(sms_recipient_id=sms_recipient_id),
            body=_models.UpdateSingleSmsRecipientRequestBody(status=status)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_sms_recipient_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/sms-recipients/{sms_recipient_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/sms-recipients/{sms_recipient_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_sms_recipient_status")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_sms_recipient_status", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_sms_recipient_status",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: SMS Webhooks
@mcp.tool()
async def list_sms_webhooks(sms_number_id: str = Field(..., description="The unique identifier of the SMS phone number for which you want to retrieve configured webhooks.")) -> dict[str, Any]:
    """Retrieve all SMS webhooks configured for a specific SMS phone number. This allows you to view all webhook endpoints that are currently set up to receive SMS events for the given number."""

    # Construct request model with validation
    try:
        _request = _models.GetListOfSmsWebhooksRequest(
            query=_models.GetListOfSmsWebhooksRequestQuery(sms_number_id=sms_number_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_sms_webhooks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/sms-webhooks"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_sms_webhooks")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_sms_webhooks", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_sms_webhooks",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: SMS Webhooks
@mcp.tool()
async def get_sms_webhook(sms_webhook_id: str = Field(..., description="The unique identifier of the SMS webhook to retrieve.")) -> dict[str, Any]:
    """Retrieve the configuration and details of a specific SMS webhook by its ID. Use this to inspect webhook settings, URL, event subscriptions, and other metadata."""

    # Construct request model with validation
    try:
        _request = _models.GetSingleSmsWebhookRequest(
            path=_models.GetSingleSmsWebhookRequestPath(sms_webhook_id=sms_webhook_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_sms_webhook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/sms-webhooks/{sms_webhook_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/sms-webhooks/{sms_webhook_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_sms_webhook")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_sms_webhook", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_sms_webhook",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: SMS Webhooks
@mcp.tool()
async def update_sms_webhook(
    sms_webhook_id: str = Field(..., description="The unique identifier of the SMS webhook to update."),
    enabled: bool = Field(..., description="Whether the SMS webhook should be active and receive events. Set to true to enable or false to disable."),
) -> dict[str, Any]:
    """Update the configuration of an SMS webhook by enabling or disabling it. This allows you to control whether the webhook is active without deleting it."""

    # Construct request model with validation
    try:
        _request = _models.UpdateSingleSmsWebhookRequest(
            path=_models.UpdateSingleSmsWebhookRequestPath(sms_webhook_id=sms_webhook_id),
            body=_models.UpdateSingleSmsWebhookRequestBody(enabled=enabled)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_sms_webhook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/sms-webhooks/{sms_webhook_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/sms-webhooks/{sms_webhook_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_sms_webhook")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_sms_webhook", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_sms_webhook",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: SMS Webhooks
@mcp.tool()
async def delete_sms_webhook(
    sms_webhook_id: str = Field(..., description="The unique identifier of the SMS webhook to delete."),
    enabled: bool = Field(..., description="A boolean flag indicating the desired state. Set to false to proceed with deletion."),
) -> dict[str, Any]:
    """Permanently delete an SMS webhook by its ID. Once deleted, the webhook will no longer receive SMS events."""

    # Construct request model with validation
    try:
        _request = _models.DeleteAnSmsWebhookRequest(
            path=_models.DeleteAnSmsWebhookRequestPath(sms_webhook_id=sms_webhook_id),
            body=_models.DeleteAnSmsWebhookRequestBody(enabled=enabled)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_sms_webhook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/sms-webhooks/{sms_webhook_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/sms-webhooks/{sms_webhook_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_sms_webhook")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_sms_webhook", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_sms_webhook",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: SMS Inbound Routing
@mcp.tool()
async def list_sms_inbound_routes() -> dict[str, Any]:
    """Retrieve all configured SMS inbound routes for your account. This returns the complete list of routes that handle incoming SMS messages."""

    # Extract parameters for API call
    _http_path = "/sms-inbounds"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_sms_inbound_routes")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_sms_inbound_routes", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_sms_inbound_routes",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: SMS Inbound Routing
@mcp.tool()
async def get_sms_inbound_route(sms_inbound_id: str = Field(..., description="The unique identifier of the SMS inbound route to retrieve.")) -> dict[str, Any]:
    """Retrieve the configuration and details of a specific SMS inbound route by its unique identifier."""

    # Construct request model with validation
    try:
        _request = _models.GetSingleSmsInboundRouteRequest(
            path=_models.GetSingleSmsInboundRouteRequestPath(sms_inbound_id=sms_inbound_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_sms_inbound_route: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/sms-inbounds/{sms_inbound_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/sms-inbounds/{sms_inbound_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_sms_inbound_route")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_sms_inbound_route", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_sms_inbound_route",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: SMS Inbound Routing
@mcp.tool()
async def update_sms_inbound_route(
    sms_inbound_id: str = Field(..., description="The unique identifier of the SMS inbound route to update."),
    sms_number_id: str = Field(..., description="The ID of the SMS phone number to associate with this inbound route."),
    name: str = Field(..., description="A descriptive name for this inbound route (e.g., 'Inbound')."),
    forward_url: str = Field(..., description="The webhook URL where incoming SMS messages will be forwarded. Must be a valid URI (e.g., https://yourapp.com/hook)."),
    enabled: bool = Field(..., description="Whether this inbound route is active and should process incoming messages."),
) -> dict[str, Any]:
    """Update an existing inbound SMS route configuration, including the associated phone number, display name, webhook destination, and activation status."""

    # Construct request model with validation
    try:
        _request = _models.UpdateSmsInboundRouteRequest(
            path=_models.UpdateSmsInboundRouteRequestPath(sms_inbound_id=sms_inbound_id),
            body=_models.UpdateSmsInboundRouteRequestBody(sms_number_id=sms_number_id, name=name, forward_url=forward_url, enabled=enabled)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_sms_inbound_route: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/sms-inbounds/{sms_inbound_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/sms-inbounds/{sms_inbound_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_sms_inbound_route")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_sms_inbound_route", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_sms_inbound_route",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: SMS Inbound Routing
@mcp.tool()
async def delete_sms_inbound_route(sms_inbound_id: str = Field(..., description="The unique identifier of the SMS inbound route to delete.")) -> dict[str, Any]:
    """Permanently delete an SMS inbound route by its ID. This action cannot be undone and will stop processing inbound SMS messages for this route."""

    # Construct request model with validation
    try:
        _request = _models.DeleteAnSmsInboundRouteRequest(
            path=_models.DeleteAnSmsInboundRouteRequestPath(sms_inbound_id=sms_inbound_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_sms_inbound_route: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/sms-inbounds/{sms_inbound_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/sms-inbounds/{sms_inbound_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_sms_inbound_route")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_sms_inbound_route", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_sms_inbound_route",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: SMTP Users
@mcp.tool()
async def list_smtp_users(domain_id: str = Field(..., description="The unique identifier of the domain for which to retrieve SMTP users.")) -> dict[str, Any]:
    """Retrieve all SMTP users configured for a specific domain. Returns a list of SMTP user accounts associated with the domain."""

    # Construct request model with validation
    try:
        _request = _models.GetListOfSmtpUsersRequest(
            path=_models.GetListOfSmtpUsersRequestPath(domain_id=domain_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_smtp_users: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/domains/{domain_id}/smtp-users", _request.path.model_dump(by_alias=True)) if _request.path else "/domains/{domain_id}/smtp-users"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_smtp_users")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_smtp_users", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_smtp_users",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: SMTP Users
@mcp.tool()
async def get_smtp_user(
    domain_id: str = Field(..., description="The unique identifier of the domain that contains the SMTP user."),
    smtp_user_id: str = Field(..., description="The unique identifier of the SMTP user to retrieve."),
) -> dict[str, Any]:
    """Retrieve detailed information about a specific SMTP user within a domain. Use this to fetch configuration, credentials, and status for a single SMTP user account."""

    # Construct request model with validation
    try:
        _request = _models.GetSingleSmtpUserRequest(
            path=_models.GetSingleSmtpUserRequestPath(domain_id=domain_id, smtp_user_id=smtp_user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_smtp_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/domains/{domain_id}/smtp-users/{smtp_user_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/domains/{domain_id}/smtp-users/{smtp_user_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_smtp_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_smtp_user", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_smtp_user",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: SMTP Users
@mcp.tool()
async def update_smtp_user(
    domain_id: str = Field(..., description="The unique identifier of the domain containing the SMTP user."),
    smtp_user_id: str = Field(..., description="The unique identifier of the SMTP user to be updated."),
    name: str = Field(..., description="The display name for the SMTP user (e.g., 'New Name')."),
    enabled: bool = Field(..., description="Whether the SMTP user account is active and can be used for authentication."),
) -> dict[str, Any]:
    """Update an SMTP user's configuration within a domain, including their display name and enabled status."""

    # Construct request model with validation
    try:
        _request = _models.UpdateSmtpUserRequest(
            path=_models.UpdateSmtpUserRequestPath(domain_id=domain_id, smtp_user_id=smtp_user_id),
            body=_models.UpdateSmtpUserRequestBody(name=name, enabled=enabled)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_smtp_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/domains/{domain_id}/smtp-users/{smtp_user_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/domains/{domain_id}/smtp-users/{smtp_user_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_smtp_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_smtp_user", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_smtp_user",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: SMTP Users
@mcp.tool()
async def delete_smtp_user(
    domain_id: str = Field(..., description="The unique identifier of the domain that contains the SMTP user to be deleted."),
    smtp_user_id: str = Field(..., description="The unique identifier of the SMTP user to be deleted from the domain."),
) -> dict[str, Any]:
    """Permanently delete an SMTP user from a domain. This action cannot be undone and will immediately revoke the user's ability to send emails through this domain."""

    # Construct request model with validation
    try:
        _request = _models.DeleteSmtpUserRequest(
            path=_models.DeleteSmtpUserRequestPath(domain_id=domain_id, smtp_user_id=smtp_user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_smtp_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/domains/{domain_id}/smtp-users/{smtp_user_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/domains/{domain_id}/smtp-users/{smtp_user_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_smtp_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_smtp_user", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_smtp_user",
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
        print("  python mailer_send_server.py", file=sys.stderr)
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

    parser = argparse.ArgumentParser(description="MailerSend MCP Server")

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
    logger.info("Starting MailerSend MCP Server")
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

#!/usr/bin/env python3
"""
Google Sheets MCP Server

API Info:
- API License: Creative Commons Attribution 3.0 (http://creativecommons.org/licenses/by/3.0/)
- Contact: Google (https://google.com)
- Terms of Service: https://developers.google.com/terms/

Generated: 2026-04-09 17:24:32 UTC
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

BASE_URL = os.getenv("BASE_URL", "https://sheets.googleapis.com")
SERVER_NAME = "Google Sheets"
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
    'OAuth2',
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

mcp = FastMCP("Google Sheets", middleware=[_JsonCoercionMiddleware()])

# Tags: spreadsheets
@mcp.tool()
async def apply_spreadsheet_updates(
    spreadsheet_id: str = Field(..., alias="spreadsheetId", description="The unique identifier of the spreadsheet to update."),
    include_spreadsheet_in_response: bool | None = Field(None, alias="includeSpreadsheetInResponse", description="When true, includes the complete spreadsheet resource in the response after updates are applied."),
    requests: list[_models.Request] | None = Field(None, description="An ordered list of update requests to apply to the spreadsheet. Requests are processed sequentially in the order specified. If any request fails validation, no updates will be applied."),
    response_ranges: list[str] | None = Field(None, alias="responseRanges", description="Restricts which ranges are included in the response spreadsheet. Only meaningful when the spreadsheet is included in the response."),
) -> dict[str, Any]:
    """Applies one or more updates to a spreadsheet atomically. All requests are validated before being applied; if any request is invalid, the entire batch fails and no changes are made. Responses mirror the structure of requests, with replies provided only for updates that generate them."""

    # Construct request model with validation
    try:
        _request = _models.BatchUpdateRequest(
            path=_models.BatchUpdateRequestPath(spreadsheet_id=spreadsheet_id),
            body=_models.BatchUpdateRequestBody(include_spreadsheet_in_response=include_spreadsheet_in_response, requests=requests, response_ranges=response_ranges)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for apply_spreadsheet_updates: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v4/spreadsheets/{spreadsheetId}:batchUpdate", _request.path.model_dump(by_alias=True)) if _request.path else "/v4/spreadsheets/{spreadsheetId}:batchUpdate"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("apply_spreadsheet_updates")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("apply_spreadsheet_updates", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="apply_spreadsheet_updates",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: spreadsheets
@mcp.tool()
async def create_spreadsheet(
    data_sources: list[_models.DataSource] | None = Field(None, alias="dataSources", description="List of external data sources to connect with the spreadsheet, such as BigQuery or database connections."),
    developer_metadata: list[_models.DeveloperMetadata] | None = Field(None, alias="developerMetadata", description="Developer metadata key-value pairs to associate with the spreadsheet for custom tracking or integration purposes."),
    named_ranges: list[_models.NamedRange] | None = Field(None, alias="namedRanges", description="Named ranges to define in the spreadsheet, allowing cells or ranges to be referenced by custom names instead of cell coordinates."),
    auto_recalc: Literal["RECALCULATION_INTERVAL_UNSPECIFIED", "ON_CHANGE", "MINUTE", "HOUR"] | None = Field(None, alias="autoRecalc", description="Recalculation frequency for volatile functions. Options include: on change, every minute, or every hour. Defaults to unspecified behavior."),
    rgb_color: dict[str, Any] | None = Field(None, alias="rgbColor", description="RGB color object for styling. Note that the alpha (transparency) channel is not generally supported by the API."),
    theme_color: Literal["THEME_COLOR_TYPE_UNSPECIFIED", "TEXT", "BACKGROUND", "ACCENT1", "ACCENT2", "ACCENT3", "ACCENT4", "ACCENT5", "ACCENT6", "LINK"] | None = Field(None, alias="themeColor", description="Theme color selection from the spreadsheet's color palette, such as text, background, accent colors, or link color."),
    borders_bottom: dict[str, Any] | None = Field(None, alias="bordersBottom", description="Bottom border styling for cells in the default format."),
    padding_bottom: str | None = Field(None, alias="paddingBottom", description="Bottom padding in pixels for cells in the default format. Must be a 32-bit integer."),
    borders_left: dict[str, Any] | None = Field(None, alias="bordersLeft", description="Left border styling for cells in the default format."),
    padding_left: str | None = Field(None, alias="paddingLeft", description="Left padding in pixels for cells in the default format. Must be a 32-bit integer."),
    borders_right: dict[str, Any] | None = Field(None, alias="bordersRight", description="Right border styling for cells in the default format."),
    padding_right: str | None = Field(None, alias="paddingRight", description="Right padding in pixels for cells in the default format. Must be a 32-bit integer."),
    borders_top: dict[str, Any] | None = Field(None, alias="bordersTop", description="Top border styling for cells in the default format."),
    padding_top: str | None = Field(None, alias="paddingTop", description="Top padding in pixels for cells in the default format. Must be a 32-bit integer."),
    horizontal_alignment: Literal["HORIZONTAL_ALIGN_UNSPECIFIED", "LEFT", "CENTER", "RIGHT"] | None = Field(None, alias="horizontalAlignment", description="Horizontal alignment for cell values: left, center, or right alignment."),
    hyperlink_display_type: Literal["HYPERLINK_DISPLAY_TYPE_UNSPECIFIED", "LINKED", "PLAIN_TEXT"] | None = Field(None, alias="hyperlinkDisplayType", description="How hyperlinks should display in cells: as clickable links or as plain text."),
    pattern: str | None = Field(None, description="Number format pattern string (e.g., for dates, currency, decimals). If not specified, a default pattern based on spreadsheet locale will be used."),
    type_: Literal["NUMBER_FORMAT_TYPE_UNSPECIFIED", "TEXT", "NUMBER", "PERCENT", "CURRENCY", "DATE", "TIME", "DATE_TIME", "SCIENTIFIC"] | None = Field(None, alias="type", description="Number format type such as text, number, percent, currency, date, time, date-time, or scientific notation. Required when setting number formats."),
    text_direction: Literal["TEXT_DIRECTION_UNSPECIFIED", "LEFT_TO_RIGHT", "RIGHT_TO_LEFT"] | None = Field(None, alias="textDirection", description="Text direction for cell content: left-to-right or right-to-left for language support."),
    bold: bool | None = Field(None, description="Whether text in cells should be displayed in bold."),
    font_family: str | None = Field(None, alias="fontFamily", description="Font family name for text styling (e.g., Arial, Times New Roman)."),
    font_size: str | None = Field(None, alias="fontSize", description="Font size in points. Must be a 32-bit integer."),
    foreground_color_style: dict[str, Any] | None = Field(None, alias="foregroundColorStyle", description="Foreground color styling for text. Takes precedence over the foreground_color field if both are set."),
    italic: bool | None = Field(None, description="Whether text in cells should be displayed in italics."),
    link: dict[str, Any] | None = Field(None, description="Hyperlink destination URL for text. Setting this clears any existing cell-level links. Link color and underline formatting are applied automatically unless overridden."),
    strikethrough: bool | None = Field(None, description="Whether text in cells should have a strikethrough line."),
    underline: bool | None = Field(None, description="Whether text in cells should be underlined."),
    angle: str | None = Field(None, description="Text rotation angle in degrees, ranging from -90 to 90. Positive angles rotate counterclockwise (LTR) or clockwise (RTL), negative angles rotate the opposite direction."),
    vertical: bool | None = Field(None, description="If true, text reads vertically from top to bottom while individual characters maintain their standard orientation."),
    vertical_alignment: Literal["VERTICAL_ALIGN_UNSPECIFIED", "TOP", "MIDDLE", "BOTTOM"] | None = Field(None, alias="verticalAlignment", description="Vertical alignment for cell values: top, middle, or bottom alignment."),
    wrap_strategy: Literal["WRAP_STRATEGY_UNSPECIFIED", "OVERFLOW_CELL", "LEGACY_WRAP", "CLIP", "WRAP"] | None = Field(None, alias="wrapStrategy", description="Text wrapping strategy: overflow into adjacent cells, legacy wrap, clip excess text, or wrap to multiple lines."),
    import_functions_external_url_access_allowed: bool | None = Field(None, alias="importFunctionsExternalUrlAccessAllowed", description="Whether to allow external URL access for image and import functions. Read-only when true. May be overridden by admin URL allowlist settings."),
    convergence_threshold: float | None = Field(None, alias="convergenceThreshold", description="Convergence threshold for iterative calculations. When successive calculation results differ by less than this value, iteration stops. Must be a double-precision number."),
    max_iterations: str | None = Field(None, alias="maxIterations", description="Maximum number of calculation rounds to perform when iterative calculation is enabled. Must be a 32-bit integer."),
    locale: str | None = Field(None, description="Spreadsheet locale in ISO 639-1 format (e.g., 'en'), ISO 639-2 format (e.g., 'fil'), or combined language-country format (e.g., 'en_US'). Not all locales are supported for updates."),
    primary_font_family: str | None = Field(None, alias="primaryFontFamily", description="Primary font family name used as the default for the spreadsheet."),
    theme_colors: list[_models.ThemeColorPair] | None = Field(None, alias="themeColors", description="Complete set of theme color pairs for the spreadsheet. All theme color pairs must be provided together when updating."),
    time_zone: str | None = Field(None, alias="timeZone", description="Spreadsheet time zone in CLDR format (e.g., 'America/New_York'). Custom time zones like 'GMT-07:00' are supported if the standard zone isn't recognized."),
    title: str | None = Field(None, description="Title or name of the spreadsheet."),
    sheets: list[_models.Sheet] | None = Field(None, description="Array of sheet objects that define the individual sheets within the spreadsheet."),
) -> dict[str, Any]:
    """Creates a new spreadsheet with optional configuration for sheets, properties, formatting defaults, and external data sources. Returns the newly created spreadsheet object."""

    _padding_bottom = _parse_int(padding_bottom)
    _padding_left = _parse_int(padding_left)
    _padding_right = _parse_int(padding_right)
    _padding_top = _parse_int(padding_top)
    _font_size = _parse_int(font_size)
    _angle = _parse_int(angle)
    _max_iterations = _parse_int(max_iterations)

    # Construct request model with validation
    try:
        _request = _models.CreateRequest(
            body=_models.CreateRequestBody(data_sources=data_sources, developer_metadata=developer_metadata, named_ranges=named_ranges, sheets=sheets,
                properties=_models.CreateRequestBodyProperties(auto_recalc=auto_recalc, import_functions_external_url_access_allowed=import_functions_external_url_access_allowed, locale=locale, time_zone=time_zone, title=title,
                    default_format=_models.CreateRequestBodyPropertiesDefaultFormat(horizontal_alignment=horizontal_alignment, hyperlink_display_type=hyperlink_display_type, text_direction=text_direction, vertical_alignment=vertical_alignment, wrap_strategy=wrap_strategy,
                        background_color_style=_models.CreateRequestBodyPropertiesDefaultFormatBackgroundColorStyle(rgb_color=rgb_color, theme_color=theme_color) if any(v is not None for v in [rgb_color, theme_color]) else None,
                        borders=_models.CreateRequestBodyPropertiesDefaultFormatBorders(bottom=borders_bottom, left=borders_left, right=borders_right, top=borders_top) if any(v is not None for v in [borders_bottom, borders_left, borders_right, borders_top]) else None,
                        padding=_models.CreateRequestBodyPropertiesDefaultFormatPadding(bottom=_padding_bottom, left=_padding_left, right=_padding_right, top=_padding_top) if any(v is not None for v in [padding_bottom, padding_left, padding_right, padding_top]) else None,
                        number_format=_models.CreateRequestBodyPropertiesDefaultFormatNumberFormat(pattern=pattern, type_=type_) if any(v is not None for v in [pattern, type_]) else None,
                        text_format=_models.CreateRequestBodyPropertiesDefaultFormatTextFormat(bold=bold, font_family=font_family, font_size=_font_size, foreground_color_style=foreground_color_style, italic=italic, link=link, strikethrough=strikethrough, underline=underline) if any(v is not None for v in [bold, font_family, font_size, foreground_color_style, italic, link, strikethrough, underline]) else None,
                        text_rotation=_models.CreateRequestBodyPropertiesDefaultFormatTextRotation(angle=_angle, vertical=vertical) if any(v is not None for v in [angle, vertical]) else None) if any(v is not None for v in [rgb_color, theme_color, borders_bottom, padding_bottom, borders_left, padding_left, borders_right, padding_right, borders_top, padding_top, horizontal_alignment, hyperlink_display_type, pattern, type_, text_direction, bold, font_family, font_size, foreground_color_style, italic, link, strikethrough, underline, angle, vertical, vertical_alignment, wrap_strategy]) else None,
                    iterative_calculation_settings=_models.CreateRequestBodyPropertiesIterativeCalculationSettings(convergence_threshold=convergence_threshold, max_iterations=_max_iterations) if any(v is not None for v in [convergence_threshold, max_iterations]) else None,
                    spreadsheet_theme=_models.CreateRequestBodyPropertiesSpreadsheetTheme(primary_font_family=primary_font_family, theme_colors=theme_colors) if any(v is not None for v in [primary_font_family, theme_colors]) else None) if any(v is not None for v in [auto_recalc, rgb_color, theme_color, borders_bottom, padding_bottom, borders_left, padding_left, borders_right, padding_right, borders_top, padding_top, horizontal_alignment, hyperlink_display_type, pattern, type_, text_direction, bold, font_family, font_size, foreground_color_style, italic, link, strikethrough, underline, angle, vertical, vertical_alignment, wrap_strategy, import_functions_external_url_access_allowed, convergence_threshold, max_iterations, locale, primary_font_family, theme_colors, time_zone, title]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_spreadsheet: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v4/spreadsheets"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_spreadsheet")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_spreadsheet", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_spreadsheet",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: spreadsheets
@mcp.tool()
async def get_spreadsheet(
    spreadsheet_id: str = Field(..., alias="spreadsheetId", description="The unique identifier of the spreadsheet to retrieve. This ID is required to access the correct spreadsheet."),
    ranges: list[str] | None = Field(None, description="Optional cell ranges to retrieve from the spreadsheet, specified using A1 notation (e.g., A1, A1:D5, or Sheet2!A1:C4). Multiple ranges can be specified to retrieve data from different areas or sheets. When specified, only data intersecting these ranges is returned."),
) -> dict[str, Any]:
    """Retrieves a spreadsheet by its ID with optional support for specific cell ranges and grid data. By default, grid data is excluded; use field masks or the includeGridData parameter to include it."""

    # Construct request model with validation
    try:
        _request = _models.GetRequest(
            path=_models.GetRequestPath(spreadsheet_id=spreadsheet_id),
            query=_models.GetRequestQuery(ranges=ranges)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_spreadsheet: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v4/spreadsheets/{spreadsheetId}", _request.path.model_dump(by_alias=True)) if _request.path else "/v4/spreadsheets/{spreadsheetId}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_spreadsheet")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_spreadsheet", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_spreadsheet",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: spreadsheets
@mcp.tool()
async def retrieve_spreadsheet_by_data_filter(
    spreadsheet_id: str = Field(..., alias="spreadsheetId", description="The unique identifier of the spreadsheet to retrieve."),
    data_filters: list[_models.DataFilter] | None = Field(None, alias="dataFilters", description="One or more data filters that specify which ranges to return from the spreadsheet. When multiple filters are provided, the response includes data from all matching ranges. If omitted, only spreadsheet metadata is returned without grid data."),
) -> dict[str, Any]:
    """Retrieves a spreadsheet by ID with the ability to filter which data ranges are returned. Use data filters to selectively fetch specific portions of the spreadsheet, optionally including grid data."""

    # Construct request model with validation
    try:
        _request = _models.GetByDataFilterRequest(
            path=_models.GetByDataFilterRequestPath(spreadsheet_id=spreadsheet_id),
            body=_models.GetByDataFilterRequestBody(data_filters=data_filters)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for retrieve_spreadsheet_by_data_filter: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v4/spreadsheets/{spreadsheetId}:getByDataFilter", _request.path.model_dump(by_alias=True)) if _request.path else "/v4/spreadsheets/{spreadsheetId}:getByDataFilter"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("retrieve_spreadsheet_by_data_filter")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("retrieve_spreadsheet_by_data_filter", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="retrieve_spreadsheet_by_data_filter",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: spreadsheets
@mcp.tool()
async def get_developer_metadata(
    spreadsheet_id: str = Field(..., alias="spreadsheetId", description="The unique identifier of the spreadsheet containing the developer metadata you want to retrieve."),
    metadata_id: int = Field(..., alias="metadataId", description="The unique identifier of the developer metadata entry to retrieve. This is a numeric ID assigned when the metadata was created."),
) -> dict[str, Any]:
    """Retrieves a specific developer metadata entry from a spreadsheet by its unique metadata ID. Use this to access custom metadata properties attached to spreadsheet resources."""

    # Construct request model with validation
    try:
        _request = _models.DeveloperMetadataGetRequest(
            path=_models.DeveloperMetadataGetRequestPath(spreadsheet_id=spreadsheet_id, metadata_id=metadata_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_developer_metadata: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v4/spreadsheets/{spreadsheetId}/developerMetadata/{metadataId}", _request.path.model_dump(by_alias=True)) if _request.path else "/v4/spreadsheets/{spreadsheetId}/developerMetadata/{metadataId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_developer_metadata")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_developer_metadata", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_developer_metadata",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: spreadsheets
@mcp.tool()
async def search_developer_metadata(
    spreadsheet_id: str = Field(..., alias="spreadsheetId", description="The unique identifier of the spreadsheet to search for developer metadata."),
    data_filters: list[_models.DataFilter] | None = Field(None, alias="dataFilters", description="One or more data filters that define the search criteria. Metadata matching any of the specified filters will be included in the results. Filters can target specific metadata lookups or location regions within the spreadsheet."),
) -> dict[str, Any]:
    """Search for developer metadata entries in a spreadsheet that match specified criteria. Returns all metadata matching the provided data filters, which can target specific metadata lookups or location-based regions."""

    # Construct request model with validation
    try:
        _request = _models.DeveloperMetadataSearchRequest(
            path=_models.DeveloperMetadataSearchRequestPath(spreadsheet_id=spreadsheet_id),
            body=_models.DeveloperMetadataSearchRequestBody(data_filters=data_filters)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_developer_metadata: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v4/spreadsheets/{spreadsheetId}/developerMetadata:search", _request.path.model_dump(by_alias=True)) if _request.path else "/v4/spreadsheets/{spreadsheetId}/developerMetadata:search"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_developer_metadata")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_developer_metadata", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_developer_metadata",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: spreadsheets
@mcp.tool()
async def copy_sheet(
    spreadsheet_id: str = Field(..., alias="spreadsheetId", description="The unique identifier of the spreadsheet that contains the sheet you want to copy."),
    sheet_id: int = Field(..., alias="sheetId", description="The unique identifier of the sheet to copy. This must be a valid sheet ID within the source spreadsheet."),
    destination_spreadsheet_id: str | None = Field(None, alias="destinationSpreadsheetId", description="The unique identifier of the spreadsheet where the sheet should be copied to. If omitted, the sheet will be copied within the same spreadsheet."),
) -> dict[str, Any]:
    """Copies a sheet from one spreadsheet to another and returns the properties of the newly created sheet. If no destination spreadsheet is specified, the sheet is copied within the same spreadsheet."""

    # Construct request model with validation
    try:
        _request = _models.SheetsCopyToRequest(
            path=_models.SheetsCopyToRequestPath(spreadsheet_id=spreadsheet_id, sheet_id=sheet_id),
            body=_models.SheetsCopyToRequestBody(destination_spreadsheet_id=destination_spreadsheet_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for copy_sheet: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v4/spreadsheets/{spreadsheetId}/sheets/{sheetId}:copyTo", _request.path.model_dump(by_alias=True)) if _request.path else "/v4/spreadsheets/{spreadsheetId}/sheets/{sheetId}:copyTo"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("copy_sheet")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("copy_sheet", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="copy_sheet",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: spreadsheets
@mcp.tool()
async def append_sheet_values(
    spreadsheet_id: str = Field(..., alias="spreadsheetId", description="The unique identifier of the spreadsheet to update."),
    range_: str = Field(..., alias="range", description="The range in A1 notation where the operation should search for an existing data table. New values will be appended to the row immediately following the last row of the detected table."),
    include_values_in_response: bool | None = Field(None, alias="includeValuesInResponse", description="When enabled, the response will include the actual values that were appended to the spreadsheet. By default, the response omits the appended values."),
    insert_data_option: Literal["OVERWRITE", "INSERT_ROWS"] | None = Field(None, alias="insertDataOption", description="Specifies how new data should be inserted: OVERWRITE replaces existing data, while INSERT_ROWS creates new rows for the appended data."),
    value_input_option: Literal["INPUT_VALUE_OPTION_UNSPECIFIED", "RAW", "USER_ENTERED"] | None = Field(None, alias="valueInputOption", description="Specifies how the input data should be interpreted: RAW treats values as-is, while USER_ENTERED applies the same parsing as if entered through the Sheets UI (e.g., formulas, dates)."),
    major_dimension: Literal["DIMENSION_UNSPECIFIED", "ROWS", "COLUMNS"] | None = Field(None, alias="majorDimension", description="Specifies whether the input array is organized by rows or columns. Defaults to ROWS, where each inner array represents a single row. Use COLUMNS if each inner array represents a single column."),
    values: list[list[Any]] | None = Field(None, description="A two-dimensional array of values to append, where each inner array represents either a row or column depending on majorDimension. Supported types are boolean, string, and number. Null values are ignored; use empty strings to set cells to empty values."),
) -> dict[str, Any]:
    """Appends values to the next row of a detected data table in a spreadsheet. The operation automatically locates the table within the specified range and adds new rows starting from the first column of that table."""

    # Construct request model with validation
    try:
        _request = _models.ValuesAppendRequest(
            path=_models.ValuesAppendRequestPath(spreadsheet_id=spreadsheet_id, range_=range_),
            query=_models.ValuesAppendRequestQuery(include_values_in_response=include_values_in_response, insert_data_option=insert_data_option, value_input_option=value_input_option),
            body=_models.ValuesAppendRequestBody(major_dimension=major_dimension, values=values)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for append_sheet_values: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v4/spreadsheets/{spreadsheetId}/values/{range}:append", _request.path.model_dump(by_alias=True)) if _request.path else "/v4/spreadsheets/{spreadsheetId}/values/{range}:append"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("append_sheet_values")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("append_sheet_values", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="append_sheet_values",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: spreadsheets
@mcp.tool()
async def clear_spreadsheet_values(
    spreadsheet_id: str = Field(..., alias="spreadsheetId", description="The unique identifier of the spreadsheet to update. This ID can be found in the spreadsheet URL."),
    ranges: list[str] | None = Field(None, description="One or more cell ranges to clear, specified using A1 notation (e.g., Sheet1!A1:B2) or R1C1 notation. If omitted, no ranges will be cleared. Order of ranges does not affect the operation."),
) -> dict[str, Any]:
    """Clears all values from one or more specified ranges in a spreadsheet while preserving cell formatting, data validation, and other properties. Useful for resetting data while maintaining spreadsheet structure."""

    # Construct request model with validation
    try:
        _request = _models.ValuesBatchClearRequest(
            path=_models.ValuesBatchClearRequestPath(spreadsheet_id=spreadsheet_id),
            body=_models.ValuesBatchClearRequestBody(ranges=ranges)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for clear_spreadsheet_values: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v4/spreadsheets/{spreadsheetId}/values:batchClear", _request.path.model_dump(by_alias=True)) if _request.path else "/v4/spreadsheets/{spreadsheetId}/values:batchClear"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("clear_spreadsheet_values")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("clear_spreadsheet_values", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="clear_spreadsheet_values",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: spreadsheets
@mcp.tool()
async def clear_spreadsheet_values_by_filter(
    spreadsheet_id: str = Field(..., alias="spreadsheetId", description="The unique identifier of the spreadsheet to update. This ID is typically found in the spreadsheet's URL."),
    data_filters: list[_models.DataFilter] | None = Field(None, alias="dataFilters", description="One or more data filters that define which ranges to clear. Each filter is evaluated independently, and all ranges matching any filter will have their values cleared. If not specified, no ranges will be cleared."),
) -> dict[str, Any]:
    """Clears cell values from a spreadsheet based on one or more data filters, while preserving all formatting, validation rules, and other cell properties. Use this to selectively remove data from ranges matching your specified filter criteria."""

    # Construct request model with validation
    try:
        _request = _models.ValuesBatchClearByDataFilterRequest(
            path=_models.ValuesBatchClearByDataFilterRequestPath(spreadsheet_id=spreadsheet_id),
            body=_models.ValuesBatchClearByDataFilterRequestBody(data_filters=data_filters)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for clear_spreadsheet_values_by_filter: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v4/spreadsheets/{spreadsheetId}/values:batchClearByDataFilter", _request.path.model_dump(by_alias=True)) if _request.path else "/v4/spreadsheets/{spreadsheetId}/values:batchClearByDataFilter"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("clear_spreadsheet_values_by_filter")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("clear_spreadsheet_values_by_filter", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="clear_spreadsheet_values_by_filter",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: spreadsheets
@mcp.tool()
async def get_spreadsheet_values_batch(
    spreadsheet_id: str = Field(..., alias="spreadsheetId", description="The unique identifier of the spreadsheet to retrieve data from."),
    date_time_render_option: Literal["SERIAL_NUMBER", "FORMATTED_STRING"] | None = Field(None, alias="dateTimeRenderOption", description="Controls how dates, times, and durations are represented in the output. Choose between serial number format (numeric representation) or formatted string. This setting is ignored if values are returned in formatted value mode. Defaults to serial number format."),
    major_dimension: Literal["DIMENSION_UNSPECIFIED", "ROWS", "COLUMNS"] | None = Field(None, alias="majorDimension", description="Determines the orientation of returned data. Use ROWS to return data organized by rows (each inner array is a row), COLUMNS to return data organized by columns (each inner array is a column), or DIMENSION_UNSPECIFIED for default behavior. Defaults to ROWS."),
    ranges: list[str] | None = Field(None, description="The cell ranges to retrieve, specified in A1 notation or R1C1 notation. Provide as an array of range strings (e.g., ['A1:B10', 'D5:E20']). If omitted, the entire sheet is retrieved."),
    value_render_option: Literal["FORMATTED_VALUE", "UNFORMATTED_VALUE", "FORMULA"] | None = Field(None, alias="valueRenderOption", description="Controls how cell values are represented in the output. Choose FORMATTED_VALUE to return values as displayed in the spreadsheet, UNFORMATTED_VALUE for raw values, or FORMULA to return formulas as text. Defaults to formatted value mode."),
) -> dict[str, Any]:
    """Retrieves one or more ranges of values from a spreadsheet. Specify the spreadsheet ID and one or more ranges to fetch, with options to control how values and dates are formatted in the response."""

    # Construct request model with validation
    try:
        _request = _models.ValuesBatchGetRequest(
            path=_models.ValuesBatchGetRequestPath(spreadsheet_id=spreadsheet_id),
            query=_models.ValuesBatchGetRequestQuery(date_time_render_option=date_time_render_option, major_dimension=major_dimension, ranges=ranges, value_render_option=value_render_option)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_spreadsheet_values_batch: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v4/spreadsheets/{spreadsheetId}/values:batchGet", _request.path.model_dump(by_alias=True)) if _request.path else "/v4/spreadsheets/{spreadsheetId}/values:batchGet"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_spreadsheet_values_batch")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_spreadsheet_values_batch", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_spreadsheet_values_batch",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: spreadsheets
@mcp.tool()
async def get_spreadsheet_values_by_filter(
    spreadsheet_id: str = Field(..., alias="spreadsheetId", description="The unique identifier of the spreadsheet to retrieve data from."),
    data_filters: list[_models.DataFilter] | None = Field(None, alias="dataFilters", description="One or more data filters that define which ranges to retrieve. Any ranges matching at least one filter will be included in the response."),
    date_time_render_option: Literal["SERIAL_NUMBER", "FORMATTED_STRING"] | None = Field(None, alias="dateTimeRenderOption", description="Controls how dates, times, and durations are formatted in the output. Choose SERIAL_NUMBER for numeric representation or FORMATTED_STRING for human-readable text. This setting is ignored when valueRenderOption is set to FORMATTED_VALUE. Defaults to SERIAL_NUMBER."),
    major_dimension: Literal["DIMENSION_UNSPECIFIED", "ROWS", "COLUMNS"] | None = Field(None, alias="majorDimension", description="Specifies whether results should be organized by rows or columns. ROWS returns data as nested arrays where each inner array is a row; COLUMNS returns data where each inner array is a column. Defaults to ROWS."),
    value_render_option: Literal["FORMATTED_VALUE", "UNFORMATTED_VALUE", "FORMULA"] | None = Field(None, alias="valueRenderOption", description="Controls how cell values are represented in the output. FORMATTED_VALUE shows values as displayed in the spreadsheet, UNFORMATTED_VALUE shows raw values, and FORMULA shows the actual formulas. Defaults to FORMATTED_VALUE."),
) -> dict[str, Any]:
    """Retrieves one or more ranges of values from a spreadsheet that match specified data filters. Multiple ranges matching any of the provided filters are returned in a single response."""

    # Construct request model with validation
    try:
        _request = _models.ValuesBatchGetByDataFilterRequest(
            path=_models.ValuesBatchGetByDataFilterRequestPath(spreadsheet_id=spreadsheet_id),
            body=_models.ValuesBatchGetByDataFilterRequestBody(data_filters=data_filters, date_time_render_option=date_time_render_option, major_dimension=major_dimension, value_render_option=value_render_option)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_spreadsheet_values_by_filter: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v4/spreadsheets/{spreadsheetId}/values:batchGetByDataFilter", _request.path.model_dump(by_alias=True)) if _request.path else "/v4/spreadsheets/{spreadsheetId}/values:batchGetByDataFilter"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_spreadsheet_values_by_filter")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_spreadsheet_values_by_filter", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_spreadsheet_values_by_filter",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: spreadsheets
@mcp.tool()
async def update_sheet_values_batch(
    spreadsheet_id: str = Field(..., alias="spreadsheetId", description="The unique identifier of the spreadsheet to update."),
    data: list[_models.ValueRange] | None = Field(None, description="An array of value ranges to update, where each range specifies the target cells and the values to write. Order matters as ranges are processed sequentially."),
    include_values_in_response: bool | None = Field(None, alias="includeValuesInResponse", description="When enabled, the response includes the actual values written to the cells, including all values in the requested range (excluding trailing empty rows and columns). Disabled by default."),
    value_input_option: Literal["INPUT_VALUE_OPTION_UNSPECIFIED", "RAW", "USER_ENTERED"] | None = Field(None, alias="valueInputOption", description="Specifies how the input data should be interpreted: RAW treats values as-is without formula parsing, USER_ENTERED parses formulas and formats like a user entering data manually, or UNSPECIFIED uses the default behavior."),
) -> dict[str, Any]:
    """Updates multiple ranges of cells in a spreadsheet with new values. Specify which ranges to update, how to interpret the input data, and optionally request the updated values in the response."""

    # Construct request model with validation
    try:
        _request = _models.ValuesBatchUpdateRequest(
            path=_models.ValuesBatchUpdateRequestPath(spreadsheet_id=spreadsheet_id),
            body=_models.ValuesBatchUpdateRequestBody(data=data, include_values_in_response=include_values_in_response, value_input_option=value_input_option)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_sheet_values_batch: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v4/spreadsheets/{spreadsheetId}/values:batchUpdate", _request.path.model_dump(by_alias=True)) if _request.path else "/v4/spreadsheets/{spreadsheetId}/values:batchUpdate"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_sheet_values_batch")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_sheet_values_batch", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_sheet_values_batch",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: spreadsheets
@mcp.tool()
async def update_spreadsheet_values_by_filter(
    spreadsheet_id: str = Field(..., alias="spreadsheetId", description="The unique identifier of the spreadsheet to update."),
    data: list[_models.DataFilterValueRange] | None = Field(None, description="Array of data filter value ranges specifying which cells to update and what values to apply. When multiple ranges match a filter, the same values are applied to all matched ranges."),
    include_values_in_response: bool | None = Field(None, alias="includeValuesInResponse", description="If true, the response will include the actual values that were written to the cells. By default, responses omit updated values. When enabled, the response includes all values in the requested range, excluding trailing empty rows and columns."),
    value_input_option: Literal["INPUT_VALUE_OPTION_UNSPECIFIED", "RAW", "USER_ENTERED"] | None = Field(None, alias="valueInputOption", description="Specifies how the input data should be interpreted: RAW treats values as-is without parsing, USER_ENTERED applies the same parsing as if entered through the Sheets UI (formulas, dates, etc.), or INPUT_VALUE_OPTION_UNSPECIFIED uses the default behavior."),
) -> dict[str, Any]:
    """Updates cell values in one or more ranges of a spreadsheet using data filters to target specific cells. Allows you to set values across multiple matched ranges simultaneously and optionally retrieve the updated values in the response."""

    # Construct request model with validation
    try:
        _request = _models.ValuesBatchUpdateByDataFilterRequest(
            path=_models.ValuesBatchUpdateByDataFilterRequestPath(spreadsheet_id=spreadsheet_id),
            body=_models.ValuesBatchUpdateByDataFilterRequestBody(data=data, include_values_in_response=include_values_in_response, value_input_option=value_input_option)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_spreadsheet_values_by_filter: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v4/spreadsheets/{spreadsheetId}/values:batchUpdateByDataFilter", _request.path.model_dump(by_alias=True)) if _request.path else "/v4/spreadsheets/{spreadsheetId}/values:batchUpdateByDataFilter"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_spreadsheet_values_by_filter")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_spreadsheet_values_by_filter", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_spreadsheet_values_by_filter",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: spreadsheets
@mcp.tool()
async def clear_spreadsheet_values_range(
    spreadsheet_id: str = Field(..., alias="spreadsheetId", description="The unique identifier of the spreadsheet to update. This ID is typically found in the spreadsheet's URL."),
    range_: str = Field(..., alias="range", description="The cells to clear, specified using A1 notation (e.g., Sheet1!A1:B10) or R1C1 notation. Supports single cells, ranges, and multiple ranges."),
) -> dict[str, Any]:
    """Clears all values from specified cells in a spreadsheet while preserving formatting, data validation, and other cell properties. Specify the spreadsheet and target range using A1 or R1C1 notation."""

    # Construct request model with validation
    try:
        _request = _models.ValuesClearRequest(
            path=_models.ValuesClearRequestPath(spreadsheet_id=spreadsheet_id, range_=range_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for clear_spreadsheet_values_range: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v4/spreadsheets/{spreadsheetId}/values/{range}:clear", _request.path.model_dump(by_alias=True)) if _request.path else "/v4/spreadsheets/{spreadsheetId}/values/{range}:clear"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("clear_spreadsheet_values_range")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("clear_spreadsheet_values_range", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="clear_spreadsheet_values_range",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: spreadsheets
@mcp.tool()
async def read_spreadsheet_range(
    spreadsheet_id: str = Field(..., alias="spreadsheetId", description="The unique identifier of the spreadsheet to read from."),
    range_: str = Field(..., alias="range", description="The cell range to retrieve, specified using A1 notation (e.g., Sheet1!A1:B10) or R1C1 notation."),
    date_time_render_option: Literal["SERIAL_NUMBER", "FORMATTED_STRING"] | None = Field(None, alias="dateTimeRenderOption", description="Controls how dates, times, and durations are formatted in the response. Choose SERIAL_NUMBER for numeric representation or FORMATTED_STRING for human-readable text. Ignored when valueRenderOption is set to FORMATTED_VALUE. Defaults to SERIAL_NUMBER."),
    major_dimension: Literal["DIMENSION_UNSPECIFIED", "ROWS", "COLUMNS"] | None = Field(None, alias="majorDimension", description="Determines the structure of the returned data. ROWS returns data organized by rows (default behavior), COLUMNS returns data organized by columns. This affects how nested arrays are structured in the response."),
    value_render_option: Literal["FORMATTED_VALUE", "UNFORMATTED_VALUE", "FORMULA"] | None = Field(None, alias="valueRenderOption", description="Specifies how cell values should be represented. FORMATTED_VALUE returns values as displayed in the spreadsheet, UNFORMATTED_VALUE returns raw values, and FORMULA returns the actual formulas. Defaults to FORMATTED_VALUE."),
) -> dict[str, Any]:
    """Retrieves cell values from a specified range in a spreadsheet. Supports flexible formatting options for dates, times, and formulas, with configurable output structure."""

    # Construct request model with validation
    try:
        _request = _models.ValuesGetRequest(
            path=_models.ValuesGetRequestPath(spreadsheet_id=spreadsheet_id, range_=range_),
            query=_models.ValuesGetRequestQuery(date_time_render_option=date_time_render_option, major_dimension=major_dimension, value_render_option=value_render_option)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for read_spreadsheet_range: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v4/spreadsheets/{spreadsheetId}/values/{range}", _request.path.model_dump(by_alias=True)) if _request.path else "/v4/spreadsheets/{spreadsheetId}/values/{range}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("read_spreadsheet_range")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("read_spreadsheet_range", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="read_spreadsheet_range",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: spreadsheets
@mcp.tool()
async def update_sheet_values(
    spreadsheet_id: str = Field(..., alias="spreadsheetId", description="The unique identifier of the spreadsheet to update."),
    range_: str = Field(..., alias="range", description="The target range in A1 notation (e.g., 'Sheet1!A1:B10') where values will be written."),
    include_values_in_response: bool | None = Field(None, alias="includeValuesInResponse", description="When enabled, the response includes the actual values written to the cells. By default, responses omit updated values."),
    value_input_option: Literal["INPUT_VALUE_OPTION_UNSPECIFIED", "RAW", "USER_ENTERED"] | None = Field(None, alias="valueInputOption", description="Specifies how input data should be interpreted: RAW treats values as-is, USER_ENTERED evaluates formulas and formats. Defaults to RAW if unspecified."),
    major_dimension: Literal["DIMENSION_UNSPECIFIED", "ROWS", "COLUMNS"] | None = Field(None, alias="majorDimension", description="Determines how the values array is organized: ROWS means each inner array represents a row, COLUMNS means each inner array represents a column. Defaults to ROWS if unspecified."),
    values: list[list[Any]] | None = Field(None, description="A 2D array of values to write, where each inner array represents either a row or column depending on majorDimension. Supported types are boolean, string, and number; null values are ignored, and empty strings clear cells."),
) -> dict[str, Any]:
    """Updates cell values in a spreadsheet within a specified range using A1 notation. Specify how input data should be interpreted (raw or user-entered formulas) and optionally retrieve the updated values in the response."""

    # Construct request model with validation
    try:
        _request = _models.ValuesUpdateRequest(
            path=_models.ValuesUpdateRequestPath(spreadsheet_id=spreadsheet_id, range_=range_),
            query=_models.ValuesUpdateRequestQuery(include_values_in_response=include_values_in_response, value_input_option=value_input_option),
            body=_models.ValuesUpdateRequestBody(major_dimension=major_dimension, values=values)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_sheet_values: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v4/spreadsheets/{spreadsheetId}/values/{range}", _request.path.model_dump(by_alias=True)) if _request.path else "/v4/spreadsheets/{spreadsheetId}/values/{range}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_sheet_values")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_sheet_values", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_sheet_values",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
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
        print("  python google_sheets_api_server.py", file=sys.stderr)
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

    parser = argparse.ArgumentParser(description="Google Sheets MCP Server")

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
    logger.info("Starting Google Sheets MCP Server")
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

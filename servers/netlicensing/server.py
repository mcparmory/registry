#!/usr/bin/env python3
"""
Labs64 NetLicensing RESTful API Test Center MCP Server

API Info:
- Terms of Service: https://www.labs64.com/legal/terms-of-service/netlicensing

Generated: 2026-04-09 17:28:31 UTC
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

BASE_URL = os.getenv("BASE_URL", "https://go.netlicensing.io/core/v2/rest")
SERVER_NAME = "Labs64 NetLicensing RESTful API Test Center"
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
    'basicAuth',
]

# Initialize authentication handlers at server startup
_auth_handlers: dict[str, Any] = {}
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

mcp = FastMCP("Labs64 NetLicensing RESTful API Test Center", middleware=[_JsonCoercionMiddleware()])

# Tags: Product
@mcp.tool()
async def list_products() -> dict[str, Any]:
    """Retrieve a complete list of all configured products available for the current vendor. Use this to discover and enumerate products in your vendor account."""

    # Extract parameters for API call
    _http_path = "/product"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_products")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_products", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_products",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Product
@mcp.tool()
async def create_product(
    active: bool = Field(..., description="Activation status of the product. When set to false, the product is disabled and prevents new licensee registrations and license issuance to existing licensees."),
    name: str = Field(..., description="The product name, which together with the version uniquely identifies the product for end customers."),
    version: str = Field(..., description="The product version, which together with the name uniquely identifies the product for end customers."),
    licensee_auto_create: bool | None = Field(None, alias="licenseeAutoCreate", description="When enabled, non-existing licensees are automatically created upon their first license validation attempt."),
    description: str | None = Field(None, description="A descriptive text providing additional information about the product."),
    licensing_info: str | None = Field(None, alias="licensingInfo", description="Licensing-related information or terms associated with the product."),
    vat_mode: Literal["GROSS", "NET"] | None = Field(None, alias="vatMode", description="Tax calculation mode for the product. Choose GROSS for prices including tax or NET for prices excluding tax."),
) -> dict[str, Any]:
    """Creates a new product with licensing configuration. The product is identified by its name and version combination and can be immediately activated or disabled for new licensee registrations."""

    # Construct request model with validation
    try:
        _request = _models.CreateProductRequest(
            body=_models.CreateProductRequestBody(active=active, name=name, version=version, licensee_auto_create=licensee_auto_create, description=description, licensing_info=licensing_info, vat_mode=vat_mode)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_product: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/product"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_product")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_product", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_product",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/x-www-form-urlencoded",
        headers=_http_headers,
    )

    return _response_data

# Tags: Product
@mcp.tool()
async def get_product(product_number: str = Field(..., alias="productNumber", description="The unique identifier for the product. This value must exactly match the product number in the system.")) -> dict[str, Any]:
    """Retrieve a specific product by its unique product number. Use this operation to fetch detailed information about a single product."""

    # Construct request model with validation
    try:
        _request = _models.ProductNumberRequest(
            path=_models.ProductNumberRequestPath(product_number=product_number)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_product: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/product/{productNumber}", _request.path.model_dump(by_alias=True)) if _request.path else "/product/{productNumber}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_product")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_product", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_product",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Product
@mcp.tool()
async def update_product(
    product_number: str = Field(..., alias="productNumber", description="The unique identifier for the product to update."),
    active: bool | None = Field(None, description="Enable or disable the product. When disabled, new licensees cannot be registered and existing licensees cannot obtain new licenses."),
    name: str | None = Field(None, description="The product name, typically displayed to end customers alongside the version."),
    version: str | None = Field(None, description="The product version, used alongside the name to identify the product to end customers."),
    licensee_auto_create: bool | None = Field(None, alias="licenseeAutoCreate", description="When enabled, licensees that do not exist will be automatically created during their first license validation attempt."),
    description: str | None = Field(None, description="A description of the product for internal or customer-facing documentation."),
    licensing_info: str | None = Field(None, alias="licensingInfo", description="Licensing terms and conditions information associated with the product."),
    vat_mode: Literal["GROSS", "NET"] | None = Field(None, alias="vatMode", description="The VAT calculation mode for the product: GROSS (price includes VAT) or NET (price excludes VAT)."),
) -> dict[str, Any]:
    """Update product properties such as name, version, licensing settings, and VAT configuration. Returns the updated product with all applied changes."""

    # Construct request model with validation
    try:
        _request = _models.UpdateProductRequest(
            path=_models.UpdateProductRequestPath(product_number=product_number),
            body=_models.UpdateProductRequestBody(active=active, name=name, version=version, licensee_auto_create=licensee_auto_create, description=description, licensing_info=licensing_info, vat_mode=vat_mode)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_product: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/product/{productNumber}", _request.path.model_dump(by_alias=True)) if _request.path else "/product/{productNumber}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_product")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_product", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_product",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/x-www-form-urlencoded",
        headers=_http_headers,
    )

    return _response_data

# Tags: Product
@mcp.tool()
async def delete_product(
    product_number: str = Field(..., alias="productNumber", description="The unique identifier for the product to delete."),
    force_cascade: bool | None = Field(None, alias="forceCascade", description="When enabled, forces deletion of the product and all its dependent objects. Use with caution as this operation cannot be undone."),
) -> dict[str, Any]:
    """Permanently delete a product by its unique product number. Optionally cascade the deletion to remove all dependent objects."""

    # Construct request model with validation
    try:
        _request = _models.DeleteProductRequest(
            path=_models.DeleteProductRequestPath(product_number=product_number),
            query=_models.DeleteProductRequestQuery(force_cascade=force_cascade)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_product: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/product/{productNumber}", _request.path.model_dump(by_alias=True)) if _request.path else "/product/{productNumber}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_product")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_product", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_product",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Product Module
@mcp.tool()
async def list_product_modules() -> dict[str, Any]:
    """Retrieve a complete list of all Product Modules available for the current Vendor. This operation returns all modules without filtering or pagination."""

    # Extract parameters for API call
    _http_path = "/productmodule"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_product_modules")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_product_modules", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_product_modules",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Product Module
@mcp.tool()
async def create_product_module(
    product_number: str = Field(..., alias="productNumber", description="Unique identifier for the Product Module within the Vendor's Product catalog. Can be assigned by the Vendor or auto-generated by NetLicensing. Becomes read-only once the first Licensee is created for this Product Module."),
    active: bool = Field(..., description="Activation status of the Product Module. When set to false, the module is disabled and Licensees cannot obtain new Licenses for it."),
    name: str = Field(..., description="Display name for the Product Module shown to end customers in the NetLicensing Shop."),
    licensing_model: str = Field(..., alias="licensingModel", description="The licensing model that governs how this Product Module's licenses are configured and validated. The selected model determines which License Templates can be used and validation behavior."),
    max_checkout_validity: str | None = Field(None, alias="maxCheckoutValidity", description="Maximum number of days a License can remain checked out offline. Required when using the Floating licensing model."),
    yellow_threshold: str | None = Field(None, alias="yellowThreshold", description="Remaining time volume threshold (in days) that triggers yellow status alerts. Required when using the Rental licensing model."),
    red_threshold: str | None = Field(None, alias="redThreshold", description="Remaining time volume threshold (in days) that triggers red status alerts. Required when using the Rental licensing model."),
    node_secret_mode: list[Literal["PREDEFINED", "CLIENT"]] | None = Field(None, alias="nodeSecretMode", description="Secret Mode configuration for node-locked licensing. Required when using the Node-Locked licensing model. Specify as an array of mode values."),
    license_template: list[Literal["TIMEVOLUME", "FEATURE"]] | None = Field(None, alias="licenseTemplate", description="License Template configuration defining license types and rules. Required when using the Try & Buy licensing model. Specify as an array of template objects."),
) -> dict[str, Any]:
    """Creates a new Product Module within a Product, establishing the licensing model and configuration for how licenses are managed and validated for end customers."""

    _max_checkout_validity = _parse_int(max_checkout_validity)
    _yellow_threshold = _parse_int(yellow_threshold)
    _red_threshold = _parse_int(red_threshold)

    # Construct request model with validation
    try:
        _request = _models.CreateProductModuleRequest(
            body=_models.CreateProductModuleRequestBody(product_number=product_number, active=active, name=name, licensing_model=licensing_model, max_checkout_validity=_max_checkout_validity, yellow_threshold=_yellow_threshold, red_threshold=_red_threshold, node_secret_mode=node_secret_mode, license_template=license_template)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_product_module: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/productmodule"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_product_module")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_product_module", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_product_module",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/x-www-form-urlencoded",
        headers=_http_headers,
    )

    return _response_data

# Tags: Product Module
@mcp.tool()
async def get_product_module(product_module_number: str = Field(..., alias="productModuleNumber", description="The unique identifier for the Product Module, assigned by the Vendor or auto-generated by NetLicensing. This value becomes read-only once the first Licensee is created for the Product.")) -> dict[str, Any]:
    """Retrieve a specific Product Module by its unique identifier. Returns the complete Product Module details for the given productModuleNumber."""

    # Construct request model with validation
    try:
        _request = _models.GetProductModuleRequest(
            path=_models.GetProductModuleRequestPath(product_module_number=product_module_number)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_product_module: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/productmodule/{productModuleNumber}", _request.path.model_dump(by_alias=True)) if _request.path else "/productmodule/{productModuleNumber}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_product_module")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_product_module", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_product_module",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Product Module
@mcp.tool()
async def update_product_module(
    product_module_number: str = Field(..., alias="productModuleNumber", description="Unique identifier for the Product Module within the Vendor's product catalog. This value becomes read-only once the first Licensee is created for the Product."),
    active: bool | None = Field(None, description="Enable or disable the Product Module. When disabled, Licensees cannot obtain new Licenses for this module."),
    name: str | None = Field(None, description="Display name for the Product Module shown to end customers in NetLicensing Shop."),
    licensing_model: str | None = Field(None, alias="licensingModel", description="Licensing model that governs how this Product Module's licenses are configured and validated. The selected model determines which additional properties are required."),
    max_checkout_validity: str | None = Field(None, alias="maxCheckoutValidity", description="Maximum number of days a license can remain checked out. Required when using the Floating licensing model."),
    yellow_threshold: str | None = Field(None, alias="yellowThreshold", description="Remaining time volume threshold (in days) that triggers yellow status. Required when using the Rental licensing model."),
    red_threshold: str | None = Field(None, alias="redThreshold", description="Remaining time volume threshold (in days) that triggers red status. Required when using the Rental licensing model."),
    license_template: list[Literal["TIMEVOLUME", "FEATURE"]] | None = Field(None, alias="licenseTemplate", description="License Template configuration for this Product Module. Required when using the Try & Buy licensing model."),
    node_secret_mode: list[Literal["PREDEFINED", "CLIENT"]] | None = Field(None, alias="nodeSecretMode", description="Secret Mode configuration for node-locked licensing. Required when using the Node-Locked licensing model."),
) -> dict[str, Any]:
    """Update properties of an existing Product Module. Modifies the specified Product Module configuration and returns the updated module details."""

    _max_checkout_validity = _parse_int(max_checkout_validity)
    _yellow_threshold = _parse_int(yellow_threshold)
    _red_threshold = _parse_int(red_threshold)

    # Construct request model with validation
    try:
        _request = _models.UpdateProductModuleRequest(
            path=_models.UpdateProductModuleRequestPath(product_module_number=product_module_number),
            body=_models.UpdateProductModuleRequestBody(active=active, name=name, licensing_model=licensing_model, max_checkout_validity=_max_checkout_validity, yellow_threshold=_yellow_threshold, red_threshold=_red_threshold, license_template=license_template, node_secret_mode=node_secret_mode)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_product_module: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/productmodule/{productModuleNumber}", _request.path.model_dump(by_alias=True)) if _request.path else "/productmodule/{productModuleNumber}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_product_module")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_product_module", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_product_module",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/x-www-form-urlencoded",
        headers=_http_headers,
    )

    return _response_data

# Tags: Product Module
@mcp.tool()
async def delete_product_module(
    product_module_number: str = Field(..., alias="productModuleNumber", description="The unique identifier for the Product Module within a Vendor's product catalog. This number must exactly match an existing Product Module."),
    force_cascade: bool | None = Field(None, alias="forceCascade", description="When enabled, forces deletion of the Product Module and all its child objects in the hierarchy. Use with caution as this operation cannot be undone."),
) -> dict[str, Any]:
    """Permanently delete a Product Module by its unique number. Optionally cascade the deletion to all descendant objects."""

    # Construct request model with validation
    try:
        _request = _models.DeleteProductModuleRequest(
            path=_models.DeleteProductModuleRequestPath(product_module_number=product_module_number),
            query=_models.DeleteProductModuleRequestQuery(force_cascade=force_cascade)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_product_module: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/productmodule/{productModuleNumber}", _request.path.model_dump(by_alias=True)) if _request.path else "/productmodule/{productModuleNumber}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_product_module")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_product_module", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_product_module",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: License Template
@mcp.tool()
async def list_license_templates() -> dict[str, Any]:
    """Retrieve all available license templates configured for the current vendor. Use this to discover template options before creating or managing licenses."""

    # Extract parameters for API call
    _http_path = "/licensetemplate"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_license_templates")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_license_templates", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_license_templates",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: License Template
@mcp.tool()
async def create_license_template(
    product_module_number: str = Field(..., alias="productModuleNumber", description="The unique identifier of the Product Module under which this License Template will be created."),
    name: str = Field(..., description="A descriptive name for the License Template that identifies its purpose and licensing model."),
    active: bool = Field(..., description="Controls whether the License Template is active; when disabled, licensees cannot obtain new licenses from this template."),
    license_type: str = Field(..., alias="licenseType", description="Specifies the licensing model for licenses created from this template. Choose from: FEATURE (feature-based licensing), TIMEVOLUME (time-limited volume licensing), FLOATING (concurrent user licensing), or QUANTITY (fixed quantity licensing)."),
    time_volume_period: str | None = Field(None, alias="timeVolumePeriod", description="Required when licenseType is set to TIMEVOLUME; specifies the duration period for time-volume licenses (e.g., monthly, yearly)."),
    automatic: bool | None = Field(None, description="When enabled, new licensees automatically receive one license from this template upon creation. Automatic licenses must have a price of zero."),
    hidden: bool | None = Field(None, description="When enabled, this License Template is hidden from the NetLicensing Shop and not offered for direct purchase by customers."),
    hide_licenses: bool | None = Field(None, alias="hideLicenses", description="When enabled, licenses created from this template are hidden from end customers but still participate in license validation checks."),
    quota: str | None = Field(None, description="Required for quota-based licensing models; defines the maximum quota allocation for licenses created from this template."),
) -> dict[str, Any]:
    """Creates a new License Template for a specified Product Module, defining the licensing model and availability rules for licensees."""

    # Construct request model with validation
    try:
        _request = _models.CreateLicenseTemplateRequest(
            body=_models.CreateLicenseTemplateRequestBody(product_module_number=product_module_number, name=name, active=active, license_type=license_type, time_volume_period=time_volume_period, automatic=automatic, hidden=hidden, hide_licenses=hide_licenses, quota=quota)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_license_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/licensetemplate"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_license_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_license_template", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_license_template",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/x-www-form-urlencoded",
        headers=_http_headers,
    )

    return _response_data

# Tags: License Template
@mcp.tool()
async def get_license_template(license_template_number: str = Field(..., alias="licenseTemplateNumber", description="The unique identifier for the License Template, assigned by the vendor during creation or auto-generated by NetLicensing. This value becomes read-only once the first License is created from this template.")) -> dict[str, Any]:
    """Retrieve a specific License Template by its unique identifier. This template defines the licensing model and terms for products from a vendor."""

    # Construct request model with validation
    try:
        _request = _models.GetLicenseTemplateRequest(
            path=_models.GetLicenseTemplateRequestPath(license_template_number=license_template_number)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_license_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/licensetemplate/{licenseTemplateNumber}", _request.path.model_dump(by_alias=True)) if _request.path else "/licensetemplate/{licenseTemplateNumber}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_license_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_license_template", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_license_template",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: License Template
@mcp.tool()
async def update_license_template(
    license_template_number: str = Field(..., alias="licenseTemplateNumber", description="The unique identifier for the License Template within the Vendor's product portfolio. This value is immutable once the first License is created from this template."),
    name: str | None = Field(None, description="A human-readable name for the License Template to identify it in the system."),
    active: bool | None = Field(None, description="Enable or disable the License Template. When disabled, new Licensees cannot obtain Licenses from this template, though existing Licenses remain valid."),
    license_type: str | None = Field(None, alias="licenseType", description="Specifies the licensing model for Licenses created from this template. Choose from: FEATURE (feature-based licensing), TIMEVOLUME (time and volume-based), FLOATING (concurrent usage), or QUANTITY (fixed quantity)."),
    time_volume_period: str | None = Field(None, alias="timeVolumePeriod", description="Required for TIMEVOLUME License Type. Defines the time period over which volume is measured (e.g., monthly, yearly)."),
    automatic: bool | None = Field(None, description="When enabled, each newly created Licensee automatically receives one License from this template at no cost. Automatic Licenses must have a price of zero."),
    hidden: bool | None = Field(None, description="When enabled, this License Template is excluded from the NetLicensing Shop and is not available for direct purchase by customers."),
    hide_licenses: bool | None = Field(None, alias="hideLicenses", description="When enabled, Licenses created from this template are hidden from end-customer visibility but still participate in license validation checks."),
    quota: str | None = Field(None, description="Required when using the Quota License Model. Specifies the quota limit for Licenses created from this template."),
) -> dict[str, Any]:
    """Update properties of an existing License Template. Changes apply to the template itself and affect how new Licenses are created from it."""

    # Construct request model with validation
    try:
        _request = _models.UpdateLicenseTemplateRequest(
            path=_models.UpdateLicenseTemplateRequestPath(license_template_number=license_template_number),
            body=_models.UpdateLicenseTemplateRequestBody(name=name, active=active, license_type=license_type, time_volume_period=time_volume_period, automatic=automatic, hidden=hidden, hide_licenses=hide_licenses, quota=quota)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_license_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/licensetemplate/{licenseTemplateNumber}", _request.path.model_dump(by_alias=True)) if _request.path else "/licensetemplate/{licenseTemplateNumber}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_license_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_license_template", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_license_template",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/x-www-form-urlencoded",
        headers=_http_headers,
    )

    return _response_data

# Tags: License Template
@mcp.tool()
async def delete_license_template(
    license_template_number: str = Field(..., alias="licenseTemplateNumber", description="The unique identifier for the License Template to delete, assigned across all Products within a Vendor."),
    force_cascade: bool | None = Field(None, alias="forceCascade", description="When enabled, forces deletion of the License Template and all its descendant objects. Use with caution as this operation cannot be undone."),
) -> dict[str, Any]:
    """Permanently delete a License Template by its unique number. Optionally cascade the deletion to remove all dependent objects."""

    # Construct request model with validation
    try:
        _request = _models.DeleteLicenseTemplateRequest(
            path=_models.DeleteLicenseTemplateRequestPath(license_template_number=license_template_number),
            query=_models.DeleteLicenseTemplateRequestQuery(force_cascade=force_cascade)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_license_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/licensetemplate/{licenseTemplateNumber}", _request.path.model_dump(by_alias=True)) if _request.path else "/licensetemplate/{licenseTemplateNumber}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_license_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_license_template", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_license_template",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Licensee
@mcp.tool()
async def list_licensees() -> dict[str, Any]:
    """Retrieve a complete list of all licensees associated with the current vendor account."""

    # Extract parameters for API call
    _http_path = "/licensee"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_licensees")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_licensees", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_licensees",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Licensee
@mcp.tool()
async def create_licensee(
    product_number: str = Field(..., alias="productNumber", description="The product number to assign to the new Licensee. This identifier links the licensee to a specific product."),
    active: bool = Field(..., description="Determines whether the Licensee is active. When set to false, the Licensee is disabled and cannot obtain new licenses or participate in validation."),
    name: str | None = Field(None, description="The display name for the Licensee. Used to identify the licensee in the system."),
    marked_for_transfer: bool | None = Field(None, alias="markedForTransfer", description="Indicates whether this Licensee is marked for transfer to another entity. Used to flag licensees pending transfer operations."),
) -> dict[str, Any]:
    """Creates a new Licensee entity that can obtain licenses and be validated. The licensee's active status determines whether it can acquire new licenses and participate in validation processes."""

    # Construct request model with validation
    try:
        _request = _models.CreateLicenseeRequest(
            body=_models.CreateLicenseeRequestBody(product_number=product_number, name=name, active=active, marked_for_transfer=marked_for_transfer)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_licensee: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/licensee"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_licensee")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_licensee", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_licensee",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/x-www-form-urlencoded",
        headers=_http_headers,
    )

    return _response_data

# Tags: Licensee
@mcp.tool()
async def get_licensee(licensee_number: str = Field(..., alias="licenseeNumber", description="The unique identifier assigned to the licensee within the vendor's product ecosystem. This value is either vendor-assigned during licensee creation or auto-generated by NetLicensing, and becomes read-only once the first license is issued.")) -> dict[str, Any]:
    """Retrieve a specific licensee by their unique identifier. Returns complete licensee details including licensing status and associated metadata."""

    # Construct request model with validation
    try:
        _request = _models.GetLicenseeRequest(
            path=_models.GetLicenseeRequestPath(licensee_number=licensee_number)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_licensee: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/licensee/{licenseeNumber}", _request.path.model_dump(by_alias=True)) if _request.path else "/licensee/{licenseeNumber}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_licensee")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_licensee", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_licensee",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Licensee
@mcp.tool()
async def update_licensee(
    licensee_number: str = Field(..., alias="licenseeNumber", description="The unique identifier for the Licensee within the Vendor's product ecosystem. This value is assigned by the Vendor during creation or auto-generated by NetLicensing, and becomes read-only once the first License is created for this Licensee."),
    active: bool | None = Field(None, description="Enable or disable the Licensee. When set to false, the Licensee cannot obtain new Licenses and validation checks are disabled."),
    name: str | None = Field(None, description="Display name or label for the Licensee."),
    marked_for_transfer: bool | None = Field(None, alias="markedForTransfer", description="Flag indicating whether this Licensee is eligible for transfer to another Vendor or account."),
) -> dict[str, Any]:
    """Update properties of an existing Licensee. Modify activation status, name, or transfer eligibility and receive the updated Licensee object."""

    # Construct request model with validation
    try:
        _request = _models.UpdateLicenseeRequest(
            path=_models.UpdateLicenseeRequestPath(licensee_number=licensee_number),
            body=_models.UpdateLicenseeRequestBody(active=active, name=name, marked_for_transfer=marked_for_transfer)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_licensee: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/licensee/{licenseeNumber}", _request.path.model_dump(by_alias=True)) if _request.path else "/licensee/{licenseeNumber}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_licensee")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_licensee", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_licensee",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/x-www-form-urlencoded",
        headers=_http_headers,
    )

    return _response_data

# Tags: Licensee
@mcp.tool()
async def delete_licensee(
    licensee_number: str = Field(..., alias="licenseeNumber", description="The unique identifier for the licensee to delete. This number is unique across all products for a given vendor."),
    force_cascade: bool | None = Field(None, alias="forceCascade", description="When enabled, forces deletion of the licensee and all its dependent objects and descendants. Use with caution as this operation cannot be undone."),
) -> dict[str, Any]:
    """Permanently delete a licensee by its unique number. Optionally cascade the deletion to remove all dependent objects and descendants."""

    # Construct request model with validation
    try:
        _request = _models.DeleteLicenseeRequest(
            path=_models.DeleteLicenseeRequestPath(licensee_number=licensee_number),
            query=_models.DeleteLicenseeRequestQuery(force_cascade=force_cascade)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_licensee: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/licensee/{licenseeNumber}", _request.path.model_dump(by_alias=True)) if _request.path else "/licensee/{licenseeNumber}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_licensee")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_licensee", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_licensee",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Licensee
@mcp.tool()
async def validate_licensee(
    licensee_number: str = Field(..., alias="licenseeNumber", description="The unique identifier for the licensee to validate. Maximum length is 1000 characters."),
    licensee_name: str | None = Field(None, alias="licenseeName", description="Human-readable name for the licensee. Used as a custom property if the licensee is auto-created during validation."),
    product_number: str | None = Field(None, alias="productNumber", description="The product identifier associated with the licensee. Required when licensee auto-creation is enabled to specify which product the new licensee should be added to."),
    product_module_number: str | None = Field(None, alias="productModuleNumber", description="The product module identifier for node-locked licensing models. Specifies which module within the product is being validated."),
    node_secret: str | None = Field(None, alias="nodeSecret", description="A unique secret value for node-locked licensing models. Used to identify and validate the specific node."),
    session_id: str | None = Field(None, alias="sessionId", description="A unique session identifier for floating licensing models. Used to track and manage the session within the available pool."),
    action: Literal["checkOut", "checkIn"] | None = Field(None, description="The session action for floating licensing models. Use 'checkOut' to allocate a session from the pool or 'checkIn' to return a session to the pool."),
) -> dict[str, Any]:
    """Validates the active licenses for a specific licensee, supporting both node-locked and floating licensing models. Use this to verify license status and manage session allocation for floating licenses."""

    # Construct request model with validation
    try:
        _request = _models.ValidateLicenseeRequest(
            path=_models.ValidateLicenseeRequestPath(licensee_number=licensee_number),
            body=_models.ValidateLicenseeRequestBody(licensee_name=licensee_name, product_number=product_number, product_module_number=product_module_number, node_secret=node_secret, session_id=session_id, action=action)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for validate_licensee: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/licensee/{licenseeNumber}/validate", _request.path.model_dump(by_alias=True)) if _request.path else "/licensee/{licenseeNumber}/validate"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("validate_licensee")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("validate_licensee", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="validate_licensee",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/x-www-form-urlencoded",
        headers=_http_headers,
    )

    return _response_data

# Tags: Licensee
@mcp.tool()
async def transfer_licenses_between_licensees(
    licensee_number: str = Field(..., alias="licenseeNumber", description="The destination licensee number that will receive the transferred licenses. Must be a valid licensee identifier with a maximum length of 1000 characters."),
    source_licensee_number: str = Field(..., alias="sourceLicenseeNumber", description="The source licensee number from which licenses will be transferred. Must be a valid licensee identifier with a maximum length of 1000 characters."),
) -> dict[str, Any]:
    """Transfer licenses from a source licensee to a destination licensee. This operation moves all or specified licenses between two licensee accounts."""

    # Construct request model with validation
    try:
        _request = _models.TransferLicensesRequest(
            path=_models.TransferLicensesRequestPath(licensee_number=licensee_number),
            body=_models.TransferLicensesRequestBody(source_licensee_number=source_licensee_number)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for transfer_licenses_between_licensees: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/licensee/{licenseeNumber}/transfer", _request.path.model_dump(by_alias=True)) if _request.path else "/licensee/{licenseeNumber}/transfer"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("transfer_licenses_between_licensees")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("transfer_licenses_between_licensees", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="transfer_licenses_between_licensees",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/x-www-form-urlencoded",
        headers=_http_headers,
    )

    return _response_data

# Tags: License
@mcp.tool()
async def list_licenses() -> dict[str, Any]:
    """Retrieve a complete list of all licenses associated with the current vendor account."""

    # Extract parameters for API call
    _http_path = "/license"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_licenses")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_licenses", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_licenses",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: License
@mcp.tool()
async def create_license(
    licensee_number: str = Field(..., alias="licenseeNumber", description="The unique identifier of the licensee to whom this license will be assigned."),
    license_template_number: str = Field(..., alias="licenseTemplateNumber", description="The unique identifier of the license template that defines the license type, model, and default properties."),
    active: bool = Field(..., description="Whether the license is active and available for use immediately upon creation."),
    name: str | None = Field(None, description="A display name for the licensed item. If not provided, the name from the license template will be used automatically."),
    parentfeature: str | None = Field(None, description="Required when the license template uses the 'TIMEVOLUME' type or 'RENTAL' licensing model. Identifies the parent feature or product this license applies to."),
    time_volume_period: str | None = Field(None, alias="timeVolumePeriod", description="The time period unit for time-volume based licenses (e.g., 'MONTH', 'YEAR'). Only applicable for 'TIMEVOLUME' license type."),
    start_date: str | None = Field(None, alias="startDate", description="The date and time when the license becomes effective. Required for 'TIMEVOLUME' license type. Must be provided in ISO 8601 date-time format."),
    hidden: bool | None = Field(None, description="If set to true, this license will not be displayed in the NetLicensing Shop as a purchased license. If not specified, the value from the license template will be used."),
    used_quantity: str | None = Field(None, alias="usedQuantity", description="The quantity of the licensed resource already consumed. Required for 'Pay-per-Use' licensing model to track usage."),
) -> dict[str, Any]:
    """Creates a new license by associating a licensee with a license template. The license inherits default properties from the template unless explicitly overridden."""

    # Construct request model with validation
    try:
        _request = _models.CreateLicenseRequest(
            body=_models.CreateLicenseRequestBody(licensee_number=licensee_number, license_template_number=license_template_number, active=active, name=name, parentfeature=parentfeature, time_volume_period=time_volume_period, start_date=start_date, hidden=hidden, used_quantity=used_quantity)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_license: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/license"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_license")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_license", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_license",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/x-www-form-urlencoded",
        headers=_http_headers,
    )

    return _response_data

# Tags: License
@mcp.tool()
async def get_license(license_number: str = Field(..., alias="licenseNumber", description="The unique license identifier assigned by the vendor or auto-generated by NetLicensing. This value is immutable after the associated creation transaction is closed.")) -> dict[str, Any]:
    """Retrieve a specific license by its unique identifier. Returns complete license details including status, product information, and licensee data."""

    # Construct request model with validation
    try:
        _request = _models.GetLicenseRequest(
            path=_models.GetLicenseRequestPath(license_number=license_number)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_license: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/license/{licenseNumber}", _request.path.model_dump(by_alias=True)) if _request.path else "/license/{licenseNumber}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_license")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_license", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_license",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: License
@mcp.tool()
async def update_license(
    license_number: str = Field(..., alias="licenseNumber", description="The unique identifier for the license to update. This number is assigned by the vendor or auto-generated by NetLicensing and cannot be changed after the creation transaction is closed."),
    active: bool | None = Field(None, description="Enable or disable the license. When disabled, the license becomes inactive."),
    name: str | None = Field(None, description="A human-readable name for the licensed item. If not provided during update, the existing name from the License Template is retained."),
    start_date: str | None = Field(None, alias="startDate", description="The start date and time for the license validity period. Required for TIMEVOLUME license types. Must be provided in ISO 8601 date-time format."),
    parentfeature: str | None = Field(None, description="The parent feature that this license is associated with or depends on."),
    time_volume_period: str | None = Field(None, alias="timeVolumePeriod", description="The time period duration for TIMEVOLUME license types (e.g., monthly, yearly, or custom interval)."),
    hidden: bool | None = Field(None, description="When set to true, this license will not be displayed in the NetLicensing Shop as a purchased license. If not specified, the setting from the License Template is used."),
    used_quantity: str | None = Field(None, alias="usedQuantity", description="The quantity of the licensed resource that has been consumed or used. Required and must be tracked for Pay-per-Use license models."),
) -> dict[str, Any]:
    """Update an existing license by its unique license number. Modify license properties such as activation status, name, validity period, and usage tracking."""

    # Construct request model with validation
    try:
        _request = _models.UpdateLicenseRequest(
            path=_models.UpdateLicenseRequestPath(license_number=license_number),
            body=_models.UpdateLicenseRequestBody(active=active, name=name, start_date=start_date, parentfeature=parentfeature, time_volume_period=time_volume_period, hidden=hidden, used_quantity=used_quantity)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_license: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/license/{licenseNumber}", _request.path.model_dump(by_alias=True)) if _request.path else "/license/{licenseNumber}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_license")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_license", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_license",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/x-www-form-urlencoded",
        headers=_http_headers,
    )

    return _response_data

# Tags: License
@mcp.tool()
async def delete_license(license_number: str = Field(..., alias="licenseNumber", description="The unique license identifier assigned by the vendor or generated by NetLicensing. This value is immutable after the associated creation transaction is closed.")) -> dict[str, Any]:
    """Permanently delete a license by its unique identifier. Once deleted, the license cannot be recovered."""

    # Construct request model with validation
    try:
        _request = _models.DeleteLicenseRequest(
            path=_models.DeleteLicenseRequestPath(license_number=license_number)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_license: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/license/{licenseNumber}", _request.path.model_dump(by_alias=True)) if _request.path else "/license/{licenseNumber}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_license")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_license", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_license",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Transaction
@mcp.tool()
async def list_transactions() -> dict[str, Any]:
    """Retrieve a complete list of all transactions associated with the current vendor account."""

    # Extract parameters for API call
    _http_path = "/transaction"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_transactions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_transactions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_transactions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Transaction
@mcp.tool()
async def create_transaction(
    active: bool = Field(..., description="Activation status of the transaction. Must always be set to true when creating a transaction."),
    status: Literal["CANCELLED", "CLOSED", "PENDING"] = Field(..., description="The current state of the transaction. Must be one of: PENDING (awaiting processing), CLOSED (completed), or CANCELLED (voided)."),
    source: Literal["SHOP"] = Field(..., description="The origin system for this transaction. Must be set to SHOP, indicating this is a point-of-sale transaction for internal use."),
    licensee_number: str | None = Field(None, alias="licenseeNumber", description="Optional identifier for the licensee associated with this transaction."),
    payment_method: str | None = Field(None, alias="paymentMethod", description="Optional payment method used for this transaction (e.g., credit card, cash, digital wallet)."),
) -> dict[str, Any]:
    """Creates a new transaction in the system. Transactions are always initialized in an active state and require a status and source to be specified."""

    # Construct request model with validation
    try:
        _request = _models.CreateTransactionRequest(
            body=_models.CreateTransactionRequestBody(licensee_number=licensee_number, active=active, status=status, source=source, payment_method=payment_method)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_transaction: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/transaction"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_transaction")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_transaction", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_transaction",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/x-www-form-urlencoded",
        headers=_http_headers,
    )

    return _response_data

# Tags: Transaction
@mcp.tool()
async def get_transaction(transaction_number: str = Field(..., alias="transactionNumber", description="The unique transaction identifier assigned by the vendor. This number is globally unique across all products within the vendor's system and is used to retrieve the specific transaction record.")) -> dict[str, Any]:
    """Retrieve a specific transaction by its unique identifier. Returns complete transaction details including all associated metadata and status information."""

    # Construct request model with validation
    try:
        _request = _models.GetTransactionRequest(
            path=_models.GetTransactionRequestPath(transaction_number=transaction_number)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_transaction: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/transaction/{transactionNumber}", _request.path.model_dump(by_alias=True)) if _request.path else "/transaction/{transactionNumber}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_transaction")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_transaction", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_transaction",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Transaction
@mcp.tool()
async def update_transaction(
    transaction_number: str = Field(..., alias="transactionNumber", description="The unique identifier for the transaction to update. This number is unique across all products for a given vendor."),
    active: bool | None = Field(None, description="Flag indicating whether the transaction is active. This field should always be set to true for transactions."),
    status: Literal["CANCELLED", "CLOSED", "PENDING"] | None = Field(None, description="The current state of the transaction. Valid states are: PENDING (awaiting processing), CLOSED (completed), or CANCELLED (voided)."),
    source: Literal["SHOP"] | None = Field(None, description="The origin system for the transaction. Currently only SHOP is supported; AUTO transactions are reserved for internal system use only."),
    payment_method: str | None = Field(None, alias="paymentMethod", description="The payment method used for the transaction (e.g., credit card, debit card, digital wallet)."),
) -> dict[str, Any]:
    """Update specific properties of an existing transaction identified by its transaction number. Returns the updated transaction with all changes applied."""

    # Construct request model with validation
    try:
        _request = _models.UpdateTransactionRequest(
            path=_models.UpdateTransactionRequestPath(transaction_number=transaction_number),
            body=_models.UpdateTransactionRequestBody(active=active, status=status, source=source, payment_method=payment_method)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_transaction: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/transaction/{transactionNumber}", _request.path.model_dump(by_alias=True)) if _request.path else "/transaction/{transactionNumber}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_transaction")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_transaction", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_transaction",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/x-www-form-urlencoded",
        headers=_http_headers,
    )

    return _response_data

# Tags: Token
@mcp.tool()
async def list_tokens() -> dict[str, Any]:
    """Retrieve all authentication tokens associated with the current vendor account. Use this to view and manage API credentials."""

    # Extract parameters for API call
    _http_path = "/token"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_tokens")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_tokens", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_tokens",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Token
@mcp.tool()
async def create_token(
    token_type: Literal["DEFAULT", "SHOP", "APIKEY"] = Field(..., alias="tokenType", description="The category of token to generate. Choose DEFAULT for licensee login actions, SHOP for customer checkout flows, or APIKEY for programmatic API access."),
    api_key_role: Literal["ROLE_APIKEY_LICENSEE", "ROLE_APIKEY_ANALYTICS", "ROLE_APIKEY_OPERATION", "ROLE_APIKEY_MAINTENANCE", "ROLE_APIKEY_ADMIN"] | None = Field(None, alias="apiKeyRole", description="The permission level for APIKEY tokens only. Defaults to ROLE_APIKEY_LICENSEE if not specified. Select from licensee, analytics, operation, maintenance, or admin roles."),
    type_: Literal["ACTION"] | None = Field(None, alias="type", description="The token behavior for DEFAULT tokens only. Currently supports ACTION type for performing specific licensee login operations."),
    action: Literal["licenseeLogin"] | None = Field(None, description="The specific operation for DEFAULT tokens with type=ACTION only. Currently supports licenseeLogin action."),
    licensee_number: str | None = Field(None, alias="licenseeNumber", description="The licensee identifier required for SHOP tokens or DEFAULT tokens with type=ACTION. Identifies which licensee owns or is associated with the token."),
    private_key: str | None = Field(None, alias="privateKey", description="The private key for APIKEY tokens only, used for token validation. Must be provided as a single line without spaces."),
    product_number: str | None = Field(None, alias="productNumber", description="The product identifier required for SHOP tokens. Specifies which product the customer can purchase through the generated shop token."),
    license_template_number: str | None = Field(None, alias="licenseTemplateNumber", description="The license template identifier for SHOP tokens only. Determines the licensing terms applied to purchases made with this token."),
    predefined_shopping_item: str | None = Field(None, alias="predefinedShoppingItem", description="The shopping item name for SHOP tokens only. Displayed to the customer during the checkout process."),
    success_url_title: str | None = Field(None, alias="successURLTitle", description="The link title for SHOP tokens only, displayed to the customer after successful checkout completion."),
    cancel_url_title: str | None = Field(None, alias="cancelURLTitle", description="The link title for SHOP tokens only, displayed to the customer if they cancel the checkout process."),
) -> dict[str, Any]:
    """Generate authentication or shop tokens for different use cases. The token type determines which additional parameters are required: APIKEY tokens for programmatic access, SHOP tokens for customer checkout flows, or DEFAULT tokens for licensee login actions."""

    # Construct request model with validation
    try:
        _request = _models.CreateTokenRequest(
            body=_models.CreateTokenRequestBody(token_type=token_type, api_key_role=api_key_role, type_=type_, action=action, licensee_number=licensee_number, private_key=private_key, product_number=product_number, license_template_number=license_template_number, predefined_shopping_item=predefined_shopping_item, success_url_title=success_url_title, cancel_url_title=cancel_url_title)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_token: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/token"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_token")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_token", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_token",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/x-www-form-urlencoded",
        headers=_http_headers,
    )

    return _response_data

# Tags: Token
@mcp.tool()
async def get_token(token_number: str = Field(..., alias="tokenNumber", description="The unique identifier of the token to retrieve, provided as a string value.")) -> dict[str, Any]:
    """Retrieve a specific token by its token number. Use this operation to fetch details about an individual token in the system."""

    # Construct request model with validation
    try:
        _request = _models.GetTokenRequest(
            path=_models.GetTokenRequestPath(token_number=token_number)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_token: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/token/{tokenNumber}", _request.path.model_dump(by_alias=True)) if _request.path else "/token/{tokenNumber}"
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

# Tags: Token
@mcp.tool()
async def delete_token(token_number: str = Field(..., alias="tokenNumber", description="The unique identifier of the token to delete, provided as a string.")) -> dict[str, Any]:
    """Permanently delete a token by its number. This operation removes the token from the system and cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteTokenRequest(
            path=_models.DeleteTokenRequestPath(token_number=token_number)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_token: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/token/{tokenNumber}", _request.path.model_dump(by_alias=True)) if _request.path else "/token/{tokenNumber}"
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

# Tags: Payment Method
@mcp.tool()
async def list_payment_methods() -> dict[str, Any]:
    """Retrieve all payment methods configured for the current vendor account. Returns a complete list of available payment options."""

    # Extract parameters for API call
    _http_path = "/paymentmethod"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_payment_methods")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_payment_methods", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_payment_methods",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Payment Method
@mcp.tool()
async def get_payment_method(payment_method_number: str = Field(..., alias="paymentMethodNumber", description="The unique identifier for the payment method to retrieve.")) -> dict[str, Any]:
    """Retrieve detailed information about a specific payment method using its unique payment method number."""

    # Construct request model with validation
    try:
        _request = _models.GetPaymentMethodRequest(
            path=_models.GetPaymentMethodRequestPath(payment_method_number=payment_method_number)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_payment_method: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/paymentmethod/{paymentMethodNumber}", _request.path.model_dump(by_alias=True)) if _request.path else "/paymentmethod/{paymentMethodNumber}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_payment_method")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_payment_method", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_payment_method",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Payment Method
@mcp.tool()
async def update_payment_method(
    payment_method_number: str = Field(..., alias="paymentMethodNumber", description="The unique identifier of the payment method to update."),
    active: bool | None = Field(None, description="Set to false to disable the payment method, or true to enable it. If not provided, the current active status is preserved."),
    paypal_subject: str | None = Field(None, description="The email address associated with the PayPal account. Required only when updating PayPal-based payment methods."),
) -> dict[str, Any]:
    """Update properties of an existing payment method, such as enabling/disabling it or modifying PayPal account details. Returns the updated payment method."""

    # Construct request model with validation
    try:
        _request = _models.UpdatePaymentMethodRequest(
            path=_models.UpdatePaymentMethodRequestPath(payment_method_number=payment_method_number),
            body=_models.UpdatePaymentMethodRequestBody(active=active, paypal_subject=paypal_subject)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_payment_method: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/paymentmethod/{paymentMethodNumber}", _request.path.model_dump(by_alias=True)) if _request.path else "/paymentmethod/{paymentMethodNumber}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_payment_method")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_payment_method", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_payment_method",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/x-www-form-urlencoded",
        headers=_http_headers,
    )

    return _response_data

# Tags: Utility
@mcp.tool()
async def list_licensing_models() -> dict[str, Any]:
    """Retrieve a complete list of all licensing models supported by the service. Use this to understand available licensing options for your integration."""

    # Extract parameters for API call
    _http_path = "/utility/licensingModels"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_licensing_models")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_licensing_models", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_licensing_models",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Utility
@mcp.tool()
async def list_license_types() -> dict[str, Any]:
    """Retrieve a complete list of all license types supported by the service. Use this to understand available licensing options for your integration."""

    # Extract parameters for API call
    _http_path = "/utility/licenseTypes"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_license_types")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_license_types", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_license_types",
        method="GET",
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
        print("  python labs64_net_licensing_res_tful_api_test_center_server.py", file=sys.stderr)
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

    parser = argparse.ArgumentParser(description="Labs64 NetLicensing RESTful API Test Center MCP Server")

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
    logger.info("Starting Labs64 NetLicensing RESTful API Test Center MCP Server")
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

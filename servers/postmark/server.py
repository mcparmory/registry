#!/usr/bin/env python3
"""
Postmark MCP Server
Generated: 2026-04-22 10:56:12 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

import argparse
import asyncio
import contextlib
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
from fastmcp.tools.tool import ToolResult
from pydantic import Field

BASE_URL = os.getenv("BASE_URL", "https://api.postmarkapp.com")
SERVER_NAME = "Postmark"
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

class UpstreamAPIError(Exception):
    """Expected upstream API error that should not become a server traceback."""

    def __init__(
        self,
        *,
        status_code: int,
        request_id: str | None,
        method: str,
        path: str,
        tool_name: str | None,
        error_data: dict[str, Any],
        error_message: str,
    ) -> None:
        super().__init__(error_message)
        self.status_code = status_code
        self.request_id = request_id
        self.method = method
        self.path = path
        self.tool_name = tool_name
        self.error_data = error_data
        self.error_message = error_message


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
                    raise UpstreamAPIError(
                        status_code=status_code,
                        request_id=request_id,
                        method=method,
                        path=path,
                        tool_name=tool_name,
                        error_data=sanitized_data,
                        error_message=error_message,
                    )

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

        except UpstreamAPIError:
            # Expected upstream HTTP error — already logged above.
            raise

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
        raise UpstreamAPIError(
            status_code=last_error.response.status_code,
            request_id=request_id,
            method=method,
            path=path,
            tool_name=tool_name,
            error_data=sanitized_error,
            error_message=error_message,
        )

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
                    with contextlib.suppress(json.JSONDecodeError, ValueError):
                        context.message.arguments[key] = json.loads(value)
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
) -> tuple[dict[str, Any] | ToolResult, int]:
    """
    Execute tool request with timeout handling and metrics recording.

    Returns:
        Tuple of (normalized_response_data_or_tool_result, status_code).
        Successful responses are normalized to dict format for Pydantic validation.
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

    except UpstreamAPIError as e:
        latency_ms = (time.time() - start_time) * 1000.0
        return ToolResult(
            content=e.error_message,
            structured_content={
                "ok": False,
                "status": e.status_code,
                "request_id": e.request_id,
                "method": e.method,
                "path": e.path,
                "error": e.error_message,
                "details": e.error_data,
            },
        ), e.status_code

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
    'ServerApiToken',
    'AccountApiToken',
]

# Initialize authentication handlers at server startup
_auth_handlers: dict[str, Any] = {}
try:
    _auth_handlers["ServerApiToken"] = _auth.APIKeyAuth(env_var="SERVER_API_TOKEN_API_KEY", location="header", param_name="X-Postmark-Server-Token")
    logging.info("Authentication configured: ServerApiToken")
except ValueError as e:
    # Extract credential names from error message (first sentence before "Leave empty")
    error_msg = str(e).split("Leave empty")[0].strip()
    logging.warning(f"Credentials for ServerApiToken not configured: {error_msg}")
    _auth_handlers["ServerApiToken"] = None
try:
    _auth_handlers["AccountApiToken"] = _auth.APIKeyAuth(env_var="ACCOUNT_API_TOKEN_API_KEY", location="header", param_name="X-Postmark-Account-Token")
    logging.info("Authentication configured: AccountApiToken")
except ValueError as e:
    # Extract credential names from error message (first sentence before "Leave empty")
    error_msg = str(e).split("Leave empty")[0].strip()
    logging.warning(f"Credentials for AccountApiToken not configured: {error_msg}")
    _auth_handlers["AccountApiToken"] = None

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

mcp = FastMCP("Postmark", middleware=[_JsonCoercionMiddleware()])

# Tags: Bounces API
@mcp.tool()
async def list_bounces(
    count: int = Field(..., description="Number of bounce records to return per request, up to a maximum of 500.", le=500),
    offset: int = Field(..., description="Number of bounce records to skip from the beginning of the result set for pagination."),
    type_: Literal["HardBounce", "Transient", "Unsubscribe", "Subscribe", "AutoResponder", "AddressChange", "DnsError", "SpamNotification", "OpenRelayTest", "Unknown", "SoftBounce", "VirusNotification", "MailFrontier Matador.", "BadEmailAddress", "SpamComplaint", "ManuallyDeactivated", "Unconfirmed", "Blocked", "SMTPApiError", "InboundError", "DMARCPolicy", "TemplateRenderingFailed"] | None = Field(None, alias="type", description="Filter results by bounce type category (e.g., HardBounce, SoftBounce, SpamComplaint, DMARCPolicy, etc.)."),
    inactive: bool | None = Field(None, description="Filter results to show only emails that were deactivated by Postmark (true), only active emails (false), or both if not specified."),
    email_filter: str | None = Field(None, alias="emailFilter", description="Filter results by a specific email address."),
    message_id: str | None = Field(None, alias="messageID", description="Filter results by the message ID associated with the bounce."),
    tag: str | None = Field(None, description="Filter results by a tag assigned to the message."),
    todate: str | None = Field(None, description="Filter results to include only bounces up to and including this date (format: YYYY-MM-DD)."),
    fromdate: str | None = Field(None, description="Filter results to include only bounces starting from and after this date (format: YYYY-MM-DD)."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of email bounces from your Postmark server, with optional filtering by bounce type, email address, date range, and other criteria."""

    # Construct request model with validation
    try:
        _request = _models.GetBouncesRequest(
            query=_models.GetBouncesRequestQuery(count=count, offset=offset, type_=type_, inactive=inactive, email_filter=email_filter, message_id=message_id, tag=tag, todate=todate, fromdate=fromdate)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_bounces: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/bounces"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_bounces")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_bounces", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_bounces",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Bounces API
@mcp.tool()
async def get_bounce_by_id(bounceid: str = Field(..., description="The unique identifier of the bounce record to retrieve. Must be a positive integer.")) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific bounce event by its ID. Use this to inspect bounce details such as type, email address, and timestamp for a particular bounce occurrence."""

    _bounceid = _parse_int(bounceid)

    # Construct request model with validation
    try:
        _request = _models.GetBouncesByBounceidRequest(
            path=_models.GetBouncesByBounceidRequestPath(bounceid=_bounceid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_bounce_by_id: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/bounces/{bounceid}", _request.path.model_dump(by_alias=True)) if _request.path else "/bounces/{bounceid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_bounce_by_id")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_bounce_by_id", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_bounce_by_id",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Bounces API
@mcp.tool()
async def activate_bounce(bounceid: str = Field(..., description="The unique identifier of the bounce record to activate. Must be a valid 64-bit integer.")) -> dict[str, Any] | ToolResult:
    """Reactivate a bounce record in Postmark, allowing it to be processed again. This operation marks a previously bounced email address as active."""

    _bounceid = _parse_int(bounceid)

    # Construct request model with validation
    try:
        _request = _models.PutBouncesActivateRequest(
            path=_models.PutBouncesActivateRequestPath(bounceid=_bounceid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for activate_bounce: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/bounces/{bounceid}/activate", _request.path.model_dump(by_alias=True)) if _request.path else "/bounces/{bounceid}/activate"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("activate_bounce")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("activate_bounce", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="activate_bounce",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Bounces API
@mcp.tool()
async def get_bounce_dump(bounceid: str = Field(..., description="The unique identifier of the bounce event whose dump data you want to retrieve. Must be a positive integer.")) -> dict[str, Any] | ToolResult:
    """Retrieve the detailed dump data for a specific bounce event. This provides comprehensive information about why a message bounced, including diagnostic details and headers."""

    _bounceid = _parse_int(bounceid)

    # Construct request model with validation
    try:
        _request = _models.GetBouncesDumpRequest(
            path=_models.GetBouncesDumpRequestPath(bounceid=_bounceid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_bounce_dump: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/bounces/{bounceid}/dump", _request.path.model_dump(by_alias=True)) if _request.path else "/bounces/{bounceid}/dump"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_bounce_dump")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_bounce_dump", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_bounce_dump",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Bounces API
@mcp.tool()
async def get_delivery_stats() -> dict[str, Any] | ToolResult:
    """Retrieve delivery statistics for messages sent through your Postmark server. This provides insights into message delivery performance and status."""

    # Extract parameters for API call
    _http_path = "/deliverystats"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_delivery_stats")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_delivery_stats", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_delivery_stats",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Sending API
@mcp.tool()
async def send_email(
    attachments: list[_models.Attachment] | None = Field(None, alias="Attachments", description="Array of file attachments to include with the email. Each attachment should specify the file content, name, and MIME type."),
    from_: str | None = Field(None, alias="From", description="Sender email address. Must correspond to a registered and confirmed Sender Signature in your Postmark account."),
    headers: list[_models.MessageHeader] | None = Field(None, alias="Headers", description="Array of custom email headers to include in the message. Each header should specify the name and value."),
    reply_to: str | None = Field(None, alias="ReplyTo", description="Email address to use for reply-to functionality. Overrides the default Reply To address configured in the sender signature."),
    subject: str | None = Field(None, alias="Subject", description="Subject line for the email message."),
    tag: str | None = Field(None, alias="Tag", description="Categorical tag for organizing and tracking email statistics. Useful for segmenting outgoing emails by type or campaign."),
    to: str | None = Field(None, alias="To", description="Recipient email address or addresses. Multiple recipients should be comma-separated. Maximum of 50 recipients per request."),
    track_links: Literal["None", "HtmlAndText", "HtmlOnly", "TextOnly"] | None = Field(None, alias="TrackLinks", description="Link tracking mode for click analytics. Options are None (no tracking), HtmlAndText (track both HTML and plain text links), HtmlOnly (track HTML links only), or TextOnly (track plain text links only). Defaults to the server's LinkTracking setting if not specified."),
    track_opens: bool | None = Field(None, alias="TrackOpens", description="Enable open tracking for this email to measure when recipients open the message."),
    text_body: str | None = Field(None, alias="TextBody", description="If no HtmlBody specified Plain text email message"),
    html_body: str | None = Field(None, alias="HtmlBody", description="If no TextBody specified HTML email message"),
) -> dict[str, Any] | ToolResult:
    """Send a single email message through Postmark. Supports attachments, custom headers, link and open tracking, and email tagging for analytics."""

    # Construct request model with validation
    try:
        _request = _models.PostEmailRequest(
            body=_models.PostEmailRequestBody(attachments=attachments, from_=from_, headers=headers, reply_to=reply_to, subject=subject, tag=tag, to=to, track_links=track_links, track_opens=track_opens, text_body=text_body, html_body=html_body)
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

# Tags: Sending API
@mcp.tool()
async def send_emails_batch(body: list[_models.SendEmailRequest] | None = Field(None, description="Array of email objects to send in this batch. Each object should contain the email details (recipient, subject, body, etc.) in Postmark's standard email format. Order is preserved for processing.")) -> dict[str, Any] | ToolResult:
    """Send multiple emails in a single batch request to efficiently deliver messages through Postmark's email service."""

    # Construct request model with validation
    try:
        _request = _models.PostEmailBatchRequest(
            body=_models.PostEmailBatchRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for send_emails_batch: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/email/batch"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("send_emails_batch")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("send_emails_batch", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="send_emails_batch",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Sending API, Templates API
@mcp.tool()
async def send_email_batch_with_templates(messages: list[_models.EmailWithTemplateRequest] | None = Field(None, alias="Messages", description="Array of email message objects to send, each containing template identifiers and recipient details. Order is preserved for batch processing.")) -> dict[str, Any] | ToolResult:
    """Send multiple emails in a single batch request using predefined email templates. This operation allows efficient bulk email delivery with template-based content."""

    # Construct request model with validation
    try:
        _request = _models.PostEmailBatchWithTemplatesRequest(
            body=_models.PostEmailBatchWithTemplatesRequestBody(messages=messages)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for send_email_batch_with_templates: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/email/batchWithTemplates"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("send_email_batch_with_templates")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("send_email_batch_with_templates", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="send_email_batch_with_templates",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Sending API, Templates API
@mcp.tool()
async def send_email_with_template(
    from_: str = Field(..., alias="From", description="Sender email address. Must be a valid email format and typically should be a verified sender on your Postmark account."),
    template_alias: str = Field(..., alias="TemplateAlias", description="Template identifier using a human-readable alias string. Either this or TemplateId must be provided to identify which template to use."),
    template_id: int = Field(..., alias="TemplateId", description="Template identifier using a numeric ID. Either this or TemplateAlias must be provided to identify which template to use."),
    template_model: dict[str, Any] = Field(..., alias="TemplateModel", description="Object containing key-value pairs that populate dynamic placeholders in the template. Structure should match the variables defined in your template."),
    to: str = Field(..., alias="To", description="Recipient email address. Must be a valid email format."),
    attachments: list[_models.Attachment] | None = Field(None, alias="Attachments", description="Array of file attachments to include with the email. Each attachment should specify the file content, filename, and MIME type."),
    headers: list[_models.MessageHeader] | None = Field(None, alias="Headers", description="Array of custom email headers to add to the message. Each header should include the header name and value."),
    inline_css: bool | None = Field(None, alias="InlineCss", description="Whether to automatically inline CSS styles from the template's style tags into individual HTML elements. Defaults to true."),
    reply_to: str | None = Field(None, alias="ReplyTo", description="Email address to set as the reply-to destination. Must be a valid email format if provided."),
    tag: str | None = Field(None, alias="Tag", description="Arbitrary label or category tag to organize and filter this email in Postmark analytics and logs."),
    track_links: Literal["None", "HtmlAndText", "HtmlOnly", "TextOnly"] | None = Field(None, alias="TrackLinks", description="Enable click tracking by rewriting links in the email content. Options are: None (no tracking), HtmlAndText (track both HTML and plain text links), HtmlOnly (track HTML links only), or TextOnly (track plain text links only). Defaults to the server's LinkTracking setting if not specified."),
    track_opens: bool | None = Field(None, alias="TrackOpens", description="Whether to track when this email is opened by the recipient. When enabled, Postmark injects a tracking pixel into the email."),
) -> dict[str, Any] | ToolResult:
    """Send an email to one or more recipients using a pre-defined email template. The template can be identified by either its numeric ID or string alias, and dynamic content is populated via the TemplateModel object."""

    # Construct request model with validation
    try:
        _request = _models.PostEmailWithTemplateRequest(
            body=_models.PostEmailWithTemplateRequestBody(attachments=attachments, from_=from_, headers=headers, inline_css=inline_css, reply_to=reply_to, tag=tag, template_alias=template_alias, template_id=template_id, template_model=template_model, to=to, track_links=track_links, track_opens=track_opens)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for send_email_with_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/email/withTemplate"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("send_email_with_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("send_email_with_template", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="send_email_with_template",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Messages API
@mcp.tool()
async def search_messages_inbound(
    count: int = Field(..., description="Number of messages to return per request, between 1 and 500."),
    offset: int = Field(..., description="Number of messages to skip from the beginning of results for pagination."),
    recipient: str | None = Field(None, description="Filter results to messages received by a specific email address."),
    fromemail: str | None = Field(None, description="Filter results to messages sent from a specific email address."),
    subject: str | None = Field(None, description="Filter results to messages with a matching subject line."),
    mailboxhash: str | None = Field(None, description="Filter results to messages associated with a specific mailbox hash identifier."),
    tag: str | None = Field(None, description="Filter results to messages with a specific tag label."),
    status: Literal["blocked", "processed", "queued", "failed", "scheduled"] | None = Field(None, description="Filter results by message processing status: blocked, processed, queued, failed, or scheduled."),
    todate: str | None = Field(None, description="Filter results to messages received on or before this date (format: YYYY-MM-DD)."),
    fromdate: str | None = Field(None, description="Filter results to messages received on or after this date (format: YYYY-MM-DD)."),
) -> dict[str, Any] | ToolResult:
    """Search and retrieve inbound messages with filtering by recipient, sender, subject, status, date range, and other metadata. Results are paginated using count and offset parameters."""

    # Construct request model with validation
    try:
        _request = _models.GetMessagesInboundRequest(
            query=_models.GetMessagesInboundRequestQuery(count=count, offset=offset, recipient=recipient, fromemail=fromemail, subject=subject, mailboxhash=mailboxhash, tag=tag, status=status, todate=todate, fromdate=fromdate)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_messages_inbound: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/messages/inbound"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_messages_inbound")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_messages_inbound", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_messages_inbound",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Messages API
@mcp.tool()
async def bypass_inbound_message_rules(messageid: str = Field(..., description="The unique identifier of the inbound message that should be exempted from rule filtering.")) -> dict[str, Any] | ToolResult:
    """Allow a blocked inbound message to bypass email filtering rules. Use this to whitelist or recover messages that were incorrectly filtered by the server's inbound rules."""

    # Construct request model with validation
    try:
        _request = _models.PutMessagesInboundBypassRequest(
            path=_models.PutMessagesInboundBypassRequestPath(messageid=messageid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for bypass_inbound_message_rules: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/messages/inbound/{messageid}/bypass", _request.path.model_dump(by_alias=True)) if _request.path else "/messages/inbound/{messageid}/bypass"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("bypass_inbound_message_rules")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("bypass_inbound_message_rules", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="bypass_inbound_message_rules",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Messages API
@mcp.tool()
async def get_inbound_message_details(messageid: str = Field(..., description="The unique identifier of the inbound message whose details you want to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific inbound message, including its content, metadata, and delivery status."""

    # Construct request model with validation
    try:
        _request = _models.GetMessagesInboundDetailsRequest(
            path=_models.GetMessagesInboundDetailsRequestPath(messageid=messageid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_inbound_message_details: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/messages/inbound/{messageid}/details", _request.path.model_dump(by_alias=True)) if _request.path else "/messages/inbound/{messageid}/details"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_inbound_message_details")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_inbound_message_details", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_inbound_message_details",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Messages API
@mcp.tool()
async def retry_inbound_message(messageid: str = Field(..., description="The unique identifier of the inbound message to retry. This should be the message ID returned from the inbound message service.")) -> dict[str, Any] | ToolResult:
    """Retry processing of a previously failed inbound message. Use this operation to reprocess a message that encountered an error during initial delivery or processing."""

    # Construct request model with validation
    try:
        _request = _models.PutMessagesInboundRetryRequest(
            path=_models.PutMessagesInboundRetryRequestPath(messageid=messageid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for retry_inbound_message: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/messages/inbound/{messageid}/retry", _request.path.model_dump(by_alias=True)) if _request.path else "/messages/inbound/{messageid}/retry"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("retry_inbound_message")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("retry_inbound_message", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="retry_inbound_message",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Messages API
@mcp.tool()
async def search_messages_outbound(
    count: int = Field(..., description="Number of messages to return per request, between 1 and 500."),
    offset: int = Field(..., description="Number of messages to skip from the beginning of results for pagination."),
    recipient: str | None = Field(None, description="Filter results to messages received by a specific email address."),
    fromemail: str | None = Field(None, description="Filter results to messages sent from a specific email address."),
    tag: str | None = Field(None, description="Filter results to messages with a specific tag."),
    status: Literal["queued", "sent"] | None = Field(None, description="Filter results by message status: either queued (pending delivery) or sent (successfully delivered)."),
    todate: str | None = Field(None, description="Filter results to messages sent on or before this date (ISO 8601 format, e.g., 2014-02-01)."),
    fromdate: str | None = Field(None, description="Filter results to messages sent on or after this date (ISO 8601 format, e.g., 2014-02-01)."),
) -> dict[str, Any] | ToolResult:
    """Search and retrieve outbound messages with filtering by recipient, sender, status, date range, and tags. Results are paginated using count and offset parameters."""

    # Construct request model with validation
    try:
        _request = _models.GetMessagesOutboundRequest(
            query=_models.GetMessagesOutboundRequestQuery(count=count, offset=offset, recipient=recipient, fromemail=fromemail, tag=tag, status=status, todate=todate, fromdate=fromdate)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_messages_outbound: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/messages/outbound"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_messages_outbound")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_messages_outbound", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_messages_outbound",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Messages API
@mcp.tool()
async def list_outbound_message_clicks(
    count: int = Field(..., description="Number of click records to return per request, up to a maximum of 500 results."),
    offset: int = Field(..., description="Number of click records to skip before returning results, used for pagination."),
    recipient: str | None = Field(None, description="Filter results by recipient email address (To, Cc, or Bcc field)."),
    tag: str | None = Field(None, description="Filter results by message tag or label."),
    client_company: str | None = Field(None, description="Filter results by email client company name (e.g., Microsoft, Apple, Google)."),
    client_family: str | None = Field(None, description="Filter results by email client family or product line (e.g., OS X, Chrome)."),
    os_family: str | None = Field(None, description="Filter results by operating system family without version specificity (e.g., OS X, Windows)."),
    platform: str | None = Field(None, description="Filter results by device platform type (e.g., webmail, desktop, mobile)."),
    country: str | None = Field(None, description="Filter results by country where the message was clicked."),
    city: str | None = Field(None, description="Filter results by city or region name where the message was clicked."),
) -> dict[str, Any] | ToolResult:
    """Retrieve click events from outbound messages with pagination and optional filtering by recipient, tags, client details, device information, and geographic location."""

    # Construct request model with validation
    try:
        _request = _models.GetMessagesOutboundClicksRequest(
            query=_models.GetMessagesOutboundClicksRequestQuery(count=count, offset=offset, recipient=recipient, tag=tag, client_company=client_company, client_family=client_family, os_family=os_family, platform=platform, country=country, city=city)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_outbound_message_clicks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/messages/outbound/clicks"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_outbound_message_clicks")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_outbound_message_clicks", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_outbound_message_clicks",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Messages API
@mcp.tool()
async def list_message_outbound_clicks(
    messageid: str = Field(..., description="The unique identifier of the outbound message for which to retrieve click statistics."),
    count: int = Field(..., description="The number of click records to return per request, between 1 and 500 clicks.", ge=1, le=500),
    offset: int = Field(..., description="The number of click records to skip before returning results, used for pagination. Must be zero or greater.", ge=0),
) -> dict[str, Any] | ToolResult:
    """Retrieve click statistics for a specific outbound message, including details about each click event with pagination support."""

    # Construct request model with validation
    try:
        _request = _models.GetMessagesOutboundClicksByMessageidRequest(
            path=_models.GetMessagesOutboundClicksByMessageidRequestPath(messageid=messageid),
            query=_models.GetMessagesOutboundClicksByMessageidRequestQuery(count=count, offset=offset)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_message_outbound_clicks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/messages/outbound/clicks/{messageid}", _request.path.model_dump(by_alias=True)) if _request.path else "/messages/outbound/clicks/{messageid}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_message_outbound_clicks")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_message_outbound_clicks", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_message_outbound_clicks",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Messages API
@mcp.tool()
async def list_message_opens(
    count: int = Field(..., description="Number of open events to return per request, between 1 and 500."),
    offset: int = Field(..., description="Number of open events to skip before returning results, used for pagination."),
    recipient: str | None = Field(None, description="Filter results by recipient email address (To, Cc, or Bcc field)."),
    tag: str | None = Field(None, description="Filter results by message tag."),
    client_company: str | None = Field(None, description="Filter results by client company name (e.g., Microsoft, Apple, Google)."),
    client_family: str | None = Field(None, description="Filter results by client family (e.g., OS X, Chrome)."),
    os_family: str | None = Field(None, description="Filter results by operating system family without version specificity (e.g., OS X, Windows)."),
    platform: str | None = Field(None, description="Filter results by platform type where the message was opened (e.g., webmail, desktop, mobile)."),
    country: str | None = Field(None, description="Filter results by country where the message was opened (e.g., Denmark, Russia)."),
    city: str | None = Field(None, description="Filter results by city or region name where the message was opened (e.g., Moscow, New York)."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of message open events across all messages, with optional filtering by recipient, tags, client details, location, and platform."""

    # Construct request model with validation
    try:
        _request = _models.GetMessagesOutboundOpensRequest(
            query=_models.GetMessagesOutboundOpensRequestQuery(count=count, offset=offset, recipient=recipient, tag=tag, client_company=client_company, client_family=client_family, os_family=os_family, platform=platform, country=country, city=city)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_message_opens: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/messages/outbound/opens"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_message_opens")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_message_opens", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_message_opens",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Messages API
@mcp.tool()
async def get_message_opens_by_id(
    messageid: str = Field(..., description="The unique identifier of the outbound message for which to retrieve open statistics."),
    count: int = Field(..., description="The number of open records to return in this request. Must be between 1 and 500 (defaults to 1).", ge=1, le=500),
    offset: int = Field(..., description="The number of open records to skip before returning results, used for pagination. Must be 0 or greater (defaults to 0).", ge=0),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of open events for a specific outbound message. Use offset and count parameters to navigate through the results."""

    # Construct request model with validation
    try:
        _request = _models.GetMessagesOutboundOpensByMessageidRequest(
            path=_models.GetMessagesOutboundOpensByMessageidRequestPath(messageid=messageid),
            query=_models.GetMessagesOutboundOpensByMessageidRequestQuery(count=count, offset=offset)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_message_opens_by_id: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/messages/outbound/opens/{messageid}", _request.path.model_dump(by_alias=True)) if _request.path else "/messages/outbound/opens/{messageid}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_message_opens_by_id")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_message_opens_by_id", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_message_opens_by_id",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Messages API
@mcp.tool()
async def get_outbound_message_details(messageid: str = Field(..., description="The unique identifier of the outbound message whose details you want to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific outbound message, including delivery status, recipient information, and message content."""

    # Construct request model with validation
    try:
        _request = _models.GetMessagesOutboundDetailsRequest(
            path=_models.GetMessagesOutboundDetailsRequestPath(messageid=messageid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_outbound_message_details: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/messages/outbound/{messageid}/details", _request.path.model_dump(by_alias=True)) if _request.path else "/messages/outbound/{messageid}/details"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_outbound_message_details")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_outbound_message_details", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_outbound_message_details",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Messages API
@mcp.tool()
async def get_outbound_message_dump(messageid: str = Field(..., description="The unique identifier of the outbound message for which to retrieve the complete dump data.")) -> dict[str, Any] | ToolResult:
    """Retrieve the full dump of an outbound message, including all metadata and content details. This operation requires authentication via a Postmark server token."""

    # Construct request model with validation
    try:
        _request = _models.GetMessagesOutboundDumpRequest(
            path=_models.GetMessagesOutboundDumpRequestPath(messageid=messageid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_outbound_message_dump: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/messages/outbound/{messageid}/dump", _request.path.model_dump(by_alias=True)) if _request.path else "/messages/outbound/{messageid}/dump"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_outbound_message_dump")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_outbound_message_dump", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_outbound_message_dump",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Server Configuration API
@mcp.tool()
async def get_server_configuration() -> dict[str, Any] | ToolResult:
    """Retrieve the configuration and settings for the authenticated Postmark server, including delivery settings, bounce handling, and other server-level configurations."""

    # Extract parameters for API call
    _http_path = "/server"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_server_configuration")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_server_configuration", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_server_configuration",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Stats API
@mcp.tool()
async def get_outbound_stats(
    tag: str | None = Field(None, description="Filter statistics to a specific tag, useful for segmenting results by campaign, sender, or other classification."),
    fromdate: str | None = Field(None, description="Start date for the statistics range in ISO 8601 format (YYYY-MM-DD). Results will include data from this date onward."),
    todate: str | None = Field(None, description="End date for the statistics range in ISO 8601 format (YYYY-MM-DD). Results will include data up to and including this date."),
) -> dict[str, Any] | ToolResult:
    """Retrieve outbound email statistics and performance overview. Optionally filter results by tag and date range to analyze specific sending campaigns or time periods."""

    # Construct request model with validation
    try:
        _request = _models.GetStatsOutboundRequest(
            query=_models.GetStatsOutboundRequestQuery(tag=tag, fromdate=fromdate, todate=todate)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_outbound_stats: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/stats/outbound"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_outbound_stats")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_outbound_stats", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_outbound_stats",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Stats API
@mcp.tool()
async def get_outbound_bounce_statistics(
    tag: str | None = Field(None, description="Filter bounce statistics to a specific tag associated with your emails."),
    fromdate: str | None = Field(None, description="Filter statistics to include data starting from this date (inclusive). Specify in ISO 8601 date format (YYYY-MM-DD)."),
    todate: str | None = Field(None, description="Filter statistics to include data up to this date (inclusive). Specify in ISO 8601 date format (YYYY-MM-DD)."),
) -> dict[str, Any] | ToolResult:
    """Retrieve bounce statistics for outbound emails, with optional filtering by tag and date range to analyze delivery failures."""

    # Construct request model with validation
    try:
        _request = _models.GetStatsOutboundBouncesRequest(
            query=_models.GetStatsOutboundBouncesRequestQuery(tag=tag, fromdate=fromdate, todate=todate)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_outbound_bounce_statistics: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/stats/outbound/bounces"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_outbound_bounce_statistics")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_outbound_bounce_statistics", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_outbound_bounce_statistics",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Stats API
@mcp.tool()
async def get_outbound_click_stats(
    tag: str | None = Field(None, description="Filter statistics to only include clicks associated with a specific tag."),
    fromdate: str | None = Field(None, description="Filter statistics to include only clicks from this date forward (inclusive). Specify as a calendar date in YYYY-MM-DD format."),
    todate: str | None = Field(None, description="Filter statistics to include only clicks up to this date (inclusive). Specify as a calendar date in YYYY-MM-DD format."),
) -> dict[str, Any] | ToolResult:
    """Retrieve click count statistics for outbound links, with optional filtering by tag and date range to analyze link performance over time."""

    # Construct request model with validation
    try:
        _request = _models.GetStatsOutboundClicksRequest(
            query=_models.GetStatsOutboundClicksRequestQuery(tag=tag, fromdate=fromdate, todate=todate)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_outbound_click_stats: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/stats/outbound/clicks"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_outbound_click_stats")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_outbound_click_stats", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_outbound_click_stats",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Stats API
@mcp.tool()
async def get_outbound_clicks_by_location(
    tag: str | None = Field(None, description="Filter results to include only clicks from messages tagged with this value."),
    fromdate: str | None = Field(None, description="Include statistics starting from this date (inclusive). Specify in ISO 8601 date format (YYYY-MM-DD)."),
    todate: str | None = Field(None, description="Include statistics up to this date (inclusive). Specify in ISO 8601 date format (YYYY-MM-DD)."),
) -> dict[str, Any] | ToolResult:
    """Retrieve click statistics for outbound links aggregated by body location. Use optional filters to narrow results by tag and date range."""

    # Construct request model with validation
    try:
        _request = _models.GetStatsOutboundClicksLocationRequest(
            query=_models.GetStatsOutboundClicksLocationRequestQuery(tag=tag, fromdate=fromdate, todate=todate)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_outbound_clicks_by_location: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/stats/outbound/clicks/location"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_outbound_clicks_by_location")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_outbound_clicks_by_location", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_outbound_clicks_by_location",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Stats API
@mcp.tool()
async def list_outbound_click_stats_by_platform(
    tag: str | None = Field(None, description="Filter results to include only clicks associated with a specific tag."),
    fromdate: str | None = Field(None, description="Filter results to include only statistics from this date forward, specified in ISO 8601 format (YYYY-MM-DD)."),
    todate: str | None = Field(None, description="Filter results to include only statistics up to and including this date, specified in ISO 8601 format (YYYY-MM-DD)."),
) -> dict[str, Any] | ToolResult:
    """Retrieve outbound click statistics aggregated by browser platform. Use optional filters to narrow results by tag and date range."""

    # Construct request model with validation
    try:
        _request = _models.GetStatsOutboundClicksPlatformsRequest(
            query=_models.GetStatsOutboundClicksPlatformsRequestQuery(tag=tag, fromdate=fromdate, todate=todate)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_outbound_click_stats_by_platform: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/stats/outbound/clicks/platforms"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_outbound_click_stats_by_platform")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_outbound_click_stats_by_platform", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_outbound_click_stats_by_platform",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Stats API
@mcp.tool()
async def get_outbound_email_opens(
    tag: str | None = Field(None, description="Filter results to only include statistics for messages tagged with this value."),
    fromdate: str | None = Field(None, description="Filter statistics to include only data from this date forward, specified in ISO 8601 date format (YYYY-MM-DD)."),
    todate: str | None = Field(None, description="Filter statistics to include only data up to and including this date, specified in ISO 8601 date format (YYYY-MM-DD)."),
) -> dict[str, Any] | ToolResult:
    """Retrieve email open statistics for outbound messages, with optional filtering by tag and date range to analyze engagement metrics."""

    # Construct request model with validation
    try:
        _request = _models.GetStatsOutboundOpensRequest(
            query=_models.GetStatsOutboundOpensRequestQuery(tag=tag, fromdate=fromdate, todate=todate)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_outbound_email_opens: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/stats/outbound/opens"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_outbound_email_opens")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_outbound_email_opens", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_outbound_email_opens",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Stats API
@mcp.tool()
async def list_outbound_email_opens_by_client(
    tag: str | None = Field(None, description="Filter results to only include opens from messages tagged with this value."),
    fromdate: str | None = Field(None, description="Include opens starting from this date (inclusive). Specify in ISO 8601 date format (YYYY-MM-DD)."),
    todate: str | None = Field(None, description="Include opens up to this date (inclusive). Specify in ISO 8601 date format (YYYY-MM-DD)."),
) -> dict[str, Any] | ToolResult:
    """Retrieve email client statistics for outbound message opens, optionally filtered by tag and date range. Use this to analyze which email clients your recipients use when opening messages."""

    # Construct request model with validation
    try:
        _request = _models.GetStatsOutboundOpensEmailclientsRequest(
            query=_models.GetStatsOutboundOpensEmailclientsRequestQuery(tag=tag, fromdate=fromdate, todate=todate)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_outbound_email_opens_by_client: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/stats/outbound/opens/emailclients"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_outbound_email_opens_by_client")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_outbound_email_opens_by_client", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_outbound_email_opens_by_client",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Stats API
@mcp.tool()
async def list_email_opens_by_platform(
    tag: str | None = Field(None, description="Filter statistics to only include opens from messages tagged with this value."),
    fromdate: str | None = Field(None, description="Include statistics starting from this date (inclusive). Specify in ISO 8601 date format (YYYY-MM-DD)."),
    todate: str | None = Field(None, description="Include statistics up to this date (inclusive). Specify in ISO 8601 date format (YYYY-MM-DD)."),
) -> dict[str, Any] | ToolResult:
    """Retrieve email open statistics aggregated by email client platform. Filter results by tag and date range to analyze which platforms your recipients use to open emails."""

    # Construct request model with validation
    try:
        _request = _models.GetStatsOutboundOpensPlatformsRequest(
            query=_models.GetStatsOutboundOpensPlatformsRequestQuery(tag=tag, fromdate=fromdate, todate=todate)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_email_opens_by_platform: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/stats/outbound/opens/platforms"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_email_opens_by_platform")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_email_opens_by_platform", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_email_opens_by_platform",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Stats API
@mcp.tool()
async def get_outbound_send_stats(
    tag: str | None = Field(None, description="Filter results to only include statistics for messages with this specific tag."),
    fromdate: str | None = Field(None, description="Filter statistics to include only data from this date forward, specified in ISO 8601 date format (YYYY-MM-DD)."),
    todate: str | None = Field(None, description="Filter statistics to include only data up to and including this date, specified in ISO 8601 date format (YYYY-MM-DD)."),
) -> dict[str, Any] | ToolResult:
    """Retrieve statistics on sent messages, with optional filtering by tag and date range. Use this to analyze outbound sending activity over time."""

    # Construct request model with validation
    try:
        _request = _models.GetStatsOutboundSendsRequest(
            query=_models.GetStatsOutboundSendsRequestQuery(tag=tag, fromdate=fromdate, todate=todate)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_outbound_send_stats: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/stats/outbound/sends"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_outbound_send_stats")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_outbound_send_stats", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_outbound_send_stats",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Stats API
@mcp.tool()
async def get_outbound_spam_stats(
    tag: str | None = Field(None, description="Filter statistics by a specific tag to isolate metrics for tagged message groups."),
    fromdate: str | None = Field(None, description="Start date for the statistics query in ISO 8601 format (YYYY-MM-DD). Results will include data from this date onward."),
    todate: str | None = Field(None, description="End date for the statistics query in ISO 8601 format (YYYY-MM-DD). Results will include data up to and including this date."),
) -> dict[str, Any] | ToolResult:
    """Retrieve spam complaint statistics for outbound messages. Filter results by tag and date range to analyze spam performance metrics."""

    # Construct request model with validation
    try:
        _request = _models.GetStatsOutboundSpamRequest(
            query=_models.GetStatsOutboundSpamRequestQuery(tag=tag, fromdate=fromdate, todate=todate)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_outbound_spam_stats: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/stats/outbound/spam"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_outbound_spam_stats")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_outbound_spam_stats", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_outbound_spam_stats",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Stats API
@mcp.tool()
async def get_outbound_tracked_email_stats(
    tag: str | None = Field(None, description="Filter results to only include emails associated with this specific tag."),
    fromdate: str | None = Field(None, description="Start date for the stats query in ISO 8601 format (YYYY-MM-DD). Only emails sent on or after this date will be included."),
    todate: str | None = Field(None, description="End date for the stats query in ISO 8601 format (YYYY-MM-DD). Only emails sent on or before this date will be included."),
) -> dict[str, Any] | ToolResult:
    """Retrieve counts of tracked outbound emails, with optional filtering by tag and date range. Use this to monitor email delivery metrics for a specific time period or tag."""

    # Construct request model with validation
    try:
        _request = _models.GetStatsOutboundTrackedRequest(
            query=_models.GetStatsOutboundTrackedRequestQuery(tag=tag, fromdate=fromdate, todate=todate)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_outbound_tracked_email_stats: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/stats/outbound/tracked"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_outbound_tracked_email_stats")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_outbound_tracked_email_stats", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_outbound_tracked_email_stats",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Templates API
@mcp.tool()
async def list_templates(
    count: int = Field(..., alias="Count", description="The maximum number of templates to return in this request. Must be a positive integer."),
    offset: int = Field(..., alias="Offset", description="The number of templates to skip before returning results, enabling pagination through your template collection. Must be a non-negative integer."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of email templates associated with this Postmark server. Use Count and Offset parameters to control pagination through your template collection."""

    # Construct request model with validation
    try:
        _request = _models.GetTemplatesRequest(
            query=_models.GetTemplatesRequestQuery(count=count, offset=offset)
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

# Tags: Templates API
@mcp.tool()
async def create_template(
    name: str = Field(..., alias="Name", description="Human-readable name for the template displayed in the Postmark dashboard and API responses."),
    subject: str = Field(..., alias="Subject", description="Template definition for the email subject line. Supports template variables and dynamic content using Postmark's templating syntax."),
    alias: str | None = Field(None, alias="Alias", description="Optional unique identifier for this template using alphanumeric characters, dots, hyphens, and underscores. Must start with a letter. Useful for programmatic template references."),
    text_body: str | None = Field(None, alias="TextBody", description="The Text template definition for this Template."),
    html_body: str | None = Field(None, alias="HtmlBody", description="The HTML template definition for this Template."),
) -> dict[str, Any] | ToolResult:
    """Create a new email template with a subject line and optional alias for easy reference. Templates can be used to standardize email content across your application."""

    # Construct request model with validation
    try:
        _request = _models.PostTemplatesRequest(
            body=_models.PostTemplatesRequestBody(alias=alias, name=name, subject=subject, text_body=text_body, html_body=html_body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/templates"
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

# Tags: Templates API
@mcp.tool()
async def validate_template(
    inline_css_for_html_test_render: bool | None = Field(None, alias="InlineCssForHtmlTestRender", description="When validating HTML content, controls whether CSS style blocks are inlined as style attributes on matching elements. Defaults to true; set to false to disable CSS inlining."),
    subject: str | None = Field(None, alias="Subject", description="The subject line template content to validate using Postmark's template language syntax. Required if neither HtmlBody nor TextBody is provided."),
    test_render_model: dict[str, Any] | None = Field(None, alias="TestRenderModel", description="A data object used to render and test the template content, allowing validation of dynamic variable substitution and template logic."),
) -> dict[str, Any] | ToolResult:
    """Validate template content by testing subject lines, HTML, and text body rendering with optional CSS inlining and a test data model."""

    # Construct request model with validation
    try:
        _request = _models.PostTemplatesValidateRequest(
            body=_models.PostTemplatesValidateRequestBody(inline_css_for_html_test_render=inline_css_for_html_test_render, subject=subject, test_render_model=test_render_model)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for validate_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/templates/validate"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("validate_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("validate_template", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="validate_template",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Templates API
@mcp.tool()
async def get_template(template_id_or_alias: str = Field(..., alias="templateIdOrAlias", description="The unique identifier or alias of the template to retrieve. You can use either the TemplateID (numeric identifier) or the Alias (custom name) to look up the template.")) -> dict[str, Any] | ToolResult:
    """Retrieve a specific email template by its unique identifier or alias. Use this to fetch template details for rendering, previewing, or managing email communications."""

    # Construct request model with validation
    try:
        _request = _models.GetTemplatesByTemplateIdOrAliasRequest(
            path=_models.GetTemplatesByTemplateIdOrAliasRequestPath(template_id_or_alias=template_id_or_alias)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/templates/{templateIdOrAlias}", _request.path.model_dump(by_alias=True)) if _request.path else "/templates/{templateIdOrAlias}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_template", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_template",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Templates API
@mcp.tool()
async def update_template(
    template_id_or_alias: str = Field(..., alias="templateIdOrAlias", description="The unique identifier or alias of the template to update. Use either the numeric TemplateID or the string Alias value."),
    alias: str | None = Field(None, alias="Alias", description="Optional string identifier for the template using letters, numbers, and the characters '.', '-', '_'. Must start with a letter."),
    name: str | None = Field(None, alias="Name", description="Optional human-readable name for the template displayed in the UI."),
    subject: str | None = Field(None, alias="Subject", description="Optional subject line template definition that supports variable substitution for dynamic email subjects."),
) -> dict[str, Any] | ToolResult:
    """Update an existing email template by its ID or alias. Modify the template's name, subject line, or alias identifier."""

    # Construct request model with validation
    try:
        _request = _models.PutTemplatesRequest(
            path=_models.PutTemplatesRequestPath(template_id_or_alias=template_id_or_alias),
            body=_models.PutTemplatesRequestBody(alias=alias, name=name, subject=subject)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/templates/{templateIdOrAlias}", _request.path.model_dump(by_alias=True)) if _request.path else "/templates/{templateIdOrAlias}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_template", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_template",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Templates API
@mcp.tool()
async def delete_template(template_id_or_alias: str = Field(..., alias="templateIdOrAlias", description="The unique identifier or alias of the template to delete. You can use either the TemplateID or the Alias value.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a template by its ID or alias. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteTemplatesRequest(
            path=_models.DeleteTemplatesRequestPath(template_id_or_alias=template_id_or_alias)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/templates/{templateIdOrAlias}", _request.path.model_dump(by_alias=True)) if _request.path else "/templates/{templateIdOrAlias}"
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

# Tags: Inbound Rules API
@mcp.tool()
async def list_inbound_rule_triggers(
    count: int = Field(..., description="The maximum number of trigger records to return in this request. Must be a positive integer."),
    offset: int = Field(..., description="The number of records to skip before returning results, enabling pagination through large result sets. Must be a non-negative integer."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of inbound rule triggers configured for the server. Use count and offset parameters to control pagination through the results."""

    # Construct request model with validation
    try:
        _request = _models.GetTriggersInboundrulesRequest(
            query=_models.GetTriggersInboundrulesRequestQuery(count=count, offset=offset)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_inbound_rule_triggers: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/triggers/inboundrules"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_inbound_rule_triggers")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_inbound_rule_triggers", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_inbound_rule_triggers",
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
        print("  python postmark_server.py", file=sys.stderr)
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

    parser = argparse.ArgumentParser(description="Postmark MCP Server")

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
    logger.info("Starting Postmark MCP Server")
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

#!/usr/bin/env python3
"""
Canva MCP Server

API Info:
- API License: ©2023 All Rights Reserved
- Contact: Canva Developer Community (https://community.canva.dev/)
- Terms of Service: https://www.canva.com/trust/legal/

Generated: 2026-04-14 18:17:01 UTC
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
from pydantic import Field

BASE_URL = os.getenv("BASE_URL", "https://api.canva.com/rest")
SERVER_NAME = "Canva"
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

def _encode_content_params(params: dict[str, Any], encodings: dict[str, str]) -> dict[str, Any]:
    """Serialize content-encoded params per OAS Parameter Object content property."""
    import json as _json_mod
    result = dict(params)
    for key, encoding in encodings.items():
        if key in result and result[key] is not None and (encoding == "application/json" or encoding.endswith("+json")):
            result[key] = _json_mod.dumps(result[key])
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
    'oauthAuthCode',
    'basicAuth',
]

# Initialize authentication handlers at server startup
_auth_handlers: dict[str, Any] = {}
try:
    _auth_handlers["oauthAuthCode"] = _auth.OAuth2Auth()
    logging.info("Authentication configured: oauthAuthCode")
except ValueError as e:
    # Extract credential names from error message (first sentence before "Leave empty")
    error_msg = str(e).split("Leave empty")[0].strip()
    logging.warning(f"Credentials for oauthAuthCode not configured: {error_msg}")
    _auth_handlers["oauthAuthCode"] = None
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

mcp = FastMCP("Canva", middleware=[_JsonCoercionMiddleware()])

# Tags: asset
@mcp.tool()
async def get_asset(asset_id: str = Field(..., alias="assetId", description="The unique identifier of the asset to retrieve. Must be alphanumeric with hyphens and underscores allowed.", pattern="^[a-zA-Z0-9_-]{1,50}$")) -> dict[str, Any]:
    """Retrieve detailed metadata for a specific asset by its unique identifier. Use this operation to fetch asset information such as properties, status, and configuration details."""

    # Construct request model with validation
    try:
        _request = _models.GetAssetRequest(
            path=_models.GetAssetRequestPath(asset_id=asset_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_asset: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/assets/{assetId}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/assets/{assetId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_asset")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_asset", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_asset",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: asset
@mcp.tool()
async def update_asset(
    asset_id: str = Field(..., alias="assetId", description="The unique identifier of the asset to update. Must be alphanumeric with hyphens and underscores.", pattern="^[a-zA-Z0-9_-]{1,50}$"),
    name: str | None = Field(None, description="The new name for the asset as displayed in the Canva UI. Leave undefined or empty to skip updating the name.", max_length=50),
    tags: list[str] | None = Field(None, description="Replacement tags for the asset. All existing tags are replaced when provided. Leave undefined to skip updating tags.", max_length=50),
) -> dict[str, Any]:
    """Update an asset's name and tags by asset ID. Tags are replaced entirely when provided, allowing you to manage asset metadata in the Canva UI."""

    # Construct request model with validation
    try:
        _request = _models.UpdateAssetRequest(
            path=_models.UpdateAssetRequestPath(asset_id=asset_id),
            body=_models.UpdateAssetRequestBody(name=name, tags=tags)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_asset: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/assets/{assetId}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/assets/{assetId}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_asset")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_asset", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_asset",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: asset
@mcp.tool()
async def delete_asset(asset_id: str = Field(..., alias="assetId", description="The unique identifier of the asset to delete.", pattern="^[a-zA-Z0-9_-]{1,50}$")) -> dict[str, Any]:
    """Delete an asset by its ID, moving it to trash. This mirrors the Canva UI behavior and does not remove the asset from designs that already use it."""

    # Construct request model with validation
    try:
        _request = _models.DeleteAssetRequest(
            path=_models.DeleteAssetRequestPath(asset_id=asset_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_asset: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/assets/{assetId}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/assets/{assetId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_asset")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_asset", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_asset",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: asset
@mcp.tool()
async def upload_asset(
    asset_upload_metadata: _models.CreateAssetUploadJobHeaderAssetUploadMetadata = Field(..., alias="Asset-Upload-Metadata", description="Metadata describing the asset being uploaded, including asset name, type, and other identifying information."),
    body: str = Field(..., description="The raw binary file content to upload as an asset. The file must be in a supported format as documented in the Assets API overview."),
) -> dict[str, Any]:
    """Initiates an asynchronous job to upload an asset file to the user's content library. Use the returned job ID to poll for completion status and retrieve the uploaded asset details."""

    # Construct request model with validation
    try:
        _request = _models.CreateAssetUploadJobRequest(
            header=_models.CreateAssetUploadJobRequestHeader(asset_upload_metadata=asset_upload_metadata),
            body=_models.CreateAssetUploadJobRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for upload_asset: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/asset-uploads"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers = _encode_content_params(_http_headers, {
        "Asset-Upload-Metadata": "application/json",
    })

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("upload_asset")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("upload_asset", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="upload_asset",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: asset
@mcp.tool()
async def get_asset_upload_job(job_id: str = Field(..., alias="jobId", description="The unique identifier of the asset upload job to retrieve status for.", pattern="^[a-zA-Z0-9_-]{1,50}$")) -> dict[str, Any]:
    """Retrieve the status and result of an asset upload job. Use this to poll for completion after creating an upload job, as the operation is asynchronous and may require multiple requests until a success or failed status is returned."""

    # Construct request model with validation
    try:
        _request = _models.GetAssetUploadJobRequest(
            path=_models.GetAssetUploadJobRequestPath(job_id=job_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_asset_upload_job: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/asset-uploads/{jobId}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/asset-uploads/{jobId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_asset_upload_job")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_asset_upload_job", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_asset_upload_job",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: asset
@mcp.tool()
async def initiate_url_asset_upload(
    name: str = Field(..., description="A descriptive name for the asset being uploaded. Must be between 1 and 255 characters.", min_length=1, max_length=255),
    url: str = Field(..., description="The publicly accessible URL of the file to import. The URL must be reachable from the internet and support direct file access. Must be between 8 and 2048 characters.", min_length=8, max_length=2048),
) -> dict[str, Any]:
    """Starts an asynchronous job to upload an asset from a publicly accessible URL to the user's content library. Supported file types are documented in the Assets API overview, with video assets limited to 100MB maximum file size."""

    # Construct request model with validation
    try:
        _request = _models.CreateUrlAssetUploadJobRequest(
            body=_models.CreateUrlAssetUploadJobRequestBody(name=name, url=url)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for initiate_url_asset_upload: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/url-asset-uploads"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("initiate_url_asset_upload")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("initiate_url_asset_upload", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="initiate_url_asset_upload",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: asset
@mcp.tool()
async def get_asset_upload_job_from_url(job_id: str = Field(..., alias="jobId", description="The unique identifier of the asset upload job to retrieve status for.", pattern="^[a-zA-Z0-9_-]{1,50}$")) -> dict[str, Any]:
    """Retrieve the status and result of an asset upload job created via URL. Poll this endpoint until the job reaches a terminal state (success or failed)."""

    # Construct request model with validation
    try:
        _request = _models.GetUrlAssetUploadJobRequest(
            path=_models.GetUrlAssetUploadJobRequestPath(job_id=job_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_asset_upload_job_from_url: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/url-asset-uploads/{jobId}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/url-asset-uploads/{jobId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_asset_upload_job_from_url")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_asset_upload_job_from_url", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_asset_upload_job_from_url",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: autofill
@mcp.tool()
async def autofill_design(
    brand_template_id: str = Field(..., description="The ID of the brand template to use for autofilling. Brand template IDs were migrated to a new format in September 2025; old IDs remain supported for 6 months."),
    data: dict[str, _models.DatasetValue] = Field(..., description="Data object containing field names mapped to their values. Supports images (via asset_id), text strings, and chart data with typed rows and cells."),
    title: str | None = Field(None, description="Optional title for the autofilled design. If not provided, the design will use the brand template's title.", min_length=1, max_length=255),
) -> dict[str, Any]:
    """Starts an asynchronous job to autofill a Canva design using a brand template and input data. Requires membership in a Canva Enterprise organization."""

    # Construct request model with validation
    try:
        _request = _models.CreateDesignAutofillJobRequest(
            body=_models.CreateDesignAutofillJobRequestBody(brand_template_id=brand_template_id, title=title, data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for autofill_design: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/autofills"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("autofill_design")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("autofill_design", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="autofill_design",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: autofill
@mcp.tool()
async def get_autofill_job(job_id: str = Field(..., alias="jobId", description="The unique identifier of the design autofill job to retrieve.", pattern="^[a-zA-Z0-9_-]{1,50}$")) -> dict[str, Any]:
    """Retrieve the result of a design autofill job. Poll this endpoint until the job reaches a `success` or `failed` status to get the final result."""

    # Construct request model with validation
    try:
        _request = _models.GetDesignAutofillJobRequest(
            path=_models.GetDesignAutofillJobRequestPath(job_id=job_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_autofill_job: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/autofills/{jobId}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/autofills/{jobId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_autofill_job")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_autofill_job", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_autofill_job",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: brand_template
@mcp.tool()
async def list_brand_templates(
    query: str | None = Field(None, description="Search brand templates by one or more search terms to filter the results."),
    limit: str | None = Field(None, description="The maximum number of brand templates to return in the response."),
    ownership: Literal["any", "owned", "shared"] | None = Field(None, description="Filter brand templates based on the user's ownership relationship to them."),
    sort_by: Literal["relevance", "modified_descending", "modified_ascending", "title_descending", "title_ascending"] | None = Field(None, description="Sort the returned brand templates by relevance, modification date, or title in ascending or descending order."),
    dataset: Literal["any", "non_empty"] | None = Field(None, description="Filter brand templates based on whether they have dataset definitions configured for use with Autofill APIs."),
) -> dict[str, Any]:
    """Retrieve a list of brand templates that the user has access to within their Canva Enterprise organization. Supports searching, filtering by ownership and dataset definitions, and sorting options."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.ListBrandTemplatesRequest(
            query=_models.ListBrandTemplatesRequestQuery(query=query, limit=_limit, ownership=ownership, sort_by=sort_by, dataset=dataset)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_brand_templates: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/brand-templates"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_brand_templates")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_brand_templates", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_brand_templates",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: brand_template
@mcp.tool()
async def get_brand_template(brand_template_id: str = Field(..., alias="brandTemplateId", description="The unique identifier for the brand template. Must be 1-50 characters long and contain only alphanumeric characters, hyphens, or underscores.", pattern="^[a-zA-Z0-9_-]{1,50}$")) -> dict[str, Any]:
    """Retrieves metadata for a brand template. Note: Brand template IDs were migrated to a new format in September 2025; old IDs remain valid for 6 months. Requires the user to be a member of a Canva Enterprise organization."""

    # Construct request model with validation
    try:
        _request = _models.GetBrandTemplateRequest(
            path=_models.GetBrandTemplateRequestPath(brand_template_id=brand_template_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_brand_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/brand-templates/{brandTemplateId}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/brand-templates/{brandTemplateId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_brand_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_brand_template", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_brand_template",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: brand_template
@mcp.tool()
async def get_brand_template_dataset(brand_template_id: str = Field(..., alias="brandTemplateId", description="The unique identifier of the brand template. Brand template IDs were migrated to a new format in September 2025; old IDs remain valid for 6 months.", pattern="^[a-zA-Z0-9_-]{1,50}$")) -> dict[str, Any]:
    """Retrieves the dataset definition for a brand template, including any autofill data fields and their accepted types (images, text, or charts). Use this to understand what data can be populated when creating a design autofill job."""

    # Construct request model with validation
    try:
        _request = _models.GetBrandTemplateDatasetRequest(
            path=_models.GetBrandTemplateDatasetRequestPath(brand_template_id=brand_template_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_brand_template_dataset: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/brand-templates/{brandTemplateId}/dataset", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/brand-templates/{brandTemplateId}/dataset"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_brand_template_dataset")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_brand_template_dataset", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_brand_template_dataset",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: comment
@mcp.tool()
async def list_comment_replies(
    design_id: str = Field(..., alias="designId", description="The unique identifier of the design containing the comment thread.", pattern="^[a-zA-Z0-9_-]{1,50}$"),
    thread_id: str = Field(..., alias="threadId", description="The unique identifier of the comment thread for which to retrieve replies.", pattern="^[a-zA-Z0-9_-]{1,50}$"),
    limit: int | None = Field(None, description="The maximum number of replies to return in the response. Defaults to 50 if not specified.", ge=1, le=100),
) -> dict[str, Any]:
    """Retrieves all replies for a specific comment or suggestion thread on a design. This preview API allows you to access threaded discussions within design comments."""

    # Construct request model with validation
    try:
        _request = _models.ListRepliesRequest(
            path=_models.ListRepliesRequestPath(design_id=design_id, thread_id=thread_id),
            query=_models.ListRepliesRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_comment_replies: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/designs/{designId}/comments/{threadId}/replies", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/designs/{designId}/comments/{threadId}/replies"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_comment_replies")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_comment_replies", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_comment_replies",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: comment
@mcp.tool()
async def create_comment_reply(
    design_id: str = Field(..., alias="designId", description="The unique identifier of the design containing the comment thread.", pattern="^[a-zA-Z0-9_-]{1,50}$"),
    thread_id: str = Field(..., alias="threadId", description="The unique identifier of the comment thread to reply to. This ID is returned when a thread is created or can be obtained from existing replies in the thread.", pattern="^[a-zA-Z0-9_-]{1,50}$"),
    message_plaintext: str = Field(..., description="The reply message in plaintext format. You can mention users by including their User ID and Team ID using the format [user_id:team_id].", min_length=1, max_length=2048),
) -> dict[str, Any]:
    """Creates a reply to a comment or suggestion thread on a design. Each thread supports a maximum of 100 replies, and you can mention users by including their User ID and Team ID in the message."""

    # Construct request model with validation
    try:
        _request = _models.CreateReplyRequest(
            path=_models.CreateReplyRequestPath(design_id=design_id, thread_id=thread_id),
            body=_models.CreateReplyRequestBody(message_plaintext=message_plaintext)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_comment_reply: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/designs/{designId}/comments/{threadId}/replies", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/designs/{designId}/comments/{threadId}/replies"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_comment_reply")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_comment_reply", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_comment_reply",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: comment
@mcp.tool()
async def get_comment_thread(
    design_id: str = Field(..., alias="designId", description="The unique identifier of the design containing the comment thread.", pattern="^[a-zA-Z0-9_-]{1,50}$"),
    thread_id: str = Field(..., alias="threadId", description="The unique identifier of the comment thread to retrieve.", pattern="^[a-zA-Z0-9_-]{1,50}$"),
) -> dict[str, Any]:
    """Retrieves a comment or suggestion thread on a design. Use this to fetch details about a specific comment thread; for replies within a thread, use the get_reply operation instead."""

    # Construct request model with validation
    try:
        _request = _models.GetThreadRequest(
            path=_models.GetThreadRequestPath(design_id=design_id, thread_id=thread_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_comment_thread: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/designs/{designId}/comments/{threadId}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/designs/{designId}/comments/{threadId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_comment_thread")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_comment_thread", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_comment_thread",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: comment
@mcp.tool()
async def get_comment_reply(
    design_id: str = Field(..., alias="designId", description="The unique identifier of the design containing the comment thread.", pattern="^[a-zA-Z0-9_-]{1,50}$"),
    thread_id: str = Field(..., alias="threadId", description="The unique identifier of the comment thread containing the reply.", pattern="^[a-zA-Z0-9_-]{1,50}$"),
    reply_id: str = Field(..., alias="replyId", description="The unique identifier of the specific reply to retrieve.", pattern="^[a-zA-Z0-9_-]{1,50}$"),
) -> dict[str, Any]:
    """Retrieves a specific reply to a comment or suggestion thread on a design. This API is currently in preview and may have unannounced breaking changes."""

    # Construct request model with validation
    try:
        _request = _models.GetReplyRequest(
            path=_models.GetReplyRequestPath(design_id=design_id, thread_id=thread_id, reply_id=reply_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_comment_reply: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/designs/{designId}/comments/{threadId}/replies/{replyId}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/designs/{designId}/comments/{threadId}/replies/{replyId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_comment_reply")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_comment_reply", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_comment_reply",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: comment
@mcp.tool()
async def create_comment(
    design_id: str = Field(..., alias="designId", description="The unique identifier of the design where the comment will be created.", pattern="^[a-zA-Z0-9_-]{1,50}$"),
    message_plaintext: str = Field(..., description="The comment message in plaintext. You can mention users by including their User ID and Team ID in the format [user_id:team_id]. If assigning the comment to a user, you must mention them in this message.", min_length=1, max_length=2048),
    assignee_id: str | None = Field(None, description="Optionally assign the comment to a Canva user by their User ID. The assigned user must be mentioned in the message_plaintext parameter."),
) -> dict[str, Any]:
    """Creates a new comment thread on a design. Comments enable collaboration and feedback within Canva designs, with optional user assignment and mentions."""

    # Construct request model with validation
    try:
        _request = _models.CreateThreadRequest(
            path=_models.CreateThreadRequestPath(design_id=design_id),
            body=_models.CreateThreadRequestBody(message_plaintext=message_plaintext, assignee_id=assignee_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/designs/{designId}/comments", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/designs/{designId}/comments"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_comment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_comment", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_comment",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: design
@mcp.tool()
async def list_designs(
    query: str | None = Field(None, description="Search term or terms to filter designs by title or content. Searches across both user-created and shared designs.", max_length=255),
    ownership: Literal["any", "owned", "shared"] | None = Field(None, description="Filter designs based on ownership status. Use 'owned' for designs created by the user, 'shared' for designs shared with the user, or 'any' to include both."),
    sort_by: Literal["relevance", "modified_descending", "modified_ascending", "title_descending", "title_ascending"] | None = Field(None, description="Sort the returned designs by relevance to search query, modification date, or title in ascending or descending order."),
    limit: str | None = Field(None, description="Maximum number of designs to return in the response. Useful for pagination and controlling response size."),
) -> dict[str, Any]:
    """Retrieve metadata for all designs in a Canva user's projects. Supports filtering by search terms, ownership status, and sorting options to help users find and organize their designs."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.ListDesignsRequest(
            query=_models.ListDesignsRequestQuery(query=query, ownership=ownership, sort_by=sort_by, limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_designs: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/designs"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_designs")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_designs", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_designs",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: design
@mcp.tool()
async def create_design(
    design_type: Annotated[_models.PresetDesignTypeInput | _models.CustomDesignTypeInput, Field(discriminator="type_")] | None = Field(None, description="The preset design type to use for the new design. Either specify a design_type or provide custom height and width dimensions."),
    asset_id: str | None = Field(None, description="The ID of an image asset from the user's projects to insert into the created design. Currently supports image assets only."),
    title: str | None = Field(None, description="The name of the design. Must be between 1 and 255 characters.", min_length=1, max_length=255),
) -> dict[str, Any]:
    """Creates a new Canva design using either a preset design type or custom dimensions. Optionally add an image asset to the design. Note: Blank designs are automatically deleted after 7 days if not edited."""

    # Construct request model with validation
    try:
        _request = _models.CreateDesignRequest(
            body=_models.CreateDesignRequestBody(design_type=design_type, asset_id=asset_id, title=title)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_design: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/designs"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_design")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_design", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_design",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: design
@mcp.tool()
async def get_design(design_id: str = Field(..., alias="designId", description="The unique identifier for the design to retrieve. Must be alphanumeric with hyphens and underscores allowed, between 1 and 50 characters in length.", pattern="^[a-zA-Z0-9_-]{1,50}$")) -> dict[str, Any]:
    """Retrieves comprehensive metadata for a specific design, including owner information, editing and viewing URLs, and thumbnail details."""

    # Construct request model with validation
    try:
        _request = _models.GetDesignRequest(
            path=_models.GetDesignRequestPath(design_id=design_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_design: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/designs/{designId}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/designs/{designId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_design")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_design", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_design",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: design
@mcp.tool()
async def list_design_pages(
    design_id: str = Field(..., alias="designId", description="The unique identifier of the design containing the pages to retrieve.", pattern="^[a-zA-Z0-9_-]{1,50}$"),
    offset: str | None = Field(None, description="The page index to start retrieving from. Pages use one-based numbering, where the first page has index 1."),
    limit: str | None = Field(None, description="The maximum number of pages to return in this request, starting from the offset index."),
) -> dict[str, Any]:
    """Retrieves metadata for pages in a design, including page-specific thumbnails. Use offset and limit parameters to paginate through pages. Note: Some design types (such as Canva docs) do not have pages."""

    _offset = _parse_int(offset)
    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetDesignPagesRequest(
            path=_models.GetDesignPagesRequestPath(design_id=design_id),
            query=_models.GetDesignPagesRequestQuery(offset=_offset, limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_design_pages: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/designs/{designId}/pages", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/designs/{designId}/pages"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_design_pages")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_design_pages", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_design_pages",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: design
@mcp.tool()
async def list_design_export_formats(design_id: str = Field(..., alias="designId", description="The unique identifier of the design whose export formats you want to retrieve.", pattern="^[a-zA-Z0-9_-]{1,50}$")) -> dict[str, Any]:
    """Retrieves the available file formats for exporting a design. The returned formats depend on the design type and page types within the design, showing only formats supported by all pages."""

    # Construct request model with validation
    try:
        _request = _models.GetDesignExportFormatsRequest(
            path=_models.GetDesignExportFormatsRequestPath(design_id=design_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_design_export_formats: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/designs/{designId}/export-formats", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/designs/{designId}/export-formats"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_design_export_formats")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_design_export_formats", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_design_export_formats",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: design_import
@mcp.tool()
async def import_design(
    import_metadata: _models.CreateDesignImportJobHeaderImportMetadata = Field(..., alias="Import-Metadata", description="Metadata describing the design being imported, including details about the source file and import configuration. Provided as an HTTP header parameter."),
    body: str = Field(..., description="The binary file content to import as a design. The file must be in a supported format for design imports."),
) -> dict[str, Any]:
    """Initiates an asynchronous job to import an external file as a new design in Canva. Supported file types include various design formats; use the Get design import job API to check job status and retrieve results."""

    # Construct request model with validation
    try:
        _request = _models.CreateDesignImportJobRequest(
            header=_models.CreateDesignImportJobRequestHeader(import_metadata=import_metadata),
            body=_models.CreateDesignImportJobRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for import_design: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/imports"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers = _encode_content_params(_http_headers, {
        "Import-Metadata": "application/json",
    })

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("import_design")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("import_design", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="import_design",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: design_import
@mcp.tool()
async def get_design_import_job(job_id: str = Field(..., alias="jobId", description="The unique identifier of the design import job to retrieve status for.", pattern="^[a-zA-Z0-9_-]{1,50}$")) -> dict[str, Any]:
    """Retrieves the status and result of a design import job. Use this to poll for completion after creating an import job, as the operation is asynchronous and may require multiple requests until a success or failed status is returned."""

    # Construct request model with validation
    try:
        _request = _models.GetDesignImportJobRequest(
            path=_models.GetDesignImportJobRequestPath(job_id=job_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_design_import_job: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/imports/{jobId}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/imports/{jobId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_design_import_job")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_design_import_job", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_design_import_job",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: design_import
@mcp.tool()
async def import_design_from_url(
    title: str = Field(..., description="The title for the imported design. Must be between 1 and 255 characters.", min_length=1, max_length=255),
    url: str = Field(..., description="The publicly accessible URL of the file to import. The URL must be reachable from the internet and support direct file access.", min_length=1, max_length=2048),
    mime_type: str | None = Field(None, description="The MIME type of the file being imported. If omitted, Canva will automatically detect the file type. Useful for improving import speed when the file type is known.", min_length=1, max_length=100),
) -> dict[str, Any]:
    """Starts an asynchronous job to import an external file from a URL as a new design in Canva. Supports multiple file types and allows optional MIME type specification for faster processing."""

    # Construct request model with validation
    try:
        _request = _models.CreateUrlImportJobRequest(
            body=_models.CreateUrlImportJobRequestBody(title=title, url=url, mime_type=mime_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for import_design_from_url: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/url-imports"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("import_design_from_url")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("import_design_from_url", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="import_design_from_url",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: design_import
@mcp.tool()
async def get_url_import_job(job_id: str = Field(..., alias="jobId", description="The unique identifier of the URL import job to retrieve status for.", pattern="^[a-zA-Z0-9_-]{1,50}$")) -> dict[str, Any]:
    """Retrieves the status and result of a URL import job. Use this to poll for completion of an asynchronous import operation, which will return a `success` or `failed` status once processing is complete."""

    # Construct request model with validation
    try:
        _request = _models.GetUrlImportJobRequest(
            path=_models.GetUrlImportJobRequestPath(job_id=job_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_url_import_job: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/url-imports/{jobId}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/url-imports/{jobId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_url_import_job")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_url_import_job", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_url_import_job",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: export
@mcp.tool()
async def start_design_export(
    design_id: str = Field(..., description="The unique identifier of the design to export."),
    format_: Annotated[_models.PdfExportFormat | _models.JpgExportFormat | _models.PngExportFormat | _models.PptxExportFormat | _models.GifExportFormat | _models.Mp4ExportFormat, Field(discriminator="type_")] = Field(..., alias="format", description="The desired export file format and associated configuration options."),
) -> dict[str, Any]:
    """Initiates an asynchronous job to export a design file in the specified format (PDF, JPG, PNG, GIF, PPTX, or MP4). Download URLs are provided upon completion and remain valid for 24 hours."""

    # Construct request model with validation
    try:
        _request = _models.CreateDesignExportJobRequest(
            body=_models.CreateDesignExportJobRequestBody(design_id=design_id, format_=format_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for start_design_export: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/exports"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("start_design_export")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("start_design_export", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="start_design_export",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: export
@mcp.tool()
async def get_design_export_job(export_id: str = Field(..., alias="exportId", description="The unique identifier of the export job to retrieve status and results for.", pattern="^[a-zA-Z0-9_-]{1,50}$")) -> dict[str, Any]:
    """Retrieves the status and results of a design export job. When successful, returns download URLs for each page of the exported design (valid for 24 hours). You may need to poll this endpoint until the job reaches a terminal status (success or failed)."""

    # Construct request model with validation
    try:
        _request = _models.GetDesignExportJobRequest(
            path=_models.GetDesignExportJobRequestPath(export_id=export_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_design_export_job: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/exports/{exportId}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/exports/{exportId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_design_export_job")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_design_export_job", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_design_export_job",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: folder
@mcp.tool()
async def get_folder(folder_id: str = Field(..., alias="folderId", description="The unique identifier of the folder to retrieve. Must be 1-50 characters containing alphanumeric characters, hyphens, or underscores.", pattern="^[a-zA-Z0-9_-]{1,50}$")) -> dict[str, Any]:
    """Retrieves the name and metadata details of a specific folder by its folder ID."""

    # Construct request model with validation
    try:
        _request = _models.GetFolderRequest(
            path=_models.GetFolderRequestPath(folder_id=folder_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_folder: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/folders/{folderId}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/folders/{folderId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_folder")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_folder", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_folder",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: folder
@mcp.tool()
async def rename_folder(
    folder_id: str = Field(..., alias="folderId", description="The unique identifier of the folder to rename.", pattern="^[a-zA-Z0-9_-]{1,50}$"),
    name: str = Field(..., description="The new name for the folder as it will appear in the Canva UI. Must be between 1 and 255 characters.", min_length=1, max_length=255),
) -> dict[str, Any]:
    """Rename a folder in Canva by updating its name. The folder is identified by its unique folder ID."""

    # Construct request model with validation
    try:
        _request = _models.UpdateFolderRequest(
            path=_models.UpdateFolderRequestPath(folder_id=folder_id),
            body=_models.UpdateFolderRequestBody(name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for rename_folder: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/folders/{folderId}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/folders/{folderId}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("rename_folder")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("rename_folder", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="rename_folder",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: folder
@mcp.tool()
async def delete_folder(folder_id: str = Field(..., alias="folderId", description="The unique identifier of the folder to delete.", pattern="^[a-zA-Z0-9_-]{1,50}$")) -> dict[str, Any]:
    """Permanently deletes a folder by moving its contents to Trash. Content owned by the folder owner goes to Trash, while content owned by other users is moved to the top level of their projects."""

    # Construct request model with validation
    try:
        _request = _models.DeleteFolderRequest(
            path=_models.DeleteFolderRequestPath(folder_id=folder_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_folder: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/folders/{folderId}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/folders/{folderId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_folder")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_folder", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_folder",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: folder
@mcp.tool()
async def list_folder_items(
    folder_id: str = Field(..., alias="folderId", description="The unique identifier of the folder to list items from.", pattern="^[a-zA-Z0-9_-]{1,50}$"),
    limit: str | None = Field(None, description="Maximum number of folder items to return in the response. Defaults to 50 items."),
    item_types: list[Literal["design", "folder", "image"]] | None = Field(None, description="Filter results to only include specified item types. Provide a comma-separated list to filter for multiple types. Available types are: design, folder, and image."),
    sort_by: Literal["created_ascending", "created_descending", "modified_ascending", "modified_descending", "title_ascending", "title_descending"] | None = Field(None, description="Sort the returned items by creation date, modification date, or title in ascending or descending order. Defaults to most recently modified first."),
    pin_status: Literal["any", "pinned"] | None = Field(None, description="Filter items by their pinned status. Use 'pinned' to show only pinned items, or 'any' to show all items regardless of pin status."),
) -> dict[str, Any]:
    """Retrieves all items contained in a folder, including nested folders, designs (such as presentations and documents), and image assets. Use optional filters to narrow results by item type, sort order, or pinned status."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.ListFolderItemsRequest(
            path=_models.ListFolderItemsRequestPath(folder_id=folder_id),
            query=_models.ListFolderItemsRequestQuery(limit=_limit, item_types=item_types, sort_by=sort_by, pin_status=pin_status)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_folder_items: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/folders/{folderId}/items", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/folders/{folderId}/items"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_query = _serialize_query(_http_query, {
        "item_types": ("form", False),
    })
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_folder_items")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_folder_items", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_folder_items",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: folder
@mcp.tool()
async def move_item(
    to_folder_id: str = Field(..., description="The ID of the destination folder. Use the special ID `root` to move the item to the top level of the user's projects.", min_length=1, max_length=50),
    item_id: str = Field(..., description="The ID of the item to move. Video assets are not supported.", min_length=1, max_length=50),
) -> dict[str, Any]:
    """Moves an item (design, folder, or asset) to a different folder. Note: If the item exists in multiple folders, use the Canva UI to move it instead."""

    # Construct request model with validation
    try:
        _request = _models.MoveFolderItemRequest(
            body=_models.MoveFolderItemRequestBody(to_folder_id=to_folder_id, item_id=item_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for move_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/folders/move"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("move_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("move_item", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="move_item",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: folder
@mcp.tool()
async def create_folder(
    name: str = Field(..., description="The name for the new folder. Must be between 1 and 255 characters.", min_length=1, max_length=255),
    parent_folder_id: str = Field(..., description="The ID of the parent folder where this folder will be created. Use `root` for top-level projects, `uploads` for the Uploads folder, or provide a specific folder ID.", min_length=1, max_length=50),
) -> dict[str, Any]:
    """Creates a new folder in a user's Canva workspace at the specified location (top-level projects, Uploads folder, or within another folder). Returns the folder ID and metadata upon successful creation."""

    # Construct request model with validation
    try:
        _request = _models.CreateFolderRequest(
            body=_models.CreateFolderRequestBody(name=name, parent_folder_id=parent_folder_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_folder: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/folders"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_folder")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_folder", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_folder",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: oidc
@mcp.tool()
async def get_current_user_info() -> dict[str, Any]:
    """Retrieves the current authenticated user's identity claims and profile information. Returns the same user attributes that were included in the ID token during authorization."""

    # Extract parameters for API call
    _http_path = "/v1/oidc/userinfo"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_current_user_info")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_current_user_info", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_current_user_info",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: resize
@mcp.tool()
async def start_design_resize_job(
    design_id: str = Field(..., description="The unique identifier of the design to be resized."),
    design_type: Annotated[_models.PresetDesignTypeInput | _models.CustomDesignTypeInput, Field(discriminator="type_")] = Field(..., description="The target design type for the resized design. Can be either a preset design type or a custom design with specified height and width dimensions."),
) -> dict[str, Any]:
    """Initiates an asynchronous job to create a resized copy of a design. The resized design is added to the user's root folder and can be sized using either a preset design type or custom dimensions."""

    # Construct request model with validation
    try:
        _request = _models.CreateDesignResizeJobRequest(
            body=_models.CreateDesignResizeJobRequestBody(design_id=design_id, design_type=design_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for start_design_resize_job: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/resizes"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("start_design_resize_job")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("start_design_resize_job", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="start_design_resize_job",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: resize
@mcp.tool()
async def get_resize_job(job_id: str = Field(..., alias="jobId", description="The unique identifier of the design resize job to retrieve status for.", pattern="^[a-zA-Z0-9_-]{1,50}$")) -> dict[str, Any]:
    """Retrieves the status and result of an asynchronous design resize job. Use this to poll for job completion after initiating a resize operation, which will include the resized design metadata upon success."""

    # Construct request model with validation
    try:
        _request = _models.GetDesignResizeJobRequest(
            path=_models.GetDesignResizeJobRequestPath(job_id=job_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_resize_job: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/resizes/{jobId}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/resizes/{jobId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_resize_job")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_resize_job", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_resize_job",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: user
@mcp.tool()
async def get_current_user() -> dict[str, Any]:
    """Retrieves the current authenticated user's ID and team ID based on the provided access token."""

    # Extract parameters for API call
    _http_path = "/v1/users/me"
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

# Tags: user
@mcp.tool()
async def list_user_capabilities() -> dict[str, Any]:
    """Retrieves the list of API capabilities available for the authenticated user account. This shows which features and operations the user's access token is authorized to use."""

    # Extract parameters for API call
    _http_path = "/v1/users/me/capabilities"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_user_capabilities")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_user_capabilities", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_user_capabilities",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: user
@mcp.tool()
async def get_user_profile() -> dict[str, Any]:
    """Retrieve the profile information for the authenticated user associated with the provided access token. Currently returns the user's display name, with additional profile data expected in future releases."""

    # Extract parameters for API call
    _http_path = "/v1/users/me/profile"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_user_profile")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_user_profile", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_user_profile",
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
        print("  python canva_server.py", file=sys.stderr)
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

    parser = argparse.ArgumentParser(description="Canva MCP Server")

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
    logger.info("Starting Canva MCP Server")
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

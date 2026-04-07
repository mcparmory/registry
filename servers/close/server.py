#!/usr/bin/env python3
"""
Close API MCP Server

API Info:
- Contact: Joe Kemp, VP of Engineering (https://calendly.com/joe-close/api-chat)

Generated: 2026-04-07 08:42:04 UTC
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
from typing import Any, Literal

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

BASE_URL = os.getenv("BASE_URL", "https://api.close.com/api/v1")
SERVER_NAME = "Close API"
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
            _content = body if body_content_type is not None and body_content_type not in ("application/json", "application/x-www-form-urlencoded", "multipart/form-data") else None
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
    # Normalize double slashes that occur when a path param value itself starts
    # with "/" and the template already has a preceding "/" (e.g. "/{path}" + "/foo")
    while "//" in result:
        result = result.replace("//", "/")
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
    'oauth2',
    'basicAuth',
]

# Initialize authentication handlers at server startup
_auth_handlers: dict[str, Any] = {}
try:
    _auth_handlers["oauth2"] = _auth.OAuth2Auth()
    logging.info("Authentication configured: oauth2")
except ValueError as e:
    # Extract credential names from error message (first sentence before "Leave empty")
    error_msg = str(e).split("Leave empty")[0].strip()
    logging.warning(f"Credentials for oauth2 not configured: {error_msg}")
    _auth_handlers["oauth2"] = None
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

mcp = FastMCP("Close API", middleware=[_JsonCoercionMiddleware()])

# Tags: Leads
@mcp.tool()
async def list_leads(limit: int | None = Field(None, alias="_limit", description="Maximum number of leads to return in the response. Specify a positive integer to limit the result set size.")) -> dict[str, Any]:
    """Retrieve a list of leads with optional pagination control. Use the limit parameter to specify the maximum number of results to return."""

    # Construct request model with validation
    try:
        _request = _models.GetLeadRequest(
            query=_models.GetLeadRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_leads: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/lead"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_leads")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_leads", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_leads",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Leads
@mcp.tool()
async def create_lead(
    name: str | None = Field(None, description="The name of the lead."),
    contacts: list[dict[str, Any]] | None = Field(None, description="An array of nested contact objects to associate with the lead. Order is preserved as provided."),
    addresses: list[dict[str, Any]] | None = Field(None, description="An array of nested address objects to associate with the lead. Order is preserved as provided."),
) -> dict[str, Any]:
    """Create a new lead with optional nested contacts and addresses. Related entities like activities, tasks, and opportunities must be created separately."""

    # Construct request model with validation
    try:
        _request = _models.PostLeadRequest(
            body=_models.PostLeadRequestBody(name=name, contacts=contacts, addresses=addresses)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_lead: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/lead"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_lead")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_lead", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_lead",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Leads
@mcp.tool()
async def get_lead(id_: str = Field(..., alias="id", description="The unique identifier of the lead to retrieve.")) -> dict[str, Any]:
    """Retrieve a single lead by its unique identifier. Use this operation to fetch detailed information about a specific lead."""

    # Construct request model with validation
    try:
        _request = _models.GetLeadIdRequest(
            path=_models.GetLeadIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_lead: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/lead/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/lead/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_lead")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_lead", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_lead",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Leads
@mcp.tool()
async def update_lead(
    id_: str = Field(..., alias="id", description="The unique identifier of the lead to update."),
    custom_field_id: str | None = Field(None, alias="custom_FIELD_ID", description="Custom field value to set, update, or remove. Set to null to unset a field. For multi-value fields, use the .add suffix to append values or .remove suffix to delete specific values."),
) -> dict[str, Any]:
    """Update an existing lead with support for partial updates. Modify standard fields like status, custom fields, or multi-value fields using add/remove suffixes without affecting unspecified fields."""

    # Construct request model with validation
    try:
        _request = _models.PutLeadIdRequest(
            path=_models.PutLeadIdRequestPath(id_=id_),
            body=_models.PutLeadIdRequestBody(custom_field_id=custom_field_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_lead: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/lead/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/lead/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_lead")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_lead", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_lead",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Leads
@mcp.tool()
async def delete_lead(id_: str = Field(..., alias="id", description="The unique identifier of the lead to delete. This must be a valid lead ID that exists in the system.")) -> dict[str, Any]:
    """Permanently remove a lead from the system by its ID. This action cannot be undone and will delete all associated data."""

    # Construct request model with validation
    try:
        _request = _models.DeleteLeadIdRequest(
            path=_models.DeleteLeadIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_lead: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/lead/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/lead/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_lead")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_lead", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_lead",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Leads
@mcp.tool()
async def merge_leads(
    source: str = Field(..., description="The ID of the source lead whose data will be consolidated into the destination lead."),
    destination: str = Field(..., description="The ID of the destination lead that will retain all merged data and serve as the primary record after the operation completes."),
) -> dict[str, Any]:
    """Merge two leads by consolidating all data from a source lead into a destination lead. The destination lead becomes the primary record containing the merged information."""

    # Construct request model with validation
    try:
        _request = _models.PostLeadMergeRequest(
            body=_models.PostLeadMergeRequestBody(source=source, destination=destination)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for merge_leads: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/lead/merge"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("merge_leads")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("merge_leads", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="merge_leads",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Contacts
@mcp.tool()
async def list_contacts(limit: int | None = Field(None, alias="_limit", description="Maximum number of contacts to return in a single request. Allows you to control pagination size for efficient data retrieval.")) -> dict[str, Any]:
    """Retrieve a paginated list of all contacts in the system. Use the limit parameter to control the number of results returned per request."""

    # Construct request model with validation
    try:
        _request = _models.GetContactRequest(
            query=_models.GetContactRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_contacts: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/contact"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_contacts")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_contacts", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_contacts",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Contacts
@mcp.tool()
async def create_contact(
    lead_id: str = Field(..., description="The ID of the lead to associate with this contact. Required to link the contact to an existing lead; if omitted, a new lead will be created automatically."),
    name: str = Field(..., description="The full name of the contact. Used to identify the contact and, if no lead_id is provided, to name the newly created lead."),
    title: str | None = Field(None, description="The contact's job title or professional role."),
    emails: list[_models.PostContactBodyEmailsItem] | None = Field(None, description="A list of email addresses for the contact. Each item should be a valid email address."),
    phones: list[_models.PostContactBodyPhonesItem] | None = Field(None, description="A list of phone numbers for the contact. Each item should be a valid phone number."),
) -> dict[str, Any]:
    """Create a new contact and associate it with a lead. If no lead_id is provided, a new lead will be automatically created using the contact's name."""

    # Construct request model with validation
    try:
        _request = _models.PostContactRequest(
            body=_models.PostContactRequestBody(lead_id=lead_id, name=name, title=title, emails=emails, phones=phones)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_contact: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/contact"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_contact")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_contact", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_contact",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Contacts
@mcp.tool()
async def get_contact(id_: str = Field(..., alias="id", description="The unique identifier of the contact to retrieve.")) -> dict[str, Any]:
    """Retrieve a single contact by its unique identifier. Use this operation to fetch detailed information about a specific contact."""

    # Construct request model with validation
    try:
        _request = _models.GetContactIdRequest(
            path=_models.GetContactIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_contact: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/contact/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/contact/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_contact")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_contact", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_contact",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Contacts
@mcp.tool()
async def update_contact(
    id_: str = Field(..., alias="id", description="The unique identifier of the contact to update."),
    name: str | None = Field(None, description="The contact's full name."),
    emails: list[dict[str, Any]] | None = Field(None, description="A list of email addresses associated with the contact. Order is preserved as provided."),
    phones: list[dict[str, Any]] | None = Field(None, description="A list of phone numbers associated with the contact. Order is preserved as provided."),
    urls: list[dict[str, Any]] | None = Field(None, description="A list of URLs associated with the contact. Order is preserved as provided."),
) -> dict[str, Any]:
    """Update an existing contact's information including name, email addresses, phone numbers, and URLs. Use `.add` or `.remove` suffixes on custom field keys to add or remove individual values from multi-value fields."""

    # Construct request model with validation
    try:
        _request = _models.PutContactIdRequest(
            path=_models.PutContactIdRequestPath(id_=id_),
            body=_models.PutContactIdRequestBody(name=name, emails=emails, phones=phones, urls=urls)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_contact: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/contact/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/contact/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_contact")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_contact", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_contact",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Contacts
@mcp.tool()
async def delete_contact(id_: str = Field(..., alias="id", description="The unique identifier of the contact to delete.")) -> dict[str, Any]:
    """Permanently remove a contact from the system by its ID. This action cannot be undone and will delete all associated data."""

    # Construct request model with validation
    try:
        _request = _models.DeleteContactIdRequest(
            path=_models.DeleteContactIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_contact: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/contact/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/contact/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_contact")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_contact", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_contact",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Activities
@mcp.tool()
async def list_activities(
    user_id__in: str | None = Field(None, description="Filter activities by one or more user IDs (comma-separated). Only available when querying activities for a single lead using lead_id."),
    contact_id__in: str | None = Field(None, description="Filter activities by one or more contact IDs (comma-separated). Only available when querying activities for a single lead using lead_id."),
    activity_at__gt: str | None = Field(None, description="Return only activities that occurred after this date and time (ISO 8601 format). Requires sorting by -activity_at when used."),
    activity_at__lt: str | None = Field(None, description="Return only activities that occurred before this date and time (ISO 8601 format). Requires sorting by -activity_at when used."),
    order_by: Literal["date_created", "-date_created", "activity_at", "-activity_at"] | None = Field(None, alias="_order_by", description="Sort results by creation date or activity timestamp. Use date_created for creation order or activity_at for activity order; prefix with hyphen (-) for descending order. Sorting by -activity_at is only available when querying a single lead with lead_id."),
    limit: int | None = Field(None, alias="_limit", description="Maximum number of results to return in the response."),
    thread_emails: Literal["true", "only"] | None = Field(None, description="Control how emails are grouped in results. Use 'true' to return email threads alongside individual email objects, or 'only' to return email threads without individual email objects. Omit to return individual email objects per message."),
) -> dict[str, Any]:
    """Retrieve and filter activity records across leads or for a specific lead. Supports advanced filtering by user, contact, and activity timestamp, with optional email threading to group related messages."""

    # Construct request model with validation
    try:
        _request = _models.GetActivityRequest(
            query=_models.GetActivityRequestQuery(user_id__in=user_id__in, contact_id__in=contact_id__in, activity_at__gt=activity_at__gt, activity_at__lt=activity_at__lt, order_by=order_by, limit=limit, thread_emails=thread_emails)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_activities: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/activity"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_activities")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_activities", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_activities",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Call
@mcp.tool()
async def list_calls(limit: int | None = Field(None, alias="_limit", description="Maximum number of call records to return in the response. Limits the result set size for pagination or performance optimization.")) -> dict[str, Any]:
    """Retrieve a list of all Call activities, with optional filtering by result count. Use this to view call records and activity history."""

    # Construct request model with validation
    try:
        _request = _models.GetActivityCallRequest(
            query=_models.GetActivityCallRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_calls: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/activity/call"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_calls")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_calls", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_calls",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Call
@mcp.tool()
async def log_call_activity(
    direction: Literal["outbound", "inbound"] = Field(..., description="Specify whether the call was outbound or inbound."),
    lead_id: str = Field(..., description="The ID of the lead associated with this call activity."),
    recording_url: str | None = Field(None, description="Optional HTTPS URL pointing to an MP3 recording of the call."),
    duration: int | None = Field(None, description="Optional call duration specified in seconds."),
) -> dict[str, Any]:
    """Manually log a call activity for calls made outside the Close VoIP system. The activity is automatically marked as completed."""

    # Construct request model with validation
    try:
        _request = _models.PostActivityCallRequest(
            body=_models.PostActivityCallRequestBody(direction=direction, recording_url=recording_url, lead_id=lead_id, duration=duration)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for log_call_activity: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/activity/call"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("log_call_activity")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("log_call_activity", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="log_call_activity",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Call
@mcp.tool()
async def get_call(id_: str = Field(..., alias="id", description="The unique identifier of the Call activity record to retrieve.")) -> dict[str, Any]:
    """Retrieve a specific Call activity record by its unique identifier. Use this to fetch detailed information about a single call activity."""

    # Construct request model with validation
    try:
        _request = _models.GetActivityCallIdRequest(
            path=_models.GetActivityCallIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_call: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/activity/call/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/activity/call/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_call")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_call", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_call",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Call
@mcp.tool()
async def update_call(
    id_: str = Field(..., alias="id", description="The unique identifier of the Call activity to update."),
    note_html: str | None = Field(None, description="HTML-formatted note content to attach to the call activity."),
    outcome_id: str | None = Field(None, description="The outcome identifier to associate with this call activity."),
) -> dict[str, Any]:
    """Update a Call activity record, typically to modify the call notes or assign an outcome. Note that certain fields like status, duration, and direction cannot be modified for calls made through Close's VoIP system."""

    # Construct request model with validation
    try:
        _request = _models.PutActivityCallIdRequest(
            path=_models.PutActivityCallIdRequestPath(id_=id_),
            body=_models.PutActivityCallIdRequestBody(note_html=note_html, outcome_id=outcome_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_call: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/activity/call/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/activity/call/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_call")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_call", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_call",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Call
@mcp.tool()
async def delete_call(id_: str = Field(..., alias="id", description="The unique identifier of the Call activity to delete.")) -> dict[str, Any]:
    """Permanently delete a Call activity record by its ID. This action cannot be undone and will remove all associated data."""

    # Construct request model with validation
    try:
        _request = _models.DeleteActivityCallIdRequest(
            path=_models.DeleteActivityCallIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_call: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/activity/call/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/activity/call/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_call")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_call", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_call",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Created
@mcp.tool()
async def list_created_activities(limit: int | None = Field(None, alias="_limit", description="Maximum number of activities to return in the response. Useful for pagination or limiting result set size.")) -> dict[str, Any]:
    """Retrieve a list of all activities with Created status, optionally limiting the number of results returned."""

    # Construct request model with validation
    try:
        _request = _models.GetActivityCreatedRequest(
            query=_models.GetActivityCreatedRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_created_activities: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/activity/created"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_created_activities")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_created_activities", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_created_activities",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Created
@mcp.tool()
async def get_activity(id_: str = Field(..., alias="id", description="The unique identifier of the Created activity record to retrieve.")) -> dict[str, Any]:
    """Retrieve a single Created activity record by its unique identifier. Use this to fetch detailed information about a specific activity that was created."""

    # Construct request model with validation
    try:
        _request = _models.GetActivityCreatedIdRequest(
            path=_models.GetActivityCreatedIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_activity: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/activity/created/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/activity/created/{id}"
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

# Tags: Email
@mcp.tool()
async def list_email_activities(limit: int | None = Field(None, alias="_limit", description="Maximum number of email activity records to return in the response. Limits the result set size for pagination or performance optimization.")) -> dict[str, Any]:
    """Retrieve a list of email activities, with each result representing a single email message. Optionally filter results by specifying a maximum number of records to return."""

    # Construct request model with validation
    try:
        _request = _models.GetActivityEmailRequest(
            query=_models.GetActivityEmailRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_email_activities: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/activity/email"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_email_activities")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_email_activities", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_email_activities",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Email
@mcp.tool()
async def create_activity_email(
    status: Literal["inbox", "draft", "scheduled", "outbox", "sent"] = Field(..., description="The email's status: use 'inbox' to log received emails, 'draft' to create editable drafts, 'scheduled' to send at a future time, 'outbox' to send immediately, or 'sent' to log already-sent emails."),
    lead_id: str = Field(..., description="The unique identifier of the lead associated with this email activity."),
    sender: str | None = Field(None, description="Sender's name and email address in the format 'Name <email@example.com>'. Required when status is inbox, scheduled, outbox, or sent."),
    followup_date: str | None = Field(None, description="ISO 8601 date-time for scheduling a follow-up task if no response is received. Only applicable for scheduled, outbox, or sent emails."),
    template_id: str | None = Field(None, description="ID of an email template to render server-side. When using a template, do not include body_text or body_html parameters."),
    attachments: list[_models.PostActivityEmailBodyAttachmentsItem] | None = Field(None, description="List of file attachments. All files must be pre-uploaded via the Files API before referencing them here."),
    subject: str | None = Field(None, description="The subject line of the email."),
    to: list[str] | None = Field(None, description="Array of recipient email addresses."),
) -> dict[str, Any]:
    """Create a new email activity with a specified status to log received emails, create drafts, schedule future sends, send immediately, or record already-sent emails. Only draft emails can be modified after creation."""

    # Construct request model with validation
    try:
        _request = _models.PostActivityEmailRequest(
            body=_models.PostActivityEmailRequestBody(status=status, sender=sender, followup_date=followup_date, template_id=template_id, attachments=attachments, lead_id=lead_id, subject=subject, to=to)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_activity_email: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/activity/email"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_activity_email")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_activity_email", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_activity_email",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Email
@mcp.tool()
async def get_email_activity(id_: str = Field(..., alias="id", description="The unique identifier of the email activity record to retrieve.")) -> dict[str, Any]:
    """Retrieve a single email activity record by its unique identifier. Use this to fetch detailed information about a specific email interaction or communication event."""

    # Construct request model with validation
    try:
        _request = _models.GetActivityEmailIdRequest(
            path=_models.GetActivityEmailIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_email_activity: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/activity/email/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/activity/email/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_email_activity")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_email_activity", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_email_activity",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Email
@mcp.tool()
async def update_email_activity(
    id_: str = Field(..., alias="id", description="The unique identifier of the email activity to update."),
    sender: str | None = Field(None, description="The sender email address. Required when changing the email status to scheduled or outbox if not already set on the email."),
    followup_date: str | None = Field(None, description="The date and time for an associated follow-up task, specified in ISO 8601 format."),
) -> dict[str, Any]:
    """Update a draft email activity or change its status to scheduled or outbox. When transitioning to scheduled or outbox status, the sender email address is required if not already set on the email."""

    # Construct request model with validation
    try:
        _request = _models.PutActivityEmailIdRequest(
            path=_models.PutActivityEmailIdRequestPath(id_=id_),
            body=_models.PutActivityEmailIdRequestBody(sender=sender, followup_date=followup_date)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_email_activity: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/activity/email/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/activity/email/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_email_activity")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_email_activity", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_email_activity",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Email
@mcp.tool()
async def delete_email_activity(id_: str = Field(..., alias="id", description="The unique identifier of the email activity record to delete.")) -> dict[str, Any]:
    """Permanently delete an email activity record by its unique identifier. This action cannot be undone and will remove all associated data."""

    # Construct request model with validation
    try:
        _request = _models.DeleteActivityEmailIdRequest(
            path=_models.DeleteActivityEmailIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_email_activity: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/activity/email/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/activity/email/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_email_activity")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_email_activity", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_email_activity",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: EmailThread
@mcp.tool()
async def list_email_threads(limit: int | None = Field(None, alias="_limit", description="Maximum number of email threads to return in the response. Limits the result set size for pagination or performance optimization.")) -> dict[str, Any]:
    """Retrieve a list of email thread activities, where each thread represents a single email conversation typically grouped by subject line."""

    # Construct request model with validation
    try:
        _request = _models.GetActivityEmailthreadRequest(
            query=_models.GetActivityEmailthreadRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_email_threads: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/activity/emailthread"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_email_threads")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_email_threads", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_email_threads",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: EmailThread
@mcp.tool()
async def get_email_thread(id_: str = Field(..., alias="id", description="The unique identifier of the email thread activity to retrieve.")) -> dict[str, Any]:
    """Retrieve a specific email thread activity by its unique identifier. Use this to fetch detailed information about a single email thread record."""

    # Construct request model with validation
    try:
        _request = _models.GetActivityEmailthreadIdRequest(
            path=_models.GetActivityEmailthreadIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_email_thread: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/activity/emailthread/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/activity/emailthread/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_email_thread")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_email_thread", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_email_thread",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: EmailThread
@mcp.tool()
async def delete_email_thread(id_: str = Field(..., alias="id", description="The unique identifier of the email thread activity to delete.")) -> dict[str, Any]:
    """Delete an email thread activity and all associated email activities within that thread. This is a permanent operation that removes the entire thread conversation."""

    # Construct request model with validation
    try:
        _request = _models.DeleteActivityEmailthreadIdRequest(
            path=_models.DeleteActivityEmailthreadIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_email_thread: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/activity/emailthread/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/activity/emailthread/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_email_thread")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_email_thread", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_email_thread",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: LeadStatusChange
@mcp.tool()
async def list_lead_status_changes(limit: int | None = Field(None, alias="_limit", description="Maximum number of lead status change records to return in the response. Useful for pagination or limiting result set size.")) -> dict[str, Any]:
    """Retrieve a list of all lead status change activities, with optional filtering by result limit. Use this to track when and how lead statuses have been modified."""

    # Construct request model with validation
    try:
        _request = _models.GetActivityStatusChangeLeadRequest(
            query=_models.GetActivityStatusChangeLeadRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_lead_status_changes: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/activity/status_change/lead"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_lead_status_changes")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_lead_status_changes", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_lead_status_changes",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: LeadStatusChange
@mcp.tool()
async def log_lead_status_change(
    new_status_id: str | None = Field(None, description="The ID of the lead status after the change. Required to document what status the lead transitioned to."),
    old_status_id: str | None = Field(None, description="The ID of the lead status before the change. Required to document what status the lead transitioned from."),
) -> dict[str, Any]:
    """Log a historical lead status change event in the activity feed without modifying the lead's current status. Use this operation to import status change records from external systems or organizations."""

    # Construct request model with validation
    try:
        _request = _models.PostActivityStatusChangeLeadRequest(
            body=_models.PostActivityStatusChangeLeadRequestBody(new_status_id=new_status_id, old_status_id=old_status_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for log_lead_status_change: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/activity/status_change/lead"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("log_lead_status_change")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("log_lead_status_change", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="log_lead_status_change",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: LeadStatusChange
@mcp.tool()
async def get_lead_status_change(id_: str = Field(..., alias="id", description="The unique identifier of the lead status change activity record to retrieve.")) -> dict[str, Any]:
    """Retrieve details of a specific lead status change activity, including when and how the lead's status was modified."""

    # Construct request model with validation
    try:
        _request = _models.GetActivityStatusChangeLeadIdRequest(
            path=_models.GetActivityStatusChangeLeadIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_lead_status_change: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/activity/status_change/lead/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/activity/status_change/lead/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_lead_status_change")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_lead_status_change", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_lead_status_change",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: LeadStatusChange
@mcp.tool()
async def delete_lead_status_change(id_: str = Field(..., alias="id", description="The unique identifier of the LeadStatusChange activity record to delete.")) -> dict[str, Any]:
    """Remove a status change event from a lead's activity history. This deletes the activity record without affecting the lead's current status, useful when a status change event is outdated or causing sync issues with external systems."""

    # Construct request model with validation
    try:
        _request = _models.DeleteActivityStatusChangeLeadIdRequest(
            path=_models.DeleteActivityStatusChangeLeadIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_lead_status_change: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/activity/status_change/lead/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/activity/status_change/lead/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_lead_status_change")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_lead_status_change", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_lead_status_change",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Meeting Search
@mcp.tool()
async def search_meetings(
    provider_calendar_event_id: str | None = Field(None, description="The unique event identifier from the calendar provider (e.g., Google Calendar or Microsoft Outlook) that the meeting was synced from. Required when searching by any other calendar provider field."),
    provider_calendar_id: str | None = Field(None, description="The calendar identifier from the provider where the meeting event is stored."),
    provider_calendar_type: Literal["google", "microsoft"] | None = Field(None, description="The calendar service provider type. Supported providers are Google Calendar or Microsoft Outlook."),
) -> dict[str, Any]:
    """Search for meetings by their synced calendar provider information, including event ID, calendar ID, provider type, and start time."""

    # Construct request model with validation
    try:
        _request = _models.GetActivityMeetingRequest(
            query=_models.GetActivityMeetingRequestQuery(provider_calendar_event_id=provider_calendar_event_id, provider_calendar_id=provider_calendar_id, provider_calendar_type=provider_calendar_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_meetings: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/activity/meeting"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_meetings")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_meetings", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_meetings",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Meeting
@mcp.tool()
async def get_meeting(id_: str = Field(..., alias="id", description="The unique identifier of the Meeting activity to retrieve.")) -> dict[str, Any]:
    """Retrieve a specific Meeting activity by its unique identifier. Use this to fetch details about a scheduled or completed meeting."""

    # Construct request model with validation
    try:
        _request = _models.GetActivityMeetingIdRequest(
            path=_models.GetActivityMeetingIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_meeting: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/activity/meeting/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/activity/meeting/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_meeting")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_meeting", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_meeting",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Meeting
@mcp.tool()
async def update_meeting(
    id_: str = Field(..., alias="id", description="The unique identifier of the Meeting activity to update."),
    user_note_html: str | None = Field(None, description="Rich text HTML content for meeting notes. Allows formatted text documentation of meeting details and discussions."),
    outcome_id: str | None = Field(None, description="Custom outcome identifier to associate with the meeting, linking the meeting to a specific result or resolution."),
) -> dict[str, Any]:
    """Update a Meeting activity by modifying its notes or associated outcome. Use this to record meeting notes in rich text format or link the meeting to a specific outcome."""

    # Construct request model with validation
    try:
        _request = _models.PutActivityMeetingIdRequest(
            path=_models.PutActivityMeetingIdRequestPath(id_=id_),
            body=_models.PutActivityMeetingIdRequestBody(user_note_html=user_note_html, outcome_id=outcome_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_meeting: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/activity/meeting/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/activity/meeting/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_meeting")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_meeting", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_meeting",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Meeting
@mcp.tool()
async def delete_meeting(id_: str = Field(..., alias="id", description="The unique identifier of the Meeting activity to delete.")) -> dict[str, Any]:
    """Permanently delete a specific Meeting activity by its ID. This action cannot be undone and will remove all associated data."""

    # Construct request model with validation
    try:
        _request = _models.DeleteActivityMeetingIdRequest(
            path=_models.DeleteActivityMeetingIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_meeting: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/activity/meeting/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/activity/meeting/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_meeting")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_meeting", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_meeting",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Meeting
@mcp.tool()
async def create_or_update_meeting_integration(
    id_: str = Field(..., alias="id", description="The unique identifier of the meeting activity to integrate with a third-party service."),
    body: dict[str, Any] = Field(..., description="The integration configuration payload. Submit an empty JSON object to perform no action, or include integration details to create or update the integration."),
) -> dict[str, Any]:
    """Create a new third-party meeting integration or update an existing one for a specific meeting activity. This operation is only available to OAuth applications and allows third-party services to be presented as tabs in the activity feed."""

    # Construct request model with validation
    try:
        _request = _models.PostActivityMeetingIdIntegrationRequest(
            path=_models.PostActivityMeetingIdIntegrationRequestPath(id_=id_),
            body=_models.PostActivityMeetingIdIntegrationRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_or_update_meeting_integration: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/activity/meeting/{id}/integration", _request.path.model_dump(by_alias=True)) if _request.path else "/activity/meeting/{id}/integration"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_or_update_meeting_integration")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_or_update_meeting_integration", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_or_update_meeting_integration",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Note
@mcp.tool()
async def list_notes(limit: int | None = Field(None, alias="_limit", description="Maximum number of note records to return in the response. Useful for pagination or limiting result set size.")) -> dict[str, Any]:
    """Retrieve a list of all Note activities, with optional filtering by result count. Use this to view note records across your activity stream."""

    # Construct request model with validation
    try:
        _request = _models.GetActivityNoteRequest(
            query=_models.GetActivityNoteRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_notes: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/activity/note"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_notes")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_notes", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_notes",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Note
@mcp.tool()
async def create_note(
    lead_id: str = Field(..., description="The lead ID to associate this note with. Required to link the note to a specific lead record."),
    note_html: str | None = Field(None, description="Rich-text note content using a subset of HTML tags. When both note_html and note are provided, note_html takes precedence."),
    pinned: bool | None = Field(None, description="Whether to pin this note for prominence. Set to true to pin or false to unpin."),
    attachments: list[_models.PostActivityNoteBodyAttachmentsItem] | None = Field(None, description="List of file attachments to include with the note. Each attachment must include a URL (beginning with https://app.close.com/go/file/), filename, and content type. Files should be uploaded via the Files API first before referencing them here."),
) -> dict[str, Any]:
    """Create a note activity associated with a lead. Notes support rich-text formatting, optional attachments, and can be pinned for visibility."""

    # Construct request model with validation
    try:
        _request = _models.PostActivityNoteRequest(
            body=_models.PostActivityNoteRequestBody(lead_id=lead_id, note_html=note_html, pinned=pinned, attachments=attachments)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_note: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/activity/note"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_note")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_note", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_note",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Note
@mcp.tool()
async def get_note(id_: str = Field(..., alias="id", description="The unique identifier of the note activity to retrieve.")) -> dict[str, Any]:
    """Retrieve a single note activity by its unique identifier. Use this to fetch detailed information about a specific note."""

    # Construct request model with validation
    try:
        _request = _models.GetActivityNoteIdRequest(
            path=_models.GetActivityNoteIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_note: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/activity/note/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/activity/note/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_note")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_note", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_note",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Note
@mcp.tool()
async def update_note(
    id_: str = Field(..., alias="id", description="The unique identifier of the note activity to update."),
    note_html: str | None = Field(None, description="Rich-text note content formatted with a subset of HTML tags. When both note_html and plain text note are provided, this field takes precedence."),
    pinned: bool | None = Field(None, description="Set to true to pin this note for visibility, or false to unpin it."),
    attachments: list[_models.PutActivityNoteIdBodyAttachmentsItem] | None = Field(None, description="An ordered list of file attachments to associate with this note. Order is preserved as provided."),
) -> dict[str, Any]:
    """Update an existing note activity, including its content, formatting, and pin status. Use note_html for rich-text content with HTML formatting, which takes precedence over plain text if both are provided."""

    # Construct request model with validation
    try:
        _request = _models.PutActivityNoteIdRequest(
            path=_models.PutActivityNoteIdRequestPath(id_=id_),
            body=_models.PutActivityNoteIdRequestBody(note_html=note_html, pinned=pinned, attachments=attachments)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_note: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/activity/note/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/activity/note/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_note")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_note", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_note",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Note
@mcp.tool()
async def delete_activity_note(id_: str = Field(..., alias="id", description="The unique identifier of the Note activity to delete.")) -> dict[str, Any]:
    """Permanently delete a Note activity by its ID. This action cannot be undone and will remove all associated data."""

    # Construct request model with validation
    try:
        _request = _models.DeleteActivityNoteIdRequest(
            path=_models.DeleteActivityNoteIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_activity_note: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/activity/note/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/activity/note/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_activity_note")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_activity_note", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_activity_note",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: OpportunityStatusChange
@mcp.tool()
async def list_opportunity_status_changes(
    opportunity_id: str | None = Field(None, description="Filter results to show status changes for a specific opportunity by its ID."),
    limit: int | None = Field(None, alias="_limit", description="Limit the number of results returned in the response."),
) -> dict[str, Any]:
    """Retrieve a list of status change activities for opportunities, with optional filtering by opportunity ID and result limiting."""

    # Construct request model with validation
    try:
        _request = _models.GetActivityStatusChangeOpportunityRequest(
            query=_models.GetActivityStatusChangeOpportunityRequestQuery(opportunity_id=opportunity_id, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_opportunity_status_changes: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/activity/status_change/opportunity"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_opportunity_status_changes")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_opportunity_status_changes", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_opportunity_status_changes",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: OpportunityStatusChange
@mcp.tool()
async def log_opportunity_status_change(
    opportunity_id: str | None = Field(None, description="The unique identifier of the opportunity associated with this status change event."),
    new_status_id: str | None = Field(None, description="The unique identifier of the opportunity status that was transitioned to."),
    old_status_id: str | None = Field(None, description="The unique identifier of the opportunity status that was transitioned from."),
) -> dict[str, Any]:
    """Log a historical opportunity status change event in the activity feed without modifying the actual opportunity status. Use this operation to import status change records from external systems or organizations."""

    # Construct request model with validation
    try:
        _request = _models.PostActivityStatusChangeOpportunityRequest(
            body=_models.PostActivityStatusChangeOpportunityRequestBody(opportunity_id=opportunity_id, new_status_id=new_status_id, old_status_id=old_status_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for log_opportunity_status_change: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/activity/status_change/opportunity"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("log_opportunity_status_change")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("log_opportunity_status_change", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="log_opportunity_status_change",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: OpportunityStatusChange
@mcp.tool()
async def get_opportunity_status_change(id_: str = Field(..., alias="id", description="The unique identifier of the OpportunityStatusChange activity record to retrieve.")) -> dict[str, Any]:
    """Retrieve details of a specific opportunity status change activity, including what changed and when the transition occurred."""

    # Construct request model with validation
    try:
        _request = _models.GetActivityStatusChangeOpportunityIdRequest(
            path=_models.GetActivityStatusChangeOpportunityIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_opportunity_status_change: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/activity/status_change/opportunity/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/activity/status_change/opportunity/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_opportunity_status_change")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_opportunity_status_change", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_opportunity_status_change",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: OpportunityStatusChange
@mcp.tool()
async def delete_opportunity_status_change(id_: str = Field(..., alias="id", description="The unique identifier of the OpportunityStatusChange activity record to delete.")) -> dict[str, Any]:
    """Remove a status change activity from an opportunity's activity feed. This deletion does not alter the opportunity's current status—it only removes the historical status change event, useful when the activity is irrelevant or causing integration conflicts."""

    # Construct request model with validation
    try:
        _request = _models.DeleteActivityStatusChangeOpportunityIdRequest(
            path=_models.DeleteActivityStatusChangeOpportunityIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_opportunity_status_change: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/activity/status_change/opportunity/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/activity/status_change/opportunity/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_opportunity_status_change")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_opportunity_status_change", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_opportunity_status_change",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: SMS
@mcp.tool()
async def list_sms_activities(limit: int | None = Field(None, alias="_limit", description="Maximum number of SMS activities to return in the response. Limits the result set size for pagination or performance optimization.")) -> dict[str, Any]:
    """Retrieve a list of SMS activities, including MMS messages with attachments. Attachments contain metadata (URL, filename, size, content type) and optional thumbnails; accessing URLs requires an authenticated session."""

    # Construct request model with validation
    try:
        _request = _models.GetActivitySmsRequest(
            query=_models.GetActivitySmsRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_sms_activities: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/activity/sms"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
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
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: SMS
@mcp.tool()
async def create_sms_activity(
    status: Literal["inbox", "draft", "scheduled", "outbox", "sent"] = Field(..., description="The current status of the SMS activity. Use inbox to log a received SMS, draft to create an editable SMS, scheduled to send at a future date/time, outbox to send immediately, or sent to log an already-sent SMS."),
    send_to_inbox: bool | None = Field(None, description="When creating an SMS with inbox status, set to true to automatically generate a corresponding Inbox Notification for the SMS."),
    template_id: str | None = Field(None, description="The ID of an SMS template to use as the content for this activity instead of providing raw text."),
    remote_phone: str | None = Field(None, description="The remote phone number for the SMS recipient (when sending) or sender (when receiving)."),
) -> dict[str, Any]:
    """Create an SMS activity to log, draft, schedule, or send SMS messages. Only draft SMS activities can be modified after creation."""

    # Construct request model with validation
    try:
        _request = _models.PostActivitySmsRequest(
            query=_models.PostActivitySmsRequestQuery(send_to_inbox=send_to_inbox),
            body=_models.PostActivitySmsRequestBody(status=status, template_id=template_id, remote_phone=remote_phone)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_sms_activity: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/activity/sms"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_sms_activity")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_sms_activity", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_sms_activity",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: SMS
@mcp.tool()
async def get_sms_activity(id_: str = Field(..., alias="id", description="The unique identifier of the SMS activity record to retrieve.")) -> dict[str, Any]:
    """Retrieve detailed information about a specific SMS activity by its unique identifier. Use this to fetch the complete record of a single SMS message or communication event."""

    # Construct request model with validation
    try:
        _request = _models.GetActivitySmsIdRequest(
            path=_models.GetActivitySmsIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_sms_activity: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/activity/sms/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/activity/sms/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_sms_activity")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_sms_activity", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_sms_activity",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: SMS
@mcp.tool()
async def update_sms_activity(id_: str = Field(..., alias="id", description="The unique identifier of the SMS activity to update.")) -> dict[str, Any]:
    """Update an SMS activity to modify its content, schedule delivery, or send it immediately. Only draft SMS activities can be modified; use status to control whether the SMS is sent immediately (outbox) or scheduled for later delivery (scheduled)."""

    # Construct request model with validation
    try:
        _request = _models.PutActivitySmsIdRequest(
            path=_models.PutActivitySmsIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_sms_activity: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/activity/sms/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/activity/sms/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_sms_activity")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_sms_activity", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_sms_activity",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: SMS
@mcp.tool()
async def delete_sms_activity(id_: str = Field(..., alias="id", description="The unique identifier of the SMS activity record to delete.")) -> dict[str, Any]:
    """Permanently delete a specific SMS activity record by its unique identifier. This action cannot be undone and will remove all associated data."""

    # Construct request model with validation
    try:
        _request = _models.DeleteActivitySmsIdRequest(
            path=_models.DeleteActivitySmsIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_sms_activity: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/activity/sms/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/activity/sms/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_sms_activity")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_sms_activity", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_sms_activity",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: TaskCompleted
@mcp.tool()
async def list_completed_activities(limit: int | None = Field(None, alias="_limit", description="Maximum number of completed activities to return in the response. Must be at least 1.", ge=1)) -> dict[str, Any]:
    """Retrieve a list of completed task activities, with optional filtering by result count. Use this to view historical task completion records."""

    # Construct request model with validation
    try:
        _request = _models.GetActivityTaskCompletedRequest(
            query=_models.GetActivityTaskCompletedRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_completed_activities: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/activity/task_completed"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_completed_activities")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_completed_activities", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_completed_activities",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: TaskCompleted
@mcp.tool()
async def get_completed_task(id_: str = Field(..., alias="id", description="The unique identifier of the completed task activity to retrieve.")) -> dict[str, Any]:
    """Retrieve a single completed task activity by its unique identifier. Use this to fetch details about a specific task that has been marked as completed."""

    # Construct request model with validation
    try:
        _request = _models.GetActivityTaskCompletedIdRequest(
            path=_models.GetActivityTaskCompletedIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_completed_task: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/activity/task_completed/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/activity/task_completed/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_completed_task")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_completed_task", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_completed_task",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: TaskCompleted
@mcp.tool()
async def delete_completed_task(id_: str = Field(..., alias="id", description="The unique identifier of the completed task activity to delete.")) -> dict[str, Any]:
    """Permanently remove a completed task activity from the system. This action cannot be undone and will delete the TaskCompleted activity record and all associated data."""

    # Construct request model with validation
    try:
        _request = _models.DeleteActivityTaskCompletedIdRequest(
            path=_models.DeleteActivityTaskCompletedIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_completed_task: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/activity/task_completed/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/activity/task_completed/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_completed_task")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_completed_task", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_completed_task",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: LeadMerge
@mcp.tool()
async def list_lead_merges(limit: int | None = Field(None, alias="_limit", description="Maximum number of results to return in a single response. Limits the size of the result set.")) -> dict[str, Any]:
    """Retrieve a list of LeadMerge activities, which are created when one lead is merged into another. The source lead is deleted after being merged into the destination lead."""

    # Construct request model with validation
    try:
        _request = _models.GetActivityLeadMergeRequest(
            query=_models.GetActivityLeadMergeRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_lead_merges: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/activity/lead_merge"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_lead_merges")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_lead_merges", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_lead_merges",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: LeadMerge
@mcp.tool()
async def get_lead_merge(id_: str = Field(..., alias="id", description="The unique identifier of the LeadMerge activity to retrieve.")) -> dict[str, Any]:
    """Retrieve a single LeadMerge activity by its ID. Use this to fetch details about a specific lead merge operation."""

    # Construct request model with validation
    try:
        _request = _models.GetActivityLeadMergeIdRequest(
            path=_models.GetActivityLeadMergeIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_lead_merge: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/activity/lead_merge/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/activity/lead_merge/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_lead_merge")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_lead_merge", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_lead_merge",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: WhatsAppMessage
@mcp.tool()
async def list_whatsapp_messages(external_whatsapp_message_id: str | None = Field(None, description="Filter results to a specific WhatsApp message by its external message ID. Useful for locating a message in Close that corresponds to a WhatsApp message that was updated or deleted.")) -> dict[str, Any]:
    """Retrieve WhatsApp message activities from Close, optionally filtered by external WhatsApp message ID. Use this to sync message updates or deletions that occurred in WhatsApp."""

    # Construct request model with validation
    try:
        _request = _models.GetActivityWhatsappMessageRequest(
            query=_models.GetActivityWhatsappMessageRequestQuery(external_whatsapp_message_id=external_whatsapp_message_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_whatsapp_messages: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/activity/whatsapp_message"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_whatsapp_messages")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_whatsapp_messages", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_whatsapp_messages",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: WhatsAppMessage
@mcp.tool()
async def create_whatsapp_message(
    external_whatsapp_message_id: str = Field(..., description="The unique identifier of the message within WhatsApp. Used to track and filter message updates or deletions."),
    message_markdown: str = Field(..., description="The message content formatted in WhatsApp Markdown syntax. The system will automatically convert this to HTML for display."),
    send_to_inbox: bool | None = Field(None, description="Set to true when creating an incoming WhatsApp message to automatically generate a corresponding inbox notification."),
    attachments: list[_models.PostActivityWhatsappMessageBodyAttachmentsItem] | None = Field(None, description="Array of file attachments to include with the message. Files must be pre-uploaded via the Files API. The combined size of all attachments cannot exceed 25MB."),
    integration_link: str | None = Field(None, description="Optional URL pointing back to this message in the external system where it was created, enabling cross-system navigation."),
    response_to_id: str | None = Field(None, description="The Close activity ID of the WhatsApp message this message is replying to (use the Close activity ID starting with 'acti_', not the WhatsApp native message ID)."),
) -> dict[str, Any]:
    """Create a new WhatsApp message activity linked to a Close contact or lead. Supports WhatsApp Markdown formatted text and file attachments (up to 25MB total). Incoming messages can automatically generate inbox notifications."""

    # Construct request model with validation
    try:
        _request = _models.PostActivityWhatsappMessageRequest(
            query=_models.PostActivityWhatsappMessageRequestQuery(send_to_inbox=send_to_inbox),
            body=_models.PostActivityWhatsappMessageRequestBody(external_whatsapp_message_id=external_whatsapp_message_id, message_markdown=message_markdown, attachments=attachments, integration_link=integration_link, response_to_id=response_to_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_whatsapp_message: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/activity/whatsapp_message"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_whatsapp_message")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_whatsapp_message", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_whatsapp_message",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: WhatsAppMessage
@mcp.tool()
async def get_whatsapp_message(id_: str = Field(..., alias="id", description="The unique identifier of the WhatsApp message activity to retrieve.")) -> dict[str, Any]:
    """Retrieve a specific WhatsApp message activity by its unique identifier. Use this to fetch details about a single WhatsApp message interaction."""

    # Construct request model with validation
    try:
        _request = _models.GetActivityWhatsappMessageIdRequest(
            path=_models.GetActivityWhatsappMessageIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_whatsapp_message: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/activity/whatsapp_message/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/activity/whatsapp_message/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_whatsapp_message")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_whatsapp_message", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_whatsapp_message",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: WhatsAppMessage
@mcp.tool()
async def update_whatsapp_message(
    id_: str = Field(..., alias="id", description="The unique identifier of the WhatsApp message activity to update."),
    message_markdown: str | None = Field(None, description="The message body formatted in WhatsApp Markdown syntax for rich text formatting."),
    attachments: list[_models.PutActivityWhatsappMessageIdBodyAttachmentsItem] | None = Field(None, description="Array of file attachments to include with the message. Order is preserved as provided."),
    integration_link: str | None = Field(None, description="A URL that links back to this message in the external system. Must be a valid URI format."),
) -> dict[str, Any]:
    """Update an existing WhatsApp message activity by its ID. Modify the message content, attachments, or external system link."""

    # Construct request model with validation
    try:
        _request = _models.PutActivityWhatsappMessageIdRequest(
            path=_models.PutActivityWhatsappMessageIdRequestPath(id_=id_),
            body=_models.PutActivityWhatsappMessageIdRequestBody(message_markdown=message_markdown, attachments=attachments, integration_link=integration_link)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_whatsapp_message: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/activity/whatsapp_message/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/activity/whatsapp_message/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_whatsapp_message")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_whatsapp_message", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_whatsapp_message",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: WhatsAppMessage
@mcp.tool()
async def delete_whatsapp_message(id_: str = Field(..., alias="id", description="The unique identifier of the WhatsApp message activity to delete.")) -> dict[str, Any]:
    """Delete a WhatsApp message activity by its ID. This removes the activity record from the system."""

    # Construct request model with validation
    try:
        _request = _models.DeleteActivityWhatsappMessageIdRequest(
            path=_models.DeleteActivityWhatsappMessageIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_whatsapp_message: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/activity/whatsapp_message/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/activity/whatsapp_message/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_whatsapp_message")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_whatsapp_message", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_whatsapp_message",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: FormSubmission
@mcp.tool()
async def list_form_submissions(
    organization_id: str | None = Field(None, description="Filter results to form submissions within a specific organization."),
    form_id: str | None = Field(None, description="Filter results to submissions from a specific form by its ID."),
    limit: int | None = Field(None, alias="_limit", description="Maximum number of results to return in the response. Use to control pagination."),
) -> dict[str, Any]:
    """Retrieve a list of form submission activities, with optional filtering by organization and specific form(s). Supports pagination to control result size."""

    # Construct request model with validation
    try:
        _request = _models.GetActivityFormSubmissionRequest(
            query=_models.GetActivityFormSubmissionRequestQuery(organization_id=organization_id, form_id=form_id, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_form_submissions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/activity/form_submission"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_form_submissions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_form_submissions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_form_submissions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: FormSubmission
@mcp.tool()
async def get_form_submission(id_: str = Field(..., alias="id", description="The unique identifier of the form submission activity to retrieve.")) -> dict[str, Any]:
    """Retrieve a single form submission activity by its unique identifier. Use this to fetch details about a specific form submission event."""

    # Construct request model with validation
    try:
        _request = _models.GetActivityFormSubmissionIdRequest(
            path=_models.GetActivityFormSubmissionIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_form_submission: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/activity/form_submission/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/activity/form_submission/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_form_submission")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_form_submission", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_form_submission",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: FormSubmission
@mcp.tool()
async def delete_form_submission(id_: str = Field(..., alias="id", description="The unique identifier of the FormSubmission activity to delete.")) -> dict[str, Any]:
    """Delete a FormSubmission activity by its ID. This operation permanently removes the form submission record from the system."""

    # Construct request model with validation
    try:
        _request = _models.DeleteActivityFormSubmissionIdRequest(
            path=_models.DeleteActivityFormSubmissionIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_form_submission: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/activity/form_submission/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/activity/form_submission/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_form_submission")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_form_submission", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_form_submission",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Opportunities
@mcp.tool()
async def list_opportunities(
    status_type: Literal["active", "won", "lost"] | None = Field(None, description="Filter opportunities by status. Accepts one or multiple values: active, won, or lost."),
    date_won__lte: str | None = Field(None, description="Filter to opportunities won on or before a specific date (ISO 8601 format)."),
    date_won__gte: str | None = Field(None, description="Filter to opportunities won on or after a specific date (ISO 8601 format)."),
    value_period: Literal["one_time", "monthly", "annual"] | None = Field(None, description="Filter opportunities by value period type. Accepts one or multiple values: one_time, monthly, or annual."),
    order_by: Literal["date_won", "-date_won", "date_updated", "-date_updated", "date_created", "-date_created", "confidence", "-confidence", "user_name", "-user_name", "value", "-value", "annualized_value", "-annualized_value", "annualized_expected_value", "-annualized_expected_value"] | None = Field(None, alias="_order_by", description="Sort results by a specified field. Supported fields: date_won, date_updated, date_created, confidence, user_name, value, annualized_value, or annualized_expected_value. Prepend a minus sign for descending order."),
    group_by: Literal["user_id", "-user_id", "date_won__week", "-date_won__week", "date_won__month", "-date_won__month", "date_won__quarter", "-date_won__quarter", "date_won__year", "-date_won__year"] | None = Field(None, alias="_group_by", description="Group results by the specified criteria: user_id, or date_won by week, month, quarter, or year. Prepend a minus sign to reverse the group order."),
    lead_saved_search_id: str | None = Field(None, description="Filter opportunities by a saved lead search (Smart View) ID."),
    limit: int | None = Field(None, alias="_limit", description="Maximum number of results to return in the response."),
) -> dict[str, Any]:
    """Retrieve and filter opportunities with optional filtering by status, dates, value period, and lead. Returns aggregated metrics for all matching opportunities, with support for sorting and grouping."""

    # Construct request model with validation
    try:
        _request = _models.GetOpportunityRequest(
            query=_models.GetOpportunityRequestQuery(status_type=status_type, date_won__lte=date_won__lte, date_won__gte=date_won__gte, value_period=value_period, order_by=order_by, group_by=group_by, lead_saved_search_id=lead_saved_search_id, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_opportunities: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/opportunity"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_opportunities")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_opportunities", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_opportunities",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Opportunities
@mcp.tool()
async def create_opportunity(
    date_won: str | None = Field(None, description="The date when the opportunity was successfully closed and won, specified in date format (YYYY-MM-DD)."),
    confidence: int | None = Field(None, description="The likelihood of winning this opportunity, expressed as a percentage between 0 and 100."),
    value_period: Literal["one_time", "monthly", "annual"] | None = Field(None, description="The billing frequency for the opportunity value: one-time payment, monthly recurring, or annual recurring."),
) -> dict[str, Any]:
    """Create a new sales opportunity. If no lead is associated, a new lead will be automatically created for this opportunity."""

    # Construct request model with validation
    try:
        _request = _models.PostOpportunityRequest(
            body=_models.PostOpportunityRequestBody(date_won=date_won, confidence=confidence, value_period=value_period)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_opportunity: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/opportunity"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_opportunity")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_opportunity", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_opportunity",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Opportunities
@mcp.tool()
async def get_opportunity(id_: str = Field(..., alias="id", description="The unique identifier of the opportunity to retrieve.")) -> dict[str, Any]:
    """Retrieve a single opportunity by its unique identifier. Use this to fetch detailed information about a specific opportunity."""

    # Construct request model with validation
    try:
        _request = _models.GetOpportunityIdRequest(
            path=_models.GetOpportunityIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_opportunity: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/opportunity/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/opportunity/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_opportunity")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_opportunity", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_opportunity",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Opportunities
@mcp.tool()
async def update_opportunity(
    id_: str = Field(..., alias="id", description="The unique identifier of the opportunity to update."),
    date_won: str | None = Field(None, description="The date when the opportunity was won, specified in date format. If not provided and the status is set to won, this will automatically be set to today's date."),
    confidence: int | None = Field(None, description="The confidence level for this opportunity, expressed as a percentage between 0 and 100."),
    value_period: Literal["one_time", "monthly", "annual"] | None = Field(None, description="The billing period for the opportunity value. Choose from one-time, monthly, or annual."),
) -> dict[str, Any]:
    """Update an existing opportunity's details. When the status is set to a won status, the date_won will automatically be set to today if not explicitly provided."""

    # Construct request model with validation
    try:
        _request = _models.PutOpportunityIdRequest(
            path=_models.PutOpportunityIdRequestPath(id_=id_),
            body=_models.PutOpportunityIdRequestBody(date_won=date_won, confidence=confidence, value_period=value_period)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_opportunity: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/opportunity/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/opportunity/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_opportunity")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_opportunity", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_opportunity",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Opportunities
@mcp.tool()
async def delete_opportunity(id_: str = Field(..., alias="id", description="The unique identifier of the opportunity to delete.")) -> dict[str, Any]:
    """Permanently remove an opportunity from the system. This action cannot be undone and will delete all associated data."""

    # Construct request model with validation
    try:
        _request = _models.DeleteOpportunityIdRequest(
            path=_models.DeleteOpportunityIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_opportunity: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/opportunity/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/opportunity/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_opportunity")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_opportunity", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_opportunity",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tasks
@mcp.tool()
async def list_tasks(
    id_: str | None = Field(None, alias="id", description="Filter results to a specific task by its unique identifier."),
    view: Literal["inbox", "future", "archive"] | None = Field(None, description="Use a convenience view to quickly access tasks by status: inbox for incomplete tasks due by end of day, future for incomplete tasks starting tomorrow, or archive for completed tasks only."),
    order_by: Literal["date", "-date", "date_created", "-date_created"] | None = Field(None, alias="_order_by", description="Sort results by task date or creation date in ascending or descending order. Prepend a minus sign for descending order (e.g., -date for newest first)."),
    limit: int | None = Field(None, alias="_limit", description="Limit the number of results returned. Must be at least 1.", ge=1),
) -> dict[str, Any]:
    """Retrieve and filter tasks with support for convenient views and sorting. By default, only lead-type tasks are returned unless filtering by a specific task type."""

    # Construct request model with validation
    try:
        _request = _models.GetTaskRequest(
            query=_models.GetTaskRequestQuery(id_=id_, view=view, order_by=order_by, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_tasks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/task"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_tasks")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_tasks", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_tasks",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tasks
@mcp.tool()
async def create_task(
    type_: Literal["lead", "outgoing_call"] = Field(..., alias="type", description="The category of task to create. Choose either 'lead' for lead follow-up tasks or 'outgoing_call' for call scheduling tasks."),
    date: str | None = Field(None, description="Optional date or date-time when this task should become actionable. Accepts dates in ISO 8601 format (e.g., YYYY-MM-DD or YYYY-MM-DDTHH:mm:ss±HH:mm)."),
) -> dict[str, Any]:
    """Create a new task for follow-up actions. Supports lead and outgoing call task types, with optional scheduling for when the task becomes actionable."""

    # Construct request model with validation
    try:
        _request = _models.PostTaskRequest(
            body=_models.PostTaskRequestBody(type_=type_, date=date)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_task: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/task"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_task")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_task", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_task",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tasks
@mcp.tool()
async def update_tasks(
    id_: str | None = Field(None, alias="id", description="Filter tasks by their unique identifier. Only tasks matching this ID will be updated."),
    is_complete: bool | None = Field(None, description="Mark the task as complete or incomplete. Set to true to mark as done, false to mark as pending."),
    assigned_to: str | None = Field(None, description="Reassign the task to a different user by specifying their user ID."),
    date: str | None = Field(None, description="Set when the task becomes actionable. Accepts a date or full date-time value in ISO 8601 format."),
) -> dict[str, Any]:
    """Bulk-update multiple tasks matching specified filters. Allows updating task completion status, assignment, and actionable date across matching records in a single operation."""

    # Construct request model with validation
    try:
        _request = _models.PutTaskRequest(
            query=_models.PutTaskRequestQuery(id_=id_),
            body=_models.PutTaskRequestBody(is_complete=is_complete, assigned_to=assigned_to, date=date)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_tasks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/task"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_tasks")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_tasks", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_tasks",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tasks
@mcp.tool()
async def get_task(id_: str = Field(..., alias="id", description="The unique identifier of the task to retrieve.")) -> dict[str, Any]:
    """Retrieve detailed information about a specific task by its unique identifier."""

    # Construct request model with validation
    try:
        _request = _models.GetTaskIdRequest(
            path=_models.GetTaskIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_task: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/task/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/task/{id}"
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
async def update_task(
    id_: str = Field(..., alias="id", description="The unique identifier of the task to update."),
    date: str | None = Field(None, description="The date or date-time when the task becomes actionable, specified in ISO 8601 format (e.g., YYYY-MM-DD or YYYY-MM-DDTHH:mm:ss±HH:mm)."),
) -> dict[str, Any]:
    """Update an existing task's properties. You can modify the assignee, due date, and completion status on any task. For lead-type tasks, you can also update the task description text."""

    # Construct request model with validation
    try:
        _request = _models.PutTaskIdRequest(
            path=_models.PutTaskIdRequestPath(id_=id_),
            body=_models.PutTaskIdRequestBody(date=date)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_task: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/task/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/task/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_task")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_task", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_task",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tasks
@mcp.tool()
async def delete_task(id_: str = Field(..., alias="id", description="The unique identifier of the task to delete.")) -> dict[str, Any]:
    """Permanently delete a task by its ID. This action cannot be undone and will remove all associated data."""

    # Construct request model with validation
    try:
        _request = _models.DeleteTaskIdRequest(
            path=_models.DeleteTaskIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_task: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/task/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/task/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_task")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_task", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_task",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Outcomes
@mcp.tool()
async def list_outcomes() -> dict[str, Any]:
    """Retrieve a list of outcomes, with optional filtering capabilities to narrow results based on specific criteria."""

    # Extract parameters for API call
    _http_path = "/outcome"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_outcomes")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_outcomes", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_outcomes",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Outcomes
@mcp.tool()
async def create_outcome(
    name: str = Field(..., description="The display name for this outcome, shown to users whenever they can select or assign outcomes to interactions."),
    applies_to: list[Literal["calls", "meetings"]] = Field(..., description="Specifies which interaction types this outcome can be assigned to. Include 'calls', 'meetings', or both as an array of values."),
    description: str | None = Field(None, description="Optional explanation of what this outcome represents and the circumstances under which it should be used, helping users apply it correctly."),
) -> dict[str, Any]:
    """Create a new outcome for your organization that can be assigned to calls, meetings, or both. Outcomes help track and categorize interactions, with optional automatic assignment for voicemail drops."""

    # Construct request model with validation
    try:
        _request = _models.PostOutcomeRequest(
            body=_models.PostOutcomeRequestBody(name=name, applies_to=applies_to, description=description)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_outcome: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/outcome"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_outcome")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_outcome", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_outcome",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Outcomes
@mcp.tool()
async def get_outcome(id_: str = Field(..., alias="id", description="The unique identifier of the outcome to retrieve.")) -> dict[str, Any]:
    """Retrieve a single outcome by its unique identifier. Use this to fetch detailed information about a specific outcome."""

    # Construct request model with validation
    try:
        _request = _models.GetOutcomeIdRequest(
            path=_models.GetOutcomeIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_outcome: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/outcome/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/outcome/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_outcome")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_outcome", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_outcome",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Outcomes
@mcp.tool()
async def update_outcome(
    id_: str = Field(..., alias="id", description="The unique identifier of the outcome to update."),
    name: str | None = Field(None, description="The new name for the outcome."),
    description: str | None = Field(None, description="The new description for the outcome."),
) -> dict[str, Any]:
    """Update an existing outcome by modifying its name, description, applicable channels, or type. Specify which channels the outcome applies to (calls, meetings) and choose between a predefined vm-dropped type or a custom type."""

    # Construct request model with validation
    try:
        _request = _models.PutOutcomeIdRequest(
            path=_models.PutOutcomeIdRequestPath(id_=id_),
            body=_models.PutOutcomeIdRequestBody(name=name, description=description)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_outcome: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/outcome/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/outcome/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_outcome")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_outcome", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_outcome",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Outcomes
@mcp.tool()
async def delete_outcome(id_: str = Field(..., alias="id", description="The unique identifier of the outcome to delete.")) -> dict[str, Any]:
    """Delete an existing outcome from the system. Associated calls and meetings will retain their references to this outcome, but it will no longer be available for assignment to new calls or meetings."""

    # Construct request model with validation
    try:
        _request = _models.DeleteOutcomeIdRequest(
            path=_models.DeleteOutcomeIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_outcome: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/outcome/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/outcome/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_outcome")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_outcome", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_outcome",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Memberships
@mcp.tool()
async def update_membership(
    id_: str = Field(..., alias="id", description="The unique identifier of the membership to update."),
    role_id: Literal["admin", "superuser", "user", "restricteduser"] | None = Field(None, description="The role to assign to this membership. Choose from predefined roles (admin, superuser, user, restricteduser) or provide a custom Role ID."),
    auto_record_calls: Literal["unset", "disabled", "enabled"] | None = Field(None, description="Automatic call recording preference. Set to 'enabled' to record calls automatically, 'disabled' to prevent recording, or 'unset' to use the default behavior."),
) -> dict[str, Any]:
    """Update a membership's role and call recording settings. Modify the assigned role (admin, superuser, user, restricteduser, or custom) and configure whether calls are automatically recorded."""

    # Construct request model with validation
    try:
        _request = _models.PutMembershipIdRequest(
            path=_models.PutMembershipIdRequestPath(id_=id_),
            body=_models.PutMembershipIdRequestBody(role_id=role_id, auto_record_calls=auto_record_calls)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_membership: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/membership/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/membership/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_membership")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_membership", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_membership",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Memberships
@mcp.tool()
async def provision_membership(
    email: str = Field(..., description="The email address of the user to provision. Must be a valid email format."),
    role_id: str = Field(..., description="The role to assign to the user. Use one of the predefined roles ('admin', 'superuser', 'user', 'restricteduser') or provide a custom Role ID."),
) -> dict[str, Any]:
    """Provision or activate a membership for a user by email address. If the user exists, they are added to your organization; if new, a user account is created. Requires 'Manage Organization' permissions and OAuth authentication."""

    # Construct request model with validation
    try:
        _request = _models.PostMembershipRequest(
            body=_models.PostMembershipRequestBody(email=email, role_id=role_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for provision_membership: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/membership"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("provision_membership")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("provision_membership", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="provision_membership",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Memberships
@mcp.tool()
async def bulk_update_memberships(
    id__in: str = Field(..., description="Comma-separated list of membership IDs to update. All specified memberships will be modified with the provided field values."),
    role_id: Literal["admin", "superuser", "user", "restricteduser"] | None = Field(None, description="Assign a role to the memberships. Valid roles are: admin, superuser, user, or restricteduser."),
    auto_record_calls: Literal["unset", "disabled", "enabled"] | None = Field(None, description="Control automatic call recording for the memberships. Set to enabled to record calls automatically, disabled to prevent recording, or unset to use default behavior."),
) -> dict[str, Any]:
    """Bulk update multiple memberships at once by specifying their IDs and the fields to modify. Supports updating role assignments and call recording settings across multiple memberships in a single request."""

    # Construct request model with validation
    try:
        _request = _models.PutMembershipRequest(
            query=_models.PutMembershipRequestQuery(id__in=id__in),
            body=_models.PutMembershipRequestBody(role_id=role_id, auto_record_calls=auto_record_calls)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for bulk_update_memberships: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/membership"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("bulk_update_memberships")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("bulk_update_memberships", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="bulk_update_memberships",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Memberships
@mcp.tool()
async def list_pinned_views(id_: str = Field(..., alias="id", description="The unique identifier of the membership whose pinned views should be retrieved.")) -> dict[str, Any]:
    """Retrieve the ordered list of pinned views for a specific membership. The views are returned in their pinned order."""

    # Construct request model with validation
    try:
        _request = _models.GetMembershipIdPinnedViewsRequest(
            path=_models.GetMembershipIdPinnedViewsRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_pinned_views: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/membership/{id}/pinned_views", _request.path.model_dump(by_alias=True)) if _request.path else "/membership/{id}/pinned_views"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_pinned_views")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_pinned_views", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_pinned_views",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Memberships
@mcp.tool()
async def set_membership_pinned_views(
    id_: str = Field(..., alias="id", description="The unique identifier of the membership whose pinned views should be updated."),
    body: list[dict[str, Any]] = Field(..., description="An ordered list of view identifiers to pin for this membership. The order determines the display sequence, and providing this list will completely replace any existing pinned views."),
) -> dict[str, Any]:
    """Update the pinned views for a membership by providing an ordered list that completely replaces the current pinned views configuration."""

    # Construct request model with validation
    try:
        _request = _models.PutMembershipIdPinnedViewsRequest(
            path=_models.PutMembershipIdPinnedViewsRequestPath(id_=id_),
            body=_models.PutMembershipIdPinnedViewsRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for set_membership_pinned_views: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/membership/{id}/pinned_views", _request.path.model_dump(by_alias=True)) if _request.path else "/membership/{id}/pinned_views"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("set_membership_pinned_views")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("set_membership_pinned_views", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="set_membership_pinned_views",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Users
@mcp.tool()
async def get_current_user() -> dict[str, Any]:
    """Retrieve the profile and organization information of the currently authenticated user. Use this to determine your user ID and the organization you belong to."""

    # Extract parameters for API call
    _http_path = "/me"
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

# Tags: Users
@mcp.tool()
async def get_user(id_: str = Field(..., alias="id", description="The unique identifier that corresponds to the user record you want to retrieve.")) -> dict[str, Any]:
    """Retrieve a single user by their unique identifier. Returns the user's profile information and details."""

    # Construct request model with validation
    try:
        _request = _models.GetUserIdRequest(
            path=_models.GetUserIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/user/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/user/{id}"
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
async def list_users(limit: int | None = Field(None, alias="_limit", description="Maximum number of user records to return in the response. Use this to control pagination and response size.")) -> dict[str, Any]:
    """Retrieve all users who are members of your organizations. This returns a filtered list based on your organization memberships."""

    # Construct request model with validation
    try:
        _request = _models.GetUserRequest(
            query=_models.GetUserRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_users: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/user"
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

# Tags: Users
@mcp.tool()
async def list_user_availability(organization_id: str | None = Field(None, description="Filter availability results to a specific organization. When omitted, returns availability for all accessible organizations.")) -> dict[str, Any]:
    """Retrieve the current availability status of all users in an organization, including details about any active calls they are participating in."""

    # Construct request model with validation
    try:
        _request = _models.GetUserAvailabilityRequest(
            query=_models.GetUserAvailabilityRequestQuery(organization_id=organization_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_user_availability: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/user/availability"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_user_availability")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_user_availability", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_user_availability",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Organizations
@mcp.tool()
async def get_organization(id_: str = Field(..., alias="id", description="The unique identifier for the organization to retrieve.")) -> dict[str, Any]:
    """Retrieve detailed information about an organization, including its members, inactive members, and associated lead and opportunity statuses. User data is flattened by default but can be nested using query expansion parameters."""

    # Construct request model with validation
    try:
        _request = _models.GetOrganizationIdRequest(
            path=_models.GetOrganizationIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_organization: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organization/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/organization/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_organization")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_organization", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_organization",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Organizations
@mcp.tool()
async def update_organization(
    id_: str = Field(..., alias="id", description="The unique identifier of the organization to update."),
    name: str | None = Field(None, description="The new name for the organization."),
    currency: str | None = Field(None, description="The currency code for the organization (e.g., USD, EUR, GBP)."),
    lead_statuses: list[dict[str, Any]] | None = Field(None, description="An ordered list of existing lead status identifiers to reorder the organization's lead pipeline. The order in this array determines the sequence of statuses in the workflow."),
) -> dict[str, Any]:
    """Update an organization's basic settings including name and currency, and reorder its lead status pipeline."""

    # Construct request model with validation
    try:
        _request = _models.PutOrganizationIdRequest(
            path=_models.PutOrganizationIdRequestPath(id_=id_),
            body=_models.PutOrganizationIdRequestBody(name=name, currency=currency, lead_statuses=lead_statuses)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_organization: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organization/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/organization/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_organization")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_organization", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_organization",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Roles
@mcp.tool()
async def get_role(id_: str = Field(..., alias="id", description="The unique identifier of the role to retrieve.")) -> dict[str, Any]:
    """Retrieve a single role by its unique identifier. Use this to fetch detailed information about a specific role."""

    # Construct request model with validation
    try:
        _request = _models.GetRoleIdRequest(
            path=_models.GetRoleIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_role: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/role/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/role/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_role")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_role", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_role",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Roles
@mcp.tool()
async def list_roles() -> dict[str, Any]:
    """Retrieve all roles defined in your organization. Use this to view available role configurations for access control and permission management."""

    # Extract parameters for API call
    _http_path = "/role"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_roles")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_roles", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_roles",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Roles
@mcp.tool()
async def create_role(
    name: str = Field(..., description="The display name for this role."),
    visibility_user_lcf_ids: list[str] | None = Field(None, description="List of Lead Custom Field IDs that determine which leads users with this role can access. Leave empty if the role has the view_all_leads permission."),
    visibility_user_lcf_behavior: Literal["require_assignment", "allow_unassigned"] | None = Field(None, description="Determines how lead visibility is handled for leads without assigned users. Choose 'require_assignment' to hide unassigned leads or 'allow_unassigned' to show them. Leave empty if the role has the view_all_leads permission."),
    permissions: list[str] | None = Field(None, description="List of permission strings that define what actions users with this role can perform."),
) -> dict[str, Any]:
    """Create a new role with customizable permissions and lead visibility settings. Lead visibility can be restricted to specific custom fields or granted universally based on role permissions."""

    # Construct request model with validation
    try:
        _request = _models.PostRoleRequest(
            body=_models.PostRoleRequestBody(visibility_user_lcf_ids=visibility_user_lcf_ids, visibility_user_lcf_behavior=visibility_user_lcf_behavior, name=name, permissions=permissions)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_role: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/role"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_role")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_role", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_role",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Roles
@mcp.tool()
async def update_role(
    role_id: str = Field(..., description="The unique identifier of the role to update."),
    name: str | None = Field(None, description="The display name for the role."),
    visibility_user_lcf_ids: list[str] | None = Field(None, description="A list of Lead Custom Field IDs that determine which leads are visible to users with this role. The order of IDs may affect visibility logic based on the configured behavior."),
    visibility_user_lcf_behavior: Literal["require_assignment", "allow_unassigned"] | None = Field(None, description="Controls how lead visibility is handled for leads without assigned users. Use 'require_assignment' to hide unassigned leads, or 'allow_unassigned' to show them regardless of assignment status."),
) -> dict[str, Any]:
    """Update an existing role's properties, including its name and lead visibility settings based on custom field criteria."""

    # Construct request model with validation
    try:
        _request = _models.PutRoleRoleIdRequest(
            path=_models.PutRoleRoleIdRequestPath(role_id=role_id),
            body=_models.PutRoleRoleIdRequestBody(name=name, visibility_user_lcf_ids=visibility_user_lcf_ids, visibility_user_lcf_behavior=visibility_user_lcf_behavior)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_role: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/role/{role_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/role/{role_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_role")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_role", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_role",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Roles
@mcp.tool()
async def delete_role(role_id: str = Field(..., description="The unique identifier of the role to delete.")) -> dict[str, Any]:
    """Permanently remove a role from the system. All users currently assigned to this role must be reassigned to another role before deletion can proceed."""

    # Construct request model with validation
    try:
        _request = _models.DeleteRoleRoleIdRequest(
            path=_models.DeleteRoleRoleIdRequestPath(role_id=role_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_role: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/role/{role_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/role/{role_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_role")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_role", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_role",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Lead Statuses
@mcp.tool()
async def list_lead_statuses() -> dict[str, Any]:
    """Retrieve all available lead statuses configured for your organization. Use this to understand the valid status values for lead management workflows."""

    # Extract parameters for API call
    _http_path = "/status/lead"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_lead_statuses")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_lead_statuses", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_lead_statuses",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Lead Statuses
@mcp.tool()
async def create_lead_status(label: str = Field(..., description="The display name for this lead status, shown in the UI and status selection dropdowns throughout the system.")) -> dict[str, Any]:
    """Create a new custom status that can be assigned to leads in your pipeline. This allows you to define custom workflow stages beyond the default statuses."""

    # Construct request model with validation
    try:
        _request = _models.PostStatusLeadRequest(
            body=_models.PostStatusLeadRequestBody(label=label)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_lead_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/status/lead"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_lead_status")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_lead_status", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_lead_status",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Lead Statuses
@mcp.tool()
async def rename_lead_status(
    status_id: str = Field(..., description="The unique identifier of the lead status to rename."),
    name: str = Field(..., description="The new display name for the lead status."),
) -> dict[str, Any]:
    """Rename an existing lead status to update its display name. This operation modifies the status label itself, not the status of individual leads."""

    # Construct request model with validation
    try:
        _request = _models.PutStatusLeadStatusIdRequest(
            path=_models.PutStatusLeadStatusIdRequestPath(status_id=status_id),
            body=_models.PutStatusLeadStatusIdRequestBody(name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for rename_lead_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/status/lead/{status_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/status/lead/{status_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("rename_lead_status")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("rename_lead_status", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="rename_lead_status",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Lead Statuses
@mcp.tool()
async def delete_lead_status(status_id: str = Field(..., description="The unique identifier of the lead status to delete.")) -> dict[str, Any]:
    """Delete a lead status from the system. Ensure no leads are currently assigned to this status before deletion, as the operation will fail if leads depend on it."""

    # Construct request model with validation
    try:
        _request = _models.DeleteStatusLeadStatusIdRequest(
            path=_models.DeleteStatusLeadStatusIdRequestPath(status_id=status_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_lead_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/status/lead/{status_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/status/lead/{status_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_lead_status")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_lead_status", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_lead_status",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Opportunity Statuses
@mcp.tool()
async def list_opportunity_statuses() -> dict[str, Any]:
    """Retrieve all opportunity statuses configured for your organization. Use this to understand the available status values for opportunities in your system."""

    # Extract parameters for API call
    _http_path = "/status/opportunity"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_opportunity_statuses")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_opportunity_statuses", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_opportunity_statuses",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Opportunity Statuses
@mcp.tool()
async def create_opportunity_status(
    label: str = Field(..., description="The display name for this opportunity status, used to identify it in the UI and reports."),
    status_type: Literal["active", "won", "lost"] = Field(..., description="The classification type for this status: active for ongoing opportunities, won for closed deals, or lost for deals that did not close."),
    pipeline_id: str | None = Field(None, description="Optional pipeline ID to scope this status to a specific pipeline; if omitted, the status will be available globally."),
) -> dict[str, Any]:
    """Create a new opportunity status to track deal progression. Statuses can be classified as active, won, or lost, and can optionally be associated with a specific pipeline."""

    # Construct request model with validation
    try:
        _request = _models.PostStatusOpportunityRequest(
            body=_models.PostStatusOpportunityRequestBody(label=label, status_type=status_type, pipeline_id=pipeline_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_opportunity_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/status/opportunity"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_opportunity_status")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_opportunity_status", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_opportunity_status",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Opportunity Statuses
@mcp.tool()
async def rename_opportunity_status(
    status_id: str = Field(..., description="The unique identifier of the opportunity status to rename."),
    label: str = Field(..., description="The new display name for the opportunity status that will be shown in the system."),
) -> dict[str, Any]:
    """Update the display name of an existing opportunity status. This allows you to change how a status appears throughout the system."""

    # Construct request model with validation
    try:
        _request = _models.PutStatusOpportunityStatusIdRequest(
            path=_models.PutStatusOpportunityStatusIdRequestPath(status_id=status_id),
            body=_models.PutStatusOpportunityStatusIdRequestBody(label=label)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for rename_opportunity_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/status/opportunity/{status_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/status/opportunity/{status_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("rename_opportunity_status")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("rename_opportunity_status", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="rename_opportunity_status",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Opportunity Statuses
@mcp.tool()
async def delete_opportunity_status(status_id: str = Field(..., description="The unique identifier of the opportunity status to delete.")) -> dict[str, Any]:
    """Delete an opportunity status from the system. Ensure no opportunities are currently assigned this status before deletion."""

    # Construct request model with validation
    try:
        _request = _models.DeleteStatusOpportunityStatusIdRequest(
            path=_models.DeleteStatusOpportunityStatusIdRequestPath(status_id=status_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_opportunity_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/status/opportunity/{status_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/status/opportunity/{status_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_opportunity_status")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_opportunity_status", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_opportunity_status",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipelines
@mcp.tool()
async def list_pipelines() -> dict[str, Any]:
    """Retrieve all pipelines configured in your organization. Use this to view available pipeline definitions and their current status."""

    # Extract parameters for API call
    _http_path = "/pipeline"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_pipelines")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_pipelines", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_pipelines",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipelines
@mcp.tool()
async def create_pipeline(name: str = Field(..., description="A unique identifier for the pipeline. This name is used to reference and manage the pipeline in subsequent operations.")) -> dict[str, Any]:
    """Create a new pipeline with the specified name. The pipeline serves as a container for organizing and executing workflow operations."""

    # Construct request model with validation
    try:
        _request = _models.PostPipelineRequest(
            body=_models.PostPipelineRequestBody(name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_pipeline: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/pipeline"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_pipeline")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_pipeline", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_pipeline",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipelines
@mcp.tool()
async def update_pipeline(
    pipeline_id: str = Field(..., description="The unique identifier of the pipeline to update."),
    name: str | None = Field(None, description="The new name to assign to the pipeline."),
    statuses: list[_models.PutPipelinePipelineIdBodyStatusesItem] | None = Field(None, description="An ordered list of opportunity status objects that defines the pipeline's status workflow. Each object must include an 'id' field referencing the status. The order of items in this list determines the sequence of statuses in the pipeline. You can reorder existing statuses or include statuses from other pipelines by their ID to move them into this pipeline."),
) -> dict[str, Any]:
    """Update an existing pipeline by modifying its name, reordering opportunity statuses, or moving statuses from other pipelines into this one."""

    # Construct request model with validation
    try:
        _request = _models.PutPipelinePipelineIdRequest(
            path=_models.PutPipelinePipelineIdRequestPath(pipeline_id=pipeline_id),
            body=_models.PutPipelinePipelineIdRequestBody(name=name, statuses=statuses)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_pipeline: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/pipeline/{pipeline_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/pipeline/{pipeline_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_pipeline")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_pipeline", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_pipeline",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipelines
@mcp.tool()
async def delete_pipeline(pipeline_id: str = Field(..., description="The unique identifier of the pipeline to delete.")) -> dict[str, Any]:
    """Permanently delete a pipeline from your workspace. The pipeline must be empty of all opportunity statuses before deletion—migrate or remove any existing opportunity statuses first."""

    # Construct request model with validation
    try:
        _request = _models.DeletePipelinePipelineIdRequest(
            path=_models.DeletePipelinePipelineIdRequestPath(pipeline_id=pipeline_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_pipeline: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/pipeline/{pipeline_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/pipeline/{pipeline_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_pipeline")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_pipeline", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_pipeline",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Groups
@mcp.tool()
async def list_groups(fields: str = Field(..., alias="_fields", description="Comma-separated list of group attributes to return in the response. Must include at least 'name' and 'members' to retrieve group membership data.")) -> dict[str, Any]:
    """Retrieve all groups in your organization. Use the _fields parameter to specify which group attributes to return; to retrieve group members, include 'members' in your field selection."""

    # Construct request model with validation
    try:
        _request = _models.GetGroupRequest(
            query=_models.GetGroupRequestQuery(fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_groups: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/group"
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
async def create_group(
    fields: str = Field(..., alias="_fields", description="Comma-separated list of fields to include in the response. Must include at least 'name' and 'members'."),
    name: str = Field(..., description="The display name for the new group."),
) -> dict[str, Any]:
    """Create a new empty group with a specified name. Members can be added or removed after creation using the member endpoint."""

    # Construct request model with validation
    try:
        _request = _models.PostGroupRequest(
            query=_models.PostGroupRequestQuery(fields=fields),
            body=_models.PostGroupRequestBody(name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/group"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
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
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Groups
@mcp.tool()
async def get_group(
    group_id: str = Field(..., description="The unique identifier of the group to retrieve."),
    fields: str = Field(..., alias="_fields", description="Comma-separated list of fields to include in the response. Must include at least 'name' and 'members' to retrieve group name and member data."),
) -> dict[str, Any]:
    """Retrieve a single group by its ID with specified fields. Returns group details including name and member information."""

    # Construct request model with validation
    try:
        _request = _models.GetGroupGroupIdRequest(
            path=_models.GetGroupGroupIdRequestPath(group_id=group_id),
            query=_models.GetGroupGroupIdRequestQuery(fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/group/{group_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/group/{group_id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_group")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_group", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_group",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Groups
@mcp.tool()
async def rename_group(
    group_id: str = Field(..., description="The unique identifier of the group to update."),
    name: str | None = Field(None, description="The new name for the group. Must be unique and cannot duplicate existing group names."),
) -> dict[str, Any]:
    """Update a group's name. The new name must be unique across all groups in the system."""

    # Construct request model with validation
    try:
        _request = _models.PutGroupGroupIdRequest(
            path=_models.PutGroupGroupIdRequestPath(group_id=group_id),
            body=_models.PutGroupGroupIdRequestBody(name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for rename_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/group/{group_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/group/{group_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("rename_group")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("rename_group", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="rename_group",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Groups
@mcp.tool()
async def delete_group(group_id: str = Field(..., description="The unique identifier of the group to delete.")) -> dict[str, Any]:
    """Delete a group from the system. This operation is only permitted if the group is not referenced by any saved reports or smart views."""

    # Construct request model with validation
    try:
        _request = _models.DeleteGroupGroupIdRequest(
            path=_models.DeleteGroupGroupIdRequestPath(group_id=group_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/group/{group_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/group/{group_id}"
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
        headers=_http_headers,
    )

    return _response_data

# Tags: Groups
@mcp.tool()
async def add_user_to_group(
    group_id: str = Field(..., description="The unique identifier of the group where the user will be added."),
    user_id: str = Field(..., description="The unique identifier of the user to add to the group."),
) -> dict[str, Any]:
    """Add a user to a group. If the user is already a member, the operation completes without changes."""

    # Construct request model with validation
    try:
        _request = _models.PostGroupGroupIdMemberRequest(
            path=_models.PostGroupGroupIdMemberRequestPath(group_id=group_id),
            body=_models.PostGroupGroupIdMemberRequestBody(user_id=user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_user_to_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/group/{group_id}/member", _request.path.model_dump(by_alias=True)) if _request.path else "/group/{group_id}/member"
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
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Groups
@mcp.tool()
async def remove_group_member(
    group_id: str = Field(..., description="The unique identifier of the group from which the user will be removed."),
    user_id: str = Field(..., description="The unique identifier of the user to remove from the group."),
) -> dict[str, Any]:
    """Remove a user from a group. If the user is not currently a member, the operation completes without error."""

    # Construct request model with validation
    try:
        _request = _models.DeleteGroupGroupIdMemberUserIdRequest(
            path=_models.DeleteGroupGroupIdMemberUserIdRequestPath(group_id=group_id, user_id=user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_group_member: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/group/{group_id}/member/{user_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/group/{group_id}/member/{user_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_group_member")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_group_member", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_group_member",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Reporting
@mcp.tool()
async def list_activity_metrics() -> dict[str, Any]:
    """Retrieve the predefined metrics available for use in activity reports. Use this to discover which metrics can be included when building or querying activity report data."""

    # Extract parameters for API call
    _http_path = "/report/activity/metrics"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_activity_metrics")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_activity_metrics", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_activity_metrics",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Reporting
@mcp.tool()
async def generate_activity_report(
    type_: Literal["overview", "comparison"] = Field(..., alias="type", description="Report structure type: 'overview' aggregates metrics across the organization by time period, while 'comparison' breaks down metrics by individual users."),
    metrics: list[str] = Field(..., description="List of metric names to include in the report. Specify which data points should be calculated and returned."),
    accept: Literal["application/json", "text/csv"] | None = Field(None, alias="Accept", description="Desired response format: JSON for structured data or CSV for spreadsheet export."),
    relative_range: Literal["today", "this-week", "this-month", "this-quarter", "this-year", "yesterday", "last-week", "last-month", "last-quarter", "last-year", "all-time"] | None = Field(None, description="Relative time range for the report data, such as 'today', 'this-week', 'last-month', or 'all-time'. Use this or datetime_range, but not both."),
    saved_search_id: str | None = Field(None, description="ID of a previously saved search configuration to apply filters and settings to this report."),
    users: list[str] | None = Field(None, description="List of user IDs to filter report results to specific users. When provided, only data for these users will be included."),
) -> dict[str, Any]:
    """Generate an activity report showing organizational metrics aggregated by time period (overview) or broken down by user (comparison). Reports can be returned as JSON or CSV format."""

    # Construct request model with validation
    try:
        _request = _models.PostReportActivityRequest(
            header=_models.PostReportActivityRequestHeader(accept=accept),
            body=_models.PostReportActivityRequestBody(type_=type_, metrics=metrics, relative_range=relative_range, users=users,
                query=_models.PostReportActivityRequestBodyQuery(saved_search_id=saved_search_id) if any(v is not None for v in [saved_search_id]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for generate_activity_report: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/report/activity"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("generate_activity_report")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("generate_activity_report", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="generate_activity_report",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Reporting
@mcp.tool()
async def list_sent_emails_report(
    organization_id: str = Field(..., description="The unique identifier of the organization for which to retrieve the sent emails report."),
    date_start: str | None = Field(None, description="The start date for filtering the report period, specified in date format (YYYY-MM-DD). If provided, only emails sent on or after this date will be included."),
    date_end: str | None = Field(None, description="The end date for filtering the report period, specified in date format (YYYY-MM-DD). If provided, only emails sent on or before this date will be included."),
) -> dict[str, Any]:
    """Retrieve a report of sent emails grouped by template for a specific organization, optionally filtered by a date range."""

    # Construct request model with validation
    try:
        _request = _models.GetReportSentEmailsOrganizationIdRequest(
            path=_models.GetReportSentEmailsOrganizationIdRequestPath(organization_id=organization_id),
            query=_models.GetReportSentEmailsOrganizationIdRequestQuery(date_start=date_start, date_end=date_end)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_sent_emails_report: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/report/sent_emails/{organization_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/report/sent_emails/{organization_id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_sent_emails_report")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_sent_emails_report", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_sent_emails_report",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Reporting
@mcp.tool()
async def get_lead_status_report(
    organization_id: str = Field(..., description="The unique identifier for the organization whose lead status changes should be reported."),
    date_start: str | None = Field(None, description="The start date for the report period in date format. If provided, only status changes on or after this date will be included."),
    date_end: str | None = Field(None, description="The end date for the report period in date format. If provided, only status changes on or before this date will be included."),
) -> dict[str, Any]:
    """Retrieve a report of lead status changes for a specific organization, with optional filtering by date range to analyze lead progression over time."""

    # Construct request model with validation
    try:
        _request = _models.GetReportStatusesLeadOrganizationIdRequest(
            path=_models.GetReportStatusesLeadOrganizationIdRequestPath(organization_id=organization_id),
            query=_models.GetReportStatusesLeadOrganizationIdRequestQuery(date_start=date_start, date_end=date_end)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_lead_status_report: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/report/statuses/lead/{organization_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/report/statuses/lead/{organization_id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_lead_status_report")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_lead_status_report", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_lead_status_report",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Reporting
@mcp.tool()
async def get_opportunity_status_report(
    organization_id: str = Field(..., description="The unique identifier of the organization for which to retrieve the opportunity status report."),
    date_start: str | None = Field(None, description="The start date for the report period in date format (YYYY-MM-DD). If omitted, the report begins from the earliest available data."),
    date_end: str | None = Field(None, description="The end date for the report period in date format (YYYY-MM-DD). If omitted, the report extends to the current date."),
) -> dict[str, Any]:
    """Retrieve a report of opportunity status changes for an organization over a specified period. Use this to track how opportunities progress through different stages."""

    # Construct request model with validation
    try:
        _request = _models.GetReportStatusesOpportunityOrganizationIdRequest(
            path=_models.GetReportStatusesOpportunityOrganizationIdRequestPath(organization_id=organization_id),
            query=_models.GetReportStatusesOpportunityOrganizationIdRequestQuery(date_start=date_start, date_end=date_end)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_opportunity_status_report: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/report/statuses/opportunity/{organization_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/report/statuses/opportunity/{organization_id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_opportunity_status_report")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_opportunity_status_report", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_opportunity_status_report",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Reporting
@mcp.tool()
async def generate_custom_report(
    organization_id: str = Field(..., description="The organization ID for which to generate the report."),
    x: str | None = Field(None, description="The field to display on the X axis, using dot notation (e.g., 'lead.custom.MRR' or 'opportunity.date_created'). Can be a date field for time-based graphs or numeric field for numeric binning."),
    y: str | None = Field(None, description="The metric to display on the Y axis using dot notation (e.g., 'lead.count', 'call.duration', 'opportunity.value'). Must be a numeric field. Defaults to counting leads."),
    interval: Literal["auto", "hour", "day", "week", "month", "quarter", "year"] | None = Field(None, description="Controls how the X axis is divided into buckets. For time-based X fields, choose from hourly, daily, weekly, monthly, quarterly, or yearly intervals; 'auto' automatically selects the best interval. For numeric X fields, specify an integer interval size. Defaults to automatic selection."),
    transform_y: Literal["sum", "avg", "min", "max"] | None = Field(None, description="Aggregation function applied to Y values within each bucket: sum (total), avg (average), min (minimum), or max (maximum). Defaults to sum."),
    group_by: str | None = Field(None, description="Optional field name to split the report into separate series, one per unique value of this field."),
    start: str | None = Field(None, description="Start of the X axis range. For date fields, use ISO 8601 format; defaults to the organization's creation date. For numeric fields, provide the numeric start value."),
    end: str | None = Field(None, description="End of the X axis range. For date fields, use ISO 8601 format; defaults to the current date/time. For numeric fields, provide the numeric end value."),
) -> dict[str, Any]:
    """Generate a custom report with arbitrary metrics for data visualization. Returns aggregated data suitable for graphing, supporting flexible field selection, time-based or numeric binning, and optional grouping by category."""

    # Construct request model with validation
    try:
        _request = _models.GetReportCustomOrganizationIdRequest(
            path=_models.GetReportCustomOrganizationIdRequestPath(organization_id=organization_id),
            query=_models.GetReportCustomOrganizationIdRequestQuery(x=x, y=y, interval=interval, transform_y=transform_y, group_by=group_by, start=start, end=end)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for generate_custom_report: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/report/custom/{organization_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/report/custom/{organization_id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("generate_custom_report")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("generate_custom_report", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="generate_custom_report",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Reporting
@mcp.tool()
async def list_custom_report_fields() -> dict[str, Any]:
    """Retrieve all available custom report fields that can be used when building custom reports. Only numeric data type fields are eligible for use as the y-axis parameter in report visualizations."""

    # Extract parameters for API call
    _http_path = "/report/custom/fields"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_custom_report_fields")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_custom_report_fields", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_custom_report_fields",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Reporting
@mcp.tool()
async def get_funnel_opportunity_totals(
    pipeline: str = Field(..., description="The pipeline ID that defines the funnel stages used to categorize and aggregate the opportunity data."),
    type_: Literal["created-cohort", "active-stage-cohort"] = Field(..., alias="type", description="The report type determines how opportunities are grouped. Use 'created-cohort' to analyze opportunities by creation date, or 'active-stage-cohort' to analyze opportunities currently in specific pipeline stages."),
    accept: Literal["application/json", "text/csv"] | None = Field(None, description="Response format for the report data. Use application/json to receive both aggregated totals and per-user metrics, or text/csv to receive per-user data only."),
    query_type: Literal["saved_search"] | None = Field(None, alias="queryType", description="The query type for filtering opportunities. Currently supports 'saved_search' to use a predefined saved search query."),
    report_datetime_range: dict[str, Any] | None = Field(None, description="Optional time range to filter the report data. Specify the period for which funnel metrics should be calculated."),
    cohort_datetime_range: dict[str, Any] | None = Field(None, description="Time range defining which opportunities to include in the cohort. Required when using 'created-cohort' report type (or provide cohort_relative_range instead). Ignored for 'active-stage-cohort' reports."),
    compared_datetime_range: Literal["same-days-last-week", "same-days-last-month", "same-days-last-quarter", "same-days-last-year"] | None = Field(None, description="Relative time range for comparison data, such as same period from previous week, month, quarter, or year. Only applicable when report_datetime_range or cohort_datetime_range is specified."),
    compared_custom_range: dict[str, Any] | None = Field(None, description="Custom absolute time range for comparison data. Use as an alternative to compared_datetime_range for specific comparison periods."),
    saved_search_id: str | None = Field(None, description="ID of a saved search to use for filtering opportunities in the report. Used when query.type is set to 'saved_search'."),
    users: list[str] | None = Field(None, description="List of user IDs or group IDs to limit report results to specific team members or groups. Leave empty to include all available users in the aggregation."),
) -> dict[str, Any]:
    """Retrieve aggregated and per-user pipeline funnel metrics for selected opportunities. Returns totals data in JSON format with optional per-user breakdown, or CSV format for per-user data only."""

    # Construct request model with validation
    try:
        _request = _models.PostReportFunnelOpportunityTotalsRequest(
            header=_models.PostReportFunnelOpportunityTotalsRequestHeader(accept=accept),
            body=_models.PostReportFunnelOpportunityTotalsRequestBody(pipeline=pipeline, type_=type_, report_datetime_range=report_datetime_range, cohort_datetime_range=cohort_datetime_range, compared_datetime_range=compared_datetime_range, compared_custom_range=compared_custom_range, users=users,
                query=_models.PostReportFunnelOpportunityTotalsRequestBodyQuery(type_=query_type, saved_search_id=saved_search_id) if any(v is not None for v in [query_type, saved_search_id]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_funnel_opportunity_totals: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/report/funnel/opportunity/totals"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_funnel_opportunity_totals")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_funnel_opportunity_totals", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_funnel_opportunity_totals",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Reporting
@mcp.tool()
async def get_opportunity_funnel_stages_report(
    pipeline: str = Field(..., description="The pipeline ID that defines the funnel stages to report on."),
    type_: Literal["created-cohort", "active-stage-cohort"] = Field(..., alias="type", description="The report type: 'created-cohort' tracks opportunities created within a cohort period, while 'active-stage-cohort' tracks opportunities currently in each stage."),
    query_type: Literal["saved_search"] | None = Field(None, alias="queryType", description="The query type for filtering; currently supports 'saved_search' to apply a predefined search filter."),
    report_datetime_range: dict[str, Any] | None = Field(None, description="The primary time range for the report data. Required for active-stage-cohort reports unless using a comparison range."),
    cohort_datetime_range: dict[str, Any] | None = Field(None, description="The time range defining which opportunities to include in the cohort. Required for created-cohort reports unless using a relative range. Ignored for active-stage-cohort reports."),
    compared_datetime_range: Literal["same-days-last-week", "same-days-last-month", "same-days-last-quarter", "same-days-last-year"] | None = Field(None, description="A relative time period to compare against the primary range: same days from the previous week, month, quarter, or year. Only valid when paired with report_datetime_range or cohort_datetime_range."),
    compared_custom_range: dict[str, Any] | None = Field(None, description="A custom time range for comparison data. Allows comparing against any specific period, not just relative ranges."),
    saved_search_id: str | None = Field(None, description="The ID of a saved search to filter report results. When specified, only opportunities matching the saved search criteria are included."),
    users: list[str] | None = Field(None, description="A list of user IDs or group IDs to limit results to. When empty or omitted, the report includes all available users."),
) -> dict[str, Any]:
    """Retrieve a funnel report showing pipeline metrics for opportunities aggregated by stage or per-user. Supports comparison against previous time periods and filtering by saved searches or specific users."""

    # Construct request model with validation
    try:
        _request = _models.PostReportFunnelOpportunityStagesRequest(
            body=_models.PostReportFunnelOpportunityStagesRequestBody(pipeline=pipeline, type_=type_, report_datetime_range=report_datetime_range, cohort_datetime_range=cohort_datetime_range, compared_datetime_range=compared_datetime_range, compared_custom_range=compared_custom_range, users=users,
                query=_models.PostReportFunnelOpportunityStagesRequestBodyQuery(type_=query_type, saved_search_id=saved_search_id) if any(v is not None for v in [query_type, saved_search_id]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_opportunity_funnel_stages_report: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/report/funnel/opportunity/stages"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_opportunity_funnel_stages_report")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_opportunity_funnel_stages_report", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_opportunity_funnel_stages_report",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Email Templates
@mcp.tool()
async def list_email_templates(
    is_archived: bool | None = Field(None, description="Filter results to show only archived templates (true), only active templates (false), or all templates regardless of status (omit parameter). Useful for managing template lifecycle."),
    limit: int | None = Field(None, alias="_limit", description="Limit the number of templates returned in the response. Helps with pagination and controlling response size for large template collections."),
) -> dict[str, Any]:
    """Retrieve a list of email templates with optional filtering by archived status and pagination support. Use this to browse available templates for sending emails or managing template collections."""

    # Construct request model with validation
    try:
        _request = _models.GetEmailTemplateRequest(
            query=_models.GetEmailTemplateRequestQuery(is_archived=is_archived, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_email_templates: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/email_template"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_email_templates")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_email_templates", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_email_templates",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Email Templates
@mcp.tool()
async def create_email_template(body: dict[str, Any] = Field(..., description="Email template configuration object containing template name, subject, body content, and any variable placeholders for dynamic content insertion.")) -> dict[str, Any]:
    """Create a new email template that can be used for sending standardized emails. Define the template structure, content, and variables for reuse across email communications."""

    # Construct request model with validation
    try:
        _request = _models.PostEmailTemplateRequest(
            body=_models.PostEmailTemplateRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_email_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/email_template"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_email_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_email_template", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_email_template",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Email Templates
@mcp.tool()
async def get_email_template(id_: str = Field(..., alias="id", description="The unique identifier of the email template to retrieve.")) -> dict[str, Any]:
    """Retrieve a specific email template by its unique identifier. Use this to fetch the full details of an email template for viewing or further processing."""

    # Construct request model with validation
    try:
        _request = _models.GetEmailTemplateIdRequest(
            path=_models.GetEmailTemplateIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_email_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/email_template/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/email_template/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_email_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_email_template", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_email_template",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Email Templates
@mcp.tool()
async def update_email_template(
    id_: str = Field(..., alias="id", description="The unique identifier of the email template to update."),
    name: str | None = Field(None, description="The display name for the email template."),
    subject: str | None = Field(None, description="The subject line that will appear in emails sent using this template."),
    body: str | None = Field(None, description="The HTML or plain text content of the email body."),
    is_shared: bool | None = Field(None, description="Whether this template is accessible to other members of your organization."),
    is_archived: bool | None = Field(None, description="Whether this template is archived and hidden from active template lists."),
) -> dict[str, Any]:
    """Update an existing email template by modifying its content, metadata, or organizational settings. Specify the template ID and provide any fields you want to change; omitted fields remain unchanged."""

    # Construct request model with validation
    try:
        _request = _models.PutEmailTemplateIdRequest(
            path=_models.PutEmailTemplateIdRequestPath(id_=id_),
            body=_models.PutEmailTemplateIdRequestBody(name=name, subject=subject, body=body, is_shared=is_shared, is_archived=is_archived)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_email_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/email_template/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/email_template/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_email_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_email_template", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_email_template",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Email Templates
@mcp.tool()
async def delete_email_template(id_: str = Field(..., alias="id", description="The unique identifier of the email template to delete.")) -> dict[str, Any]:
    """Permanently delete an email template by its ID. This action cannot be undone and will remove the template from all systems."""

    # Construct request model with validation
    try:
        _request = _models.DeleteEmailTemplateIdRequest(
            path=_models.DeleteEmailTemplateIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_email_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/email_template/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/email_template/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_email_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_email_template", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_email_template",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Email Templates
@mcp.tool()
async def render_email_template(
    id_: str = Field(..., alias="id", description="The unique identifier of the email template to render."),
    entry: int | None = Field(None, description="When rendering from search query results, the zero-based index of the lead/contact to use (0-99). Omit this parameter when rendering for a specific lead/contact.", ge=0, le=99),
) -> dict[str, Any]:
    """Render an email template with actual data for a specific lead or contact. Supports rendering against a single lead/contact or previewing from a search query result."""

    # Construct request model with validation
    try:
        _request = _models.GetEmailTemplateIdRenderRequest(
            path=_models.GetEmailTemplateIdRenderRequestPath(id_=id_),
            query=_models.GetEmailTemplateIdRenderRequestQuery(entry=entry)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for render_email_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/email_template/{id}/render", _request.path.model_dump(by_alias=True)) if _request.path else "/email_template/{id}/render"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("render_email_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("render_email_template", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="render_email_template",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: SMS Templates
@mcp.tool()
async def list_sms_templates(limit: int | None = Field(None, alias="_limit", description="Maximum number of SMS templates to return in a single response. Useful for controlling result set size in paginated requests.")) -> dict[str, Any]:
    """Retrieve a paginated list of SMS templates available in your account. Use the limit parameter to control the number of results returned."""

    # Construct request model with validation
    try:
        _request = _models.GetSmsTemplateRequest(
            query=_models.GetSmsTemplateRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_sms_templates: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/sms_template"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_sms_templates")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_sms_templates", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_sms_templates",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: SMS Templates
@mcp.tool()
async def create_sms_template(body: dict[str, Any] = Field(..., description="Template configuration object containing the SMS template details such as name, content, and any variable placeholders for personalization.")) -> dict[str, Any]:
    """Create a new SMS template that can be used for sending standardized text messages. Define the template content and configuration for reuse across SMS campaigns."""

    # Construct request model with validation
    try:
        _request = _models.PostSmsTemplateRequest(
            body=_models.PostSmsTemplateRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_sms_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/sms_template"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_sms_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_sms_template", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_sms_template",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: SMS Templates
@mcp.tool()
async def get_sms_template(id_: str = Field(..., alias="id", description="The unique identifier of the SMS template to retrieve.")) -> dict[str, Any]:
    """Retrieve a specific SMS template by its unique identifier. Use this to fetch template details for viewing or further processing."""

    # Construct request model with validation
    try:
        _request = _models.GetSmsTemplateIdRequest(
            path=_models.GetSmsTemplateIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_sms_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/sms_template/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/sms_template/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_sms_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_sms_template", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_sms_template",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: SMS Templates
@mcp.tool()
async def update_sms_template(
    id_: str = Field(..., alias="id", description="The unique identifier of the SMS template to update."),
    name: str | None = Field(None, description="The display name for the SMS template."),
    body: str | None = Field(None, description="The message content of the SMS template."),
) -> dict[str, Any]:
    """Update an existing SMS template by modifying its name and/or body content. Provide the template ID and specify which fields to update."""

    # Construct request model with validation
    try:
        _request = _models.PutSmsTemplateIdRequest(
            path=_models.PutSmsTemplateIdRequestPath(id_=id_),
            body=_models.PutSmsTemplateIdRequestBody(name=name, body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_sms_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/sms_template/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/sms_template/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_sms_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_sms_template", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_sms_template",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: SMS Templates
@mcp.tool()
async def delete_sms_template(id_: str = Field(..., alias="id", description="The unique identifier of the SMS template to delete.")) -> dict[str, Any]:
    """Permanently delete an SMS template by its ID. This action cannot be undone and will remove the template from your account."""

    # Construct request model with validation
    try:
        _request = _models.DeleteSmsTemplateIdRequest(
            path=_models.DeleteSmsTemplateIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_sms_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/sms_template/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/sms_template/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_sms_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_sms_template", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_sms_template",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Connected Accounts
@mcp.tool()
async def list_connected_accounts() -> dict[str, Any]:
    """Retrieve all connected accounts available in your organization. Optionally filter results to a specific user by providing their user ID."""

    # Extract parameters for API call
    _http_path = "/connected_account"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_connected_accounts")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_connected_accounts", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_connected_accounts",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Connected Accounts
@mcp.tool()
async def get_connected_account(id_: str = Field(..., alias="id", description="The unique identifier of the connected account to retrieve.")) -> dict[str, Any]:
    """Retrieve detailed information about a specific connected account using its unique identifier."""

    # Construct request model with validation
    try:
        _request = _models.GetConnectedAccountIdRequest(
            path=_models.GetConnectedAccountIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_connected_account: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/connected_account/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/connected_account/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_connected_account")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_connected_account", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_connected_account",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Send As
@mcp.tool()
async def list_send_as_associations(
    allowing_user_id: str | None = Field(None, description="Filter associations where this user is granting Send As permission. Must match your own user ID if provided."),
    allowed_user_id: str | None = Field(None, description="Filter associations where this user is receiving Send As permission. Must match your own user ID if provided."),
) -> dict[str, Any]:
    """Retrieve all Send As associations for the authenticated user, either as the user granting permission or receiving it. At least one filter parameter should be provided to scope results to your user ID."""

    # Construct request model with validation
    try:
        _request = _models.GetSendAsRequest(
            query=_models.GetSendAsRequestQuery(allowing_user_id=allowing_user_id, allowed_user_id=allowed_user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_send_as_associations: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/send_as"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_send_as_associations")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_send_as_associations", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_send_as_associations",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Send As
@mcp.tool()
async def grant_send_as_permission(
    allowing_user_id: str = Field(..., description="Your user ID that will grant send-as permission. This must match your own user ID to authorize the delegation."),
    allowed_user_id: str = Field(..., description="The user ID of the person who will receive permission to send messages as you."),
) -> dict[str, Any]:
    """Grant another user permission to send messages on your behalf by creating a Send As Association. The allowing user ID must be your own user ID."""

    # Construct request model with validation
    try:
        _request = _models.PostSendAsRequest(
            body=_models.PostSendAsRequestBody(allowing_user_id=allowing_user_id, allowed_user_id=allowed_user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for grant_send_as_permission: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/send_as"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("grant_send_as_permission")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("grant_send_as_permission", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="grant_send_as_permission",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Send As
@mcp.tool()
async def revoke_send_as_permission(
    allowing_user_id: str = Field(..., description="Your user ID — the user who originally granted Send As permission. This must match your authenticated user ID."),
    allowed_user_id: str = Field(..., description="The user ID of the user whose Send As permission is being revoked."),
) -> dict[str, Any]:
    """Revoke Send As permission that was previously granted to another user. The requesting user must be the one who originally granted the permission."""

    # Construct request model with validation
    try:
        _request = _models.DeleteSendAsRequest(
            query=_models.DeleteSendAsRequestQuery(allowing_user_id=allowing_user_id, allowed_user_id=allowed_user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for revoke_send_as_permission: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/send_as"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("revoke_send_as_permission")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("revoke_send_as_permission", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="revoke_send_as_permission",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Send As
@mcp.tool()
async def get_send_as(id_: str = Field(..., alias="id", description="The unique identifier of the Send As Association to retrieve.")) -> dict[str, Any]:
    """Retrieve a specific Send As Association by its unique identifier to view its configuration and details."""

    # Construct request model with validation
    try:
        _request = _models.GetSendAsIdRequest(
            path=_models.GetSendAsIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_send_as: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/send_as/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/send_as/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_send_as")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_send_as", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_send_as",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Send As
@mcp.tool()
async def delete_send_as(id_: str = Field(..., alias="id", description="The unique identifier of the Send As Association to delete.")) -> dict[str, Any]:
    """Remove a Send As Association by its unique identifier. This operation permanently deletes the specified Send As Association, preventing further use of that sending identity."""

    # Construct request model with validation
    try:
        _request = _models.DeleteSendAsIdRequest(
            path=_models.DeleteSendAsIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_send_as: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/send_as/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/send_as/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_send_as")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_send_as", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_send_as",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Send As
@mcp.tool()
async def update_send_as_permissions(
    allow: list[str] | None = Field(None, description="List of user IDs to grant Send As permission to. Each ID must be a valid user identifier in your organization."),
    disallow: list[str] | None = Field(None, description="List of user IDs to revoke Send As permission from. Each ID must be a valid user identifier in your organization."),
) -> dict[str, Any]:
    """Grant or revoke Send As permissions for multiple users in a single request. Returns all current Send As associations where you are the allowing user."""

    # Construct request model with validation
    try:
        _request = _models.PostSendAsBulkRequest(
            body=_models.PostSendAsBulkRequestBody(allow=allow, disallow=disallow)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_send_as_permissions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/send_as/bulk"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_send_as_permissions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_send_as_permissions", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_send_as_permissions",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Sequences
@mcp.tool()
async def list_sequences(limit: int | None = Field(None, alias="_limit", description="Maximum number of sequences to return in a single request. Allows you to control pagination size for efficient data retrieval.")) -> dict[str, Any]:
    """Retrieve a paginated list of all sequences. Use the limit parameter to control the number of results returned per request."""

    # Construct request model with validation
    try:
        _request = _models.GetSequenceRequest(
            query=_models.GetSequenceRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_sequences: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/sequence"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_sequences")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_sequences", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_sequences",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Sequences
@mcp.tool()
async def create_sequence(body: dict[str, Any] = Field(..., description="The sequence configuration object containing all required properties to define the new sequence.")) -> dict[str, Any]:
    """Create a new sequence with the specified configuration. This operation initializes a sequence resource that can be used for ordered processing or workflow management."""

    # Construct request model with validation
    try:
        _request = _models.PostSequenceRequest(
            body=_models.PostSequenceRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_sequence: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/sequence"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_sequence")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_sequence", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_sequence",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Sequences
@mcp.tool()
async def get_sequence(id_: str = Field(..., alias="id", description="The unique identifier that specifies which sequence to retrieve.")) -> dict[str, Any]:
    """Retrieve a single sequence by its unique identifier. Use this operation to fetch detailed information about a specific sequence."""

    # Construct request model with validation
    try:
        _request = _models.GetSequenceIdRequest(
            path=_models.GetSequenceIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_sequence: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/sequence/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/sequence/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_sequence")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_sequence", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_sequence",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Sequences
@mcp.tool()
async def update_sequence(
    id_: str = Field(..., alias="id", description="The unique identifier of the sequence to update."),
    steps: list[dict[str, Any]] | None = Field(None, description="An ordered array of steps that defines the sequence workflow. When provided, this completely replaces all existing steps; any steps not included in the request will be removed from the sequence."),
) -> dict[str, Any]:
    """Update an existing sequence by modifying its configuration. The steps array, if provided, will completely replace all current steps in the sequence."""

    # Construct request model with validation
    try:
        _request = _models.PutSequenceIdRequest(
            path=_models.PutSequenceIdRequestPath(id_=id_),
            body=_models.PutSequenceIdRequestBody(steps=steps)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_sequence: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/sequence/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/sequence/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_sequence")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_sequence", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_sequence",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Sequences
@mcp.tool()
async def delete_sequence(id_: str = Field(..., alias="id", description="The unique identifier of the sequence to delete.")) -> dict[str, Any]:
    """Permanently delete a sequence by its unique identifier. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteSequenceIdRequest(
            path=_models.DeleteSequenceIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_sequence: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/sequence/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/sequence/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_sequence")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_sequence", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_sequence",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Sequences
@mcp.tool()
async def list_sequence_subscriptions(sequence_id: str | None = Field(None, description="Filter results by sequence ID. At least one of sequence_id, contact_id, or lead_id must be specified.")) -> dict[str, Any]:
    """Retrieve a list of sequence subscriptions filtered by sequence, contact, or lead. At least one filter criterion must be provided."""

    # Construct request model with validation
    try:
        _request = _models.GetSequenceSubscriptionRequest(
            query=_models.GetSequenceSubscriptionRequestQuery(sequence_id=sequence_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_sequence_subscriptions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/sequence_subscription"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_sequence_subscriptions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_sequence_subscriptions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_sequence_subscriptions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Sequences
@mcp.tool()
async def subscribe_contact_to_sequence(body: dict[str, Any] = Field(..., description="Request body containing the contact ID and sequence ID. Specify which contact to subscribe and which sequence to enroll them in.")) -> dict[str, Any]:
    """Subscribe a contact to an automation sequence. This enrolls the contact in the specified sequence, triggering any configured automation workflows."""

    # Construct request model with validation
    try:
        _request = _models.PostSequenceSubscriptionRequest(
            body=_models.PostSequenceSubscriptionRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for subscribe_contact_to_sequence: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/sequence_subscription"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("subscribe_contact_to_sequence")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("subscribe_contact_to_sequence", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="subscribe_contact_to_sequence",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Sequences
@mcp.tool()
async def get_sequence_subscription(id_: str = Field(..., alias="id", description="The unique identifier of the sequence subscription to retrieve.")) -> dict[str, Any]:
    """Retrieve a specific sequence subscription by its unique identifier to view its configuration and status."""

    # Construct request model with validation
    try:
        _request = _models.GetSequenceSubscriptionIdRequest(
            path=_models.GetSequenceSubscriptionIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_sequence_subscription: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/sequence_subscription/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/sequence_subscription/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_sequence_subscription")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_sequence_subscription", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_sequence_subscription",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Sequences
@mcp.tool()
async def update_sequence_subscription(
    id_: str = Field(..., alias="id", description="The unique identifier of the sequence subscription to update."),
    body: dict[str, Any] = Field(..., description="The updated configuration and settings for the sequence subscription. Include only the fields you want to modify."),
) -> dict[str, Any]:
    """Update an existing sequence subscription with new configuration, settings, or other properties. Modifies the subscription identified by the provided ID."""

    # Construct request model with validation
    try:
        _request = _models.PutSequenceSubscriptionIdRequest(
            path=_models.PutSequenceSubscriptionIdRequestPath(id_=id_),
            body=_models.PutSequenceSubscriptionIdRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_sequence_subscription: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/sequence_subscription/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/sequence_subscription/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_sequence_subscription")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_sequence_subscription", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_sequence_subscription",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Dialer
@mcp.tool()
async def list_dialer_sessions(
    source_value: str | None = Field(None, description="Filter results by the source identifier, which can be either a Smart View ID or Shared Entry ID."),
    source_type: Literal["saved-search", "shared-entry"] | None = Field(None, description="Filter results by source type. Valid options are 'saved-search' for saved search sources or 'shared-entry' for shared entry sources."),
    limit: int | None = Field(None, alias="_limit", description="Maximum number of dialer sessions to return in the results."),
) -> dict[str, Any]:
    """Retrieve and filter dialer sessions to view their source, type, and associated user information. Use filters to narrow results by source identifier or type."""

    # Construct request model with validation
    try:
        _request = _models.GetDialerRequest(
            query=_models.GetDialerRequestQuery(source_value=source_value, source_type=source_type, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_dialer_sessions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/dialer"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_dialer_sessions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_dialer_sessions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_dialer_sessions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Dialer
@mcp.tool()
async def get_dialer(id_: str = Field(..., alias="id", description="The unique identifier of the dialer session to retrieve.")) -> dict[str, Any]:
    """Retrieve detailed information about a specific dialer session using its unique identifier."""

    # Construct request model with validation
    try:
        _request = _models.GetDialerIdRequest(
            path=_models.GetDialerIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_dialer: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/dialer/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/dialer/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_dialer")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_dialer", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_dialer",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Smart Views
@mcp.tool()
async def list_smart_views(type__in: str | None = Field(None, description="Filter results by one or more record types using comma-separated values (e.g., lead,contact). Omit this parameter to retrieve Smart Views for all types.")) -> dict[str, Any]:
    """Retrieve all Smart Views with optional filtering by record type. Use this to display available saved searches for leads, contacts, or both."""

    # Construct request model with validation
    try:
        _request = _models.GetSavedSearchRequest(
            query=_models.GetSavedSearchRequestQuery(type__in=type__in)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_smart_views: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/saved_search"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_smart_views")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_smart_views", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_smart_views",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Smart Views
@mcp.tool()
async def create_smart_view(
    name: str = Field(..., description="The display name for the Smart View. This is the label users will see when accessing the saved search."),
    query: dict[str, Any] = Field(..., description="A filter query object that defines which records appear in the Smart View. Must include an `object_type` clause specifying either 'Lead' or 'Contact' to determine the record type for this Smart View."),
) -> dict[str, Any]:
    """Create a Smart View (saved search) for Leads or Contacts. The Smart View uses a filter query to automatically populate with matching records based on your specified criteria."""

    # Construct request model with validation
    try:
        _request = _models.PostSavedSearchRequest(
            body=_models.PostSavedSearchRequestBody(name=name, query=query)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_smart_view: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/saved_search"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_smart_view")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_smart_view", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_smart_view",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Smart Views
@mcp.tool()
async def get_smart_view(id_: str = Field(..., alias="id", description="The unique identifier of the Smart View to retrieve.")) -> dict[str, Any]:
    """Retrieve a single Smart View by its unique identifier. Use this to fetch detailed information about a saved search view."""

    # Construct request model with validation
    try:
        _request = _models.GetSavedSearchIdRequest(
            path=_models.GetSavedSearchIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_smart_view: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/saved_search/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/saved_search/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_smart_view")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_smart_view", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_smart_view",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Smart Views
@mcp.tool()
async def update_smart_view(
    id_: str = Field(..., alias="id", description="The unique identifier of the Smart View to update. This ID is assigned when the Smart View is created and is used to reference it in subsequent operations."),
    name: str | None = Field(None, description="The display name for the Smart View. This is the human-readable label shown in the user interface to identify the Smart View."),
) -> dict[str, Any]:
    """Update an existing Smart View by modifying its properties such as the display name. Use this operation to rename or reconfigure a Smart View that you've previously created."""

    # Construct request model with validation
    try:
        _request = _models.PutSavedSearchIdRequest(
            path=_models.PutSavedSearchIdRequestPath(id_=id_),
            body=_models.PutSavedSearchIdRequestBody(name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_smart_view: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/saved_search/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/saved_search/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_smart_view")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_smart_view", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_smart_view",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Smart Views
@mcp.tool()
async def delete_smart_view(id_: str = Field(..., alias="id", description="The unique identifier of the Smart View to delete.")) -> dict[str, Any]:
    """Permanently delete a Smart View by its unique identifier. This action cannot be undone and will remove all saved search criteria and filters associated with the Smart View."""

    # Construct request model with validation
    try:
        _request = _models.DeleteSavedSearchIdRequest(
            path=_models.DeleteSavedSearchIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_smart_view: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/saved_search/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/saved_search/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_smart_view")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_smart_view", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_smart_view",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Bulk Actions
@mcp.tool()
async def list_bulk_emails() -> dict[str, Any]:
    """Retrieve a list of all bulk email actions that have been created. This operation allows you to view the history and status of bulk email campaigns."""

    # Extract parameters for API call
    _http_path = "/bulk_action/email"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_bulk_emails")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_bulk_emails", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_bulk_emails",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Bulk Actions
@mcp.tool()
async def send_bulk_email(
    s_query: dict[str, Any] = Field(..., description="Structured query to filter which leads receive the email, using the same query syntax as the Advanced Filtering API."),
    results_limit: int | None = Field(None, description="Optional limit on the number of leads to affect. If not specified, all leads matching the query will be included."),
    sort: list[dict[str, Any]] | None = Field(None, description="Optional sort criteria to order the filtered leads. Specify as an array of sort expressions."),
    contact_preference: Literal["lead", "contact"] | None = Field(None, description="Determines email recipient scope: use 'lead' to email only the primary contact of each lead, or 'contact' to email the first contact email of each individual contact associated with the lead."),
    send_done_email: bool | None = Field(None, description="Whether to send a confirmation email after the bulk action completes. Enabled by default."),
) -> dict[str, Any]:
    """Send bulk emails to leads matching specified criteria. Choose whether to email the primary lead contact or each individual contact associated with the leads."""

    # Construct request model with validation
    try:
        _request = _models.PostBulkActionEmailRequest(
            body=_models.PostBulkActionEmailRequestBody(s_query=s_query, results_limit=results_limit, sort=sort, contact_preference=contact_preference, send_done_email=send_done_email)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for send_bulk_email: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/bulk_action/email"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("send_bulk_email")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("send_bulk_email", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="send_bulk_email",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Bulk Actions
@mcp.tool()
async def get_bulk_email(id_: str = Field(..., alias="id", description="The unique identifier of the bulk email action to retrieve.")) -> dict[str, Any]:
    """Retrieve the details and status of a specific bulk email action by its unique identifier."""

    # Construct request model with validation
    try:
        _request = _models.GetBulkActionEmailIdRequest(
            path=_models.GetBulkActionEmailIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_bulk_email: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/bulk_action/email/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/bulk_action/email/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_bulk_email")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_bulk_email", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_bulk_email",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Bulk Actions
@mcp.tool()
async def list_sequence_subscriptions_bulk_action() -> dict[str, Any]:
    """Retrieve all bulk sequence subscription actions. Use this to view the complete list of active sequence subscriptions in your bulk action system."""

    # Extract parameters for API call
    _http_path = "/bulk_action/sequence_subscription"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_sequence_subscriptions_bulk_action")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_sequence_subscriptions_bulk_action", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_sequence_subscriptions_bulk_action",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Bulk Actions
@mcp.tool()
async def apply_sequence_subscription_bulk_action(
    s_query: dict[str, Any] = Field(..., description="Structured query object that defines which leads to target with the bulk action. This filter determines the lead set before applying the subscription action."),
    action_type: Literal["subscribe", "resume", "resume_finished", "pause"] = Field(..., description="The subscription action to perform: 'subscribe' (enroll leads in a sequence), 'resume' (restart paused sequences), 'resume_finished' (restart completed sequences), or 'pause' (pause active sequences)."),
    results_limit: int | None = Field(None, description="Maximum number of leads to affect with this bulk action. If not specified, all matching leads will be included."),
    sort: list[dict[str, Any]] | None = Field(None, description="Sort criteria to order the filtered leads. Specify as an array where order matters for determining which leads are processed first when combined with results_limit."),
    sequence_id: str | None = Field(None, description="ID of the sequence to target. Required when action_type is 'subscribe'; optional for resume and pause actions to target all sequences for matching leads."),
    sender_account_id: str | None = Field(None, description="Account ID of the sender. Required when action_type is 'subscribe' to identify which account will send the sequence messages."),
    sender_name: str | None = Field(None, description="Display name of the sender. Required when action_type is 'subscribe' to personalize outgoing sequence messages."),
    sender_email: str | None = Field(None, description="Email address of the sender. Required when action_type is 'subscribe' as the reply-to and from address for sequence messages. Must be a valid email format."),
    contact_preference: Literal["lead", "contact"] | None = Field(None, description="Determines subscription scope when action_type is 'subscribe': 'lead' subscribes the primary lead contact, or 'contact' subscribes each contact's individual email address. Required when action_type is 'subscribe'."),
    send_done_email: bool | None = Field(None, description="Whether to send a confirmation email after the bulk action completes. Defaults to true if not specified."),
) -> dict[str, Any]:
    """Apply a bulk subscription action (subscribe, resume, pause, or resume finished) to leads matching specified criteria. Use structured queries to filter leads and optionally limit the number affected."""

    # Construct request model with validation
    try:
        _request = _models.PostBulkActionSequenceSubscriptionRequest(
            body=_models.PostBulkActionSequenceSubscriptionRequestBody(s_query=s_query, results_limit=results_limit, sort=sort, action_type=action_type, sequence_id=sequence_id, sender_account_id=sender_account_id, sender_name=sender_name, sender_email=sender_email, contact_preference=contact_preference, send_done_email=send_done_email)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for apply_sequence_subscription_bulk_action: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/bulk_action/sequence_subscription"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("apply_sequence_subscription_bulk_action")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("apply_sequence_subscription_bulk_action", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="apply_sequence_subscription_bulk_action",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Bulk Actions
@mcp.tool()
async def get_sequence_subscription_bulk_action(id_: str = Field(..., alias="id", description="The unique identifier of the bulk sequence subscription to retrieve.")) -> dict[str, Any]:
    """Retrieve a single bulk sequence subscription by its ID. Use this to fetch details about a specific sequence subscription object."""

    # Construct request model with validation
    try:
        _request = _models.GetBulkActionSequenceSubscriptionIdRequest(
            path=_models.GetBulkActionSequenceSubscriptionIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_sequence_subscription_bulk_action: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/bulk_action/sequence_subscription/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/bulk_action/sequence_subscription/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_sequence_subscription_bulk_action")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_sequence_subscription_bulk_action", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_sequence_subscription_bulk_action",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Bulk Actions
@mcp.tool()
async def list_bulk_deletes() -> dict[str, Any]:
    """Retrieve a list of all bulk delete actions that have been performed or are in progress. Use this to track and monitor deletion operations across your resources."""

    # Extract parameters for API call
    _http_path = "/bulk_action/delete"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_bulk_deletes")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_bulk_deletes", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_bulk_deletes",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Bulk Actions
@mcp.tool()
async def delete_leads_bulk(
    s_query: dict[str, Any] = Field(..., description="Structured query object that defines which leads to delete based on filter conditions."),
    results_limit: int | None = Field(None, description="Maximum number of leads to delete in this bulk action. If not specified, all matching leads will be deleted."),
    sort: list[dict[str, Any]] | None = Field(None, description="Array of sort criteria to order the leads before deletion. Order matters and determines which leads are processed first if a results limit is applied."),
    send_done_email: bool | None = Field(None, description="Whether to send a confirmation email after the bulk delete completes. Defaults to true if not specified."),
) -> dict[str, Any]:
    """Initiate a bulk delete action to remove multiple leads matching specified criteria. Optionally receive a confirmation email when the deletion completes."""

    # Construct request model with validation
    try:
        _request = _models.PostBulkActionDeleteRequest(
            body=_models.PostBulkActionDeleteRequestBody(s_query=s_query, results_limit=results_limit, sort=sort, send_done_email=send_done_email)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_leads_bulk: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/bulk_action/delete"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_leads_bulk")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_leads_bulk", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_leads_bulk",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Bulk Actions
@mcp.tool()
async def get_bulk_delete(id_: str = Field(..., alias="id", description="The unique identifier of the bulk delete operation to retrieve.")) -> dict[str, Any]:
    """Retrieve details of a specific bulk delete operation by its ID. Use this to check the status and configuration of a previously initiated bulk deletion."""

    # Construct request model with validation
    try:
        _request = _models.GetBulkActionDeleteIdRequest(
            path=_models.GetBulkActionDeleteIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_bulk_delete: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/bulk_action/delete/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/bulk_action/delete/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_bulk_delete")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_bulk_delete", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_bulk_delete",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Bulk Actions
@mcp.tool()
async def list_bulk_edits() -> dict[str, Any]:
    """Retrieve a list of all bulk edit actions that have been created. Use this to view the history and status of bulk editing operations."""

    # Extract parameters for API call
    _http_path = "/bulk_action/edit"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_bulk_edits")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_bulk_edits", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_bulk_edits",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Bulk Actions
@mcp.tool()
async def bulk_edit_leads(
    s_query: dict[str, Any] = Field(..., description="Structured query object that defines which leads to include in the bulk edit operation."),
    type_: Literal["set_lead_status", "clear_custom_field", "set_custom_field"] = Field(..., alias="type", description="The type of bulk edit operation to perform: set_lead_status updates lead status, clear_custom_field removes a custom field value, or set_custom_field assigns a custom field value."),
    results_limit: int | None = Field(None, description="Maximum number of leads to affect with this bulk edit action. If not specified, all matching leads will be included."),
    sort: list[dict[str, Any]] | None = Field(None, description="Array of sort criteria to order the leads before applying the bulk edit. Order matters and determines which leads are prioritized if results_limit is applied."),
    lead_status_id: str | None = Field(None, description="The ID of the Lead Status to assign. Required when type is 'set_lead_status'."),
    custom_field_name: str | None = Field(None, description="The exact name of the custom field to modify. Required when type is 'clear_custom_field' or 'set_custom_field' (unless custom_field_id is provided instead)."),
    custom_field_values: list[str] | None = Field(None, description="Array of values to set for custom fields that support multiple values. Used only when type is 'set_custom_field'."),
    custom_field_operation: Literal["replace", "add", "remove"] | None = Field(None, description="How to apply values to multi-value custom fields: 'replace' overwrites existing values, 'add' appends new values, or 'remove' deletes specified values. Defaults to 'replace' and only applies when type is 'set_custom_field'."),
    send_done_email: bool | None = Field(None, description="Whether to send a confirmation email after the bulk edit completes. Defaults to true; set to false to skip the notification."),
) -> dict[str, Any]:
    """Execute a bulk edit action on leads matching specified criteria. Supports updating lead status, clearing custom fields, or setting custom field values across multiple leads."""

    # Construct request model with validation
    try:
        _request = _models.PostBulkActionEditRequest(
            body=_models.PostBulkActionEditRequestBody(s_query=s_query, results_limit=results_limit, sort=sort, type_=type_, lead_status_id=lead_status_id, custom_field_name=custom_field_name, custom_field_values=custom_field_values, custom_field_operation=custom_field_operation, send_done_email=send_done_email)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for bulk_edit_leads: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/bulk_action/edit"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("bulk_edit_leads")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("bulk_edit_leads", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="bulk_edit_leads",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Bulk Actions
@mcp.tool()
async def get_bulk_edit(id_: str = Field(..., alias="id", description="The unique identifier of the bulk edit action to retrieve.")) -> dict[str, Any]:
    """Retrieve the details and current status of a specific bulk edit action by its unique identifier."""

    # Construct request model with validation
    try:
        _request = _models.GetBulkActionEditIdRequest(
            path=_models.GetBulkActionEditIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_bulk_edit: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/bulk_action/edit/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/bulk_action/edit/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_bulk_edit")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_bulk_edit", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_bulk_edit",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Integration Links
@mcp.tool()
async def list_integration_links() -> dict[str, Any]:
    """Retrieve all integration links that have been configured for your organization. This provides a complete view of all active integrations and their connection details."""

    # Extract parameters for API call
    _http_path = "/integration_link"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_integration_links")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_integration_links", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_integration_links",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Integration Links
@mcp.tool()
async def create_integration_link(
    name: str = Field(..., description="The display name for this integration link, shown as clickable link text to users."),
    type_: Literal["lead", "contact", "opportunity"] = Field(..., alias="type", description="The entity type this integration link applies to. Must be one of: lead, contact, or opportunity."),
    url: str = Field(..., description="The URL template that defines where this integration link directs to. Use template variables to dynamically construct URLs based on entity data."),
) -> dict[str, Any]:
    """Create a new integration link for your organization to connect entities to external systems. This operation is restricted to organization administrators only."""

    # Construct request model with validation
    try:
        _request = _models.PostIntegrationLinkRequest(
            body=_models.PostIntegrationLinkRequestBody(name=name, type_=type_, url=url)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_integration_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/integration_link"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_integration_link")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_integration_link", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_integration_link",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Integration Links
@mcp.tool()
async def get_integration_link(id_: str = Field(..., alias="id", description="The unique identifier of the integration link to retrieve.")) -> dict[str, Any]:
    """Retrieve a specific integration link by its unique identifier. Use this to fetch details about a configured integration connection."""

    # Construct request model with validation
    try:
        _request = _models.GetIntegrationLinkIdRequest(
            path=_models.GetIntegrationLinkIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_integration_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/integration_link/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/integration_link/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_integration_link")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_integration_link", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_integration_link",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Integration Links
@mcp.tool()
async def update_integration_link(
    id_: str = Field(..., alias="id", description="The unique identifier of the integration link to update."),
    name: str | None = Field(None, description="The text displayed as the clickable link in the user interface."),
    url: str | None = Field(None, description="The URL template that defines the target destination, supporting dynamic variable substitution (e.g., using placeholders for dynamic values)."),
) -> dict[str, Any]:
    """Update an existing integration link's display name and URL template. Requires organization admin privileges."""

    # Construct request model with validation
    try:
        _request = _models.PutIntegrationLinkIdRequest(
            path=_models.PutIntegrationLinkIdRequestPath(id_=id_),
            body=_models.PutIntegrationLinkIdRequestBody(name=name, url=url)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_integration_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/integration_link/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/integration_link/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_integration_link")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_integration_link", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_integration_link",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Integration Links
@mcp.tool()
async def delete_integration_link(id_: str = Field(..., alias="id", description="The unique identifier of the integration link to delete.")) -> dict[str, Any]:
    """Permanently delete an integration link from your organization. This action is restricted to organization administrators only and cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteIntegrationLinkIdRequest(
            path=_models.DeleteIntegrationLinkIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_integration_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/integration_link/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/integration_link/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_integration_link")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_integration_link", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_integration_link",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Exports
@mcp.tool()
async def export_leads(
    format_: Literal["csv", "json"] = Field(..., alias="format", description="Output file format. Choose CSV for spreadsheet compatibility or JSON for raw data backups and migrations. JSON is recommended for data preservation."),
    type_: Literal["leads", "contacts", "lead_opps"] = Field(..., alias="type", description="Record type to export: leads (one row per lead or complete JSON structure), contacts (one row per contact), or lead_opps (one row per opportunity)."),
    s_query: dict[str, Any] | None = Field(None, description="Advanced query filter to narrow the exported results. If omitted, all records of the specified type are exported."),
    results_limit: int | None = Field(None, description="Maximum number of records to include in the export. If not specified, all matching records are exported."),
    sort: list[dict[str, Any]] | None = Field(None, description="Sort order for the exported results. Specify as an array of sort criteria to control result ordering."),
    date_format: Literal["original", "iso8601", "excel"] | None = Field(None, description="Date format for CSV exports only. Choose original (as-is), ISO 8601 (standardized format), or excel (spreadsheet-compatible format). Defaults to original format."),
    fields: list[str] | None = Field(None, description="Specific fields to include in the export. If omitted, all available fields are exported."),
    include_activities: bool | None = Field(None, description="Include associated activities in the export. Only applies when exporting leads in JSON format."),
    include_smart_fields: bool | None = Field(None, description="Include smart fields in the export. Works with leads in JSON format or any record type in CSV format."),
    send_done_email: bool | None = Field(None, description="Send a confirmation email when the export completes. Set to false to skip the notification email."),
) -> dict[str, Any]:
    """Export leads, contacts, or opportunities to a compressed file based on search criteria. The generated file will be sent to your email once the export completes."""

    # Construct request model with validation
    try:
        _request = _models.PostExportLeadRequest(
            body=_models.PostExportLeadRequestBody(s_query=s_query, results_limit=results_limit, sort=sort, format_=format_, type_=type_, date_format=date_format, fields=fields, include_activities=include_activities, include_smart_fields=include_smart_fields, send_done_email=send_done_email)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for export_leads: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/export/lead"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("export_leads")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("export_leads", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="export_leads",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Exports
@mcp.tool()
async def export_opportunities(
    format_: Literal["csv", "json"] = Field(..., alias="format", description="File format for the exported data. Choose between CSV for spreadsheet compatibility or JSON for structured data interchange."),
    params: dict[str, Any] | None = Field(None, description="Filter criteria to select which opportunities to export, using the same filter options available in the opportunities endpoint."),
    date_format: Literal["original", "iso8601", "excel"] | None = Field(None, description="Date formatting style for CSV exports only. Choose 'original' to preserve the source format, 'iso8601' for standardized date-time strings, or 'excel' for Excel-compatible date values."),
    fields: list[str] | None = Field(None, description="Specific fields to include in the export. If not specified, all available data fields are included. Provide as an ordered list of field names."),
    send_done_email: bool | None = Field(None, description="Set to false to skip the confirmation email after the export completes. By default, a confirmation email is sent."),
) -> dict[str, Any]:
    """Export opportunities matching specified filters to a file in your chosen format. A confirmation email is sent upon completion unless explicitly disabled."""

    # Construct request model with validation
    try:
        _request = _models.PostExportOpportunityRequest(
            body=_models.PostExportOpportunityRequestBody(params=params, format_=format_, date_format=date_format, fields=fields, send_done_email=send_done_email)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for export_opportunities: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/export/opportunity"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("export_opportunities")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("export_opportunities", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="export_opportunities",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Exports
@mcp.tool()
async def get_export(id_: str = Field(..., alias="id", description="The unique identifier of the export to retrieve.")) -> dict[str, Any]:
    """Retrieve a single export by its unique identifier to check its current processing status or obtain a download URL once completed. Status values include: created, started, in_progress, done, and error."""

    # Construct request model with validation
    try:
        _request = _models.GetExportIdRequest(
            path=_models.GetExportIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_export: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/export/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/export/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_export")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_export", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_export",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Exports
@mcp.tool()
async def list_exports(limit: int | None = Field(None, alias="_limit", description="Maximum number of exports to return in the response. Useful for pagination and controlling response size.")) -> dict[str, Any]:
    """Retrieve a list of all exports with optional pagination control. Use the limit parameter to restrict the number of results returned."""

    # Construct request model with validation
    try:
        _request = _models.GetExportRequest(
            query=_models.GetExportRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_exports: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/export"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_exports")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_exports", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_exports",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Phone Numbers
@mcp.tool()
async def list_phone_numbers(
    number: str | None = Field(None, description="Filter results to phone numbers matching this specific value. Leave empty to include all numbers regardless of their value."),
    is_group_number: bool | None = Field(None, description="Filter results to show only group numbers (true) or non-group numbers (false). Omit to include both types."),
    limit: int | None = Field(None, alias="_limit", description="Maximum number of phone numbers to return in the response. Useful for pagination or limiting large result sets."),
) -> dict[str, Any]:
    """Retrieve phone numbers from your organization with optional filtering by number value, group status, or result limit. Use this to search for specific phone numbers or get an overview of all numbers in your system."""

    # Construct request model with validation
    try:
        _request = _models.GetPhoneNumberRequest(
            query=_models.GetPhoneNumberRequestQuery(number=number, is_group_number=is_group_number, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_phone_numbers: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/phone_number"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_phone_numbers")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_phone_numbers", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_phone_numbers",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Phone Numbers
@mcp.tool()
async def get_phone_number(id_: str = Field(..., alias="id", description="The unique identifier of the phone number to retrieve.")) -> dict[str, Any]:
    """Retrieve detailed information for a specific phone number by its unique identifier."""

    # Construct request model with validation
    try:
        _request = _models.GetPhoneNumberIdRequest(
            path=_models.GetPhoneNumberIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_phone_number: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/phone_number/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/phone_number/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_phone_number")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_phone_number", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_phone_number",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Phone Numbers
@mcp.tool()
async def update_phone_number(
    id_: str = Field(..., alias="id", description="The unique identifier of the phone number to update."),
    label: str | None = Field(None, description="A custom label or name for this phone number to help identify it."),
    forward_to: str | None = Field(None, description="The phone number to forward incoming calls to when call forwarding is enabled."),
    forward_to_enabled: bool | None = Field(None, description="Enable or disable call forwarding for this phone number."),
    voicemail_greeting_url: str | None = Field(None, description="HTTPS URL pointing to an MP3 audio file to play as the voicemail greeting when callers reach voicemail."),
) -> dict[str, Any]:
    """Update settings for a phone number including its label, call forwarding configuration, and voicemail greeting. Personal numbers can only be updated by their owner, while group numbers require 'Manage Group Phone Numbers' permission."""

    # Construct request model with validation
    try:
        _request = _models.PutPhoneNumberIdRequest(
            path=_models.PutPhoneNumberIdRequestPath(id_=id_),
            body=_models.PutPhoneNumberIdRequestBody(label=label, forward_to=forward_to, forward_to_enabled=forward_to_enabled, voicemail_greeting_url=voicemail_greeting_url)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_phone_number: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/phone_number/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/phone_number/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_phone_number")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_phone_number", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_phone_number",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Phone Numbers
@mcp.tool()
async def delete_phone_number(id_: str = Field(..., alias="id", description="The unique identifier of the phone number to delete.")) -> dict[str, Any]:
    """Delete a phone number from your account or group. Requires 'Manage Group Phone Numbers' permission to delete group numbers; personal numbers can only be deleted by their owner."""

    # Construct request model with validation
    try:
        _request = _models.DeletePhoneNumberIdRequest(
            path=_models.DeletePhoneNumberIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_phone_number: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/phone_number/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/phone_number/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_phone_number")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_phone_number", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_phone_number",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Phone Numbers
@mcp.tool()
async def rent_phone_number(
    country: str = Field(..., description="Two-letter ISO country code indicating where the phone number should be rented (e.g., US for United States)."),
    sharing: Literal["personal", "group"] = Field(..., description="Scope of the phone number: 'personal' for an individual user or 'group' for a shared group number."),
    prefix: str | None = Field(None, description="Optional phone number prefix or area code, excluding the country code."),
    with_sms: bool | None = Field(None, description="Optional flag to control SMS capability. When true, forces an SMS-capable number; when false, allows non-SMS-capable numbers. By default, SMS-capable numbers are rented if supported in the country."),
    with_mms: bool | None = Field(None, description="Optional flag to control MMS capability. When true, forces an MMS-capable number; when false, allows non-MMS-capable numbers. By default, MMS-capable numbers are rented if supported in the country."),
) -> dict[str, Any]:
    """Rent an internal phone number for personal or group use. Renting incurs a cost and requires appropriate permissions for group numbers."""

    # Construct request model with validation
    try:
        _request = _models.PostPhoneNumberRequestInternalRequest(
            body=_models.PostPhoneNumberRequestInternalRequestBody(country=country, sharing=sharing, prefix=prefix, with_sms=with_sms, with_mms=with_mms)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for rent_phone_number: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/phone_number/request/internal"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("rent_phone_number")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("rent_phone_number", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="rent_phone_number",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Files
@mcp.tool()
async def generate_file_upload_credentials(
    filename: str = Field(..., description="The name of the file being uploaded, including its file extension (e.g., image.jpg, document.pdf)."),
    content_type: str = Field(..., description="The MIME type of the file being uploaded (e.g., image/jpeg, application/pdf, text/plain)."),
) -> dict[str, Any]:
    """Generate signed S3 upload credentials and a download URL for storing a file. Use the returned credentials to upload your file directly to S3, then reference the download URL in other API endpoints."""

    # Construct request model with validation
    try:
        _request = _models.PostFilesUploadRequest(
            body=_models.PostFilesUploadRequestBody(filename=filename, content_type=content_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for generate_file_upload_credentials: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/files/upload"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("generate_file_upload_credentials")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("generate_file_upload_credentials", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="generate_file_upload_credentials",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Comments
@mcp.tool()
async def list_comment_threads(
    object_ids: list[str] | None = Field(None, description="Filter results to include only threads associated with specific object IDs. Provide as an array of object identifiers."),
    ids: list[str] | None = Field(None, description="Filter results to include only threads with specific thread IDs. Provide as an array of thread identifiers."),
    limit: int | None = Field(None, alias="_limit", description="Maximum number of comment threads to return in the response. Limits the result set size."),
) -> dict[str, Any]:
    """Retrieve multiple comment threads with optional filtering by associated objects or specific thread identifiers. Useful for fetching discussions related to particular items or retrieving known threads."""

    # Construct request model with validation
    try:
        _request = _models.GetCommentThreadRequest(
            query=_models.GetCommentThreadRequestQuery(object_ids=object_ids, ids=ids, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_comment_threads: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/comment_thread"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_comment_threads")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_comment_threads", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_comment_threads",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Comments
@mcp.tool()
async def get_comment_thread(thread_id: str = Field(..., description="The unique identifier that specifies which comment thread to retrieve.")) -> dict[str, Any]:
    """Retrieve a specific comment thread by its unique identifier. Use this to fetch the full details of a single comment thread including all associated metadata."""

    # Construct request model with validation
    try:
        _request = _models.GetCommentThreadThreadIdRequest(
            path=_models.GetCommentThreadThreadIdRequestPath(thread_id=thread_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_comment_thread: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/comment_thread/{thread_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/comment_thread/{thread_id}"
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

# Tags: Comments
@mcp.tool()
async def list_comments(
    object_id: str | None = Field(None, description="Filter comments by the ID of the object that was commented on. Cannot be used together with thread_id."),
    thread_id: str | None = Field(None, description="Filter comments by the discussion thread ID. Cannot be used together with object_id."),
) -> dict[str, Any]:
    """Retrieve comments filtered by either the object being commented on or the discussion thread. Provide exactly one filter to retrieve the relevant comments."""

    # Construct request model with validation
    try:
        _request = _models.GetCommentRequest(
            query=_models.GetCommentRequestQuery(object_id=object_id, thread_id=thread_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_comments: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/comment"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_comments")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_comments", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_comments",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Comments
@mcp.tool()
async def create_comment(
    object_type: str = Field(..., description="The type of object being commented on (e.g., task, document, issue)."),
    object_id: str = Field(..., description="The unique identifier of the object being commented on."),
    body: str = Field(..., description="The comment text formatted as rich text."),
) -> dict[str, Any]:
    """Create a comment on an object, automatically creating a comment thread if one doesn't already exist, or adding to an existing thread if it does."""

    # Construct request model with validation
    try:
        _request = _models.PostCommentRequest(
            body=_models.PostCommentRequestBody(object_type=object_type, object_id=object_id, body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/comment"
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

# Tags: Comments
@mcp.tool()
async def get_comment(comment_id: str = Field(..., description="The unique identifier of the comment to retrieve.")) -> dict[str, Any]:
    """Retrieve a specific comment by its unique identifier. Use this to fetch the full details of an individual comment."""

    # Construct request model with validation
    try:
        _request = _models.GetCommentCommentIdRequest(
            path=_models.GetCommentCommentIdRequestPath(comment_id=comment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/comment/{comment_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/comment/{comment_id}"
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

# Tags: Comments
@mcp.tool()
async def update_comment(
    comment_id: str = Field(..., description="The unique identifier of the comment you want to update."),
    body: str = Field(..., description="The new comment text formatted as rich text."),
) -> dict[str, Any]:
    """Edit the body of a comment. You can only update comments that you created."""

    # Construct request model with validation
    try:
        _request = _models.PutCommentCommentIdRequest(
            path=_models.PutCommentCommentIdRequestPath(comment_id=comment_id),
            body=_models.PutCommentCommentIdRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/comment/{comment_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/comment/{comment_id}"
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
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Comments
@mcp.tool()
async def delete_comment(comment_id: str = Field(..., description="The unique identifier of the comment to delete.")) -> dict[str, Any]:
    """Remove a comment from a thread. The comment content is deleted but the comment object remains until all comments in the thread are removed, at which point the entire thread is deleted. Deletion permissions are based on the user's ability to delete their own or other users' activities."""

    # Construct request model with validation
    try:
        _request = _models.DeleteCommentCommentIdRequest(
            path=_models.DeleteCommentCommentIdRequestPath(comment_id=comment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/comment/{comment_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/comment/{comment_id}"
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

# Tags: Event Log
@mcp.tool()
async def get_event(id_: str = Field(..., alias="id", description="The unique identifier of the event to retrieve.")) -> dict[str, Any]:
    """Retrieve a single event by its unique identifier. Returns a dictionary containing the event details."""

    # Construct request model with validation
    try:
        _request = _models.GetEventIdRequest(
            path=_models.GetEventIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_event: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/event/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/event/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_event")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_event", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_event",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Event Log
@mcp.tool()
async def list_events(
    object_type: str | None = Field(None, description="Filter results to events for objects of a specific type (e.g., lead). When specified, only events matching this object type are returned."),
    object_id: str | None = Field(None, description="Filter results to events for a specific object by its ID (e.g., lead_123). Returns only direct events for this object, excluding related object events."),
    action: str | None = Field(None, description="Filter results to events of specific action types (e.g., deleted). Only events matching the specified action are returned."),
    request_id: str | None = Field(None, description="Filter results to events emitted during processing of a specific API request. Use this to trace all events generated by a single request."),
    limit: int | None = Field(None, alias="_limit", description="Maximum number of events to return in the response. Limited to a maximum of 50 events; defaults to 50 if not specified.", le=50),
) -> dict[str, Any]:
    """Retrieve a paginated list of events from the event log, ordered by date with the most recent first. Supports filtering by object type, object ID, action, lead ID, user ID, and request ID to narrow results to specific events of interest."""

    # Construct request model with validation
    try:
        _request = _models.GetEventRequest(
            query=_models.GetEventRequestQuery(object_type=object_type, object_id=object_id, action=action, request_id=request_id, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_events: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/event"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
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
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Webhook Subscriptions
@mcp.tool()
async def list_webhooks() -> dict[str, Any]:
    """Retrieve all webhook subscriptions configured for your organization. This lists the active webhooks that are receiving event notifications."""

    # Extract parameters for API call
    _http_path = "/webhook"
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

# Tags: Webhook Subscriptions
@mcp.tool()
async def create_webhook(
    url: str = Field(..., description="The destination URL where webhook events will be sent. Must be a valid URI (e.g., https://example.com/webhook)."),
    events: list[_models.PostWebhookBodyEventsItem] = Field(..., description="List of events to subscribe to. Each event specifies an object type and action to monitor (e.g., user.created, order.updated). Only events matching these subscriptions will be sent to your webhook URL."),
    verify_ssl: bool | None = Field(None, description="Whether to verify the SSL certificate when sending events to your webhook URL. Enabled by default for security; disable only if using self-signed certificates in development."),
) -> dict[str, Any]:
    """Create a new webhook subscription to receive event notifications at a specified URL. The webhook will automatically send POST requests to your endpoint whenever subscribed events occur."""

    # Construct request model with validation
    try:
        _request = _models.PostWebhookRequest(
            body=_models.PostWebhookRequestBody(url=url, events=events, verify_ssl=verify_ssl)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_webhook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/webhook"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_webhook")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_webhook", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_webhook",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Webhook Subscriptions
@mcp.tool()
async def get_webhook(id_: str = Field(..., alias="id", description="The unique identifier of the webhook subscription to retrieve.")) -> dict[str, Any]:
    """Retrieve the details of a specific webhook subscription by its unique identifier. Returns configuration, status, and event settings for the webhook."""

    # Construct request model with validation
    try:
        _request = _models.GetWebhookIdRequest(
            path=_models.GetWebhookIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_webhook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/webhook/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/webhook/{id}"
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

# Tags: Webhook Subscriptions
@mcp.tool()
async def update_webhook(
    id_: str = Field(..., alias="id", description="The unique identifier of the webhook subscription to update."),
    url: str | None = Field(None, description="The destination URL where webhook events will be sent. Must be a valid URI."),
    events: list[_models.PutWebhookIdBodyEventsItem] | None = Field(None, description="List of events to subscribe to. Each event specifies an object type and an action to trigger the webhook."),
    verify_ssl: bool | None = Field(None, description="Whether to verify the SSL certificate of the destination webhook URL. Set to true for production environments to ensure secure connections."),
) -> dict[str, Any]:
    """Update an existing webhook subscription with new configuration. Only the parameters you provide will be updated; omitted parameters retain their current values."""

    # Construct request model with validation
    try:
        _request = _models.PutWebhookIdRequest(
            path=_models.PutWebhookIdRequestPath(id_=id_),
            body=_models.PutWebhookIdRequestBody(url=url, events=events, verify_ssl=verify_ssl)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_webhook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/webhook/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/webhook/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_webhook")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_webhook", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_webhook",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Webhook Subscriptions
@mcp.tool()
async def delete_webhook(id_: str = Field(..., alias="id", description="The unique identifier of the webhook subscription to delete.")) -> dict[str, Any]:
    """Delete a webhook subscription to stop receiving event notifications at the configured endpoint."""

    # Construct request model with validation
    try:
        _request = _models.DeleteWebhookIdRequest(
            path=_models.DeleteWebhookIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_webhook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/webhook/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/webhook/{id}"
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

# Tags: Scheduling Links
@mcp.tool()
async def list_scheduling_links() -> dict[str, Any]:
    """Retrieve all scheduling links that have been created by the authenticated user. This allows you to view and manage all available scheduling links for booking meetings or appointments."""

    # Extract parameters for API call
    _http_path = "/scheduling_link"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_scheduling_links")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_scheduling_links", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_scheduling_links",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Scheduling Links
@mcp.tool()
async def create_scheduling_link(
    name: str = Field(..., description="A descriptive name for the scheduling link to help identify it among your other scheduling links."),
    url: str = Field(..., description="The external URL where the scheduling link points to. Must be a valid URI format."),
    description: str | None = Field(None, description="An optional description providing additional context or details about the scheduling link's purpose."),
) -> dict[str, Any]:
    """Create a new scheduling link that can be shared with users to access your availability and book meetings."""

    # Construct request model with validation
    try:
        _request = _models.PostSchedulingLinkRequest(
            body=_models.PostSchedulingLinkRequestBody(name=name, url=url, description=description)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_scheduling_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/scheduling_link"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_scheduling_link")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_scheduling_link", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_scheduling_link",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Scheduling Links
@mcp.tool()
async def get_scheduling_link(id_: str = Field(..., alias="id", description="The unique identifier of the scheduling link to retrieve.")) -> dict[str, Any]:
    """Retrieve a scheduling link by its unique identifier to access its configuration and sharing details."""

    # Construct request model with validation
    try:
        _request = _models.GetSchedulingLinkIdRequest(
            path=_models.GetSchedulingLinkIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_scheduling_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/scheduling_link/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/scheduling_link/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_scheduling_link")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_scheduling_link", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_scheduling_link",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Scheduling Links
@mcp.tool()
async def update_scheduling_link(
    id_: str = Field(..., alias="id", description="The unique identifier of the scheduling link to update."),
    name: str | None = Field(None, description="A display name for the scheduling link as shown in the Close application."),
    url: str | None = Field(None, description="The external URL for the scheduling link. Must be a valid URI format."),
    description: str | None = Field(None, description="A description for the scheduling link displayed in the Close application."),
    source_id: str | None = Field(None, description="The identifier for this scheduling link in the source or integrating application."),
    source_type: str | None = Field(None, description="A short descriptor identifying the type or category of the scheduling link."),
    duration_in_minutes: int | None = Field(None, description="The duration of meetings scheduled with this link, specified in minutes."),
) -> dict[str, Any]:
    """Update an existing scheduling link by its unique identifier. Modify scheduling link details such as name, URL, description, and meeting duration."""

    # Construct request model with validation
    try:
        _request = _models.PutSchedulingLinkIdRequest(
            path=_models.PutSchedulingLinkIdRequestPath(id_=id_),
            body=_models.PutSchedulingLinkIdRequestBody(name=name, url=url, description=description, source_id=source_id, source_type=source_type, duration_in_minutes=duration_in_minutes)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_scheduling_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/scheduling_link/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/scheduling_link/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_scheduling_link")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_scheduling_link", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_scheduling_link",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Scheduling Links
@mcp.tool()
async def delete_scheduling_link(id_: str = Field(..., alias="id", description="The unique identifier of the scheduling link to delete.")) -> dict[str, Any]:
    """Remove a scheduling link by its unique identifier. This permanently deletes the scheduling link and prevents further access to it."""

    # Construct request model with validation
    try:
        _request = _models.DeleteSchedulingLinkIdRequest(
            path=_models.DeleteSchedulingLinkIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_scheduling_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/scheduling_link/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/scheduling_link/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_scheduling_link")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_scheduling_link", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_scheduling_link",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Scheduling Links
@mcp.tool()
async def upsert_scheduling_link(
    source_id: str = Field(..., description="Your OAuth application's unique identifier for this scheduling link. Used to identify and deduplicate resources created by your app."),
    name: str | None = Field(None, description="Human-readable name displayed to users for this scheduling link."),
    url: str | None = Field(None, description="Public-facing URL where users can access and interact with this scheduling link. Must be a valid URI."),
    description: str | None = Field(None, description="Additional context or explanation about the scheduling link's purpose and usage."),
    source_type: str | None = Field(None, description="Category or classification type for organizing and filtering scheduling links."),
    duration_in_minutes: int | None = Field(None, description="Default meeting duration in minutes for scheduling sessions created through this link."),
) -> dict[str, Any]:
    """Create a new scheduling link or update an existing one using your OAuth application's unique identifier. The system uses the source_id to detect and merge duplicate resources, ensuring only one scheduling link exists per source_id."""

    # Construct request model with validation
    try:
        _request = _models.PostSchedulingLinkIntegrationRequest(
            body=_models.PostSchedulingLinkIntegrationRequestBody(source_id=source_id, name=name, url=url, description=description, source_type=source_type, duration_in_minutes=duration_in_minutes)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for upsert_scheduling_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/scheduling_link/integration"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("upsert_scheduling_link")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("upsert_scheduling_link", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="upsert_scheduling_link",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Scheduling Links
@mcp.tool()
async def delete_scheduling_link_oauth(source_id: str = Field(..., description="The unique source identifier of the scheduling link to delete, as assigned by your OAuth application when the link was created.")) -> dict[str, Any]:
    """Delete a scheduling link by its source identifier. This operation is only available to OAuth applications and uses the source_id assigned by your OAuth app to identify and remove the scheduling link."""

    # Construct request model with validation
    try:
        _request = _models.DeleteSchedulingLinkIntegrationSourceIdRequest(
            path=_models.DeleteSchedulingLinkIntegrationSourceIdRequestPath(source_id=source_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_scheduling_link_oauth: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/scheduling_link/integration/{source_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/scheduling_link/integration/{source_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_scheduling_link_oauth")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_scheduling_link_oauth", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_scheduling_link_oauth",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Scheduling Links
@mcp.tool()
async def list_scheduling_links_shared() -> dict[str, Any]:
    """Retrieve all shared scheduling links available in your account. Use this to view and manage scheduling links you've created for others to book time with you."""

    # Extract parameters for API call
    _http_path = "/shared_scheduling_link"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_scheduling_links_shared")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_scheduling_links_shared", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_scheduling_links_shared",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Scheduling Links
@mcp.tool()
async def create_scheduling_link_shared(body: dict[str, Any] = Field(..., description="Configuration object for the shared scheduling link, including settings such as availability windows, booking constraints, and link customization options.")) -> dict[str, Any]:
    """Create a shared scheduling link that allows others to view your available time slots and book meetings directly on your calendar without needing direct access to your calendar."""

    # Construct request model with validation
    try:
        _request = _models.PostSharedSchedulingLinkRequest(
            body=_models.PostSharedSchedulingLinkRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_scheduling_link_shared: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/shared_scheduling_link"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_scheduling_link_shared")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_scheduling_link_shared", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_scheduling_link_shared",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Scheduling Links
@mcp.tool()
async def get_scheduling_link_shared(id_: str = Field(..., alias="id", description="The unique identifier of the shared scheduling link to retrieve.")) -> dict[str, Any]:
    """Retrieve a specific shared scheduling link by its unique identifier to access its configuration and sharing details."""

    # Construct request model with validation
    try:
        _request = _models.GetSharedSchedulingLinkIdRequest(
            path=_models.GetSharedSchedulingLinkIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_scheduling_link_shared: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/shared_scheduling_link/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/shared_scheduling_link/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_scheduling_link_shared")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_scheduling_link_shared", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_scheduling_link_shared",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Scheduling Links
@mcp.tool()
async def update_scheduling_link_shared(
    id_: str = Field(..., alias="id", description="The unique identifier of the shared scheduling link to update."),
    body: dict[str, Any] | None = Field(None, description="An object containing the scheduling link properties to modify. Only provided fields will be updated; omitted fields remain unchanged."),
) -> dict[str, Any]:
    """Modify the configuration and settings of an existing shared scheduling link, such as availability windows, meeting duration, or access permissions."""

    # Construct request model with validation
    try:
        _request = _models.PutSharedSchedulingLinkIdRequest(
            path=_models.PutSharedSchedulingLinkIdRequestPath(id_=id_),
            body=_models.PutSharedSchedulingLinkIdRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_scheduling_link_shared: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/shared_scheduling_link/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/shared_scheduling_link/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_scheduling_link_shared")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_scheduling_link_shared", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_scheduling_link_shared",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Scheduling Links
@mcp.tool()
async def delete_scheduling_link_shared(id_: str = Field(..., alias="id", description="The unique identifier of the shared scheduling link to delete.")) -> dict[str, Any]:
    """Permanently delete a shared scheduling link by its ID. This action cannot be undone and will immediately revoke access to the scheduling link for all users."""

    # Construct request model with validation
    try:
        _request = _models.DeleteSharedSchedulingLinkIdRequest(
            path=_models.DeleteSharedSchedulingLinkIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_scheduling_link_shared: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/shared_scheduling_link/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/shared_scheduling_link/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_scheduling_link_shared")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_scheduling_link_shared", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_scheduling_link_shared",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Scheduling Links
@mcp.tool()
async def associate_shared_scheduling_link(
    shared_scheduling_link_id: str = Field(..., description="The unique identifier of the shared scheduling link to associate."),
    user_scheduling_link_id: str | None = Field(None, description="The unique identifier of the user scheduling link to associate with the shared link. Either this parameter or url must be provided."),
    url: str | None = Field(None, description="A valid URI to associate with the shared link. Either this parameter or user_scheduling_link_id must be provided."),
) -> dict[str, Any]:
    """Associate a shared scheduling link with either a user scheduling link or a custom URL to enable scheduling access through the shared link."""

    # Construct request model with validation
    try:
        _request = _models.PostSharedSchedulingLinkAssociationRequest(
            body=_models.PostSharedSchedulingLinkAssociationRequestBody(shared_scheduling_link_id=shared_scheduling_link_id, user_scheduling_link_id=user_scheduling_link_id, url=url)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for associate_shared_scheduling_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/shared_scheduling_link_association"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("associate_shared_scheduling_link")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("associate_shared_scheduling_link", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="associate_shared_scheduling_link",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Scheduling Links
@mcp.tool()
async def disable_shared_scheduling_link(shared_scheduling_link_id: str = Field(..., description="The unique identifier of the shared scheduling link to disable.")) -> dict[str, Any]:
    """Disable a shared scheduling link by removing its association with a user scheduling link or URL, preventing further access through that shared link."""

    # Construct request model with validation
    try:
        _request = _models.PostSharedSchedulingLinkAssociationUnmapRequest(
            body=_models.PostSharedSchedulingLinkAssociationUnmapRequestBody(shared_scheduling_link_id=shared_scheduling_link_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for disable_shared_scheduling_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/shared_scheduling_link_association/unmap"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("disable_shared_scheduling_link")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("disable_shared_scheduling_link", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="disable_shared_scheduling_link",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Fields
@mcp.tool()
async def list_lead_custom_fields(limit: int | None = Field(None, alias="_limit", description="Maximum number of custom fields to return in the response. Omit to retrieve all available custom fields.")) -> dict[str, Any]:
    """Retrieve all custom fields configured for leads in your organization. Use the optional limit parameter to control the number of results returned."""

    # Construct request model with validation
    try:
        _request = _models.GetCustomFieldLeadRequest(
            query=_models.GetCustomFieldLeadRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_lead_custom_fields: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/custom_field/lead"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_lead_custom_fields")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_lead_custom_fields", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_lead_custom_fields",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Fields
@mcp.tool()
async def create_lead_custom_field(
    name: str = Field(..., description="The display name for the custom field that will appear in the UI and API responses."),
    type_: str = Field(..., alias="type", description="The data type of the custom field (e.g., text, number, date, choice). This determines how the field stores and validates data."),
    accepts_multiple_values: bool | None = Field(None, description="Whether this field can store multiple values simultaneously. Useful for fields like tags or multi-select options."),
    options: list[dict[str, Any]] | None = Field(None, description="Predefined options available for choice-type fields. Each option becomes a selectable value when the field type supports choices."),
    editable_roles: list[str] | None = Field(None, description="List of user roles that have permission to edit this custom field. If not specified, defaults to system defaults or all roles."),
) -> dict[str, Any]:
    """Create a new custom field for leads with configurable data type, multiple value support, and role-based edit permissions."""

    # Construct request model with validation
    try:
        _request = _models.PostCustomFieldLeadRequest(
            body=_models.PostCustomFieldLeadRequestBody(name=name, type_=type_, accepts_multiple_values=accepts_multiple_values, options=options, editable_roles=editable_roles)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_lead_custom_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/custom_field/lead"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_lead_custom_field")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_lead_custom_field", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_lead_custom_field",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Fields
@mcp.tool()
async def get_lead_custom_field(id_: str = Field(..., alias="id", description="The unique identifier of the lead custom field to retrieve.")) -> dict[str, Any]:
    """Retrieve the details of a specific custom field associated with a lead, including its configuration and current values."""

    # Construct request model with validation
    try:
        _request = _models.GetCustomFieldLeadIdRequest(
            path=_models.GetCustomFieldLeadIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_lead_custom_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/custom_field/lead/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/custom_field/lead/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_lead_custom_field")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_lead_custom_field", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_lead_custom_field",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Fields
@mcp.tool()
async def update_lead_custom_field(
    custom_field_id: str = Field(..., description="The unique identifier of the Lead custom field to update."),
    name: str | None = Field(None, description="The new display name for the custom field."),
    accepts_multiple_values: bool | None = Field(None, description="Whether this field should accept multiple values simultaneously."),
    editable_roles: list[str] | None = Field(None, description="List of role identifiers that are permitted to edit this field's values. Only users with these roles can modify the field."),
    options: list[dict[str, Any]] | None = Field(None, description="Array of choice options for fields with choice/select type. Each option represents a selectable value in the field."),
) -> dict[str, Any]:
    """Update a Lead custom field's configuration including its name, type, multi-value support, role-based edit permissions, and choice options. Changes take effect immediately in the Close UI."""

    # Construct request model with validation
    try:
        _request = _models.PutCustomFieldLeadCustomFieldIdRequest(
            path=_models.PutCustomFieldLeadCustomFieldIdRequestPath(custom_field_id=custom_field_id),
            body=_models.PutCustomFieldLeadCustomFieldIdRequestBody(name=name, accepts_multiple_values=accepts_multiple_values, editable_roles=editable_roles, options=options)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_lead_custom_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/custom_field/lead/{custom_field_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/custom_field/lead/{custom_field_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_lead_custom_field")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_lead_custom_field", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_lead_custom_field",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Fields
@mcp.tool()
async def delete_lead_custom_field(custom_field_id: str = Field(..., description="The unique identifier of the Lead custom field to delete.")) -> dict[str, Any]:
    """Permanently delete a custom field from your Lead records. The field will be immediately removed from all Lead API responses and cannot be recovered."""

    # Construct request model with validation
    try:
        _request = _models.DeleteCustomFieldLeadCustomFieldIdRequest(
            path=_models.DeleteCustomFieldLeadCustomFieldIdRequestPath(custom_field_id=custom_field_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_lead_custom_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/custom_field/lead/{custom_field_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/custom_field/lead/{custom_field_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_lead_custom_field")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_lead_custom_field", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_lead_custom_field",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Fields
@mcp.tool()
async def list_contact_custom_fields(limit: int | None = Field(None, alias="_limit", description="Maximum number of custom fields to return in the response. Useful for pagination or limiting result set size.")) -> dict[str, Any]:
    """Retrieve all custom fields configured for contacts in your organization. Use the limit parameter to control the number of results returned."""

    # Construct request model with validation
    try:
        _request = _models.GetCustomFieldContactRequest(
            query=_models.GetCustomFieldContactRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_contact_custom_fields: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/custom_field/contact"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_contact_custom_fields")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_contact_custom_fields", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_contact_custom_fields",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Fields
@mcp.tool()
async def create_contact_custom_field(
    name: str = Field(..., description="The display name for the custom field. This is the label users will see when viewing or editing contact records."),
    type_: str = Field(..., alias="type", description="The data type for the custom field. Supported types include text, number, date, and choice. The type determines how the field stores and validates data."),
    accepts_multiple_values: bool | None = Field(None, description="Enable this to allow the field to store multiple values. Useful for fields like tags, skills, or other multi-select attributes."),
    options: list[dict[str, Any]] | None = Field(None, description="A list of predefined options for choice-type fields. Each option becomes a selectable value when users interact with the field. Only applicable when type is set to choice."),
    restricted_to_roles: bool | None = Field(None, description="Enable this to restrict field editing permissions to users with specific roles. When enabled, only authorized users can modify values in this field."),
) -> dict[str, Any]:
    """Create a new custom field for contacts with configurable data types and optional multi-value support. Use this to extend contact records with additional attributes tailored to your business needs."""

    # Construct request model with validation
    try:
        _request = _models.PostCustomFieldContactRequest(
            body=_models.PostCustomFieldContactRequestBody(name=name, type_=type_, accepts_multiple_values=accepts_multiple_values, options=options, restricted_to_roles=restricted_to_roles)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_contact_custom_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/custom_field/contact"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_contact_custom_field")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_contact_custom_field", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_contact_custom_field",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Fields
@mcp.tool()
async def get_contact_custom_field(id_: str = Field(..., alias="id", description="The unique identifier of the contact custom field to retrieve.")) -> dict[str, Any]:
    """Retrieve the details of a specific custom field associated with a contact. Use this to access custom field configuration and values for a particular contact."""

    # Construct request model with validation
    try:
        _request = _models.GetCustomFieldContactIdRequest(
            path=_models.GetCustomFieldContactIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_contact_custom_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/custom_field/contact/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/custom_field/contact/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_contact_custom_field")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_contact_custom_field", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_contact_custom_field",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Fields
@mcp.tool()
async def update_contact_custom_field(
    custom_field_id: str = Field(..., description="The unique identifier of the contact custom field to update."),
    name: str | None = Field(None, description="The new display name for the custom field as it will appear in the Close UI."),
    accepts_multiple_values: bool | None = Field(None, description="Whether this field can store multiple values simultaneously."),
    restricted_to_roles: bool | None = Field(None, description="Whether editing this field's values should be restricted to users with specific roles."),
    options: list[dict[str, Any]] | None = Field(None, description="A list of predefined values available for selection when the field type is choice-based. Order and format should match the field's expected choice structure."),
) -> dict[str, Any]:
    """Update a contact custom field's configuration including its display name, value multiplicity, role-based access restrictions, and available options for choice-based fields. Changes take effect immediately in the Close UI."""

    # Construct request model with validation
    try:
        _request = _models.PutCustomFieldContactCustomFieldIdRequest(
            path=_models.PutCustomFieldContactCustomFieldIdRequestPath(custom_field_id=custom_field_id),
            body=_models.PutCustomFieldContactCustomFieldIdRequestBody(name=name, accepts_multiple_values=accepts_multiple_values, restricted_to_roles=restricted_to_roles, options=options)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_contact_custom_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/custom_field/contact/{custom_field_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/custom_field/contact/{custom_field_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_contact_custom_field")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_contact_custom_field", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_contact_custom_field",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Fields
@mcp.tool()
async def delete_contact_custom_field(custom_field_id: str = Field(..., description="The unique identifier of the custom field to delete.")) -> dict[str, Any]:
    """Permanently delete a custom field from your Contact system. The field will be immediately removed from all Contact API responses and cannot be recovered."""

    # Construct request model with validation
    try:
        _request = _models.DeleteCustomFieldContactCustomFieldIdRequest(
            path=_models.DeleteCustomFieldContactCustomFieldIdRequestPath(custom_field_id=custom_field_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_contact_custom_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/custom_field/contact/{custom_field_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/custom_field/contact/{custom_field_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_contact_custom_field")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_contact_custom_field", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_contact_custom_field",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Opportunity Custom Fields
@mcp.tool()
async def list_opportunity_custom_fields(limit: int | None = Field(None, alias="_limit", description="Maximum number of custom fields to return in the response. Useful for pagination when dealing with large numbers of custom fields.")) -> dict[str, Any]:
    """Retrieve all custom fields configured for opportunities in your organization. Use this to understand the custom data structure available for opportunity records."""

    # Construct request model with validation
    try:
        _request = _models.GetCustomFieldOpportunityRequest(
            query=_models.GetCustomFieldOpportunityRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_opportunity_custom_fields: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/custom_field/opportunity"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_opportunity_custom_fields")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_opportunity_custom_fields", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_opportunity_custom_fields",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Fields
@mcp.tool()
async def create_opportunity_custom_field(
    name: str = Field(..., description="The display name for the custom field. This is how the field will be identified throughout the system."),
    type_: str = Field(..., alias="type", description="The data type that determines how the field stores and validates data (e.g., text, number, date, choice)."),
    accepts_multiple_values: bool | None = Field(None, description="When enabled, allows the field to store multiple values simultaneously rather than a single value."),
    editable_with_roles: list[str] | None = Field(None, description="A list of role identifiers that have permission to edit this field. If not specified, default role permissions apply."),
    options: list[dict[str, Any]] | None = Field(None, description="A list of predefined choices available for selection when the field type is set to choice or similar selection-based types. Order may be significant for display purposes."),
) -> dict[str, Any]:
    """Create a new custom field for Opportunity records. Define the field's name, data type, and optionally configure multi-value support, role-based editing permissions, and predefined options for choice fields."""

    # Construct request model with validation
    try:
        _request = _models.PostCustomFieldOpportunityRequest(
            body=_models.PostCustomFieldOpportunityRequestBody(name=name, type_=type_, accepts_multiple_values=accepts_multiple_values, editable_with_roles=editable_with_roles, options=options)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_opportunity_custom_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/custom_field/opportunity"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_opportunity_custom_field")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_opportunity_custom_field", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_opportunity_custom_field",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Opportunity Custom Fields
@mcp.tool()
async def get_opportunity_custom_field(id_: str = Field(..., alias="id", description="The unique identifier of the custom field to retrieve. This ID must correspond to an existing custom field in the opportunity.")) -> dict[str, Any]:
    """Retrieve detailed information about a specific custom field associated with an opportunity. Use this to fetch custom field values and metadata for a given opportunity."""

    # Construct request model with validation
    try:
        _request = _models.GetCustomFieldOpportunityIdRequest(
            path=_models.GetCustomFieldOpportunityIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_opportunity_custom_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/custom_field/opportunity/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/custom_field/opportunity/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_opportunity_custom_field")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_opportunity_custom_field", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_opportunity_custom_field",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Opportunity Custom Fields
@mcp.tool()
async def update_opportunity_custom_field(
    custom_field_id: str = Field(..., description="The unique identifier of the custom field to update."),
    name: str | None = Field(None, description="The new display name for the custom field."),
    accepts_multiple_values: bool | None = Field(None, description="Whether the field should accept multiple values simultaneously."),
    restricted_to_roles: bool | None = Field(None, description="Whether editing this field's values should be restricted to users with specific roles."),
    options: list[dict[str, Any]] | None = Field(None, description="Updated list of available options for a choices field type. Order is preserved and determines the display sequence in the UI."),
) -> dict[str, Any]:
    """Update an Opportunity Custom Field by modifying its name, type, value acceptance settings, role restrictions, or choice options. Changes take effect immediately in the Close UI, and type conversions are handled automatically when required."""

    # Construct request model with validation
    try:
        _request = _models.PutCustomFieldOpportunityCustomFieldIdRequest(
            path=_models.PutCustomFieldOpportunityCustomFieldIdRequestPath(custom_field_id=custom_field_id),
            body=_models.PutCustomFieldOpportunityCustomFieldIdRequestBody(name=name, accepts_multiple_values=accepts_multiple_values, restricted_to_roles=restricted_to_roles, options=options)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_opportunity_custom_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/custom_field/opportunity/{custom_field_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/custom_field/opportunity/{custom_field_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_opportunity_custom_field")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_opportunity_custom_field", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_opportunity_custom_field",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Opportunity Custom Fields
@mcp.tool()
async def delete_opportunity_custom_field(custom_field_id: str = Field(..., description="The unique identifier of the custom field to delete.")) -> dict[str, Any]:
    """Permanently delete a custom field from Opportunities. The field will be immediately removed from all Opportunity records and API responses, and this action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteCustomFieldOpportunityCustomFieldIdRequest(
            path=_models.DeleteCustomFieldOpportunityCustomFieldIdRequestPath(custom_field_id=custom_field_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_opportunity_custom_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/custom_field/opportunity/{custom_field_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/custom_field/opportunity/{custom_field_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_opportunity_custom_field")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_opportunity_custom_field", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_opportunity_custom_field",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Fields
@mcp.tool()
async def list_activity_custom_fields(limit: int | None = Field(None, alias="_limit", description="Maximum number of custom fields to return in the response. Limits the result set size for pagination or performance optimization.")) -> dict[str, Any]:
    """Retrieve all custom fields configured for activities in your organization. Use the limit parameter to control the number of results returned."""

    # Construct request model with validation
    try:
        _request = _models.GetCustomFieldActivityRequest(
            query=_models.GetCustomFieldActivityRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_activity_custom_fields: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/custom_field/activity"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_activity_custom_fields")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_activity_custom_fields", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_activity_custom_fields",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Fields
@mcp.tool()
async def create_activity_custom_field(
    name: str = Field(..., description="The display name for the custom field. This is the label shown to users when interacting with the field."),
    type_: str = Field(..., alias="type", description="The data type of the field, which determines what kind of values it can store (e.g., text, number, date, choice)."),
    custom_activity_type_id: str = Field(..., description="The ID of the Custom Activity Type this field belongs to. The field will be associated with and available only for activities of this type."),
    required: bool | None = Field(None, description="Whether this field must be populated before an activity can be published. When enabled, the field becomes mandatory for activity creation."),
    accepts_multiple_values: bool | None = Field(None, description="Whether this field can store multiple values simultaneously. When enabled, the field can hold a collection of values instead of a single value."),
    options: list[dict[str, Any]] | None = Field(None, description="A list of predefined options available for selection in choice-type fields. Each option represents a valid value users can select from."),
) -> dict[str, Any]:
    """Create a new custom field for a specific Custom Activity Type. Custom fields extend activity records with additional data attributes and can be configured as required or optional."""

    # Construct request model with validation
    try:
        _request = _models.PostCustomFieldActivityRequest(
            body=_models.PostCustomFieldActivityRequestBody(name=name, type_=type_, custom_activity_type_id=custom_activity_type_id, required=required, accepts_multiple_values=accepts_multiple_values, options=options)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_activity_custom_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/custom_field/activity"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_activity_custom_field")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_activity_custom_field", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_activity_custom_field",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Fields
@mcp.tool()
async def get_activity_custom_field(id_: str = Field(..., alias="id", description="The unique identifier of the Activity Custom Field to retrieve.")) -> dict[str, Any]:
    """Retrieve the details of a specific Activity Custom Field by its unique identifier. Use this to access configuration, metadata, and settings for a custom field associated with activities."""

    # Construct request model with validation
    try:
        _request = _models.GetCustomFieldActivityIdRequest(
            path=_models.GetCustomFieldActivityIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_activity_custom_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/custom_field/activity/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/custom_field/activity/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_activity_custom_field")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_activity_custom_field", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_activity_custom_field",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Fields
@mcp.tool()
async def update_activity_custom_field(
    custom_field_id: str = Field(..., description="The unique identifier of the Activity Custom Field to update."),
    name: str | None = Field(None, description="New display name for the custom field."),
    required: bool | None = Field(None, description="Whether this field must be populated before publishing an activity."),
    accepts_multiple_values: bool | None = Field(None, description="Whether this field allows users to select or enter multiple values."),
    restricted_to_roles: list[str] | None = Field(None, description="List of role identifiers that are permitted to edit this field. If specified, only users with these roles can modify the field value."),
    options: list[dict[str, Any]] | None = Field(None, description="Updated list of available choices for a choices-type field. Each option should include its identifier and display label."),
) -> dict[str, Any]:
    """Update an existing Activity Custom Field by modifying its name, requirements, multi-value support, role-based access restrictions, or choice options. The field type and associated activity type cannot be changed."""

    # Construct request model with validation
    try:
        _request = _models.PutCustomFieldActivityCustomFieldIdRequest(
            path=_models.PutCustomFieldActivityCustomFieldIdRequestPath(custom_field_id=custom_field_id),
            body=_models.PutCustomFieldActivityCustomFieldIdRequestBody(name=name, required=required, accepts_multiple_values=accepts_multiple_values, restricted_to_roles=restricted_to_roles, options=options)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_activity_custom_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/custom_field/activity/{custom_field_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/custom_field/activity/{custom_field_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_activity_custom_field")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_activity_custom_field", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_activity_custom_field",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Fields
@mcp.tool()
async def delete_activity_custom_field(custom_field_id: str = Field(..., description="The unique identifier of the Activity Custom Field to delete.")) -> dict[str, Any]:
    """Permanently delete an Activity Custom Field. The field will be immediately removed from all Custom Activity API responses and cannot be recovered."""

    # Construct request model with validation
    try:
        _request = _models.DeleteCustomFieldActivityCustomFieldIdRequest(
            path=_models.DeleteCustomFieldActivityCustomFieldIdRequestPath(custom_field_id=custom_field_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_activity_custom_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/custom_field/activity/{custom_field_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/custom_field/activity/{custom_field_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_activity_custom_field")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_activity_custom_field", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_activity_custom_field",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Fields
@mcp.tool()
async def list_custom_object_custom_fields() -> dict[str, Any]:
    """Retrieve all custom fields associated with custom objects in your organization. This operation returns the complete list of custom fields that have been defined for your custom object types."""

    # Extract parameters for API call
    _http_path = "/custom_field/custom_object_type"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_custom_object_custom_fields")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_custom_object_custom_fields", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_custom_object_custom_fields",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Fields
@mcp.tool()
async def create_custom_object_field(
    name: str = Field(..., description="The display name for the custom field, shown in the user interface."),
    type_: str = Field(..., alias="type", description="The data type that defines what kind of values this field accepts (e.g., text, number, date, choice)."),
    custom_object_type_id: str = Field(..., description="The unique identifier of the Custom Object Type that this field belongs to."),
    required: bool | None = Field(None, description="Whether this field must have a value before the custom object can be saved."),
    accepts_multiple_values: bool | None = Field(None, description="Whether this field can store multiple values instead of a single value."),
    editable_with_roles: list[str] | None = Field(None, description="A list of role identifiers that are permitted to edit this field. If not specified, all roles may edit the field."),
    options: list[dict[str, Any]] | None = Field(None, description="A list of predefined options available for selection when the field type is set to choice. Each option should be formatted as specified by the field type."),
) -> dict[str, Any]:
    """Create a new custom field for a specific Custom Object Type. The field will be added to the object type's schema and can be configured as required or optional, with support for multiple values and role-based edit permissions."""

    # Construct request model with validation
    try:
        _request = _models.PostCustomFieldCustomObjectTypeRequest(
            body=_models.PostCustomFieldCustomObjectTypeRequestBody(name=name, type_=type_, custom_object_type_id=custom_object_type_id, required=required, accepts_multiple_values=accepts_multiple_values, editable_with_roles=editable_with_roles, options=options)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_custom_object_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/custom_field/custom_object_type"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_custom_object_field")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_custom_object_field", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_custom_object_field",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Fields
@mcp.tool()
async def get_custom_field(id_: str = Field(..., alias="id", description="The unique identifier of the custom field to retrieve.")) -> dict[str, Any]:
    """Retrieve the details of a specific custom field associated with a custom object type. This includes field configuration, type, and metadata."""

    # Construct request model with validation
    try:
        _request = _models.GetCustomFieldCustomObjectTypeIdRequest(
            path=_models.GetCustomFieldCustomObjectTypeIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_custom_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/custom_field/custom_object_type/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/custom_field/custom_object_type/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_custom_field")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_custom_field", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_custom_field",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Fields
@mcp.tool()
async def update_custom_field(
    custom_field_id: str = Field(..., description="The unique identifier of the custom field to update."),
    name: str | None = Field(None, description="The new display name for the custom field."),
    required: bool | None = Field(None, description="Whether this field must be populated to save the custom object."),
    accepts_multiple_values: bool | None = Field(None, description="Whether this field can store multiple values simultaneously."),
    editable_with_roles: list[str] | None = Field(None, description="List of role identifiers that are permitted to edit this field's values. If specified, only users with these roles can modify the field."),
    options: list[dict[str, Any]] | None = Field(None, description="Updated list of available choices for a choices-type field. Each item represents a selectable option."),
) -> dict[str, Any]:
    """Update a custom object field's configuration, including its name, requirement status, multi-value support, role-based edit restrictions, and choice options. The field type and custom object type cannot be modified."""

    # Construct request model with validation
    try:
        _request = _models.PutCustomFieldCustomObjectTypeCustomFieldIdRequest(
            path=_models.PutCustomFieldCustomObjectTypeCustomFieldIdRequestPath(custom_field_id=custom_field_id),
            body=_models.PutCustomFieldCustomObjectTypeCustomFieldIdRequestBody(name=name, required=required, accepts_multiple_values=accepts_multiple_values, editable_with_roles=editable_with_roles, options=options)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_custom_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/custom_field/custom_object_type/{custom_field_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/custom_field/custom_object_type/{custom_field_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_custom_field")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_custom_field", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_custom_field",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Fields
@mcp.tool()
async def delete_custom_field(custom_field_id: str = Field(..., description="The unique identifier of the custom field to delete.")) -> dict[str, Any]:
    """Permanently delete a custom field from a custom object type. The field will be immediately removed from all Custom Object API responses."""

    # Construct request model with validation
    try:
        _request = _models.DeleteCustomFieldCustomObjectTypeCustomFieldIdRequest(
            path=_models.DeleteCustomFieldCustomObjectTypeCustomFieldIdRequestPath(custom_field_id=custom_field_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_custom_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/custom_field/custom_object_type/{custom_field_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/custom_field/custom_object_type/{custom_field_id}"
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

# Tags: Custom Fields
@mcp.tool()
async def list_shared_custom_fields() -> dict[str, Any]:
    """Retrieve all shared custom fields available across your organization. These fields can be used across multiple resources and are accessible to authorized users."""

    # Extract parameters for API call
    _http_path = "/custom_field/shared"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_shared_custom_fields")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_shared_custom_fields", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_shared_custom_fields",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Fields
@mcp.tool()
async def create_shared_custom_field(
    name: str = Field(..., description="The display name for the custom field. This is the label users will see when interacting with this field."),
    type_: str = Field(..., alias="type", description="The data type that defines how values in this custom field are stored and validated (e.g., text, number, date, dropdown)."),
    associations: list[dict[str, Any]] | None = Field(None, description="A list of object types this custom field can be applied to. Specifies which entities in your workspace can use this shared custom field."),
) -> dict[str, Any]:
    """Create a new shared custom field that can be reused across multiple object types in your workspace. Shared custom fields provide consistent data structure and validation across associated objects."""

    # Construct request model with validation
    try:
        _request = _models.PostCustomFieldSharedRequest(
            body=_models.PostCustomFieldSharedRequestBody(name=name, type_=type_, associations=associations)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_shared_custom_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/custom_field/shared"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_shared_custom_field")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_shared_custom_field", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_shared_custom_field",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Fields
@mcp.tool()
async def update_shared_custom_field(
    custom_field_id: str = Field(..., description="The unique identifier of the shared custom field to update."),
    name: str | None = Field(None, description="The new name for the custom field. Provide a descriptive name to identify the field's purpose."),
    choices: list[str] | None = Field(None, description="Updated list of options for a choices field type. Each item represents an available choice that users can select. Only applicable for fields with a choices type."),
) -> dict[str, Any]:
    """Update a shared custom field by modifying its name or the available options for a choices field type. The field type itself cannot be changed after creation."""

    # Construct request model with validation
    try:
        _request = _models.PutCustomFieldSharedCustomFieldIdRequest(
            path=_models.PutCustomFieldSharedCustomFieldIdRequestPath(custom_field_id=custom_field_id),
            body=_models.PutCustomFieldSharedCustomFieldIdRequestBody(name=name, choices=choices)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_shared_custom_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/custom_field/shared/{custom_field_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/custom_field/shared/{custom_field_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_shared_custom_field")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_shared_custom_field", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_shared_custom_field",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Fields
@mcp.tool()
async def delete_custom_field_shared(custom_field_id: str = Field(..., description="The unique identifier of the shared custom field to delete.")) -> dict[str, Any]:
    """Permanently delete a shared custom field. The field will be immediately removed from all objects it was assigned to."""

    # Construct request model with validation
    try:
        _request = _models.DeleteCustomFieldSharedCustomFieldIdRequest(
            path=_models.DeleteCustomFieldSharedCustomFieldIdRequestPath(custom_field_id=custom_field_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_custom_field_shared: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/custom_field/shared/{custom_field_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/custom_field/shared/{custom_field_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_custom_field_shared")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_custom_field_shared", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_custom_field_shared",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Fields
@mcp.tool()
async def associate_shared_custom_field(
    shared_custom_field_id: str = Field(..., description="The unique identifier of the Shared Custom Field to associate with an object type."),
    object_type: Literal["lead", "contact", "opportunity", "custom_activity_type", "custom_object_type"] = Field(..., description="The object type to associate the field with. Must be one of: lead, contact, opportunity, custom_activity_type, or custom_object_type."),
    custom_activity_type_id: str | None = Field(None, description="The ID of the Custom Activity Type. Required only when object_type is set to custom_activity_type."),
    custom_object_type_id: str | None = Field(None, description="The ID of the Custom Object Type. Required only when object_type is set to custom_object_type."),
    editable_with_roles: list[str] | None = Field(None, description="A list of Role IDs that are permitted to edit the values of this field on the associated object. Roles not included in this list will have read-only access."),
    required: bool | None = Field(None, description="Whether a value must be provided for this field on the associated object. Only applicable when object_type is custom_activity_type or custom_object_type."),
) -> dict[str, Any]:
    """Associates a Shared Custom Field with a specific object type (Lead, Contact, Opportunity, Custom Activity Type, or Custom Object Type), optionally configuring edit permissions and field requirements."""

    # Construct request model with validation
    try:
        _request = _models.PostCustomFieldSharedSharedCustomFieldIdAssociationRequest(
            path=_models.PostCustomFieldSharedSharedCustomFieldIdAssociationRequestPath(shared_custom_field_id=shared_custom_field_id),
            body=_models.PostCustomFieldSharedSharedCustomFieldIdAssociationRequestBody(object_type=object_type, custom_activity_type_id=custom_activity_type_id, custom_object_type_id=custom_object_type_id, editable_with_roles=editable_with_roles, required=required)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for associate_shared_custom_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/custom_field/shared/{shared_custom_field_id}/association", _request.path.model_dump(by_alias=True)) if _request.path else "/custom_field/shared/{shared_custom_field_id}/association"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("associate_shared_custom_field")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("associate_shared_custom_field", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="associate_shared_custom_field",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Fields
@mcp.tool()
async def update_shared_custom_field_association(
    shared_custom_field_id: str = Field(..., description="The unique identifier of the Shared Custom Field being associated."),
    object_type: str = Field(..., description="The object type to associate with this field. Valid values are: lead, contact, opportunity, custom_activity_type/<catype_id>, or custom_object_type/<cotype_id>."),
    editable_with_roles: list[str] | None = Field(None, description="List of Role IDs that are permitted to edit the values of this field. Roles not included in this list cannot modify the field value."),
    required: bool | None = Field(None, description="Whether a value is mandatory for this field on the specified object type. When true, users must provide a value; when false, the field is optional."),
) -> dict[str, Any]:
    """Update an existing Shared Custom Field Association by modifying its required status and role-based edit permissions. Specify the object type (lead, contact, opportunity, or custom types) to target the correct association."""

    # Construct request model with validation
    try:
        _request = _models.PutCustomFieldSharedSharedCustomFieldIdAssociationObjectTypeRequest(
            path=_models.PutCustomFieldSharedSharedCustomFieldIdAssociationObjectTypeRequestPath(shared_custom_field_id=shared_custom_field_id, object_type=object_type),
            body=_models.PutCustomFieldSharedSharedCustomFieldIdAssociationObjectTypeRequestBody(editable_with_roles=editable_with_roles, required=required)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_shared_custom_field_association: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/custom_field/shared/{shared_custom_field_id}/association/{object_type}", _request.path.model_dump(by_alias=True)) if _request.path else "/custom_field/shared/{shared_custom_field_id}/association/{object_type}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_shared_custom_field_association")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_shared_custom_field_association", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_shared_custom_field_association",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Fields
@mcp.tool()
async def remove_shared_custom_field_association(
    custom_field_id: str = Field(..., description="The unique identifier of the Shared Custom Field to disassociate."),
    object_type: str = Field(..., description="The object type to disassociate from. Valid values are: lead, contact, opportunity, custom_activity_type/<catype_id>, or custom_object_type/<cotype_id>, where <catype_id> and <cotype_id> are the respective type identifiers."),
) -> dict[str, Any]:
    """Remove a Shared Custom Field association from a specific object type (Lead, Contact, Opportunity, Custom Activity Type, or Custom Object Type). This disassociates the custom field from the target object type."""

    # Construct request model with validation
    try:
        _request = _models.DeleteCustomFieldSharedCustomFieldIdAssociationObjectTypeRequest(
            path=_models.DeleteCustomFieldSharedCustomFieldIdAssociationObjectTypeRequestPath(custom_field_id=custom_field_id, object_type=object_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_shared_custom_field_association: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/custom_field/shared/{custom_field_id}/association/{object_type}", _request.path.model_dump(by_alias=True)) if _request.path else "/custom_field/shared/{custom_field_id}/association/{object_type}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_shared_custom_field_association")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_shared_custom_field_association", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_shared_custom_field_association",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Fields
@mcp.tool()
async def get_custom_field_schema(object_type: str = Field(..., description="The object type to fetch the schema for. Use standard types (lead, contact, opportunity), activity with a category ID (activity/<cat_id>), or custom object with a type ID (custom_object/<cotype_id>).")) -> dict[str, Any]:
    """Retrieve the custom field schema for a specific object type, including all regular and shared custom fields in their defined order. Supports standard objects (lead, contact, opportunity) and dynamic objects (activities and custom objects)."""

    # Construct request model with validation
    try:
        _request = _models.GetCustomFieldSchemaObjectTypeRequest(
            path=_models.GetCustomFieldSchemaObjectTypeRequestPath(object_type=object_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_custom_field_schema: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/custom_field_schema/{object_type}", _request.path.model_dump(by_alias=True)) if _request.path else "/custom_field_schema/{object_type}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_custom_field_schema")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_custom_field_schema", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_custom_field_schema",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Fields
@mcp.tool()
async def reorder_custom_fields(
    object_type: str = Field(..., description="The object type whose custom field schema should be reordered. Valid values include lead, contact, opportunity, activity with a category ID, or custom_object with a custom object type ID."),
    fields: list[_models.PutCustomFieldSchemaObjectTypeBodyFieldsItem] = Field(..., description="An ordered array of field ID objects that defines the new field sequence. Each item should contain an id property; fields not included in this list will be automatically appended to the end."),
) -> dict[str, Any]:
    """Reorder custom fields within a schema by specifying the desired field order. Fields omitted from the list will be appended at the end; to remove fields, delete them or disassociate shared custom fields instead."""

    # Construct request model with validation
    try:
        _request = _models.PutCustomFieldSchemaObjectTypeRequest(
            path=_models.PutCustomFieldSchemaObjectTypeRequestPath(object_type=object_type),
            body=_models.PutCustomFieldSchemaObjectTypeRequestBody(fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for reorder_custom_fields: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/custom_field_schema/{object_type}", _request.path.model_dump(by_alias=True)) if _request.path else "/custom_field_schema/{object_type}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("reorder_custom_fields")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("reorder_custom_fields", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="reorder_custom_fields",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Field Enrichment
@mcp.tool()
async def enrich_field(
    organization_id: str = Field(..., description="The unique identifier for your organization."),
    object_type: Literal["lead", "contact"] = Field(..., description="The type of object to enrich: either 'lead' or 'contact'."),
    object_id: str = Field(..., description="The unique identifier of the lead or contact record to enrich."),
    field_id: str = Field(..., description="The unique identifier of the custom field to enrich."),
    set_new_value: bool | None = Field(None, description="Whether to persist the enriched value to the field. Defaults to true if not specified."),
    overwrite_existing_value: bool | None = Field(None, description="Whether to replace any existing field value with the enriched result. Defaults to false, preserving existing data unless explicitly overwritten."),
) -> dict[str, Any]:
    """Intelligently enrich a specific field on a lead or contact by analyzing existing data and external sources. The operation completes synchronously and optionally updates the field with the enriched value."""

    # Construct request model with validation
    try:
        _request = _models.PostEnrichFieldRequest(
            body=_models.PostEnrichFieldRequestBody(organization_id=organization_id, object_type=object_type, object_id=object_id, field_id=field_id, set_new_value=set_new_value, overwrite_existing_value=overwrite_existing_value)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for enrich_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/enrich_field"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("enrich_field")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("enrich_field", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="enrich_field",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Activities
@mcp.tool()
async def list_custom_activities() -> dict[str, Any]:
    """Retrieve all custom activity types configured for your organization, including their associated custom field metadata."""

    # Extract parameters for API call
    _http_path = "/custom_activity"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_custom_activities")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_custom_activities", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_custom_activities",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Activities
@mcp.tool()
async def create_custom_activity_type(
    name: str = Field(..., description="The display name for this custom activity type. This name identifies the activity type throughout the system."),
    description: str | None = Field(None, description="A detailed explanation of what this custom activity type is used for and its purpose."),
    api_create_only: bool | None = Field(None, description="When enabled, activity instances of this type can only be created through API calls, preventing creation through the user interface."),
    editable_with_roles: list[str] | None = Field(None, description="A list of role identifiers that are permitted to edit activities of this type. If not specified, default role permissions apply."),
    is_archived: bool | None = Field(None, description="When enabled, this activity type is marked as archived and will not appear in active selections, though existing instances remain accessible."),
) -> dict[str, Any]:
    """Create a new custom activity type that serves as a template for activity instances. Custom activity types must be created before you can add custom fields to activities of that type."""

    # Construct request model with validation
    try:
        _request = _models.PostCustomActivityRequest(
            body=_models.PostCustomActivityRequestBody(name=name, description=description, api_create_only=api_create_only, editable_with_roles=editable_with_roles, is_archived=is_archived)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_custom_activity_type: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/custom_activity"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_custom_activity_type")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_custom_activity_type", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_custom_activity_type",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Activities
@mcp.tool()
async def get_custom_activity(id_: str = Field(..., alias="id", description="The unique identifier of the Custom Activity Type to retrieve.")) -> dict[str, Any]:
    """Retrieve a specific Custom Activity Type by its ID, including detailed metadata about associated custom fields."""

    # Construct request model with validation
    try:
        _request = _models.GetCustomActivityIdRequest(
            path=_models.GetCustomActivityIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_custom_activity: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/custom_activity/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/custom_activity/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_custom_activity")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_custom_activity", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_custom_activity",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Activities
@mcp.tool()
async def update_custom_activity(
    id_: str = Field(..., alias="id", description="The unique identifier of the Custom Activity Type to update."),
    name: str | None = Field(None, description="The display name for the custom activity type."),
    description: str | None = Field(None, description="A detailed explanation of the custom activity type's purpose and usage."),
    api_create_only: bool | None = Field(None, description="When enabled, instances of this activity type can only be created through API calls, preventing creation via the user interface."),
    editable_with_roles: list[str] | None = Field(None, description="A list of role identifiers that are permitted to edit instances of this activity type. Roles not included will be unable to modify activities of this type."),
    is_archived: bool | None = Field(None, description="When enabled, this activity type is marked as archived and becomes unavailable for new instance creation."),
    field_order: list[str] | None = Field(None, description="An ordered array of field IDs that determines the display sequence of fields in the user interface. The order specified here controls how fields appear to users."),
) -> dict[str, Any]:
    """Update an existing Custom Activity Type's metadata including name, description, creation restrictions, editor permissions, archive status, and field display order. Field structure changes require the Custom Field API."""

    # Construct request model with validation
    try:
        _request = _models.PutCustomActivityIdRequest(
            path=_models.PutCustomActivityIdRequestPath(id_=id_),
            body=_models.PutCustomActivityIdRequestBody(name=name, description=description, api_create_only=api_create_only, editable_with_roles=editable_with_roles, is_archived=is_archived, field_order=field_order)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_custom_activity: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/custom_activity/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/custom_activity/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_custom_activity")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_custom_activity", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_custom_activity",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Activities
@mcp.tool()
async def delete_custom_activity(id_: str = Field(..., alias="id", description="The unique identifier of the custom activity type to delete.")) -> dict[str, Any]:
    """Permanently delete a custom activity type by its ID. This action cannot be undone and will remove the activity type from your system."""

    # Construct request model with validation
    try:
        _request = _models.DeleteCustomActivityIdRequest(
            path=_models.DeleteCustomActivityIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_custom_activity: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/custom_activity/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/custom_activity/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_custom_activity")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_custom_activity", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_custom_activity",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Activities
@mcp.tool()
async def list_custom_activities_instances(custom_activity_type_id: str | None = Field(None, description="Filter results to a specific custom activity type. When using this filter, the lead_id parameter is required to scope the results appropriately.")) -> dict[str, Any]:
    """Retrieve and filter custom activity instances. Supports filtering by custom activity type, with results including custom fields formatted as custom.{custom_field_id}."""

    # Construct request model with validation
    try:
        _request = _models.GetActivityCustomRequest(
            query=_models.GetActivityCustomRequestQuery(custom_activity_type_id=custom_activity_type_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_custom_activities_instances: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/activity/custom"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_custom_activities_instances")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_custom_activities_instances", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_custom_activities_instances",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Activities
@mcp.tool()
async def create_custom_activity(
    custom_activity_type_id: str = Field(..., description="The unique identifier of the Custom Activity Type to instantiate."),
    lead_id: str = Field(..., description="The unique identifier of the lead to associate with this activity."),
    pinned: bool | None = Field(None, description="Whether to pin this activity for increased visibility. Defaults to unpinned if not specified."),
) -> dict[str, Any]:
    """Create a new Custom Activity instance for a lead. Activities are published by default with all required fields validated, or can be created as drafts to defer validation. Optionally pin the activity for visibility."""

    # Construct request model with validation
    try:
        _request = _models.PostActivityCustomRequest(
            body=_models.PostActivityCustomRequestBody(custom_activity_type_id=custom_activity_type_id, lead_id=lead_id, pinned=pinned)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_custom_activity: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/activity/custom"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_custom_activity")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_custom_activity", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_custom_activity",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Activities
@mcp.tool()
async def get_custom_activity_instance(id_: str = Field(..., alias="id", description="The unique identifier of the Custom Activity instance to retrieve.")) -> dict[str, Any]:
    """Retrieve a specific Custom Activity instance by its unique identifier. Use this to fetch detailed information about a single custom activity."""

    # Construct request model with validation
    try:
        _request = _models.GetActivityCustomIdRequest(
            path=_models.GetActivityCustomIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_custom_activity_instance: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/activity/custom/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/activity/custom/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_custom_activity_instance")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_custom_activity_instance", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_custom_activity_instance",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Activities
@mcp.tool()
async def update_custom_activity_instance(
    id_: str = Field(..., alias="id", description="The unique identifier of the Custom Activity instance to update."),
    pinned: bool | None = Field(None, description="Set to true to pin the activity or false to unpin it. Omit to leave the pinned status unchanged."),
) -> dict[str, Any]:
    """Update an existing Custom Activity instance by modifying custom fields, changing its status between draft and published states, or adjusting its pinned status."""

    # Construct request model with validation
    try:
        _request = _models.PutActivityCustomIdRequest(
            path=_models.PutActivityCustomIdRequestPath(id_=id_),
            body=_models.PutActivityCustomIdRequestBody(pinned=pinned)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_custom_activity_instance: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/activity/custom/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/activity/custom/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_custom_activity_instance")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_custom_activity_instance", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_custom_activity_instance",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Activities
@mcp.tool()
async def delete_custom_activity_instance(id_: str = Field(..., alias="id", description="The unique identifier of the Custom Activity instance to delete.")) -> dict[str, Any]:
    """Permanently delete a Custom Activity instance by its ID. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteActivityCustomIdRequest(
            path=_models.DeleteActivityCustomIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_custom_activity_instance: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/activity/custom/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/activity/custom/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_custom_activity_instance")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_custom_activity_instance", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_custom_activity_instance",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Objects
@mcp.tool()
async def list_custom_object_types() -> dict[str, Any]:
    """Retrieve all Custom Object Types configured in your organization, including their field definitions and back-references from other objects. Each Custom Object Type includes metadata about its own fields and any objects (Leads, Contacts, Opportunities, Custom Activities, or other Custom Objects) that reference it."""

    # Extract parameters for API call
    _http_path = "/custom_object_type"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_custom_object_types")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_custom_object_types", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_custom_object_types",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Objects
@mcp.tool()
async def create_custom_object_type(
    name: str = Field(..., description="The display name of the Custom Object Type. This is used to identify the type throughout the system."),
    name_plural: str = Field(..., description="The plural form of the Custom Object Type name. This is used in UI displays and lists where multiple instances are shown."),
    description: str | None = Field(None, description="An optional longer description that provides additional context or details about the purpose and use of this Custom Object Type."),
    api_create_only: bool | None = Field(None, description="When enabled, instances of this Custom Object Type can only be created through API clients. UI-based creation will be restricted. Defaults to false, allowing creation through all available interfaces."),
    editable_with_roles: list[str] | None = Field(None, description="An optional list of user roles that are permitted to edit instances of this Custom Object Type. If specified, only users with one of these roles can modify instances. If not specified, default role-based permissions apply."),
) -> dict[str, Any]:
    """Create a new Custom Object Type that serves as a blueprint for custom objects in your system. Custom Object Types must be created before you can add custom fields or create instances of that type."""

    # Construct request model with validation
    try:
        _request = _models.PostCustomObjectTypeRequest(
            body=_models.PostCustomObjectTypeRequestBody(name=name, name_plural=name_plural, description=description, api_create_only=api_create_only, editable_with_roles=editable_with_roles)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_custom_object_type: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/custom_object_type"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_custom_object_type")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_custom_object_type", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_custom_object_type",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Objects
@mcp.tool()
async def get_custom_object_type(id_: str = Field(..., alias="id", description="The unique identifier that specifies which Custom Object Type to retrieve.")) -> dict[str, Any]:
    """Retrieve a specific Custom Object Type by its unique identifier, including comprehensive Custom Field metadata associated with it."""

    # Construct request model with validation
    try:
        _request = _models.GetCustomObjectTypeIdRequest(
            path=_models.GetCustomObjectTypeIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_custom_object_type: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/custom_object_type/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/custom_object_type/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_custom_object_type")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_custom_object_type", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_custom_object_type",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Objects
@mcp.tool()
async def update_custom_object_type(
    id_: str = Field(..., alias="id", description="The unique identifier of the Custom Object Type to update."),
    name: str | None = Field(None, description="The display name of the Custom Object Type."),
    name_plural: str | None = Field(None, description="The pluralized form of the Custom Object Type name, used in API responses and UI contexts."),
    description: str | None = Field(None, description="A detailed description explaining the purpose and use of this Custom Object Type."),
    api_create_only: bool | None = Field(None, description="When enabled, only API clients can create new instances of this type; UI-based creation is disabled."),
    editable_with_roles: list[str] | None = Field(None, description="A list of role identifiers whose members are permitted to edit instances of this type. If empty or omitted, all users with general edit permissions can modify instances."),
) -> dict[str, Any]:
    """Update an existing Custom Object Type's metadata including name, description, and access controls. Field structure cannot be modified through this operation."""

    # Construct request model with validation
    try:
        _request = _models.PutCustomObjectTypeIdRequest(
            path=_models.PutCustomObjectTypeIdRequestPath(id_=id_),
            body=_models.PutCustomObjectTypeIdRequestBody(name=name, name_plural=name_plural, description=description, api_create_only=api_create_only, editable_with_roles=editable_with_roles)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_custom_object_type: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/custom_object_type/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/custom_object_type/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_custom_object_type")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_custom_object_type", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_custom_object_type",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Objects
@mcp.tool()
async def delete_custom_object_type(id_: str = Field(..., alias="id", description="The unique identifier of the Custom Object Type to delete.")) -> dict[str, Any]:
    """Permanently delete a Custom Object Type and remove it from your system. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteCustomObjectTypeIdRequest(
            path=_models.DeleteCustomObjectTypeIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_custom_object_type: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/custom_object_type/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/custom_object_type/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_custom_object_type")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_custom_object_type", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_custom_object_type",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Objects
@mcp.tool()
async def list_custom_objects(
    lead_id: str = Field(..., description="The unique identifier of the lead whose Custom Object instances you want to retrieve."),
    custom_object_type_id: str | None = Field(None, description="Optional filter to narrow results to a specific Custom Object Type by its unique identifier."),
) -> dict[str, Any]:
    """Retrieve all Custom Object instances associated with a specific lead, with optional filtering by Custom Object Type. Custom field values are returned using the format custom.{custom_field_id}."""

    # Construct request model with validation
    try:
        _request = _models.GetCustomObjectRequest(
            query=_models.GetCustomObjectRequestQuery(lead_id=lead_id, custom_object_type_id=custom_object_type_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_custom_objects: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/custom_object"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_custom_objects")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_custom_objects", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_custom_objects",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Objects
@mcp.tool()
async def create_custom_object(
    custom_object_type_id: str = Field(..., description="The type identifier for the Custom Object being created, which determines which Custom Fields are available for this instance."),
    lead_id: str = Field(..., description="The Lead identifier that this Custom Object instance will be associated with."),
    name: str = Field(..., description="A display name for this Custom Object instance."),
) -> dict[str, Any]:
    """Create a new Custom Object instance linked to a lead. Custom Field values can be set using the custom.{custom_field_id} format."""

    # Construct request model with validation
    try:
        _request = _models.PostCustomObjectRequest(
            body=_models.PostCustomObjectRequestBody(custom_object_type_id=custom_object_type_id, lead_id=lead_id, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_custom_object: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/custom_object"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_custom_object")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_custom_object", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_custom_object",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Objects
@mcp.tool()
async def get_custom_object(id_: str = Field(..., alias="id", description="The unique identifier of the Custom Object instance to retrieve.")) -> dict[str, Any]:
    """Retrieve a single Custom Object instance by its unique identifier. Returns the complete object data for the specified Custom Object."""

    # Construct request model with validation
    try:
        _request = _models.GetCustomObjectIdRequest(
            path=_models.GetCustomObjectIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_custom_object: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/custom_object/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/custom_object/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_custom_object")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_custom_object", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_custom_object",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Objects
@mcp.tool()
async def update_custom_object(
    id_: str = Field(..., alias="id", description="The unique identifier of the Custom Object instance to update."),
    name: str | None = Field(None, description="The display name for this Custom Object instance."),
) -> dict[str, Any]:
    """Update a Custom Object instance by modifying its custom fields and display name. Use this operation to add, change, or remove custom field values and update the instance's name property."""

    # Construct request model with validation
    try:
        _request = _models.PutCustomObjectIdRequest(
            path=_models.PutCustomObjectIdRequestPath(id_=id_),
            body=_models.PutCustomObjectIdRequestBody(name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_custom_object: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/custom_object/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/custom_object/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_custom_object")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_custom_object", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_custom_object",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Objects
@mcp.tool()
async def delete_custom_object(id_: str = Field(..., alias="id", description="The unique identifier of the Custom Object instance to delete.")) -> dict[str, Any]:
    """Permanently delete a Custom Object instance by its unique identifier. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteCustomObjectIdRequest(
            path=_models.DeleteCustomObjectIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_custom_object: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/custom_object/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/custom_object/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_custom_object")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_custom_object", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_custom_object",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Unsubscribe Email Address
@mcp.tool()
async def list_unsubscribed_emails() -> dict[str, Any]:
    """Retrieve a complete list of email addresses that have been unsubscribed from communications. Use this to manage your unsubscribe list and ensure compliance with user preferences."""

    # Extract parameters for API call
    _http_path = "/unsubscribe/email"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_unsubscribed_emails")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_unsubscribed_emails", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_unsubscribed_emails",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Unsubscribe Email Address
@mcp.tool()
async def unsubscribe_email(email: str = Field(..., description="The email address to unsubscribe from Close's messaging system. Must be a valid email format.")) -> dict[str, Any]:
    """Remove an email address from Close's messaging system. Use this when an email has unsubscribed through external channels (such as a mailing list) and needs to be marked as unsubscribed in Close."""

    # Construct request model with validation
    try:
        _request = _models.PostUnsubscribeEmailRequest(
            body=_models.PostUnsubscribeEmailRequestBody(email=email)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for unsubscribe_email: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/unsubscribe/email"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("unsubscribe_email")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("unsubscribe_email", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="unsubscribe_email",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Unsubscribe Email Address
@mcp.tool()
async def resubscribe_email(email_address: str = Field(..., description="The email address to resubscribe. Must be a valid email format.")) -> dict[str, Any]:
    """Resubscribe an email address to receive messages from Close. Use this operation to restore messaging delivery for an email that was previously unsubscribed."""

    # Construct request model with validation
    try:
        _request = _models.DeleteUnsubscribeEmailEmailAddressRequest(
            path=_models.DeleteUnsubscribeEmailEmailAddressRequestPath(email_address=email_address)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for resubscribe_email: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/unsubscribe/email/{email_address}", _request.path.model_dump(by_alias=True)) if _request.path else "/unsubscribe/email/{email_address}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("resubscribe_email")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("resubscribe_email", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="resubscribe_email",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Advanced Filtering
@mcp.tool()
async def search_contacts_and_leads(
    query_type: Literal["and", "or", "id", "object_type", "text", "has_related", "field_condition"] = Field(..., alias="queryType", description="The type of query to execute: 'and'/'or' for combining multiple conditions, 'id' to search by object ID, 'object_type' to filter by entity type, 'text' for full-text search, 'has_related' to find objects with related entities, or 'field_condition' for attribute-based filtering."),
    field_type: Literal["regular_field", "custom_field"] | None = Field(None, alias="fieldType", description="Specifies whether the field is a standard built-in field or a custom field defined for your organization."),
    condition_type: Literal["boolean", "current_user", "exists", "text", "term", "reference", "number_range"] | None = Field(None, alias="conditionType", description="The type of condition to apply: 'boolean' for true/false values, 'current_user' to reference the authenticated user, 'exists' to check field presence, 'text' for text matching, 'term' for exact value matching, 'reference' for linked objects, or 'number_range' for numeric comparisons."),
    queries: list[dict[str, Any]] | None = Field(None, description="Array of nested query objects used with 'and'/'or' query types to combine multiple filter conditions."),
    query_object_type: Literal["contact", "lead", "contact_phone", "contact_email", "contact_url", "address"] | None = Field(None, alias="queryObject_type", description="The entity type to filter by: 'contact', 'lead', 'contact_phone', 'contact_email', 'contact_url', or 'address'."),
    field_object_type: str | None = Field(None, alias="fieldObject_type", description="The object type that contains the field being filtered on (e.g., 'contact' or 'lead')."),
    value: str | None = Field(None, description="The value to match against for boolean or text-based conditions."),
    mode: Literal["full_words", "phrase"] | None = Field(None, description="Text matching strategy: 'full_words' matches complete words only, 'phrase' matches the exact phrase as entered."),
    this_object_type: str | None = Field(None, description="The primary object type being queried in a 'has_related' query (e.g., 'contact' or 'lead')."),
    related_object_type: str | None = Field(None, description="The related object type to check for existence in a 'has_related' query (e.g., 'contact_email' or 'contact_phone')."),
    related_query: dict[str, Any] | None = Field(None, description="A query object defining conditions that related objects must satisfy in a 'has_related' query."),
    field_name: str | None = Field(None, description="The name of the field to filter on when using 'field_condition' query type."),
    values: list[str] | None = Field(None, description="Array of values to match against for 'term' conditions; returns objects where the field matches any value in the list."),
    reference_type: str | None = Field(None, description="The type of object being referenced in a 'reference' condition (e.g., 'user', 'company')."),
    object_ids: list[str] | None = Field(None, description="Array of object IDs to match against in a 'reference' condition; returns objects linked to any of these IDs."),
    gt: float | None = Field(None, description="Lower bound (exclusive) for numeric range filtering; matches values strictly greater than this number."),
    gte: float | None = Field(None, description="Lower bound (inclusive) for numeric range filtering; matches values greater than or equal to this number."),
    lt: float | None = Field(None, description="Upper bound (exclusive) for numeric range filtering; matches values strictly less than this number."),
    lte: float | None = Field(None, description="Upper bound (inclusive) for numeric range filtering; matches values less than or equal to this number."),
    negate: bool | None = Field(None, description="When enabled, inverts the query logic to return objects that do NOT match the specified conditions."),
    fields: dict[str, Any] | None = Field(None, description="Specify which fields to include in results for each object type. Provide as an object where keys are object type names (e.g., 'contact', 'lead') and values are arrays of field names to return."),
    results_limit: int | None = Field(None, description="Maximum total number of results to return across all pages. Set to 0 with include_counts enabled to retrieve only the result count without fetching records.", ge=0),
    include_counts: bool | None = Field(None, description="When enabled, the response includes a count object showing both the limited count (results returned) and total count (all matching records)."),
    sort: list[_models.PostApiV1DataSearchBodySortItem] | None = Field(None, description="Array of sort specifications to order results. Only numeric, date, and text fields directly on the object can be sorted; specify field name and direction for each sort criterion."),
    limit: int | None = Field(None, description="Number of results to return per page for pagination; must be at least 1.", ge=1),
) -> dict[str, Any]:
    """Search and filter contacts and leads using advanced query logic with support for complex conditions, text search, and related object queries. Returns paginated results with optional field selection and sorting."""

    # Construct request model with validation
    try:
        _request = _models.PostApiV1DataSearchRequest(
            body=_models.PostApiV1DataSearchRequestBody(fields=fields, results_limit=results_limit, include_counts=include_counts, sort=sort, limit=limit,
                query=_models.PostApiV1DataSearchRequestBodyQuery(
                    type_=query_type, queries=queries, object_type=query_object_type, this_object_type=this_object_type, related_object_type=related_object_type, related_query=related_query, negate=negate,
                    field=_models.PostApiV1DataSearchRequestBodyQueryField(type_=field_type, object_type=field_object_type, field_name=field_name) if any(v is not None for v in [field_type, field_object_type, field_name]) else None,
                    condition=_models.PostApiV1DataSearchRequestBodyQueryCondition(type_=condition_type, value=value, mode=mode, values=values, reference_type=reference_type, object_ids=object_ids, gt=gt, gte=gte, lt=lt, lte=lte) if any(v is not None for v in [condition_type, value, mode, values, reference_type, object_ids, gt, gte, lt, lte]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_contacts_and_leads: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/data/search"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_contacts_and_leads")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_contacts_and_leads", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_contacts_and_leads",
        method="POST",
        path=_http_path,
        request_id=_request_id,
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
        print("  python close_api_server.py", file=sys.stderr)
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

    parser = argparse.ArgumentParser(description="Close API MCP Server")

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
    logger.info("Starting Close API MCP Server")
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

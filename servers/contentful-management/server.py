#!/usr/bin/env python3
"""
CMA - Contentful Management API MCP Server
Generated: 2026-04-06 17:14:54 UTC
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
from typing import Any

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

BASE_URL = os.getenv("BASE_URL", "https://api.contentful.com")
SERVER_NAME = "CMA - Contentful Management API"
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

mcp = FastMCP("CMA - Contentful Management API", middleware=[_JsonCoercionMiddleware()])

# Tags: Spaces
@mcp.tool()
async def list_spaces() -> dict[str, Any]:
    """Retrieve all spaces accessible to your account across organizations. Spaces are containers for content types and content; use this to discover available spaces before accessing their content."""

    # Extract parameters for API call
    _http_path = "/spaces"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_spaces")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_spaces", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_spaces",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Spaces
@mcp.tool()
async def create_space(x_contentful_organization: str | None = Field(None, alias="X-Contentful-Organization", description="The ID of the Contentful organization where the space will be created. Required to route the request to the correct organization context.")) -> dict[str, Any]:
    """Create a new space in Contentful by specifying its name and default locale. A space is a container for content types, entries, and assets within your Contentful organization."""

    # Construct request model with validation
    try:
        _request = _models.PostSpacesRequest(
            header=_models.PostSpacesRequestHeader(x_contentful_organization=x_contentful_organization)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_space: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/spaces"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_space")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_space", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_space",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Spaces
@mcp.tool()
async def get_space(space_id: str = Field(..., description="The unique identifier of the space to retrieve. This is a required string that identifies which Contentful space you want to access.")) -> dict[str, Any]:
    """Retrieve detailed information about a specific Contentful space by its ID. This returns the space's configuration, settings, and metadata."""

    # Construct request model with validation
    try:
        _request = _models.GetSpacesBySpaceIdRequest(
            path=_models.GetSpacesBySpaceIdRequestPath(space_id=space_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_space: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_space")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_space", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_space",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Spaces
@mcp.tool()
async def update_space(
    space_id: str = Field(..., description="The unique identifier of the space to update."),
    x_contentful_organization: str | None = Field(None, alias="X-Contentful-Organization", description="Optional organization ID to scope the operation within a specific organization context."),
) -> dict[str, Any]:
    """Update a space's name in your Contentful environment. Requires the current version number to prevent concurrent modification conflicts."""

    # Construct request model with validation
    try:
        _request = _models.PutSpacesRequest(
            path=_models.PutSpacesRequestPath(space_id=space_id),
            header=_models.PutSpacesRequestHeader(x_contentful_organization=x_contentful_organization)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_space: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_space")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_space", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_space",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Spaces
@mcp.tool()
async def delete_space(space_id: str = Field(..., description="The unique identifier of the space to delete.")) -> dict[str, Any]:
    """Permanently delete a space and all its associated content. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteSpacesRequest(
            path=_models.DeleteSpacesRequestPath(space_id=space_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_space: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_space")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_space", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_space",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Enviroments
@mcp.tool()
async def list_environments(space_id: str = Field(..., description="The unique identifier of the Contentful space containing the environments you want to retrieve.")) -> dict[str, Any]:
    """Retrieve all environments within a Contentful space. Environments allow you to manage different versions of your content (e.g., staging, production)."""

    # Construct request model with validation
    try:
        _request = _models.GetSpacesBySpaceIdEnvironmentsRequest(
            path=_models.GetSpacesBySpaceIdEnvironmentsRequestPath(space_id=space_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_environments: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_environments")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_environments", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_environments",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Enviroments
@mcp.tool()
async def create_environment(
    space_id: str = Field(..., description="The unique identifier of the space where the environment will be created."),
    x_contentful_source_environment: str | None = Field(None, alias="X-Contentful-Source-Environment", description="Optional identifier of an existing environment to clone as the source for the new environment's content and structure."),
) -> dict[str, Any]:
    """Create a new environment within a Contentful space. Optionally clone content from an existing source environment."""

    # Construct request model with validation
    try:
        _request = _models.PostSpacesEnvironmentsRequest(
            path=_models.PostSpacesEnvironmentsRequestPath(space_id=space_id),
            header=_models.PostSpacesEnvironmentsRequestHeader(x_contentful_source_environment=x_contentful_source_environment)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_environment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_environment")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_environment", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_environment",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Enviroments
@mcp.tool()
async def get_environment(
    space_id: str = Field(..., description="The unique identifier of the Contentful space containing the environment."),
    environment_id: str = Field(..., description="The unique identifier of the environment to retrieve."),
) -> dict[str, Any]:
    """Retrieve a single environment within a Contentful space. Environments allow you to manage different versions of your content independently."""

    # Construct request model with validation
    try:
        _request = _models.GetSpacesBySpaceIdEnvironmentsByEnvironmentIdRequest(
            path=_models.GetSpacesBySpaceIdEnvironmentsByEnvironmentIdRequestPath(space_id=space_id, environment_id=environment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_environment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_environment")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_environment", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_environment",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Enviroments
@mcp.tool()
async def update_environment(
    space_id: str = Field(..., description="The unique identifier of the Contentful space containing the environment to update."),
    environment_id: str = Field(..., description="The unique identifier of the environment to update."),
) -> dict[str, Any]:
    """Update the configuration and settings of an environment within a Contentful space. This allows you to modify environment properties after creation."""

    # Construct request model with validation
    try:
        _request = _models.PutSpacesEnvironmentsRequest(
            path=_models.PutSpacesEnvironmentsRequestPath(space_id=space_id, environment_id=environment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_environment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_environment")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_environment", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_environment",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Enviroments
@mcp.tool()
async def delete_environment(
    space_id: str = Field(..., description="The unique identifier of the Contentful space containing the environment to delete."),
    environment_id: str = Field(..., description="The unique identifier of the environment to delete. Common examples include 'master' for the default environment."),
) -> dict[str, Any]:
    """Permanently delete an environment within a Contentful space. This action cannot be undone and will remove all content and configuration associated with the environment."""

    # Construct request model with validation
    try:
        _request = _models.DeleteSpacesEnvironmentsRequest(
            path=_models.DeleteSpacesEnvironmentsRequestPath(space_id=space_id, environment_id=environment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_environment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_environment")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_environment", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_environment",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Environment alias
@mcp.tool()
async def list_environment_aliases(space_id: str = Field(..., description="The unique identifier of the space containing the environment aliases you want to retrieve.")) -> dict[str, Any]:
    """Retrieve all environment aliases configured for a specific space in Contentful. Environment aliases allow you to reference environments by custom names in addition to their IDs."""

    # Construct request model with validation
    try:
        _request = _models.GetSpacesBySpaceIdEnvironmentAliasesRequest(
            path=_models.GetSpacesBySpaceIdEnvironmentAliasesRequestPath(space_id=space_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_environment_aliases: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environment_aliases", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environment_aliases"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_environment_aliases")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_environment_aliases", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_environment_aliases",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Environment alias
@mcp.tool()
async def get_environment_alias(
    space_id: str = Field(..., description="The unique identifier of the space containing the environment alias."),
    environment_alias_id: str = Field(..., description="The unique identifier of the environment alias to retrieve."),
) -> dict[str, Any]:
    """Retrieve a specific environment alias within a space. Environment aliases provide alternative identifiers for accessing environments in the Content Management API."""

    # Construct request model with validation
    try:
        _request = _models.GetSpacesBySpaceIdEnvironmentAliasesByEnvironmentAliasIdRequest(
            path=_models.GetSpacesBySpaceIdEnvironmentAliasesByEnvironmentAliasIdRequestPath(space_id=space_id, environment_alias_id=environment_alias_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_environment_alias: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environment_aliases/{environment_alias_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environment_aliases/{environment_alias_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_environment_alias")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_environment_alias", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_environment_alias",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Environment alias
@mcp.tool()
async def create_or_update_environment_alias(
    space_id: str = Field(..., description="The unique identifier of the Contentful space containing the environment alias."),
    environment_alias_id: str = Field(..., description="The unique identifier of the environment alias to create or update."),
) -> dict[str, Any]:
    """Create a new environment alias or update an existing one within a Contentful space. Environment aliases provide stable references to environments that can be updated without changing client configurations."""

    # Construct request model with validation
    try:
        _request = _models.PutSpacesEnvironmentAliasesRequest(
            path=_models.PutSpacesEnvironmentAliasesRequestPath(space_id=space_id, environment_alias_id=environment_alias_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_or_update_environment_alias: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environment_aliases/{environment_alias_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environment_aliases/{environment_alias_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_or_update_environment_alias")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_or_update_environment_alias", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_or_update_environment_alias",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Environment alias
@mcp.tool()
async def delete_environment_alias(
    space_id: str = Field(..., description="The unique identifier of the space containing the environment alias to delete."),
    environment_alias_id: str = Field(..., description="The unique identifier of the environment alias to delete."),
) -> dict[str, Any]:
    """Delete an environment alias from a space. This removes the alias mapping, making it no longer available for accessing the associated environment."""

    # Construct request model with validation
    try:
        _request = _models.DeleteSpacesEnvironmentAliasesRequest(
            path=_models.DeleteSpacesEnvironmentAliasesRequestPath(space_id=space_id, environment_alias_id=environment_alias_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_environment_alias: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environment_aliases/{environment_alias_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environment_aliases/{environment_alias_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_environment_alias")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_environment_alias", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_environment_alias",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Organizations
@mcp.tool()
async def list_organizations() -> dict[str, Any]:
    """Retrieve all organizations that your account has access to. This returns a collection of organizations you can manage or collaborate within."""

    # Extract parameters for API call
    _http_path = "/organizations"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_organizations")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_organizations", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_organizations",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Content Types
@mcp.tool()
async def list_content_types(
    space_id: str = Field(..., description="The unique identifier of the space containing the environment and content types."),
    environment_id: str = Field(..., description="The unique identifier of the environment within the space from which to retrieve content types."),
) -> dict[str, Any]:
    """Retrieve all content types defined for a specific environment within a space. Content types define the structure and fields for entries in Contentful."""

    # Construct request model with validation
    try:
        _request = _models.GetSpacesBySpaceIdEnvironmentsByEnvironmentIdContentTypesRequest(
            path=_models.GetSpacesBySpaceIdEnvironmentsByEnvironmentIdContentTypesRequestPath(space_id=space_id, environment_id=environment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_content_types: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}/content_types", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}/content_types"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_content_types")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_content_types", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_content_types",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Content Types
@mcp.tool()
async def create_content_type(
    space_id: str = Field(..., description="The unique identifier of the space where the content type will be created."),
    environment_id: str = Field(..., description="The unique identifier of the environment within the space where the content type will be created."),
) -> dict[str, Any]:
    """Create a new content type within a specific environment. Content types define the structure and fields for entries in Contentful."""

    # Construct request model with validation
    try:
        _request = _models.PostSpacesEnvironmentsContentTypesRequest(
            path=_models.PostSpacesEnvironmentsContentTypesRequestPath(space_id=space_id, environment_id=environment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_content_type: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}/content_types", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}/content_types"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_content_type")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_content_type", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_content_type",
        method="POST",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Content Types
@mcp.tool()
async def get_content_type(
    space_id: str = Field(..., description="The unique identifier of the space containing the content type. Example format: alphanumeric string like '5nvk6q4s3ttw'."),
    environment_id: str = Field(..., description="The unique identifier of the environment within the space. Typically 'master' for the default environment, but can be any environment name."),
    content_type_id: str = Field(..., description="The unique identifier of the content type to retrieve. Example format: alphanumeric string like 'testValid'."),
) -> dict[str, Any]:
    """Retrieve a single content type definition from a specific environment within a space. Content types define the structure and fields for entries in Contentful."""

    # Construct request model with validation
    try:
        _request = _models.GetSpacesBySpaceIdEnvironmentsByEnvironmentIdContentTypesByContentTypeIdRequest(
            path=_models.GetSpacesBySpaceIdEnvironmentsByEnvironmentIdContentTypesByContentTypeIdRequestPath(space_id=space_id, environment_id=environment_id, content_type_id=content_type_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_content_type: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}/content_types/{content_type_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}/content_types/{content_type_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_content_type")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_content_type", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_content_type",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Content Types
@mcp.tool()
async def create_or_update_content_type(
    space_id: str = Field(..., description="The unique identifier of the space containing the content type."),
    environment_id: str = Field(..., description="The unique identifier of the environment within the space where the content type will be created or updated."),
    content_type_id: str = Field(..., description="The unique identifier for the content type being created or updated."),
) -> dict[str, Any]:
    """Create a new content type or update an existing one within a specific space and environment. This operation allows you to define the structure and fields for content entries."""

    # Construct request model with validation
    try:
        _request = _models.PutSpacesEnvironmentsContentTypesRequest(
            path=_models.PutSpacesEnvironmentsContentTypesRequestPath(space_id=space_id, environment_id=environment_id, content_type_id=content_type_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_or_update_content_type: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}/content_types/{content_type_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}/content_types/{content_type_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_or_update_content_type")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_or_update_content_type", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_or_update_content_type",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Content Types
@mcp.tool()
async def delete_content_type(
    space_id: str = Field(..., description="The unique identifier of the space containing the content type to delete."),
    environment_id: str = Field(..., description="The unique identifier of the environment within the space where the content type is located."),
    content_type_id: str = Field(..., description="The unique identifier of the content type to delete."),
) -> dict[str, Any]:
    """Permanently delete a content type from a specific environment within a space. This action cannot be undone and will remove the content type definition."""

    # Construct request model with validation
    try:
        _request = _models.DeleteSpacesEnvironmentsContentTypesRequest(
            path=_models.DeleteSpacesEnvironmentsContentTypesRequestPath(space_id=space_id, environment_id=environment_id, content_type_id=content_type_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_content_type: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}/content_types/{content_type_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}/content_types/{content_type_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_content_type")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_content_type", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_content_type",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Content Types
@mcp.tool()
async def publish_content_type(
    space_id: str = Field(..., description="The unique identifier of the Contentful space containing the content type."),
    environment_id: str = Field(..., description="The unique identifier of the environment within the space where the content type will be published."),
    content_type_id: str = Field(..., description="The unique identifier of the content type to be published and activated."),
) -> dict[str, Any]:
    """Activate a content type to make it available for use in a Contentful space. Once published, the content type can be used to create and manage content entries."""

    # Construct request model with validation
    try:
        _request = _models.PutSpacesEnvironmentsContentTypesPublishedRequest(
            path=_models.PutSpacesEnvironmentsContentTypesPublishedRequestPath(space_id=space_id, environment_id=environment_id, content_type_id=content_type_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for publish_content_type: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}/content_types/{content_type_id}/published", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}/content_types/{content_type_id}/published"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("publish_content_type")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("publish_content_type", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="publish_content_type",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Content Types
@mcp.tool()
async def deactivate_content_type(
    space_id: str = Field(..., description="The unique identifier of the space containing the content type."),
    environment_id: str = Field(..., description="The unique identifier of the environment where the content type is published."),
    content_type_id: str = Field(..., description="The unique identifier of the content type to deactivate."),
) -> dict[str, Any]:
    """Deactivate a published content type in a specific environment, making it unavailable for use in new content entries."""

    # Construct request model with validation
    try:
        _request = _models.DeleteSpacesEnvironmentsContentTypesPublishedRequest(
            path=_models.DeleteSpacesEnvironmentsContentTypesPublishedRequestPath(space_id=space_id, environment_id=environment_id, content_type_id=content_type_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for deactivate_content_type: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}/content_types/{content_type_id}/published", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}/content_types/{content_type_id}/published"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("deactivate_content_type")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("deactivate_content_type", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="deactivate_content_type",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Content Types
@mcp.tool()
async def list_content_types_published(
    space_id: str = Field(..., description="The unique identifier of the space containing the content types you want to retrieve."),
    environment_id: str = Field(..., description="The unique identifier of the environment within the space from which to fetch activated content types."),
) -> dict[str, Any]:
    """Retrieve all activated content types for a specific space and environment. Content types define the structure and fields available for entries in your space."""

    # Construct request model with validation
    try:
        _request = _models.GetSpacesEnvironmentsPublicContentTypesRequest(
            path=_models.GetSpacesEnvironmentsPublicContentTypesRequestPath(space_id=space_id, environment_id=environment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_content_types_published: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}/public/content_types", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}/public/content_types"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_content_types_published")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_content_types_published", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_content_types_published",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Editor Interface
@mcp.tool()
async def list_editor_interfaces(
    space_id: str = Field(..., description="The unique identifier of the space containing the environment and editor interfaces."),
    environment_id: str = Field(..., description="The unique identifier of the environment within the space for which to retrieve editor interfaces."),
) -> dict[str, Any]:
    """Retrieve all editor interface configurations for a specific environment within a space. Editor interfaces define how content fields are presented and edited in the Contentful UI."""

    # Construct request model with validation
    try:
        _request = _models.GetSpacesEnvironmentsEditorInterfacesRequest(
            path=_models.GetSpacesEnvironmentsEditorInterfacesRequestPath(space_id=space_id, environment_id=environment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_editor_interfaces: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}/editor_interfaces", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}/editor_interfaces"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_editor_interfaces")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_editor_interfaces", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_editor_interfaces",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Editor Interface
@mcp.tool()
async def get_editor_interface(
    space_id: str = Field(..., description="The unique identifier of the space containing the content type."),
    environment_id: str = Field(..., description="The unique identifier of the environment within the space."),
    content_type_id: str = Field(..., description="The unique identifier of the content type for which to retrieve the editor interface configuration."),
) -> dict[str, Any]:
    """Retrieve the editor interface configuration for a specific content type. The editor interface defines how fields are displayed and organized in the Contentful web app."""

    # Construct request model with validation
    try:
        _request = _models.GetSpacesEnvironmentsContentTypesEditorInterfacesRequest(
            path=_models.GetSpacesEnvironmentsContentTypesEditorInterfacesRequestPath(space_id=space_id, environment_id=environment_id, content_type_id=content_type_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_editor_interface: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}/content_types/{content_type_id}/editor_interfaces", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}/content_types/{content_type_id}/editor_interfaces"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_editor_interface")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_editor_interface", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_editor_interface",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Editor Interface
@mcp.tool()
async def update_editor_interface(
    space_id: str = Field(..., description="The unique identifier of the space containing the content type whose editor interface you want to update."),
    environment_id: str = Field(..., description="The unique identifier of the environment within the space where the editor interface configuration will be updated."),
    content_type_id: str = Field(..., description="The unique identifier of the content type whose editor interface you want to modify."),
) -> dict[str, Any]:
    """Update the editor interface configuration for a specific content type, controlling how fields are displayed and organized in the Contentful editor UI."""

    # Construct request model with validation
    try:
        _request = _models.PutSpacesEnvironmentsContentTypesEditorInterfacesRequest(
            path=_models.PutSpacesEnvironmentsContentTypesEditorInterfacesRequestPath(space_id=space_id, environment_id=environment_id, content_type_id=content_type_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_editor_interface: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}/content_types/{content_type_id}/editor_interfaces", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}/content_types/{content_type_id}/editor_interfaces"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_editor_interface")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_editor_interface", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_editor_interface",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: UI Extensions
@mcp.tool()
async def list_extensions(
    space_id: str = Field(..., description="The unique identifier of the space containing the environment and extensions."),
    environment_id: str = Field(..., description="The unique identifier of the environment from which to retrieve extensions."),
) -> dict[str, Any]:
    """Retrieve all UI extensions configured for a specific environment within a space. Extensions allow customization of the Contentful UI for content editors."""

    # Construct request model with validation
    try:
        _request = _models.GetSpacesBySpaceIdEnvironmentsByEnvironmentIdExtensionsRequest(
            path=_models.GetSpacesBySpaceIdEnvironmentsByEnvironmentIdExtensionsRequestPath(space_id=space_id, environment_id=environment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_extensions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}/extensions", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}/extensions"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_extensions")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_extensions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_extensions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: UI Extensions
@mcp.tool()
async def create_extension(
    space_id: str = Field(..., description="The unique identifier of the space where the extension will be created."),
    environment_id: str = Field(..., description="The unique identifier of the environment within the space where the extension will be created."),
) -> dict[str, Any]:
    """Create a new UI extension within a specific environment. Extensions allow you to customize the Contentful editor interface with custom widgets and tools."""

    # Construct request model with validation
    try:
        _request = _models.PostSpacesEnvironmentsExtensionsRequest(
            path=_models.PostSpacesEnvironmentsExtensionsRequestPath(space_id=space_id, environment_id=environment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_extension: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}/extensions", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}/extensions"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_extension")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_extension", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_extension",
        method="POST",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: UI Extensions
@mcp.tool()
async def get_extension(
    space_id: str = Field(..., description="The unique identifier of the space containing the extension."),
    environment_id: str = Field(..., description="The unique identifier of the environment within the space where the extension is configured."),
    extension_id: str = Field(..., description="The unique identifier of the extension to retrieve."),
) -> dict[str, Any]:
    """Retrieve a single UI extension configuration from a specific environment within a space. This returns the extension's definition and settings."""

    # Construct request model with validation
    try:
        _request = _models.GetSpacesBySpaceIdEnvironmentsByEnvironmentIdExtensionsByExtensionIdRequest(
            path=_models.GetSpacesBySpaceIdEnvironmentsByEnvironmentIdExtensionsByExtensionIdRequestPath(space_id=space_id, environment_id=environment_id, extension_id=extension_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_extension: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}/extensions/{extension_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}/extensions/{extension_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_extension")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_extension", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_extension",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: UI Extensions
@mcp.tool()
async def create_or_update_extension(
    space_id: str = Field(..., description="The unique identifier of the Contentful space where the extension will be created or updated."),
    environment_id: str = Field(..., description="The unique identifier of the environment within the space where the extension will be created or updated."),
    extension_id: str = Field(..., description="The unique identifier for the extension being created or updated."),
) -> dict[str, Any]:
    """Create a new UI extension or update an existing one in a Contentful space environment. This operation allows you to define custom UI components for the Contentful editor."""

    # Construct request model with validation
    try:
        _request = _models.PutSpacesEnvironmentsExtensionsRequest(
            path=_models.PutSpacesEnvironmentsExtensionsRequestPath(space_id=space_id, environment_id=environment_id, extension_id=extension_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_or_update_extension: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}/extensions/{extension_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}/extensions/{extension_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_or_update_extension")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_or_update_extension", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_or_update_extension",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: UI Extensions
@mcp.tool()
async def delete_extension(
    space_id: str = Field(..., description="The unique identifier of the space containing the extension to delete."),
    environment_id: str = Field(..., description="The unique identifier of the environment within the space where the extension is located."),
    extension_id: str = Field(..., description="The unique identifier of the extension to delete."),
) -> dict[str, Any]:
    """Permanently delete a UI extension from a specific environment within a space. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteSpacesEnvironmentsExtensionsRequest(
            path=_models.DeleteSpacesEnvironmentsExtensionsRequestPath(space_id=space_id, environment_id=environment_id, extension_id=extension_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_extension: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}/extensions/{extension_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}/extensions/{extension_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_extension")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_extension", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_extension",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Entries collection
@mcp.tool()
async def list_entries(
    space_id: str = Field(..., description="The unique identifier of the space containing the entries to retrieve."),
    environment_id: str = Field(..., description="The unique identifier of the environment within the space from which to fetch entries."),
    tag_key: str | None = Field(None, alias="TAG_KEY", description="Optional tag key to filter entries by a specific tag value. Use this to retrieve only entries associated with a particular tag."),
) -> dict[str, Any]:
    """Retrieve all entries from a specific environment within a space. Entries represent content items managed in Contentful and can be filtered by tags."""

    # Construct request model with validation
    try:
        _request = _models.GetSpacesBySpaceIdEnvironmentsByEnvironmentIdEntriesRequest(
            path=_models.GetSpacesBySpaceIdEnvironmentsByEnvironmentIdEntriesRequestPath(space_id=space_id, environment_id=environment_id),
            query=_models.GetSpacesBySpaceIdEnvironmentsByEnvironmentIdEntriesRequestQuery(tag_key=tag_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_entries: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}/entries", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}/entries"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_entries")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_entries", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_entries",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Entries collection
@mcp.tool()
async def create_entry(
    space_id: str = Field(..., description="The unique identifier of the Contentful space where the entry will be created."),
    environment_id: str = Field(..., description="The environment within the space where the entry will be created. Defaults to 'master' for the main environment."),
    x_contentful_content_type: str | None = Field(None, alias="X-Contentful-Content-Type", description="The content type ID that defines the structure and fields for this entry. This determines what fields are available and required for the entry."),
) -> dict[str, Any]:
    """Create a new entry in a Contentful space environment. Entries are the primary content objects that hold your data according to a defined content model."""

    # Construct request model with validation
    try:
        _request = _models.PostSpacesEnvironmentsEntriesRequest(
            path=_models.PostSpacesEnvironmentsEntriesRequestPath(space_id=space_id, environment_id=environment_id),
            header=_models.PostSpacesEnvironmentsEntriesRequestHeader(x_contentful_content_type=x_contentful_content_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_entry: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}/entries", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}/entries"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_entry")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_entry", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_entry",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Entry
@mcp.tool()
async def get_entry(
    space_id: str = Field(..., description="The unique identifier of the Contentful space (e.g., '5nvk6q4s3ttw'). This identifies which space contains the entry."),
    environment_id: str = Field(..., description="The environment identifier within the space, typically 'master' for the main environment. Specifies which environment version of the entry to retrieve."),
    entry_id: str = Field(..., description="The unique identifier of the entry to retrieve (e.g., '4Mxj1aVYccLOCunUzsNcNL'). This identifies the specific entry within the environment."),
) -> dict[str, Any]:
    """Retrieve a single entry from a Contentful space and environment. Returns the complete entry object with all its fields and metadata."""

    # Construct request model with validation
    try:
        _request = _models.GetSpacesBySpaceIdEnvironmentsByEnvironmentIdEntriesByEntryIdRequest(
            path=_models.GetSpacesBySpaceIdEnvironmentsByEnvironmentIdEntriesByEntryIdRequestPath(space_id=space_id, environment_id=environment_id, entry_id=entry_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_entry: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}/entries/{entry_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}/entries/{entry_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_entry")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_entry", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_entry",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Entry
@mcp.tool()
async def upsert_entry(
    space_id: str = Field(..., description="The unique identifier of the space containing the entry. This is the workspace where your content is organized."),
    environment_id: str = Field(..., description="The unique identifier of the environment within the space. Environments allow you to manage different versions of your content (e.g., draft, published)."),
    entry_id: str = Field(..., description="The unique identifier of the entry to create or update. If the entry doesn't exist, it will be created; otherwise, the existing entry will be updated."),
    x_contentful_content_type: str | None = Field(None, alias="X-Contentful-Content-Type", description="The content type ID that defines the structure and fields for this entry. This determines what fields are available and their validation rules."),
) -> dict[str, Any]:
    """Create a new entry or update an existing entry within a specific environment and space. This operation allows you to define or modify content entries in your Contentful workspace."""

    # Construct request model with validation
    try:
        _request = _models.PutSpacesEnvironmentsEntriesRequest(
            path=_models.PutSpacesEnvironmentsEntriesRequestPath(space_id=space_id, environment_id=environment_id, entry_id=entry_id),
            header=_models.PutSpacesEnvironmentsEntriesRequestHeader(x_contentful_content_type=x_contentful_content_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for upsert_entry: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}/entries/{entry_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}/entries/{entry_id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("upsert_entry")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("upsert_entry", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="upsert_entry",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Entry
@mcp.tool()
async def update_entry(
    space_id: str = Field(..., description="The unique identifier of the Contentful space containing the entry to update."),
    environment_id: str = Field(..., description="The environment identifier where the entry resides. Typically 'master' for the default environment."),
    entry_id: str = Field(..., description="The unique identifier of the entry to update."),
    x_contentful_content_type: str | None = Field(None, alias="X-Contentful-Content-Type", description="The content type ID that defines the structure of the entry being updated."),
) -> dict[str, Any]:
    """Partially update an entry within a Contentful space and environment. Use this operation to modify specific fields of an existing entry without replacing the entire entry."""

    # Construct request model with validation
    try:
        _request = _models.PatchSpacesEnvironmentsEntriesRequest(
            path=_models.PatchSpacesEnvironmentsEntriesRequestPath(space_id=space_id, environment_id=environment_id, entry_id=entry_id),
            header=_models.PatchSpacesEnvironmentsEntriesRequestHeader(x_contentful_content_type=x_contentful_content_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_entry: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}/entries/{entry_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}/entries/{entry_id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_entry")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_entry", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_entry",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Entry
@mcp.tool()
async def delete_entry(
    space_id: str = Field(..., description="The unique identifier of the Contentful space containing the entry to delete."),
    environment_id: str = Field(..., description="The environment within the space where the entry exists. Typically 'master' for the main environment."),
    entry_id: str = Field(..., description="The unique identifier of the entry to delete."),
) -> dict[str, Any]:
    """Permanently delete an entry from a Contentful space environment. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteSpacesEnvironmentsEntriesRequest(
            path=_models.DeleteSpacesEnvironmentsEntriesRequestPath(space_id=space_id, environment_id=environment_id, entry_id=entry_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_entry: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}/entries/{entry_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}/entries/{entry_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_entry")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_entry", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_entry",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Entry references
@mcp.tool()
async def list_entry_references(
    space_id: str = Field(..., description="The unique identifier of the Contentful space containing the entry (e.g., '5nvk6q4s3ttw')."),
    environment_id: str = Field(..., description="The environment identifier within the space, typically 'master' for the default environment."),
    entry_id: str = Field(..., description="The unique identifier of the entry for which to retrieve references (e.g., '4Mxj1aVYccLOCunUzsNcNL')."),
) -> dict[str, Any]:
    """Retrieve all entries that reference a specific entry within a Contentful space and environment. This helps identify content dependencies and relationships."""

    # Construct request model with validation
    try:
        _request = _models.GetSpacesEnvironmentsEntriesReferencesRequest(
            path=_models.GetSpacesEnvironmentsEntriesReferencesRequestPath(space_id=space_id, environment_id=environment_id, entry_id=entry_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_entry_references: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}/entries/{entry_id}/references", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}/entries/{entry_id}/references"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_entry_references")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_entry_references", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_entry_references",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Entry publishing
@mcp.tool()
async def publish_entry(
    space_id: str = Field(..., description="The unique identifier of the space containing the entry to publish."),
    environment_id: str = Field(..., description="The environment where the entry will be published. Typically 'master' for the main environment."),
    entry_id: str = Field(..., description="The unique identifier of the entry to publish."),
) -> dict[str, Any]:
    """Publish an entry to make it publicly available. This operation marks the entry as published in the specified environment."""

    # Construct request model with validation
    try:
        _request = _models.PutSpacesEnvironmentsEntriesPublishedRequest(
            path=_models.PutSpacesEnvironmentsEntriesPublishedRequestPath(space_id=space_id, environment_id=environment_id, entry_id=entry_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for publish_entry: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}/entries/{entry_id}/published", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}/entries/{entry_id}/published"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("publish_entry")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("publish_entry", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="publish_entry",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Entry publishing
@mcp.tool()
async def unpublish_entry(
    space_id: str = Field(..., description="The unique identifier of the space containing the entry to unpublish."),
    environment_id: str = Field(..., description="The environment identifier where the entry exists. Typically 'master' for the default environment."),
    entry_id: str = Field(..., description="The unique identifier of the entry to unpublish."),
) -> dict[str, Any]:
    """Unpublish an entry, removing it from the published state while keeping the draft version intact. This operation reverses a previous publish action."""

    # Construct request model with validation
    try:
        _request = _models.DeleteSpacesEnvironmentsEntriesPublishedRequest(
            path=_models.DeleteSpacesEnvironmentsEntriesPublishedRequestPath(space_id=space_id, environment_id=environment_id, entry_id=entry_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for unpublish_entry: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}/entries/{entry_id}/published", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}/entries/{entry_id}/published"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("unpublish_entry")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("unpublish_entry", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="unpublish_entry",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Entry archiving
@mcp.tool()
async def archive_entry(
    space_id: str = Field(..., description="The unique identifier of the Contentful space containing the entry to archive."),
    environment_id: str = Field(..., description="The environment identifier where the entry resides. Typically 'master' for the default environment."),
    entry_id: str = Field(..., description="The unique identifier of the entry to archive."),
) -> dict[str, Any]:
    """Archive an entry in a Contentful space environment. Archived entries are hidden from published content but retained for historical reference."""

    # Construct request model with validation
    try:
        _request = _models.PutSpacesEnvironmentsEntriesArchivedRequest(
            path=_models.PutSpacesEnvironmentsEntriesArchivedRequestPath(space_id=space_id, environment_id=environment_id, entry_id=entry_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for archive_entry: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}/entries/{entry_id}/archived", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}/entries/{entry_id}/archived"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("archive_entry")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("archive_entry", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="archive_entry",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Entry archiving
@mcp.tool()
async def unarchive_entry(
    space_id: str = Field(..., description="The unique identifier of the Contentful space containing the entry."),
    environment_id: str = Field(..., description="The environment identifier where the entry is stored. Typically 'master' for the default environment."),
    entry_id: str = Field(..., description="The unique identifier of the entry to unarchive."),
) -> dict[str, Any]:
    """Restore an archived entry to active status in a Contentful space. This operation reverses the archival of an entry, making it available for use again."""

    # Construct request model with validation
    try:
        _request = _models.DeleteSpacesEnvironmentsEntriesArchivedRequest(
            path=_models.DeleteSpacesEnvironmentsEntriesArchivedRequestPath(space_id=space_id, environment_id=environment_id, entry_id=entry_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for unarchive_entry: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}/entries/{entry_id}/archived", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}/entries/{entry_id}/archived"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("unarchive_entry")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("unarchive_entry", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="unarchive_entry",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Uploads
@mcp.tool()
async def upload_file(space_id: str = Field(..., description="The unique identifier of the space where the file will be uploaded.")) -> dict[str, Any]:
    """Upload a file to a Contentful space. The uploaded file can then be used as an asset within the space."""

    # Construct request model with validation
    try:
        _request = _models.PostSpacesUploadsRequest(
            path=_models.PostSpacesUploadsRequestPath(space_id=space_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for upload_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/uploads", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/uploads"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("upload_file")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("upload_file", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="upload_file",
        method="POST",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Uploads
@mcp.tool()
async def get_upload(
    space_id: str = Field(..., description="The unique identifier of the space containing the upload."),
    upload_id: str = Field(..., description="The unique identifier of the upload to retrieve."),
) -> dict[str, Any]:
    """Retrieve details about a specific upload in a space. Use this to check the status and metadata of a previously created upload."""

    # Construct request model with validation
    try:
        _request = _models.GetSpacesUploadsRequest(
            path=_models.GetSpacesUploadsRequestPath(space_id=space_id, upload_id=upload_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_upload: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/uploads/{upload_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/uploads/{upload_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_upload")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_upload", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_upload",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Uploads
@mcp.tool()
async def delete_upload(
    space_id: str = Field(..., description="The unique identifier of the space containing the upload to delete."),
    upload_id: str = Field(..., description="The unique identifier of the upload to delete."),
) -> dict[str, Any]:
    """Permanently delete an upload from a Contentful space. Once deleted, the upload cannot be recovered."""

    # Construct request model with validation
    try:
        _request = _models.DeleteSpacesUploadsRequest(
            path=_models.DeleteSpacesUploadsRequestPath(space_id=space_id, upload_id=upload_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_upload: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/uploads/{upload_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/uploads/{upload_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_upload")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_upload", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_upload",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Assets
@mcp.tool()
async def list_assets(
    space_id: str = Field(..., description="The unique identifier of the space containing the assets you want to retrieve."),
    environment_id: str = Field(..., description="The unique identifier of the environment within the space from which to fetch assets."),
) -> dict[str, Any]:
    """Retrieve all assets in a specific environment within a space. Assets are media files and other resources managed in Contentful."""

    # Construct request model with validation
    try:
        _request = _models.GetSpacesBySpaceIdEnvironmentsByEnvironmentIdAssetsRequest(
            path=_models.GetSpacesBySpaceIdEnvironmentsByEnvironmentIdAssetsRequestPath(space_id=space_id, environment_id=environment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_assets: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}/assets", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}/assets"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_assets")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_assets", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_assets",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Assets
@mcp.tool()
async def create_asset(
    space_id: str = Field(..., description="The unique identifier of the Contentful space where the asset will be created."),
    environment_id: str = Field(..., description="The unique identifier of the environment within the space where the asset will be created."),
) -> dict[str, Any]:
    """Create a new asset in a specified Contentful space and environment. Assets are files and media that can be referenced by content entries."""

    # Construct request model with validation
    try:
        _request = _models.PostSpacesEnvironmentsAssetsRequest(
            path=_models.PostSpacesEnvironmentsAssetsRequestPath(space_id=space_id, environment_id=environment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_asset: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}/assets", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}/assets"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_asset")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_asset", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_asset",
        method="POST",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Assets
@mcp.tool()
async def list_published_assets(
    space_id: str = Field(..., description="The unique identifier of the space containing the assets."),
    environment_id: str = Field(..., description="The unique identifier of the environment within the space from which to retrieve published assets."),
) -> dict[str, Any]:
    """Retrieve all published assets for a specific space and environment. This returns assets that have been explicitly published and are available for use."""

    # Construct request model with validation
    try:
        _request = _models.GetSpacesEnvironmentsPublicAssetsRequest(
            path=_models.GetSpacesEnvironmentsPublicAssetsRequestPath(space_id=space_id, environment_id=environment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_published_assets: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}/public/assets", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}/public/assets"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_published_assets")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_published_assets", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_published_assets",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Assets
@mcp.tool()
async def get_asset(
    space_id: str = Field(..., description="The unique identifier of the space containing the asset."),
    environment_id: str = Field(..., description="The unique identifier of the environment within the space where the asset is located."),
    asset_id: str = Field(..., description="The unique identifier of the asset to retrieve (e.g., B1fZbskHLWGKIVuZySN5P)."),
) -> dict[str, Any]:
    """Retrieve a single asset from a specific environment within a space. Assets are media files and other resources managed in Contentful."""

    # Construct request model with validation
    try:
        _request = _models.GetSpacesBySpaceIdEnvironmentsByEnvironmentIdAssetsByAssetIdRequest(
            path=_models.GetSpacesBySpaceIdEnvironmentsByEnvironmentIdAssetsByAssetIdRequestPath(space_id=space_id, environment_id=environment_id, asset_id=asset_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_asset: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}/assets/{asset_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}/assets/{asset_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_asset")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_asset", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_asset",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Assets
@mcp.tool()
async def create_or_update_asset(
    space_id: str = Field(..., description="The unique identifier of the Contentful space containing the asset."),
    environment_id: str = Field(..., description="The unique identifier of the environment within the space where the asset is located."),
    asset_id: str = Field(..., description="The unique identifier of the asset to create or update. If the asset does not exist, it will be created with this ID."),
) -> dict[str, Any]:
    """Create a new asset or update an existing asset in a Contentful space environment. Use this operation to manage media files and other assets within your content management system."""

    # Construct request model with validation
    try:
        _request = _models.PutSpacesEnvironmentsAssetsRequest(
            path=_models.PutSpacesEnvironmentsAssetsRequestPath(space_id=space_id, environment_id=environment_id, asset_id=asset_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_or_update_asset: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}/assets/{asset_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}/assets/{asset_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_or_update_asset")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_or_update_asset", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_or_update_asset",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Assets
@mcp.tool()
async def delete_asset(
    space_id: str = Field(..., description="The unique identifier of the space containing the asset to delete."),
    environment_id: str = Field(..., description="The unique identifier of the environment within the space where the asset is located."),
    asset_id: str = Field(..., description="The unique identifier of the asset to delete."),
) -> dict[str, Any]:
    """Permanently delete an asset from a specific environment within a space. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteSpacesEnvironmentsAssetsRequest(
            path=_models.DeleteSpacesEnvironmentsAssetsRequestPath(space_id=space_id, environment_id=environment_id, asset_id=asset_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_asset: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}/assets/{asset_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}/assets/{asset_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_asset")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_asset", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_asset",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Assets
@mcp.tool()
async def process_asset_file(
    space_id: str = Field(..., description="The unique identifier of the Contentful space containing the asset."),
    environment_id: str = Field(..., description="The unique identifier of the environment within the space where the asset is located."),
    asset_id: str = Field(..., description="The unique identifier of the asset file to process."),
    locale_code: str = Field(..., description="The locale code for the asset file variant to process, specified in language-region format (e.g., en-us for US English)."),
) -> dict[str, Any]:
    """Trigger processing of an asset file in a specific locale within a Contentful space and environment. This initiates any necessary transformations or optimizations for the uploaded asset."""

    # Construct request model with validation
    try:
        _request = _models.PutSpacesEnvironmentsAssetsFilesProcessRequest(
            path=_models.PutSpacesEnvironmentsAssetsFilesProcessRequestPath(space_id=space_id, environment_id=environment_id, asset_id=asset_id, locale_code=locale_code)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for process_asset_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}/assets/{asset_id}/files/{locale_code}/process", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}/assets/{asset_id}/files/{locale_code}/process"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("process_asset_file")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("process_asset_file", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="process_asset_file",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Assets
@mcp.tool()
async def publish_asset(
    space_id: str = Field(..., description="The unique identifier of the space containing the asset to publish."),
    environment_id: str = Field(..., description="The unique identifier of the environment where the asset will be published."),
    asset_id: str = Field(..., description="The unique identifier of the asset to publish."),
) -> dict[str, Any]:
    """Publish an asset to make it available in the specified environment. Publishing an asset marks it as ready for use in your content delivery pipeline."""

    # Construct request model with validation
    try:
        _request = _models.PutSpacesEnvironmentsAssetsPublishedRequest(
            path=_models.PutSpacesEnvironmentsAssetsPublishedRequestPath(space_id=space_id, environment_id=environment_id, asset_id=asset_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for publish_asset: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}/assets/{asset_id}/published", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}/assets/{asset_id}/published"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("publish_asset")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("publish_asset", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="publish_asset",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Assets
@mcp.tool()
async def unpublish_asset(
    space_id: str = Field(..., description="The unique identifier of the space containing the asset."),
    environment_id: str = Field(..., description="The unique identifier of the environment from which to unpublish the asset."),
    asset_id: str = Field(..., description="The unique identifier of the asset to unpublish."),
) -> dict[str, Any]:
    """Unpublish an asset from a specific environment, making it unavailable to content consumers while retaining the asset in the space."""

    # Construct request model with validation
    try:
        _request = _models.DeleteSpacesEnvironmentsAssetsPublishedRequest(
            path=_models.DeleteSpacesEnvironmentsAssetsPublishedRequestPath(space_id=space_id, environment_id=environment_id, asset_id=asset_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for unpublish_asset: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}/assets/{asset_id}/published", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}/assets/{asset_id}/published"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("unpublish_asset")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("unpublish_asset", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="unpublish_asset",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Assets
@mcp.tool()
async def archive_asset(
    space_id: str = Field(..., description="The unique identifier of the Contentful space containing the asset."),
    environment_id: str = Field(..., description="The unique identifier of the environment within the space where the asset is located."),
    asset_id: str = Field(..., description="The unique identifier of the asset to archive."),
) -> dict[str, Any]:
    """Archive an asset in a Contentful space environment. Archived assets are hidden from delivery but retained for historical purposes."""

    # Construct request model with validation
    try:
        _request = _models.PutSpacesEnvironmentsAssetsArchivedRequest(
            path=_models.PutSpacesEnvironmentsAssetsArchivedRequestPath(space_id=space_id, environment_id=environment_id, asset_id=asset_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for archive_asset: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}/assets/{asset_id}/archived", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}/assets/{asset_id}/archived"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("archive_asset")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("archive_asset", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="archive_asset",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Assets
@mcp.tool()
async def unarchive_asset(
    space_id: str = Field(..., description="The unique identifier of the space containing the asset."),
    environment_id: str = Field(..., description="The unique identifier of the environment within the space where the asset is located."),
    asset_id: str = Field(..., description="The unique identifier of the asset to unarchive."),
) -> dict[str, Any]:
    """Restore an archived asset in a specific environment, making it available for use again. This operation removes the archived status from the asset."""

    # Construct request model with validation
    try:
        _request = _models.DeleteSpacesEnvironmentsAssetsArchivedRequest(
            path=_models.DeleteSpacesEnvironmentsAssetsArchivedRequestPath(space_id=space_id, environment_id=environment_id, asset_id=asset_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for unarchive_asset: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}/assets/{asset_id}/archived", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}/assets/{asset_id}/archived"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("unarchive_asset")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("unarchive_asset", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="unarchive_asset",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Assets keys
@mcp.tool()
async def create_asset_key(
    space_id: str = Field(..., description="The unique identifier of the space where the asset key will be created."),
    environment_id: str = Field(..., description="The unique identifier of the environment within the space where the asset key will be created."),
) -> dict[str, Any]:
    """Create a new asset key within a specific environment. Asset keys are used to manage and organize digital assets in your content space."""

    # Construct request model with validation
    try:
        _request = _models.PostSpacesEnvironmentsAssetKeysRequest(
            path=_models.PostSpacesEnvironmentsAssetKeysRequestPath(space_id=space_id, environment_id=environment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_asset_key: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}/asset_keys", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}/asset_keys"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_asset_key")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_asset_key", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_asset_key",
        method="POST",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Locale
@mcp.tool()
async def list_locales(
    space_id: str = Field(..., description="The unique identifier of the space containing the environment and locales to retrieve."),
    environment_id: str = Field(..., description="The unique identifier of the environment within the space from which to fetch locales."),
) -> dict[str, Any]:
    """Retrieve all locales configured for a specific environment within a space. Locales define the languages and regional variants available for content in that environment."""

    # Construct request model with validation
    try:
        _request = _models.GetSpacesBySpaceIdEnvironmentsByEnvironmentIdLocalesRequest(
            path=_models.GetSpacesBySpaceIdEnvironmentsByEnvironmentIdLocalesRequestPath(space_id=space_id, environment_id=environment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_locales: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}/locales", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}/locales"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_locales")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_locales", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_locales",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Locale
@mcp.tool()
async def create_locale(
    space_id: str = Field(..., description="The unique identifier of the Contentful space where the locale will be created (e.g., 'r0926rqjrebl')."),
    environment_id: str = Field(..., description="The environment identifier within the space where the locale will be added (e.g., 'master' for the default environment)."),
) -> dict[str, Any]:
    """Create a new locale within a specific environment of a Contentful space. Locales define the languages and regional variants available for content in your space."""

    # Construct request model with validation
    try:
        _request = _models.PostSpacesEnvironmentsLocalesRequest(
            path=_models.PostSpacesEnvironmentsLocalesRequestPath(space_id=space_id, environment_id=environment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_locale: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}/locales", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}/locales"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_locale")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_locale", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_locale",
        method="POST",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Locale
@mcp.tool()
async def get_locale(
    space_id: str = Field(..., description="The unique identifier of the space containing the locale."),
    environment_id: str = Field(..., description="The unique identifier of the environment within the space."),
    locale_id: str = Field(..., description="The unique identifier of the locale to retrieve."),
) -> dict[str, Any]:
    """Retrieve a specific locale configuration for a given space and environment. Locales define language and regional settings for content management."""

    # Construct request model with validation
    try:
        _request = _models.GetSpacesBySpaceIdEnvironmentsByEnvironmentIdLocalesByLocaleIdRequest(
            path=_models.GetSpacesBySpaceIdEnvironmentsByEnvironmentIdLocalesByLocaleIdRequestPath(space_id=space_id, environment_id=environment_id, locale_id=locale_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_locale: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}/locales/{locale_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}/locales/{locale_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_locale")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_locale", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_locale",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Locale
@mcp.tool()
async def update_locale(
    space_id: str = Field(..., description="The unique identifier of the space containing the locale to update."),
    environment_id: str = Field(..., description="The unique identifier of the environment within the space where the locale resides."),
    locale_id: str = Field(..., description="The unique identifier of the locale to update."),
) -> dict[str, Any]:
    """Update the configuration of a specific locale within a Contentful environment, such as display name or other locale settings."""

    # Construct request model with validation
    try:
        _request = _models.PutSpacesEnvironmentsLocalesRequest(
            path=_models.PutSpacesEnvironmentsLocalesRequestPath(space_id=space_id, environment_id=environment_id, locale_id=locale_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_locale: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}/locales/{locale_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}/locales/{locale_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_locale")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_locale", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_locale",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Locale
@mcp.tool()
async def delete_locale(
    space_id: str = Field(..., description="The unique identifier of the space containing the locale to delete."),
    environment_id: str = Field(..., description="The unique identifier of the environment within the space where the locale exists."),
    locale_id: str = Field(..., description="The unique identifier of the locale to delete."),
) -> dict[str, Any]:
    """Permanently delete a locale from a specific environment within a space. This action removes the locale configuration and cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteSpacesEnvironmentsLocalesRequest(
            path=_models.DeleteSpacesEnvironmentsLocalesRequestPath(space_id=space_id, environment_id=environment_id, locale_id=locale_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_locale: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}/locales/{locale_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}/locales/{locale_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_locale")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_locale", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_locale",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Content tags
@mcp.tool()
async def list_environment_tags(
    space_id: str = Field(..., description="The unique identifier of the space containing the environment. This is required to scope the request to the correct workspace."),
    environment_id: str = Field(..., description="The unique identifier of the environment within the space. This specifies which environment's tags should be retrieved."),
) -> dict[str, Any]:
    """Retrieve all tags configured for a specific environment within a space. Tags are used to organize and categorize content management UI extensions."""

    # Construct request model with validation
    try:
        _request = _models.GetSpacesBySpaceIdEnvironmentsByEnvironmentIdTagsRequest(
            path=_models.GetSpacesBySpaceIdEnvironmentsByEnvironmentIdTagsRequestPath(space_id=space_id, environment_id=environment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_environment_tags: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}/tags", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}/tags"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_environment_tags")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_environment_tags", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_environment_tags",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Content tags
@mcp.tool()
async def get_tag(
    space_id: str = Field(..., description="The unique identifier of the space containing the tag."),
    environment_id: str = Field(..., description="The unique identifier of the environment within the space where the tag is located."),
    tag_id: str = Field(..., description="The unique identifier of the tag to retrieve."),
) -> dict[str, Any]:
    """Retrieve a single tag from a specific environment within a space. Tags are used to organize and categorize content in Contentful."""

    # Construct request model with validation
    try:
        _request = _models.GetSpacesBySpaceIdEnvironmentsByEnvironmentIdTagsByTagIdRequest(
            path=_models.GetSpacesBySpaceIdEnvironmentsByEnvironmentIdTagsByTagIdRequestPath(space_id=space_id, environment_id=environment_id, tag_id=tag_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_tag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}/tags/{tag_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}/tags/{tag_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_tag")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_tag", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_tag",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Content tags
@mcp.tool()
async def create_tag(
    space_id: str = Field(..., description="The unique identifier of the space containing the environment where the tag will be created."),
    environment_id: str = Field(..., description="The unique identifier of the environment within the space where the tag will be created."),
    tag_id: str = Field(..., description="The unique identifier for the tag being created."),
) -> dict[str, Any]:
    """Create a new tag within a specific environment in Contentful. Tags are used to organize and categorize content for better management and filtering."""

    # Construct request model with validation
    try:
        _request = _models.PostSpacesEnvironmentsTagsRequest(
            path=_models.PostSpacesEnvironmentsTagsRequestPath(space_id=space_id, environment_id=environment_id, tag_id=tag_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_tag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}/tags/{tag_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}/tags/{tag_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_tag")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_tag", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_tag",
        method="POST",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Content tags
@mcp.tool()
async def update_tag(
    space_id: str = Field(..., description="The unique identifier of the space containing the tag to be updated."),
    environment_id: str = Field(..., description="The unique identifier of the environment within the space where the tag is located."),
    tag_id: str = Field(..., description="The unique identifier of the tag to be updated."),
) -> dict[str, Any]:
    """Update an existing tag within a specific environment and space. This operation allows you to modify tag properties and settings."""

    # Construct request model with validation
    try:
        _request = _models.PutSpacesEnvironmentsTagsRequest(
            path=_models.PutSpacesEnvironmentsTagsRequestPath(space_id=space_id, environment_id=environment_id, tag_id=tag_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_tag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}/tags/{tag_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}/tags/{tag_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_tag")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_tag", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_tag",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Content tags
@mcp.tool()
async def delete_tag(
    space_id: str = Field(..., description="The unique identifier of the space containing the environment and tag to be deleted."),
    environment_id: str = Field(..., description="The unique identifier of the environment within the space that contains the tag to be deleted."),
    tag_id: str = Field(..., description="The unique identifier of the tag to be deleted."),
) -> dict[str, Any]:
    """Remove a tag from a specific environment within a space. This permanently deletes the tag and its associations."""

    # Construct request model with validation
    try:
        _request = _models.DeleteSpacesEnvironmentsTagsRequest(
            path=_models.DeleteSpacesEnvironmentsTagsRequestPath(space_id=space_id, environment_id=environment_id, tag_id=tag_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_tag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}/tags/{tag_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}/tags/{tag_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_tag")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_tag", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_tag",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Webhook
@mcp.tool()
async def list_webhooks(space_id: str = Field(..., description="The unique identifier of the space containing the webhooks you want to retrieve (e.g., '5nvk6q4s3ttw').")) -> dict[str, Any]:
    """Retrieve all webhook definitions configured for a specific space. Webhooks allow you to receive HTTP notifications when content changes occur in your space."""

    # Construct request model with validation
    try:
        _request = _models.GetSpacesBySpaceIdWebhookDefinitionsRequest(
            path=_models.GetSpacesBySpaceIdWebhookDefinitionsRequestPath(space_id=space_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_webhooks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/webhook_definitions", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/webhook_definitions"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_webhooks")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_webhooks", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_webhooks",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Webhook
@mcp.tool()
async def create_webhook(space_id: str = Field(..., description="The unique identifier of the space where the webhook will be created (e.g., '5nvk6q4s3ttw').")) -> dict[str, Any]:
    """Create a new webhook definition for a space to receive HTTP notifications when content changes. Webhooks enable real-time integration with external systems by posting events to your specified endpoint."""

    # Construct request model with validation
    try:
        _request = _models.PostSpacesWebhookDefinitionsRequest(
            path=_models.PostSpacesWebhookDefinitionsRequestPath(space_id=space_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_webhook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/webhook_definitions", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/webhook_definitions"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_webhook")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_webhook", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_webhook",
        method="POST",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Webhook
@mcp.tool()
async def list_webhook_calls(
    space_id: str = Field(..., description="The unique identifier of the space containing the webhook. This is required to scope the webhook calls to the correct environment."),
    webhook_id: str = Field(..., description="The unique identifier of the webhook whose call history you want to retrieve. This specifies which webhook's execution log to fetch."),
) -> dict[str, Any]:
    """Retrieve a list of recent webhook call attempts for a specific webhook, including their status and execution details. This helps monitor webhook delivery and troubleshoot integration issues."""

    # Construct request model with validation
    try:
        _request = _models.GetSpacesBySpaceIdWebhooksByWebhookIdCallsRequest(
            path=_models.GetSpacesBySpaceIdWebhooksByWebhookIdCallsRequestPath(space_id=space_id, webhook_id=webhook_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_webhook_calls: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/webhooks/{webhook_id}/calls", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/webhooks/{webhook_id}/calls"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_webhook_calls")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_webhook_calls", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_webhook_calls",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Webhook
@mcp.tool()
async def get_webhook_call(
    space_id: str = Field(..., description="The unique identifier of the space containing the webhook."),
    webhook_id: str = Field(..., description="The unique identifier of the webhook for which to retrieve call details."),
    call_id: str = Field(..., description="The unique identifier of the specific webhook call to retrieve."),
) -> dict[str, Any]:
    """Retrieve detailed information about a specific webhook call, including its request, response, and execution status."""

    # Construct request model with validation
    try:
        _request = _models.GetSpacesBySpaceIdWebhooksByWebhookIdCallsByCallIdRequest(
            path=_models.GetSpacesBySpaceIdWebhooksByWebhookIdCallsByCallIdRequestPath(space_id=space_id, webhook_id=webhook_id, call_id=call_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_webhook_call: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/webhooks/{webhook_id}/calls/{call_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/webhooks/{webhook_id}/calls/{call_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_webhook_call")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_webhook_call", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_webhook_call",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Webhook
@mcp.tool()
async def check_webhook_health(
    space_id: str = Field(..., description="The unique identifier of the space containing the webhook."),
    webhook_id: str = Field(..., description="The unique identifier of the webhook whose health status should be retrieved."),
) -> dict[str, Any]:
    """Retrieve the health status and diagnostic information for a specific webhook in a space, including recent delivery attempts and error details."""

    # Construct request model with validation
    try:
        _request = _models.GetSpacesWebhooksHealthRequest(
            path=_models.GetSpacesWebhooksHealthRequestPath(space_id=space_id, webhook_id=webhook_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for check_webhook_health: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/webhooks/{webhook_id}/health", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/webhooks/{webhook_id}/health"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("check_webhook_health")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("check_webhook_health", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="check_webhook_health",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Webhook
@mcp.tool()
async def get_webhook_definition(
    space_id: str = Field(..., description="The unique identifier of the Contentful space containing the webhook definition."),
    webhook_definition_id: str = Field(..., description="The unique identifier of the webhook definition to retrieve."),
) -> dict[str, Any]:
    """Retrieve a single webhook definition by its ID. Returns the complete configuration and metadata for the specified webhook in a Contentful space."""

    # Construct request model with validation
    try:
        _request = _models.GetSpacesBySpaceIdWebhookDefinitionsByWebhookDefinitionIdRequest(
            path=_models.GetSpacesBySpaceIdWebhookDefinitionsByWebhookDefinitionIdRequestPath(space_id=space_id, webhook_definition_id=webhook_definition_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_webhook_definition: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/webhook_definitions/{webhook_definition_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/webhook_definitions/{webhook_definition_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_webhook_definition")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_webhook_definition", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_webhook_definition",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Webhook
@mcp.tool()
async def upsert_webhook(
    space_id: str = Field(..., description="The unique identifier of the space where the webhook will be created or updated."),
    webhook_definition_id: str = Field(..., description="The unique identifier of the webhook definition to create or update."),
) -> dict[str, Any]:
    """Create a new webhook or update an existing one for a space. Webhooks allow you to receive HTTP notifications when content changes occur."""

    # Construct request model with validation
    try:
        _request = _models.PutSpacesWebhookDefinitionsRequest(
            path=_models.PutSpacesWebhookDefinitionsRequestPath(space_id=space_id, webhook_definition_id=webhook_definition_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for upsert_webhook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/webhook_definitions/{webhook_definition_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/webhook_definitions/{webhook_definition_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("upsert_webhook")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("upsert_webhook", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="upsert_webhook",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Webhook
@mcp.tool()
async def delete_webhook(
    space_id: str = Field(..., description="The unique identifier of the space containing the webhook definition to delete."),
    webhook_definition_id: str = Field(..., description="The unique identifier of the webhook definition to delete."),
) -> dict[str, Any]:
    """Permanently delete a webhook definition from a space. This removes the webhook configuration and stops any further event notifications from being sent to the configured endpoint."""

    # Construct request model with validation
    try:
        _request = _models.DeleteSpacesWebhookDefinitionsRequest(
            path=_models.DeleteSpacesWebhookDefinitionsRequestPath(space_id=space_id, webhook_definition_id=webhook_definition_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_webhook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/webhook_definitions/{webhook_definition_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/webhook_definitions/{webhook_definition_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_webhook")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_webhook", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_webhook",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Roles
@mcp.tool()
async def list_roles(space_id: str = Field(..., description="The unique identifier of the Contentful space (e.g., '5nvk6q4s3ttw'). This space ID is required to fetch its associated roles.")) -> dict[str, Any]:
    """Retrieve all roles available in a Contentful space. Roles define permissions and access control for space members."""

    # Construct request model with validation
    try:
        _request = _models.GetSpacesBySpaceIdRolesRequest(
            path=_models.GetSpacesBySpaceIdRolesRequestPath(space_id=space_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_roles: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/roles", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/roles"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_roles")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_roles", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_roles",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Roles
@mcp.tool()
async def create_role(space_id: str = Field(..., description="The unique identifier of the Contentful space where the role will be created.")) -> dict[str, Any]:
    """Create a new role within a Contentful space. Roles define permissions and access control for team members working in the space."""

    # Construct request model with validation
    try:
        _request = _models.PostSpacesRolesRequest(
            path=_models.PostSpacesRolesRequestPath(space_id=space_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_role: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/roles", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/roles"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_role")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_role", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_role",
        method="POST",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Roles
@mcp.tool()
async def get_role(
    space_id: str = Field(..., description="The unique identifier of the space containing the role."),
    role_id: str = Field(..., description="The unique identifier of the role to retrieve."),
) -> dict[str, Any]:
    """Retrieve a specific role within a space. Returns the role's details including permissions and associated metadata."""

    # Construct request model with validation
    try:
        _request = _models.GetSpacesBySpaceIdRolesByRoleIdRequest(
            path=_models.GetSpacesBySpaceIdRolesByRoleIdRequestPath(space_id=space_id, role_id=role_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_role: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/roles/{role_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/roles/{role_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_role")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_role", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_role",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Roles
@mcp.tool()
async def update_role(
    space_id: str = Field(..., description="The unique identifier of the space containing the role to be updated."),
    role_id: str = Field(..., description="The unique identifier of the role to be updated."),
) -> dict[str, Any]:
    """Update an existing role within a space. Modify role properties such as name, description, and permissions."""

    # Construct request model with validation
    try:
        _request = _models.PutSpacesRolesRequest(
            path=_models.PutSpacesRolesRequestPath(space_id=space_id, role_id=role_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_role: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/roles/{role_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/roles/{role_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_role")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_role", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_role",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Roles
@mcp.tool()
async def delete_role(
    space_id: str = Field(..., description="The unique identifier of the space containing the role to delete."),
    role_id: str = Field(..., description="The unique identifier of the role to delete."),
) -> dict[str, Any]:
    """Permanently delete a role from a space. This action removes the role and all associated permissions, affecting any users or API tokens assigned to this role."""

    # Construct request model with validation
    try:
        _request = _models.DeleteSpacesRolesRequest(
            path=_models.DeleteSpacesRolesRequestPath(space_id=space_id, role_id=role_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_role: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/roles/{role_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/roles/{role_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_role")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_role", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_role",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Snapshots
@mcp.tool()
async def list_entry_snapshots(
    space_id: str = Field(..., description="The unique identifier of the space containing the entry. This is a required alphanumeric identifier that specifies which workspace to query."),
    entry_id: str = Field(..., description="The unique identifier of the entry for which to retrieve snapshots. This is a required alphanumeric identifier that specifies which entry's version history to fetch."),
) -> dict[str, Any]:
    """Retrieve all snapshots for a specific entry in the master environment. Snapshots capture the state of an entry at different points in time, allowing you to view historical versions and changes."""

    # Construct request model with validation
    try:
        _request = _models.GetSpacesBySpaceIdEnvironmentsMasterEntriesByEntryIdSnapshotsRequest(
            path=_models.GetSpacesBySpaceIdEnvironmentsMasterEntriesByEntryIdSnapshotsRequestPath(space_id=space_id, entry_id=entry_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_entry_snapshots: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/master/entries/{entry_id}/snapshots", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/master/entries/{entry_id}/snapshots"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_entry_snapshots")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_entry_snapshots", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_entry_snapshots",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Snapshots
@mcp.tool()
async def list_content_type_snapshots(
    space_id: str = Field(..., description="The unique identifier of the space containing the content type."),
    content_type_id: str = Field(..., description="The unique identifier of the content type for which to retrieve snapshots."),
) -> dict[str, Any]:
    """Retrieve all snapshots for a specific content type in the master environment. Snapshots capture the state of a content type at different points in time, allowing you to track changes and restore previous versions."""

    # Construct request model with validation
    try:
        _request = _models.GetSpacesBySpaceIdEnvironmentsMasterContentTypesByContentTypeIdSnapshotsRequest(
            path=_models.GetSpacesBySpaceIdEnvironmentsMasterContentTypesByContentTypeIdSnapshotsRequestPath(space_id=space_id, content_type_id=content_type_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_content_type_snapshots: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/master/content_types/{content_type_id}/snapshots", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/master/content_types/{content_type_id}/snapshots"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_content_type_snapshots")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_content_type_snapshots", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_content_type_snapshots",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Snapshots
@mcp.tool()
async def get_content_type_snapshot(
    space_id: str = Field(..., description="The unique identifier of the space containing the content type."),
    content_type_id: str = Field(..., description="The unique identifier of the content type for which to retrieve the snapshot."),
    snapshot_id: str = Field(..., description="The unique identifier of the snapshot to retrieve."),
) -> dict[str, Any]:
    """Retrieve a specific snapshot of a content type, allowing you to view the content type definition at a particular point in time."""

    # Construct request model with validation
    try:
        _request = _models.GetSpacesBySpaceIdEnvironmentsMasterContentTypesByContentTypeIdSnapshotsBySnapshotIdRequest(
            path=_models.GetSpacesBySpaceIdEnvironmentsMasterContentTypesByContentTypeIdSnapshotsBySnapshotIdRequestPath(space_id=space_id, content_type_id=content_type_id, snapshot_id=snapshot_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_content_type_snapshot: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/master/content_types/{content_type_id}/snapshots/{snapshot_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/master/content_types/{content_type_id}/snapshots/{snapshot_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_content_type_snapshot")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_content_type_snapshot", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_content_type_snapshot",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Snapshots
@mcp.tool()
async def get_entry_snapshot(
    space_id: str = Field(..., description="The unique identifier of the space containing the entry."),
    entry_id: str = Field(..., description="The unique identifier of the entry for which you want to retrieve the snapshot."),
    snapshot_id: str = Field(..., description="The unique identifier of the snapshot to retrieve."),
) -> dict[str, Any]:
    """Retrieve a specific snapshot of an entry, allowing you to view the entry's state at a particular point in time."""

    # Construct request model with validation
    try:
        _request = _models.GetSpacesBySpaceIdEnvironmentsMasterEntriesByEntryIdSnapshotsBySnapshotIdRequest(
            path=_models.GetSpacesBySpaceIdEnvironmentsMasterEntriesByEntryIdSnapshotsBySnapshotIdRequestPath(space_id=space_id, entry_id=entry_id, snapshot_id=snapshot_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_entry_snapshot: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/master/entries/{entry_id}/snapshots/{snapshot_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/master/entries/{entry_id}/snapshots/{snapshot_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_entry_snapshot")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_entry_snapshot", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_entry_snapshot",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Space memberships
@mcp.tool()
async def list_space_memberships(space_id: str = Field(..., description="The unique identifier of the space. Use the space ID to target a specific workspace (e.g., '5nvk6q4s3ttw').")) -> dict[str, Any]:
    """Retrieve all space memberships for a given space. Returns a collection of all users and their roles within the specified space."""

    # Construct request model with validation
    try:
        _request = _models.GetSpacesBySpaceIdSpaceMembershipsRequest(
            path=_models.GetSpacesBySpaceIdSpaceMembershipsRequestPath(space_id=space_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_space_memberships: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/space_memberships", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/space_memberships"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_space_memberships")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_space_memberships", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_space_memberships",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Space memberships
@mcp.tool()
async def create_space_membership(space_id: str = Field(..., description="The unique identifier of the space where the membership will be created.")) -> dict[str, Any]:
    """Add a new member to a space with specified roles and permissions. This operation creates a space membership record that grants a user or team access to the space."""

    # Construct request model with validation
    try:
        _request = _models.PostSpacesSpaceMembershipsRequest(
            path=_models.PostSpacesSpaceMembershipsRequestPath(space_id=space_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_space_membership: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/space_memberships", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/space_memberships"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_space_membership")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_space_membership", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_space_membership",
        method="POST",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Space memberships
@mcp.tool()
async def get_space_membership(
    space_id: str = Field(..., description="The unique identifier of the Contentful space containing the membership."),
    space_membership_id: str = Field(..., description="The unique identifier of the space membership to retrieve."),
) -> dict[str, Any]:
    """Retrieve a specific space membership by its ID. Returns detailed information about a user's membership and role within a Contentful space."""

    # Construct request model with validation
    try:
        _request = _models.GetSpacesBySpaceIdSpaceMembershipsBySpaceMembershipIdRequest(
            path=_models.GetSpacesBySpaceIdSpaceMembershipsBySpaceMembershipIdRequestPath(space_id=space_id, space_membership_id=space_membership_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_space_membership: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/space_memberships/{space_membership_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/space_memberships/{space_membership_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_space_membership")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_space_membership", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_space_membership",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Space memberships
@mcp.tool()
async def update_space_membership(
    space_id: str = Field(..., description="The unique identifier of the space containing the membership to update."),
    space_membership_id: str = Field(..., description="The unique identifier of the space membership record to update."),
) -> dict[str, Any]:
    """Update a space membership to modify user roles and permissions within a specific space. This operation allows you to change access levels and membership details for a user in the space."""

    # Construct request model with validation
    try:
        _request = _models.PutSpacesSpaceMembershipsRequest(
            path=_models.PutSpacesSpaceMembershipsRequestPath(space_id=space_id, space_membership_id=space_membership_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_space_membership: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/space_memberships/{space_membership_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/space_memberships/{space_membership_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_space_membership")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_space_membership", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_space_membership",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Space memberships
@mcp.tool()
async def remove_space_member(
    space_id: str = Field(..., description="The unique identifier of the space from which the member will be removed."),
    space_membership_id: str = Field(..., description="The unique identifier of the space membership record to delete."),
) -> dict[str, Any]:
    """Remove a member from a space by deleting their space membership. This revokes their access to the specified space."""

    # Construct request model with validation
    try:
        _request = _models.DeleteSpacesSpaceMembershipsRequest(
            path=_models.DeleteSpacesSpaceMembershipsRequestPath(space_id=space_id, space_membership_id=space_membership_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_space_member: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/space_memberships/{space_membership_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/space_memberships/{space_membership_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_space_member")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_space_member", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_space_member",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Space teams
@mcp.tool()
async def list_teams(space_id: str = Field(..., description="The unique identifier of the space for which to retrieve teams.")) -> dict[str, Any]:
    """Retrieve all teams associated with a specific space. Teams are organizational units within a space that can be assigned permissions and manage content collaboratively."""

    # Construct request model with validation
    try:
        _request = _models.GetSpacesTeamsRequest(
            path=_models.GetSpacesTeamsRequestPath(space_id=space_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_teams: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/teams", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/teams"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_teams")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_teams", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_teams",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: API keys
@mcp.tool()
async def get_delivery_api_key(
    space_id: str = Field(..., description="The unique identifier of the space containing the API key."),
    api_key_id: str = Field(..., description="The unique identifier of the Delivery API key to retrieve."),
) -> dict[str, Any]:
    """Retrieve a specific Delivery API key for a space. Use this to view details of an existing API key used for content delivery."""

    # Construct request model with validation
    try:
        _request = _models.GetSpacesBySpaceIdApiKeysByApiKeyIdRequest(
            path=_models.GetSpacesBySpaceIdApiKeysByApiKeyIdRequestPath(space_id=space_id, api_key_id=api_key_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_delivery_api_key: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/api_keys/{api_key_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/api_keys/{api_key_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_delivery_api_key")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_delivery_api_key", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_delivery_api_key",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: API keys
@mcp.tool()
async def update_delivery_api_key(
    space_id: str = Field(..., description="The unique identifier of the space containing the API key to update."),
    api_key_id: str = Field(..., description="The unique identifier of the Delivery API key to update."),
) -> dict[str, Any]:
    """Update the configuration of a Delivery API key within a space. This allows you to modify settings for an existing API key used for content delivery."""

    # Construct request model with validation
    try:
        _request = _models.PutSpacesApiKeysRequest(
            path=_models.PutSpacesApiKeysRequestPath(space_id=space_id, api_key_id=api_key_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_delivery_api_key: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/api_keys/{api_key_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/api_keys/{api_key_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_delivery_api_key")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_delivery_api_key", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_delivery_api_key",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: API keys
@mcp.tool()
async def delete_delivery_api_key(
    space_id: str = Field(..., description="The unique identifier of the space containing the API key to delete."),
    api_key_id: str = Field(..., description="The unique identifier of the Delivery API key to delete."),
) -> dict[str, Any]:
    """Permanently delete a Delivery API key from a space. This action cannot be undone and will immediately revoke access for any applications using this key."""

    # Construct request model with validation
    try:
        _request = _models.DeleteSpacesApiKeysRequest(
            path=_models.DeleteSpacesApiKeysRequestPath(space_id=space_id, api_key_id=api_key_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_delivery_api_key: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/api_keys/{api_key_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/api_keys/{api_key_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_delivery_api_key")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_delivery_api_key", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_delivery_api_key",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: API keys
@mcp.tool()
async def list_delivery_api_keys(space_id: str = Field(..., description="The unique identifier of the space containing the API keys to retrieve.")) -> dict[str, Any]:
    """Retrieve all Delivery API keys configured for a specific space. These keys are used to access published content through the Contentful Delivery API."""

    # Construct request model with validation
    try:
        _request = _models.GetSpacesBySpaceIdApiKeysRequest(
            path=_models.GetSpacesBySpaceIdApiKeysRequestPath(space_id=space_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_delivery_api_keys: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/api_keys", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/api_keys"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_delivery_api_keys")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_delivery_api_keys", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_delivery_api_keys",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: API keys
@mcp.tool()
async def create_delivery_api_key(space_id: str = Field(..., description="The unique identifier of the Contentful space where the API key will be created.")) -> dict[str, Any]:
    """Create a new Delivery API key for a Contentful space to enable read-only access to published content via the Delivery API."""

    # Construct request model with validation
    try:
        _request = _models.PostSpacesApiKeysRequest(
            path=_models.PostSpacesApiKeysRequestPath(space_id=space_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_delivery_api_key: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/api_keys", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/api_keys"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_delivery_api_key")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_delivery_api_key", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_delivery_api_key",
        method="POST",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: API keys
@mcp.tool()
async def list_preview_api_keys(space_id: str = Field(..., description="The unique identifier of the space containing the Preview API keys to retrieve.")) -> dict[str, Any]:
    """Retrieve all Preview API keys for a specific space. Preview API keys are used to access published content in a read-only manner."""

    # Construct request model with validation
    try:
        _request = _models.GetSpacesBySpaceIdPreviewApiKeysRequest(
            path=_models.GetSpacesBySpaceIdPreviewApiKeysRequestPath(space_id=space_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_preview_api_keys: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/preview_api_keys", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/preview_api_keys"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_preview_api_keys")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_preview_api_keys", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_preview_api_keys",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: API keys
@mcp.tool()
async def get_preview_api_key(
    space_id: str = Field(..., description="The unique identifier of the space containing the Preview API key."),
    preview_api_key_id: str = Field(..., description="The unique identifier of the Preview API key to retrieve."),
) -> dict[str, Any]:
    """Retrieve a single Preview API key for a specific space. Preview API keys are used to access published content in a read-only manner."""

    # Construct request model with validation
    try:
        _request = _models.GetSpacesBySpaceIdPreviewApiKeysByPreviewApiKeyIdRequest(
            path=_models.GetSpacesBySpaceIdPreviewApiKeysByPreviewApiKeyIdRequestPath(space_id=space_id, preview_api_key_id=preview_api_key_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_preview_api_key: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/preview_api_keys/{preview_api_key_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/preview_api_keys/{preview_api_key_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_preview_api_key")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_preview_api_key", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_preview_api_key",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Personal Access token
@mcp.tool()
async def list_access_tokens() -> dict[str, Any]:
    """Retrieve all personal access tokens for the authenticated user. This allows you to view and manage your API credentials used for programmatic access to Contentful."""

    # Extract parameters for API call
    _http_path = "/users/me/access_tokens"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_access_tokens")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_access_tokens", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_access_tokens",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Personal Access token
@mcp.tool()
async def create_access_token() -> dict[str, Any]:
    """Generate a new personal access token for authenticating API requests on behalf of the current user. This token can be used to access the Content Management API without exposing your main credentials."""

    # Extract parameters for API call
    _http_path = "/users/me/access_tokens"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_access_token")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_access_token", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_access_token",
        method="POST",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Personal Access token
@mcp.tool()
async def get_access_token(token_id: str = Field(..., description="The unique identifier of the personal access token to retrieve.")) -> dict[str, Any]:
    """Retrieve a specific personal access token by its ID. This allows you to view details about an individual access token associated with your account."""

    # Construct request model with validation
    try:
        _request = _models.GetUsersMeAccessTokensByTokenIdRequest(
            path=_models.GetUsersMeAccessTokensByTokenIdRequestPath(token_id=token_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_access_token: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/users/me/access_tokens/{token_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/users/me/access_tokens/{token_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_access_token")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_access_token", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_access_token",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Personal Access token
@mcp.tool()
async def revoke_access_token(token_id: str = Field(..., description="The unique identifier of the personal access token to revoke.")) -> dict[str, Any]:
    """Revoke a personal access token to immediately invalidate it and prevent further API access using that token."""

    # Construct request model with validation
    try:
        _request = _models.PutUsersMeAccessTokensRevokedRequest(
            path=_models.PutUsersMeAccessTokensRevokedRequestPath(token_id=token_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for revoke_access_token: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/users/me/access_tokens/{token_id}/revoked", _request.path.model_dump(by_alias=True)) if _request.path else "/users/me/access_tokens/{token_id}/revoked"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("revoke_access_token")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("revoke_access_token", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="revoke_access_token",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Users
@mcp.tool()
async def get_current_user() -> dict[str, Any]:
    """Retrieve the profile and details of the currently authenticated user. This operation requires valid authentication credentials."""

    # Extract parameters for API call
    _http_path = "/users/me"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_current_user")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_current_user", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_current_user",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Tasks
@mcp.tool()
async def list_entry_tasks(
    space_id: str = Field(..., description="The unique identifier of the Contentful space containing the entry."),
    environment_id: str = Field(..., description="The unique identifier of the environment within the space where the entry resides."),
    entry_id: str = Field(..., description="The unique identifier of the entry for which to retrieve associated tasks."),
) -> dict[str, Any]:
    """Retrieve all tasks associated with a specific entry within a Contentful environment. Tasks represent workflow actions or assignments related to the entry."""

    # Construct request model with validation
    try:
        _request = _models.GetSpacesBySpaceIdEnvironmentsByEnvironmentIdEntriesByEntryIdTasksRequest(
            path=_models.GetSpacesBySpaceIdEnvironmentsByEnvironmentIdEntriesByEntryIdTasksRequestPath(space_id=space_id, environment_id=environment_id, entry_id=entry_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_entry_tasks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}/entries/{entry_id}/tasks", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}/entries/{entry_id}/tasks"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_entry_tasks")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_entry_tasks", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_entry_tasks",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Tasks
@mcp.tool()
async def create_entry_task(
    space_id: str = Field(..., description="The unique identifier of the Contentful space containing the entry."),
    environment_id: str = Field(..., description="The unique identifier of the environment within the space where the entry resides."),
    entry_id: str = Field(..., description="The unique identifier of the entry for which the task is being created."),
) -> dict[str, Any]:
    """Create a task for a specific entry within a Contentful space and environment. Tasks are used to track workflows and actions associated with content entries."""

    # Construct request model with validation
    try:
        _request = _models.PostSpacesEnvironmentsEntriesTasksRequest(
            path=_models.PostSpacesEnvironmentsEntriesTasksRequestPath(space_id=space_id, environment_id=environment_id, entry_id=entry_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_entry_task: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}/entries/{entry_id}/tasks", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}/entries/{entry_id}/tasks"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_entry_task")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_entry_task", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_entry_task",
        method="POST",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Tasks
@mcp.tool()
async def get_task(
    space_id: str = Field(..., description="The unique identifier of the space containing the task."),
    environment_id: str = Field(..., description="The unique identifier of the environment within the space."),
    entry_id: str = Field(..., description="The unique identifier of the entry that contains the task."),
    task_id: str = Field(..., description="The unique identifier of the task to retrieve."),
) -> dict[str, Any]:
    """Retrieve a specific task associated with an entry. Tasks are used to track workflows and approvals within Contentful entries."""

    # Construct request model with validation
    try:
        _request = _models.GetSpacesBySpaceIdEnvironmentsByEnvironmentIdEntriesByEntryIdTasksByTaskIdRequest(
            path=_models.GetSpacesBySpaceIdEnvironmentsByEnvironmentIdEntriesByEntryIdTasksByTaskIdRequestPath(space_id=space_id, environment_id=environment_id, entry_id=entry_id, task_id=task_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_task: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}/entries/{entry_id}/tasks/{task_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}/entries/{entry_id}/tasks/{task_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_task")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_task", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_task",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Tasks
@mcp.tool()
async def update_task(
    space_id: str = Field(..., description="The unique identifier of the space containing the entry and task to update."),
    environment_id: str = Field(..., description="The unique identifier of the environment within the space where the task exists."),
    entry_id: str = Field(..., description="The unique identifier of the entry that the task is associated with."),
    task_id: str = Field(..., description="The unique identifier of the task to update."),
) -> dict[str, Any]:
    """Update an existing task associated with a specific entry in a Contentful environment. This allows you to modify task details such as status, assignees, or other task-related metadata."""

    # Construct request model with validation
    try:
        _request = _models.PutSpacesEnvironmentsEntriesTasksRequest(
            path=_models.PutSpacesEnvironmentsEntriesTasksRequestPath(space_id=space_id, environment_id=environment_id, entry_id=entry_id, task_id=task_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_task: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}/entries/{entry_id}/tasks/{task_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}/entries/{entry_id}/tasks/{task_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_task")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_task", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_task",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Tasks
@mcp.tool()
async def delete_task(
    space_id: str = Field(..., description="The unique identifier of the space containing the entry and task to be deleted."),
    environment_id: str = Field(..., description="The unique identifier of the environment within the space where the entry and task reside."),
    entry_id: str = Field(..., description="The unique identifier of the entry that contains the task to be deleted."),
    task_id: str = Field(..., description="The unique identifier of the task to be deleted."),
) -> dict[str, Any]:
    """Permanently delete a specific task associated with an entry. This removes the task and all its related data from the entry."""

    # Construct request model with validation
    try:
        _request = _models.DeleteSpacesEnvironmentsEntriesTasksRequest(
            path=_models.DeleteSpacesEnvironmentsEntriesTasksRequestPath(space_id=space_id, environment_id=environment_id, entry_id=entry_id, task_id=task_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_task: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}/entries/{entry_id}/tasks/{task_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}/entries/{entry_id}/tasks/{task_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_task")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_task", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_task",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Schedule actions
@mcp.tool()
async def list_scheduled_actions(space_id: str = Field(..., description="The unique identifier of the space containing the scheduled actions you want to retrieve.")) -> dict[str, Any]:
    """Retrieve all scheduled actions for a specific space. Scheduled actions allow you to automate content management tasks at predetermined times."""

    # Construct request model with validation
    try:
        _request = _models.GetSpacesScheduledActionsRequest(
            path=_models.GetSpacesScheduledActionsRequestPath(space_id=space_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_scheduled_actions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/scheduled_actions", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/scheduled_actions"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_scheduled_actions")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_scheduled_actions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_scheduled_actions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Schedule actions
@mcp.tool()
async def create_scheduled_action(space_id: str = Field(..., description="The unique identifier of the space where the scheduled action will be created.")) -> dict[str, Any]:
    """Create a new scheduled action within a space. Scheduled actions allow you to automate content management tasks at specified times."""

    # Construct request model with validation
    try:
        _request = _models.PostSpacesScheduledActionsRequest(
            path=_models.PostSpacesScheduledActionsRequestPath(space_id=space_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_scheduled_action: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/scheduled_actions", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/scheduled_actions"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_scheduled_action")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_scheduled_action", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_scheduled_action",
        method="POST",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Schedule actions
@mcp.tool()
async def update_scheduled_action(
    space_id: str = Field(..., description="The unique identifier of the space containing the scheduled action to update."),
    scheduled_action_id: str = Field(..., description="The unique identifier of the scheduled action to update."),
) -> dict[str, Any]:
    """Update an existing scheduled action in a space. Modify the configuration and settings of a scheduled action that has been previously created."""

    # Construct request model with validation
    try:
        _request = _models.PutSpacesScheduledActionsRequest(
            path=_models.PutSpacesScheduledActionsRequestPath(space_id=space_id, scheduled_action_id=scheduled_action_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_scheduled_action: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/scheduled_actions/{scheduled_action_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/scheduled_actions/{scheduled_action_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_scheduled_action")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_scheduled_action", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_scheduled_action",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Schedule actions
@mcp.tool()
async def cancel_scheduled_action(
    space_id: str = Field(..., description="The unique identifier of the space containing the scheduled action to cancel."),
    scheduled_action_id: str = Field(..., description="The unique identifier of the scheduled action to cancel."),
) -> dict[str, Any]:
    """Cancel a scheduled action in a space. This prevents the scheduled action from executing at its designated time."""

    # Construct request model with validation
    try:
        _request = _models.DeleteSpacesScheduledActionsRequest(
            path=_models.DeleteSpacesScheduledActionsRequestPath(space_id=space_id, scheduled_action_id=scheduled_action_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for cancel_scheduled_action: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/scheduled_actions/{scheduled_action_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/scheduled_actions/{scheduled_action_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("cancel_scheduled_action")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("cancel_scheduled_action", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="cancel_scheduled_action",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Releases
@mcp.tool()
async def list_releases(
    space_id: str = Field(..., description="The unique identifier of the space containing the environment and releases."),
    environment_id: str = Field(..., description="The unique identifier of the environment within the space from which to retrieve releases."),
) -> dict[str, Any]:
    """Retrieve all scheduled releases for a specific environment within a space. This allows you to query and manage content publication schedules."""

    # Construct request model with validation
    try:
        _request = _models.GetSpacesBySpaceIdEnvironmentByEnvironmentIdReleasesRequest(
            path=_models.GetSpacesBySpaceIdEnvironmentByEnvironmentIdReleasesRequestPath(space_id=space_id, environment_id=environment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_releases: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environment/{environment_id}/releases", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environment/{environment_id}/releases"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_releases")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_releases", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_releases",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Releases
@mcp.tool()
async def create_environment_release(
    space_id: str = Field(..., description="The unique identifier of the space containing the environment where the release will be created."),
    environment_id: str = Field(..., description="The unique identifier of the environment within the space where the release will be created."),
) -> dict[str, Any]:
    """Create a new release for a specific environment within a space. Releases allow you to schedule and manage content deployments across your Contentful workspace."""

    # Construct request model with validation
    try:
        _request = _models.PostSpacesEnvironmentReleasesRequest(
            path=_models.PostSpacesEnvironmentReleasesRequestPath(space_id=space_id, environment_id=environment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_environment_release: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environment/{environment_id}/releases", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environment/{environment_id}/releases"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_environment_release")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_environment_release", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_environment_release",
        method="POST",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Releases
@mcp.tool()
async def validate_release(
    space_id: str = Field(..., description="The unique identifier of the space containing the release."),
    environment_id: str = Field(..., description="The unique identifier of the environment where the release will be validated."),
    releases_id: str = Field(..., description="The unique identifier of the release to validate."),
) -> dict[str, Any]:
    """Create a validation action for a scheduled release in a specific environment. This initiates validation of the release's contents before it can be published."""

    # Construct request model with validation
    try:
        _request = _models.PostSpacesEnvironmentReleasesValidateRequest(
            path=_models.PostSpacesEnvironmentReleasesValidateRequestPath(space_id=space_id, environment_id=environment_id, releases_id=releases_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for validate_release: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environment/{environment_id}/releases/{releases_id}/validate", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environment/{environment_id}/releases/{releases_id}/validate"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("validate_release")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("validate_release", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="validate_release",
        method="POST",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Releases
@mcp.tool()
async def list_release_actions(
    space_id: str = Field(..., description="The unique identifier of the Contentful space containing the release."),
    environment_id: str = Field(..., description="The unique identifier of the environment within the space where the release exists."),
    releases_id: str = Field(..., description="The unique identifier of the release for which to retrieve associated actions."),
) -> dict[str, Any]:
    """Retrieve all scheduled actions associated with a specific release in a Contentful environment. This allows you to query and monitor the actions planned for a release."""

    # Construct request model with validation
    try:
        _request = _models.GetSpacesBySpaceIdEnvironmentByEnvironmentIdReleasesByReleasesIdActionsRequest(
            path=_models.GetSpacesBySpaceIdEnvironmentByEnvironmentIdReleasesByReleasesIdActionsRequestPath(space_id=space_id, environment_id=environment_id, releases_id=releases_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_release_actions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environment/{environment_id}/releases/{releases_id}/actions", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environment/{environment_id}/releases/{releases_id}/actions"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_release_actions")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_release_actions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_release_actions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Releases
@mcp.tool()
async def get_release_action(
    space_id: str = Field(..., description="The unique identifier of the space containing the release and action."),
    environment_id: str = Field(..., description="The unique identifier of the environment within the space where the release action is defined."),
    releases_id: str = Field(..., description="The unique identifier of the release that contains the action."),
    release_action_id: str = Field(..., description="The unique identifier of the specific release action to retrieve."),
) -> dict[str, Any]:
    """Retrieve a specific scheduled action within a release. Use this to fetch details about a single release action, such as its status, timing, and associated content changes."""

    # Construct request model with validation
    try:
        _request = _models.GetSpacesBySpaceIdEnvironmentByEnvironmentIdReleasesByReleasesIdActionsByReleaseActionIdRequest(
            path=_models.GetSpacesBySpaceIdEnvironmentByEnvironmentIdReleasesByReleasesIdActionsByReleaseActionIdRequestPath(space_id=space_id, environment_id=environment_id, releases_id=releases_id, release_action_id=release_action_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_release_action: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environment/{environment_id}/releases/{releases_id}/actions/{release_action_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environment/{environment_id}/releases/{releases_id}/actions/{release_action_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_release_action")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_release_action", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_release_action",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Releases
@mcp.tool()
async def publish_release(
    space_id: str = Field(..., description="The unique identifier of the space containing the release to be published."),
    releases_id: str = Field(..., description="The unique identifier of the release to publish."),
    environment_id: str = Field(..., description="The unique identifier of the environment where the release will be published."),
) -> dict[str, Any]:
    """Publish a release to make its scheduled changes live in the specified environment. This marks the release as published and applies all contained entries and assets to the target environment."""

    # Construct request model with validation
    try:
        _request = _models.PutSpacesEnvironmentReleasesPublishedRequest(
            path=_models.PutSpacesEnvironmentReleasesPublishedRequestPath(space_id=space_id, releases_id=releases_id, environment_id=environment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for publish_release: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environment/{environment_id}/releases/{releases_id}/published", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environment/{environment_id}/releases/{releases_id}/published"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("publish_release")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("publish_release", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="publish_release",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Releases
@mcp.tool()
async def unpublish_release(
    space_id: str = Field(..., description="The unique identifier of the space containing the release."),
    releases_id: str = Field(..., description="The unique identifier of the release to unpublish."),
    environment_id: str = Field(..., description="The unique identifier of the environment where the release is published."),
) -> dict[str, Any]:
    """Unpublish a scheduled release, removing it from the published state and preventing its scheduled actions from executing."""

    # Construct request model with validation
    try:
        _request = _models.DeleteSpacesEnvironmentReleasesPublishedRequest(
            path=_models.DeleteSpacesEnvironmentReleasesPublishedRequestPath(space_id=space_id, releases_id=releases_id, environment_id=environment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for unpublish_release: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environment/{environment_id}/releases/{releases_id}/published", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environment/{environment_id}/releases/{releases_id}/published"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("unpublish_release")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("unpublish_release", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="unpublish_release",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Releases
@mcp.tool()
async def get_release(
    space_id: str = Field(..., description="The unique identifier of the space containing the release."),
    environment_id: str = Field(..., description="The unique identifier of the environment within the space where the release is located."),
    releases_id: str = Field(..., description="The unique identifier of the release to retrieve."),
) -> dict[str, Any]:
    """Retrieve a single scheduled release by its ID within a specific space and environment. This operation fetches detailed information about a release, including its scheduled actions and metadata."""

    # Construct request model with validation
    try:
        _request = _models.GetSpacesBySpaceIdEnvironmentByEnvironmentIdReleasesByReleasesIdRequest(
            path=_models.GetSpacesBySpaceIdEnvironmentByEnvironmentIdReleasesByReleasesIdRequestPath(space_id=space_id, environment_id=environment_id, releases_id=releases_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_release: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environment/{environment_id}/releases/{releases_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environment/{environment_id}/releases/{releases_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_release")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_release", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_release",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Releases
@mcp.tool()
async def update_release(
    space_id: str = Field(..., description="The unique identifier of the Contentful space containing the release to update."),
    environment_id: str = Field(..., description="The unique identifier of the environment within the space where the release exists."),
    releases_id: str = Field(..., description="The unique identifier of the release to update."),
) -> dict[str, Any]:
    """Update an existing release in a Contentful space environment. This operation allows you to modify release details such as scheduling, metadata, or other release properties."""

    # Construct request model with validation
    try:
        _request = _models.PutSpacesEnvironmentReleasesRequest(
            path=_models.PutSpacesEnvironmentReleasesRequestPath(space_id=space_id, environment_id=environment_id, releases_id=releases_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_release: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environment/{environment_id}/releases/{releases_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environment/{environment_id}/releases/{releases_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_release")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_release", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_release",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Releases
@mcp.tool()
async def delete_release(
    space_id: str = Field(..., description="The unique identifier of the space containing the release to be deleted."),
    environment_id: str = Field(..., description="The unique identifier of the environment within the space where the release exists."),
    releases_id: str = Field(..., description="The unique identifier of the release to be permanently removed."),
) -> dict[str, Any]:
    """Permanently remove a scheduled release from a specific environment within a space. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteSpacesEnvironmentReleasesRequest(
            path=_models.DeleteSpacesEnvironmentReleasesRequestPath(space_id=space_id, environment_id=environment_id, releases_id=releases_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_release: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environment/{environment_id}/releases/{releases_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environment/{environment_id}/releases/{releases_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_release")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_release", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_release",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Bulk Actions
@mcp.tool()
async def get_bulk_action(
    space_id: str = Field(..., description="The unique identifier of the space containing the bulk action."),
    environment_id: str = Field(..., description="The unique identifier of the environment within the space where the bulk action is located."),
    bulk_action_id: str = Field(..., description="The unique identifier of the bulk action to retrieve."),
) -> dict[str, Any]:
    """Retrieve details of a specific bulk action by its ID within a given space and environment. Use this to check the status and results of scheduled bulk operations."""

    # Construct request model with validation
    try:
        _request = _models.GetSpacesEnvironmentBulkActionsActionsRequest(
            path=_models.GetSpacesEnvironmentBulkActionsActionsRequestPath(space_id=space_id, environment_id=environment_id, bulk_action_id=bulk_action_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_bulk_action: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environment/{environment_id}/bulk_actions/actions/{bulk_action_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environment/{environment_id}/bulk_actions/actions/{bulk_action_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_bulk_action")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_bulk_action", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_bulk_action",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Bulk Actions
@mcp.tool()
async def publish_scheduled_actions(
    space_id: str = Field(..., description="The unique identifier of the space containing the environment where scheduled actions will be published."),
    environment_id: str = Field(..., description="The unique identifier of the environment within the space where the scheduled bulk actions will be published."),
) -> dict[str, Any]:
    """Publish scheduled bulk actions for a specific environment, making them active and executable. This operation processes pending scheduled actions that have been queued for publication."""

    # Construct request model with validation
    try:
        _request = _models.PostSpacesEnvironmentBulkActionsPublishRequest(
            path=_models.PostSpacesEnvironmentBulkActionsPublishRequestPath(space_id=space_id, environment_id=environment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for publish_scheduled_actions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environment/{environment_id}/bulk_actions/publish", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environment/{environment_id}/bulk_actions/publish"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("publish_scheduled_actions")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("publish_scheduled_actions", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="publish_scheduled_actions",
        method="POST",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Bulk Actions
@mcp.tool()
async def unpublish_scheduled_actions(
    space_id: str = Field(..., description="The unique identifier of the space containing the environment where scheduled actions will be unpublished."),
    environment_id: str = Field(..., description="The unique identifier of the environment within the space where scheduled actions will be unpublished."),
) -> dict[str, Any]:
    """Unpublish scheduled actions in bulk for a specific environment. This operation reverts previously scheduled publish actions, preventing them from being executed."""

    # Construct request model with validation
    try:
        _request = _models.PostSpacesEnvironmentBulkActionsUnpublishRequest(
            path=_models.PostSpacesEnvironmentBulkActionsUnpublishRequestPath(space_id=space_id, environment_id=environment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for unpublish_scheduled_actions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environment/{environment_id}/bulk_actions/unpublish", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environment/{environment_id}/bulk_actions/unpublish"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("unpublish_scheduled_actions")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("unpublish_scheduled_actions", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="unpublish_scheduled_actions",
        method="POST",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Bulk Actions
@mcp.tool()
async def validate_scheduled_bulk_action(
    space_id: str = Field(..., description="The unique identifier of the space containing the environment where the bulk action will be validated."),
    environment_id: str = Field(..., description="The unique identifier of the environment where the bulk action will be executed and validated."),
) -> dict[str, Any]:
    """Validate a bulk action before execution in a specific environment. This operation checks the bulk action configuration for errors and ensures it can be safely scheduled."""

    # Construct request model with validation
    try:
        _request = _models.PostSpacesEnvironmentBulkActionsValidateRequest(
            path=_models.PostSpacesEnvironmentBulkActionsValidateRequestPath(space_id=space_id, environment_id=environment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for validate_scheduled_bulk_action: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environment/{environment_id}/bulk_actions/validate", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environment/{environment_id}/bulk_actions/validate"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("validate_scheduled_bulk_action")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("validate_scheduled_bulk_action", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="validate_scheduled_bulk_action",
        method="POST",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: App definitions
@mcp.tool()
async def list_app_definitions(organization_id: str = Field(..., description="The unique identifier of the organization for which to retrieve app definitions.")) -> dict[str, Any]:
    """Retrieve all app definitions for a specific organization. App definitions describe the configuration and capabilities of apps available within the organization."""

    # Construct request model with validation
    try:
        _request = _models.GetOrganizationsByOrganizationIdAppDefinitionsRequest(
            path=_models.GetOrganizationsByOrganizationIdAppDefinitionsRequestPath(organization_id=organization_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_app_definitions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{organization_id}/app_definitions", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{organization_id}/app_definitions"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_app_definitions")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_app_definitions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_app_definitions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: App definitions
@mcp.tool()
async def create_app_definition(organization_id: str = Field(..., description="The unique identifier of the organization where the app definition will be created.")) -> dict[str, Any]:
    """Create a new app definition within an organization. App definitions specify the configuration and metadata for custom apps that can be installed and used within Contentful."""

    # Construct request model with validation
    try:
        _request = _models.PostOrganizationsAppDefinitionsRequest(
            path=_models.PostOrganizationsAppDefinitionsRequestPath(organization_id=organization_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_app_definition: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{organization_id}/app_definitions", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{organization_id}/app_definitions"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_app_definition")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_app_definition", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_app_definition",
        method="POST",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: App definitions
@mcp.tool()
async def get_app_definition(
    organization_id: str = Field(..., description="The unique identifier of the organization containing the app definition."),
    app_definition_id: str = Field(..., description="The unique identifier of the app definition to retrieve."),
) -> dict[str, Any]:
    """Retrieve a specific app definition by its ID within an organization. App definitions describe the configuration and metadata for apps installed in Contentful."""

    # Construct request model with validation
    try:
        _request = _models.GetOrganizationsByOrganizationIdAppDefinitionsByAppDefinitionIdRequest(
            path=_models.GetOrganizationsByOrganizationIdAppDefinitionsByAppDefinitionIdRequestPath(organization_id=organization_id, app_definition_id=app_definition_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_app_definition: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{organization_id}/app_definitions/{app_definition_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{organization_id}/app_definitions/{app_definition_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_app_definition")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_app_definition", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_app_definition",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: App definitions
@mcp.tool()
async def update_app_definition(
    organization_id: str = Field(..., description="The unique identifier of the organization that contains the app definition to be updated."),
    app_definition_id: str = Field(..., description="The unique identifier of the app definition to be updated."),
) -> dict[str, Any]:
    """Update an existing app definition within an organization. This allows you to modify the configuration and properties of a previously created app definition."""

    # Construct request model with validation
    try:
        _request = _models.PutOrganizationsAppDefinitionsRequest(
            path=_models.PutOrganizationsAppDefinitionsRequestPath(organization_id=organization_id, app_definition_id=app_definition_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_app_definition: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{organization_id}/app_definitions/{app_definition_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{organization_id}/app_definitions/{app_definition_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_app_definition")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_app_definition", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_app_definition",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: App definitions
@mcp.tool()
async def delete_app_definition(
    organization_id: str = Field(..., description="The unique identifier of the organization that contains the app definition to be deleted."),
    app_definition_id: str = Field(..., description="The unique identifier of the app definition to be deleted."),
) -> dict[str, Any]:
    """Permanently delete an app definition from an organization. This action cannot be undone and will remove the app definition and all associated configurations."""

    # Construct request model with validation
    try:
        _request = _models.DeleteOrganizationsAppDefinitionsRequest(
            path=_models.DeleteOrganizationsAppDefinitionsRequestPath(organization_id=organization_id, app_definition_id=app_definition_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_app_definition: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{organization_id}/app_definitions/{app_definition_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{organization_id}/app_definitions/{app_definition_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_app_definition")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_app_definition", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_app_definition",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: App uploads
@mcp.tool()
async def get_app_upload(
    organization_id: str = Field(..., description="The unique identifier of the organization that owns the app upload."),
    app_upload_id: str = Field(..., description="The unique identifier of the app upload to retrieve."),
) -> dict[str, Any]:
    """Retrieve details of a specific app upload within an organization. This returns metadata and status information about a previously uploaded app package."""

    # Construct request model with validation
    try:
        _request = _models.GetOrganizationsAppUploadsRequest(
            path=_models.GetOrganizationsAppUploadsRequestPath(organization_id=organization_id, app_upload_id=app_upload_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_app_upload: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{organization_id}/app_uploads/{app_upload_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{organization_id}/app_uploads/{app_upload_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_app_upload")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_app_upload", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_app_upload",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: App uploads
@mcp.tool()
async def create_app_upload(
    organization_id: str = Field(..., description="The unique identifier of the organization where the app upload will be created."),
    app_upload_id: str = Field(..., description="The unique identifier of the app upload resource to be created."),
) -> dict[str, Any]:
    """Create a new app upload for an organization. This operation initializes an app upload resource that can be used to manage application bundles and assets."""

    # Construct request model with validation
    try:
        _request = _models.PostOrganizationsAppUploadsRequest(
            path=_models.PostOrganizationsAppUploadsRequestPath(organization_id=organization_id, app_upload_id=app_upload_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_app_upload: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{organization_id}/app_uploads/{app_upload_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{organization_id}/app_uploads/{app_upload_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_app_upload")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_app_upload", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_app_upload",
        method="POST",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: App bundles
@mcp.tool()
async def list_app_bundles(
    organization_id: str = Field(..., description="The unique identifier of the organization containing the app definition."),
    app_definition_id: str = Field(..., description="The unique identifier of the app definition for which to retrieve associated app bundles."),
) -> dict[str, Any]:
    """Retrieve all app bundles associated with a specific app definition within an organization. App bundles are collections of app configuration and resources."""

    # Construct request model with validation
    try:
        _request = _models.GetOrganizationsByOrganizationIdAppDefinitionsByAppDefinitionIdAppBundlesRequest(
            path=_models.GetOrganizationsByOrganizationIdAppDefinitionsByAppDefinitionIdAppBundlesRequestPath(organization_id=organization_id, app_definition_id=app_definition_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_app_bundles: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{organization_id}/app_definitions/{app_definition_id}/app_bundles", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{organization_id}/app_definitions/{app_definition_id}/app_bundles"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_app_bundles")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_app_bundles", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_app_bundles",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: App bundles
@mcp.tool()
async def create_app_bundle(
    organization_id: str = Field(..., description="The unique identifier of the organization that owns the app definition."),
    app_definition_id: str = Field(..., description="The unique identifier of the app definition under which the app bundle will be created."),
) -> dict[str, Any]:
    """Create a new app bundle within an organization's app definition. App bundles package application code and configuration for deployment."""

    # Construct request model with validation
    try:
        _request = _models.PostOrganizationsAppDefinitionsAppBundlesRequest(
            path=_models.PostOrganizationsAppDefinitionsAppBundlesRequestPath(organization_id=organization_id, app_definition_id=app_definition_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_app_bundle: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{organization_id}/app_definitions/{app_definition_id}/app_bundles", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{organization_id}/app_definitions/{app_definition_id}/app_bundles"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_app_bundle")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_app_bundle", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_app_bundle",
        method="POST",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: App bundles
@mcp.tool()
async def get_app_bundle(
    organization_id: str = Field(..., description="The unique identifier of the organization that contains the app definition and app bundle."),
    app_definition_id: str = Field(..., description="The unique identifier of the app definition that contains the app bundle."),
    app_bundle_id: str = Field(..., description="The unique identifier of the app bundle to retrieve."),
) -> dict[str, Any]:
    """Retrieve a specific app bundle within an app definition. This returns the configuration and metadata for a single app bundle identified by its ID."""

    # Construct request model with validation
    try:
        _request = _models.GetOrganizationsByOrganizationIdAppDefinitionsByAppDefinitionIdAppBundlesByAppBundleIdRequest(
            path=_models.GetOrganizationsByOrganizationIdAppDefinitionsByAppDefinitionIdAppBundlesByAppBundleIdRequestPath(organization_id=organization_id, app_definition_id=app_definition_id, app_bundle_id=app_bundle_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_app_bundle: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{organization_id}/app_definitions/{app_definition_id}/app_bundles/{app_bundle_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{organization_id}/app_definitions/{app_definition_id}/app_bundles/{app_bundle_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_app_bundle")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_app_bundle", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_app_bundle",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: App bundles
@mcp.tool()
async def delete_app_bundle(
    organization_id: str = Field(..., description="The unique identifier of the organization that contains the app definition."),
    app_definition_id: str = Field(..., description="The unique identifier of the app definition that contains the app bundle to be deleted."),
    app_bundle_id: str = Field(..., description="The unique identifier of the app bundle to delete."),
) -> dict[str, Any]:
    """Permanently delete an app bundle from an app definition within an organization. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteOrganizationsAppDefinitionsAppBundlesRequest(
            path=_models.DeleteOrganizationsAppDefinitionsAppBundlesRequestPath(organization_id=organization_id, app_definition_id=app_definition_id, app_bundle_id=app_bundle_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_app_bundle: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{organization_id}/app_definitions/{app_definition_id}/app_bundles/{app_bundle_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{organization_id}/app_definitions/{app_definition_id}/app_bundles/{app_bundle_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_app_bundle")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_app_bundle", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_app_bundle",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: App event subscriptions
@mcp.tool()
async def get_app_event_subscription(
    organization_id: str = Field(..., description="The unique identifier of the organization that owns the app definition."),
    app_definition_id: str = Field(..., description="The unique identifier of the app definition whose event subscription configuration you want to retrieve."),
) -> dict[str, Any]:
    """Retrieve the event subscription configuration for a specific app definition within an organization. This returns the webhook and event settings that determine which events trigger notifications for the app."""

    # Construct request model with validation
    try:
        _request = _models.GetOrganizationsAppDefinitionsEventSubscriptionRequest(
            path=_models.GetOrganizationsAppDefinitionsEventSubscriptionRequestPath(organization_id=organization_id, app_definition_id=app_definition_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_app_event_subscription: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{organization_id}/app_definitions/{app_definition_id}/event_subscription", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{organization_id}/app_definitions/{app_definition_id}/event_subscription"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_app_event_subscription")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_app_event_subscription", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_app_event_subscription",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: App event subscriptions
@mcp.tool()
async def update_app_event_subscription(
    organization_id: str = Field(..., description="The unique identifier of the organization that owns the app definition."),
    app_definition_id: str = Field(..., description="The unique identifier of the app definition for which to update the event subscription."),
) -> dict[str, Any]:
    """Update or create an event subscription for an app definition, enabling the app to receive notifications for specified events within an organization."""

    # Construct request model with validation
    try:
        _request = _models.PutOrganizationsAppDefinitionsEventSubscriptionRequest(
            path=_models.PutOrganizationsAppDefinitionsEventSubscriptionRequestPath(organization_id=organization_id, app_definition_id=app_definition_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_app_event_subscription: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{organization_id}/app_definitions/{app_definition_id}/event_subscription", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{organization_id}/app_definitions/{app_definition_id}/event_subscription"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_app_event_subscription")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_app_event_subscription", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_app_event_subscription",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: App event subscriptions
@mcp.tool()
async def delete_app_event_subscription(
    organization_id: str = Field(..., description="The unique identifier of the organization that owns the app definition."),
    app_definition_id: str = Field(..., description="The unique identifier of the app definition from which to remove the event subscription."),
) -> dict[str, Any]:
    """Remove an event subscription from an app definition. This prevents the app from receiving event notifications for the specified app definition."""

    # Construct request model with validation
    try:
        _request = _models.DeleteOrganizationsAppDefinitionsEventSubscriptionRequest(
            path=_models.DeleteOrganizationsAppDefinitionsEventSubscriptionRequestPath(organization_id=organization_id, app_definition_id=app_definition_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_app_event_subscription: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{organization_id}/app_definitions/{app_definition_id}/event_subscription", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{organization_id}/app_definitions/{app_definition_id}/event_subscription"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_app_event_subscription")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_app_event_subscription", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_app_event_subscription",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: App signing secret
@mcp.tool()
async def get_app_signing_secret(
    organization_id: str = Field(..., description="The unique identifier of the organization that owns the app definition."),
    app_definition_id: str = Field(..., description="The unique identifier of the app definition for which to retrieve the signing secret."),
) -> dict[str, Any]:
    """Retrieve the current cryptographic signing secret for an app definition. This secret is used to verify the authenticity of requests from Contentful to your app."""

    # Construct request model with validation
    try:
        _request = _models.GetOrganizationsAppDefinitionsSigningSecretRequest(
            path=_models.GetOrganizationsAppDefinitionsSigningSecretRequestPath(organization_id=organization_id, app_definition_id=app_definition_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_app_signing_secret: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{organization_id}/app_definitions/{app_definition_id}/signing_secret", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{organization_id}/app_definitions/{app_definition_id}/signing_secret"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_app_signing_secret")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_app_signing_secret", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_app_signing_secret",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: App signing secret
@mcp.tool()
async def set_app_signing_secret(
    organization_id: str = Field(..., description="The unique identifier of the organization that owns the app definition."),
    app_definition_id: str = Field(..., description="The unique identifier of the app definition for which to set the signing secret."),
) -> dict[str, Any]:
    """Create or overwrite the signing secret for an app definition. This secret is used to verify the authenticity of requests from Contentful to your app."""

    # Construct request model with validation
    try:
        _request = _models.PutOrganizationsAppDefinitionsSigningSecretRequest(
            path=_models.PutOrganizationsAppDefinitionsSigningSecretRequestPath(organization_id=organization_id, app_definition_id=app_definition_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for set_app_signing_secret: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{organization_id}/app_definitions/{app_definition_id}/signing_secret", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{organization_id}/app_definitions/{app_definition_id}/signing_secret"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("set_app_signing_secret")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("set_app_signing_secret", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="set_app_signing_secret",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: App signing secret
@mcp.tool()
async def revoke_app_signing_secret(
    organization_id: str = Field(..., description="The unique identifier of the organization that owns the app definition."),
    app_definition_id: str = Field(..., description="The unique identifier of the app definition whose signing secret should be revoked."),
) -> dict[str, Any]:
    """Revoke and remove the current signing secret for an app definition. This invalidates the existing secret, requiring a new one to be generated for future app authentications."""

    # Construct request model with validation
    try:
        _request = _models.DeleteOrganizationsAppDefinitionsSigningSecretRequest(
            path=_models.DeleteOrganizationsAppDefinitionsSigningSecretRequestPath(organization_id=organization_id, app_definition_id=app_definition_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for revoke_app_signing_secret: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{organization_id}/app_definitions/{app_definition_id}/signing_secret", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{organization_id}/app_definitions/{app_definition_id}/signing_secret"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("revoke_app_signing_secret")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("revoke_app_signing_secret", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="revoke_app_signing_secret",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: App signed request
@mcp.tool()
async def create_app_signed_request(
    organization_id: str = Field(..., description="The unique identifier of the organization that owns the app installation."),
    app_definition_id: str = Field(..., description="The unique identifier of the app definition for which to create the signed request."),
) -> dict[str, Any]:
    """Generate a signed request for an app installation within an organization. This is used to authenticate and authorize app operations in Contentful."""

    # Construct request model with validation
    try:
        _request = _models.PostOrganizationsAppInstallationsSignedRequest(
            path=_models.PostOrganizationsAppInstallationsSignedRequestPath(organization_id=organization_id, app_definition_id=app_definition_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_app_signed_request: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{organization_id}/app_installations/{app_definition_id}/signed_request", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{organization_id}/app_installations/{app_definition_id}/signed_request"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_app_signed_request")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_app_signed_request", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_app_signed_request",
        method="POST",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: App keys
@mcp.tool()
async def list_app_keys(
    organization_id: str = Field(..., description="The unique identifier of the organization that contains the app definition."),
    app_definition_id: str = Field(..., description="The unique identifier of the app definition for which to retrieve all associated API keys."),
) -> dict[str, Any]:
    """Retrieve all API keys associated with a specific app definition within an organization. This allows you to manage and view the credentials used for app authentication."""

    # Construct request model with validation
    try:
        _request = _models.GetOrganizationsByOrganizationIdAppDefinitionsByAppDefinitionIdKeysRequest(
            path=_models.GetOrganizationsByOrganizationIdAppDefinitionsByAppDefinitionIdKeysRequestPath(organization_id=organization_id, app_definition_id=app_definition_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_app_keys: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{organization_id}/app_definitions/{app_definition_id}/keys", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{organization_id}/app_definitions/{app_definition_id}/keys"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_app_keys")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_app_keys", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_app_keys",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: App keys
@mcp.tool()
async def create_app_key(
    organization_id: str = Field(..., description="The unique identifier of the organization that owns the app definition."),
    app_definition_id: str = Field(..., description="The unique identifier of the app definition for which to create the new key."),
) -> dict[str, Any]:
    """Create a new API key for an app definition within an organization. This key can be used to authenticate requests on behalf of the app."""

    # Construct request model with validation
    try:
        _request = _models.PostOrganizationsAppDefinitionsKeysRequest(
            path=_models.PostOrganizationsAppDefinitionsKeysRequestPath(organization_id=organization_id, app_definition_id=app_definition_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_app_key: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{organization_id}/app_definitions/{app_definition_id}/keys", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{organization_id}/app_definitions/{app_definition_id}/keys"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_app_key")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_app_key", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_app_key",
        method="POST",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: App keys
@mcp.tool()
async def get_app_key(
    organization_id: str = Field(..., description="The unique identifier of the organization that owns the app definition."),
    app_definition_id: str = Field(..., description="The unique identifier of the app definition containing the key."),
    key_kid: str = Field(..., description="The unique identifier (kid) of the specific key to retrieve."),
) -> dict[str, Any]:
    """Retrieve a specific cryptographic key associated with an app definition. This key is used for secure communication and authentication with the app."""

    # Construct request model with validation
    try:
        _request = _models.GetOrganizationsByOrganizationIdAppDefinitionsByAppDefinitionIdKeysByKeyKidRequest(
            path=_models.GetOrganizationsByOrganizationIdAppDefinitionsByAppDefinitionIdKeysByKeyKidRequestPath(organization_id=organization_id, app_definition_id=app_definition_id, key_kid=key_kid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_app_key: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{organization_id}/app_definitions/{app_definition_id}/keys/{key_kid}", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{organization_id}/app_definitions/{app_definition_id}/keys/{key_kid}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_app_key")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_app_key", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_app_key",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: App keys
@mcp.tool()
async def delete_app_key(
    organization_id: str = Field(..., description="The unique identifier of the organization that owns the app definition."),
    app_definition_id: str = Field(..., description="The unique identifier of the app definition containing the key to be deleted."),
    key_kid: str = Field(..., description="The unique identifier (kid) of the specific key to delete from the app definition."),
) -> dict[str, Any]:
    """Delete a specific cryptographic key associated with an app definition. This removes the key from the app definition, preventing it from being used for authentication or signing operations."""

    # Construct request model with validation
    try:
        _request = _models.DeleteOrganizationsAppDefinitionsKeysRequest(
            path=_models.DeleteOrganizationsAppDefinitionsKeysRequestPath(organization_id=organization_id, app_definition_id=app_definition_id, key_kid=key_kid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_app_key: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{organization_id}/app_definitions/{app_definition_id}/keys/{key_kid}", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{organization_id}/app_definitions/{app_definition_id}/keys/{key_kid}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_app_key")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_app_key", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_app_key",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: App Installations
@mcp.tool()
async def list_app_installations(
    space_id: str = Field(..., description="The unique identifier of the space containing the environment and app installations."),
    environment_id: str = Field(..., description="The unique identifier of the environment within the space for which to retrieve app installations."),
) -> dict[str, Any]:
    """Retrieve all app installations configured for a specific environment within a space. This returns the complete list of installed applications and their configurations."""

    # Construct request model with validation
    try:
        _request = _models.GetSpacesBySpaceIdEnvironmentsByEnvironmentIdAppInstallationsRequest(
            path=_models.GetSpacesBySpaceIdEnvironmentsByEnvironmentIdAppInstallationsRequestPath(space_id=space_id, environment_id=environment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_app_installations: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}/app_installations", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}/app_installations"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_app_installations")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_app_installations", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_app_installations",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: App Installations
@mcp.tool()
async def get_app_installation(
    space_id: str = Field(..., description="The unique identifier of the space containing the app installation."),
    environment_id: str = Field(..., description="The unique identifier of the environment within the space where the app is installed."),
    app_definition_id: str = Field(..., description="The unique identifier of the app definition for which to retrieve the installation details."),
) -> dict[str, Any]:
    """Retrieve a specific app installation configuration for an app within a given space and environment. This returns the installation details and settings for the specified app definition."""

    # Construct request model with validation
    try:
        _request = _models.GetSpacesBySpaceIdEnvironmentsByEnvironmentIdAppInstallationsByAppDefinitionIdRequest(
            path=_models.GetSpacesBySpaceIdEnvironmentsByEnvironmentIdAppInstallationsByAppDefinitionIdRequestPath(space_id=space_id, environment_id=environment_id, app_definition_id=app_definition_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_app_installation: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}/app_installations/{app_definition_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}/app_installations/{app_definition_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_app_installation")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_app_installation", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_app_installation",
        method="GET",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: App Installations
@mcp.tool()
async def install_app(
    space_id: str = Field(..., description="The unique identifier of the Contentful space where the app will be installed or updated."),
    environment_id: str = Field(..., description="The unique identifier of the environment within the space where the app installation will be managed."),
    app_definition_id: str = Field(..., description="The unique identifier of the app definition to install or update."),
) -> dict[str, Any]:
    """Install a new app or update an existing app installation in a specific environment. This operation manages app configurations within a Contentful space and environment."""

    # Construct request model with validation
    try:
        _request = _models.PutSpacesEnvironmentsAppInstallationsRequest(
            path=_models.PutSpacesEnvironmentsAppInstallationsRequestPath(space_id=space_id, environment_id=environment_id, app_definition_id=app_definition_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for install_app: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}/app_installations/{app_definition_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}/app_installations/{app_definition_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("install_app")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("install_app", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="install_app",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: App Installations
@mcp.tool()
async def uninstall_app(
    space_id: str = Field(..., description="The unique identifier of the space containing the environment where the app is installed."),
    environment_id: str = Field(..., description="The unique identifier of the environment from which the app will be uninstalled."),
    app_definition_id: str = Field(..., description="The unique identifier of the app definition to uninstall."),
) -> dict[str, Any]:
    """Remove an installed app from a specific environment within a space. This operation permanently uninstalls the app and removes its access to the environment."""

    # Construct request model with validation
    try:
        _request = _models.DeleteSpacesEnvironmentsAppInstallationsRequest(
            path=_models.DeleteSpacesEnvironmentsAppInstallationsRequestPath(space_id=space_id, environment_id=environment_id, app_definition_id=app_definition_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for uninstall_app: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}/app_installations/{app_definition_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}/app_installations/{app_definition_id}"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("uninstall_app")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("uninstall_app", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="uninstall_app",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: App access token
@mcp.tool()
async def issue_app_installation_access_token(
    space_id: str = Field(..., description="The unique identifier of the space containing the app installation."),
    environment_id: str = Field(..., description="The unique identifier of the environment within the space where the app is installed."),
    app_definition_id: str = Field(..., description="The unique identifier of the app definition for which to issue an access token."),
) -> dict[str, Any]:
    """Generate an access token for an app installation within a specific space environment. This token enables the app to authenticate and interact with Contentful APIs on behalf of the installation."""

    # Construct request model with validation
    try:
        _request = _models.PostSpacesEnvironmentsAppInstallationsAccessTokensRequest(
            path=_models.PostSpacesEnvironmentsAppInstallationsAccessTokensRequestPath(space_id=space_id, environment_id=environment_id, app_definition_id=app_definition_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for issue_app_installation_access_token: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/spaces/{space_id}/environments/{environment_id}/app_installations/{app_definition_id}/access_tokens", _request.path.model_dump(by_alias=True)) if _request.path else "/spaces/{space_id}/environments/{environment_id}/app_installations/{app_definition_id}/access_tokens"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("issue_app_installation_access_token")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("issue_app_installation_access_token", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="issue_app_installation_access_token",
        method="POST",
        path=_http_path,
        request_id=_request_id,
    )

    return _response_data

# Tags: Usage
@mcp.tool()
async def list_organization_usage_metrics(
    organization_id: str = Field(..., description="The unique identifier of the organization for which to retrieve usage data."),
    order: str | None = Field(None, description="Field to sort results by, such as usage metrics. Determines the order of returned usage records."),
    metric_in: str | None = Field(None, alias="metricin", description="Comma-separated list of metric types to include in the results, such as Content Management API (cma), Content Preview API (cpa), or GraphQL (gql) usage."),
    date_range_start_at: str | None = Field(None, alias="dateRange.startAt", description="Start date for the usage period in ISO 8601 format (YYYY-MM-DD). Defines the beginning of the date range for usage data retrieval."),
    date_range_end_at: str | None = Field(None, alias="dateRange.endAt", description="End date for the usage period in ISO 8601 format (YYYY-MM-DD). Defines the end of the date range for usage data retrieval."),
) -> dict[str, Any]:
    """Retrieve periodic usage metrics for an organization, including API calls and resource consumption across specified time periods and metric types."""

    # Construct request model with validation
    try:
        _request = _models.GetOrganizationsOrganizationPeriodicUsagesRequest(
            path=_models.GetOrganizationsOrganizationPeriodicUsagesRequestPath(organization_id=organization_id),
            query=_models.GetOrganizationsOrganizationPeriodicUsagesRequestQuery(order=order, metric_in=metric_in, date_range_start_at=date_range_start_at, date_range_end_at=date_range_end_at)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_organization_usage_metrics: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{organization_id}/organization_periodic_usages", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{organization_id}/organization_periodic_usages"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_organization_usage_metrics")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_organization_usage_metrics", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_organization_usage_metrics",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Usage
@mcp.tool()
async def list_space_periodic_usages(
    organization_id: str = Field(..., description="The unique identifier of the organization for which to retrieve space usage data."),
    order: str | None = Field(None, description="Field to sort results by, such as usage metrics. Determines the order in which usage records are returned."),
    metric_in: str | None = Field(None, alias="metricin", description="Comma-separated list of metrics to include in the response, such as Content Management API (cma), Content Preview API (cpa), or GraphQL (gql) usage."),
    date_range_start_at: str | None = Field(None, alias="dateRange.startAt", description="Start date for the usage period in ISO 8601 format (YYYY-MM-DD). Usage data will be retrieved from this date onwards."),
    date_range_end_at: str | None = Field(None, alias="dateRange.endAt", description="End date for the usage period in ISO 8601 format (YYYY-MM-DD). Usage data will be retrieved up to and including this date."),
) -> dict[str, Any]:
    """Retrieve periodic space usage metrics for an organization, allowing you to track content delivery and API consumption patterns over a specified time range."""

    # Construct request model with validation
    try:
        _request = _models.GetOrganizationsSpacePeriodicUsagesRequest(
            path=_models.GetOrganizationsSpacePeriodicUsagesRequestPath(organization_id=organization_id),
            query=_models.GetOrganizationsSpacePeriodicUsagesRequestQuery(order=order, metric_in=metric_in, date_range_start_at=date_range_start_at, date_range_end_at=date_range_end_at)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_space_periodic_usages: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{organization_id}/space_periodic_usages", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{organization_id}/space_periodic_usages"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_space_periodic_usages")

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_space_periodic_usages", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_space_periodic_usages",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
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
        print("  python cma___contentful_management_api_server.py", file=sys.stderr)
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

    parser = argparse.ArgumentParser(description="CMA - Contentful Management API MCP Server")

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
    logger.info("Starting CMA - Contentful Management API MCP Server")
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

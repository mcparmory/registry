#!/usr/bin/env python3
"""
Apollo REST API MCP Server
Generated: 2026-04-06 15:44:00 UTC
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

BASE_URL = os.getenv("BASE_URL", "https://api.apollo.io")
SERVER_NAME = "Apollo REST API"
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
            cookies=None  # Disable cookie persistence for multi-tenant safety
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

def parse_sort(value: str | None = None) -> dict | None:
    """Helper function for parameter transformation"""
    if value is None:
        return None
    if ':' not in value:
        raise ValueError('Sort specification must be in format "field:direction"') from None
    parts = value.split(':')
    if len(parts) != 2:
        raise ValueError('Sort specification must contain exactly one colon') from None
    field, direction = parts
    direction_lower = direction.lower().strip()
    if direction_lower not in ('asc', 'desc'):
        raise ValueError(f'Direction must be "asc" or "desc", got "{direction}"') from None
    return {'sort_by_field': field.strip(), 'sort_ascending': direction_lower == 'asc'}


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
    'apiKey',
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
    _auth_handlers["apiKey"] = _auth.APIKeyAuth(env_var="API_KEY", location="header", param_name="x-api-key")
    logging.info("Authentication configured: apiKey")
except ValueError as e:
    # Extract credential names from error message (first sentence before "Leave empty")
    error_msg = str(e).split("Leave empty")[0].strip()
    logging.warning(f"Credentials for apiKey not configured: {error_msg}")
    _auth_handlers["apiKey"] = None

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

mcp = FastMCP("Apollo REST API", middleware=[_JsonCoercionMiddleware()])

# Tags: Enrichment
@mcp.tool()
async def enrich_person(
    name: str | None = Field(None, description="The person's full name, typically first and last name separated by a space. Use this as an alternative to providing separate first_name and last_name parameters."),
    hashed_email: str | None = Field(None, description="The hashed email address of the person in MD5 or SHA-256 format. Use this to match against the database when you have a hashed email available."),
    domain: str | None = Field(None, description="The domain name of the person's employer (current or previous). Provide only the domain without www, @, or other prefixes (e.g., apollo.io)."),
    id_: str | None = Field(None, alias="id", description="The unique Apollo ID assigned to the person in the database. Use this when you already have the Apollo identifier for direct lookup."),
    linkedin_url: str | None = Field(None, description="The URL to the person's LinkedIn profile. Provide the full profile URL to help identify and enrich the correct person."),
    run_waterfall_email: bool | None = Field(None, description="Enable email waterfall enrichment to discover additional email addresses beyond standard matching. Set to true to activate this enrichment method."),
    run_waterfall_phone: bool | None = Field(None, description="Enable phone waterfall enrichment to discover additional phone numbers beyond standard matching. Set to true to activate this enrichment method."),
    reveal_personal_emails: bool | None = Field(None, description="Reveal the person's personal email addresses in the response. This may consume credits and will not return emails for individuals in GDPR-compliant regions. Set to true to include personal emails in enrichment results."),
    reveal_phone_number: bool | None = Field(None, description="Reveal all available phone numbers including mobile numbers in the response. This may consume credits and requires a webhook_url to be specified for asynchronous phone number verification results. Set to true to request phone number enrichment."),
    webhook_url: str | None = Field(None, description="The webhook URL where Apollo will send phone number verification results asynchronously. Required only when reveal_phone_number is set to true. Provide a valid HTTPS endpoint to receive the phone enrichment response."),
) -> dict[str, Any]:
    """Enrich data for a single person by matching against the Apollo database. Provide identifying information such as name, email, domain, or LinkedIn profile to locate and return enriched contact details. Optionally reveal personal emails and phone numbers, or enable waterfall enrichment for additional data discovery."""

    # Construct request model with validation
    try:
        _request = _models.PostApiV1PeopleMatchRequest(
            query=_models.PostApiV1PeopleMatchRequestQuery(name=name, hashed_email=hashed_email, domain=domain, id_=id_, linkedin_url=linkedin_url, run_waterfall_email=run_waterfall_email, run_waterfall_phone=run_waterfall_phone, reveal_personal_emails=reveal_personal_emails, reveal_phone_number=reveal_phone_number, webhook_url=webhook_url)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for enrich_person: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/people/match"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("enrich_person")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("enrich_person", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="enrich_person",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Enrichment
@mcp.tool()
async def enrich_people_bulk(
    details: list[dict[str, Any]] = Field(..., description="Array of up to 10 person objects containing identifying information (name, email, company, location, etc.) to match and enrich. Each object should include available details to improve match accuracy."),
    run_waterfall_email: bool | None = Field(None, description="Enable email waterfall enrichment to progressively search multiple data sources for email addresses when initial matches don't return results."),
    run_waterfall_phone: bool | None = Field(None, description="Enable phone waterfall enrichment to progressively search multiple data sources for phone numbers when initial matches don't return results."),
    reveal_personal_emails: bool | None = Field(None, description="Include personal email addresses in enriched results for all matched people. This may consume credits based on your plan. Personal emails will not be revealed for people in GDPR-compliant regions."),
    reveal_phone_number: bool | None = Field(None, description="Include all available phone numbers (including mobile) in enriched results for matched people. Requires a valid webhook_url to receive asynchronous phone verification results."),
    webhook_url: str | None = Field(None, description="Webhook endpoint URL where Apollo will send phone number verification results asynchronously. Required when reveal_phone_number is enabled. Must be a valid HTTPS or HTTP URI."),
) -> dict[str, Any]:
    """Enrich contact and professional data for up to 10 people in a single request. Apollo uses the provided person details to identify and match records, then returns enriched information with optional email, phone, and waterfall verification."""

    # Construct request model with validation
    try:
        _request = _models.PostApiV1PeopleBulkMatchRequest(
            query=_models.PostApiV1PeopleBulkMatchRequestQuery(run_waterfall_email=run_waterfall_email, run_waterfall_phone=run_waterfall_phone, reveal_personal_emails=reveal_personal_emails, reveal_phone_number=reveal_phone_number, webhook_url=webhook_url),
            body=_models.PostApiV1PeopleBulkMatchRequestBody(details=details)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for enrich_people_bulk: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/people/bulk_match"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("enrich_people_bulk")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("enrich_people_bulk", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="enrich_people_bulk",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Enrichment
@mcp.tool()
async def enrich_organization(domain: str = Field(..., description="The company domain to enrich (e.g., apollo.io). Provide the domain without www prefix, @ symbol, or other special characters.")) -> dict[str, Any]:
    """Enrich company data by domain to retrieve detailed organizational information including industry, revenue, employee counts, funding details, and contact information. Each call consumes credits from your Apollo pricing plan."""

    # Construct request model with validation
    try:
        _request = _models.GetApiV1OrganizationsEnrichRequest(
            query=_models.GetApiV1OrganizationsEnrichRequestQuery(domain=domain)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for enrich_organization: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/organizations/enrich"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("enrich_organization")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("enrich_organization", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="enrich_organization",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Enrichment
@mcp.tool()
async def enrich_organizations(domains: list[str] = Field(..., description="Array of company domains to enrich, up to 10 domains per request. Provide domains without www prefix, @ symbol, or other modifiers (e.g., apollo.io, microsoft.com).")) -> dict[str, Any]:
    """Enrich company data for up to 10 organizations in a single request. Returns enriched information including industry, revenue, employee count, funding details, phone numbers, and locations."""

    # Construct request model with validation
    try:
        _request = _models.PostApiV1OrganizationsBulkEnrichRequest(
            query=_models.PostApiV1OrganizationsBulkEnrichRequestQuery(domains=domains)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for enrich_organizations: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/organizations/bulk_enrich"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("enrich_organizations")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("enrich_organizations", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="enrich_organizations",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Search
@mcp.tool()
async def search_people(
    person_titles: list[str] | None = Field(None, description="Filter by job titles held by people. Results include titles containing the same terms, even if not exact matches."),
    q_keywords: str | None = Field(None, description="Filter results by keywords that appear in person profiles."),
    person_locations: list[str] | None = Field(None, description="Filter by the locations where people currently live, including cities, US states, and countries."),
    person_seniorities: list[Literal["owner", "founder", "c_suite", "partner", "vp", "head", "director", "manager", "senior", "entry", "intern"]] | None = Field(None, description="Filter by the seniority level of people's current job positions (e.g., entry-level, mid-level, executive)."),
    organization_locations: list[str] | None = Field(None, description="Filter by the headquarters location of people's current employers, including cities, US states, and countries."),
    q_organization_domains_list: list[str] | None = Field(None, description="Filter by employer domain names. Accepts up to 1,000 domains per request."),
    contact_email_status: list[Literal["verified", "unverified", "likely to engage", "unavailable"]] | None = Field(None, description="Filter by email verification status of people (e.g., verified, unverified, bounced)."),
    organization_ids: list[str] | None = Field(None, description="Filter by Apollo organization IDs to include only people employed at specific companies."),
    organization_num_employees_ranges: list[str] | None = Field(None, description="Filter by employee count ranges of people's current employers. Specify as comma-separated lower and upper bounds (e.g., '1,10' for 1-10 employees)."),
    currently_using_all_of_technology_uids: list[str] | None = Field(None, description="Filter by people whose employers use all of the specified technologies. Supports 1,500+ technology identifiers."),
    currently_using_any_of_technology_uids: list[str] | None = Field(None, description="Filter by people whose employers use any of the specified technologies. Supports 1,500+ technology identifiers."),
    currently_not_using_any_of_technology_uids: list[str] | None = Field(None, description="Exclude people whose employers use any of the specified technologies. Supports 1,500+ technology identifiers."),
    q_organization_job_titles: list[str] | None = Field(None, description="Filter by job titles listed in active job postings at people's current employers."),
    organization_job_locations: list[str] | None = Field(None, description="Filter by locations where people's current employers are actively recruiting for open positions."),
) -> dict[str, Any]:
    """Search the Apollo database for people matching specified criteria such as job title, location, seniority, and employer technology stack. This API-optimized endpoint does not consume credits and returns up to 50,000 records without email addresses or phone numbers."""

    # Construct request model with validation
    try:
        _request = _models.PostApiV1MixedPeopleApiSearchRequest(
            query=_models.PostApiV1MixedPeopleApiSearchRequestQuery(person_titles=person_titles, q_keywords=q_keywords, person_locations=person_locations, person_seniorities=person_seniorities, organization_locations=organization_locations, q_organization_domains_list=q_organization_domains_list, contact_email_status=contact_email_status, organization_ids=organization_ids, organization_num_employees_ranges=organization_num_employees_ranges, currently_using_all_of_technology_uids=currently_using_all_of_technology_uids, currently_using_any_of_technology_uids=currently_using_any_of_technology_uids, currently_not_using_any_of_technology_uids=currently_not_using_any_of_technology_uids, q_organization_job_titles=q_organization_job_titles, organization_job_locations=organization_job_locations)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_people: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/mixed_people/api_search"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_people")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_people", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_people",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Search
@mcp.tool()
async def search_companies(
    q_organization_domains_list: list[str] | None = Field(None, description="Filter by company domain names (e.g., apollo.io, microsoft.com). Omit www, @, and similar prefixes. Accepts up to 1,000 domains per request to find companies by their current or previous employer domains."),
    organization_num_employees_ranges: list[str] | None = Field(None, description="Filter by company headcount ranges. Specify ranges as comma-separated pairs (e.g., 1,10 or 250,500). Add multiple ranges to broaden results and find companies within specific employee count brackets."),
    organization_locations: list[str] | None = Field(None, description="Filter by company headquarters location using city, US state, or country names. Results are based on headquarters location even if the company has multiple offices."),
    organization_not_locations: list[str] | None = Field(None, description="Exclude companies from results based on headquarters location. Specify cities, US states, or countries to filter out unwanted geographic regions."),
    currently_using_any_of_technology_uids: list[str] | None = Field(None, description="Filter by technologies currently in use at companies. Apollo supports 1,500+ technologies; use underscores to replace spaces and periods in technology names (e.g., google_analytics, wordpress_org)."),
    q_organization_keyword_tags: list[str] | None = Field(None, description="Filter by industry or business keywords associated with companies (e.g., mining, consulting). Enables targeted searches by company classification or sector."),
    q_organization_name: str | None = Field(None, description="Filter by specific company name. Partial name matches are supported to find companies with similar naming patterns."),
    organization_ids: list[str] | None = Field(None, description="Filter by Apollo's unique company identifiers. Provide one or more company IDs to retrieve specific organizations from the database."),
    q_organization_job_titles: list[str] | None = Field(None, description="Filter by job titles listed in active company job postings. Find companies actively recruiting for specific roles (e.g., sales manager, research analyst)."),
    organization_job_locations: list[str] | None = Field(None, description="Filter by geographic locations where companies are actively recruiting. Specify cities or countries to find organizations hiring in particular regions."),
) -> dict[str, Any]:
    """Search the Apollo database for companies using multiple filter criteria including domain, location, technology stack, and hiring activity. Results are paginated at 100 records per page (up to 500 pages, 50,000 record limit) and consume credits based on your Apollo plan."""

    # Construct request model with validation
    try:
        _request = _models.PostApiV1MixedCompaniesSearchRequest(
            query=_models.PostApiV1MixedCompaniesSearchRequestQuery(q_organization_domains_list=q_organization_domains_list, organization_num_employees_ranges=organization_num_employees_ranges, organization_locations=organization_locations, organization_not_locations=organization_not_locations, currently_using_any_of_technology_uids=currently_using_any_of_technology_uids, q_organization_keyword_tags=q_organization_keyword_tags, q_organization_name=q_organization_name, organization_ids=organization_ids, q_organization_job_titles=q_organization_job_titles, organization_job_locations=organization_job_locations)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_companies: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/mixed_companies/search"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_companies")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_companies", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_companies",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Search
@mcp.tool()
async def list_organization_job_postings(organization_id: str = Field(..., description="The unique identifier for the organization whose job postings you want to retrieve. You can find organization IDs by calling the Organization Search endpoint.")) -> dict[str, Any]:
    """Retrieve current job postings for a specific organization to identify companies expanding headcount in strategically important areas. This endpoint is useful for competitive intelligence and hiring trend analysis."""

    # Construct request model with validation
    try:
        _request = _models.GetApiV1OrganizationsOrganizationIdJobPostingsRequest(
            path=_models.GetApiV1OrganizationsOrganizationIdJobPostingsRequestPath(organization_id=organization_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_organization_job_postings: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/organizations/{organization_id}/job_postings", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/organizations/{organization_id}/job_postings"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_organization_job_postings")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_organization_job_postings", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_organization_job_postings",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Search
@mcp.tool()
async def get_organization(id_: str = Field(..., alias="id", description="The Apollo organization ID to retrieve details for. You can find organization IDs by calling the Organization Search endpoint and extracting the organization_id value from the results.")) -> dict[str, Any]:
    """Retrieve complete details about a specific organization from the Apollo database, including company information, contact data, and other organizational metadata. Requires a master API key for authentication."""

    # Construct request model with validation
    try:
        _request = _models.GetApiV1OrganizationsIdRequest(
            path=_models.GetApiV1OrganizationsIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_organization: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/organizations/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/organizations/{id}"
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

# Tags: Search
@mcp.tool()
async def search_company_news(
    organization_ids: list[str] = Field(..., description="One or more Apollo company IDs to search for news coverage. Retrieve company IDs from the Organization Search endpoint. Results will include news for all specified companies."),
    categories: list[str] | None = Field(None, description="Optional news categories or sub-categories to filter results (e.g., hires, investment, contract). When specified, only articles matching these categories are returned. Omit to include all available categories."),
) -> dict[str, Any]:
    """Search for news articles related to companies in the Apollo database. Filter results by company IDs and optionally by news categories to find relevant coverage. Note: This operation consumes credits from your Apollo plan."""

    # Construct request model with validation
    try:
        _request = _models.PostApiV1NewsArticlesSearchRequest(
            query=_models.PostApiV1NewsArticlesSearchRequestQuery(organization_ids=organization_ids, categories=categories)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_company_news: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/news_articles/search"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_company_news")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_company_news", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_company_news",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Accounts
@mcp.tool()
async def create_account(
    name: str = Field(..., description="The human-readable name of the account/company you are creating."),
    domain: str = Field(..., description="The domain name for the account, without www or similar prefixes (e.g., apollo.io)."),
    owner_id: str | None = Field(None, description="The Apollo user ID of the team member who will own this account."),
    account_stage_id: str | None = Field(None, description="The Apollo ID of the account stage (pipeline status) to assign to this account."),
    phone: str | None = Field(None, description="The primary phone number for the account. Apollo automatically formats phone numbers regardless of input format."),
    raw_address: str | None = Field(None, description="The corporate headquarters location for the account, which may include city, state, and country."),
    typed_custom_fields: dict[str, Any] | None = Field(None, description="Custom field values specific to your team's Apollo account, provided as key-value pairs where keys are custom field IDs and values are the field data."),
) -> dict[str, Any]:
    """Create a new account (company) in your Apollo team database. Note that Apollo does not deduplicate accounts, so creating an account with the same name, domain, or details as an existing account will result in a duplicate entry rather than an update. Requires a master API key."""

    # Construct request model with validation
    try:
        _request = _models.PostApiV1AccountsRequest(
            body=_models.PostApiV1AccountsRequestBody(name=name, domain=domain, owner_id=owner_id, account_stage_id=account_stage_id, phone=phone, raw_address=raw_address, typed_custom_fields=typed_custom_fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_account: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/accounts"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_account")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_account", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_account",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Accounts
@mcp.tool()
async def update_account(
    account_id: str = Field(..., description="The unique Apollo identifier for the account to update."),
    name: str | None = Field(None, description="A human-readable name for the account (e.g., 'The Fast Irish Copywriters')."),
    domain: str | None = Field(None, description="The domain name associated with the account, without www or protocol prefix (e.g., 'apollo.io' or 'microsoft.com')."),
    owner_id: str | None = Field(None, description="The Apollo ID of the team member who owns this account."),
    account_stage_id: str | None = Field(None, description="The Apollo ID of the account stage to assign to this account, determining its position in your sales pipeline."),
    raw_address: str | None = Field(None, description="The corporate headquarters location or primary office address (e.g., 'Belfield, Dublin 4, Ireland' or 'Dallas, United States')."),
    phone: str | None = Field(None, description="The primary contact phone number for the account in any standard format (e.g., '555-303-1234' or '+44 7911 123456')."),
    typed_custom_fields: dict[str, Any] | None = Field(None, description="Custom field values specific to your Apollo workspace. Structure as key-value pairs where keys match your configured custom field names."),
) -> dict[str, Any]:
    """Update an existing account in your Apollo workspace. Requires a master API key and the account ID. You can modify account details such as name, domain, owner, stage, location, phone, and custom fields."""

    # Construct request model with validation
    try:
        _request = _models.PatchApiV1AccountsAccountIdRequest(
            path=_models.PatchApiV1AccountsAccountIdRequestPath(account_id=account_id),
            body=_models.PatchApiV1AccountsAccountIdRequestBody(name=name, domain=domain, owner_id=owner_id, account_stage_id=account_stage_id, raw_address=raw_address, phone=phone, typed_custom_fields=typed_custom_fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_account: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/accounts/{account_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/accounts/{account_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_account")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_account", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_account",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Accounts
@mcp.tool()
async def bulk_create_accounts(
    accounts: list[_models.PostApiV1AccountsBulkCreateBodyAccountsItem] = Field(..., description="Array of account objects to create, up to 100 accounts per request. Each object should contain the account attributes you want to set."),
    append_label_names: list[str] | None = Field(None, description="Optional array of label names to apply to all accounts created in this request."),
    run_dedupe: bool | None = Field(None, description="Enable aggressive deduplication matching by domain, organization_id, and name in addition to CRM IDs. When disabled (default), only CRM ID matching is used. Existing accounts are returned without modification regardless of this setting."),
) -> dict[str, Any]:
    """Create up to 100 accounts in a single request with intelligent deduplication. The endpoint returns newly created accounts and existing matches separately without modifying existing accounts."""

    # Construct request model with validation
    try:
        _request = _models.PostApiV1AccountsBulkCreateRequest(
            body=_models.PostApiV1AccountsBulkCreateRequestBody(accounts=accounts, append_label_names=append_label_names, run_dedupe=run_dedupe)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for bulk_create_accounts: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/accounts/bulk_create"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("bulk_create_accounts")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("bulk_create_accounts", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="bulk_create_accounts",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Accounts
@mcp.tool()
async def bulk_update_accounts(
    account_ids: list[str] | None = Field(None, description="List of account IDs to update with identical values. Use this when applying the same changes across multiple accounts. Required if account_attributes is not provided."),
    account_attributes: list[dict[str, Any]] | None = Field(None, description="List of account objects, each containing an ID and the specific fields to update for that account. Use this for applying different updates to individual accounts. Required if account_ids is not provided. Not compatible with async processing."),
    name: str | None = Field(None, description="New name to assign to all accounts when using account_ids. Ignored when using account_attributes."),
    owner_id: str | None = Field(None, description="Owner ID to assign to all accounts when using account_ids. Ignored when using account_attributes."),
    account_stage_id: str | None = Field(None, description="Account stage ID to assign to all accounts when using account_ids. Ignored when using account_attributes."),
    async_: bool | None = Field(None, alias="async", description="Enable asynchronous processing for the bulk update. Only available when using account_ids with uniform updates; will fail if used with account_attributes. Defaults to false for synchronous processing."),
) -> dict[str, Any]:
    """Update multiple accounts simultaneously with common or individual field changes. Supports updating up to 1000 accounts per request, with optional asynchronous processing when applying uniform updates."""

    # Construct request model with validation
    try:
        _request = _models.PostApiV1AccountsBulkUpdateRequest(
            body=_models.PostApiV1AccountsBulkUpdateRequestBody(account_ids=account_ids, account_attributes=account_attributes, name=name, owner_id=owner_id, account_stage_id=account_stage_id, async_=async_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for bulk_update_accounts: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/accounts/bulk_update"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("bulk_update_accounts")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("bulk_update_accounts", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="bulk_update_accounts",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Accounts
@mcp.tool()
async def search_accounts(
    q_organization_name: str | None = Field(None, description="Keywords to filter accounts by name. The search matches keywords against account names, supporting partial matches. Examples include company names like 'apollo', 'microsoft', or 'marketing'."),
    account_stage_ids: list[str] | None = Field(None, description="Apollo IDs of account stages to include in results. Provide as an array of stage IDs to filter accounts by their current stage."),
    account_label_ids: list[str] | None = Field(None, description="Apollo IDs of labels to include in results. Provide as an array of label IDs to filter accounts by their assigned labels."),
    sort_by_field: Literal["account_last_activity_date", "account_created_at", "account_updated_at"] | None = Field(None, description="Field to sort results by. Choose from account activity date, creation date, or last update date."),
    sort_ascending: bool | None = Field(None, description="Sort results in ascending order. Only applies when sort_by_field is specified. Defaults to descending order when not provided."),
) -> dict[str, Any]:
    """Search for accounts that have been added to your team's Apollo database. Filter by name, stage, labels, and sort results by activity or creation date. Results are paginated with a maximum of 50,000 records (100 per page)."""

    # Construct request model with validation
    try:
        _request = _models.PostApiV1AccountsSearchRequest(
            body=_models.PostApiV1AccountsSearchRequestBody(q_organization_name=q_organization_name, account_stage_ids=account_stage_ids, account_label_ids=account_label_ids, sort_by_field=sort_by_field, sort_ascending=sort_ascending)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_accounts: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/accounts/search"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_accounts")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_accounts", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_accounts",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Accounts
@mcp.tool()
async def get_account(id_: str = Field(..., alias="id", description="The Apollo ID of the account to retrieve. You can find account IDs by calling the Search for Accounts endpoint.")) -> dict[str, Any]:
    """Retrieve detailed information for a specific account (company) in your Apollo database. Requires a master API key."""

    # Construct request model with validation
    try:
        _request = _models.GetApiV1AccountsIdRequest(
            path=_models.GetApiV1AccountsIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_account: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/accounts/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/accounts/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_account")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_account", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_account",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Accounts
@mcp.tool()
async def assign_accounts_to_owner(
    account_ids: list[str] = Field(..., description="Array of Apollo account IDs to reassign to the new owner. Retrieve account IDs from the Search for Accounts endpoint. Each ID should be a valid Apollo account identifier."),
    owner_id: str = Field(..., description="The Apollo user ID of the team member who will become the owner of the specified accounts. Retrieve available user IDs from the Get a List of Users endpoint."),
) -> dict[str, Any]:
    """Assign multiple accounts to a different owner within your team's Apollo account. This operation requires a master API key and allows bulk reassignment of account ownership."""

    # Construct request model with validation
    try:
        _request = _models.PostApiV1AccountsUpdateOwnersRequest(
            query=_models.PostApiV1AccountsUpdateOwnersRequestQuery(account_ids=account_ids, owner_id=owner_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for assign_accounts_to_owner: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/accounts/update_owners"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("assign_accounts_to_owner")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("assign_accounts_to_owner", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="assign_accounts_to_owner",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Accounts
@mcp.tool()
async def list_account_stages() -> dict[str, Any]:
    """Retrieve all available account stages in your Apollo account. Use the returned stage IDs to update individual accounts or bulk update account stages across multiple accounts."""

    # Extract parameters for API call
    _http_path = "/api/v1/account_stages"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_account_stages")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_account_stages", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_account_stages",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Contacts
@mcp.tool()
async def create_contact(
    title: str | None = Field(None, description="The contact's current job title (e.g., 'senior research analyst')."),
    account_id: str | None = Field(None, description="The Apollo ID of the account to associate with this contact."),
    website_url: str | None = Field(None, description="The corporate website URL in URI format (e.g., https://example.com)."),
    label_names: list[str] | None = Field(None, description="An array of list names to which this contact should be added."),
    contact_stage_id: str | None = Field(None, description="The Apollo ID of the contact stage to assign to this contact."),
    present_raw_address: str | None = Field(None, description="The contact's personal location or address (e.g., 'Atlanta, United States')."),
    typed_custom_fields: dict[str, Any] | None = Field(None, description="An object containing custom field data specific to your Apollo account. Field names and values should match your team's configured custom fields."),
    run_dedupe: bool | None = Field(None, description="Set to true to enable deduplication logic that prevents creating duplicate contacts. Defaults to false."),
) -> dict[str, Any]:
    """Add a new contact to your Apollo account. By default, deduplication is disabled; enable it by setting `run_dedupe` to true to prevent creating duplicate contacts."""

    # Construct request model with validation
    try:
        _request = _models.PostApiV1ContactsRequest(
            body=_models.PostApiV1ContactsRequestBody(title=title, account_id=account_id, website_url=website_url, label_names=label_names, contact_stage_id=contact_stage_id, present_raw_address=present_raw_address, typed_custom_fields=typed_custom_fields, run_dedupe=run_dedupe)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_contact: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/contacts"
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
async def get_contact(contact_id: str = Field(..., description="The unique Apollo identifier for the contact you want to retrieve. You can find contact IDs by using the search contacts endpoint.")) -> dict[str, Any]:
    """Retrieve detailed information for a specific contact in your Apollo database. This endpoint returns enriched contact data including email addresses, phone numbers, and other profile information."""

    # Construct request model with validation
    try:
        _request = _models.GetApiV1ContactsContactIdRequest(
            path=_models.GetApiV1ContactsContactIdRequestPath(contact_id=contact_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_contact: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/contacts/{contact_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/contacts/{contact_id}"
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
    contact_id: str = Field(..., description="The Apollo ID of the contact to update. Retrieve contact IDs using the Search for Contacts endpoint."),
    title: str | None = Field(None, description="The contact's job title (e.g., 'senior research analyst')."),
    account_id: str | None = Field(None, description="The Apollo account ID to associate with this contact."),
    website_url: str | None = Field(None, description="The employer's website URL in standard URI format (e.g., https://www.apollo.io/)."),
    label_names: list[str] | None = Field(None, description="List of label names to assign to this contact. Providing new values will completely replace any existing list assignments."),
    contact_stage_id: str | None = Field(None, description="The contact stage ID to update the contact's pipeline stage."),
    present_raw_address: str | None = Field(None, description="The contact's location as a city/state/country string (e.g., 'Atlanta, United States')."),
    typed_custom_fields: dict[str, Any] | None = Field(None, description="Custom field data specific to your Apollo account. Provide as key-value pairs where keys match your team's custom field identifiers."),
) -> dict[str, Any]:
    """Update an existing contact in your Apollo account. Modify contact details such as job title, account association, location, stage, and custom fields. List assignments are replaced entirely when provided."""

    # Construct request model with validation
    try:
        _request = _models.PatchApiV1ContactsContactIdRequest(
            path=_models.PatchApiV1ContactsContactIdRequestPath(contact_id=contact_id),
            body=_models.PatchApiV1ContactsContactIdRequestBody(title=title, account_id=account_id, website_url=website_url, label_names=label_names, contact_stage_id=contact_stage_id, present_raw_address=present_raw_address, typed_custom_fields=typed_custom_fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_contact: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/contacts/{contact_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/contacts/{contact_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_contact")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_contact", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_contact",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Contacts
@mcp.tool()
async def bulk_create_contacts(
    contacts: list[dict[str, Any]] = Field(..., description="Array of contact objects to create. Maximum of 100 contacts per request. Order is preserved in the response."),
    append_label_names: list[str] | None = Field(None, description="Optional array of label names to apply to all contacts created in this request."),
    run_dedupe: bool | None = Field(None, description="Enable intelligent deduplication across all data sources by matching on email, CRM IDs, or name plus organization. When disabled (default), duplicates are created for non-email import sources while email import placeholders are still merged. When enabled, existing contacts are returned without modification except for email import placeholder merging."),
) -> dict[str, Any]:
    """Create up to 100 contacts in a single request with optional deduplication and bulk label assignment. The endpoint intelligently separates newly created contacts from existing ones in the response."""

    # Construct request model with validation
    try:
        _request = _models.PostApiV1ContactsBulkCreateRequest(
            body=_models.PostApiV1ContactsBulkCreateRequestBody(contacts=contacts, append_label_names=append_label_names, run_dedupe=run_dedupe)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for bulk_create_contacts: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/contacts/bulk_create"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("bulk_create_contacts")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("bulk_create_contacts", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="bulk_create_contacts",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Contacts
@mcp.tool()
async def bulk_update_contacts(
    contact_ids: list[str] = Field(..., description="List of contact IDs to update. All contacts in this list will receive the same field updates."),
    owner_id: str | None = Field(None, description="ID of the user to assign as owner for all specified contacts."),
    title: str | None = Field(None, description="Job title to apply to all specified contacts."),
    account_id: str | None = Field(None, description="Account ID to associate with all specified contacts."),
    present_raw_address: str | None = Field(None, description="Physical address to apply to all specified contacts."),
    linkedin_url: str | None = Field(None, description="LinkedIn profile URL for all specified contacts. Must be a valid URI format."),
    typed_custom_fields: dict[str, Any] | None = Field(None, description="Custom field key-value pairs to apply to all specified contacts. Structure as an object with field names as keys."),
    async_: bool | None = Field(None, alias="async", description="Force asynchronous processing of the update request. Automatically enabled when updating more than 100 contacts. Defaults to false for smaller batches."),
) -> dict[str, Any]:
    """Update multiple contacts simultaneously with common field values. Supports updating up to 100 contacts per request, with automatic asynchronous processing for larger batches."""

    # Construct request model with validation
    try:
        _request = _models.PostApiV1ContactsBulkUpdateRequest(
            body=_models.PostApiV1ContactsBulkUpdateRequestBody(contact_ids=contact_ids, owner_id=owner_id, title=title, account_id=account_id, present_raw_address=present_raw_address, linkedin_url=linkedin_url, typed_custom_fields=typed_custom_fields, async_=async_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for bulk_update_contacts: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/contacts/bulk_update"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("bulk_update_contacts")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("bulk_update_contacts", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="bulk_update_contacts",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Contacts
@mcp.tool()
async def search_contacts(
    q_keywords: str | None = Field(None, description="Keywords to filter contacts by name, job title, employer, or email address. Supports multiple search terms combined together."),
    contact_stage_ids: list[str] | None = Field(None, description="Apollo IDs of contact stages to include in the search results. Provide as an array of stage IDs to filter by one or more stages."),
    contact_label_ids: list[str] | None = Field(None, description="Apollo IDs of labels to include in the search results. Provide as an array of label IDs to filter by one or more labels."),
    sort: str | None = Field(None, description="Sort specification in the format 'field:direction' where direction is 'asc' or 'desc'. Example: 'contact_created_at:asc'"),
) -> dict[str, Any]:
    """Search for contacts in your team's Apollo account by keywords, stage, or labels. Results are paginated with a maximum of 100 records per page, up to 500 pages (50,000 total records)."""

    # Call helper functions
    sort_parsed = parse_sort(sort)

    # Construct request model with validation
    try:
        _request = _models.PostApiV1ContactsSearchRequest(
            body=_models.PostApiV1ContactsSearchRequestBody(q_keywords=q_keywords, contact_stage_ids=contact_stage_ids, contact_label_ids=contact_label_ids, sort_by_field=sort_parsed.get('sort_by_field') if sort_parsed else None, sort_ascending=sort_parsed.get('sort_ascending') if sort_parsed else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_contacts: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/contacts/search"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_contacts")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_contacts", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_contacts",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Contacts
@mcp.tool()
async def update_contact_stages(
    contact_ids: list[str] = Field(..., description="Array of Apollo contact IDs to update. Retrieve contact IDs from the Search for Contacts endpoint. All specified contacts will be assigned to the same target stage."),
    contact_stage_id: str = Field(..., description="The Apollo ID of the contact stage to assign to the specified contacts. Retrieve available stage IDs from the List Contact Stages endpoint."),
) -> dict[str, Any]:
    """Update the stage assignment for multiple contacts in your Apollo account. Specify the contacts to update and the target stage they should be assigned to."""

    # Construct request model with validation
    try:
        _request = _models.PostApiV1ContactsUpdateStagesRequest(
            query=_models.PostApiV1ContactsUpdateStagesRequestQuery(contact_ids=contact_ids, contact_stage_id=contact_stage_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_contact_stages: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/contacts/update_stages"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_contact_stages")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_contact_stages", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_contact_stages",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Contacts
@mcp.tool()
async def assign_contacts_to_owner(
    contact_ids: list[str] = Field(..., description="Array of Apollo contact IDs to reassign. Retrieve contact IDs from the Search for Contacts endpoint by identifying the `id` field for each contact you want to update."),
    owner_id: str = Field(..., description="The Apollo user ID of the team member who will become the owner of the specified contacts. Retrieve available user IDs from the Get a List of Users endpoint."),
) -> dict[str, Any]:
    """Reassign multiple contacts to a different owner within your Apollo account. This operation allows you to bulk update contact ownership across your team."""

    # Construct request model with validation
    try:
        _request = _models.PostApiV1ContactsUpdateOwnersRequest(
            query=_models.PostApiV1ContactsUpdateOwnersRequestQuery(contact_ids=contact_ids, owner_id=owner_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for assign_contacts_to_owner: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/contacts/update_owners"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("assign_contacts_to_owner")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("assign_contacts_to_owner", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="assign_contacts_to_owner",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Contacts
@mcp.tool()
async def list_contact_stages() -> dict[str, Any]:
    """Retrieve all available contact stages in your Apollo account. Use the returned stage IDs to update individual contacts or bulk update contact stages across multiple contacts."""

    # Extract parameters for API call
    _http_path = "/api/v1/contact_stages"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_contact_stages")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_contact_stages", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_contact_stages",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Deals
@mcp.tool()
async def create_deal(
    name: str = Field(..., description="A human-readable name for the deal (e.g., 'Massive Q3 Deal')."),
    owner_id: str | None = Field(None, description="The ID of the team member who owns this deal within your Apollo account."),
    account_id: str | None = Field(None, description="The ID of the target company account within your Apollo instance that this deal is associated with."),
    amount: str | None = Field(None, description="The monetary value of the deal as a numeric amount. Enter only digits without commas or currency symbols."),
    opportunity_stage_id: str | None = Field(None, description="The ID of the deal stage (pipeline stage) within your Apollo account that categorizes this deal's progress."),
    closed_date: str | None = Field(None, description="The estimated close date for the deal in YYYY-MM-DD format. Can be a future or past date."),
    typed_custom_fields: dict[str, Any] | None = Field(None, description="Custom field data specific to your Apollo account. Structure and available fields depend on your team's custom field configuration."),
) -> dict[str, Any]:
    """Create a new deal in your Apollo account to track account activity, including deal value, ownership, and pipeline stage. Requires a master API key."""

    # Construct request model with validation
    try:
        _request = _models.PostApiV1OpportunitiesRequest(
            body=_models.PostApiV1OpportunitiesRequestBody(name=name, owner_id=owner_id, account_id=account_id, amount=amount, opportunity_stage_id=opportunity_stage_id, closed_date=closed_date, typed_custom_fields=typed_custom_fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_deal: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/opportunities"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_deal")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_deal", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_deal",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Deals
@mcp.tool()
async def list_opportunities(sort_by_field: Literal["amount", "is_closed", "is_won"] | None = Field(None, description="Sort results by one of three criteria: amount (largest deal values first), is_closed (closed deals first), or is_won (won deals first). If not specified, results are returned in default order.")) -> dict[str, Any]:
    """Retrieve all deals created in your Apollo account. This endpoint requires a master API key and returns a complete list of opportunities for your team."""

    # Construct request model with validation
    try:
        _request = _models.GetApiV1OpportunitiesSearchRequest(
            query=_models.GetApiV1OpportunitiesSearchRequestQuery(sort_by_field=sort_by_field)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_opportunities: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/opportunities/search"
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

# Tags: Deals
@mcp.tool()
async def get_deal(opportunity_id: str = Field(..., description="The unique identifier for the deal you want to retrieve. Use the List All Deals endpoint to find the ID of the desired deal.")) -> dict[str, Any]:
    """Retrieve complete details about a specific deal in your Apollo account, including deal owner, monetary value, stage, and associated account information. Requires a master API key."""

    # Construct request model with validation
    try:
        _request = _models.GetApiV1OpportunitiesOpportunityIdRequest(
            path=_models.GetApiV1OpportunitiesOpportunityIdRequestPath(opportunity_id=opportunity_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_deal: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/opportunities/{opportunity_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/opportunities/{opportunity_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_deal")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_deal", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_deal",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Deals
@mcp.tool()
async def update_opportunity(
    opportunity_id: str = Field(..., description="The unique identifier of the deal to update."),
    owner_id: str | None = Field(None, description="The user ID of the deal owner within your team. Retrieve available user IDs from the Get a List of Users endpoint."),
    name: str | None = Field(None, description="A human-readable name for the deal."),
    amount: str | None = Field(None, description="The monetary value of the deal as a numeric string without commas or currency symbols. The currency is determined by your Apollo account settings."),
    opportunity_stage_id: str | None = Field(None, description="The ID of the deal stage for this opportunity. Retrieve available stage IDs from the List Deal Stages endpoint."),
    closed_date: str | None = Field(None, description="The estimated close date for the deal in YYYY-MM-DD format."),
    typed_custom_fields: dict[str, Any] | None = Field(None, description="Custom field values specific to your team's Apollo account. Use the Get a List of All Custom Fields endpoint to identify field IDs and their required data types."),
) -> dict[str, Any]:
    """Update an existing deal in your Apollo account. Modify deal details such as name, monetary value, owner, stage, and close date to keep your pipeline current."""

    # Construct request model with validation
    try:
        _request = _models.PatchApiV1OpportunitiesOpportunityIdRequest(
            path=_models.PatchApiV1OpportunitiesOpportunityIdRequestPath(opportunity_id=opportunity_id),
            body=_models.PatchApiV1OpportunitiesOpportunityIdRequestBody(owner_id=owner_id, name=name, amount=amount, opportunity_stage_id=opportunity_stage_id, closed_date=closed_date, typed_custom_fields=typed_custom_fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_opportunity: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/opportunities/{opportunity_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/opportunities/{opportunity_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_opportunity")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_opportunity", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_opportunity",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Deals
@mcp.tool()
async def list_deal_stages() -> dict[str, Any]:
    """Retrieve all available deal stages in your Apollo account. Use the stage IDs returned by this endpoint when creating or updating deals through the Apollo API."""

    # Extract parameters for API call
    _http_path = "/api/v1/opportunity_stages"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_deal_stages")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_deal_stages", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_deal_stages",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Sequences
@mcp.tool()
async def search_sequences(q_name: str | None = Field(None, description="Keywords to filter sequences by name. The search will match sequences whose names contain any of the provided keywords.")) -> dict[str, Any]:
    """Search for email sequences in your Apollo account by name. This endpoint requires a master API key and returns sequences matching your search criteria."""

    # Construct request model with validation
    try:
        _request = _models.PostApiV1EmailerCampaignsSearchRequest(
            query=_models.PostApiV1EmailerCampaignsSearchRequestQuery(q_name=q_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_sequences: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/emailer_campaigns/search"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_sequences")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_sequences", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_sequences",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Sequences
@mcp.tool()
async def add_contacts_to_sequence(
    sequence_id: str = Field(..., description="The Apollo ID of the sequence to add contacts to. Retrieve sequence IDs using the Search for Sequences endpoint."),
    emailer_campaign_id: str = Field(..., description="The Apollo ID of the emailer campaign, which must match the sequence_id value."),
    send_email_from_email_account_id: str = Field(..., description="The Apollo ID of the email account to use for sending emails to added contacts. Retrieve email account IDs using the Get a List of Email Accounts endpoint."),
    contact_ids: list[str] | None = Field(None, description="Array of Apollo contact IDs to add to the sequence. Retrieve contact IDs using the Search for Contacts endpoint. Either this or label_names[] must be provided."),
    label_names: list[str] | None = Field(None, description="Array of label names to identify contacts for addition to the sequence. Contacts matching any of these labels will be added. Either this or contact_ids[] must be provided."),
    send_email_from_email_address: str | None = Field(None, description="Optional specific email address within the selected email account to send from."),
    sequence_no_email: bool | None = Field(None, description="Set to true to add contacts to the sequence even if they lack an email address. Defaults to false."),
    sequence_unverified_email: bool | None = Field(None, description="Set to true to add contacts with unverified email addresses to the sequence. Defaults to false."),
    sequence_job_change: bool | None = Field(None, description="Set to true to add contacts to the sequence even if they have recently changed jobs. Defaults to false."),
    sequence_active_in_other_campaigns: bool | None = Field(None, description="Set to true to add contacts to the sequence even if they are already active in other sequences. Defaults to false."),
    sequence_finished_in_other_campaigns: bool | None = Field(None, description="Set to true to add contacts to the sequence if they have previously completed another sequence. Defaults to false."),
    sequence_same_company_in_same_campaign: bool | None = Field(None, description="Set to true to add contacts to the sequence even if other contacts from the same company are already enrolled. Defaults to false."),
    contacts_without_ownership_permission: bool | None = Field(None, description="Set to true to add contacts to the sequence even if you lack ownership permissions for them. Defaults to false."),
    add_if_in_queue: bool | None = Field(None, description="Set to true to add contacts to the sequence even if they are currently queued for processing. Defaults to false."),
    contact_verification_skipped: bool | None = Field(None, description="Set to true to skip contact verification during the addition process. Defaults to false."),
    user_id: str | None = Field(None, description="The Apollo user ID of the team member performing this action. This user will be recorded in the activity log. Retrieve user IDs using the Get a List of Users endpoint."),
    status: Literal["active", "paused"] | None = Field(None, description="Initial enrollment status for added contacts. Use 'paused' with auto_unpause_at to schedule contact addition. Valid values are 'active' or 'paused'."),
    auto_unpause_at: str | None = Field(None, description="ISO 8601 datetime when paused contacts should automatically resume. Must be used together with status set to 'paused'."),
) -> dict[str, Any]:
    """Add contacts to an email sequence in your Apollo account. Contacts can be specified by individual IDs or by label names. Requires a master API key and a valid email account to send from."""

    # Construct request model with validation
    try:
        _request = _models.PostApiV1EmailerCampaignsSequenceIdAddContactIdsRequest(
            path=_models.PostApiV1EmailerCampaignsSequenceIdAddContactIdsRequestPath(sequence_id=sequence_id),
            query=_models.PostApiV1EmailerCampaignsSequenceIdAddContactIdsRequestQuery(emailer_campaign_id=emailer_campaign_id, contact_ids=contact_ids, label_names=label_names, send_email_from_email_account_id=send_email_from_email_account_id, send_email_from_email_address=send_email_from_email_address, sequence_no_email=sequence_no_email, sequence_unverified_email=sequence_unverified_email, sequence_job_change=sequence_job_change, sequence_active_in_other_campaigns=sequence_active_in_other_campaigns, sequence_finished_in_other_campaigns=sequence_finished_in_other_campaigns, sequence_same_company_in_same_campaign=sequence_same_company_in_same_campaign, contacts_without_ownership_permission=contacts_without_ownership_permission, add_if_in_queue=add_if_in_queue, contact_verification_skipped=contact_verification_skipped, user_id=user_id, status=status, auto_unpause_at=auto_unpause_at)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_contacts_to_sequence: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/emailer_campaigns/{sequence_id}/add_contact_ids", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/emailer_campaigns/{sequence_id}/add_contact_ids"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_contacts_to_sequence")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_contacts_to_sequence", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_contacts_to_sequence",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Sequences
@mcp.tool()
async def update_sequence_contact_status(
    emailer_campaign_ids: list[str] = Field(..., description="One or more Apollo sequence IDs to update. When multiple sequences are specified, the contact status change applies across all selected sequences."),
    contact_ids: list[str] = Field(..., description="One or more Apollo contact IDs whose sequence status should be updated. These contacts must exist within the specified sequences."),
    mode: Literal["mark_as_finished", "remove", "stop"] = Field(..., description="The action to perform on the contacts: mark_as_finished to indicate sequence completion, remove to delete contacts from the sequence, or stop to pause their progress."),
) -> dict[str, Any]:
    """Update the status of contacts within email sequences by marking them as finished, removing them entirely, or stopping their progress. Requires a master API key."""

    # Construct request model with validation
    try:
        _request = _models.PostApiV1EmailerCampaignsRemoveOrStopContactIdsRequest(
            query=_models.PostApiV1EmailerCampaignsRemoveOrStopContactIdsRequestQuery(emailer_campaign_ids=emailer_campaign_ids, contact_ids=contact_ids, mode=mode)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_sequence_contact_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/emailer_campaigns/remove_or_stop_contact_ids"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_sequence_contact_status")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_sequence_contact_status", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_sequence_contact_status",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Sequences
@mcp.tool()
async def activate_email_sequence(sequence_id: str = Field(..., description="The Apollo ID of the email sequence to activate. Retrieve sequence IDs by calling the Search for Sequences endpoint.")) -> dict[str, Any]:
    """Activate an inactive email sequence to begin sending emails to its contacts on the configured schedule. The sequence must have at least one step configured before activation."""

    # Construct request model with validation
    try:
        _request = _models.PostApiV1EmailerCampaignsSequenceIdApproveRequest(
            path=_models.PostApiV1EmailerCampaignsSequenceIdApproveRequestPath(sequence_id=sequence_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for activate_email_sequence: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/emailer_campaigns/{sequence_id}/approve", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/emailer_campaigns/{sequence_id}/approve"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("activate_email_sequence")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("activate_email_sequence", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="activate_email_sequence",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Sequences
@mcp.tool()
async def abort_email_sequence(sequence_id: str = Field(..., description="The unique Apollo identifier for the email sequence you want to abort. This is a 24-character hexadecimal string that uniquely identifies the sequence in the system.")) -> dict[str, Any]:
    """Stop an active email sequence and pause all contacts from receiving further emails. Once aborted, the sequence halts all outgoing communications."""

    # Construct request model with validation
    try:
        _request = _models.PostApiV1EmailerCampaignsSequenceIdAbortRequest(
            path=_models.PostApiV1EmailerCampaignsSequenceIdAbortRequestPath(sequence_id=sequence_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for abort_email_sequence: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/emailer_campaigns/{sequence_id}/abort", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/emailer_campaigns/{sequence_id}/abort"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("abort_email_sequence")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("abort_email_sequence", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="abort_email_sequence",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Sequences
@mcp.tool()
async def archive_sequence(sequence_id: str = Field(..., description="The Apollo ID of the sequence to archive. This is a unique identifier in the format of a 24-character hexadecimal string.")) -> dict[str, Any]:
    """Archive an email sequence to mark it as inactive and automatically finish all contacts currently enrolled in it. Only the sequence owner or users with full access sharing permissions can perform this action, and a master API key is required."""

    # Construct request model with validation
    try:
        _request = _models.PostApiV1EmailerCampaignsSequenceIdArchiveRequest(
            path=_models.PostApiV1EmailerCampaignsSequenceIdArchiveRequestPath(sequence_id=sequence_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for archive_sequence: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/emailer_campaigns/{sequence_id}/archive", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/emailer_campaigns/{sequence_id}/archive"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("archive_sequence")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("archive_sequence", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="archive_sequence",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Sequences
@mcp.tool()
async def search_outreach_emails(
    emailer_message_stats: list[Literal["delivered", "scheduled", "drafted", "not_opened", "opened", "clicked", "unsubscribed", "demoed", "bounced", "spam_blocked", "failed_other"]] | None = Field(None, description="Filter emails by their delivery status (e.g., delivered, opened, bounced). Accepts multiple status values to broaden results."),
    emailer_message_reply_classes: list[Literal["willing_to_meet", "follow_up_question", "person_referral", "out_of_office", "already_left_company_or_not_right_person", "not_interested", "unsubscribe", "none_of_the_above"]] | None = Field(None, description="Filter emails by recipient response sentiment, such as interest in meeting or follow-up questions. Accepts multiple response types."),
    user_ids: list[str] | None = Field(None, description="Filter emails sent by specific team members. Provide user IDs as an array; retrieve user IDs from the Get a List of Users endpoint."),
    email_account_id_and_aliases: str | None = Field(None, description="Filter results by a specific email account ID and its associated aliases."),
    not_emailer_campaign_ids: list[str] | None = Field(None, description="Exclude emails from specific sequences. Provide sequence IDs as an array; all sequences not listed will be included in results. Retrieve sequence IDs from the Search for Sequences endpoint."),
    emailer_message_date_range_mode: Literal["due_at", "completed_at"] | None = Field(None, description="Specify the date field to filter by: use 'due_at' for scheduled delivery dates or 'completed_at' for actual delivery dates. Use with the min/max date range parameters."),
    not_sent_reason_cds: list[Literal["contact_stage_safeguard", "same_account_reply", "account_stage_safeguard", "email_unverified", "snippets_missing", "personalized_opener_missing", "thread_reply_original_email_missing", "no_active_email_account", "email_format_invalid", "ownership_permission", "email_service_provider_delivery_failure", "sendgrid_dropped_email", "mailgun_dropped_email", "gdpr_compliance", "not_valid_hard_bounce_detected", "other_safeguard", "new_job_change_detected", "email_on_global_bounce_list"]] | None = Field(None, description="Filter emails by the reason they were not sent (e.g., invalid address, bounced). Accepts multiple reasons."),
    q_keywords: str | None = Field(None, description="Narrow results by keywords that match email content. Keywords must directly match at least part of an email's body or subject."),
) -> dict[str, Any]:
    """Search for outreach emails created and sent through Apollo sequences by your team. Returns up to 50,000 records with pagination support (100 records per page, maximum 500 pages). Requires a master API key."""

    # Construct request model with validation
    try:
        _request = _models.GetApiV1EmailerMessagesSearchRequest(
            query=_models.GetApiV1EmailerMessagesSearchRequestQuery(emailer_message_stats=emailer_message_stats, emailer_message_reply_classes=emailer_message_reply_classes, user_ids=user_ids, email_account_id_and_aliases=email_account_id_and_aliases, not_emailer_campaign_ids=not_emailer_campaign_ids, emailer_message_date_range_mode=emailer_message_date_range_mode, not_sent_reason_cds=not_sent_reason_cds, q_keywords=q_keywords)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_outreach_emails: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/emailer_messages/search"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_outreach_emails")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_outreach_emails", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_outreach_emails",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Sequences
@mcp.tool()
async def get_email_activities(id_: str = Field(..., alias="id", description="The unique identifier of the email message. This ID is assigned to each outreach email in Apollo and can be obtained by calling the search emails endpoint.")) -> dict[str, Any]:
    """Retrieve detailed statistics and activity information for a specific email sent through an Apollo sequence, including email contents, engagement metrics (opens and clicks), and recipient contact details."""

    # Construct request model with validation
    try:
        _request = _models.GetApiV1EmailerMessagesIdActivitiesRequest(
            path=_models.GetApiV1EmailerMessagesIdActivitiesRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_email_activities: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/emailer_messages/{id}/activities", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/emailer_messages/{id}/activities"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_email_activities")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_email_activities", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_email_activities",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tasks
@mcp.tool()
async def create_task(
    user_id: str = Field(..., description="The ID of the team member who will own this task. Retrieve user IDs from the Get a List of Users endpoint."),
    contact_id: str = Field(..., description="The Apollo ID of the contact associated with this task. Use the Search for Contacts endpoint to find valid contact IDs."),
    type_: Literal["call", "outreach_manual_email", "linkedin_step_connect", "linkedin_step_message", "linkedin_step_view_profile", "linkedin_step_interact_post", "action_item"] = Field(..., alias="type", description="The type of action required for this task. Choose from: call, outreach via manual email, LinkedIn connection request, LinkedIn message, LinkedIn profile view, LinkedIn post interaction, or general action item."),
    status: str = Field(..., description="The current status of the task. Use 'scheduled' for future tasks or 'completed'/'skipped' for already-finished tasks."),
    due_at: str = Field(..., description="The due date and time for this task in ISO 8601 format (UTC/GMT). Example: 2025-02-15T08:10:30Z."),
    priority: Literal["high", "medium", "low"] | None = Field(None, description="The priority level for this task. Defaults to medium if not specified. Options are high, medium, or low."),
    title: str | None = Field(None, description="An optional title for the task. If not provided, Apollo will auto-generate a title based on the task type and contact name."),
    note: str | None = Field(None, description="An optional description providing context for the task owner about the action they need to take."),
) -> dict[str, Any]:
    """Create a task to track upcoming actions for you and your team, such as calls, emails, or LinkedIn outreach. The created task is assigned to a specific team member and linked to a contact."""

    # Construct request model with validation
    try:
        _request = _models.PostApiV1TasksRequest(
            body=_models.PostApiV1TasksRequestBody(user_id=user_id, contact_id=contact_id, type_=type_, priority=priority, status=status, due_at=due_at, title=title, note=note)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_task: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/tasks"
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
async def bulk_create_tasks(
    user_id: str = Field(..., description="The ID of the team member who will own and execute these tasks within your Apollo account."),
    contact_ids: list[str] = Field(..., description="Array of Apollo contact IDs to assign tasks to. A separate task will be created for each contact using the same task configuration."),
    type_: Literal["call", "outreach_manual_email", "linkedin_step_connect", "linkedin_step_message", "linkedin_step_view_profile", "linkedin_step_interact_post", "action_item"] = Field(..., alias="type", description="The type of action for the task: call, outreach_manual_email, linkedin_step_connect, linkedin_step_message, linkedin_step_view_profile, linkedin_step_interact_post, or action_item."),
    status: str = Field(..., description="The task status: use 'scheduled' for future tasks, or 'completed'/'skipped' for tasks already finished."),
    due_at: str = Field(..., description="The due date and time for the task in ISO 8601 format (e.g., 2025-02-15T08:10:30Z). Apollo uses Greenwich Mean Time (GMT) by default."),
    priority: Literal["high", "medium", "low"] | None = Field(None, description="Priority level for the task. Defaults to medium if not specified."),
    note: str | None = Field(None, description="Optional description providing context for the task owner about the action they need to take."),
) -> dict[str, Any]:
    """Create multiple tasks in a single request, with one task generated per contact. Returns a success status and array of created tasks. Requires a master API key."""

    # Construct request model with validation
    try:
        _request = _models.PostApiV1TasksBulkCreateRequest(
            body=_models.PostApiV1TasksBulkCreateRequestBody(user_id=user_id, contact_ids=contact_ids, type_=type_, priority=priority, status=status, due_at=due_at, note=note)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for bulk_create_tasks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/tasks/bulk_create"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("bulk_create_tasks")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("bulk_create_tasks", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="bulk_create_tasks",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tasks
@mcp.tool()
async def search_tasks(
    sort_by_field: Literal["task_due_at", "task_priority"] | None = Field(None, description="Sort results by task due date (future dates first) or priority level (highest priority first)."),
    open_factor_names: list[str] | None = Field(None, description="Request task type counts in the response by including task_types. When specified, the response includes a task_types array with count values for each task type."),
) -> dict[str, Any]:
    """Search for tasks created in Apollo across your team. Returns up to 50,000 records with pagination support (100 records per page, maximum 500 pages). Requires a master API key."""

    # Construct request model with validation
    try:
        _request = _models.PostApiV1TasksSearchRequest(
            query=_models.PostApiV1TasksSearchRequestQuery(sort_by_field=sort_by_field, open_factor_names=open_factor_names)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_tasks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/tasks/search"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_tasks")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_tasks", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_tasks",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Calls
@mcp.tool()
async def create_phone_call(
    logged: bool | None = Field(None, description="Whether to create an individual call record in Apollo. Defaults to true if not specified."),
    user_id: list[str] | None = Field(None, description="IDs of team members who made the call. Retrieve available user IDs from the Get a List of Users endpoint. Accepts multiple user IDs as an array."),
    account_id: str | None = Field(None, description="ID of the account associated with this call. Retrieve available account IDs from the Search for Accounts endpoint."),
    status: Literal["queued", "ringing", "in-progress", "completed", "no_answer", "failed", "busy"] | None = Field(None, description="Current status of the call. Valid statuses are: queued, ringing, in-progress, completed, no_answer, failed, or busy."),
    start_time: str | None = Field(None, description="Timestamp when the call started, formatted in ISO 8601 date-time format using Greenwich Mean Time (GMT)."),
    end_time: str | None = Field(None, description="Timestamp when the call ended, formatted in ISO 8601 date-time format using Greenwich Mean Time (GMT)."),
    duration: int | None = Field(None, description="Length of the call in seconds (not minutes)."),
    phone_call_purpose_id: str | None = Field(None, description="ID of the call purpose category to assign to this record. Call purposes are custom to your Apollo account."),
    phone_call_outcome_id: str | None = Field(None, description="ID of the call outcome to assign to this record. Call outcomes are custom to your Apollo account."),
    note: str | None = Field(None, description="Additional notes or context about the call to include in the record."),
) -> dict[str, Any]:
    """Log phone calls made through external systems (such as Orum or Nooks) into Apollo. This endpoint records call metadata and outcomes but cannot initiate calls. Requires a master API key."""

    # Construct request model with validation
    try:
        _request = _models.PostApiV1PhoneCallsRequest(
            query=_models.PostApiV1PhoneCallsRequestQuery(logged=logged, user_id=user_id, account_id=account_id, status=status, start_time=start_time, end_time=end_time, duration=duration, phone_call_purpose_id=phone_call_purpose_id, phone_call_outcome_id=phone_call_outcome_id, note=note)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_phone_call: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/phone_calls"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_phone_call")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_phone_call", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_phone_call",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Calls
@mcp.tool()
async def search_phone_calls(
    date_range_min: str | None = Field(None, alias="date_rangemin", description="Lower bound of the date range to search (YYYY-MM-DD format). Must be earlier than date_range[max] if both are specified."),
    date_range_max: str | None = Field(None, alias="date_rangemax", description="Upper bound of the date range to search (YYYY-MM-DD format). Must be later than date_range[min] if both are specified."),
    duration_min: int | None = Field(None, alias="durationmin", description="Minimum call duration in seconds. Must be smaller than duration[max] if both are specified."),
    duration_max: int | None = Field(None, alias="durationmax", description="Maximum call duration in seconds. Must be larger than duration[min] if both are specified."),
    inbound: Literal["incoming", "outgoing"] | None = Field(None, description="Filter by call direction: 'incoming' for calls received by your team, or 'outgoing' for calls made by your team."),
    user_ids: list[str] | None = Field(None, description="Filter calls by one or more team members. Provide an array of user IDs from your Apollo account."),
    contact_label_ids: list[str] | None = Field(None, description="Filter calls by one or more contacts in your Apollo database. Provide an array of contact IDs."),
    phone_call_purpose_ids: list[str] | None = Field(None, description="Filter calls by their purpose. Provide an array of call purpose IDs configured in your Apollo account."),
    phone_call_outcome_ids: list[str] | None = Field(None, description="Filter calls by their outcome or disposition. Provide an array of call outcome IDs configured in your Apollo account."),
    q_keywords: str | None = Field(None, description="Narrow search results by keywords found in call records."),
) -> dict[str, Any]:
    """Search for phone calls made or received by your team using the Apollo dialer. Filter results by date range, duration, call direction, team members, contacts, call purposes, outcomes, and keywords."""

    # Construct request model with validation
    try:
        _request = _models.GetApiV1PhoneCallsSearchRequest(
            query=_models.GetApiV1PhoneCallsSearchRequestQuery(date_range_min=date_range_min, date_range_max=date_range_max, duration_min=duration_min, duration_max=duration_max, inbound=inbound, user_ids=user_ids, contact_label_ids=contact_label_ids, phone_call_purpose_ids=phone_call_purpose_ids, phone_call_outcome_ids=phone_call_outcome_ids, q_keywords=q_keywords)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_phone_calls: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/phone_calls/search"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_phone_calls")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_phone_calls", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_phone_calls",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Calls
@mcp.tool()
async def update_call(
    id_: str = Field(..., alias="id", description="The unique Apollo identifier for the call record to update."),
    logged: bool | None = Field(None, description="Set to true to create an individual record for this phone call in Apollo."),
    user_id: list[str] | None = Field(None, description="Array of user IDs from your Apollo account to designate who made the call."),
    account_id: str | None = Field(None, description="The Apollo account ID to associate this call with."),
    status: Literal["queued", "ringing", "in-progress", "completed", "no_answer", "failed", "busy"] | None = Field(None, description="The current status of the call: queued, ringing, in-progress, completed, no_answer, failed, or busy."),
    start_time: str | None = Field(None, description="The date and time when the call started, formatted in ISO 8601 format."),
    end_time: str | None = Field(None, description="The date and time when the call ended, formatted in ISO 8601 format."),
    duration: int | None = Field(None, description="The total duration of the call in seconds."),
    phone_call_purpose_id: str | None = Field(None, description="The Apollo ID of the call purpose category to assign to this record."),
    phone_call_outcome_id: str | None = Field(None, description="The Apollo ID of the call outcome to assign to this record."),
    note: str | None = Field(None, description="A text note to add to the call record for additional context or details."),
) -> dict[str, Any]:
    """Update an existing call record in Apollo with new details such as status, timing, duration, purpose, outcome, and notes. Requires a master API key."""

    # Construct request model with validation
    try:
        _request = _models.PutApiV1PhoneCallsIdRequest(
            path=_models.PutApiV1PhoneCallsIdRequestPath(id_=id_),
            query=_models.PutApiV1PhoneCallsIdRequestQuery(logged=logged, user_id=user_id, account_id=account_id, status=status, start_time=start_time, end_time=end_time, duration=duration, phone_call_purpose_id=phone_call_purpose_id, phone_call_outcome_id=phone_call_outcome_id, note=note)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_call: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/phone_calls/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/phone_calls/{id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
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
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Miscellaneous
@mcp.tool()
async def get_api_usage_stats() -> dict[str, Any]:
    """Retrieve your team's API usage statistics and current rate limits across all endpoints. This endpoint shows usage metrics and rate limit thresholds (per minute, hour, and day) based on your Apollo pricing plan and requires a master API key for authentication."""

    # Extract parameters for API call
    _http_path = "/api/v1/usage_stats/api_usage_stats"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_api_usage_stats")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_api_usage_stats", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_api_usage_stats",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Miscellaneous
@mcp.tool()
async def list_users() -> dict[str, Any]:
    """Retrieve all user IDs in your Apollo account. These IDs are essential for creating deals, accounts, tasks, and other resources that require user assignment."""

    # Extract parameters for API call
    _http_path = "/api/v1/users/search"
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

# Tags: Miscellaneous
@mcp.tool()
async def list_email_accounts() -> dict[str, Any]:
    """Retrieve all linked email accounts and inboxes used by your team in Apollo. Returns account IDs that can be used with sequence operations. Requires a master API key."""

    # Extract parameters for API call
    _http_path = "/api/v1/email_accounts"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_email_accounts")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_email_accounts", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_email_accounts",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Miscellaneous
@mcp.tool()
async def list_lists() -> dict[str, Any]:
    """Retrieve all lists created in your Apollo account. Use this endpoint to discover available lists before creating contacts or performing other list-based operations. Requires a master API key."""

    # Extract parameters for API call
    _http_path = "/api/v1/labels"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_lists")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_lists", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_lists",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Miscellaneous
@mcp.tool()
async def list_custom_fields() -> dict[str, Any]:
    """Retrieve all custom fields configured in your Apollo account. This endpoint provides a complete inventory of custom field definitions available for use across your organization."""

    # Extract parameters for API call
    _http_path = "/api/v1/typed_custom_fields"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_custom_fields")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_custom_fields", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_custom_fields",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Miscellaneous
@mcp.tool()
async def list_fields(source: Literal["system", "custom", "crm_synced"] | None = Field(None, description="Filter the returned fields by their source type: system fields (built-in), custom fields (user-created), or crm_synced fields (synchronized from your CRM).")) -> dict[str, Any]:
    """Retrieve all fields available in your Apollo account, with optional filtering by source type. Requires a master API key for authentication."""

    # Construct request model with validation
    try:
        _request = _models.GetApiV1FieldsRequest(
            query=_models.GetApiV1FieldsRequestQuery(source=source)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_fields: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/fields"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
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
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Miscellaneous
@mcp.tool()
async def create_custom_field(
    label: str = Field(..., description="The display name for the custom field (e.g., 'Test Name'). This is how the field will appear in your Apollo account."),
    modality: Literal["contact", "account", "opportunity"] = Field(..., description="The entity type this custom field applies to: contact, account, or opportunity. This determines where the field will be available in your Apollo workspace."),
    type_: Literal["string", "textarea", "number", "date", "datetime", "boolean"] = Field(..., alias="type", description="The data type for the custom field. Choose from: string (single-line text), textarea (multi-line text), number, date, datetime, or boolean (true/false)."),
    meta: dict[str, Any] | None = Field(None, description="Optional metadata object to store additional configuration or properties for the custom field."),
) -> dict[str, Any]:
    """Create a custom field in your Apollo account to capture unique details about contacts, accounts, or deals. Custom fields enable your team to store specialized information and personalize outreach sequences."""

    # Construct request model with validation
    try:
        _request = _models.PostApiV1FieldsRequest(
            body=_models.PostApiV1FieldsRequestBody(label=label, modality=modality, type_=type_, meta=meta)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_custom_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/fields"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_custom_field")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_custom_field", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_custom_field",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Miscellaneous
@mcp.tool()
async def list_notes(
    account_id: str | None = Field(None, description="The ID of the account to retrieve notes for."),
    opportunity_id: str | None = Field(None, description="The ID of the opportunity to retrieve notes for."),
    calendar_event_id: str | None = Field(None, description="The ID of the calendar event to retrieve notes for."),
    conversation_ids: list[str] | None = Field(None, description="One or more conversation IDs to filter notes by multiple conversations."),
    contact_ids: list[str] | None = Field(None, description="One or more contact IDs to filter notes by multiple contacts."),
    start_date: str | None = Field(None, description="Filter notes to only those created on or after this date (ISO 8601 format)."),
    sort_by_field: Literal["created_at", "updated_at"] | None = Field(None, description="Field to sort results by. Defaults to creation date. Options are creation date or last update date."),
    sort_direction: Literal["asc", "desc"] | None = Field(None, description="Sort direction for results. Defaults to descending (newest first). Use ascending for oldest first."),
    skip: int | None = Field(None, description="Number of notes to skip for pagination. Must be zero or greater. Defaults to 0.", ge=0),
    limit: int | None = Field(None, description="Maximum number of notes to return per request. Must be between 1 and 100. Defaults to 25.", ge=1, le=100),
) -> dict[str, Any]:
    """Retrieve notes associated with a specific contact, account, opportunity, calendar event, or conversation. At least one relation parameter must be provided to filter results, with support for sorting and pagination."""

    # Construct request model with validation
    try:
        _request = _models.GetApiV1NotesRequest(
            query=_models.GetApiV1NotesRequestQuery(account_id=account_id, opportunity_id=opportunity_id, calendar_event_id=calendar_event_id, conversation_ids=conversation_ids, contact_ids=contact_ids, start_date=start_date, sort_by_field=sort_by_field, sort_direction=sort_direction, skip=skip, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_notes: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/notes"
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
        print("  python apollo_rest_api_server.py", file=sys.stderr)
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

    parser = argparse.ArgumentParser(description="Apollo REST API MCP Server")

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
    logger.info("Starting Apollo REST API MCP Server")
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

#!/usr/bin/env python3
"""
Outline MCP Server

API Info:
- API License: BSD-3-Clause (https://github.com/outline/openapi/blob/main/LICENSE)

Generated: 2026-04-10 10:09:45 UTC
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

BASE_URL = os.getenv("BASE_URL", "https://app.getoutline.com/api")
SERVER_NAME = "Outline"
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
    'BearerAuth',
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
try:
    _auth_handlers["BearerAuth"] = _auth.BearerTokenAuth(env_var="BEARER_TOKEN", token_format="Bearer")
    logging.info("Authentication configured: BearerAuth")
except ValueError as e:
    # Extract credential names from error message (first sentence before "Leave empty")
    error_msg = str(e).split("Leave empty")[0].strip()
    logging.warning(f"Credentials for BearerAuth not configured: {error_msg}")
    _auth_handlers["BearerAuth"] = None

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

mcp = FastMCP("Outline", middleware=[_JsonCoercionMiddleware()])

# Tags: Attachments
@mcp.tool()
async def create_attachment(
    name: str = Field(..., description="The filename of the attachment, including the file extension (e.g., image.png, document.pdf)."),
    content_type: str = Field(..., alias="contentType", description="The MIME type of the file being attached (e.g., image/png, application/pdf, text/plain). Must match the actual file format."),
    size: float = Field(..., description="The size of the file in bytes. Must be a positive number representing the exact file size before upload."),
    document_id: str | None = Field(None, alias="documentId", description="Optional UUID identifier of the document this attachment is associated with. Omit if the attachment is not linked to a specific document."),
) -> dict[str, Any]:
    """Create an attachment record in the database and obtain the necessary credentials to upload the file to cloud storage from the client. Returns upload configuration details for completing the file transfer."""

    # Construct request model with validation
    try:
        _request = _models.AttachmentsCreateRequest(
            body=_models.AttachmentsCreateRequestBody(name=name, document_id=document_id, content_type=content_type, size=size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_attachment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/attachments.create"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_attachment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_attachment", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_attachment",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Attachments
@mcp.tool()
async def get_attachment(id_: str = Field(..., alias="id", description="The unique identifier of the attachment, formatted as a UUID.")) -> dict[str, Any]:
    """Retrieve an attachment by its unique identifier. For private attachments, a temporary signed URL with embedded credentials is generated automatically."""

    # Construct request model with validation
    try:
        _request = _models.AttachmentsRedirectRequest(
            body=_models.AttachmentsRedirectRequestBody(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_attachment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/attachments.redirect"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_attachment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_attachment", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_attachment",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Attachments
@mcp.tool()
async def delete_attachment(id_: str = Field(..., alias="id", description="The unique identifier (UUID) of the attachment to delete.")) -> dict[str, Any]:
    """Permanently delete an attachment by its unique identifier. Note that this action does not remove any references or links to the attachment that may exist in documents."""

    # Construct request model with validation
    try:
        _request = _models.AttachmentsDeleteRequest(
            body=_models.AttachmentsDeleteRequestBody(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_attachment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/attachments.delete"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_attachment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_attachment", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_attachment",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Auth
@mcp.tool()
async def get_auth_info() -> dict[str, Any]:
    """Retrieve authentication details and metadata for the current API key, including permissions and account information."""

    # Extract parameters for API call
    _http_path = "/auth.info"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_auth_info")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_auth_info", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_auth_info",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Collections
@mcp.tool()
async def get_collection(id_: str = Field(..., alias="id", description="The UUID that uniquely identifies the collection to retrieve.")) -> dict[str, Any]:
    """Retrieve detailed information about a specific collection using its unique identifier."""

    # Construct request model with validation
    try:
        _request = _models.CollectionsInfoRequest(
            body=_models.CollectionsInfoRequestBody(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_collection: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/collections.info"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_collection")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_collection", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_collection",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Collections
@mcp.tool()
async def get_collection_document_structure(id_: str = Field(..., alias="id", description="The unique identifier of the collection, formatted as a UUID.")) -> dict[str, Any]:
    """Retrieve the document structure of a collection as a hierarchical tree of navigation nodes, showing how documents are organized within the collection."""

    # Construct request model with validation
    try:
        _request = _models.CollectionsDocumentsRequest(
            body=_models.CollectionsDocumentsRequestBody(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_collection_document_structure: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/collections.documents"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_collection_document_structure")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_collection_document_structure", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_collection_document_structure",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Collections
@mcp.tool()
async def list_collections(body: _models.CollectionsListBody | None = Field(None, description="Optional request body for filtering or configuring the list operation. Consult API documentation for supported query parameters or filter options.")) -> dict[str, Any]:
    """Retrieve all collections that the authenticated user has access to. Returns a list of collections with their metadata and details."""

    # Construct request model with validation
    try:
        _request = _models.CollectionsListRequest(
            body=_models.CollectionsListRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_collections: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/collections.list"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_collections")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_collections", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_collections",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Collections
@mcp.tool()
async def create_collection(
    name: str = Field(..., description="The name of the collection (e.g., 'Human Resources'). Used as the primary identifier for the collection."),
    description: str | None = Field(None, description="A brief description of the collection's purpose and contents. Markdown formatting is supported for rich text."),
    permission: Literal["read", "read_write"] | None = Field(None, description="The access level for the collection. Choose 'read' for view-only access or 'read_write' for full editing permissions."),
    color: str | None = Field(None, description="A hex color code (e.g., '#123123') to customize the visual appearance of the collection icon."),
    sharing: bool | None = Field(None, description="Whether documents in this collection can be shared publicly. Set to true to enable public sharing, false to restrict sharing."),
) -> dict[str, Any]:
    """Create a new collection to organize and manage documents. Specify the collection's name, description, visual styling, and access permissions."""

    # Construct request model with validation
    try:
        _request = _models.CollectionsCreateRequest(
            body=_models.CollectionsCreateRequestBody(name=name, description=description, permission=permission, color=color, sharing=sharing)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_collection: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/collections.create"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_collection")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_collection", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_collection",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Collections
@mcp.tool()
async def update_collection(
    id_: str = Field(..., alias="id", description="The unique identifier of the collection to update, provided as a UUID."),
    name: str | None = Field(None, description="The new name for the collection. Use a clear, descriptive title that reflects the collection's purpose."),
    description: str | None = Field(None, description="A brief description of the collection's contents and purpose. Markdown formatting is supported for rich text styling."),
    permission: Literal["read", "read_write"] | None = Field(None, description="The access level for users who can access this collection. Choose 'read' for view-only access or 'read_write' to allow modifications."),
    color: str | None = Field(None, description="A hex color code (e.g., #123456) to customize the collection's icon color for visual organization and identification."),
    sharing: bool | None = Field(None, description="Whether to allow public sharing of documents within this collection. Set to true to enable sharing, false to restrict to authenticated users only."),
) -> dict[str, Any]:
    """Update an existing collection's properties including name, description, icon color, sharing settings, and access permissions. Changes apply immediately to the collection and affect how it appears and behaves for all users with access."""

    # Construct request model with validation
    try:
        _request = _models.CollectionsUpdateRequest(
            body=_models.CollectionsUpdateRequestBody(id_=id_, name=name, description=description, permission=permission, color=color, sharing=sharing)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_collection: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/collections.update"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_collection")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_collection", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_collection",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Collections
@mcp.tool()
async def add_user_to_collection(
    id_: str = Field(..., alias="id", description="The unique identifier (UUID) of the collection to which the user will be added."),
    user_id: str = Field(..., alias="userId", description="The unique identifier (UUID) of the user to add as a member to the collection."),
    permission: Literal["read", "read_write"] | None = Field(None, description="The access permission level for the user in this collection. Choose 'read' for view-only access or 'read_write' for full read and write access. Defaults to 'read' if not specified."),
) -> dict[str, Any]:
    """Add a user as a member to a collection with specified access permissions. The user will gain access to the collection based on the permission level assigned."""

    # Construct request model with validation
    try:
        _request = _models.CollectionsAddUserRequest(
            body=_models.CollectionsAddUserRequestBody(id_=id_, user_id=user_id, permission=permission)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_user_to_collection: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/collections.add_user"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_user_to_collection")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_user_to_collection", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_user_to_collection",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Collections
@mcp.tool()
async def remove_user_from_collection(
    id_: str = Field(..., alias="id", description="The unique identifier (UUID) of the collection from which the user will be removed."),
    user_id: str = Field(..., alias="userId", description="The unique identifier (UUID) of the user to remove from the collection."),
) -> dict[str, Any]:
    """Remove a user from a collection. This operation revokes the specified user's access to the collection."""

    # Construct request model with validation
    try:
        _request = _models.CollectionsRemoveUserRequest(
            body=_models.CollectionsRemoveUserRequestBody(id_=id_, user_id=user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_user_from_collection: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/collections.remove_user"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_user_from_collection")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_user_from_collection", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_user_from_collection",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Collections
@mcp.tool()
async def list_collection_memberships(body: _models.CollectionsMembershipsBody | None = Field(None, description="Request body containing the collection identifier and optional filtering criteria for the membership query.")) -> dict[str, Any]:
    """Retrieve all individual memberships for a specific collection. Note that this endpoint returns only direct memberships and does not include group-based memberships."""

    # Construct request model with validation
    try:
        _request = _models.CollectionsMembershipsRequest(
            body=_models.CollectionsMembershipsRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_collection_memberships: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/collections.memberships"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_collection_memberships")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_collection_memberships", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_collection_memberships",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Collections
@mcp.tool()
async def add_group_to_collection(
    id_: str = Field(..., alias="id", description="The unique identifier (UUID) of the collection to which the group will be granted access."),
    group_id: str = Field(..., alias="groupId", description="The unique identifier (UUID) of the group whose members will receive access to the collection."),
    permission: Literal["read", "read_write"] | None = Field(None, description="The access level to grant the group members. Choose 'read' for view-only access or 'read_write' for full read and write permissions. Defaults to 'read' if not specified."),
) -> dict[str, Any]:
    """Grant all members of a group access to a collection with a specified permission level. This enables group-based access control for collaborative collection management."""

    # Construct request model with validation
    try:
        _request = _models.CollectionsAddGroupRequest(
            body=_models.CollectionsAddGroupRequestBody(id_=id_, group_id=group_id, permission=permission)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_group_to_collection: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/collections.add_group"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_group_to_collection")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_group_to_collection", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_group_to_collection",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Collections
@mcp.tool()
async def remove_group_from_collection(
    id_: str = Field(..., alias="id", description="The unique identifier (UUID) of the collection from which the group will be removed."),
    group_id: str = Field(..., alias="groupId", description="The unique identifier (UUID) of the group whose members will lose access to the collection."),
) -> dict[str, Any]:
    """Revoke all members of a group from accessing a collection. Note that group members may retain access through other group memberships or individual collection access."""

    # Construct request model with validation
    try:
        _request = _models.CollectionsRemoveGroupRequest(
            body=_models.CollectionsRemoveGroupRequestBody(id_=id_, group_id=group_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_group_from_collection: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/collections.remove_group"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_group_from_collection")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_group_from_collection", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_group_from_collection",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Collections
@mcp.tool()
async def list_collection_group_memberships(body: _models.CollectionsGroupMembershipsBody | None = Field(None, description="Request body containing the collection identifier and optional filtering criteria for the group memberships query.")) -> dict[str, Any]:
    """Retrieve all groups that have been granted access to a specific collection. This lists the group memberships associated with the collection."""

    # Construct request model with validation
    try:
        _request = _models.CollectionsGroupMembershipsRequest(
            body=_models.CollectionsGroupMembershipsRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_collection_group_memberships: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/collections.group_memberships"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_collection_group_memberships")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_collection_group_memberships", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_collection_group_memberships",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Collections
@mcp.tool()
async def delete_collection(id_: str = Field(..., alias="id", description="The unique identifier (UUID) of the collection to delete.")) -> dict[str, Any]:
    """Permanently delete a collection and all of its documents. This action cannot be undone, so exercise caution before proceeding."""

    # Construct request model with validation
    try:
        _request = _models.CollectionsDeleteRequest(
            body=_models.CollectionsDeleteRequestBody(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_collection: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/collections.delete"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_collection")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_collection", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_collection",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Collections
@mcp.tool()
async def export_collection(
    id_: str = Field(..., alias="id", description="The unique identifier (UUID) of the collection to export. Required to specify which collection should be exported."),
    format_: Literal["outline-markdown", "json", "html"] | None = Field(None, alias="format", description="Export format for the collection. Choose from outline-markdown (default), json, or html. Determines the structure and format of exported documents."),
) -> dict[str, Any]:
    """Triggers a bulk export of a collection in your preferred format (markdown, JSON, or HTML) along with all attachments. Nested documents are preserved as folders in the resulting zip file. Returns a FileOperation object to track export progress and retrieve the download URL."""

    # Construct request model with validation
    try:
        _request = _models.CollectionsExportRequest(
            body=_models.CollectionsExportRequestBody(format_=format_, id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for export_collection: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/collections.export"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("export_collection")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("export_collection", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="export_collection",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Collections
@mcp.tool()
async def export_all_collections(
    format_: Literal["outline-markdown", "json", "html"] | None = Field(None, alias="format", description="Output format for the exported collections. Choose from outline-markdown for structured text, json for machine-readable data, or html for web-viewable content."),
    include_attachments: bool | None = Field(None, alias="includeAttachments", description="Whether to include file attachments and media in the export. Enabled by default."),
    include_private: bool | None = Field(None, alias="includePrivate", description="Whether to include private collections in the export. Enabled by default."),
) -> dict[str, Any]:
    """Initiates a bulk export of all collections and their documents in your specified format. Returns a FileOperation object that you can poll to track export progress and retrieve the download URL when complete."""

    # Construct request model with validation
    try:
        _request = _models.CollectionsExportAllRequest(
            body=_models.CollectionsExportAllRequestBody(format_=format_, include_attachments=include_attachments, include_private=include_private)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for export_all_collections: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/collections.export_all"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("export_all_collections")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("export_all_collections", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="export_all_collections",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Comments
@mcp.tool()
async def create_comment_on_document(
    document_id: str = Field(..., alias="documentId", description="The unique identifier (UUID format) of the document to which the comment will be added."),
    parent_comment_id: str | None = Field(None, alias="parentCommentId", description="The unique identifier (UUID format) of the parent comment if this is a reply; omit to create a top-level comment."),
    data: dict[str, Any] | None = Field(None, description="The body of the comment."),
    text: str | None = Field(None, description="The body of the comment in markdown."),
) -> dict[str, Any]:
    """Add a new comment or reply to a document. Use parentCommentId to create a reply to an existing comment, or omit it to create a top-level comment."""

    # Construct request model with validation
    try:
        _request = _models.CommentsCreateRequest(
            body=_models.CommentsCreateRequestBody(document_id=document_id, parent_comment_id=parent_comment_id, data=data, text=text)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_comment_on_document: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/comments.create"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_comment_on_document")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_comment_on_document", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_comment_on_document",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Comments
@mcp.tool()
async def get_comment(
    id_: str = Field(..., alias="id", description="The unique identifier of the comment to retrieve, formatted as a UUID."),
    include_anchor_text: bool | None = Field(None, alias="includeAnchorText", description="When enabled, includes the document text that the comment is anchored to in the response, if available."),
) -> dict[str, Any]:
    """Retrieve a specific comment by its unique identifier, with optional inclusion of the anchored document text."""

    # Construct request model with validation
    try:
        _request = _models.CommentsInfoRequest(
            body=_models.CommentsInfoRequestBody(id_=id_, include_anchor_text=include_anchor_text)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/comments.info"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_comment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_comment", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_comment",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Comments
@mcp.tool()
async def update_comment(
    id_: str = Field(..., alias="id", description="The unique identifier of the comment to update, formatted as a UUID."),
    data: dict[str, Any] = Field(..., description="An object containing the comment fields to update. Specify the properties you want to modify in this object."),
) -> dict[str, Any]:
    """Update an existing comment by its unique identifier. Modify comment content and properties using the provided data object."""

    # Construct request model with validation
    try:
        _request = _models.CommentsUpdateRequest(
            body=_models.CommentsUpdateRequestBody(id_=id_, data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/comments.update"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_comment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_comment", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_comment",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Comments
@mcp.tool()
async def delete_comment(id_: str = Field(..., alias="id", description="The unique identifier of the comment to delete, formatted as a UUID.")) -> dict[str, Any]:
    """Deletes a comment by its unique identifier. If the comment is a top-level comment, all of its child replies will be automatically deleted as well."""

    # Construct request model with validation
    try:
        _request = _models.CommentsDeleteRequest(
            body=_models.CommentsDeleteRequestBody(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/comments.delete"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_comment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_comment", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_comment",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Comments
@mcp.tool()
async def list_comments(body: _models.CommentsListBody | None = Field(None, description="Request body containing filter properties to match comments against. Structure and supported fields depend on the API's comment schema and filtering capabilities.")) -> dict[str, Any]:
    """Retrieve all comments matching the specified filter criteria. Use the request body to define which comments to return based on properties like author, date range, or associated resources."""

    # Construct request model with validation
    try:
        _request = _models.CommentsListRequest(
            body=_models.CommentsListRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_comments: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/comments.list"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_comments")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_comments", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_comments",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: DataAttributes
@mcp.tool()
async def get_data_attribute(id_: str = Field(..., alias="id", description="The unique identifier (UUID format) of the data attribute to retrieve.")) -> dict[str, Any]:
    """Retrieve a specific data attribute by its unique identifier. Use this operation to fetch detailed information about a single data attribute."""

    # Construct request model with validation
    try:
        _request = _models.DataAttributesInfoRequest(
            body=_models.DataAttributesInfoRequestBody(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_data_attribute: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/dataAttributes.info"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_data_attribute")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_data_attribute", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_data_attribute",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: DataAttributes
@mcp.tool()
async def list_data_attributes(body: _models.DataAttributesListBody | None = Field(None, description="Optional request body for filtering or configuring the list operation. Consult API documentation for supported query parameters or filter options.")) -> dict[str, Any]:
    """Retrieve a complete list of all available data attributes in the system. Use this operation to discover and enumerate data attributes for reference or integration purposes."""

    # Construct request model with validation
    try:
        _request = _models.DataAttributesListRequest(
            body=_models.DataAttributesListRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_data_attributes: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/dataAttributes.list"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_data_attributes")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_data_attributes", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_data_attributes",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: DataAttributes
@mcp.tool()
async def update_data_attribute(
    id_: str = Field(..., alias="id", description="The unique identifier of the data attribute to update, formatted as a UUID."),
    name: str = Field(..., description="The name of the data attribute (e.g., 'Status'). Used to identify the attribute in the system."),
    description: str | None = Field(None, description="An optional description providing additional context or details about the data attribute's purpose."),
    options: list[_models.DataAttributesUpdateBodyOptionsOptionsItem] | None = Field(None, description="An optional list of valid options for list-type data attributes. Each item represents a selectable value for this attribute."),
    pinned: bool | None = Field(None, description="An optional boolean flag indicating whether this data attribute should be pinned to the top of documents for quick access."),
) -> dict[str, Any]:
    """Update an existing data attribute with new metadata. Only administrators can perform this operation. Note that the data type cannot be changed after the attribute is created."""

    # Construct request model with validation
    try:
        _request = _models.DataAttributesUpdateRequest(
            body=_models.DataAttributesUpdateRequestBody(id_=id_, name=name, description=description, pinned=pinned,
                options=_models.DataAttributesUpdateRequestBodyOptions(options=options) if any(v is not None for v in [options]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_data_attribute: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/dataAttributes.update"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_data_attribute")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_data_attribute", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_data_attribute",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: DataAttributes
@mcp.tool()
async def delete_data_attribute(id_: str = Field(..., alias="id", description="The unique identifier (UUID) of the data attribute to delete.")) -> dict[str, Any]:
    """Permanently delete a data attribute from the system. Only administrators have permission to perform this operation."""

    # Construct request model with validation
    try:
        _request = _models.DataAttributesDeleteRequest(
            body=_models.DataAttributesDeleteRequestBody(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_data_attribute: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/dataAttributes.delete"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_data_attribute")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_data_attribute", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_data_attribute",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Documents
@mcp.tool()
async def get_document(share_id: str | None = Field(None, alias="shareId", description="The unique identifier for a shared document, formatted as a UUID. This shareId allows access to documents shared with you without requiring the original document UUID.")) -> dict[str, Any]:
    """Retrieve a document by its share identifier. Use this operation to access a document that has been shared with you via a shareId."""

    # Construct request model with validation
    try:
        _request = _models.DocumentsInfoRequest(
            body=_models.DocumentsInfoRequestBody(share_id=share_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_document: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/documents.info"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_document")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_document", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_document",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Documents
@mcp.tool()
async def create_document_from_file(
    file_: dict[str, Any] = Field(..., alias="file", description="The file to import as a document. Supported formats include plain text, markdown, docx, csv, tsv, and html."),
    publish: bool | None = Field(None, description="Whether to automatically publish the imported document upon creation. Defaults to unpublished if not specified."),
) -> dict[str, Any]:
    """Create a new document by importing a file. The document is placed at the collection root by default, or as a child document if a parent document ID is specified."""

    # Construct request model with validation
    try:
        _request = _models.DocumentsImportRequest(
            body=_models.DocumentsImportRequestBody(file_=file_, publish=publish)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_document_from_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/documents.import"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_document_from_file")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_document_from_file", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_document_from_file",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: Documents
@mcp.tool()
async def export_document(
    id_: str = Field(..., alias="id", description="The document to export, specified by either its UUID or URL-friendly identifier."),
    paper_size: str | None = Field(None, alias="paperSize", description="Paper size for PDF exports, such as A4 or Letter. Only applicable when exporting to PDF format."),
    signed_urls: float | None = Field(None, alias="signedUrls", description="Duration in seconds that signed URLs for attachment links should remain valid. Determines how long generated attachment links can be accessed."),
    include_child_documents: bool | None = Field(None, alias="includeChildDocuments", description="Include all child documents in the export. When enabled, the response will always be returned as a zip file regardless of other parameters. Defaults to false."),
) -> dict[str, Any]:
    """Export a document in Markdown, HTML, or PDF format, with optional inclusion of child documents as a zip file. The response format is determined by the Accept header."""

    # Construct request model with validation
    try:
        _request = _models.DocumentsExportRequest(
            body=_models.DocumentsExportRequestBody(id_=id_, paper_size=paper_size, signed_urls=signed_urls, include_child_documents=include_child_documents)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for export_document: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/documents.export"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("export_document")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("export_document", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="export_document",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Documents
@mcp.tool()
async def list_documents(body: _models.DocumentsListBody | None = Field(None, description="Optional request body for filtering or configuring the document list retrieval.")) -> dict[str, Any]:
    """Retrieve all documents accessible to the current user, including both published and draft documents."""

    # Construct request model with validation
    try:
        _request = _models.DocumentsListRequest(
            body=_models.DocumentsListRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_documents: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/documents.list"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_documents")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_documents", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_documents",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Documents
@mcp.tool()
async def get_document_children(id_: str = Field(..., alias="id", description="The unique identifier for the document, provided as either a UUID or URL-friendly ID.")) -> dict[str, Any]:
    """Retrieve the nested child structure (tree) of a document. Returns all immediate children and their hierarchical relationships for the specified document."""

    # Construct request model with validation
    try:
        _request = _models.DocumentsDocumentsRequest(
            body=_models.DocumentsDocumentsRequestBody(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_document_children: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/documents.documents"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_document_children")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_document_children", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_document_children",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Documents
@mcp.tool()
async def list_draft_documents(body: _models.DocumentsDraftsBody | None = Field(None, description="Optional request body for filtering or pagination options. Refer to API documentation for supported query parameters.")) -> dict[str, Any]:
    """Retrieve all draft documents belonging to the current user. Returns a collection of documents that have not yet been finalized or published."""

    # Construct request model with validation
    try:
        _request = _models.DocumentsDraftsRequest(
            body=_models.DocumentsDraftsRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_draft_documents: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/documents.drafts"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_draft_documents")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_draft_documents", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_draft_documents",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Documents
@mcp.tool()
async def list_viewed_documents(body: _models.DocumentsViewedBody | None = Field(None, description="Optional request body for filtering or pagination options. If provided, structure should follow the API's standard filtering conventions.")) -> dict[str, Any]:
    """Retrieve a list of all documents recently viewed by the current user, ordered by most recent view first."""

    # Construct request model with validation
    try:
        _request = _models.DocumentsViewedRequest(
            body=_models.DocumentsViewedRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_viewed_documents: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/documents.viewed"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_viewed_documents")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_viewed_documents", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_viewed_documents",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Documents
@mcp.tool()
async def search_documents_with_question(body: _models.DocumentsAnswerQuestionBody | None = Field(None, description="Request payload containing the question and optional search parameters to query against your documents.")) -> dict[str, Any]:
    """Query documents using natural language questions to retrieve direct answers. Results are filtered to documents accessible by your current credentials, and requires AI answers to be enabled in your workspace."""

    # Construct request model with validation
    try:
        _request = _models.DocumentsAnswerQuestionRequest(
            body=_models.DocumentsAnswerQuestionRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_documents_with_question: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/documents.answerQuestion"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_documents_with_question")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_documents_with_question", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_documents_with_question",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Documents
@mcp.tool()
async def search_document_titles(body: _models.DocumentsSearchTitlesBody | None = Field(None, description="Request body containing search parameters such as keywords and optional filters for refining title search results.")) -> dict[str, Any]:
    """Search document titles using keywords for fast, title-only matching. This operation is optimized for title searches and returns results faster than the full documents.search method."""

    # Construct request model with validation
    try:
        _request = _models.DocumentsSearchTitlesRequest(
            body=_models.DocumentsSearchTitlesRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_document_titles: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/documents.search_titles"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_document_titles")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_document_titles", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_document_titles",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Documents
@mcp.tool()
async def search_documents(body: _models.DocumentsSearchBody | None = Field(None, description="Request body containing search parameters such as keywords, filters, and pagination options. Refer to the API documentation for the expected structure and available search filters.")) -> dict[str, Any]:
    """Search across all documents in your workspace using keywords. Results are automatically filtered to only include documents accessible with your current credentials."""

    # Construct request model with validation
    try:
        _request = _models.DocumentsSearchRequest(
            body=_models.DocumentsSearchRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_documents: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/documents.search"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_documents")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_documents", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_documents",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Documents
@mcp.tool()
async def create_document(
    title: str | None = Field(None, description="The title of the document (e.g., 'Welcome to Acme Inc'). If not provided, the document will be created without a title."),
    color: str | None = Field(None, description="The color for the document icon in hexadecimal format (e.g., '#FF5733'). Helps visually distinguish documents in the workspace."),
    template_id: str | None = Field(None, alias="templateId", description="The UUID of a template to use when creating the document. If provided, the document will be initialized with the template's structure and content."),
    publish: bool | None = Field(None, description="Whether to immediately publish the document and make it visible to other workspace members. If false or omitted, the document will be created in draft state."),
    full_width: bool | None = Field(None, alias="fullWidth", description="Whether the document should be displayed in full width mode. If true, the document will span the full available width; otherwise, it uses standard width constraints."),
    data_attributes: list[_models.DocumentsCreateBodyDataAttributesItem] | None = Field(None, alias="dataAttributes", description="An array of data attributes to attach to the document. Each attribute is a key-value pair that can be used for custom metadata or integration purposes."),
    collection_id: str | None = Field(None, alias="collectionId", description="Identifier for the collection. Required to publish unless parentDocumentId is provided"),
    parent_document_id: str | None = Field(None, alias="parentDocumentId", description="Identifier for the parent document. Required to publish unless collectionId is provided"),
    text: str | None = Field(None, description="The body of the document in markdown"),
) -> dict[str, Any]:
    """Create a new document in the workspace, optionally as a child of an existing document. The document can be immediately published and configured with display preferences."""

    # Construct request model with validation
    try:
        _request = _models.DocumentsCreateRequest(
            body=_models.DocumentsCreateRequestBody(title=title, color=color, template_id=template_id, publish=publish, full_width=full_width, data_attributes=data_attributes, collection_id=collection_id, parent_document_id=parent_document_id, text=text)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_document: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/documents.create"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_document")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_document", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_document",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Documents
@mcp.tool()
async def update_document(
    id_: str = Field(..., alias="id", description="The document identifier, accepting either a UUID or URL-friendly ID (e.g., 'hDYep1TPAM'). Required to specify which document to update."),
    title: str | None = Field(None, description="The new title for the document. Updates the document's display name."),
    color: str | None = Field(None, description="The icon color for the document in hexadecimal format (e.g., '#FF5733'). Controls the visual appearance in document lists."),
    full_width: bool | None = Field(None, alias="fullWidth", description="Whether the document should render using the full available width. When enabled, removes side margins for expanded viewing."),
    template_id: str | None = Field(None, alias="templateId", description="The UUID of a template to base this document on. Applies template structure and formatting to the document."),
    insights_enabled: bool | None = Field(None, alias="insightsEnabled", description="Whether to enable insights visibility on the document. When enabled, displays analytics and insights panels."),
    edit_mode: Literal["append", "prepend", "replace"] | None = Field(None, alias="editMode", description="The text update strategy: 'append' adds content to the end, 'prepend' adds to the beginning, or 'replace' overwrites existing content. Determines how text modifications are applied."),
    publish: bool | None = Field(None, description="Whether to publish the document and make it visible to other workspace members. Only applies if the document is currently in draft status."),
    data_attributes: list[_models.DocumentsUpdateBodyDataAttributesItem] | None = Field(None, alias="dataAttributes", description="An array of data attributes to update on the document. Any attributes not included in this array will be removed from the document. Specify as an array of attribute objects."),
    text: str | None = Field(None, description="The body of the document in markdown."),
    collection_id: str | None = Field(None, alias="collectionId", description="Identifier for the collection to move the document to"),
) -> dict[str, Any]:
    """Modify an existing document's properties, including metadata, display settings, and content attributes. Accepts either the document's UUID or URL ID for identification."""

    # Construct request model with validation
    try:
        _request = _models.DocumentsUpdateRequest(
            body=_models.DocumentsUpdateRequestBody(id_=id_, title=title, color=color, full_width=full_width, template_id=template_id, insights_enabled=insights_enabled, edit_mode=edit_mode, publish=publish, data_attributes=data_attributes, text=text, collection_id=collection_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_document: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/documents.update"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_document")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_document", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_document",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Documents
@mcp.tool()
async def create_template_from_document(
    id_: str = Field(..., alias="id", description="The unique identifier (UUID) of the document to use as the template basis."),
    publish: bool = Field(..., description="Whether to publish the newly created template immediately. If true, the template becomes available for use; if false, it remains in draft state."),
) -> dict[str, Any]:
    """Create a new template based on an existing document. The document content and structure become the foundation for the template, which can optionally be published immediately upon creation."""

    # Construct request model with validation
    try:
        _request = _models.DocumentsTemplatizeRequest(
            body=_models.DocumentsTemplatizeRequestBody(id_=id_, publish=publish)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_template_from_document: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/documents.templatize"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_template_from_document")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_template_from_document", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_template_from_document",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Documents
@mcp.tool()
async def unpublish_document(
    id_: str = Field(..., alias="id", description="The document identifier, which can be either a UUID or URL-friendly ID (urlId)."),
    detach_: bool | None = Field(None, alias="detach", description="Whether to detach the document from its collection when unpublishing. Defaults to false, keeping the document in the collection as a draft."),
) -> dict[str, Any]:
    """Unpublish a document to revert it from published status back to draft, optionally removing it from its collection."""

    # Construct request model with validation
    try:
        _request = _models.DocumentsUnpublishRequest(
            body=_models.DocumentsUnpublishRequestBody(id_=id_, detach_=detach_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for unpublish_document: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/documents.unpublish"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("unpublish_document")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("unpublish_document", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="unpublish_document",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Documents
@mcp.tool()
async def move_document(
    id_: str = Field(..., alias="id", description="The unique identifier of the document to move, accepting either a UUID or URL-friendly ID format."),
    index: float | None = Field(None, description="The position index where the document should be placed within its new parent collection. Lower indices position the document earlier in the collection structure."),
    collection_id: str | None = Field(None, alias="collectionId"),
    parent_document_id: str | None = Field(None, alias="parentDocumentId"),
) -> dict[str, Any]:
    """Move a document to a new location within the collection hierarchy. If no parent document is specified, the document will be relocated to the collection root."""

    # Construct request model with validation
    try:
        _request = _models.DocumentsMoveRequest(
            body=_models.DocumentsMoveRequestBody(id_=id_, index=index, collection_id=collection_id, parent_document_id=parent_document_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for move_document: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/documents.move"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("move_document")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("move_document", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="move_document",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Documents
@mcp.tool()
async def archive_document(id_: str = Field(..., alias="id", description="The document identifier, which can be either the UUID or the URL-friendly ID (urlId). Both formats are accepted interchangeably.")) -> dict[str, Any]:
    """Move a document to archived status, removing it from active view while preserving it for future search and restoration. Archived documents remain accessible but are hidden from standard document listings."""

    # Construct request model with validation
    try:
        _request = _models.DocumentsArchiveRequest(
            body=_models.DocumentsArchiveRequestBody(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for archive_document: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/documents.archive"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("archive_document")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("archive_document", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="archive_document",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Documents
@mcp.tool()
async def restore_document(
    id_: str = Field(..., alias="id", description="The document identifier, which can be either a UUID or URL-friendly ID (e.g., 'hDYep1TPAM')."),
    revision_id: str | None = Field(None, alias="revisionId", description="Optional UUID of a specific revision to restore the document to. If not provided, the document is restored to its most recent state."),
) -> dict[str, Any]:
    """Restore a previously archived or deleted document. Optionally restore to a specific revision to recover the document at a previous point in time."""

    # Construct request model with validation
    try:
        _request = _models.DocumentsRestoreRequest(
            body=_models.DocumentsRestoreRequestBody(id_=id_, revision_id=revision_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for restore_document: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/documents.restore"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("restore_document")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("restore_document", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="restore_document",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Documents
@mcp.tool()
async def delete_document(
    id_: str = Field(..., alias="id", description="The document identifier, either as a UUID or URL-friendly ID (e.g., 'hDYep1TPAM')."),
    permanent: bool | None = Field(None, description="When true, permanently destroys the document with no recovery option instead of moving it to trash. Defaults to false (moves to trash)."),
) -> dict[str, Any]:
    """Delete a document by moving it to trash, where it remains recoverable for 30 days before permanent deletion. Optionally bypass trash and permanently destroy the document immediately."""

    # Construct request model with validation
    try:
        _request = _models.DocumentsDeleteRequest(
            body=_models.DocumentsDeleteRequestBody(id_=id_, permanent=permanent)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_document: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/documents.delete"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_document")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_document", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_document",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Documents
@mcp.tool()
async def list_document_users(
    id_: str = Field(..., alias="id", description="The document identifier, either as a UUID or URL-friendly ID (e.g., 'hDYep1TPAM')."),
    query: str | None = Field(None, description="Optional filter to search users by name. When provided, results are filtered to users matching this query string."),
    user_id: str | None = Field(None, alias="userId", description="Optional filter to retrieve a specific user by their UUID. When provided, results are limited to this single user if they have access to the document."),
) -> dict[str, Any]:
    """Retrieve all users with access to a document, including both direct members and inherited access. Use `list_document_memberships` to filter for only direct document members."""

    # Construct request model with validation
    try:
        _request = _models.DocumentsUsersRequest(
            body=_models.DocumentsUsersRequestBody(id_=id_, query=query, user_id=user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_document_users: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/documents.users"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_document_users")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_document_users", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_document_users",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Documents
@mcp.tool()
async def list_document_memberships(
    id_: str = Field(..., alias="id", description="The document identifier, either as a UUID or URL-friendly ID (e.g., 'hDYep1TPAM')."),
    query: str | None = Field(None, description="Optional filter to search memberships by user name. When provided, results are filtered to users matching this query."),
    permission: Literal["read", "read_write"] | None = Field(None, description="Optional filter to return only memberships with a specific permission level: 'read' for view-only access or 'read_write' for edit access."),
) -> dict[str, Any]:
    """Retrieve users with direct membership to a document. This lists only users explicitly granted access to the document; use `documents.users` to see all users with any level of access."""

    # Construct request model with validation
    try:
        _request = _models.DocumentsMembershipsRequest(
            body=_models.DocumentsMembershipsRequestBody(id_=id_, query=query, permission=permission)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_document_memberships: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/documents.memberships"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_document_memberships")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_document_memberships", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_document_memberships",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Documents
@mcp.tool()
async def add_user_to_document(
    id_: str = Field(..., alias="id", description="The document identifier, which can be either a UUID or a URL-friendly ID (urlId)."),
    user_id: str = Field(..., alias="userId", description="The unique identifier (UUID format) of the user to add to the document."),
    permission: Literal["read", "read_write"] | None = Field(None, description="The access level for the user: 'read' for view-only access or 'read_write' for editing permissions. Defaults to 'read' if not specified."),
) -> dict[str, Any]:
    """Grant a user access to a document by adding them as a member with specified permissions. The user will be able to interact with the document according to their assigned permission level."""

    # Construct request model with validation
    try:
        _request = _models.DocumentsAddUserRequest(
            body=_models.DocumentsAddUserRequestBody(id_=id_, user_id=user_id, permission=permission)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_user_to_document: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/documents.add_user"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_user_to_document")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_user_to_document", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_user_to_document",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Documents
@mcp.tool()
async def remove_user_from_document(
    id_: str = Field(..., alias="id", description="The document identifier, which can be either a UUID or a URL-friendly ID (urlId)."),
    user_id: str = Field(..., alias="userId", description="The UUID of the user to remove from the document."),
) -> dict[str, Any]:
    """Remove a user's membership and access from a specified document. The user will no longer be able to view or interact with the document."""

    # Construct request model with validation
    try:
        _request = _models.DocumentsRemoveUserRequest(
            body=_models.DocumentsRemoveUserRequestBody(id_=id_, user_id=user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_user_from_document: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/documents.remove_user"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_user_from_document")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_user_from_document", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_user_from_document",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Documents
@mcp.tool()
async def list_archived_documents(body: _models.DocumentsArchivedBody | None = Field(None, description="Optional request body for filtering or pagination options. Refer to API documentation for supported filter and pagination parameters.")) -> dict[str, Any]:
    """Retrieve all archived documents in the workspace that the current user has access to. Returns a list of archived document records with their metadata."""

    # Construct request model with validation
    try:
        _request = _models.DocumentsArchivedRequest(
            body=_models.DocumentsArchivedRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_archived_documents: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/documents.archived"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_archived_documents")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_archived_documents", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_archived_documents",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Documents
@mcp.tool()
async def list_deleted_documents(body: _models.DocumentsDeletedBody | None = Field(None, description="Optional request body for filtering or pagination options. Refer to API documentation for supported query parameters.")) -> dict[str, Any]:
    """Retrieve a list of all deleted documents in the workspace that the current user has access to. This allows users to view and potentially recover deleted documents."""

    # Construct request model with validation
    try:
        _request = _models.DocumentsDeletedRequest(
            body=_models.DocumentsDeletedRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_deleted_documents: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/documents.deleted"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_deleted_documents")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_deleted_documents", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_deleted_documents",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Documents
@mcp.tool()
async def duplicate_document(
    id_: str = Field(..., alias="id", description="The document to duplicate, specified as either its UUID or URL-friendly identifier."),
    title: str | None = Field(None, description="Optional custom title for the duplicated document. If not provided, the original title will be used."),
    recursive: bool | None = Field(None, description="When enabled, all child documents nested under the original document will also be duplicated, preserving the document hierarchy."),
    publish: bool | None = Field(None, description="When enabled, the newly created document will be published immediately. If disabled, it will be created in draft state."),
) -> dict[str, Any]:
    """Creates a copy of an existing document with an optional new title, and optionally duplicates all child documents in the hierarchy."""

    # Construct request model with validation
    try:
        _request = _models.DocumentsDuplicateRequest(
            body=_models.DocumentsDuplicateRequestBody(id_=id_, title=title, recursive=recursive, publish=publish)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for duplicate_document: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/documents.duplicate"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("duplicate_document")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("duplicate_document", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="duplicate_document",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Documents
@mcp.tool()
async def add_group_to_document(
    id_: str = Field(..., alias="id", description="The document identifier, which can be either a UUID or URL-friendly ID."),
    group_id: str = Field(..., alias="groupId", description="The unique identifier (UUID format) of the group to grant access to the document."),
    permission: Literal["read", "read_write"] | None = Field(None, description="The access level for group members: 'read' for view-only access or 'read_write' for editing permissions. Defaults to 'read' if not specified."),
) -> dict[str, Any]:
    """Grant all members of a group access to a document by adding the group and specifying their permission level."""

    # Construct request model with validation
    try:
        _request = _models.DocumentsAddGroupRequest(
            body=_models.DocumentsAddGroupRequestBody(id_=id_, group_id=group_id, permission=permission)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_group_to_document: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/documents.add_group"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_group_to_document")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_group_to_document", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_group_to_document",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Documents
@mcp.tool()
async def remove_group_from_document(
    id_: str = Field(..., alias="id", description="The document identifier, which can be either a UUID or URL-friendly ID (urlId)."),
    group_id: str = Field(..., alias="groupId", description="The unique identifier (UUID format) of the group whose access should be revoked from the document."),
) -> dict[str, Any]:
    """Revoke all members of a group from accessing a document. This operation removes the group's collective access permissions to the specified document."""

    # Construct request model with validation
    try:
        _request = _models.DocumentsRemoveGroupRequest(
            body=_models.DocumentsRemoveGroupRequestBody(id_=id_, group_id=group_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_group_from_document: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/documents.remove_group"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_group_from_document")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_group_from_document", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_group_from_document",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Documents
@mcp.tool()
async def list_document_group_memberships(body: _models.DocumentsGroupMembershipsBody | None = Field(None, description="Request body containing the document identifier and optional filtering criteria for group memberships.")) -> dict[str, Any]:
    """Retrieve all group memberships associated with a specific document. This allows you to see which groups have access to or are linked with the document."""

    # Construct request model with validation
    try:
        _request = _models.DocumentsGroupMembershipsRequest(
            body=_models.DocumentsGroupMembershipsRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_document_group_memberships: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/documents.group_memberships"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_document_group_memberships")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_document_group_memberships", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_document_group_memberships",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Documents
@mcp.tool()
async def delete_all_trash() -> dict[str, Any]:
    """Permanently delete all documents currently in the trash. This action is irreversible and can only be performed by admin users."""

    # Extract parameters for API call
    _http_path = "/documents.empty_trash"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_all_trash")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_all_trash", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_all_trash",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Events
@mcp.tool()
async def list_events(body: _models.EventsListBody | None = Field(None, description="Optional request body for filtering or configuring the events list query. Specify any desired filters or parameters to narrow down the results.")) -> dict[str, Any]:
    """Retrieve a list of all events from the knowledge base audit trail. Events represent important activities and changes that have occurred within the system."""

    # Construct request model with validation
    try:
        _request = _models.EventsListRequest(
            body=_models.EventsListRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_events: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/events.list"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_events")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_events", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_events",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: FileOperations
@mcp.tool()
async def get_file_operation(id_: str = Field(..., alias="id", description="The unique identifier (UUID) of the file operation to retrieve.")) -> dict[str, Any]:
    """Retrieve the details and current status of a file operation by its unique identifier. Use this to monitor long-running import or export tasks."""

    # Construct request model with validation
    try:
        _request = _models.FileOperationsInfoRequest(
            body=_models.FileOperationsInfoRequestBody(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_file_operation: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/fileOperations.info"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_file_operation")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_file_operation", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_file_operation",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: FileOperations
@mcp.tool()
async def delete_file_operation(id_: str = Field(..., alias="id", description="The unique identifier (UUID) of the file operation to delete.")) -> dict[str, Any]:
    """Delete a file operation and permanently remove its associated files. Use this to clean up completed, failed, or unwanted import/export operations."""

    # Construct request model with validation
    try:
        _request = _models.FileOperationsDeleteRequest(
            body=_models.FileOperationsDeleteRequestBody(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_file_operation: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/fileOperations.delete"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_file_operation")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_file_operation", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_file_operation",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: FileOperations
@mcp.tool()
async def get_file_redirect(id_: str = Field(..., alias="id", description="The unique identifier (UUID format) of the file operation to retrieve.")) -> dict[str, Any]:
    """Retrieve a file by generating a temporary, signed URL with embedded credentials that redirects to the file's storage location."""

    # Construct request model with validation
    try:
        _request = _models.FileOperationsRedirectRequest(
            body=_models.FileOperationsRedirectRequestBody(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_file_redirect: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/fileOperations.redirect"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_file_redirect")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_file_redirect", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_file_redirect",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: FileOperations
@mcp.tool()
async def list_file_operations(body: _models.FileOperationsListBody | None = Field(None, description="Request body containing optional filter criteria such as operation type (import or export) to narrow results. Omit to retrieve all file operations.")) -> dict[str, Any]:
    """Retrieve all file operations (imports and exports) for the current workspace. Results can be filtered by operation type to show only imports, exports, or all operations."""

    # Construct request model with validation
    try:
        _request = _models.FileOperationsListRequest(
            body=_models.FileOperationsListRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_file_operations: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/fileOperations.list"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_file_operations")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_file_operations", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_file_operations",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Groups
@mcp.tool()
async def get_group(id_: str = Field(..., alias="id", description="The unique identifier (UUID) of the group to retrieve.")) -> dict[str, Any]:
    """Retrieve detailed information about a specific group, including its name and member count, using its unique identifier."""

    # Construct request model with validation
    try:
        _request = _models.GroupsInfoRequest(
            body=_models.GroupsInfoRequestBody(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/groups.info"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_group")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_group", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_group",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Groups
@mcp.tool()
async def list_groups(body: _models.GroupsListBody | None = Field(None, description="Optional request body for filtering or configuring the list operation. Refer to API documentation for supported query parameters.")) -> dict[str, Any]:
    """Retrieve all groups in the workspace. Groups organize users and control access permissions for collections."""

    # Construct request model with validation
    try:
        _request = _models.GroupsListRequest(
            body=_models.GroupsListRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_groups: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/groups.list"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_groups")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_groups", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_groups",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Groups
@mcp.tool()
async def create_group(name: str = Field(..., description="The name of the group (e.g., 'Designers'). Used to identify and reference the group in permission assignments and user management.")) -> dict[str, Any]:
    """Create a new group with a specified name. Groups organize users and enable efficient permission management by allowing collection access to be assigned to multiple users simultaneously."""

    # Construct request model with validation
    try:
        _request = _models.GroupsCreateRequest(
            body=_models.GroupsCreateRequestBody(name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/groups.create"
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
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Groups
@mcp.tool()
async def update_group(
    id_: str = Field(..., alias="id", description="The unique identifier of the group to update, formatted as a UUID."),
    name: str = Field(..., description="The new name for the group. Use a descriptive name that reflects the group's purpose or membership."),
) -> dict[str, Any]:
    """Update an existing group's name by providing its unique identifier and the new name."""

    # Construct request model with validation
    try:
        _request = _models.GroupsUpdateRequest(
            body=_models.GroupsUpdateRequestBody(id_=id_, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/groups.update"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_group")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_group", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_group",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Groups
@mcp.tool()
async def delete_group(id_: str = Field(..., alias="id", description="The unique identifier (UUID) of the group to delete.")) -> dict[str, Any]:
    """Permanently delete a group and revoke all member access to collections the group was added to. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.GroupsDeleteRequest(
            body=_models.GroupsDeleteRequestBody(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/groups.delete"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_group")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_group", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_group",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Groups
@mcp.tool()
async def list_group_memberships(body: _models.GroupsMembershipsBody | None = Field(None, description="Request body containing filter criteria, sorting options, and pagination parameters to customize the membership list results.")) -> dict[str, Any]:
    """Retrieve and filter all members belonging to a specific group. Use the request body to specify filtering criteria and pagination options."""

    # Construct request model with validation
    try:
        _request = _models.GroupsMembershipsRequest(
            body=_models.GroupsMembershipsRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_group_memberships: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/groups.memberships"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_group_memberships")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_group_memberships", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_group_memberships",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Groups
@mcp.tool()
async def add_user_to_group(
    id_: str = Field(..., alias="id", description="The unique identifier of the group to which the user will be added. Must be a valid UUID."),
    user_id: str = Field(..., alias="userId", description="The unique identifier of the user to add to the group. Must be a valid UUID."),
) -> dict[str, Any]:
    """Add a user to a group. The user will become a member of the specified group and gain access to group resources."""

    # Construct request model with validation
    try:
        _request = _models.GroupsAddUserRequest(
            body=_models.GroupsAddUserRequestBody(id_=id_, user_id=user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_user_to_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/groups.add_user"
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
async def remove_user_from_group(
    id_: str = Field(..., alias="id", description="The unique identifier (UUID) of the group from which the user will be removed."),
    user_id: str = Field(..., alias="userId", description="The unique identifier (UUID) of the user to remove from the group."),
) -> dict[str, Any]:
    """Remove a user from a group. This operation deletes the membership relationship between the specified user and group."""

    # Construct request model with validation
    try:
        _request = _models.GroupsRemoveUserRequest(
            body=_models.GroupsRemoveUserRequestBody(id_=id_, user_id=user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_user_from_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/groups.remove_user"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_user_from_group")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_user_from_group", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_user_from_group",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: OAuthClients
@mcp.tool()
async def get_oauth_client() -> dict[str, Any]:
    """Retrieve detailed information about a specific OAuth client by providing either its unique identifier or client ID."""

    # Extract parameters for API call
    _http_path = "/oauthClients.info"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_oauth_client")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_oauth_client", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_oauth_client",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: OAuthClients
@mcp.tool()
async def list_oauth_clients(
    offset: float | None = Field(None, description="The number of results to skip before returning items, used for pagination. Defaults to 0 to start from the beginning."),
    limit: float | None = Field(None, description="The maximum number of OAuth clients to return in a single response, used for pagination. Defaults to 25 items per page."),
) -> dict[str, Any]:
    """Retrieve a paginated list of OAuth clients accessible to the authenticated user, including both user-created clients and published clients available to the workspace."""

    # Construct request model with validation
    try:
        _request = _models.OauthClientsListRequest(
            body=_models.OauthClientsListRequestBody(offset=offset, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_oauth_clients: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/oauthClients.list"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_oauth_clients")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_oauth_clients", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_oauth_clients",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: OAuthClients
@mcp.tool()
async def update_oauth_client(
    id_: str = Field(..., alias="id", description="The unique identifier of the OAuth client to update, formatted as a UUID."),
    name: str | None = Field(None, description="The display name for the OAuth client."),
    description: str | None = Field(None, description="A brief description explaining the purpose or functionality of the OAuth client."),
    developer_name: str | None = Field(None, alias="developerName", description="The name of the developer or organization that created this OAuth client."),
    developer_url: str | None = Field(None, alias="developerUrl", description="A URL pointing to the developer's or organization's website."),
    avatar_url: str | None = Field(None, alias="avatarUrl", description="A URL pointing to an image that represents the OAuth client visually."),
    redirect_uris: list[str] | None = Field(None, alias="redirectUris", description="A list of valid redirect URIs where the OAuth client can redirect users after authentication. Each URI should be a complete, valid URL."),
    published: bool | None = Field(None, description="Whether this OAuth client is published and available for use by other workspaces."),
) -> dict[str, Any]:
    """Update an existing OAuth client's configuration, including its name, description, developer information, redirect URIs, and publication status."""

    # Construct request model with validation
    try:
        _request = _models.OauthClientsUpdateRequest(
            body=_models.OauthClientsUpdateRequestBody(id_=id_, name=name, description=description, developer_name=developer_name, developer_url=developer_url, avatar_url=avatar_url, redirect_uris=redirect_uris, published=published)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_oauth_client: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/oauthClients.update"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_oauth_client")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_oauth_client", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_oauth_client",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: OAuthClients
@mcp.tool()
async def rotate_oauth_client_secret(id_: str = Field(..., alias="id", description="The unique identifier of the OAuth client, provided as a UUID.")) -> dict[str, Any]:
    """Generate a new client secret for an OAuth client, immediately invalidating the previous secret. Update your application to use the new secret before the old one expires to avoid authentication failures."""

    # Construct request model with validation
    try:
        _request = _models.OauthClientsRotateSecretRequest(
            body=_models.OauthClientsRotateSecretRequestBody(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for rotate_oauth_client_secret: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/oauthClients.rotate_secret"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("rotate_oauth_client_secret")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("rotate_oauth_client_secret", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="rotate_oauth_client_secret",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: OAuthClients
@mcp.tool()
async def delete_oauth_client(id_: str = Field(..., alias="id", description="The unique identifier (UUID) of the OAuth client to delete.")) -> dict[str, Any]:
    """Permanently delete an OAuth client and revoke all associated access tokens. This action cannot be undone and will immediately invalidate all active sessions using this client."""

    # Construct request model with validation
    try:
        _request = _models.OauthClientsDeleteRequest(
            body=_models.OauthClientsDeleteRequestBody(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_oauth_client: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/oauthClients.delete"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_oauth_client")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_oauth_client", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_oauth_client",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: OAuthAuthentications
@mcp.tool()
async def list_oauth_authentications(
    offset: float | None = Field(None, description="The number of results to skip before returning items, used for pagination. Defaults to 0 to start from the beginning."),
    limit: float | None = Field(None, description="The maximum number of OAuth authentications to return in a single response, used for pagination. Defaults to 25 items per page."),
) -> dict[str, Any]:
    """Retrieve a list of all OAuth authentications accessible to the current user, representing third-party applications that have been authorized to access their account."""

    # Construct request model with validation
    try:
        _request = _models.OauthAuthenticationsListRequest(
            body=_models.OauthAuthenticationsListRequestBody(offset=offset, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_oauth_authentications: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/oauthAuthentications.list"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_oauth_authentications")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_oauth_authentications", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_oauth_authentications",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: OAuthAuthentications
@mcp.tool()
async def revoke_oauth_authentication(
    oauth_client_id: str = Field(..., alias="oauthClientId", description="The unique identifier (UUID format) of the OAuth client application whose access should be revoked."),
    scope: list[str] | None = Field(None, description="Optional list of specific permission scopes to revoke. If omitted, all scopes for the OAuth client will be revoked."),
) -> dict[str, Any]:
    """Revoke an OAuth authentication to remove a third-party application's access to the user's account. This operation permanently disconnects the authorized application."""

    # Construct request model with validation
    try:
        _request = _models.OauthAuthenticationsDeleteRequest(
            body=_models.OauthAuthenticationsDeleteRequestBody(oauth_client_id=oauth_client_id, scope=scope)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for revoke_oauth_authentication: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/oauthAuthentications.delete"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("revoke_oauth_authentication")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("revoke_oauth_authentication", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="revoke_oauth_authentication",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Revisions
@mcp.tool()
async def get_revision(id_: str = Field(..., alias="id", description="The unique identifier of the revision to retrieve, formatted as a UUID.")) -> dict[str, Any]:
    """Retrieve a specific revision of a document by its unique identifier. A revision represents a snapshot of the document at a particular point in time."""

    # Construct request model with validation
    try:
        _request = _models.RevisionsInfoRequest(
            body=_models.RevisionsInfoRequestBody(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_revision: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/revisions.info"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_revision")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_revision", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_revision",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Revisions
@mcp.tool()
async def list_revisions(body: _models.RevisionsListBody | None = Field(None, description="Request body containing the document identifier and optional filtering criteria for revisions to retrieve.")) -> dict[str, Any]:
    """Retrieve all revisions for a specific document. Revisions represent historical snapshots of document content and enable tracking of changes over time."""

    # Construct request model with validation
    try:
        _request = _models.RevisionsListRequest(
            body=_models.RevisionsListRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_revisions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/revisions.list"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_revisions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_revisions", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_revisions",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Shares
@mcp.tool()
async def get_share_by_document(document_id: str | None = Field(None, alias="documentId", description="The unique identifier of the document whose share information should be retrieved. Must be a valid UUID format.")) -> dict[str, Any]:
    """Retrieve detailed information about a share link using its associated document ID. This operation returns the share object containing access permissions and sharing configuration for the specified document."""

    # Construct request model with validation
    try:
        _request = _models.SharesInfoRequest(
            body=_models.SharesInfoRequestBody(document_id=document_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_share_by_document: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/shares.info"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_share_by_document")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_share_by_document", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_share_by_document",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Shares
@mcp.tool()
async def list_shares(body: _models.SharesListBody | None = Field(None, description="Optional request body for filtering or configuring the share list retrieval. Consult the API documentation for supported query parameters or filter options.")) -> dict[str, Any]:
    """Retrieve all share links available in the workspace. This operation returns a complete list of shares that have been created for collaborative access."""

    # Construct request model with validation
    try:
        _request = _models.SharesListRequest(
            body=_models.SharesListRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_shares: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/shares.list"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_shares")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_shares", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_shares",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Shares
@mcp.tool()
async def create_share(document_id: str = Field(..., alias="documentId", description="The unique identifier (UUID) of the document to create a share link for.")) -> dict[str, Any]:
    """Creates a new share link for accessing a document. If multiple shares are requested for the same document using the same API key, the existing share object is returned. Shares are unpublished by default."""

    # Construct request model with validation
    try:
        _request = _models.SharesCreateRequest(
            body=_models.SharesCreateRequestBody(document_id=document_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_share: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/shares.create"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_share")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_share", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_share",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Shares
@mcp.tool()
async def update_share_published_status(
    id_: str = Field(..., alias="id", description="The unique identifier of the share to update, formatted as a UUID."),
    published: bool = Field(..., description="Whether the share should be published (true) and publicly accessible, or unpublished (false) and require authentication."),
) -> dict[str, Any]:
    """Update a share's published status to control access. When published is set to true, the share becomes publicly accessible via its link without requiring authentication."""

    # Construct request model with validation
    try:
        _request = _models.SharesUpdateRequest(
            body=_models.SharesUpdateRequestBody(id_=id_, published=published)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_share_published_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/shares.update"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_share_published_status")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_share_published_status", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_share_published_status",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Shares
@mcp.tool()
async def revoke_share(id_: str = Field(..., alias="id", description="The unique identifier of the share to revoke, formatted as a UUID.")) -> dict[str, Any]:
    """Deactivate a share link to prevent further access to the shared document. Once revoked, the share link becomes inactive and can no longer be used."""

    # Construct request model with validation
    try:
        _request = _models.SharesRevokeRequest(
            body=_models.SharesRevokeRequestBody(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for revoke_share: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/shares.revoke"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("revoke_share")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("revoke_share", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="revoke_share",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Stars
@mcp.tool()
async def add_star(
    document_id: str | None = Field(None, alias="documentId", description="The UUID of the document to star. Either this or collectionId must be provided."),
    index: str | None = Field(None, description="The position in the starred items list where this star should appear. If not specified, the star will be added at the end."),
) -> dict[str, Any]:
    """Add a document or collection to the user's starred items, making it appear in their sidebar for quick access. Either a document ID or collection ID must be provided."""

    # Construct request model with validation
    try:
        _request = _models.StarsCreateRequest(
            body=_models.StarsCreateRequestBody(document_id=document_id, index=index)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_star: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/stars.create"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_star")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_star", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_star",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Stars
@mcp.tool()
async def list_starred_documents(
    offset: float | None = Field(None, description="Number of documents to skip from the beginning of the list, useful for pagination. Defaults to 0 to start from the first document."),
    limit: float | None = Field(None, description="Maximum number of documents to return per request, useful for controlling response size and pagination. Defaults to 25 documents."),
) -> dict[str, Any]:
    """Retrieve all starred documents for the authenticated user. Stars serve as bookmarks for quick access to important documents in the sidebar."""

    # Construct request model with validation
    try:
        _request = _models.StarsListRequest(
            body=_models.StarsListRequestBody(offset=offset, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_starred_documents: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/stars.list"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_starred_documents")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_starred_documents", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_starred_documents",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Stars
@mcp.tool()
async def update_star(
    id_: str = Field(..., alias="id", description="The unique identifier of the starred document to update, formatted as a UUID."),
    index: str = Field(..., description="The new display position for this starred document in the sidebar order. Lower indices appear higher in the list."),
) -> dict[str, Any]:
    """Reorder a starred document in the sidebar by updating its display position relative to other starred items."""

    # Construct request model with validation
    try:
        _request = _models.StarsUpdateRequest(
            body=_models.StarsUpdateRequestBody(id_=id_, index=index)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_star: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/stars.update"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_star")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_star", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_star",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Stars
@mcp.tool()
async def remove_star(id_: str = Field(..., alias="id", description="The unique identifier of the starred document to remove, formatted as a UUID.")) -> dict[str, Any]:
    """Remove a star from a document, deleting it from the user's starred documents list in the sidebar."""

    # Construct request model with validation
    try:
        _request = _models.StarsDeleteRequest(
            body=_models.StarsDeleteRequestBody(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_star: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/stars.delete"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_star")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_star", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_star",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Users
@mcp.tool()
async def send_user_invites(invites: list[_models.Invite] = Field(..., description="Array of user invitations to send. Each invitation specifies the recipient and any relevant details for account creation. Order is preserved as submitted.")) -> dict[str, Any]:
    """Send email invitations to one or more users to join the workspace. Each invitation includes a personalized link that allows recipients to create an account and access the workspace."""

    # Construct request model with validation
    try:
        _request = _models.UsersInviteRequest(
            body=_models.UsersInviteRequestBody(invites=invites)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for send_user_invites: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/users.invite"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("send_user_invites")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("send_user_invites", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="send_user_invites",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Users
@mcp.tool()
async def get_user(id_: str = Field(..., alias="id", description="The unique identifier (UUID) of the user to retrieve.")) -> dict[str, Any]:
    """Retrieve detailed information about a specific user, including their name, email, avatar, and workspace role."""

    # Construct request model with validation
    try:
        _request = _models.UsersInfoRequest(
            body=_models.UsersInfoRequestBody(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/users.info"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_user", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_user",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Users
@mcp.tool()
async def list_users(body: _models.UsersListBody | None = Field(None, description="Optional request body containing filter criteria and pagination options to customize the user list results.")) -> dict[str, Any]:
    """Retrieve and filter all users in the workspace. Supports optional filtering and pagination parameters to narrow results."""

    # Construct request model with validation
    try:
        _request = _models.UsersListRequest(
            body=_models.UsersListRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_users: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/users.list"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_users")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_users", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_users",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Users
@mcp.tool()
async def update_user(
    name: str | None = Field(None, description="The user's display name. Can be any string value."),
    language: str | None = Field(None, description="The user's preferred language, specified as a BCP 47 language tag (e.g., en, en-US, fr-CA)."),
    avatar_url: str | None = Field(None, alias="avatarUrl", description="A URI pointing to the user's avatar image. Must be a valid URL format."),
) -> dict[str, Any]:
    """Update the authenticated user's profile information, including their display name and avatar. Optionally specify a user ID to update a different user's profile."""

    # Construct request model with validation
    try:
        _request = _models.UsersUpdateRequest(
            body=_models.UsersUpdateRequestBody(name=name, language=language, avatar_url=avatar_url)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/users.update"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_user", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_user",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Users
@mcp.tool()
async def update_user_role(
    id_: str = Field(..., alias="id", description="The unique identifier of the user whose role should be updated, formatted as a UUID."),
    role: Literal["admin", "member", "viewer", "guest"] = Field(..., description="The new role to assign to the user. Must be one of: admin, member, viewer, or guest."),
) -> dict[str, Any]:
    """Update a user's role within the system. This operation requires admin authorization and allows changing a user's access level to one of the predefined role types."""

    # Construct request model with validation
    try:
        _request = _models.UsersUpdateRoleRequest(
            body=_models.UsersUpdateRoleRequestBody(id_=id_, role=role)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_user_role: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/users.update_role"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_user_role")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_user_role", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_user_role",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Users
@mcp.tool()
async def suspend_user(id_: str = Field(..., alias="id", description="The unique identifier (UUID) of the user to suspend.")) -> dict[str, Any]:
    """Suspend a user account to prevent sign-in and exclude them from billing calculations. Suspended users retain their data but cannot access the system."""

    # Construct request model with validation
    try:
        _request = _models.UsersSuspendRequest(
            body=_models.UsersSuspendRequestBody(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for suspend_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/users.suspend"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("suspend_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("suspend_user", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="suspend_user",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Users
@mcp.tool()
async def activate_user(id_: str = Field(..., alias="id", description="The UUID of the user to activate.")) -> dict[str, Any]:
    """Reactivate a suspended user to restore their signin access. Activation triggers billing recalculation in hosted environments."""

    # Construct request model with validation
    try:
        _request = _models.UsersActivateRequest(
            body=_models.UsersActivateRequestBody(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for activate_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/users.activate"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("activate_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("activate_user", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="activate_user",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Users
@mcp.tool()
async def delete_user(id_: str = Field(..., alias="id", description="The unique identifier (UUID) of the user to delete.")) -> dict[str, Any]:
    """Permanently delete a user account. Note: Deleted users can be recreated if they sign in via SSO again. Consider suspending the user instead in most cases to preserve data integrity."""

    # Construct request model with validation
    try:
        _request = _models.UsersDeleteRequest(
            body=_models.UsersDeleteRequestBody(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/users.delete"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_user", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_user",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Views
@mcp.tool()
async def list_document_views(
    document_id: str = Field(..., alias="documentId", description="The unique identifier of the document to retrieve views for, formatted as a UUID."),
    include_suspended: bool | None = Field(None, alias="includeSuspended", description="Whether to include view records from users with suspended accounts. Defaults to false, excluding suspended user views."),
) -> dict[str, Any]:
    """Retrieve a list of all users who have viewed a specific document along with the total view count. Optionally include views from suspended users."""

    # Construct request model with validation
    try:
        _request = _models.ViewsListRequest(
            body=_models.ViewsListRequestBody(document_id=document_id, include_suspended=include_suspended)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_document_views: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/views.list"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_document_views")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_document_views", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_document_views",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Views
@mcp.tool()
async def create_view_for_document(document_id: str = Field(..., alias="documentId", description="The unique identifier (UUID) of the document for which to create the view.")) -> dict[str, Any]:
    """Creates a new view for a document. Note: This operation is provided for completeness, but it is recommended to create views through the Outline UI instead of programmatically."""

    # Construct request model with validation
    try:
        _request = _models.ViewsCreateRequest(
            body=_models.ViewsCreateRequestBody(document_id=document_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_view_for_document: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/views.create"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_view_for_document")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_view_for_document", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_view_for_document",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Templates
@mcp.tool()
async def create_template(
    title: str = Field(..., description="The display name for the template. Must be between 1 and 255 characters.", min_length=1, max_length=255),
    data: dict[str, Any] = Field(..., description="The template content structured as a ProseMirror document object, defining the default body and formatting for documents created from this template."),
    color: str | None = Field(None, description="Optional hex color code for the template icon (e.g., #FF5733). Must be a valid 6-digit hexadecimal color.", pattern="^#[0-9A-Fa-f]{6}$"),
) -> dict[str, Any]:
    """Create a new template that serves as a reusable starting point for documents. Templates can be customized with content and styling, and optionally scoped to a specific collection."""

    # Construct request model with validation
    try:
        _request = _models.TemplatesCreateRequest(
            body=_models.TemplatesCreateRequestBody(title=title, data=data, color=color)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/templates.create"
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

# Tags: Templates
@mcp.tool()
async def list_templates(body: _models.TemplatesListBody | None = Field(None, description="Optional request body to filter templates by collection or apply other query criteria.")) -> dict[str, Any]:
    """Retrieve all templates available to the current user, with optional filtering by collection. Templates without an associated collection are accessible workspace-wide."""

    # Construct request model with validation
    try:
        _request = _models.TemplatesListRequest(
            body=_models.TemplatesListRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_templates: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/templates.list"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_templates")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_templates", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_templates",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Templates
@mcp.tool()
async def get_template(id_: str = Field(..., alias="id", description="The unique identifier for the template, provided as either a UUID or a URL-friendly ID string.")) -> dict[str, Any]:
    """Retrieve a specific template by its unique identifier. Accepts either the UUID or URL-friendly ID format."""

    # Construct request model with validation
    try:
        _request = _models.TemplatesInfoRequest(
            body=_models.TemplatesInfoRequestBody(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/templates.info"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_template", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_template",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Templates
@mcp.tool()
async def update_template(
    id_: str = Field(..., alias="id", description="The unique identifier for the template, accepting either a UUID or URL-friendly ID."),
    title: str | None = Field(None, description="The display name for the template."),
    color: str | None = Field(None, description="The color of the template icon specified in hexadecimal format (e.g., #FF5733).", pattern="^#[0-9A-Fa-f]{6}$"),
    full_width: bool | None = Field(None, alias="fullWidth", description="Whether the template should render at full width in the user interface."),
) -> dict[str, Any]:
    """Update an existing template's properties such as title, icon color, and display width by providing its unique identifier."""

    # Construct request model with validation
    try:
        _request = _models.TemplatesUpdateRequest(
            body=_models.TemplatesUpdateRequestBody(id_=id_, title=title, color=color, full_width=full_width)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/templates.update"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_template", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_template",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Templates
@mcp.tool()
async def delete_template(id_: str = Field(..., alias="id", description="The unique identifier for the template, accepting either the UUID or the URL-friendly ID.")) -> dict[str, Any]:
    """Soft-delete a template by its unique identifier. The template can be restored later if needed."""

    # Construct request model with validation
    try:
        _request = _models.TemplatesDeleteRequest(
            body=_models.TemplatesDeleteRequestBody(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/templates.delete"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_template", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_template",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Templates
@mcp.tool()
async def restore_template(id_: str = Field(..., alias="id", description="The unique identifier of the template to restore. Accept either the UUID or the URL-friendly ID (urlId) format.")) -> dict[str, Any]:
    """Restore a previously deleted template using its unique identifier. This operation recovers a soft-deleted template and makes it available for use again."""

    # Construct request model with validation
    try:
        _request = _models.TemplatesRestoreRequest(
            body=_models.TemplatesRestoreRequestBody(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for restore_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/templates.restore"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("restore_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("restore_template", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="restore_template",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Templates
@mcp.tool()
async def duplicate_template(
    id_: str = Field(..., alias="id", description="The unique identifier of the template to duplicate. Accepts either the UUID or the URL-friendly ID (urlId) of the template."),
    title: str | None = Field(None, description="Optional custom title for the duplicated template. If not provided, the original template's title will be used for the copy."),
) -> dict[str, Any]:
    """Create a copy of an existing template with optional customization. You can override the duplicated template's title and specify the target collection for the copy."""

    # Construct request model with validation
    try:
        _request = _models.TemplatesDuplicateRequest(
            body=_models.TemplatesDuplicateRequestBody(id_=id_, title=title)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for duplicate_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/templates.duplicate"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("duplicate_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("duplicate_template", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="duplicate_template",
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
        print("  python outline_server.py", file=sys.stderr)
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

    parser = argparse.ArgumentParser(description="Outline MCP Server")

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
    logger.info("Starting Outline MCP Server")
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

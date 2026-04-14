#!/usr/bin/env python3
"""
Parallel API MCP Server

API Info:
- Contact: Parallel Support <support@parallel.ai> (https://parallel.ai)

Generated: 2026-04-14 18:30:00 UTC
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

BASE_URL = os.getenv("BASE_URL", "https://api.parallel.ai")
SERVER_NAME = "Parallel API"
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
    'ApiKeyAuth',
]

# Initialize authentication handlers at server startup
_auth_handlers: dict[str, Any] = {}
try:
    _auth_handlers["ApiKeyAuth"] = _auth.APIKeyAuth(env_var="API_KEY", location="header", param_name="x-api-key")
    logging.info("Authentication configured: ApiKeyAuth")
except ValueError as e:
    # Extract credential names from error message (first sentence before "Leave empty")
    error_msg = str(e).split("Leave empty")[0].strip()
    logging.warning(f"Credentials for ApiKeyAuth not configured: {error_msg}")
    _auth_handlers["ApiKeyAuth"] = None

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

mcp = FastMCP("Parallel API", middleware=[_JsonCoercionMiddleware()])

# Tags: Search (Beta)
@mcp.tool()
async def search_web(
    mode: Literal["one-shot", "agentic", "fast"] | None = Field(None, description="Execution mode that presets parameter defaults for different use cases: 'one-shot' for comprehensive single-response answers, 'agentic' for token-efficient results in multi-step workflows, or 'fast' for lower-latency results with concise queries. Defaults to 'one-shot'."),
    objective: str | None = Field(None, description="Natural language description of the search objective, including any preferences about source types or content freshness. Either this or search_queries must be provided."),
    search_queries: list[str] | None = Field(None, description="List of traditional keyword search queries to guide the search, optionally including search operators. Either this or objective must be provided."),
    max_results: int | None = Field(None, description="Maximum number of results to return. Defaults to 10 if not specified."),
    max_chars_per_result: int | None = Field(None, description="Maximum characters to include per URL in excerpts. Values below 1000 are automatically increased to 1000. Excerpts may be shorter to prioritize relevance and token efficiency."),
    max_chars_total: int | None = Field(None, description="Maximum total characters across all results combined. Values below 1000 are automatically increased to 1000. This limit applies in addition to the per-result limit to maximize relevance and token efficiency."),
    include_domains: list[str] | None = Field(None, description="List of domains to restrict results to. Accepts full domains (e.g., example.com, subdomain.example.gov) or domain extensions with leading period (e.g., .gov, .edu). Only sources from specified domains will be included."),
    exclude_domains: list[str] | None = Field(None, description="List of domains to exclude from results. Accepts full domains (e.g., example.com, subdomain.example.gov) or domain extensions with leading period (e.g., .gov, .edu). Sources from specified domains will be filtered out."),
    after_date: str | None = Field(None, description="Start date for filtering results, provided as an RFC 3339 date string. Only content published on or after this date will be included."),
) -> dict[str, Any]:
    """Search the web for information based on natural language objectives or keyword queries. Returns relevant results with excerpts optimized for the specified use case."""

    # Construct request model with validation
    try:
        _request = _models.WebSearchV1betaSearchPostRequest(
            body=_models.WebSearchV1betaSearchPostRequestBody(mode=mode, objective=objective, search_queries=search_queries, max_results=max_results,
                excerpts=_models.WebSearchV1betaSearchPostRequestBodyExcerpts(max_chars_per_result=max_chars_per_result, max_chars_total=max_chars_total) if any(v is not None for v in [max_chars_per_result, max_chars_total]) else None,
                source_policy=_models.WebSearchV1betaSearchPostRequestBodySourcePolicy(include_domains=include_domains, exclude_domains=exclude_domains, after_date=after_date) if any(v is not None for v in [include_domains, exclude_domains, after_date]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_web: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1beta/search"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_web")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_web", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_web",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Extract (Beta)
@mcp.tool()
async def extract_content_from_urls(
    urls: list[str] = Field(..., description="List of web URLs to extract content from. Each URL should be a valid HTTP or HTTPS address."),
    objective: str | None = Field(None, description="Optional search objective to focus extraction on specific topics or themes. When provided, helps filter extracted content to relevant sections."),
    search_queries: list[str] | None = Field(None, description="Optional list of keyword search queries to focus extraction. When provided, extracted content will prioritize sections matching these queries."),
    excerpts: bool | _models.ExcerptSettings | None = Field(None, description="Whether to include excerpts from each URL relevant to the search objective and queries. Enabled by default. Most useful when objective or search_queries are specified; redundant if neither is provided."),
    full_content: bool | _models.FullContentSettings | None = Field(None, description="Whether to include the complete content from each URL. Disabled by default. Enable to retrieve full page content; useful when objective and search_queries are not specified."),
) -> dict[str, Any]:
    """Extracts relevant content from specified web URLs, optionally focused on a search objective or keyword queries."""

    # Construct request model with validation
    try:
        _request = _models.BetaExtractV1betaExtractPostRequest(
            body=_models.BetaExtractV1betaExtractPostRequestBody(urls=urls, objective=objective, search_queries=search_queries, excerpts=excerpts, full_content=full_content)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for extract_content_from_urls: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1beta/extract"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("extract_content_from_urls")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("extract_content_from_urls", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="extract_content_from_urls",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tasks v1
@mcp.tool()
async def create_task_run(
    processor: str = Field(..., description="The processor type to execute the task. Use 'base' for standard processing."),
    output_schema: Any | _models.TextSchema | _models.AutoSchema | str = Field(..., description="JSON schema or text description defining the desired output structure and content. Field descriptions determine the form and content of the response. A plain string is treated as a text schema."),
    input_: str | dict[str, Any] = Field(..., alias="input", description="The input data for the task, provided as either plain text or a JSON object matching the input schema."),
    url: str = Field(..., description="Webhook URL where task run notifications will be sent."),
    metadata: dict[str, str | int | float | bool] | None = Field(None, description="Custom key-value metadata to attach to the run. Keys and values must be strings, with keys limited to 16 characters and values to 512 characters."),
    include_domains: list[str] | None = Field(None, description="Restrict results to specific domains. Accepts full domains (e.g., example.com, subdomain.example.gov) or domain extensions with leading period (e.g., .gov, .edu, .co.uk). Only sources matching these domains will be included."),
    exclude_domains: list[str] | None = Field(None, description="Exclude results from specific domains. Accepts full domains (e.g., example.com, subdomain.example.gov) or domain extensions with leading period (e.g., .gov, .edu, .co.uk). Sources matching these domains will be filtered out."),
    after_date: str | None = Field(None, description="Filter results to content published on or after this date. Provide as an RFC 3339 date string in YYYY-MM-DD format."),
    input_schema: str | Any | _models.TextSchema | None = Field(None, description="Optional JSON schema or text description of the expected input format. A plain string is treated as a text schema with that description."),
    previous_interaction_id: str | None = Field(None, description="Reference to a previous interaction to use as context for this task run, enabling multi-turn workflows."),
    mcp_servers: list[_models.McpServer] | None = Field(None, description="Optional list of MCP servers to use for this run. Requires 'mcp-server-2025-07-17' in the parallel-beta header to enable."),
    enable_events: bool | None = Field(None, description="Enable or disable progress event tracking for this run. When true, execution progress events are recorded and accessible via the Task Run events endpoint. Defaults to true for premium processors. Requires 'events-sse-2025-07-24' in the parallel-beta header to enable."),
    event_types: list[Literal["task_run.status"]] | None = Field(None, description="List of event types that trigger webhook notifications. Defaults to empty array (no notifications sent)."),
) -> dict[str, Any]:
    """Initiates a new task run that processes input according to a specified processor and output schema. Returns immediately with a run object in 'queued' status. Supports optional filtering by domain, date range, and webhook notifications."""

    # Construct request model with validation
    try:
        _request = _models.TasksRunsPostV1TasksRunsPostRequest(
            body=_models.TasksRunsPostV1TasksRunsPostRequestBody(processor=processor, metadata=metadata, input_=input_, previous_interaction_id=previous_interaction_id, mcp_servers=mcp_servers, enable_events=enable_events,
                source_policy=_models.TasksRunsPostV1TasksRunsPostRequestBodySourcePolicy(include_domains=include_domains, exclude_domains=exclude_domains, after_date=after_date) if any(v is not None for v in [include_domains, exclude_domains, after_date]) else None,
                task_spec=_models.TasksRunsPostV1TasksRunsPostRequestBodyTaskSpec(output_schema=output_schema, input_schema=input_schema),
                webhook=_models.TasksRunsPostV1TasksRunsPostRequestBodyWebhook(url=url, event_types=event_types))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_task_run: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/tasks/runs"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_task_run")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_task_run", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_task_run",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tasks v1
@mcp.tool()
async def get_task_run(run_id: str = Field(..., description="The unique identifier of the task run to retrieve.")) -> dict[str, Any]:
    """Retrieve the status and details of a specific task run by its ID. Use the `/result` endpoint to access the run's output results."""

    # Construct request model with validation
    try:
        _request = _models.TasksRunsGetV1TasksRunsRunIdGetRequest(
            path=_models.TasksRunsGetV1TasksRunsRunIdGetRequestPath(run_id=run_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_task_run: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/tasks/runs/{run_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/tasks/runs/{run_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_task_run")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_task_run", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_task_run",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tasks v1
@mcp.tool()
async def get_task_run_input(run_id: str = Field(..., description="The unique identifier of the task run whose input you want to retrieve.")) -> dict[str, Any]:
    """Retrieves the input data that was provided to a specific task run. Use this to inspect what parameters or data were passed when the task run was executed."""

    # Construct request model with validation
    try:
        _request = _models.TasksRunsInputGetV1TasksRunsRunIdInputGetRequest(
            path=_models.TasksRunsInputGetV1TasksRunsRunIdInputGetRequestPath(run_id=run_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_task_run_input: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/tasks/runs/{run_id}/input", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/tasks/runs/{run_id}/input"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_task_run_input")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_task_run_input", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_task_run_input",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tasks v1
@mcp.tool()
async def get_task_run_result(run_id: str = Field(..., description="The unique identifier of the task run whose result you want to retrieve.")) -> dict[str, Any]:
    """Retrieves the result of a completed task run by its ID. This operation blocks until the task run finishes executing, then returns the final result."""

    # Construct request model with validation
    try:
        _request = _models.TasksRunsResultGetV1TasksRunsRunIdResultGetRequest(
            path=_models.TasksRunsResultGetV1TasksRunsRunIdResultGetRequestPath(run_id=run_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_task_run_result: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/tasks/runs/{run_id}/result", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/tasks/runs/{run_id}/result"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_task_run_result")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_task_run_result", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_task_run_result",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tasks v1
@mcp.tool()
async def stream_task_run_events(run_id: str = Field(..., description="The unique identifier of the task run for which to retrieve events.")) -> dict[str, Any]:
    """Stream events for a specific task run, including progress updates and state changes. Event frequency is reduced for task runs created without event streaming enabled."""

    # Construct request model with validation
    try:
        _request = _models.TasksRunsEventsGetV1betaTasksRunsRunIdEventsGetRequest(
            path=_models.TasksRunsEventsGetV1betaTasksRunsRunIdEventsGetRequestPath(run_id=run_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for stream_task_run_events: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1beta/tasks/runs/{run_id}/events", _request.path.model_dump(by_alias=True)) if _request.path else "/v1beta/tasks/runs/{run_id}/events"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("stream_task_run_events")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("stream_task_run_events", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="stream_task_run_events",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tasks (Beta)
@mcp.tool()
async def create_task_group(metadata: dict[str, str | int | float | bool] | None = Field(None, description="Optional custom metadata to attach to the task group for organizational or tracking purposes. This metadata is stored with the group and can be used to add context or labels relevant to your use case.")) -> dict[str, Any]:
    """Creates a new TaskGroup to organize and monitor multiple task runs together. Use this to establish a logical grouping for related tasks that should be tracked as a unit."""

    # Construct request model with validation
    try:
        _request = _models.TasksTaskgroupsPostV1betaTasksGroupsPostRequest(
            body=_models.TasksTaskgroupsPostV1betaTasksGroupsPostRequestBody(metadata=metadata)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_task_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1beta/tasks/groups"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_task_group")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_task_group", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_task_group",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tasks (Beta)
@mcp.tool()
async def get_taskgroup(taskgroup_id: str = Field(..., description="The unique identifier of the TaskGroup to retrieve.")) -> dict[str, Any]:
    """Retrieves a TaskGroup and its aggregated status across all runs, providing a summary view of the group's execution state."""

    # Construct request model with validation
    try:
        _request = _models.TasksTaskgroupsGetV1betaTasksGroupsTaskgroupIdGetRequest(
            path=_models.TasksTaskgroupsGetV1betaTasksGroupsTaskgroupIdGetRequestPath(taskgroup_id=taskgroup_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_taskgroup: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1beta/tasks/groups/{taskgroup_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1beta/tasks/groups/{taskgroup_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_taskgroup")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_taskgroup", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_taskgroup",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tasks (Beta)
@mcp.tool()
async def stream_task_group_events(
    taskgroup_id: str = Field(..., description="The unique identifier of the TaskGroup whose events should be streamed."),
    last_event_id: str | None = Field(None, description="Optional event ID to resume streaming from a specific point, useful for recovering from connection interruptions without missing events."),
) -> dict[str, Any]:
    """Streams real-time events from a TaskGroup, including status updates and run completions. The connection remains open for up to one hour while at least one run in the group is active."""

    # Construct request model with validation
    try:
        _request = _models.TasksSessionsEventsGetV1betaTasksGroupsTaskgroupIdEventsGetRequest(
            path=_models.TasksSessionsEventsGetV1betaTasksGroupsTaskgroupIdEventsGetRequestPath(taskgroup_id=taskgroup_id),
            query=_models.TasksSessionsEventsGetV1betaTasksGroupsTaskgroupIdEventsGetRequestQuery(last_event_id=last_event_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for stream_task_group_events: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1beta/tasks/groups/{taskgroup_id}/events", _request.path.model_dump(by_alias=True)) if _request.path else "/v1beta/tasks/groups/{taskgroup_id}/events"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("stream_task_group_events")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("stream_task_group_events", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="stream_task_group_events",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tasks (Beta)
@mcp.tool()
async def list_task_group_runs(
    taskgroup_id: str = Field(..., description="The unique identifier of the TaskGroup whose runs should be retrieved."),
    last_event_id: str | None = Field(None, description="Resume a stream from a specific point by providing the event_id of the last received event. The stream will continue from the next event after this cursor."),
    status: Literal["queued", "action_required", "running", "completed", "failed", "cancelling", "cancelled"] | None = Field(None, description="Filter runs by their current status: queued (waiting to start), action_required (awaiting user input), running (in progress), completed (finished successfully), failed (encountered an error), cancelling (cancellation in progress), or cancelled (cancellation completed)."),
    include_input: bool | None = Field(None, description="Include the input data for each run in the stream response. Defaults to false."),
    include_output: bool | None = Field(None, description="Include the output data for each run in the stream response. Defaults to false."),
) -> dict[str, Any]:
    """Retrieves all task runs within a TaskGroup as a resumable stream, with optional inclusion of run inputs and outputs."""

    # Construct request model with validation
    try:
        _request = _models.TasksTaskgroupsRunsGetV1betaTasksGroupsTaskgroupIdRunsGetRequest(
            path=_models.TasksTaskgroupsRunsGetV1betaTasksGroupsTaskgroupIdRunsGetRequestPath(taskgroup_id=taskgroup_id),
            query=_models.TasksTaskgroupsRunsGetV1betaTasksGroupsTaskgroupIdRunsGetRequestQuery(last_event_id=last_event_id, status=status, include_input=include_input, include_output=include_output)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_task_group_runs: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1beta/tasks/groups/{taskgroup_id}/runs", _request.path.model_dump(by_alias=True)) if _request.path else "/v1beta/tasks/groups/{taskgroup_id}/runs"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_task_group_runs")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_task_group_runs", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_task_group_runs",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tasks (Beta)
@mcp.tool()
async def add_runs_to_task_group(
    taskgroup_id: str = Field(..., description="The unique identifier of the TaskGroup to which runs will be added."),
    output_schema: Any | _models.TextSchema | _models.AutoSchema | str = Field(..., description="JSON schema or text description defining the desired output structure from each task. Field descriptions in the schema will determine the form and content of task responses. A plain string is treated as a text schema with that description."),
    inputs: list[_models.BetaTaskRunInput] = Field(..., description="Array of task run configurations to execute. Each item represents a single task run with its input parameters. Up to 1,000 runs can be added per request; for larger batches, split across multiple requests."),
    input_schema: str | Any | _models.TextSchema | None = Field(None, description="Optional JSON schema or text description specifying the expected input structure for tasks. A plain string is treated as a text schema with that description."),
) -> dict[str, Any]:
    """Initiates multiple task runs within a TaskGroup, allowing batch execution of tasks with specified inputs and output requirements."""

    # Construct request model with validation
    try:
        _request = _models.TasksTaskgroupsRunsPostV1betaTasksGroupsTaskgroupIdRunsPostRequest(
            path=_models.TasksTaskgroupsRunsPostV1betaTasksGroupsTaskgroupIdRunsPostRequestPath(taskgroup_id=taskgroup_id),
            body=_models.TasksTaskgroupsRunsPostV1betaTasksGroupsTaskgroupIdRunsPostRequestBody(inputs=inputs,
                default_task_spec=_models.TasksTaskgroupsRunsPostV1betaTasksGroupsTaskgroupIdRunsPostRequestBodyDefaultTaskSpec(output_schema=output_schema, input_schema=input_schema))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_runs_to_task_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1beta/tasks/groups/{taskgroup_id}/runs", _request.path.model_dump(by_alias=True)) if _request.path else "/v1beta/tasks/groups/{taskgroup_id}/runs"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_runs_to_task_group")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_runs_to_task_group", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_runs_to_task_group",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tasks (Beta)
@mcp.tool()
async def get_task_group_run(
    taskgroup_id: str = Field(..., description="The unique identifier of the task group containing the run."),
    run_id: str = Field(..., description="The unique identifier of the run whose status and details should be retrieved."),
) -> dict[str, Any]:
    """Retrieves the status and details of a specific task group run by its run ID. The run result data is available separately via the `/result` endpoint."""

    # Construct request model with validation
    try:
        _request = _models.TasksTaskgroupsRunsIdGetV1betaTasksGroupsTaskgroupIdRunsRunIdGetRequest(
            path=_models.TasksTaskgroupsRunsIdGetV1betaTasksGroupsTaskgroupIdRunsRunIdGetRequestPath(taskgroup_id=taskgroup_id, run_id=run_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_task_group_run: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1beta/tasks/groups/{taskgroup_id}/runs/{run_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1beta/tasks/groups/{taskgroup_id}/runs/{run_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_task_group_run")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_task_group_run", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_task_group_run",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: FindAll API (Beta)
@mcp.tool()
async def create_findall_spec_from_objective(objective: str = Field(..., description="A natural language description of what you want to find. Describe your search goal in plain English, such as company characteristics, funding criteria, or other business attributes you're looking for.")) -> dict[str, Any]:
    """Converts a natural language search objective into a structured FindAll specification that can be used to execute targeted searches. The generated spec serves as a customizable starting point and can be further refined by the user."""

    # Construct request model with validation
    try:
        _request = _models.IngestFindallRunV1betaFindallIngestPostRequest(
            body=_models.IngestFindallRunV1betaFindallIngestPostRequestBody(objective=objective)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_findall_spec_from_objective: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1beta/findall/ingest"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    # Constant headers (from schemas.patch.json add_constant_headers) — fixed values, not agent-configurable
    _http_headers["parallel-beta"] = "findall-2025-09-15"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_findall_spec_from_objective")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_findall_spec_from_objective", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_findall_spec_from_objective",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: FindAll API (Beta)
@mcp.tool()
async def create_findall_run(
    objective: str = Field(..., description="The goal or search objective described in natural language for the FindAll run."),
    entity_type: str = Field(..., description="The category or type of entity to search for (e.g., company, person, product)."),
    match_conditions: list[_models.MatchCondition] = Field(..., description="Array of conditions that entities must satisfy to be included in results. Order and format depend on the entity type and generator used."),
    generator: Literal["base", "core", "pro", "preview"] = Field(..., description="The search algorithm tier to use: 'base' for basic matching, 'core' for standard accuracy, 'pro' for advanced matching, or 'preview' for experimental features."),
    match_limit: int = Field(..., description="Maximum number of matching entities to return, between 5 and 1000 inclusive."),
    exclude_list: list[_models.ExcludeCandidate] | None = Field(None, description="Optional list of entity names or IDs to exclude from the search results."),
    metadata: dict[str, str | int | float | bool] | None = Field(None, description="Optional custom metadata object to attach to the FindAll run for tracking or reference purposes."),
) -> dict[str, Any]:
    """Initiates a FindAll run to search for entities matching specified criteria. Returns immediately with a queued run object; use the returned run ID to poll status, stream events, or receive webhook notifications as the search progresses."""

    # Construct request model with validation
    try:
        _request = _models.FindallRunsV1V1betaFindallRunsPostRequest(
            body=_models.FindallRunsV1V1betaFindallRunsPostRequestBody(objective=objective, entity_type=entity_type, match_conditions=match_conditions, generator=generator, match_limit=match_limit, exclude_list=exclude_list, metadata=metadata)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_findall_run: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1beta/findall/runs"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    # Constant headers (from schemas.patch.json add_constant_headers) — fixed values, not agent-configurable
    _http_headers["parallel-beta"] = "findall-2025-09-15"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_findall_run")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_findall_run", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_findall_run",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Monitor
@mcp.tool()
async def list_monitors(
    monitor_id: str | None = Field(None, description="Cursor for pagination—specify a monitor ID to start listing after that point in lexicographic order. Useful for fetching subsequent pages of results."),
    limit: int | None = Field(None, description="Maximum number of monitors to return per request, between 1 and 10,000. Omit to retrieve all monitors at once.", ge=1, le=10000),
) -> dict[str, Any]:
    """Retrieve all active monitors for the user with their current configuration and status. Supports cursor-based pagination to efficiently browse large monitor lists."""

    # Construct request model with validation
    try:
        _request = _models.ListMonitorsV1alphaMonitorsGetRequest(
            query=_models.ListMonitorsV1alphaMonitorsGetRequestQuery(monitor_id=monitor_id, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_monitors: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1alpha/monitors"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_monitors")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_monitors", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_monitors",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Monitor
@mcp.tool()
async def create_monitor(
    query: str = Field(..., description="The search query to monitor for material changes. This query will be executed periodically according to the monitor's frequency."),
    webhook: _models.MonitorWebhook | None = Field(None, description="Optional webhook URL that will receive notifications whenever the monitor executes, including execution results and any detected changes."),
    metadata: dict[str, str] | None = Field(None, description="Optional custom metadata object to store application-specific context with the monitor. This metadata is returned in webhook notifications and GET requests, allowing you to correlate monitor responses with your application's internal objects (e.g., storing a Slack thread ID to route notifications to the correct conversation)."),
    output_schema: Any | None = Field(None, description="Optional schema definition for structuring the monitor's output events. Defines how results should be formatted in webhook notifications."),
    frequency: str | None = Field(None, description="How often the monitor should execute, specified as a number followed by a time unit: 'h' for hours, 'd' for days, or 'w' for weeks (e.g., '1h', '2d', '1w'). Must be between 1 hour and 30 days inclusive."),
    cadence: Literal["daily", "every_two_weeks", "hourly", "weekly"] | None = Field(None, description="Deprecated: use the 'frequency' field instead. Predefined execution cadence options: hourly, daily, weekly, or every two weeks."),
) -> dict[str, Any]:
    """Create a web monitor that periodically executes a search query at a specified frequency and sends updates to an optional webhook. The monitor runs immediately upon creation and then continues according to the configured schedule."""

    # Construct request model with validation
    try:
        _request = _models.CreateMonitorV1alphaMonitorsPostRequest(
            body=_models.CreateMonitorV1alphaMonitorsPostRequestBody(query=query, webhook=webhook, metadata=metadata, output_schema=output_schema, frequency=frequency, cadence=cadence)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_monitor: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1alpha/monitors"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_monitor")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_monitor", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_monitor",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Monitor
@mcp.tool()
async def list_monitors_paginated(
    cursor: str | None = Field(None, description="Opaque token for cursor-based pagination. Omit this parameter to start from the most recently created monitor, or provide the `next_cursor` value from a previous response to fetch the next page of results."),
    limit: int | None = Field(None, description="Maximum number of monitors to return per page. Must be between 1 and 10,000, defaults to 100 if not specified.", ge=1, le=10000),
) -> dict[str, Any]:
    """Retrieve a paginated list of active monitors ordered by creation time, newest first. Use cursor-based pagination to navigate through results."""

    # Construct request model with validation
    try:
        _request = _models.ListMonitorsPaginatedV1alphaMonitorsListGetRequest(
            query=_models.ListMonitorsPaginatedV1alphaMonitorsListGetRequestQuery(cursor=cursor, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_monitors_paginated: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1alpha/monitors/list"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_monitors_paginated")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_monitors_paginated", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_monitors_paginated",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Monitor
@mcp.tool()
async def get_monitor(monitor_id: str = Field(..., description="The unique identifier of the monitor to retrieve.")) -> dict[str, Any]:
    """Retrieve a specific monitor by its ID. Returns the complete monitor configuration including status, cadence, input settings, and webhook configuration."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveMonitorV1alphaMonitorsMonitorIdGetRequest(
            path=_models.RetrieveMonitorV1alphaMonitorsMonitorIdGetRequestPath(monitor_id=monitor_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_monitor: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1alpha/monitors/{monitor_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1alpha/monitors/{monitor_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_monitor")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_monitor", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_monitor",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Monitor
@mcp.tool()
async def update_monitor(
    monitor_id: str = Field(..., description="The unique identifier of the monitor to update."),
    url: str = Field(..., description="The webhook URL where monitor notifications will be sent. Must be a valid HTTPS or HTTP endpoint."),
    query: str | None = Field(None, description="Updated search query for the monitor. Use for minor prompt and instruction refinements only; major query changes may affect change detection accuracy since the monitor compares new results against previously cached results."),
    frequency: str | None = Field(None, description="Updated check frequency for the monitor. Specify as a number followed by a unit: 'h' for hours, 'd' for days, or 'w' for weeks. Must be between 1 hour and 30 days inclusive."),
    event_types: list[Literal["monitor.event.detected", "monitor.execution.completed", "monitor.execution.failed"]] | None = Field(None, description="Event types that should trigger webhook notifications. Specify as an array of event type identifiers."),
    metadata: dict[str, str] | None = Field(None, description="Custom metadata object to associate with the monitor. This metadata is included in all webhook notifications, allowing you to correlate monitor events with corresponding objects in your application."),
) -> dict[str, Any]:
    """Update an existing monitor's configuration, including its search query, check frequency, webhook URL, and associated metadata. At least one field must be provided to apply changes."""

    # Construct request model with validation
    try:
        _request = _models.UpdateMonitorV1alphaMonitorsMonitorIdPostRequest(
            path=_models.UpdateMonitorV1alphaMonitorsMonitorIdPostRequestPath(monitor_id=monitor_id),
            body=_models.UpdateMonitorV1alphaMonitorsMonitorIdPostRequestBody(query=query, frequency=frequency, metadata=metadata,
                webhook=_models.UpdateMonitorV1alphaMonitorsMonitorIdPostRequestBodyWebhook(url=url, event_types=event_types))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_monitor: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1alpha/monitors/{monitor_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1alpha/monitors/{monitor_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_monitor")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_monitor", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_monitor",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Monitor
@mcp.tool()
async def delete_monitor(monitor_id: str = Field(..., description="The unique identifier of the monitor to delete.")) -> dict[str, Any]:
    """Permanently delete a monitor and stop all its future executions. Deleted monitors cannot be updated or retrieved."""

    # Construct request model with validation
    try:
        _request = _models.DeleteMonitorV1alphaMonitorsMonitorIdDeleteRequest(
            path=_models.DeleteMonitorV1alphaMonitorsMonitorIdDeleteRequestPath(monitor_id=monitor_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_monitor: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1alpha/monitors/{monitor_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1alpha/monitors/{monitor_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_monitor")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_monitor", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_monitor",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Monitor
@mcp.tool()
async def get_event_group(
    monitor_id: str = Field(..., description="The unique identifier of the monitor that contains the event group."),
    event_group_id: str = Field(..., description="The unique identifier of the event group to retrieve."),
) -> dict[str, Any]:
    """Retrieve a specific event group associated with a monitor. The response contains event items that represent individual events within the group."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveEventGroupV1alphaMonitorsMonitorIdEventGroupsEventGroupIdGetRequest(
            path=_models.RetrieveEventGroupV1alphaMonitorsMonitorIdEventGroupsEventGroupIdGetRequestPath(monitor_id=monitor_id, event_group_id=event_group_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_event_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1alpha/monitors/{monitor_id}/event_groups/{event_group_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1alpha/monitors/{monitor_id}/event_groups/{event_group_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_event_group")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_event_group", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_event_group",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Monitor
@mcp.tool()
async def list_monitor_events(
    monitor_id: str = Field(..., description="The unique identifier of the monitor for which to retrieve events."),
    lookback_period: str | None = Field(None, description="The time window to search for events, specified as a duration (e.g., '10d' for 10 days, '1w' for 1 week). Supports day and week increments with a minimum of 1 day. Defaults to 10 days if not specified."),
) -> dict[str, Any]:
    """Retrieve events for a specific monitor, including errors and material changes from up to the last 300 event groups. Events are returned in reverse chronological order with the most recent first."""

    # Construct request model with validation
    try:
        _request = _models.ListMonitorEventsV1alphaMonitorsMonitorIdEventsGetRequest(
            path=_models.ListMonitorEventsV1alphaMonitorsMonitorIdEventsGetRequestPath(monitor_id=monitor_id),
            query=_models.ListMonitorEventsV1alphaMonitorsMonitorIdEventsGetRequestQuery(lookback_period=lookback_period)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_monitor_events: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1alpha/monitors/{monitor_id}/events", _request.path.model_dump(by_alias=True)) if _request.path else "/v1alpha/monitors/{monitor_id}/events"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_monitor_events")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_monitor_events", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_monitor_events",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Monitor
@mcp.tool()
async def simulate_monitor_event(
    monitor_id: str = Field(..., description="The unique identifier of the monitor to simulate an event for."),
    event_type: Literal["monitor.event.detected", "monitor.execution.completed", "monitor.execution.failed"] | None = Field(None, description="The type of event to simulate. Defaults to `monitor.event.detected` if not specified. Valid options are: `monitor.event.detected` (standard event detection), `monitor.execution.completed` (successful execution), or `monitor.execution.failed` (execution failure)."),
    body: str | None = Field(None, description="Optional binary payload data to include with the simulated event."),
) -> dict[str, Any]:
    """Simulate sending an event to a monitor to test its event handling and triggering behavior. Useful for validating monitor configurations without waiting for real events."""

    # Construct request model with validation
    try:
        _request = _models.SimulateEventV1alphaMonitorsMonitorIdSimulateEventPostRequest(
            path=_models.SimulateEventV1alphaMonitorsMonitorIdSimulateEventPostRequestPath(monitor_id=monitor_id),
            query=_models.SimulateEventV1alphaMonitorsMonitorIdSimulateEventPostRequestQuery(event_type=event_type),
            body=_models.SimulateEventV1alphaMonitorsMonitorIdSimulateEventPostRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for simulate_monitor_event: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1alpha/monitors/{monitor_id}/simulate_event", _request.path.model_dump(by_alias=True)) if _request.path else "/v1alpha/monitors/{monitor_id}/simulate_event"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("simulate_monitor_event")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("simulate_monitor_event", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="simulate_monitor_event",
        method="POST",
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
        print("  python parallel_api_server.py", file=sys.stderr)
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

    parser = argparse.ArgumentParser(description="Parallel API MCP Server")

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
    logger.info("Starting Parallel API MCP Server")
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

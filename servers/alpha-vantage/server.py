#!/usr/bin/env python3
"""
Alpha Vantage MCP Server

API Info:
- Contact: Alpha Vantage Support <support@alphavantage.co> (https://www.alphavantage.co/support/)
- Terms of Service: https://www.alphavantage.co/terms_of_service/

Generated: 2026-04-09 17:13:40 UTC
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

BASE_URL = os.getenv("BASE_URL", "https://www.alphavantage.co")
SERVER_NAME = "Alpha Vantage"
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
    'apiKey',
]

# Initialize authentication handlers at server startup
_auth_handlers: dict[str, Any] = {}
try:
    _auth_handlers["apiKey"] = _auth.APIKeyAuth(env_var="API_KEY", location="query", param_name="apikey")
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

mcp = FastMCP("Alpha Vantage", middleware=[_JsonCoercionMiddleware()])

# Tags: Core Stock APIs
@mcp.tool()
async def get_intraday_time_series(
    function: Literal["TIME_SERIES_INTRADAY"] = Field(..., description="The time series function to query. Must be TIME_SERIES_INTRADAY for intraday data."),
    symbol: str = Field(..., description="The stock symbol or ticker of the equity to retrieve data for (e.g., IBM, AAPL)."),
    interval: Literal["1min", "5min", "15min", "30min", "60min"] = Field(..., description="The time interval between consecutive data points. Choose from 1-minute, 5-minute, 15-minute, 30-minute, or 60-minute intervals."),
    adjusted: bool | None = Field(None, description="Whether to adjust historical prices for stock splits and dividend events. Defaults to true for adjusted data."),
    extended_hours: bool | None = Field(None, description="Whether to include pre-market and post-market trading hours in the results. Defaults to true."),
    month: str | None = Field(None, description="Query a specific month of historical data in YYYY-MM format (e.g., 2009-01). Supported from January 2000 onwards.", pattern="^\\d{4}-\\d{2}$"),
    outputsize: Literal["compact", "full"] | None = Field(None, description="Control the amount of data returned. Use 'compact' for the latest 100 data points, or 'full' for trailing 30 days of data (or the entire month if a specific month is requested). Defaults to compact."),
) -> dict[str, Any]:
    """Retrieve intraday OHLCV (open, high, low, close, volume) time series data for an equity, with support for 20+ years of historical data and optional adjustment for splits and dividends."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryTimeSeriesIntradayRequest(
            query=_models.GetQueryTimeSeriesIntradayRequestQuery(function=function, symbol=symbol, interval=interval, adjusted=adjusted, extended_hours=extended_hours, month=month, outputsize=outputsize)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_intraday_time_series: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__TIME_SERIES_INTRADAY"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_intraday_time_series")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_intraday_time_series", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_intraday_time_series",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Core Stock APIs
@mcp.tool()
async def get_daily_time_series(
    function: Literal["TIME_SERIES_DAILY"] = Field(..., description="The time series data type to retrieve. Must be set to TIME_SERIES_DAILY for daily candlestick data."),
    symbol: str = Field(..., description="The stock symbol or ticker of the equity to retrieve data for (e.g., IBM, AAPL)."),
    outputsize: Literal["compact", "full"] | None = Field(None, description="Controls the amount of historical data returned. Use 'compact' for the latest 100 data points (recommended for reducing response size), or 'full' for the complete 20+ year historical dataset. Full output requires a premium API key."),
) -> dict[str, Any]:
    """Retrieves daily OHLCV (open, high, low, close, volume) time series data for a specified equity, covering 20+ years of historical data. Choose between compact (latest 100 data points) or full historical dataset."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryTimeSeriesDailyRequest(
            query=_models.GetQueryTimeSeriesDailyRequestQuery(function=function, symbol=symbol, outputsize=outputsize)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_daily_time_series: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__TIME_SERIES_DAILY"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_daily_time_series")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_daily_time_series", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_daily_time_series",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Core Stock APIs
@mcp.tool()
async def get_daily_adjusted_time_series(
    function: Literal["TIME_SERIES_DAILY_ADJUSTED"] = Field(..., description="The time series data type to retrieve. Must be set to TIME_SERIES_DAILY_ADJUSTED for daily adjusted price and volume data."),
    symbol: str = Field(..., description="The stock ticker symbol of the equity to query (e.g., IBM, AAPL). Case-insensitive."),
    outputsize: Literal["compact", "full"] | None = Field(None, description="Controls the amount of historical data returned. Use 'compact' for the most recent 100 trading days, or 'full' for the complete 20+ year historical dataset. Defaults to compact."),
) -> dict[str, Any]:
    """Retrieves daily adjusted OHLCV (open, high, low, close, volume) time series data for an equity, including split and dividend adjustments. Supports up to 20+ years of historical data with flexible output sizing."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryTimeSeriesDailyAdjustedRequest(
            query=_models.GetQueryTimeSeriesDailyAdjustedRequestQuery(function=function, symbol=symbol, outputsize=outputsize)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_daily_adjusted_time_series: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__TIME_SERIES_DAILY_ADJUSTED"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_daily_adjusted_time_series")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_daily_adjusted_time_series", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_daily_adjusted_time_series",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Core Stock APIs
@mcp.tool()
async def get_weekly_time_series(
    function: Literal["TIME_SERIES_WEEKLY"] = Field(..., description="The time series data type to retrieve. Must be set to TIME_SERIES_WEEKLY for weekly equity data."),
    symbol: str = Field(..., description="The stock symbol or ticker of the equity to retrieve data for (e.g., IBM, AAPL)."),
) -> dict[str, Any]:
    """Retrieves weekly time series data for a specified equity, including open, high, low, close prices and trading volume for the last trading day of each week, covering 20+ years of historical data."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryTimeSeriesWeeklyRequest(
            query=_models.GetQueryTimeSeriesWeeklyRequestQuery(function=function, symbol=symbol)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_weekly_time_series: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__TIME_SERIES_WEEKLY"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_weekly_time_series")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_weekly_time_series", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_weekly_time_series",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Core Stock APIs
@mcp.tool()
async def get_weekly_adjusted_time_series(
    function: Literal["TIME_SERIES_WEEKLY_ADJUSTED"] = Field(..., description="The time series function type. Must be set to TIME_SERIES_WEEKLY_ADJUSTED to retrieve weekly adjusted historical data."),
    symbol: str = Field(..., description="The stock symbol or ticker of the equity to retrieve data for (e.g., IBM, AAPL). Case-insensitive."),
) -> dict[str, Any]:
    """Retrieves weekly adjusted time series data for an equity, including open, high, low, close, adjusted close, volume, and dividend information. Covers 20+ years of historical data with the last trading day of each week as the reference point."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryTimeSeriesWeeklyAdjustedRequest(
            query=_models.GetQueryTimeSeriesWeeklyAdjustedRequestQuery(function=function, symbol=symbol)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_weekly_adjusted_time_series: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__TIME_SERIES_WEEKLY_ADJUSTED"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_weekly_adjusted_time_series")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_weekly_adjusted_time_series", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_weekly_adjusted_time_series",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Core Stock APIs
@mcp.tool()
async def get_equity_monthly_time_series(
    function: Literal["TIME_SERIES_MONTHLY"] = Field(..., description="The time series data type to retrieve. Must be set to TIME_SERIES_MONTHLY for monthly aggregated equity data."),
    symbol: str = Field(..., description="The stock symbol or ticker of the equity to retrieve data for (e.g., IBM, AAPL, MSFT)."),
) -> dict[str, Any]:
    """Retrieves monthly time series data for a specified global equity, including open, high, low, close prices and trading volume for the last trading day of each month, covering 20+ years of historical data."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryTimeSeriesMonthlyRequest(
            query=_models.GetQueryTimeSeriesMonthlyRequestQuery(function=function, symbol=symbol)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_equity_monthly_time_series: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__TIME_SERIES_MONTHLY"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_equity_monthly_time_series")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_equity_monthly_time_series", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_equity_monthly_time_series",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Core Stock APIs
@mcp.tool()
async def get_monthly_adjusted_time_series(
    function: Literal["TIME_SERIES_MONTHLY_ADJUSTED"] = Field(..., description="The time series function type. Must be set to TIME_SERIES_MONTHLY_ADJUSTED to retrieve monthly adjusted data."),
    symbol: str = Field(..., description="The stock symbol or ticker of the equity to retrieve data for (e.g., IBM, AAPL)."),
) -> dict[str, Any]:
    """Retrieves monthly adjusted historical time series data for an equity, including split and dividend-adjusted prices, volumes, and dividends covering 20+ years of historical data."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryTimeSeriesMonthlyAdjustedRequest(
            query=_models.GetQueryTimeSeriesMonthlyAdjustedRequestQuery(function=function, symbol=symbol)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_monthly_adjusted_time_series: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__TIME_SERIES_MONTHLY_ADJUSTED"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_monthly_adjusted_time_series")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_monthly_adjusted_time_series", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_monthly_adjusted_time_series",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Core Stock APIs
@mcp.tool()
async def get_realtime_quotes(
    function: Literal["REALTIME_BULK_QUOTES"] = Field(..., description="The API function type; must be set to REALTIME_BULK_QUOTES to retrieve real-time quotes."),
    symbol: str = Field(..., description="One or more stock symbols separated by commas (e.g., MSFT,AAPL,IBM). Up to 100 symbols are accepted per request; additional symbols beyond 100 will be ignored."),
) -> dict[str, Any]:
    """Fetch real-time market quotes for multiple US-traded symbols in a single request, supporting up to 100 symbols with coverage of regular and extended trading hours."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryRealtimeBulkQuotesRequest(
            query=_models.GetQueryRealtimeBulkQuotesRequestQuery(function=function, symbol=symbol)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_realtime_quotes: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__REALTIME_BULK_QUOTES"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_realtime_quotes")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_realtime_quotes", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_realtime_quotes",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Core Stock APIs
@mcp.tool()
async def search_symbols(
    function: Literal["SYMBOL_SEARCH"] = Field(..., description="The search function to execute. Must be set to SYMBOL_SEARCH to perform symbol lookups."),
    keywords: str = Field(..., description="A text string containing one or more keywords to search for symbols. For example, company names like 'microsoft' or 'tesco'."),
) -> dict[str, Any]:
    """Search for financial symbols and market information by keywords. Returns matching symbols ranked by relevance with match scores to support custom filtering logic."""

    # Construct request model with validation
    try:
        _request = _models.GetQuerySymbolSearchRequest(
            query=_models.GetQuerySymbolSearchRequestQuery(function=function, keywords=keywords)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_symbols: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__SYMBOL_SEARCH"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_symbols")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_symbols", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_symbols",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Core Stock APIs
@mcp.tool()
async def check_market_status(function: Literal["MARKET_STATUS"] = Field(..., description="The function to execute; must be set to MARKET_STATUS to retrieve global market status information.")) -> dict[str, Any]:
    """Check the current open or closed status of major global trading venues across equities, forex, and cryptocurrency markets."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryMarketStatusRequest(
            query=_models.GetQueryMarketStatusRequestQuery(function=function)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for check_market_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__MARKET_STATUS"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("check_market_status")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("check_market_status", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="check_market_status",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Index Data APIs
@mcp.tool()
async def get_index_data(
    function: Literal["INDEX_DATA"] = Field(..., description="The data function type to retrieve. Must be set to INDEX_DATA to fetch index time series information."),
    symbol: Literal["COMP"] = Field(..., description="The stock market index symbol. Must be set to COMP to retrieve NASDAQ Composite Index data."),
    interval: Literal["daily", "weekly", "monthly"] = Field(..., description="The time interval between consecutive data points in the returned series. Choose from daily, weekly, or monthly granularity."),
) -> dict[str, Any]:
    """Retrieves historical OHLC (open, high, low, close) time series data for the NASDAQ Composite Index spanning decades of market data."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryIndexDataRequest(
            query=_models.GetQueryIndexDataRequestQuery(function=function, symbol=symbol, interval=interval)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_index_data: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__INDEX_DATA"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_index_data")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_index_data", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_index_data",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Index Data APIs
@mcp.tool()
async def list_index_symbols(function: Literal["INDEX_CATALOG"] = Field(..., description="The catalog function to execute. Must be set to INDEX_CATALOG to retrieve the index symbol catalog.")) -> dict[str, Any]:
    """Retrieves a complete catalog of all supported index symbols with their full names. Use this to discover available indices for market data queries."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryIndexCatalogRequest(
            query=_models.GetQueryIndexCatalogRequestQuery(function=function)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_index_symbols: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__INDEX_CATALOG"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_index_symbols")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_index_symbols", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_index_symbols",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Options Data APIs
@mcp.tool()
async def list_realtime_options(
    function: Literal["REALTIME_OPTIONS"] = Field(..., description="The data type to retrieve. Must be set to REALTIME_OPTIONS to fetch current options market data."),
    symbol: str = Field(..., description="The stock symbol for which to retrieve options data (e.g., IBM)."),
    require_greeks: bool | None = Field(None, description="Include greeks (delta, gamma, vega, theta, rho) and implied volatility (IV) calculations in the response. Disabled by default for faster responses."),
    contract: str | None = Field(None, description="Filter results to a specific options contract by its contract ID. When omitted, returns the entire option chain for the symbol."),
    expiration: str | None = Field(None, description="Filter results to contracts expiring on a specific date in YYYY-MM-DD format. The date must be today or later. When omitted, returns contracts across all available expiration dates."),
) -> dict[str, Any]:
    """Retrieve realtime US options data with full market coverage. Option chains are automatically sorted by expiration date (chronological) and then by strike price (low to high)."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryRealtimeOptionsRequest(
            query=_models.GetQueryRealtimeOptionsRequestQuery(function=function, symbol=symbol, require_greeks=require_greeks, contract=contract, expiration=expiration)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_realtime_options: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__REALTIME_OPTIONS"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_realtime_options")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_realtime_options", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_realtime_options",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Options Data APIs
@mcp.tool()
async def get_realtime_put_call_ratio(
    function: Literal["REALTIME_PUT_CALL_RATIO"] = Field(..., description="The function type for this operation, which must be set to REALTIME_PUT_CALL_RATIO to retrieve realtime put-call ratio data."),
    symbol: str = Field(..., description="The stock ticker symbol for the equity to analyze (e.g., IBM). This identifies which company's option chain data to retrieve."),
) -> dict[str, Any]:
    """Retrieves the realtime put-call ratio for a specified equity symbol, indicating market sentiment across the entire option chain and by expiration date. Lower ratios (≤0.6) suggest bullish sentiment with more call buying, while higher ratios (≥1.0) indicate bearish sentiment with more put buying."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryRealtimePutCallRatioRequest(
            query=_models.GetQueryRealtimePutCallRatioRequestQuery(function=function, symbol=symbol)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_realtime_put_call_ratio: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__REALTIME_PUT_CALL_RATIO"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_realtime_put_call_ratio")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_realtime_put_call_ratio", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_realtime_put_call_ratio",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Options Data APIs
@mcp.tool()
async def get_historical_options(
    function: Literal["HISTORICAL_OPTIONS"] = Field(..., description="The data type to retrieve. Must be set to HISTORICAL_OPTIONS to fetch historical options chain data."),
    symbol: str = Field(..., description="The equity ticker symbol (e.g., IBM). Used to identify which stock's options data to retrieve."),
    date: str | None = Field(None, description="The date for which to retrieve options data in YYYY-MM-DD format. Any date from 2008-01-01 onwards is accepted. If omitted, defaults to the previous trading session."),
) -> dict[str, Any]:
    """Retrieve historical options chain data for a given equity symbol, including implied volatility and Greeks (delta, gamma, theta, vega, rho). Data spans 15+ years and defaults to the previous trading session if no date is specified."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryHistoricalOptionsRequest(
            query=_models.GetQueryHistoricalOptionsRequestQuery(function=function, symbol=symbol, date=date)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_historical_options: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__HISTORICAL_OPTIONS"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_historical_options")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_historical_options", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_historical_options",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Options Data APIs
@mcp.tool()
async def get_historical_put_call_ratio(
    function: Literal["HISTORICAL_PUT_CALL_RATIO"] = Field(..., description="The function type for this operation. Must be set to HISTORICAL_PUT_CALL_RATIO to retrieve put-call ratio data."),
    symbol: str = Field(..., description="The stock ticker symbol for the equity (e.g., IBM). This identifies which company's options data to retrieve."),
    date: str | None = Field(None, description="The date for which to retrieve put-call ratio data in YYYY-MM-DD format. If not provided, defaults to the most recent trading session. Any date from 2008-01-01 onwards is accepted."),
) -> dict[str, Any]:
    """Retrieves historical put-call ratios for an equity symbol, indicating market sentiment through the proportion of put to call options. Ratios below 0.6 suggest bullish sentiment, while ratios above 1.0 indicate bearish sentiment."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryHistoricalPutCallRatioRequest(
            query=_models.GetQueryHistoricalPutCallRatioRequestQuery(function=function, symbol=symbol, date=date)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_historical_put_call_ratio: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__HISTORICAL_PUT_CALL_RATIO"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_historical_put_call_ratio")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_historical_put_call_ratio", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_historical_put_call_ratio",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Alpha Intelligence
@mcp.tool()
async def search_news_sentiment(
    function: Literal["NEWS_SENTIMENT"] = Field(..., description="The operation type to perform. Must be set to NEWS_SENTIMENT to retrieve news and sentiment data."),
    tickers: str | None = Field(None, description="Filter articles by one or more asset symbols (e.g., AAPL for stocks, CRYPTO:BTC for Bitcoin, FOREX:USD for US Dollar). Use comma-separated values to match articles mentioning multiple symbols simultaneously."),
    topics: Literal["blockchain", "earnings", "ipo", "mergers_and_acquisitions", "financial_markets", "economy_fiscal", "economy_monetary", "economy_macro", "energy_transportation", "finance", "life_sciences", "manufacturing", "real_estate", "retail_wholesale", "technology"] | None = Field(None, description="Filter articles by news topic category. Choose from: blockchain, earnings, ipo, mergers_and_acquisitions, financial_markets, economy_fiscal, economy_monetary, economy_macro, energy_transportation, finance, life_sciences, manufacturing, real_estate, retail_wholesale, or technology."),
    time_from: str | None = Field(None, description="Filter articles published on or after this date and time. Use YYYYMMDDTHHMM format (e.g., 20220410T0130 for April 10, 2022 at 1:30 AM)."),
    time_to: str | None = Field(None, description="Filter articles published on or before this date and time. Use YYYYMMDDTHHMM format. If omitted, defaults to the current time."),
    sort: Literal["LATEST", "EARLIEST", "RELEVANCE"] | None = Field(None, description="Order results by LATEST (most recent first, default), EARLIEST (oldest first), or RELEVANCE (best match first)."),
    limit: Literal[50, 1000] | None = Field(None, description="Maximum number of results to return. Choose 50 (default) or 1000."),
) -> dict[str, Any]:
    """Search live and historical market news with sentiment analysis across stocks, cryptocurrencies, forex, and economic topics from global news outlets."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryNewsSentimentRequest(
            query=_models.GetQueryNewsSentimentRequestQuery(function=function, tickers=tickers, topics=topics, time_from=time_from, time_to=time_to, sort=sort, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_news_sentiment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__NEWS_SENTIMENT"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_news_sentiment")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_news_sentiment", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_news_sentiment",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Alpha Intelligence
@mcp.tool()
async def get_earnings_call_transcript(
    function: Literal["EARNINGS_CALL_TRANSCRIPT"] = Field(..., description="The function identifier for this operation. Must be set to EARNINGS_CALL_TRANSCRIPT to retrieve earnings call transcripts."),
    symbol: str = Field(..., description="The stock ticker symbol of the company (e.g., IBM). Used to identify which company's earnings call transcript to retrieve."),
    quarter: str = Field(..., description="The fiscal quarter in YYYYQM format (e.g., 2024Q1), where Q is followed by a digit 1-4. Any quarter from 2010Q1 onwards is supported.", pattern="^[0-9]{4}Q[1-4]$"),
) -> dict[str, Any]:
    """Retrieves the earnings call transcript for a specified company and fiscal quarter, with historical data spanning over 15 years and enriched with LLM-based sentiment analysis."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryEarningsCallTranscriptRequest(
            query=_models.GetQueryEarningsCallTranscriptRequestQuery(function=function, symbol=symbol, quarter=quarter)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_earnings_call_transcript: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__EARNINGS_CALL_TRANSCRIPT"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_earnings_call_transcript")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_earnings_call_transcript", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_earnings_call_transcript",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Alpha Intelligence
@mcp.tool()
async def list_market_movers(function: Literal["TOP_GAINERS_LOSERS"] = Field(..., description="The function to execute. Must be set to TOP_GAINERS_LOSERS to retrieve market mover data.")) -> dict[str, Any]:
    """Retrieve the top 20 gainers, losers, and most actively traded stocks in the US market. Historical data is returned by default, with real-time or 15-minute delayed data available for premium members."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryTopGainersLosersRequest(
            query=_models.GetQueryTopGainersLosersRequestQuery(function=function)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_market_movers: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__TOP_GAINERS_LOSERS"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_market_movers")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_market_movers", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_market_movers",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Alpha Intelligence
@mcp.tool()
async def list_insider_transactions(
    function: Literal["INSIDER_TRANSACTIONS"] = Field(..., description="The function type to invoke. Must be set to INSIDER_TRANSACTIONS to retrieve insider transaction data."),
    symbol: str = Field(..., description="The stock ticker symbol of the company for which to retrieve insider transactions (e.g., IBM, AAPL)."),
) -> dict[str, Any]:
    """Retrieve insider transactions (SEC Form 4 filings) for a specified company, including historical records of trades made by key stakeholders such as executives, founders, and board members."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryInsiderTransactionsRequest(
            query=_models.GetQueryInsiderTransactionsRequestQuery(function=function, symbol=symbol)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_insider_transactions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__INSIDER_TRANSACTIONS"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_insider_transactions")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_insider_transactions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_insider_transactions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Alpha Intelligence
@mcp.tool()
async def get_institutional_holdings(
    function: Literal["INSTITUTIONAL_HOLDINGS"] = Field(..., description="The function type to execute; must be set to INSTITUTIONAL_HOLDINGS to retrieve institutional ownership data."),
    symbol: str = Field(..., description="The stock ticker symbol for the equity of interest (e.g., IBM, AAPL). Use the standard market symbol without exchange suffix."),
) -> dict[str, Any]:
    """Retrieves institutional ownership and holdings data for a specified equity, showing which institutions hold shares and their ownership percentages."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryInstitutionalHoldingsRequest(
            query=_models.GetQueryInstitutionalHoldingsRequestQuery(function=function, symbol=symbol)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_institutional_holdings: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__INSTITUTIONAL_HOLDINGS"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_institutional_holdings")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_institutional_holdings", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_institutional_holdings",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Alpha Intelligence
@mcp.tool()
async def calculate_analytics_fixed_window(
    function: Literal["ANALYTICS_FIXED_WINDOW"] = Field(..., description="The analytics function to execute. Must be set to ANALYTICS_FIXED_WINDOW for this operation."),
    symbols: str = Field(..., alias="SYMBOLS", description="Comma-separated list of stock symbols to analyze. Free API keys support up to 5 symbols per request; premium keys support up to 50 symbols."),
    range_: str = Field(..., alias="RANGE", description="The time period for analysis. Specify as 'full' for all available data, a relative range like '30day' or '6month', a single date in YYYY-MM-DD format, or a date range using start and end dates (e.g., '2023-07-01&RANGE=2023-08-31'). Also accepts YYYY-MM for a full month or YYYY-MM-DD for a single day."),
    interval: Literal["1min", "5min", "15min", "30min", "60min", "DAILY", "WEEKLY", "MONTHLY"] = Field(..., alias="INTERVAL", description="The frequency of data points in the time series. Choose from minute-level intervals (1min, 5min, 15min, 30min, 60min) or daily/weekly/monthly aggregations (DAILY, WEEKLY, MONTHLY)."),
    calculations: str = Field(..., alias="CALCULATIONS", description="Comma-separated list of metrics to calculate. Available metrics include MIN, MAX, MEAN, MEDIAN, CUMULATIVE_RETURN, VARIANCE, STDDEV, MAX_DRAWDOWN, HISTOGRAM, AUTOCORRELATION, COVARIANCE, and CORRELATION. Some metrics accept optional parameters in parentheses (e.g., VARIANCE(annualized=True), HISTOGRAM(bins=20), AUTOCORRELATION(lag=2), CORRELATION(method=KENDALL))."),
    ohlc: Literal["open", "high", "low", "close"] | None = Field(None, alias="OHLC", description="The price field to use for calculations: open, high, low, or close. Defaults to close price if not specified."),
) -> dict[str, Any]:
    """Calculate advanced analytics metrics for one or more financial symbols over a fixed time window, including statistical measures like returns, variance, drawdown, and correlation analysis."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryAnalyticsFixedWindowRequest(
            query=_models.GetQueryAnalyticsFixedWindowRequestQuery(function=function, symbols=symbols, range_=range_, interval=interval, calculations=calculations, ohlc=ohlc)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for calculate_analytics_fixed_window: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__ANALYTICS_FIXED_WINDOW"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("calculate_analytics_fixed_window")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("calculate_analytics_fixed_window", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="calculate_analytics_fixed_window",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Alpha Intelligence
@mcp.tool()
async def analyze_sliding_window_metrics(
    function: Literal["ANALYTICS_SLIDING_WINDOW"] = Field(..., description="The analytics function to execute. Must be set to ANALYTICS_SLIDING_WINDOW."),
    symbols: str = Field(..., alias="SYMBOLS", description="One or more stock symbols to analyze, provided as a comma-separated list. Free API keys support up to 5 symbols per request; premium keys support up to 50."),
    range_: str = Field(..., alias="RANGE", description="The time period for the analysis. Accepts relative ranges (e.g., '2month', '10day'), specific dates in YYYY-MM-DD format, or ISO 8601 format. You can specify a start and end date by providing two RANGE parameters."),
    interval: Literal["1min", "5min", "15min", "30min", "60min", "DAILY", "WEEKLY", "MONTHLY"] = Field(..., alias="INTERVAL", description="The frequency of data points in the time series. Choose from minute-level intervals (1min, 5min, 15min, 30min, 60min) for intraday analysis or daily/weekly/monthly intervals for longer-term trends."),
    window_size: int = Field(..., alias="WINDOW_SIZE", description="The number of data points in each sliding window. Must be at least 10, though larger windows (e.g., 20+) are recommended for more reliable statistical results.", ge=10),
    calculations: str = Field(..., alias="CALCULATIONS", description="A comma-separated list of metrics to calculate, such as MEAN, MEDIAN, CUMULATIVE_RETURN, VARIANCE, STDDEV, COVARIANCE, or CORRELATION. Free API keys allow 1 metric per request; premium keys allow multiple. Optional parameters can be appended to metrics (e.g., STDDEV(annualized=True), CORRELATION(method=KENDALL))."),
    ohlc: Literal["open", "high", "low", "close"] | None = Field(None, alias="OHLC", description="The price field to use for calculations: open, high, low, or close price. Defaults to close price if not specified."),
) -> dict[str, Any]:
    """Calculate advanced analytics metrics (mean, variance, correlation, etc.) for one or more stock symbols over sliding time windows, enabling trend analysis and statistical insights across different time intervals."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryAnalyticsSlidingWindowRequest(
            query=_models.GetQueryAnalyticsSlidingWindowRequestQuery(function=function, symbols=symbols, range_=range_, interval=interval, ohlc=ohlc, window_size=window_size, calculations=calculations)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for analyze_sliding_window_metrics: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__ANALYTICS_SLIDING_WINDOW"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("analyze_sliding_window_metrics")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("analyze_sliding_window_metrics", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="analyze_sliding_window_metrics",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Fundamental Data
@mcp.tool()
async def get_company_overview(
    function: Literal["OVERVIEW"] = Field(..., description="The type of company data to retrieve. Must be set to OVERVIEW to fetch company information and financial metrics."),
    symbol: str = Field(..., description="The stock ticker symbol of the company you want to look up (e.g., IBM, AAPL)."),
) -> dict[str, Any]:
    """Retrieve comprehensive company information including financial ratios and key metrics for a specified equity ticker. Data is typically updated on the same day the company reports its latest earnings and financial results."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryOverviewRequest(
            query=_models.GetQueryOverviewRequestQuery(function=function, symbol=symbol)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_company_overview: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__OVERVIEW"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_company_overview")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_company_overview", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_company_overview",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Fundamental Data
@mcp.tool()
async def get_etf_profile(
    function: Literal["ETF_PROFILE"] = Field(..., description="The function type to execute; must be set to ETF_PROFILE to retrieve ETF profile and holdings data."),
    symbol: str = Field(..., description="The ticker symbol of the ETF to retrieve profile information for (e.g., QQQ, SPY)."),
) -> dict[str, Any]:
    """Retrieves comprehensive ETF profile data including key metrics (net assets, expense ratio, turnover) and detailed holdings information with allocation breakdown by asset types and sectors."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryEtfProfileRequest(
            query=_models.GetQueryEtfProfileRequestQuery(function=function, symbol=symbol)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_etf_profile: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__ETF_PROFILE"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_etf_profile")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_etf_profile", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_etf_profile",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Fundamental Data
@mcp.tool()
async def get_dividend_history(
    function: Literal["DIVIDENDS"] = Field(..., description="The dividend query function type. Must be set to DIVIDENDS to retrieve dividend data."),
    symbol: str = Field(..., description="The equity ticker symbol for which to retrieve dividend information (e.g., IBM, AAPL)."),
) -> dict[str, Any]:
    """Retrieve historical and declared future dividend distributions for a specified equity ticker symbol."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryDividendsRequest(
            query=_models.GetQueryDividendsRequestQuery(function=function, symbol=symbol)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_dividend_history: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__DIVIDENDS"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_dividend_history")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_dividend_history", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_dividend_history",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Fundamental Data
@mcp.tool()
async def get_stock_splits(
    function: Literal["SPLITS"] = Field(..., description="The function type to execute. Must be set to SPLITS to retrieve stock split data."),
    symbol: str = Field(..., description="The stock ticker symbol for which to retrieve historical split data (e.g., IBM, AAPL)."),
) -> dict[str, Any]:
    """Retrieves historical stock split events for a given equity ticker symbol, including dates and split ratios."""

    # Construct request model with validation
    try:
        _request = _models.GetQuerySplitsRequest(
            query=_models.GetQuerySplitsRequestQuery(function=function, symbol=symbol)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_stock_splits: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__SPLITS"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_stock_splits")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_stock_splits", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_stock_splits",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Fundamental Data
@mcp.tool()
async def get_income_statement(
    function: Literal["INCOME_STATEMENT"] = Field(..., description="The financial statement type to retrieve. Must be set to INCOME_STATEMENT to fetch income statement data."),
    symbol: str = Field(..., description="The stock ticker symbol of the company whose income statement you want to retrieve (e.g., IBM, AAPL)."),
) -> dict[str, Any]:
    """Retrieve annual and quarterly income statements for a specified equity, with normalized fields mapped to GAAP and IFRS taxonomies. Data is typically updated on the same day the company reports its latest earnings."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryIncomeStatementRequest(
            query=_models.GetQueryIncomeStatementRequestQuery(function=function, symbol=symbol)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_income_statement: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__INCOME_STATEMENT"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_income_statement")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_income_statement", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_income_statement",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Fundamental Data
@mcp.tool()
async def get_balance_sheet(
    function: Literal["BALANCE_SHEET"] = Field(..., description="The balance sheet data type to retrieve. Must be set to BALANCE_SHEET."),
    symbol: str = Field(..., description="The stock ticker symbol of the company (e.g., IBM, AAPL). Used to identify which equity's balance sheet to retrieve."),
) -> dict[str, Any]:
    """Retrieve annual and quarterly balance sheet data for a specified equity, with normalized fields mapped to GAAP and IFRS taxonomies. Data is typically updated on the same day the company reports its latest earnings and financials."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryBalanceSheetRequest(
            query=_models.GetQueryBalanceSheetRequestQuery(function=function, symbol=symbol)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_balance_sheet: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__BALANCE_SHEET"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_balance_sheet")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_balance_sheet", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_balance_sheet",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Fundamental Data
@mcp.tool()
async def get_cash_flow_statement(
    function: Literal["CASH_FLOW"] = Field(..., description="The cash flow statement function type. Must be set to CASH_FLOW to retrieve cash flow data."),
    symbol: str = Field(..., description="The stock ticker symbol of the company for which to retrieve cash flow statements (e.g., IBM, AAPL)."),
) -> dict[str, Any]:
    """Retrieves annual and quarterly cash flow statements for a specified equity, with normalized fields mapped to GAAP and IFRS taxonomies. Data is typically updated on the same day the company reports its latest earnings and financial results."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryCashFlowRequest(
            query=_models.GetQueryCashFlowRequestQuery(function=function, symbol=symbol)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_cash_flow_statement: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__CASH_FLOW"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_cash_flow_statement")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_cash_flow_statement", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_cash_flow_statement",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Fundamental Data
@mcp.tool()
async def get_shares_outstanding(
    function: Literal["SHARES_OUTSTANDING"] = Field(..., description="The function identifier for this operation. Must be set to SHARES_OUTSTANDING to retrieve shares outstanding data."),
    symbol: str = Field(..., description="The stock ticker symbol of the company (e.g., MSFT). Use the standard market ticker symbol for the equity of interest."),
) -> dict[str, Any]:
    """Retrieves quarterly shares outstanding data for a specified equity, including both basic and diluted share counts. Data is typically updated on the same day the company reports its latest earnings and financial results."""

    # Construct request model with validation
    try:
        _request = _models.GetQuerySharesOutstandingRequest(
            query=_models.GetQuerySharesOutstandingRequestQuery(function=function, symbol=symbol)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_shares_outstanding: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__SHARES_OUTSTANDING"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_shares_outstanding")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_shares_outstanding", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_shares_outstanding",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Fundamental Data
@mcp.tool()
async def get_earnings(
    function: Literal["EARNINGS"] = Field(..., description="The earnings data function type. Must be set to EARNINGS to retrieve earnings data."),
    symbol: str = Field(..., description="The stock ticker symbol of the company (e.g., IBM, AAPL). Used to identify which company's earnings data to retrieve."),
) -> dict[str, Any]:
    """Retrieve annual and quarterly earnings per share (EPS) data for a company, including analyst estimates and surprise metrics for quarterly periods."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryEarningsRequest(
            query=_models.GetQueryEarningsRequestQuery(function=function, symbol=symbol)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_earnings: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__EARNINGS"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_earnings")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_earnings", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_earnings",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Fundamental Data
@mcp.tool()
async def get_earnings_estimates(
    function: Literal["EARNINGS_ESTIMATES"] = Field(..., description="The earnings estimates function type. Must be set to EARNINGS_ESTIMATES to retrieve consensus analyst estimates."),
    symbol: str = Field(..., description="The stock ticker symbol for the company of interest (e.g., IBM, AAPL). Used to identify which equity's earnings estimates to retrieve."),
) -> dict[str, Any]:
    """Retrieve consensus earnings estimates for a specified equity, including annual and quarterly EPS and revenue projections, analyst count, and revision history."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryEarningsEstimatesRequest(
            query=_models.GetQueryEarningsEstimatesRequestQuery(function=function, symbol=symbol)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_earnings_estimates: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__EARNINGS_ESTIMATES"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_earnings_estimates")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_earnings_estimates", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_earnings_estimates",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Fundamental Data
@mcp.tool()
async def list_listing_status(
    function: Literal["LISTING_STATUS"] = Field(..., description="The function type for this operation. Must be set to LISTING_STATUS to query asset listing status."),
    date: str | None = Field(None, description="The date for which to retrieve listing status. Use YYYY-MM-DD format for any date from January 1, 2010 onwards. If omitted, returns data as of the latest trading day."),
    state: Literal["active", "delisted"] | None = Field(None, description="Filter results by asset state: active returns currently traded stocks and ETFs, while delisted returns assets that have been removed from exchanges. Defaults to active if not specified."),
) -> dict[str, Any]:
    """Retrieve a list of active or delisted US stocks and ETFs as of a specific date or the latest trading day, enabling equity research on asset lifecycle and survivorship."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryListingStatusRequest(
            query=_models.GetQueryListingStatusRequestQuery(function=function, date=date, state=state)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_listing_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__LISTING_STATUS"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_listing_status")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_listing_status", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_listing_status",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Fundamental Data
@mcp.tool()
async def list_earnings_calendar(
    function: Literal["EARNINGS_CALENDAR"] = Field(..., description="The function identifier for this operation. Must be set to EARNINGS_CALENDAR."),
    symbol: str | None = Field(None, description="Optional company stock symbol to filter results for a specific company. When omitted, returns earnings data for all companies."),
    horizon: Literal["3month", "6month", "12month"] | None = Field(None, description="Time horizon for the earnings forecast. Choose from 3 months, 6 months, or 12 months. Defaults to 3 months if not specified."),
) -> dict[str, Any]:
    """Retrieve expected earnings release dates for companies over a specified time horizon. Filter by a specific company symbol or view the full market earnings calendar."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryEarningsCalendarRequest(
            query=_models.GetQueryEarningsCalendarRequestQuery(function=function, symbol=symbol, horizon=horizon)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_earnings_calendar: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__EARNINGS_CALENDAR"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_earnings_calendar")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_earnings_calendar", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_earnings_calendar",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Fundamental Data
@mcp.tool()
async def list_ipo_calendar(function: Literal["IPO_CALENDAR"] = Field(..., description="The API function to invoke. Must be set to IPO_CALENDAR to retrieve IPO calendar data.")) -> dict[str, Any]:
    """Retrieve a list of upcoming IPO events scheduled in the US market over the next 3 months."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryIpoCalendarRequest(
            query=_models.GetQueryIpoCalendarRequestQuery(function=function)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_ipo_calendar: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__IPO_CALENDAR"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_ipo_calendar")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_ipo_calendar", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_ipo_calendar",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Cryptocurrencies
@mcp.tool()
async def get_exchange_rate(
    function: Literal["CURRENCY_EXCHANGE_RATE"] = Field(..., description="The function identifier for this operation; must be set to CURRENCY_EXCHANGE_RATE."),
    from_currency: str = Field(..., description="The source currency code (e.g., BTC for Bitcoin, USD for US Dollar). Accepts both cryptocurrency and fiat currency codes."),
    to_currency: str = Field(..., description="The target currency code (e.g., EUR for Euro, BTC for Bitcoin). Accepts both cryptocurrency and fiat currency codes."),
) -> dict[str, Any]:
    """Retrieves the current exchange rate between two currencies, supporting both cryptocurrencies (e.g., BTC) and fiat currencies (e.g., USD, EUR)."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryCurrencyExchangeRateRequest(
            query=_models.GetQueryCurrencyExchangeRateRequestQuery(function=function, from_currency=from_currency, to_currency=to_currency)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_exchange_rate: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__CURRENCY_EXCHANGE_RATE"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_exchange_rate")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_exchange_rate", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_exchange_rate",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Forex (FX)
@mcp.tool()
async def get_forex_intraday(
    function: Literal["FX_INTRADAY"] = Field(..., description="The time series function type; must be set to FX_INTRADAY for forex intraday data."),
    from_symbol: str = Field(..., description="The three-letter ISO 4217 currency code for the base currency (e.g., EUR, GBP, JPY).", min_length=3, max_length=3),
    to_symbol: str = Field(..., description="The three-letter ISO 4217 currency code for the quote currency (e.g., USD, EUR, GBP).", min_length=3, max_length=3),
    interval: Literal["1min", "5min", "15min", "30min", "60min"] = Field(..., description="The time interval between consecutive data points; choose from 1-minute, 5-minute, 15-minute, 30-minute, or 60-minute intervals."),
    outputsize: Literal["compact", "full"] | None = Field(None, description="Controls the amount of data returned: use 'compact' for the latest 100 data points (default) or 'full' for the complete intraday time series."),
) -> dict[str, Any]:
    """Retrieves real-time intraday time series data (open, high, low, close prices with timestamps) for a specified forex currency pair at your chosen time interval."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryFxIntradayRequest(
            query=_models.GetQueryFxIntradayRequestQuery(function=function, from_symbol=from_symbol, to_symbol=to_symbol, interval=interval, outputsize=outputsize)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_forex_intraday: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__FX_INTRADAY"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_forex_intraday")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_forex_intraday", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_forex_intraday",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Forex (FX)
@mcp.tool()
async def get_fx_daily(
    function: Literal["FX_DAILY"] = Field(..., description="The time series function type. Must be set to FX_DAILY for daily forex data."),
    from_symbol: str = Field(..., description="The base currency as a three-letter ISO 4217 code (e.g., EUR, GBP, JPY)."),
    to_symbol: str = Field(..., description="The quote currency as a three-letter ISO 4217 code (e.g., USD, EUR, GBP)."),
    outputsize: Literal["compact", "full"] | None = Field(None, description="Controls the amount of historical data returned. Use 'compact' for the latest 100 data points (recommended for smaller responses) or 'full' for the complete historical time series. Defaults to compact."),
) -> dict[str, Any]:
    """Retrieve daily forex time series data (open, high, low, close prices) for a specified currency pair, updated in real-time."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryFxDailyRequest(
            query=_models.GetQueryFxDailyRequestQuery(function=function, from_symbol=from_symbol, to_symbol=to_symbol, outputsize=outputsize)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_fx_daily: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__FX_DAILY"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_fx_daily")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_fx_daily", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_fx_daily",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Forex (FX)
@mcp.tool()
async def get_forex_weekly(
    function: Literal["FX_WEEKLY"] = Field(..., description="The time series function type. Must be set to FX_WEEKLY to retrieve weekly forex data."),
    from_symbol: str = Field(..., description="The three-letter ISO 4217 currency code for the base currency (e.g., EUR, GBP, JPY).", min_length=3, max_length=3),
    to_symbol: str = Field(..., description="The three-letter ISO 4217 currency code for the quote currency (e.g., USD, EUR, GBP).", min_length=3, max_length=3),
) -> dict[str, Any]:
    """Retrieves weekly OHLC (open, high, low, close) time series data for a specified forex currency pair, with real-time updates reflecting the current or partial trading week."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryFxWeeklyRequest(
            query=_models.GetQueryFxWeeklyRequestQuery(function=function, from_symbol=from_symbol, to_symbol=to_symbol)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_forex_weekly: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__FX_WEEKLY"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_forex_weekly")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_forex_weekly", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_forex_weekly",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Forex (FX)
@mcp.tool()
async def get_forex_monthly(
    function: Literal["FX_MONTHLY"] = Field(..., description="The time series function type. Must be set to FX_MONTHLY to retrieve monthly forex data."),
    from_symbol: str = Field(..., description="The base currency as a three-letter ISO 4217 code (e.g., EUR, GBP, JPY). This is the currency being converted from."),
    to_symbol: str = Field(..., description="The target currency as a three-letter ISO 4217 code (e.g., USD, EUR, GBP). This is the currency being converted to."),
) -> dict[str, Any]:
    """Retrieves monthly time series data for a forex currency pair, including open, high, low, and close prices. Data is updated in real-time, with the latest data point representing the current or partial month."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryFxMonthlyRequest(
            query=_models.GetQueryFxMonthlyRequestQuery(function=function, from_symbol=from_symbol, to_symbol=to_symbol)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_forex_monthly: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__FX_MONTHLY"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_forex_monthly")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_forex_monthly", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_forex_monthly",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Cryptocurrencies
@mcp.tool()
async def get_crypto_intraday(
    function: Literal["CRYPTO_INTRADAY"] = Field(..., description="The function type for this request. Must be set to CRYPTO_INTRADAY to retrieve intraday cryptocurrency time series data."),
    symbol: str = Field(..., description="The cryptocurrency symbol to retrieve data for (e.g., ETH for Ethereum, BTC for Bitcoin). Must be a valid cryptocurrency code from the supported list."),
    market: str = Field(..., description="The market currency to trade against (e.g., USD for US Dollar, EUR for Euro). Must be a valid currency code from the supported list."),
    interval: Literal["1min", "5min", "15min", "30min", "60min"] = Field(..., description="The time interval between consecutive data points. Choose from 1-minute, 5-minute, 15-minute, 30-minute, or 60-minute intervals."),
    outputsize: Literal["compact", "full"] | None = Field(None, description="Controls the amount of data returned. Use 'compact' (default) to get the latest 100 data points for faster responses, or 'full' to retrieve the complete intraday time series."),
) -> dict[str, Any]:
    """Retrieves real-time intraday price data for a cryptocurrency, including open, high, low, close prices and trading volume at specified time intervals."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryCryptoIntradayRequest(
            query=_models.GetQueryCryptoIntradayRequestQuery(function=function, symbol=symbol, market=market, interval=interval, outputsize=outputsize)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_crypto_intraday: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__CRYPTO_INTRADAY"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_crypto_intraday")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_crypto_intraday", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_crypto_intraday",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Cryptocurrencies
@mcp.tool()
async def get_cryptocurrency_daily_prices(
    function: Literal["DIGITAL_CURRENCY_DAILY"] = Field(..., description="The API function to invoke. Must be set to DIGITAL_CURRENCY_DAILY to retrieve daily cryptocurrency price history."),
    symbol: str = Field(..., description="The cryptocurrency symbol to query (e.g., BTC for Bitcoin). Use any valid cryptocurrency code from the supported currency list."),
    market: str = Field(..., description="The target market currency for price conversion (e.g., EUR for Euro). Use any valid fiat or cryptocurrency code from the supported currency list."),
) -> dict[str, Any]:
    """Retrieves daily historical price and volume data for a cryptocurrency traded against a specific fiat currency. Data is updated daily at midnight UTC and includes prices quoted in both the target market currency and USD."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryDigitalCurrencyDailyRequest(
            query=_models.GetQueryDigitalCurrencyDailyRequestQuery(function=function, symbol=symbol, market=market)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_cryptocurrency_daily_prices: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__DIGITAL_CURRENCY_DAILY"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_cryptocurrency_daily_prices")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_cryptocurrency_daily_prices", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_cryptocurrency_daily_prices",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Cryptocurrencies
@mcp.tool()
async def get_cryptocurrency_weekly_prices(
    function: Literal["DIGITAL_CURRENCY_WEEKLY"] = Field(..., description="The API function to invoke. Must be set to DIGITAL_CURRENCY_WEEKLY to retrieve weekly cryptocurrency time series data."),
    symbol: str = Field(..., description="The cryptocurrency symbol to query (e.g., BTC for Bitcoin). Use any valid cryptocurrency code from the supported currency list."),
    market: str = Field(..., description="The target market currency for price conversion (e.g., EUR for Euro). Use any valid fiat currency code from the supported market list."),
) -> dict[str, Any]:
    """Retrieves weekly historical price and volume data for a cryptocurrency traded against a specified fiat currency. Data is updated daily at midnight UTC and includes prices quoted in both the target market currency and USD."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryDigitalCurrencyWeeklyRequest(
            query=_models.GetQueryDigitalCurrencyWeeklyRequestQuery(function=function, symbol=symbol, market=market)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_cryptocurrency_weekly_prices: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__DIGITAL_CURRENCY_WEEKLY"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_cryptocurrency_weekly_prices")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_cryptocurrency_weekly_prices", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_cryptocurrency_weekly_prices",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Cryptocurrencies
@mcp.tool()
async def get_cryptocurrency_monthly_history(
    function: Literal["DIGITAL_CURRENCY_MONTHLY"] = Field(..., description="The API function to invoke. Must be set to DIGITAL_CURRENCY_MONTHLY to retrieve monthly time series data."),
    symbol: str = Field(..., description="The cryptocurrency symbol to query (e.g., BTC for Bitcoin). Must be a valid cryptocurrency code from the supported currency list."),
    market: str = Field(..., description="The target market or currency to trade against (e.g., EUR for Euro). Can be any fiat or cryptocurrency code from the supported currency list."),
) -> dict[str, Any]:
    """Retrieves monthly historical price and volume data for a cryptocurrency traded against a specific fiat or crypto market currency. Data is updated daily at midnight UTC and includes prices quoted in both the market currency and USD."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryDigitalCurrencyMonthlyRequest(
            query=_models.GetQueryDigitalCurrencyMonthlyRequestQuery(function=function, symbol=symbol, market=market)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_cryptocurrency_monthly_history: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__DIGITAL_CURRENCY_MONTHLY"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_cryptocurrency_monthly_history")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_cryptocurrency_monthly_history", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_cryptocurrency_monthly_history",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Commodities
@mcp.tool()
async def get_spot_price(
    function: Literal["GOLD_SILVER_SPOT"] = Field(..., description="The API function to invoke; must be set to GOLD_SILVER_SPOT to retrieve precious metal spot prices."),
    symbol: Literal["GOLD", "XAU", "SILVER", "XAG"] = Field(..., description="The precious metal symbol to query: use GOLD or XAU for gold prices, or SILVER or XAG for silver prices."),
) -> dict[str, Any]:
    """Retrieves the current live spot price for gold or silver in real-time market data."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryGoldSilverSpotRequest(
            query=_models.GetQueryGoldSilverSpotRequestQuery(function=function, symbol=symbol)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_spot_price: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__GOLD_SILVER_SPOT"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_spot_price")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_spot_price", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_spot_price",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Commodities
@mcp.tool()
async def get_precious_metal_history(
    function: Literal["GOLD_SILVER_HISTORY"] = Field(..., description="The API function to invoke. Must be set to GOLD_SILVER_HISTORY to retrieve precious metal historical data."),
    symbol: Literal["GOLD", "XAU", "SILVER", "XAG"] = Field(..., description="The precious metal to query. Use GOLD or XAU for gold prices, or SILVER or XAG for silver prices."),
    interval: Literal["daily", "weekly", "monthly"] = Field(..., description="The time interval for historical data aggregation. Choose from daily, weekly, or monthly price snapshots."),
) -> dict[str, Any]:
    """Retrieves historical price data for gold or silver across multiple time horizons (daily, weekly, or monthly intervals)."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryGoldSilverHistoryRequest(
            query=_models.GetQueryGoldSilverHistoryRequestQuery(function=function, symbol=symbol, interval=interval)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_precious_metal_history: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__GOLD_SILVER_HISTORY"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_precious_metal_history")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_precious_metal_history", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_precious_metal_history",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Commodities
@mcp.tool()
async def get_wti_crude_oil_prices(
    function: Literal["WTI"] = Field(..., description="The data function to retrieve. Must be set to WTI to fetch West Texas Intermediate crude oil prices."),
    interval: Literal["daily", "weekly", "monthly"] | None = Field(None, description="The time interval for price data aggregation. Choose from daily, weekly, or monthly granularity. Defaults to monthly if not specified."),
) -> dict[str, Any]:
    """Retrieves West Texas Intermediate (WTI) crude oil prices from the U.S. Energy Information Administration. Supports daily, weekly, and monthly price data sourced from FRED (Federal Reserve Bank of St. Louis)."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryWtiRequest(
            query=_models.GetQueryWtiRequestQuery(function=function, interval=interval)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_wti_crude_oil_prices: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__WTI"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_wti_crude_oil_prices")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_wti_crude_oil_prices", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_wti_crude_oil_prices",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Commodities
@mcp.tool()
async def get_brent_crude_oil_prices(
    function: Literal["BRENT"] = Field(..., description="The data source identifier. Must be set to BRENT to retrieve Brent crude oil prices."),
    interval: Literal["daily", "weekly", "monthly"] | None = Field(None, description="The time interval for price data. Choose from daily, weekly, or monthly granularity. Defaults to monthly if not specified."),
) -> dict[str, Any]:
    """Retrieves Brent (Europe) crude oil prices from the U.S. Energy Information Administration via FRED. Data is available in daily, weekly, or monthly intervals."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryBrentRequest(
            query=_models.GetQueryBrentRequestQuery(function=function, interval=interval)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_brent_crude_oil_prices: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__BRENT"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_brent_crude_oil_prices")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_brent_crude_oil_prices", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_brent_crude_oil_prices",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Commodities
@mcp.tool()
async def get_natural_gas_prices(
    function: Literal["NATURAL_GAS"] = Field(..., description="Specifies the data type to retrieve. Must be set to NATURAL_GAS to fetch Henry Hub natural gas spot prices."),
    interval: Literal["daily", "weekly", "monthly"] | None = Field(None, description="Time interval for price data aggregation. Choose from daily, weekly, or monthly granularity. Defaults to monthly if not specified."),
) -> dict[str, Any]:
    """Retrieves Henry Hub natural gas spot prices from the U.S. Energy Information Administration. Supports daily, weekly, and monthly price data sourced from the Federal Reserve Bank of St. Louis."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryNaturalGasRequest(
            query=_models.GetQueryNaturalGasRequestQuery(function=function, interval=interval)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_natural_gas_prices: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__NATURAL_GAS"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_natural_gas_prices")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_natural_gas_prices", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_natural_gas_prices",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Commodities
@mcp.tool()
async def get_copper_prices(
    function: Literal["COPPER"] = Field(..., description="The commodity type to query. Must be set to COPPER to retrieve copper price data."),
    interval: Literal["monthly", "quarterly", "annual"] | None = Field(None, description="The time interval for price data aggregation. Choose from monthly (default), quarterly, or annual intervals to match your analysis needs."),
) -> dict[str, Any]:
    """Retrieves global copper prices from the International Monetary Fund (IMF) via the Federal Reserve Economic Data (FRED) service, available in monthly, quarterly, or annual time intervals."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryCopperRequest(
            query=_models.GetQueryCopperRequestQuery(function=function, interval=interval)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_copper_prices: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__COPPER"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_copper_prices")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_copper_prices", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_copper_prices",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Commodities
@mcp.tool()
async def get_aluminum_prices(
    function: Literal["ALUMINUM"] = Field(..., description="Specifies the commodity type to query. Must be set to ALUMINUM to retrieve aluminum price data."),
    interval: Literal["monthly", "quarterly", "annual"] | None = Field(None, description="Time interval for the price data. Accepts monthly (default), quarterly, or annual aggregations."),
) -> dict[str, Any]:
    """Retrieves global aluminum prices from the International Monetary Fund via the Federal Reserve Economic Data (FRED) service, available in monthly, quarterly, or annual time intervals."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryAluminumRequest(
            query=_models.GetQueryAluminumRequestQuery(function=function, interval=interval)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_aluminum_prices: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__ALUMINUM"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_aluminum_prices")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_aluminum_prices", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_aluminum_prices",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Commodities
@mcp.tool()
async def get_wheat_price(
    function: Literal["WHEAT"] = Field(..., description="The commodity type to query. Must be set to WHEAT for this operation."),
    interval: Literal["monthly", "quarterly", "annual"] | None = Field(None, description="The time interval for the price data. Choose from monthly (default), quarterly, or annual aggregations."),
) -> dict[str, Any]:
    """Retrieve global wheat prices from the International Monetary Fund (IMF) via FRED. Data is available in monthly, quarterly, or annual intervals."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryWheatRequest(
            query=_models.GetQueryWheatRequestQuery(function=function, interval=interval)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_wheat_price: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__WHEAT"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_wheat_price")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_wheat_price", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_wheat_price",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Commodities
@mcp.tool()
async def get_corn_prices(
    function: Literal["CORN"] = Field(..., description="The commodity type to query. Must be set to CORN to retrieve corn price data."),
    interval: Literal["monthly", "quarterly", "annual"] | None = Field(None, description="The time interval for price data aggregation. Choose from monthly (default), quarterly, or annual intervals."),
) -> dict[str, Any]:
    """Retrieves global corn prices from the International Monetary Fund (IMF) via FRED (Federal Reserve Bank of St. Louis) in your choice of monthly, quarterly, or annual time intervals."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryCornRequest(
            query=_models.GetQueryCornRequestQuery(function=function, interval=interval)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_corn_prices: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__CORN"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_corn_prices")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_corn_prices", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_corn_prices",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Commodities
@mcp.tool()
async def get_cotton_prices(
    function: Literal["COTTON"] = Field(..., description="Specifies the commodity data to retrieve. Must be set to COTTON to fetch cotton price data."),
    interval: Literal["monthly", "quarterly", "annual"] | None = Field(None, description="Specifies the time interval for the price data. Choose from monthly (default), quarterly, or annual aggregations."),
) -> dict[str, Any]:
    """Retrieves global cotton prices from the International Monetary Fund via the Federal Reserve Economic Data (FRED) service, available in monthly, quarterly, or annual time intervals."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryCottonRequest(
            query=_models.GetQueryCottonRequestQuery(function=function, interval=interval)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_cotton_prices: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__COTTON"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_cotton_prices")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_cotton_prices", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_cotton_prices",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Commodities
@mcp.tool()
async def get_sugar_prices(
    function: Literal["SUGAR"] = Field(..., description="The commodity type to query. Must be set to SUGAR for sugar price data."),
    interval: Literal["monthly", "quarterly", "annual"] | None = Field(None, description="The time interval for price data aggregation. Choose from monthly, quarterly, or annual intervals. Defaults to monthly if not specified."),
) -> dict[str, Any]:
    """Retrieves global sugar prices from the International Monetary Fund (IMF) across different time horizons. Data is sourced from the Federal Reserve Bank of St. Louis FRED database."""

    # Construct request model with validation
    try:
        _request = _models.GetQuerySugarRequest(
            query=_models.GetQuerySugarRequestQuery(function=function, interval=interval)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_sugar_prices: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__SUGAR"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_sugar_prices")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_sugar_prices", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_sugar_prices",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Commodities
@mcp.tool()
async def get_coffee_prices(
    function: Literal["COFFEE"] = Field(..., description="Specifies the commodity type to query. Must be set to COFFEE to retrieve coffee price data."),
    interval: Literal["monthly", "quarterly", "annual"] | None = Field(None, description="Defines the time period aggregation for price data. Accepts monthly, quarterly, or annual intervals, with monthly as the default."),
) -> dict[str, Any]:
    """Retrieves global coffee prices from the International Monetary Fund (IMF) across different time horizons. Data represents the global price of Other Mild Arabica coffee sourced from the Federal Reserve Bank of St. Louis."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryCoffeeRequest(
            query=_models.GetQueryCoffeeRequestQuery(function=function, interval=interval)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_coffee_prices: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__COFFEE"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_coffee_prices")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_coffee_prices", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_coffee_prices",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Commodities
@mcp.tool()
async def get_commodity_price_index(
    function: Literal["ALL_COMMODITIES"] = Field(..., description="Specifies the commodity dataset to retrieve. Must be set to ALL_COMMODITIES to fetch the global price index for all commodities."),
    interval: Literal["monthly", "quarterly", "annual"] | None = Field(None, description="Defines the time period granularity for the price index data. Accepts monthly (default), quarterly, or annual intervals."),
) -> dict[str, Any]:
    """Retrieves the global price index for all commodities across different time periods. Data is sourced from the International Monetary Fund (IMF) Global Price Index and provided by the Federal Reserve Bank of St. Louis."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryAllCommoditiesRequest(
            query=_models.GetQueryAllCommoditiesRequestQuery(function=function, interval=interval)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_commodity_price_index: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__ALL_COMMODITIES"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_commodity_price_index")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_commodity_price_index", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_commodity_price_index",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Economic Indicators
@mcp.tool()
async def get_real_gdp(
    function: Literal["REAL_GDP"] = Field(..., description="The data function to retrieve; must be set to REAL_GDP to fetch Real Gross Domestic Product data."),
    interval: Literal["annual", "quarterly"] | None = Field(None, description="The time interval for the data; choose either annual or quarterly frequency. Defaults to annual if not specified."),
) -> dict[str, Any]:
    """Retrieves annual or quarterly Real Gross Domestic Product data for the United States from the Federal Reserve Economic Data (FRED) database, sourced from the U.S. Bureau of Economic Analysis."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryRealGdpRequest(
            query=_models.GetQueryRealGdpRequestQuery(function=function, interval=interval)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_real_gdp: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__REAL_GDP"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_real_gdp")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_real_gdp", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_real_gdp",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Economic Indicators
@mcp.tool()
async def get_real_gdp_per_capita(function: Literal["REAL_GDP_PER_CAPITA"] = Field(..., description="The data function to retrieve; must be set to REAL_GDP_PER_CAPITA to fetch quarterly Real GDP per Capita metrics.")) -> dict[str, Any]:
    """Retrieves quarterly Real GDP per Capita data for the United States from the Federal Reserve Economic Data (FRED) database, sourced from the U.S. Bureau of Economic Analysis."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryRealGdpPerCapitaRequest(
            query=_models.GetQueryRealGdpPerCapitaRequestQuery(function=function)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_real_gdp_per_capita: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__REAL_GDP_PER_CAPITA"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_real_gdp_per_capita")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_real_gdp_per_capita", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_real_gdp_per_capita",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Economic Indicators
@mcp.tool()
async def fetch_treasury_yield(
    function: Literal["TREASURY_YIELD"] = Field(..., description="The data function to execute. Must be set to TREASURY_YIELD to retrieve Treasury yield data."),
    interval: Literal["daily", "weekly", "monthly"] | None = Field(None, description="The time interval for data points. Choose from daily, weekly, or monthly granularity. Defaults to monthly if not specified."),
    maturity: Literal["3month", "2year", "5year", "7year", "10year", "30year"] | None = Field(None, description="The maturity timeline of the Treasury security. Select from 3-month, 2-year, 5-year, 7-year, 10-year, or 30-year constant maturities. Defaults to 10-year if not specified."),
) -> dict[str, Any]:
    """Retrieves US Treasury yield data for a specified maturity timeline at daily, weekly, or monthly intervals. Data sourced from the Federal Reserve's official market yield on constant maturity securities."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryTreasuryYieldRequest(
            query=_models.GetQueryTreasuryYieldRequestQuery(function=function, interval=interval, maturity=maturity)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for fetch_treasury_yield: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__TREASURY_YIELD"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("fetch_treasury_yield")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("fetch_treasury_yield", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="fetch_treasury_yield",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Economic Indicators
@mcp.tool()
async def get_federal_funds_rate(
    function: Literal["FEDERAL_FUNDS_RATE"] = Field(..., description="The data function to retrieve; must be set to FEDERAL_FUNDS_RATE to fetch federal funds rate data."),
    interval: Literal["daily", "weekly", "monthly"] | None = Field(None, description="The time interval for the data: daily for individual trading days, weekly for week-over-week rates, or monthly for month-over-month rates. Defaults to monthly if not specified."),
) -> dict[str, Any]:
    """Retrieves the current federal funds rate (interest rate) set by the United States Federal Reserve. Data is available at daily, weekly, or monthly intervals and sourced from the Federal Reserve Bank of St. Louis."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryFederalFundsRateRequest(
            query=_models.GetQueryFederalFundsRateRequestQuery(function=function, interval=interval)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_federal_funds_rate: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__FEDERAL_FUNDS_RATE"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_federal_funds_rate")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_federal_funds_rate", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_federal_funds_rate",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Economic Indicators
@mcp.tool()
async def get_cpi_data(
    function: Literal["CPI"] = Field(..., description="The data type to retrieve; must be set to CPI for Consumer Price Index data."),
    interval: Literal["monthly", "semiannual"] | None = Field(None, description="The reporting frequency for CPI data; choose either monthly (default) for month-over-month data or semiannual for six-month intervals."),
) -> dict[str, Any]:
    """Retrieves monthly or semiannual Consumer Price Index (CPI) data for the United States, which measures inflation levels across the broader economy."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryCpiRequest(
            query=_models.GetQueryCpiRequestQuery(function=function, interval=interval)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_cpi_data: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__CPI"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_cpi_data")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_cpi_data", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_cpi_data",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Economic Indicators
@mcp.tool()
async def get_inflation_rates(function: Literal["INFLATION"] = Field(..., description="Specifies the data function to retrieve; must be set to INFLATION to fetch annual consumer price inflation rates.")) -> dict[str, Any]:
    """Retrieves annual inflation rates based on consumer prices for the United States, sourced from the Federal Reserve Economic Data (FRED) database via the World Bank."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryInflationRequest(
            query=_models.GetQueryInflationRequestQuery(function=function)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_inflation_rates: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__INFLATION"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_inflation_rates")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_inflation_rates", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_inflation_rates",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Economic Indicators
@mcp.tool()
async def get_retail_sales(function: Literal["RETAIL_SALES"] = Field(..., description="The data function to retrieve; must be set to RETAIL_SALES to fetch monthly retail trade sales data.")) -> dict[str, Any]:
    """Retrieves monthly Advance Retail Sales data for the United States from the U.S. Census Bureau, sourced through the Federal Reserve Economic Data (FRED) system."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryRetailSalesRequest(
            query=_models.GetQueryRetailSalesRequestQuery(function=function)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_retail_sales: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__RETAIL_SALES"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_retail_sales")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_retail_sales", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_retail_sales",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Economic Indicators
@mcp.tool()
async def get_durable_goods_orders(function: Literal["DURABLES"] = Field(..., description="The data function to retrieve; must be set to DURABLES to fetch durable goods orders data.")) -> dict[str, Any]:
    """Retrieves monthly data on manufacturers' new orders for durable goods in the United States, sourced from the U.S. Census Bureau via the Federal Reserve Economic Data (FRED) database."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryDurablesRequest(
            query=_models.GetQueryDurablesRequestQuery(function=function)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_durable_goods_orders: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__DURABLES"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_durable_goods_orders")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_durable_goods_orders", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_durable_goods_orders",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Economic Indicators
@mcp.tool()
async def get_unemployment_rate(function: Literal["UNEMPLOYMENT"] = Field(..., description="Specifies the data function to retrieve; must be set to UNEMPLOYMENT to fetch unemployment rate data.")) -> dict[str, Any]:
    """Retrieves the monthly unemployment rate for the United States, showing the percentage of unemployed individuals within the labor force. Data covers the civilian population aged 16 and older residing in the 50 states or District of Columbia."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryUnemploymentRequest(
            query=_models.GetQueryUnemploymentRequestQuery(function=function)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_unemployment_rate: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__UNEMPLOYMENT"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_unemployment_rate")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_unemployment_rate", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_unemployment_rate",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Economic Indicators
@mcp.tool()
async def get_nonfarm_payroll(function: Literal["NONFARM_PAYROLL"] = Field(..., description="The data function to retrieve; must be set to NONFARM_PAYROLL to fetch monthly nonfarm payroll employment data.")) -> dict[str, Any]:
    """Retrieves monthly US nonfarm payroll employment figures from the Bureau of Labor Statistics, representing the total number of employed workers in the economy excluding farm workers, proprietors, and self-employed individuals."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryNonfarmPayrollRequest(
            query=_models.GetQueryNonfarmPayrollRequestQuery(function=function)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_nonfarm_payroll: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__NONFARM_PAYROLL"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_nonfarm_payroll")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_nonfarm_payroll", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_nonfarm_payroll",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Technical Indicators
@mcp.tool()
async def calculate_sma(
    function: Literal["SMA"] = Field(..., description="The technical indicator function to use. Must be set to SMA for simple moving average calculations."),
    symbol: str = Field(..., description="The ticker symbol of the equity or currency pair (e.g., IBM, AAPL, EUR/USD)."),
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(..., description="The time interval between consecutive data points. Choose from minute-level intervals (1, 5, 15, 30, 60 minutes) or daily/weekly/monthly aggregations."),
    time_period: int = Field(..., description="The number of data points used to calculate each moving average value. Must be at least 1. Larger values produce smoother averages over longer periods.", ge=1),
    series_type: Literal["close", "open", "high", "low"] = Field(..., description="The price type to use in calculations: open (opening price), close (closing price), high (highest price), or low (lowest price) for each interval."),
    month: str | None = Field(None, description="Optional. Retrieve SMA values for a specific month in history using YYYY-MM format (e.g., 2009-01). If omitted, calculations use the default historical data length for the selected interval.", pattern="^\\d{4}-\\d{2}$"),
) -> dict[str, Any]:
    """Calculates the simple moving average (SMA) for a given equity or currency pair over a specified time interval and period. Returns SMA values based on your chosen price type (open, close, high, or low)."""

    # Construct request model with validation
    try:
        _request = _models.GetQuerySmaRequest(
            query=_models.GetQuerySmaRequestQuery(function=function, symbol=symbol, interval=interval, time_period=time_period, series_type=series_type, month=month)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for calculate_sma: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__SMA"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("calculate_sma")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("calculate_sma", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="calculate_sma",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Technical Indicators
@mcp.tool()
async def calculate_ema(
    function: Literal["EMA"] = Field(..., description="The technical indicator type. Must be set to EMA for exponential moving average calculations."),
    symbol: str = Field(..., description="The ticker symbol of the equity or currency pair to analyze (e.g., IBM, AAPL, EUR/USD)."),
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(..., description="The time interval between consecutive data points. Choose from minute-level intervals (1, 5, 15, 30, 60 minutes) or longer periods (daily, weekly, monthly)."),
    time_period: int = Field(..., description="The number of data points used to calculate each EMA value. Must be a positive integer of at least 1.", ge=1),
    series_type: Literal["close", "open", "high", "low"] = Field(..., description="The price type to use in calculations. Select from closing price, opening price, high price, or low price for each interval."),
    month: str | None = Field(None, description="Optional historical month for calculations in YYYY-MM format (e.g., 2009-01). If omitted, uses the default length of the underlying time series data.", pattern="^\\d{4}-\\d{2}$"),
) -> dict[str, Any]:
    """Calculates exponential moving average (EMA) values for a given equity or currency pair over a specified time interval and period."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryEmaRequest(
            query=_models.GetQueryEmaRequestQuery(function=function, symbol=symbol, interval=interval, time_period=time_period, series_type=series_type, month=month)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for calculate_ema: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__EMA"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("calculate_ema")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("calculate_ema", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="calculate_ema",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Technical Indicators
@mcp.tool()
async def calculate_weighted_moving_average(
    function: Literal["WMA"] = Field(..., description="The technical indicator function to apply. Must be WMA (Weighted Moving Average)."),
    symbol: str = Field(..., description="The stock ticker symbol to analyze (e.g., IBM, AAPL). Case-insensitive."),
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(..., description="The time interval between consecutive data points in the returned series. Choose from minute-level intervals (1, 5, 15, 30, 60 minutes) or daily/weekly/monthly aggregations."),
    time_period: int = Field(..., description="The number of data points used to calculate each WMA value. Must be a positive integer of at least 1. Larger values produce smoother averages over longer periods.", ge=1),
    series_type: Literal["close", "open", "high", "low"] = Field(..., description="The price type to use in calculations. Select from closing price, opening price, high price, or low price for each interval."),
    month: str | None = Field(None, description="Optional: Retrieve historical WMA data for a specific month in YYYY-MM format (e.g., 2009-01). Omit to get the most recent data."),
) -> dict[str, Any]:
    """Calculates weighted moving average (WMA) values for a given equity symbol across specified time intervals. Returns a time series of WMA data points based on your chosen price type and lookback period."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryWmaRequest(
            query=_models.GetQueryWmaRequestQuery(function=function, symbol=symbol, interval=interval, time_period=time_period, series_type=series_type, month=month)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for calculate_weighted_moving_average: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__WMA"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("calculate_weighted_moving_average")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("calculate_weighted_moving_average", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="calculate_weighted_moving_average",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Technical Indicators
@mcp.tool()
async def calculate_dema(
    function: Literal["DEMA"] = Field(..., description="The technical indicator type; must be set to DEMA for this operation."),
    symbol: str = Field(..., description="The stock ticker symbol (e.g., IBM) for which to calculate the moving average."),
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(..., description="The time interval between consecutive data points: 1-minute, 5-minute, 15-minute, 30-minute, 60-minute, daily, weekly, or monthly."),
    time_period: int = Field(..., description="The number of data points used in each moving average calculation; determines the sensitivity and smoothing of the DEMA values."),
    series_type: Literal["close", "open", "high", "low"] = Field(..., description="The price type to use in calculations: closing price, opening price, high price, or low price for the interval."),
    month: str | None = Field(None, description="Optional historical month for retrieving past DEMA values, specified in YYYY-MM format (e.g., 2009-01). Omit to get current data."),
) -> dict[str, Any]:
    """Calculates the double exponential moving average (DEMA) for a given equity symbol, providing smoothed price trend analysis across various time intervals and historical periods."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryDemaRequest(
            query=_models.GetQueryDemaRequestQuery(function=function, symbol=symbol, interval=interval, time_period=time_period, series_type=series_type, month=month)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for calculate_dema: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__DEMA"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("calculate_dema")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("calculate_dema", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="calculate_dema",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Technical Indicators
@mcp.tool()
async def calculate_tema(
    function: Literal["TEMA"] = Field(..., description="The technical indicator type; must be set to TEMA for this operation."),
    symbol: str = Field(..., description="The stock ticker symbol to analyze (e.g., IBM, AAPL)."),
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(..., description="The time interval between consecutive data points, ranging from 1-minute intraday data to monthly historical data."),
    time_period: int = Field(..., description="The number of data points used to calculate each TEMA value; must be at least 1. Larger values produce smoother averages.", ge=1),
    series_type: Literal["close", "open", "high", "low"] = Field(..., description="The price type to use in calculations: closing price, opening price, high price, or low price for the interval."),
    month: str | None = Field(None, description="Optional historical month filter in YYYY-MM format to retrieve TEMA values for a specific month. If omitted, calculations use the default time series length.", pattern="^\\d{4}-\\d{2}$"),
) -> dict[str, Any]:
    """Calculates the Triple Exponential Moving Average (TEMA) for a given equity symbol, providing smoothed price trend analysis across various time intervals."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryTemaRequest(
            query=_models.GetQueryTemaRequestQuery(function=function, symbol=symbol, interval=interval, time_period=time_period, series_type=series_type, month=month)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for calculate_tema: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__TEMA"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("calculate_tema")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("calculate_tema", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="calculate_tema",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Technical Indicators
@mcp.tool()
async def calculate_triangular_moving_average(
    function: Literal["TRIMA"] = Field(..., description="The technical indicator type. Must be set to TRIMA for this operation."),
    symbol: str = Field(..., description="The stock ticker symbol to analyze (e.g., IBM, AAPL)."),
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(..., description="The time interval between consecutive data points. Choose from intraday intervals (1, 5, 15, or 30 minutes, or 1 hour) or daily/weekly/monthly historical data."),
    time_period: int = Field(..., description="The number of data points used to calculate each TRIMA value. Must be a positive integer (minimum 1). Larger values produce smoother averages.", ge=1),
    series_type: Literal["close", "open", "high", "low"] = Field(..., description="The price type to use in calculations. Select from closing, opening, high, or low prices for each interval."),
    month: str | None = Field(None, description="Optional historical month to retrieve data for, specified in YYYY-MM format. If omitted, returns the most recent data based on the default time range."),
) -> dict[str, Any]:
    """Calculates the triangular moving average (TRIMA) for a given equity symbol across specified time intervals. TRIMA is a double-smoothed moving average that emphasizes mid-range price data."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryTrimaRequest(
            query=_models.GetQueryTrimaRequestQuery(function=function, symbol=symbol, interval=interval, time_period=time_period, series_type=series_type, month=month)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for calculate_triangular_moving_average: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__TRIMA"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("calculate_triangular_moving_average")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("calculate_triangular_moving_average", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="calculate_triangular_moving_average",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Technical Indicators
@mcp.tool()
async def calculate_kama(
    function: Literal["KAMA"] = Field(..., description="The technical indicator type. Must be set to KAMA for this operation."),
    symbol: str = Field(..., description="The stock ticker symbol to analyze (e.g., IBM, AAPL)."),
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(..., description="The time interval between data points. Choose from intraday intervals (1, 5, 15, or 30 minutes, or 1 hour) or longer periods (daily, weekly, or monthly)."),
    time_period: int = Field(..., description="The number of periods used to calculate each KAMA value. Must be at least 1; larger values produce smoother averages.", ge=1),
    series_type: Literal["close", "open", "high", "low"] = Field(..., description="The price type to use in calculations. Select from closing, opening, high, or low prices."),
    month: str | None = Field(None, description="Optional historical month for the calculation in YYYY-MM format. If not specified, the indicator uses the default time series length for the selected interval."),
) -> dict[str, Any]:
    """Calculates the Kaufman Adaptive Moving Average (KAMA) for a given equity symbol, providing adaptive trend-following values that adjust to market volatility and noise."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryKamaRequest(
            query=_models.GetQueryKamaRequestQuery(function=function, symbol=symbol, interval=interval, time_period=time_period, series_type=series_type, month=month)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for calculate_kama: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__KAMA"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("calculate_kama")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("calculate_kama", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="calculate_kama",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Technical Indicators
@mcp.tool()
async def get_mama_indicator(
    function: Literal["MAMA"] = Field(..., description="The technical indicator type; must be set to MAMA for this operation."),
    symbol: str = Field(..., description="The stock ticker symbol to analyze (e.g., IBM, AAPL)."),
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(..., description="The time interval between data points: 1-minute, 5-minute, 15-minute, 30-minute, 60-minute, daily, weekly, or monthly."),
    series_type: Literal["close", "open", "high", "low"] = Field(..., description="The price type to use in calculations: closing price, opening price, high price, or low price."),
    month: str | None = Field(None, description="Optional historical month for the calculation in YYYY-MM format. If omitted, uses the default length of the underlying time series data."),
    fastlimit: float | None = Field(None, description="Optional fast limit parameter controlling the upper bound of the adaptive moving average acceleration. Accepts positive decimal values; defaults to 0.01."),
    slowlimit: float | None = Field(None, description="Optional slow limit parameter controlling the lower bound of the adaptive moving average acceleration. Accepts positive decimal values; defaults to 0.01."),
) -> dict[str, Any]:
    """Retrieves MESA adaptive moving average (MAMA) values for a specified equity, allowing analysis of trend direction and momentum across multiple timeframes and price types."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryMamaRequest(
            query=_models.GetQueryMamaRequestQuery(function=function, symbol=symbol, interval=interval, series_type=series_type, month=month, fastlimit=fastlimit, slowlimit=slowlimit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_mama_indicator: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__MAMA"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_mama_indicator")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_mama_indicator", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_mama_indicator",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Technical Indicators
@mcp.tool()
async def calculate_vwap(
    function: Literal["VWAP"] = Field(..., description="The technical indicator type; must be set to VWAP for this operation."),
    symbol: str = Field(..., description="The stock ticker symbol (e.g., IBM) for which to calculate VWAP."),
    interval: Literal["1min", "5min", "15min", "30min", "60min"] = Field(..., description="The time interval between consecutive data points in the intraday series; choose from 1-minute, 5-minute, 15-minute, 30-minute, or 60-minute intervals."),
    month: str | None = Field(None, description="Optional historical month to retrieve VWAP data for; specify in YYYY-MM format (e.g., 2009-01). If omitted, returns the most recent data."),
) -> dict[str, Any]:
    """Calculate the volume weighted average price (VWAP) for intraday time series data of a given equity, helping identify fair value and trend direction based on price and volume."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryVwapRequest(
            query=_models.GetQueryVwapRequestQuery(function=function, symbol=symbol, interval=interval, month=month)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for calculate_vwap: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__VWAP"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("calculate_vwap")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("calculate_vwap", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="calculate_vwap",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Technical Indicators
@mcp.tool()
async def calculate_t3_moving_average(
    function: Literal["T3"] = Field(..., description="The technical indicator type. Must be set to T3 for Tilson triple exponential moving average calculations."),
    symbol: str = Field(..., description="The equity ticker symbol (e.g., IBM, AAPL) for which to calculate the moving average."),
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(..., description="The time interval between data points in the series. Choose from 1-minute, 5-minute, 15-minute, 30-minute, 60-minute, daily, weekly, or monthly intervals."),
    time_period: int = Field(..., description="The number of data points used to calculate each moving average value. Must be a positive integer of at least 1.", ge=1),
    series_type: Literal["close", "open", "high", "low"] = Field(..., description="The price type to use in calculations. Select from closing price, opening price, high price, or low price for each interval."),
    month: str | None = Field(None, description="Optional. Retrieve historical technical indicator data for a specific month. Specify the month in YYYY-MM format (e.g., 2009-01)."),
) -> dict[str, Any]:
    """Calculates the Tilson T3 triple exponential moving average for a given equity symbol. Returns smoothed price data based on your specified time interval and period."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryT3Request(
            query=_models.GetQueryT3RequestQuery(function=function, symbol=symbol, interval=interval, time_period=time_period, series_type=series_type, month=month)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for calculate_t3_moving_average: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__T3"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("calculate_t3_moving_average")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("calculate_t3_moving_average", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="calculate_t3_moving_average",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Technical Indicators
@mcp.tool()
async def calculate_macd(
    function: Literal["MACD"] = Field(..., description="The technical indicator type; must be set to MACD for this operation."),
    symbol: str = Field(..., description="The ticker symbol of the equity or forex pair to analyze (e.g., IBM, EURUSD)."),
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(..., description="The time interval between consecutive data points in the time series. Choose from minute-level intervals (1, 5, 15, or 30 minutes), hourly (60 minutes), or daily/weekly/monthly aggregations."),
    series_type: Literal["close", "open", "high", "low"] = Field(..., description="The price type to use for calculations: closing price, opening price, high price, or low price for each interval."),
    month: str | None = Field(None, description="Optional historical month to retrieve data for, specified in YYYY-MM format. If omitted, returns the most recent data available."),
    fastperiod: int | None = Field(None, description="The number of periods for the fast exponential moving average. Must be a positive integer; defaults to 12 if not specified.", ge=1),
    slowperiod: int | None = Field(None, description="The number of periods for the slow exponential moving average. Must be a positive integer; defaults to 26 if not specified.", ge=1),
    signalperiod: int | None = Field(None, description="The number of periods for the signal line exponential moving average. Must be a positive integer; defaults to 9 if not specified.", ge=1),
) -> dict[str, Any]:
    """Calculates Moving Average Convergence/Divergence (MACD) technical indicator values for a given equity or forex pair, returning MACD line, signal line, and histogram data across specified time intervals."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryMacdRequest(
            query=_models.GetQueryMacdRequestQuery(function=function, symbol=symbol, interval=interval, series_type=series_type, month=month, fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for calculate_macd: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__MACD"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("calculate_macd")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("calculate_macd", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="calculate_macd",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Technical Indicators
@mcp.tool()
async def calculate_macd_extended(
    function: Literal["MACDEXT"] = Field(..., description="The technical indicator function to execute. Must be set to MACDEXT for extended MACD calculation with configurable moving average types."),
    symbol: str = Field(..., description="The stock ticker symbol to analyze (e.g., IBM, AAPL). Case-insensitive."),
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(..., description="The time interval between data points. Choose from minute-level intervals (1, 5, 15, 30, 60 minutes) or daily/weekly/monthly aggregations."),
    series_type: Literal["close", "open", "high", "low"] = Field(..., description="The price type to use in calculations: closing price, opening price, high price, or low price for the interval."),
    month: str | None = Field(None, description="Optional historical month for backtesting in YYYY-MM format (e.g., 2009-01). If omitted, uses the most recent available data."),
    fastperiod: int | None = Field(None, description="The number of periods for the fast-moving average. Must be a positive integer; defaults to 12 if not specified.", ge=1),
    slowperiod: int | None = Field(None, description="The number of periods for the slow-moving average. Must be a positive integer; defaults to 26 if not specified.", ge=1),
    signalperiod: int | None = Field(None, description="The number of periods for the signal line (exponential moving average of MACD). Must be a positive integer; defaults to 9 if not specified.", ge=1),
) -> dict[str, Any]:
    """Calculate MACD (Moving Average Convergence Divergence) with customizable moving average types for technical analysis of equity price movements. Returns MACD line, signal line, and histogram values."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryMacdextRequest(
            query=_models.GetQueryMacdextRequestQuery(function=function, symbol=symbol, interval=interval, series_type=series_type, month=month, fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for calculate_macd_extended: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__MACDEXT"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("calculate_macd_extended")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("calculate_macd_extended", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="calculate_macd_extended",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Technical Indicators
@mcp.tool()
async def get_stochastic_oscillator(
    function: Literal["STOCH"] = Field(..., description="The technical indicator type. Must be set to STOCH for stochastic oscillator calculations."),
    symbol: str = Field(..., description="The ticker symbol of the equity or forex pair to analyze (e.g., IBM, EURUSD)."),
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(..., description="The time interval between data points. Choose from: 1min, 5min, 15min, 30min, 60min for intraday data, or daily, weekly, monthly for longer-term analysis."),
    month: str | None = Field(None, description="Optional historical month for the calculation in YYYY-MM format. If not specified, the indicator is calculated on the default time series data for the selected interval."),
    slowkperiod: int | None = Field(None, description="The number of periods for the slow K moving average smoothing. Must be a positive integer; defaults to 3 if not specified.", ge=1),
    slowdperiod: int | None = Field(None, description="The number of periods for the slow D moving average smoothing. Must be a positive integer; defaults to 3 if not specified.", ge=1),
) -> dict[str, Any]:
    """Retrieves stochastic oscillator (STOCH) technical indicator values for a specified equity or forex pair at a given time interval. The stochastic oscillator measures momentum by comparing closing prices to price ranges over a defined period."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryStochRequest(
            query=_models.GetQueryStochRequestQuery(function=function, symbol=symbol, interval=interval, month=month, slowkperiod=slowkperiod, slowdperiod=slowdperiod)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_stochastic_oscillator: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__STOCH"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_stochastic_oscillator")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_stochastic_oscillator", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_stochastic_oscillator",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Technical Indicators
@mcp.tool()
async def get_stochastic_fast_indicator(
    function: Literal["STOCHF"] = Field(..., description="The technical indicator type. Must be set to STOCHF for this operation."),
    symbol: str = Field(..., description="The equity ticker symbol (e.g., IBM, AAPL). Used to identify the security for which to calculate the indicator."),
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(..., description="The time interval between data points. Supported intervals range from 1-minute to monthly granularity, allowing analysis across intraday and longer-term timeframes."),
    month: str | None = Field(None, description="Optional historical month for calculation in YYYY-MM format (e.g., 2009-01). When omitted, the indicator is calculated using the default length of the underlying time series data."),
) -> dict[str, Any]:
    """Retrieves stochastic fast (STOCHF) technical indicator values for a given equity symbol. The STOCHF oscillator measures momentum by comparing closing prices to price ranges over a specified period."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryStochfRequest(
            query=_models.GetQueryStochfRequestQuery(function=function, symbol=symbol, interval=interval, month=month)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_stochastic_fast_indicator: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__STOCHF"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_stochastic_fast_indicator")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_stochastic_fast_indicator", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_stochastic_fast_indicator",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Technical Indicators
@mcp.tool()
async def calculate_rsi(
    function: Literal["RSI"] = Field(..., description="The technical indicator type. Must be set to RSI for this operation."),
    symbol: str = Field(..., description="The ticker symbol of the equity or forex pair to analyze (e.g., IBM, AAPL, EUR/USD)."),
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(..., description="The time interval between consecutive data points. Choose from: 1min, 5min, 15min, 30min, 60min, daily, weekly, or monthly."),
    time_period: int = Field(..., description="The number of data points used to calculate each RSI value. Must be a positive integer (e.g., 10, 14, 60, 200).", ge=1),
    series_type: Literal["close", "open", "high", "low"] = Field(..., description="The price type to use in calculations. Choose from: close, open, high, or low."),
    month: str | None = Field(None, description="Optional historical month for which to calculate RSI values, specified in YYYY-MM format (e.g., 2009-01). If omitted, uses the default time series data."),
) -> dict[str, Any]:
    """Calculates the Relative Strength Index (RSI) technical indicator for a given equity or forex pair over a specified time period and interval."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryRsiRequest(
            query=_models.GetQueryRsiRequestQuery(function=function, symbol=symbol, interval=interval, time_period=time_period, series_type=series_type, month=month)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for calculate_rsi: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__RSI"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("calculate_rsi")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("calculate_rsi", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="calculate_rsi",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Technical Indicators
@mcp.tool()
async def calculate_stochrsi(
    function: Literal["STOCHRSI"] = Field(..., description="The technical indicator type. Must be set to STOCHRSI for this operation."),
    symbol: str = Field(..., description="The stock ticker symbol to analyze (e.g., IBM, AAPL)."),
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(..., description="The time interval between data points. Choose from intraday intervals (1, 5, 15, or 30 minutes, or 1 hour) or daily/weekly/monthly historical data."),
    time_period: int = Field(..., description="The number of periods used to calculate each STOCHRSI value. Must be a positive integer (e.g., 10, 14, 21)."),
    series_type: Literal["close", "open", "high", "low"] = Field(..., description="The price type to use in calculations. Select from closing, opening, high, or low prices."),
    month: str | None = Field(None, description="Optional. Retrieve STOCHRSI values for a specific month in history using YYYY-MM format (e.g., 2009-01). If omitted, returns the most recent data."),
) -> dict[str, Any]:
    """Calculate the Stochastic Relative Strength Index (STOCHRSI) for a given equity symbol. Returns STOCHRSI values at your specified time interval and lookback period."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryStochrsiRequest(
            query=_models.GetQueryStochrsiRequestQuery(function=function, symbol=symbol, interval=interval, time_period=time_period, series_type=series_type, month=month)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for calculate_stochrsi: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__STOCHRSI"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("calculate_stochrsi")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("calculate_stochrsi", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="calculate_stochrsi",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Technical Indicators
@mcp.tool()
async def get_williams_percent_r(
    function: Literal["WILLR"] = Field(..., description="The technical indicator type. Must be set to WILLR for Williams' %R calculation."),
    symbol: str = Field(..., description="The equity ticker symbol (e.g., IBM, AAPL). Used to identify which security to analyze."),
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(..., description="The time interval between consecutive data points. Choose from minute-level intervals (1, 5, 15, or 30 minutes, or 1 hour) or daily/weekly/monthly aggregations."),
    time_period: int = Field(..., description="The number of periods used in the WILLR calculation. Must be a positive integer (e.g., 60 for a 60-period lookback window).", ge=1),
    month: str | None = Field(None, description="Optional filter to retrieve historical WILLR values for a specific month in YYYY-MM format (e.g., 2009-01). If omitted, returns the most recent data."),
) -> dict[str, Any]:
    """Retrieves Williams' %R (WILLR) momentum oscillator values for a given equity symbol. This technical indicator measures the level of the closing price relative to the highest high over a specified period, helping identify overbought and oversold conditions."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryWillrRequest(
            query=_models.GetQueryWillrRequestQuery(function=function, symbol=symbol, interval=interval, time_period=time_period, month=month)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_williams_percent_r: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__WILLR"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_williams_percent_r")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_williams_percent_r", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_williams_percent_r",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Technical Indicators
@mcp.tool()
async def calculate_adx(
    function: Literal["ADX"] = Field(..., description="The technical indicator type; must be set to ADX for this operation."),
    symbol: str = Field(..., description="The ticker symbol of the equity or forex pair (e.g., IBM, EURUSD)."),
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(..., description="The time interval between data points: 1min, 5min, 15min, 30min, 60min for intraday data, or daily, weekly, monthly for longer-term analysis."),
    time_period: int = Field(..., description="The number of periods used to calculate each ADX value; must be a positive integer (e.g., 10, 14, 60, 200).", ge=1),
    month: str | None = Field(None, description="Optional historical month filter in YYYY-MM format (e.g., 2009-01) to retrieve ADX values for a specific month; if omitted, uses the default time series length for the selected interval.", pattern="^\\d{4}-\\d{2}$"),
) -> dict[str, Any]:
    """Calculates the Average Directional Movement Index (ADX) for a given equity or forex pair, returning trend strength values across your specified time interval and period."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryAdxRequest(
            query=_models.GetQueryAdxRequestQuery(function=function, symbol=symbol, interval=interval, time_period=time_period, month=month)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for calculate_adx: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__ADX"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("calculate_adx")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("calculate_adx", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="calculate_adx",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Technical Indicators
@mcp.tool()
async def get_adxr_values(
    function: Literal["ADXR"] = Field(..., description="The technical indicator type; must be set to ADXR for this operation."),
    symbol: str = Field(..., description="The stock ticker symbol (e.g., IBM, AAPL) for which to retrieve ADXR values."),
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(..., description="The time interval between consecutive data points, ranging from 1-minute to monthly granularity."),
    time_period: int = Field(..., description="The number of data points used to calculate each ADXR value; must be at least 1.", ge=1),
    month: str | None = Field(None, description="Optional historical month to retrieve data from, specified in YYYY-MM format (e.g., 2009-01). If omitted, returns the most recent data."),
) -> dict[str, Any]:
    """Retrieves Average Directional Movement Index Rating (ADXR) values for a specified equity, providing trend strength analysis over a chosen time interval and historical period."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryAdxrRequest(
            query=_models.GetQueryAdxrRequestQuery(function=function, symbol=symbol, interval=interval, time_period=time_period, month=month)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_adxr_values: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__ADXR"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_adxr_values")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_adxr_values", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_adxr_values",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Technical Indicators
@mcp.tool()
async def calculate_absolute_price_oscillator(
    function: Literal["APO"] = Field(..., description="The technical indicator function to calculate. Must be set to APO for this operation."),
    symbol: str = Field(..., description="The stock ticker symbol for which to calculate the APO (e.g., IBM, AAPL)."),
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(..., description="The time interval between consecutive data points in the returned series. Choose from minute-level intervals (1, 5, 15, or 30 minutes, or 1 hour) or daily/weekly/monthly historical data."),
    series_type: Literal["close", "open", "high", "low"] = Field(..., description="The price type to use in the calculation. Select from the open, high, low, or closing price of each interval."),
    fastperiod: int | None = Field(None, description="The number of periods for the faster exponential moving average. Accepts any positive integer; defaults to 12 if not specified."),
    slowperiod: int | None = Field(None, description="The number of periods for the slower exponential moving average. Accepts any positive integer; defaults to 26 if not specified."),
    month: str | None = Field(None, description="Retrieve APO values for a specific month in history using YYYY-MM format (e.g., 2009-01). If omitted, returns the most recent data available."),
) -> dict[str, Any]:
    """Calculates the Absolute Price Oscillator (APO) technical indicator for a given equity, measuring momentum by comparing two exponential moving averages. Returns APO values at your specified time interval."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryApoRequest(
            query=_models.GetQueryApoRequestQuery(function=function, symbol=symbol, interval=interval, series_type=series_type, fastperiod=fastperiod, slowperiod=slowperiod, month=month)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for calculate_absolute_price_oscillator: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__APO"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("calculate_absolute_price_oscillator")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("calculate_absolute_price_oscillator", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="calculate_absolute_price_oscillator",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Technical Indicators
@mcp.tool()
async def calculate_ppo(
    function: Literal["PPO"] = Field(..., description="The technical indicator type. Must be set to PPO for this operation."),
    symbol: str = Field(..., description="The stock ticker symbol (e.g., IBM, AAPL) for which to calculate the PPO."),
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(..., description="The time interval between consecutive data points. Choose from minute-level intervals (1, 5, 15, or 30 minutes, or 1 hour) or daily/weekly/monthly aggregations."),
    series_type: Literal["close", "open", "high", "low"] = Field(..., description="The price type to use in calculations. Select from open, high, low, or close prices."),
    fastperiod: int | None = Field(None, description="The period for the fast exponential moving average. Must be a positive integer; defaults to 12 if not specified.", ge=1),
    slowperiod: int | None = Field(None, description="The period for the slow exponential moving average. Must be a positive integer; defaults to 26 if not specified.", ge=1),
    month: str | None = Field(None, description="Optional historical month to retrieve PPO values for, specified in YYYY-MM format (e.g., 2009-01). If omitted, returns the most recent data.", pattern="^\\d{4}-\\d{2}$"),
) -> dict[str, Any]:
    """Calculates the Percentage Price Oscillator (PPO) for an equity, a momentum indicator that measures the relationship between two exponential moving averages. Returns PPO values across a specified time interval and historical period."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryPpoRequest(
            query=_models.GetQueryPpoRequestQuery(function=function, symbol=symbol, interval=interval, series_type=series_type, fastperiod=fastperiod, slowperiod=slowperiod, month=month)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for calculate_ppo: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__PPO"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("calculate_ppo")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("calculate_ppo", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="calculate_ppo",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Technical Indicators
@mcp.tool()
async def calculate_momentum(
    function: Literal["MOM"] = Field(..., description="The technical indicator type. Must be set to MOM for momentum calculations."),
    symbol: str = Field(..., description="The stock ticker symbol to analyze (e.g., IBM, AAPL)."),
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(..., description="The time interval between consecutive data points. Choose from: 1min, 5min, 15min, 30min, 60min for intraday data, or daily, weekly, monthly for longer-term analysis."),
    time_period: int = Field(..., description="The number of data points used to calculate each momentum value. Must be a positive integer (e.g., 10, 60, 200). Larger values smooth out short-term fluctuations.", ge=1),
    series_type: Literal["close", "open", "high", "low"] = Field(..., description="The price type to use in calculations. Choose from: close, open, high, or low prices."),
    month: str | None = Field(None, description="Optional historical month for analysis in YYYY-MM format (e.g., 2009-01). If not specified, calculations use the default length of available time series data for the selected interval."),
) -> dict[str, Any]:
    """Calculates momentum (MOM) technical indicator values for a given equity symbol. Returns momentum measurements based on price changes over a specified time period and interval."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryMomRequest(
            query=_models.GetQueryMomRequestQuery(function=function, symbol=symbol, interval=interval, time_period=time_period, series_type=series_type, month=month)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for calculate_momentum: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__MOM"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("calculate_momentum")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("calculate_momentum", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="calculate_momentum",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Technical Indicators
@mcp.tool()
async def get_balance_of_power(
    function: Literal["BOP"] = Field(..., description="The technical indicator type. Must be set to BOP for Balance of Power calculations."),
    symbol: str = Field(..., description="The stock ticker symbol (e.g., IBM, AAPL) for which to calculate the Balance of Power indicator."),
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(..., description="The time interval between consecutive data points. Choose from: 1min, 5min, 15min, 30min, 60min for intraday data, or daily, weekly, monthly for longer-term analysis."),
    month: str | None = Field(None, description="Optional. Retrieve Balance of Power values for a specific month in history using YYYY-MM format (e.g., 2009-01). If omitted, returns data based on the default time series length for the selected interval."),
) -> dict[str, Any]:
    """Retrieves Balance of Power (BOP) technical indicator values for a specified equity symbol at your chosen time interval. Optionally filter results to a specific month in history."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryBopRequest(
            query=_models.GetQueryBopRequestQuery(function=function, symbol=symbol, interval=interval, month=month)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_balance_of_power: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__BOP"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_balance_of_power")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_balance_of_power", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_balance_of_power",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Technical Indicators
@mcp.tool()
async def calculate_commodity_channel_index(
    function: Literal["CCI"] = Field(..., description="The technical indicator type. Must be set to CCI for this operation."),
    symbol: str = Field(..., description="The ticker symbol of the equity or forex pair to analyze (e.g., IBM, EURUSD)."),
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(..., description="The time interval between consecutive data points in the returned series. Choose from minute-level intervals (1, 5, 15, or 30 minutes), hourly (60 minutes), or daily/weekly/monthly aggregations."),
    time_period: int = Field(..., description="The number of data points used to calculate each CCI value. Must be a positive integer of at least 1. Larger values smooth the indicator over longer periods.", ge=1),
    month: str | None = Field(None, description="Optional. Retrieve CCI values for a specific month in history using YYYY-MM format (e.g., 2009-01). If omitted, returns data using the default historical length."),
) -> dict[str, Any]:
    """Calculates the Commodity Channel Index (CCI) technical indicator for a given equity or forex pair, returning CCI values across a specified time series at your chosen interval."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryCciRequest(
            query=_models.GetQueryCciRequestQuery(function=function, symbol=symbol, interval=interval, time_period=time_period, month=month)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for calculate_commodity_channel_index: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__CCI"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("calculate_commodity_channel_index")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("calculate_commodity_channel_index", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="calculate_commodity_channel_index",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Technical Indicators
@mcp.tool()
async def calculate_momentum_oscillator(
    function: Literal["CMO"] = Field(..., description="The technical indicator type; must be set to CMO for Chande Momentum Oscillator calculations."),
    symbol: str = Field(..., description="The stock ticker symbol for which to calculate the momentum oscillator (e.g., IBM, AAPL)."),
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(..., description="The time interval between consecutive data points, ranging from 1-minute intraday data to monthly historical data."),
    time_period: int = Field(..., description="The number of data points used in each CMO calculation; must be at least 1. Larger values smooth the oscillator over longer periods.", ge=1),
    series_type: Literal["close", "open", "high", "low"] = Field(..., description="The price type to use for calculations: closing price, opening price, high price, or low price for each interval."),
    month: str | None = Field(None, description="Optional historical month to retrieve CMO values for a specific period in the past, specified in YYYY-MM format."),
) -> dict[str, Any]:
    """Calculates the Chande Momentum Oscillator (CMO) for a given equity, providing momentum-based technical analysis values across specified time intervals and historical periods."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryCmoRequest(
            query=_models.GetQueryCmoRequestQuery(function=function, symbol=symbol, interval=interval, time_period=time_period, series_type=series_type, month=month)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for calculate_momentum_oscillator: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__CMO"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("calculate_momentum_oscillator")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("calculate_momentum_oscillator", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="calculate_momentum_oscillator",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Technical Indicators
@mcp.tool()
async def calculate_equity_roc(
    function: Literal["ROC"] = Field(..., description="The technical indicator type. Must be set to ROC for rate of change calculations."),
    symbol: str = Field(..., description="The stock ticker symbol (e.g., IBM, AAPL) for which to calculate ROC values."),
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(..., description="The time interval between consecutive data points. Choose from intraday intervals (1, 5, 15, 30, or 60 minutes) or longer periods (daily, weekly, or monthly)."),
    time_period: int = Field(..., description="The number of periods used to calculate each ROC value. Must be a positive integer (e.g., 10 means ROC is calculated over the last 10 periods)."),
    series_type: Literal["close", "open", "high", "low"] = Field(..., description="The price type to use in calculations. Choose from closing price, opening price, high price, or low price for each period."),
    month: str | None = Field(None, description="Optional. Retrieve historical ROC values for a specific month in YYYY-MM format (e.g., 2009-01). If omitted, returns the most recent data based on the selected interval."),
) -> dict[str, Any]:
    """Calculates the rate of change (ROC) technical indicator for an equity, measuring the percentage change in price over a specified period. Returns ROC values at your chosen time interval."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryRocRequest(
            query=_models.GetQueryRocRequestQuery(function=function, symbol=symbol, interval=interval, time_period=time_period, series_type=series_type, month=month)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for calculate_equity_roc: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__ROC"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("calculate_equity_roc")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("calculate_equity_roc", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="calculate_equity_roc",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Technical Indicators
@mcp.tool()
async def calculate_rocr(
    function: Literal["ROCR"] = Field(..., description="The technical indicator type. Must be set to ROCR for this operation."),
    symbol: str = Field(..., description="The stock ticker symbol (e.g., IBM, AAPL) for which to calculate ROCR values."),
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(..., description="The time interval between data points. Choose from intraday intervals (1min, 5min, 15min, 30min, 60min) or longer periods (daily, weekly, monthly)."),
    time_period: int = Field(..., description="The number of periods to use in the ROCR calculation. Must be a positive integer (e.g., 10, 60, 200). Larger values smooth the indicator over longer timeframes.", ge=1),
    series_type: Literal["close", "open", "high", "low"] = Field(..., description="The price type to use in calculations: closing price, opening price, high price, or low price for each period."),
    month: str | None = Field(None, description="Optional. Retrieve ROCR values for a specific month in history using YYYY-MM format (e.g., 2009-01). If omitted, uses the default historical data length for the selected interval."),
) -> dict[str, Any]:
    """Calculates the rate of change ratio (ROCR) technical indicator for an equity, measuring the percentage change in price over a specified period. Returns ROCR values at your chosen time interval."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryRocrRequest(
            query=_models.GetQueryRocrRequestQuery(function=function, symbol=symbol, interval=interval, time_period=time_period, series_type=series_type, month=month)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for calculate_rocr: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__ROCR"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("calculate_rocr")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("calculate_rocr", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="calculate_rocr",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Technical Indicators
@mcp.tool()
async def calculate_aroon_indicator(
    function: Literal["AROON"] = Field(..., description="The technical indicator type; must be set to AROON for this operation."),
    symbol: str = Field(..., description="The ticker symbol of the equity or forex pair to analyze (e.g., IBM, EURUSD)."),
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(..., description="The time interval between data points, ranging from 1-minute to monthly granularity."),
    time_period: int = Field(..., description="The number of periods used to calculate the Aroon values; typically 14 periods is standard for this indicator."),
    month: str | None = Field(None, description="Optional historical month in YYYY-MM format to retrieve Aroon values for a specific month; if omitted, uses the most recent data."),
) -> dict[str, Any]:
    """Calculates the Aroon technical indicator for a given equity or forex pair, returning Aroon Up and Aroon Down values to identify trend direction and strength."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryAroonRequest(
            query=_models.GetQueryAroonRequestQuery(function=function, symbol=symbol, interval=interval, time_period=time_period, month=month)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for calculate_aroon_indicator: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__AROON"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("calculate_aroon_indicator")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("calculate_aroon_indicator", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="calculate_aroon_indicator",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Technical Indicators
@mcp.tool()
async def calculate_aroon_oscillator(
    function: Literal["AROONOSC"] = Field(..., description="The technical indicator type. Must be set to AROONOSC for this operation."),
    symbol: str = Field(..., description="The stock ticker symbol to analyze (e.g., IBM, AAPL)."),
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(..., description="The time interval between data points. Choose from: 1min, 5min, 15min, 30min, 60min for intraday data, or daily, weekly, monthly for longer-term analysis."),
    time_period: int = Field(..., description="The number of periods used to calculate the oscillator value. Must be a positive integer (e.g., 10, 25, 60). Larger values smooth the indicator over longer timeframes.", ge=1),
    month: str | None = Field(None, description="Optional historical month for retrieving past indicator values in YYYY-MM format (e.g., 2009-01). If omitted, uses the default data length for the selected interval.", pattern="^\\d{4}-\\d{2}$"),
) -> dict[str, Any]:
    """Calculates the Aroon oscillator (AROONOSC) technical indicator for a given equity symbol. The Aroon oscillator measures the difference between Aroon-Up and Aroon-Down, helping identify trend strength and direction changes."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryAroonoscRequest(
            query=_models.GetQueryAroonoscRequestQuery(function=function, symbol=symbol, interval=interval, time_period=time_period, month=month)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for calculate_aroon_oscillator: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__AROONOSC"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("calculate_aroon_oscillator")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("calculate_aroon_oscillator", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="calculate_aroon_oscillator",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Technical Indicators
@mcp.tool()
async def calculate_money_flow_index(
    function: Literal["MFI"] = Field(..., description="The technical indicator type. Must be set to MFI for this operation."),
    symbol: str = Field(..., description="The stock ticker symbol to analyze (e.g., IBM, AAPL)."),
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(..., description="The time interval between consecutive data points. Choose from: 1min, 5min, 15min, 30min, 60min for intraday data, or daily, weekly, monthly for longer-term analysis."),
    time_period: int = Field(..., description="The number of data points used to calculate each MFI value. Must be a positive integer (e.g., 10, 14, 60). Larger values smooth the indicator over longer periods.", ge=1),
    month: str | None = Field(None, description="Optional historical month to retrieve MFI values for a specific period in the past, specified in YYYY-MM format (e.g., 2009-01). If omitted, uses the default length of the underlying time series data."),
) -> dict[str, Any]:
    """Calculates the Money Flow Index (MFI) technical indicator for a given equity symbol. MFI measures buying and selling pressure by analyzing price and volume data over a specified time period and interval."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryMfiRequest(
            query=_models.GetQueryMfiRequestQuery(function=function, symbol=symbol, interval=interval, time_period=time_period, month=month)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for calculate_money_flow_index: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__MFI"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("calculate_money_flow_index")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("calculate_money_flow_index", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="calculate_money_flow_index",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Technical Indicators
@mcp.tool()
async def calculate_trix(
    function: Literal["TRIX"] = Field(..., description="The technical indicator type. Must be set to TRIX for this operation."),
    symbol: str = Field(..., description="The stock ticker symbol to analyze (e.g., IBM, AAPL)."),
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(..., description="The time interval between consecutive data points. Choose from minute-level intervals (1, 5, 15, 30, 60 minutes) or daily/weekly/monthly aggregations."),
    time_period: int = Field(..., description="The number of data points used to calculate each TRIX value. Must be a positive integer (e.g., 10, 60, 200). Larger values produce smoother results.", ge=1),
    series_type: Literal["close", "open", "high", "low"] = Field(..., description="The price type to use in calculations. Select from closing, opening, high, or low prices for each period."),
    month: str | None = Field(None, description="Optional historical month to retrieve TRIX values for a specific period in the past, specified in YYYY-MM format. If omitted, uses the default length of available time series data."),
) -> dict[str, Any]:
    """Calculates the 1-day rate of change of a triple smooth exponential moving average (TRIX) for a given equity, providing momentum analysis based on the specified time interval and price series."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryTrixRequest(
            query=_models.GetQueryTrixRequestQuery(function=function, symbol=symbol, interval=interval, time_period=time_period, series_type=series_type, month=month)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for calculate_trix: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__TRIX"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("calculate_trix")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("calculate_trix", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="calculate_trix",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Technical Indicators
@mcp.tool()
async def calculate_ultimate_oscillator(
    function: Literal["ULTOSC"] = Field(..., description="The technical indicator function to execute. Must be set to ULTOSC for this operation."),
    symbol: str = Field(..., description="The stock ticker symbol to analyze (e.g., IBM, AAPL)."),
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(..., description="The time interval between data points. Choose from intraday intervals (1, 5, 15, or 30 minutes, or 1 hour) or daily/weekly/monthly historical data."),
    month: str | None = Field(None, description="Optional: Retrieve data for a specific month in history using YYYY-MM format (e.g., 2009-01). If omitted, returns the most recent data."),
    timeperiod1: int | None = Field(None, description="Optional: The first lookback period for the indicator calculation. Must be a positive integer; defaults to 7 if not specified.", ge=1),
    timeperiod2: int | None = Field(None, description="Optional: The second lookback period for the indicator calculation. Must be a positive integer; defaults to 14 if not specified.", ge=1),
    timeperiod3: int | None = Field(None, description="Optional: The third lookback period for the indicator calculation. Must be a positive integer; defaults to 28 if not specified.", ge=1),
) -> dict[str, Any]:
    """Calculates the Ultimate Oscillator (ULTOSC) technical indicator for a given equity symbol and time interval. The Ultimate Oscillator is a momentum indicator that combines multiple timeframes to identify overbought and oversold conditions."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryUltoscRequest(
            query=_models.GetQueryUltoscRequestQuery(function=function, symbol=symbol, interval=interval, month=month, timeperiod1=timeperiod1, timeperiod2=timeperiod2, timeperiod3=timeperiod3)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for calculate_ultimate_oscillator: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__ULTOSC"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("calculate_ultimate_oscillator")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("calculate_ultimate_oscillator", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="calculate_ultimate_oscillator",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Technical Indicators
@mcp.tool()
async def get_directional_index(
    function: Literal["DX"] = Field(..., description="The technical indicator type. Must be set to DX for directional movement index calculations."),
    symbol: str = Field(..., description="The stock ticker symbol to analyze (e.g., IBM, AAPL)."),
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(..., description="The time interval between data points in the series. Choose from minute-level intervals (1, 5, 15, or 30 minutes, or 1 hour) or daily/weekly/monthly aggregations."),
    time_period: int = Field(..., description="The number of data points used to calculate each DX value. Must be a positive integer of at least 1.", ge=1),
    month: str | None = Field(None, description="Optional filter to retrieve DX values for a specific month in historical data. Specify in YYYY-MM format (e.g., 2009-01 for January 2009)."),
) -> dict[str, Any]:
    """Retrieves the Directional Movement Index (DX) technical indicator values for a specified equity symbol, time interval, and calculation period. Optionally returns historical data for a specific month."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryDxRequest(
            query=_models.GetQueryDxRequestQuery(function=function, symbol=symbol, interval=interval, time_period=time_period, month=month)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_directional_index: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__DX"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_directional_index")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_directional_index", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_directional_index",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Technical Indicators
@mcp.tool()
async def get_minus_directional_indicator(
    function: Literal["MINUS_DI"] = Field(..., description="The technical indicator type. Must be set to MINUS_DI for this operation."),
    symbol: str = Field(..., description="The stock ticker symbol (e.g., IBM, AAPL) for which to calculate the indicator."),
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(..., description="The time interval between consecutive data points. Choose from: 1min, 5min, 15min, 30min, 60min for intraday data, or daily, weekly, monthly for longer-term data."),
    time_period: int = Field(..., description="The number of data points used to calculate each MINUS_DI value. Must be a positive integer (e.g., 10, 60, 200).", ge=1),
    month: str | None = Field(None, description="Optional. Retrieve historical indicator values for a specific month in YYYY-MM format (e.g., 2009-01). If omitted, uses the default length of the underlying time series data.", pattern="^\\d{4}-\\d{2}$"),
) -> dict[str, Any]:
    """Retrieves the Minus Directional Indicator (MINUS_DI) values for a given equity symbol, which measures downward price movement strength over a specified time period and interval."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryMinusDiRequest(
            query=_models.GetQueryMinusDiRequestQuery(function=function, symbol=symbol, interval=interval, time_period=time_period, month=month)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_minus_directional_indicator: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__MINUS_DI"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_minus_directional_indicator")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_minus_directional_indicator", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_minus_directional_indicator",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Technical Indicators
@mcp.tool()
async def get_plus_directional_indicator(
    function: Literal["PLUS_DI"] = Field(..., description="The technical indicator type. Must be set to PLUS_DI for this operation."),
    symbol: str = Field(..., description="The stock ticker symbol to analyze (e.g., IBM)."),
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(..., description="The time interval between consecutive data points. Choose from 1-minute, 5-minute, 15-minute, 30-minute, 60-minute, daily, weekly, or monthly intervals."),
    time_period: int = Field(..., description="The number of data points used to calculate each PLUS_DI value. Must be a positive integer (e.g., 60).", ge=1),
    month: str | None = Field(None, description="Optional. Retrieve historical PLUS_DI values for a specific month in YYYY-MM format. If not provided, the calculation uses the default length of the underlying time series data."),
) -> dict[str, Any]:
    """Retrieves Plus Directional Indicator (PLUS_DI) values for a given equity symbol, which measures upward price movement strength over a specified time period and interval."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryPlusDiRequest(
            query=_models.GetQueryPlusDiRequestQuery(function=function, symbol=symbol, interval=interval, time_period=time_period, month=month)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_plus_directional_indicator: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__PLUS_DI"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_plus_directional_indicator")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_plus_directional_indicator", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_plus_directional_indicator",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Technical Indicators
@mcp.tool()
async def get_minus_directional_movement(
    function: Literal["MINUS_DM"] = Field(..., description="The technical indicator type. Must be set to MINUS_DM for this operation."),
    symbol: str = Field(..., description="The stock ticker symbol (e.g., IBM, AAPL) for which to calculate the indicator."),
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(..., description="The time interval between data points: 1min, 5min, 15min, 30min, 60min for intraday data, or daily, weekly, monthly for longer-term analysis."),
    time_period: int = Field(..., description="The number of periods used in the MINUS_DM calculation. Must be a positive integer (e.g., 10, 14, 60). Larger values smooth the indicator over longer timeframes.", ge=1),
    month: str | None = Field(None, description="Optional historical month for the calculation in YYYY-MM format (e.g., 2009-01). If omitted, uses the default data length for the selected interval.", pattern="^\\d{4}-\\d{2}$"),
) -> dict[str, Any]:
    """Retrieves minus directional movement (MINUS_DM) technical indicator values for a specified equity, measuring downward price movement over a configurable time period and interval."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryMinusDmRequest(
            query=_models.GetQueryMinusDmRequestQuery(function=function, symbol=symbol, interval=interval, time_period=time_period, month=month)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_minus_directional_movement: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__MINUS_DM"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_minus_directional_movement")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_minus_directional_movement", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_minus_directional_movement",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Technical Indicators
@mcp.tool()
async def get_plus_directional_movement(
    function: Literal["PLUS_DM"] = Field(..., description="The technical indicator type. Must be set to PLUS_DM for this operation."),
    symbol: str = Field(..., description="The stock ticker symbol (e.g., IBM, AAPL). Case-insensitive."),
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(..., description="The time interval between consecutive data points. Choose from minute-level intervals (1, 5, 15, 30, 60 minutes) or daily/weekly/monthly aggregations."),
    time_period: int = Field(..., description="The number of data points used to calculate each PLUS_DM value. Must be a positive integer of at least 1.", ge=1),
    month: str | None = Field(None, description="Optional historical month for retrieving technical indicators from a specific period. Specify in YYYY-MM format (e.g., 2009-01). If omitted, uses the default length of the underlying time series data.", pattern="^\\d{4}-\\d{2}$"),
) -> dict[str, Any]:
    """Retrieves Plus Directional Movement (PLUS_DM) values for a given equity symbol. PLUS_DM is a technical indicator that measures upward price movement over a specified time period."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryPlusDmRequest(
            query=_models.GetQueryPlusDmRequestQuery(function=function, symbol=symbol, interval=interval, time_period=time_period, month=month)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_plus_directional_movement: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__PLUS_DM"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_plus_directional_movement")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_plus_directional_movement", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_plus_directional_movement",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Technical Indicators
@mcp.tool()
async def calculate_bollinger_bands(
    function: Literal["BBANDS"] = Field(..., description="The technical indicator function to execute. Must be set to BBANDS for Bollinger Bands calculation."),
    symbol: str = Field(..., description="The ticker symbol of the equity or forex pair to analyze (e.g., IBM, AAPL, EUR/USD)."),
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(..., description="The time interval between consecutive data points in the time series. Choose from intraday intervals (1, 5, 15, or 30 minutes, or 1 hour) or daily/weekly/monthly historical data."),
    time_period: int = Field(..., description="The number of data points used to calculate each Bollinger Band value. Must be at least 1; typical values range from 20 to 200 depending on your analysis timeframe.", ge=1),
    series_type: Literal["close", "open", "high", "low"] = Field(..., description="The price type to use for calculations: closing price, opening price, high price, or low price of each interval."),
    month: str | None = Field(None, description="Optional historical month to retrieve data for, specified in YYYY-MM format. If not provided, returns the most recent data available."),
    nbdevup: int | None = Field(None, description="The standard deviation multiplier for the upper Bollinger Band. Must be at least 1; defaults to 2 for typical two standard deviation bands.", ge=1),
    nbdevdn: int | None = Field(None, description="The standard deviation multiplier for the lower Bollinger Band. Must be at least 1; defaults to 2 for typical two standard deviation bands.", ge=1),
) -> dict[str, Any]:
    """Calculates Bollinger Bands technical indicator values for a given equity or forex pair, providing upper, middle, and lower bands based on standard deviation multipliers applied to a moving average."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryBbandsRequest(
            query=_models.GetQueryBbandsRequestQuery(function=function, symbol=symbol, interval=interval, time_period=time_period, series_type=series_type, month=month, nbdevup=nbdevup, nbdevdn=nbdevdn)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for calculate_bollinger_bands: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__BBANDS"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("calculate_bollinger_bands")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("calculate_bollinger_bands", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="calculate_bollinger_bands",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Technical Indicators
@mcp.tool()
async def calculate_midpoint(
    function: Literal["MIDPOINT"] = Field(..., description="The technical indicator function to use. Must be set to MIDPOINT for this operation."),
    symbol: str = Field(..., description="The stock ticker symbol (e.g., IBM, AAPL) for which to calculate midpoint values."),
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(..., description="The time interval between consecutive data points. Choose from 1-minute, 5-minute, 15-minute, 30-minute, 60-minute, daily, weekly, or monthly intervals."),
    time_period: int = Field(..., description="The number of data points to use in calculating each midpoint value. Must be a positive integer (e.g., 10, 60, 200).", ge=1),
    series_type: Literal["close", "open", "high", "low"] = Field(..., description="The price type to use in the calculation: closing price, opening price, highest price, or lowest price of each interval."),
    month: str | None = Field(None, description="Optional historical month for which to calculate midpoint values, specified in YYYY-MM format. If not provided, calculations use the default time series data."),
) -> dict[str, Any]:
    """Calculates the midpoint values (average of highest and lowest prices) for an equity over a specified period and time interval."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryMidpointRequest(
            query=_models.GetQueryMidpointRequestQuery(function=function, symbol=symbol, interval=interval, time_period=time_period, series_type=series_type, month=month)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for calculate_midpoint: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__MIDPOINT"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("calculate_midpoint")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("calculate_midpoint", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="calculate_midpoint",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Technical Indicators
@mcp.tool()
async def calculate_midprice(
    function: Literal["MIDPRICE"] = Field(..., description="The technical indicator type. Must be set to MIDPRICE for this operation."),
    symbol: str = Field(..., description="The stock ticker symbol (e.g., IBM, AAPL) for which to calculate the midpoint price."),
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(..., description="The time interval between consecutive data points. Choose from minute-level intervals (1, 5, 15, 30, or 60 minutes) or longer periods (daily, weekly, or monthly)."),
    time_period: int = Field(..., description="The number of data points used to calculate each MIDPRICE value. Must be a positive integer (e.g., 10, 60, 200).", ge=1),
    month: str | None = Field(None, description="Optional historical month for retrieving technical indicators from a specific period in the past. Specify in YYYY-MM format (e.g., 2009-01). If omitted, uses the default time series data for the selected interval.", pattern="^\\d{4}-\\d{2}$"),
) -> dict[str, Any]:
    """Calculates the midpoint price (MIDPRICE) indicator for an equity over a specified period and time interval. MIDPRICE is computed as the average of the highest high and lowest low prices within each interval."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryMidpriceRequest(
            query=_models.GetQueryMidpriceRequestQuery(function=function, symbol=symbol, interval=interval, time_period=time_period, month=month)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for calculate_midprice: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__MIDPRICE"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("calculate_midprice")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("calculate_midprice", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="calculate_midprice",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Technical Indicators
@mcp.tool()
async def get_parabolic_sar(
    function: Literal["SAR"] = Field(..., description="The technical indicator type; must be set to SAR for parabolic SAR calculations."),
    symbol: str = Field(..., description="The stock ticker symbol (e.g., IBM) for which to calculate the parabolic SAR."),
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(..., description="The time interval between consecutive data points: 1-minute, 5-minute, 15-minute, 30-minute, 60-minute, daily, weekly, or monthly."),
    month: str | None = Field(None, description="Optional historical month filter in YYYY-MM format to retrieve SAR values for a specific month."),
    acceleration: float | None = Field(None, description="The acceleration factor used in SAR calculations; defaults to 0.01 and accepts positive decimal values to control how quickly the SAR adjusts to price movements."),
    maximum: float | None = Field(None, description="The maximum acceleration factor cap; defaults to 0.2 and accepts positive decimal values to limit the maximum rate of SAR adjustment."),
) -> dict[str, Any]:
    """Retrieves parabolic SAR (Stop and Reverse) technical indicator values for a given equity at specified time intervals, useful for identifying potential trend reversals and stop-loss levels."""

    # Construct request model with validation
    try:
        _request = _models.GetQuerySarRequest(
            query=_models.GetQuerySarRequestQuery(function=function, symbol=symbol, interval=interval, month=month, acceleration=acceleration, maximum=maximum)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_parabolic_sar: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__SAR"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_parabolic_sar")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_parabolic_sar", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_parabolic_sar",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Technical Indicators
@mcp.tool()
async def get_true_range(
    function: Literal["TRANGE"] = Field(..., description="The technical indicator type. Must be set to TRANGE to calculate true range values."),
    symbol: str = Field(..., description="The stock ticker symbol (e.g., IBM, AAPL). Identifies which equity to retrieve true range data for."),
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(..., description="The time interval between data points. Choose from minute-level intervals (1, 5, 15, or 30 minutes, or 1 hour) or daily/weekly/monthly aggregations."),
    month: str | None = Field(None, description="Optional. Retrieve true range values for a specific month in history using YYYY-MM format (e.g., 2009-01). If omitted, returns data based on the default time series length for the selected interval."),
) -> dict[str, Any]:
    """Retrieves True Range (TRANGE) volatility values for a specified equity symbol at your chosen time interval. Optionally retrieve historical data for a specific month."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryTrangeRequest(
            query=_models.GetQueryTrangeRequestQuery(function=function, symbol=symbol, interval=interval, month=month)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_true_range: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__TRANGE"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_true_range")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_true_range", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_true_range",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Technical Indicators
@mcp.tool()
async def get_atr(
    function: Literal["ATR"] = Field(..., description="The technical indicator type. Must be set to ATR for this operation."),
    symbol: str = Field(..., description="The stock ticker symbol (e.g., IBM, AAPL) for which to retrieve ATR data."),
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(..., description="The time interval between consecutive data points. Choose from minute-level intervals (1, 5, 15, or 30 minutes), hourly (60 minutes), or daily/weekly/monthly aggregations."),
    time_period: int = Field(..., description="The number of periods used to calculate each ATR value. Must be a positive integer (e.g., 14 is a common default for daily charts).", ge=1),
    month: str | None = Field(None, description="Optional filter to retrieve historical ATR data for a specific month in YYYY-MM format (e.g., 2009-01). Omit to get the most recent data."),
) -> dict[str, Any]:
    """Retrieves Average True Range (ATR) technical indicator values for a specified equity, showing volatility measurements over a chosen time interval and period."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryAtrRequest(
            query=_models.GetQueryAtrRequestQuery(function=function, symbol=symbol, interval=interval, time_period=time_period, month=month)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_atr: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__ATR"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_atr")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_atr", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_atr",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Technical Indicators
@mcp.tool()
async def get_natr_values(
    function: Literal["NATR"] = Field(..., description="The technical indicator type. Must be set to NATR for this operation."),
    symbol: str = Field(..., description="The stock ticker symbol to analyze (e.g., IBM, AAPL)."),
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(..., description="The time interval between consecutive data points. Choose from minute-level intervals (1, 5, 15, or 30 minutes, or 1 hour) or daily/weekly/monthly aggregations."),
    time_period: int = Field(..., description="The number of periods used to calculate each NATR value. Must be a positive integer (e.g., 60 for a 60-period moving average).", ge=1),
    month: str | None = Field(None, description="Optional historical month to retrieve data for, specified in YYYY-MM format (e.g., 2009-01 for January 2009). Omit to get the most recent data."),
) -> dict[str, Any]:
    """Retrieves normalized average true range (NATR) technical indicator values for a specified equity symbol. NATR measures volatility as a percentage of the closing price, allowing for normalized comparison across different price levels."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryNatrRequest(
            query=_models.GetQueryNatrRequestQuery(function=function, symbol=symbol, interval=interval, time_period=time_period, month=month)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_natr_values: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__NATR"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_natr_values")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_natr_values", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_natr_values",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Technical Indicators
@mcp.tool()
async def get_chaikin_ad_line(
    function: Literal["AD"] = Field(..., description="The technical indicator type. Must be set to AD for Chaikin A/D line calculations."),
    symbol: str = Field(..., description="The stock ticker symbol (e.g., IBM, AAPL). Identifies which equity to retrieve data for."),
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(..., description="The time interval between data points in the series. Choose from minute-level intervals (1, 5, 15, or 30 minutes, or 1 hour) or daily/weekly/monthly historical data."),
    month: str | None = Field(None, description="Optional filter to retrieve historical data for a specific month. Use YYYY-MM format (e.g., 2009-01). If omitted, returns the most recent data."),
) -> dict[str, Any]:
    """Retrieves Chaikin A/D line (Accumulation/Distribution) values for a given equity, showing the relationship between price and volume to identify buying and selling pressure."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryAdRequest(
            query=_models.GetQueryAdRequestQuery(function=function, symbol=symbol, interval=interval, month=month)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_chaikin_ad_line: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__AD"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_chaikin_ad_line")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_chaikin_ad_line", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_chaikin_ad_line",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Technical Indicators
@mcp.tool()
async def get_adosc_values(
    function: Literal["ADOSC"] = Field(..., description="The technical indicator type; must be set to ADOSC for this operation."),
    symbol: str = Field(..., description="The stock ticker symbol to analyze (e.g., IBM, AAPL)."),
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(..., description="The time interval between data points: 1min, 5min, 15min, 30min, or 60min for intraday data, or daily, weekly, monthly for longer periods."),
    month: str | None = Field(None, description="Optional historical month in YYYY-MM format to retrieve ADOSC values for a specific month. If not provided, uses the default time series data."),
    fastperiod: int | None = Field(None, description="The time period for the fast exponential moving average calculation. Must be a positive integer; defaults to 3 if not specified.", ge=1),
    slowperiod: int | None = Field(None, description="The time period for the slow exponential moving average calculation. Must be a positive integer; defaults to 10 if not specified.", ge=1),
) -> dict[str, Any]:
    """Retrieves Chaikin A/D oscillator (ADOSC) technical indicator values for a specified equity symbol and time interval, with optional historical month selection and EMA period customization."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryAdoscRequest(
            query=_models.GetQueryAdoscRequestQuery(function=function, symbol=symbol, interval=interval, month=month, fastperiod=fastperiod, slowperiod=slowperiod)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_adosc_values: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__ADOSC"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_adosc_values")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_adosc_values", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_adosc_values",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Technical Indicators
@mcp.tool()
async def get_obv(
    function: Literal["OBV"] = Field(..., description="The technical indicator type to calculate. Must be set to OBV (On-Balance Volume)."),
    symbol: str = Field(..., description="The stock ticker symbol for the equity you want to analyze (e.g., IBM, AAPL)."),
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(..., description="The time interval between data points. Choose from: 1min, 5min, 15min, 30min, 60min for intraday data, or daily, weekly, monthly for longer-term analysis."),
    month: str | None = Field(None, description="Optional historical month to retrieve OBV values for a specific period in the past, specified in YYYY-MM format. If omitted, returns data based on the default time series length for the selected interval."),
) -> dict[str, Any]:
    """Retrieves on-balance volume (OBV) technical indicator values for a specified equity, showing cumulative volume trends across your chosen time interval."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryObvRequest(
            query=_models.GetQueryObvRequestQuery(function=function, symbol=symbol, interval=interval, month=month)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_obv: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__OBV"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_obv")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_obv", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_obv",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Technical Indicators
@mcp.tool()
async def get_hilbert_trendline(
    function: Literal["HT_TRENDLINE"] = Field(..., description="The technical indicator type. Must be set to HT_TRENDLINE for this operation."),
    symbol: str = Field(..., description="The stock ticker symbol (e.g., IBM, AAPL) for which to calculate the trendline."),
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(..., description="The time interval between data points. Choose from 1-minute, 5-minute, 15-minute, 30-minute, 60-minute, daily, weekly, or monthly intervals."),
    series_type: Literal["close", "open", "high", "low"] = Field(..., description="The price type to use in calculations. Select from closing price, opening price, high price, or low price for the interval."),
    month: str | None = Field(None, description="Optional historical month to retrieve data for, specified in YYYY-MM format (e.g., 2009-01). If omitted, returns the most recent data."),
) -> dict[str, Any]:
    """Retrieves Hilbert transform instantaneous trendline (HT_TRENDLINE) technical indicator values for a specified equity, helping identify trend direction and potential reversal points."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryHtTrendlineRequest(
            query=_models.GetQueryHtTrendlineRequestQuery(function=function, symbol=symbol, interval=interval, series_type=series_type, month=month)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_hilbert_trendline: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__HT_TRENDLINE"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_hilbert_trendline")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_hilbert_trendline", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_hilbert_trendline",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Technical Indicators
@mcp.tool()
async def get_hilbert_sine_indicator(
    function: Literal["HT_SINE"] = Field(..., description="The technical indicator function to calculate. Must be set to HT_SINE for this operation."),
    symbol: str = Field(..., description="The stock ticker symbol for which to retrieve the indicator (e.g., IBM, AAPL)."),
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(..., description="The time interval between consecutive data points. Choose from 1-minute, 5-minute, 15-minute, 30-minute, 60-minute, daily, weekly, or monthly intervals."),
    series_type: Literal["close", "open", "high", "low"] = Field(..., description="The price type to use in calculations. Select from closing price, opening price, high price, or low price for the interval."),
    month: str | None = Field(None, description="Optional historical month to retrieve data for, specified in YYYY-MM format (e.g., 2009-01 for January 2009). If omitted, returns the most recent data."),
) -> dict[str, Any]:
    """Retrieves Hilbert transform sine wave (HT_SINE) technical indicator values for a given equity symbol, useful for identifying cyclical trends and potential turning points in price movements."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryHtSineRequest(
            query=_models.GetQueryHtSineRequestQuery(function=function, symbol=symbol, interval=interval, series_type=series_type, month=month)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_hilbert_sine_indicator: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__HT_SINE"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_hilbert_sine_indicator")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_hilbert_sine_indicator", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_hilbert_sine_indicator",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Technical Indicators
@mcp.tool()
async def analyze_hilbert_trend_cycle(
    function: Literal["HT_TRENDMODE"] = Field(..., description="The technical indicator function to apply. Must be set to HT_TRENDMODE for Hilbert Transform trend vs cycle analysis."),
    symbol: str = Field(..., description="The stock ticker symbol to analyze (e.g., IBM, AAPL, MSFT)."),
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(..., description="The time interval between data points. Choose from minute-level intervals (1, 5, 15, 30, 60 minutes) or longer periods (daily, weekly, monthly)."),
    series_type: Literal["close", "open", "high", "low"] = Field(..., description="The price type to use in calculations: closing price, opening price, high price, or low price for each interval."),
    month: str | None = Field(None, description="Optional historical month for analysis in YYYY-MM format (e.g., 2009-01). If omitted, uses the default length of available time series data.", pattern="^\\d{4}-\\d{2}$"),
) -> dict[str, Any]:
    """Analyzes price data using the Hilbert Transform to identify whether the market is in a trend or cycle mode, returning mode values for the specified equity and time interval."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryHtTrendmodeRequest(
            query=_models.GetQueryHtTrendmodeRequestQuery(function=function, symbol=symbol, interval=interval, series_type=series_type, month=month)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for analyze_hilbert_trend_cycle: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__HT_TRENDMODE"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("analyze_hilbert_trend_cycle")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("analyze_hilbert_trend_cycle", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="analyze_hilbert_trend_cycle",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Technical Indicators
@mcp.tool()
async def get_dominant_cycle_period(
    function: Literal["HT_DCPERIOD"] = Field(..., description="The technical indicator to calculate. Must be set to HT_DCPERIOD for this operation."),
    symbol: str = Field(..., description="The stock ticker symbol (e.g., IBM, AAPL) for which to calculate the dominant cycle period."),
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(..., description="The time interval between data points. Choose from: 1-minute, 5-minute, 15-minute, 30-minute, 60-minute, daily, weekly, or monthly intervals."),
    series_type: Literal["close", "open", "high", "low"] = Field(..., description="The price type to use in calculations. Select from: close, open, high, or low prices."),
    month: str | None = Field(None, description="Optional historical month for the calculation in YYYY-MM format (e.g., 2009-01). If not specified, the calculation uses the default length of available time series data."),
) -> dict[str, Any]:
    """Calculates the Hilbert transform dominant cycle period (HT_DCPERIOD) for a given equity, identifying the dominant cycle length in the price data at your specified time interval."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryHtDcperiodRequest(
            query=_models.GetQueryHtDcperiodRequestQuery(function=function, symbol=symbol, interval=interval, series_type=series_type, month=month)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_dominant_cycle_period: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__HT_DCPERIOD"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_dominant_cycle_period")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_dominant_cycle_period", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_dominant_cycle_period",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Technical Indicators
@mcp.tool()
async def get_dominant_cycle_phase(
    function: Literal["HT_DCPHASE"] = Field(..., description="The technical indicator function to calculate. Must be set to HT_DCPHASE for this operation."),
    symbol: str = Field(..., description="The stock ticker symbol to analyze (e.g., IBM, AAPL)."),
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(..., description="The time interval between data points. Choose from minute-level intervals (1, 5, 15, or 30 minutes, or 60 minutes) or daily/weekly/monthly historical data."),
    series_type: Literal["close", "open", "high", "low"] = Field(..., description="The price type to use in calculations. Select from open, high, low, or close prices."),
    month: str | None = Field(None, description="Optional historical month to retrieve data for, specified in YYYY-MM format (e.g., 2009-01 for January 2009)."),
) -> dict[str, Any]:
    """Retrieves the Hilbert transform dominant cycle phase indicator for a given equity symbol, helping identify the current phase position within the dominant market cycle."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryHtDcphaseRequest(
            query=_models.GetQueryHtDcphaseRequestQuery(function=function, symbol=symbol, interval=interval, series_type=series_type, month=month)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_dominant_cycle_phase: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__HT_DCPHASE"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_dominant_cycle_phase")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_dominant_cycle_phase", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_dominant_cycle_phase",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Technical Indicators
@mcp.tool()
async def get_hilbert_phasor(
    function: Literal["HT_PHASOR"] = Field(..., description="The technical indicator type. Must be set to HT_PHASOR to retrieve Hilbert transform phasor components."),
    symbol: str = Field(..., description="The equity ticker symbol to analyze (e.g., IBM, AAPL). Case-insensitive."),
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(..., description="The time interval between consecutive data points. Choose from: 1-minute, 5-minute, 15-minute, 30-minute, 60-minute, daily, weekly, or monthly intervals."),
    series_type: Literal["close", "open", "high", "low"] = Field(..., description="The price type to use in calculations. Select one of: closing price, opening price, high price, or low price for each period."),
    month: str | None = Field(None, description="Optional historical month for the calculation in YYYY-MM format (e.g., 2009-01). If omitted, uses the default length of the underlying time series data."),
) -> dict[str, Any]:
    """Retrieves Hilbert transform phasor components for a given equity symbol, providing phase and amplitude information derived from the specified price series and time interval."""

    # Construct request model with validation
    try:
        _request = _models.GetQueryHtPhasorRequest(
            query=_models.GetQueryHtPhasorRequestQuery(function=function, symbol=symbol, interval=interval, series_type=series_type, month=month)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_hilbert_phasor: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query__HT_PHASOR"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_hilbert_phasor")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_hilbert_phasor", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_hilbert_phasor",
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
        print("  python alpha_vantage_api_server.py", file=sys.stderr)
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

    parser = argparse.ArgumentParser(description="Alpha Vantage MCP Server")

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
    logger.info("Starting Alpha Vantage MCP Server")
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

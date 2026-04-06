#!/usr/bin/env python3
"""
Close API MCP Server

API Info:
- Contact: Joe Kemp, VP of Engineering (https://calendly.com/joe-close/api-chat)

Generated: 2026-04-06 18:43:55 UTC
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

BASE_URL = os.getenv("BASE_URL", "https://api.close.com/api")
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

def parse_sender(value: str | None = None) -> dict | None:
    """Helper function for parameter transformation"""
    if value is None:
        return None
    try:
        if '<' not in value or '>' not in value:
            raise ValueError('Invalid format')
        name_part = value[:value.index('<')].strip()
        email_part = value[value.index('<')+1:value.index('>')].strip()
        if not email_part or '@' not in email_part:
            raise ValueError('Invalid email')
        return {'sender_name': name_part, 'sender_email': email_part}
    except (ValueError, IndexError) as e:
        raise ValueError(f'Failed to parse sender: {value}') from e


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
async def list_leads(limit: int | None = Field(None, alias="_limit", description="Maximum number of leads to return in a single request. Must be at least 1.", ge=1)) -> dict[str, Any]:
    """Retrieve a list of all leads with optional pagination support. Use the limit parameter to control the number of results returned per request."""

    # Construct request model with validation
    try:
        _request = _models.GetV1LeadRequest(
            query=_models.GetV1LeadRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_leads: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/lead/"
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
async def create_lead(name: str | None = Field(None, description="The name of the lead being created.")) -> dict[str, Any]:
    """Create a new lead in the system. Nested contacts, addresses, and custom fields can be included in the request, while activities, tasks, and opportunities should be created separately."""

    # Construct request model with validation
    try:
        _request = _models.PostV1LeadRequest(
            body=_models.PostV1LeadRequestBody(name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_lead: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/lead/"
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
    """Retrieve a lead by ID with basic information, related tasks, opportunities, and custom fields. Note that activities must be fetched separately using a dedicated endpoint."""

    # Construct request model with validation
    try:
        _request = _models.GetV1LeadIdRequest(
            path=_models.GetV1LeadIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_lead: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/lead/{id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/lead/{id}/"
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
    custom_field_id_add: str | None = Field(None, alias="custom_FIELD_ID_add", description="Add a value to a multi-value custom field. Use the field ID in the parameter name to target the specific custom field."),
    custom_field_id_remove: str | None = Field(None, alias="custom_FIELD_ID_remove", description="Remove a value from a multi-value custom field. Use the field ID in the parameter name to target the specific custom field."),
) -> dict[str, Any]:
    """Update an existing lead with support for non-destructive patches. Modify lead status, custom fields, and manage multi-value custom field entries using add/remove modifiers."""

    # Construct request model with validation
    try:
        _request = _models.PutV1LeadIdRequest(
            path=_models.PutV1LeadIdRequestPath(id_=id_),
            body=_models.PutV1LeadIdRequestBody(custom_field_id_add=custom_field_id_add, custom_field_id_remove=custom_field_id_remove)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_lead: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/lead/{id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/lead/{id}/"
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
async def delete_lead(id_: str = Field(..., alias="id", description="The unique identifier of the lead to delete.")) -> dict[str, Any]:
    """Permanently delete a lead from the system by its ID. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteV1LeadIdRequest(
            path=_models.DeleteV1LeadIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_lead: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/lead/{id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/lead/{id}/"
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
    source: str | None = Field(None, description="The ID of the lead to merge from. This lead's data will be consolidated into the destination lead."),
    destination: str | None = Field(None, description="The ID of the lead to merge into. This lead will retain the merged data and become the primary record after the operation completes."),
) -> dict[str, Any]:
    """Merge two leads by consolidating data from a source lead into a destination lead. The source lead's information is transferred to the destination lead, which becomes the primary record."""

    # Construct request model with validation
    try:
        _request = _models.PostV1LeadMergeRequest(
            body=_models.PostV1LeadMergeRequestBody(source=source, destination=destination)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for merge_leads: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/lead/merge/"
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
async def list_contacts(limit: int | None = Field(None, alias="_limit", description="Maximum number of contacts to return in a single request. Defaults to 100 if not specified.")) -> dict[str, Any]:
    """Retrieve a paginated list of all contacts in the system. Use the limit parameter to control the number of results returned per request."""

    # Construct request model with validation
    try:
        _request = _models.GetV1ContactRequest(
            query=_models.GetV1ContactRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_contacts: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/contact"
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
    name: str = Field(..., description="The full name of the contact."),
    emails: list[dict[str, Any]] | None = Field(None, description="A list of email addresses associated with the contact. Order is preserved as provided."),
    phones: list[dict[str, Any]] | None = Field(None, description="A list of phone numbers associated with the contact. Order is preserved as provided."),
    urls: list[dict[str, Any]] | None = Field(None, description="A list of URLs associated with the contact (e.g., website, social profiles). Order is preserved as provided."),
) -> dict[str, Any]:
    """Create a new contact and optionally associate it with an existing lead. If no lead is specified, a new lead will be automatically created using the contact's name."""

    # Construct request model with validation
    try:
        _request = _models.PostV1ContactRequest(
            body=_models.PostV1ContactRequestBody(name=name, emails=emails, phones=phones, urls=urls)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_contact: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/contact"
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
    """Retrieve a specific contact by its unique identifier. Returns the complete contact details including name, email, phone, and other associated information."""

    # Construct request model with validation
    try:
        _request = _models.GetV1ContactIdRequest(
            path=_models.GetV1ContactIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_contact: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/contact/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/contact/{id}"
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
    name: str | None = Field(None, description="The contact's full name or display name."),
    emails: list[dict[str, Any]] | None = Field(None, description="A list of email addresses associated with the contact. Order is preserved as provided."),
    phones: list[dict[str, Any]] | None = Field(None, description="A list of phone numbers associated with the contact. Order is preserved as provided."),
    urls: list[dict[str, Any]] | None = Field(None, description="A list of URLs associated with the contact (e.g., website, social profiles). Order is preserved as provided."),
) -> dict[str, Any]:
    """Update an existing contact's information including name, email addresses, phone numbers, and URLs. Supports adding or removing individual values from multi-value custom fields using .add or .remove suffixes."""

    # Construct request model with validation
    try:
        _request = _models.PutV1ContactIdRequest(
            path=_models.PutV1ContactIdRequestPath(id_=id_),
            body=_models.PutV1ContactIdRequestBody(name=name, emails=emails, phones=phones, urls=urls)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_contact: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/contact/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/contact/{id}"
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
    """Permanently delete a contact from the system by its ID. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteV1ContactIdRequest(
            path=_models.DeleteV1ContactIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_contact: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/contact/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/contact/{id}"
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
    user_id__in: list[str] | None = Field(None, description="Filter results to activities created by specific users. Only applicable when querying activities for a single lead."),
    contact_id__in: list[str] | None = Field(None, description="Filter results to activities associated with specific contacts. Only applicable when querying activities for a single lead."),
    type__in: list[str] | None = Field(None, alias="_type__in", description="Filter results to specific activity types by type ID or name. Supports multiple types including 'Custom' for custom activity types. Only applicable when querying activities for a single lead."),
    activity_at__gt: str | None = Field(None, description="Return only activities that occurred after this date and time (ISO 8601 format). Requires sorting by activity_at in descending order."),
    activity_at__lt: str | None = Field(None, description="Return only activities that occurred before this date and time (ISO 8601 format). Requires sorting by activity_at in descending order."),
    order_by: str | None = Field(None, alias="_order_by", description="Sort results by date_created or activity_at. Prefix with '-' for descending order (e.g., -activity_at for newest first)."),
    limit: int | None = Field(None, alias="_limit", description="Maximum number of results to return per request."),
    thread_emails: Literal["true", "only"] | None = Field(None, description="Controls email object formatting in results. Use 'true' to group emails into threads with condensed email objects, or 'only' to return threads exclusively without individual email objects."),
) -> dict[str, Any]:
    """Retrieve and filter activities across your CRM. Supports filtering by lead, user, contact, activity type, and date ranges, with flexible sorting and email threading options."""

    # Construct request model with validation
    try:
        _request = _models.GetV1ActivityRequest(
            query=_models.GetV1ActivityRequestQuery(user_id__in=user_id__in, contact_id__in=contact_id__in, type__in=type__in, activity_at__gt=activity_at__gt, activity_at__lt=activity_at__lt, order_by=order_by, limit=limit, thread_emails=thread_emails)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_activities: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/activity"
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

# Tags: Activities
@mcp.tool()
async def list_call_activities(limit: int | None = Field(None, alias="_limit", description="Maximum number of call activity records to return in a single response for pagination purposes.")) -> dict[str, Any]:
    """Retrieve a list of all Call activities with optional filtering and pagination support. Use query parameters to narrow results by lead, user, or date range as needed."""

    # Construct request model with validation
    try:
        _request = _models.GetV1ActivityCallRequest(
            query=_models.GetV1ActivityCallRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_call_activities: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/activity/call"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_call_activities")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_call_activities", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_call_activities",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Activities
@mcp.tool()
async def log_call_activity(
    direction: Literal["outbound", "inbound"] | None = Field(None, description="Specifies whether the call was inbound or outbound. If not provided, the direction will not be recorded."),
    recording_url: str | None = Field(None, description="HTTPS URL pointing to an MP3 recording of the call. Must use HTTPS protocol for security purposes."),
) -> dict[str, Any]:
    """Manually log a call activity for calls made outside the Close VoIP system. The activity status defaults to completed upon creation."""

    # Construct request model with validation
    try:
        _request = _models.PostV1ActivityCallRequest(
            body=_models.PostV1ActivityCallRequestBody(direction=direction, recording_url=recording_url)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for log_call_activity: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/activity/call"
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

# Tags: Activities
@mcp.tool()
async def get_call_activity(id_: str = Field(..., alias="id", description="The unique identifier of the Call activity record to retrieve.")) -> dict[str, Any]:
    """Retrieve a single Call activity record by its unique identifier. Use this to fetch detailed information about a specific call interaction."""

    # Construct request model with validation
    try:
        _request = _models.GetV1ActivityCallIdRequest(
            path=_models.GetV1ActivityCallIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_call_activity: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/activity/call/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/activity/call/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_call_activity")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_call_activity", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_call_activity",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Activities
@mcp.tool()
async def update_call_activity(
    id_: str = Field(..., alias="id", description="The unique identifier of the Call activity to update."),
    outcome_id: str | None = Field(None, description="The user-defined outcome ID to assign to this call activity, indicating how the call concluded."),
) -> dict[str, Any]:
    """Update a Call activity record, such as adding notes or changing the outcome. Note that certain fields like status, duration, and direction cannot be modified for calls made through Close's VoIP system."""

    # Construct request model with validation
    try:
        _request = _models.PutV1ActivityCallIdRequest(
            path=_models.PutV1ActivityCallIdRequestPath(id_=id_),
            body=_models.PutV1ActivityCallIdRequestBody(outcome_id=outcome_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_call_activity: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/activity/call/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/activity/call/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_call_activity")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_call_activity", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_call_activity",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Activities
@mcp.tool()
async def delete_call_activity(id_: str = Field(..., alias="id", description="The unique identifier of the Call activity to delete.")) -> dict[str, Any]:
    """Permanently delete a Call activity record by its ID. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteV1ActivityCallIdRequest(
            path=_models.DeleteV1ActivityCallIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_call_activity: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/activity/call/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/activity/call/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_call_activity")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_call_activity", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_call_activity",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Activities
@mcp.tool()
async def list_created_activities(limit: int | None = Field(None, alias="_limit", description="Maximum number of results to return in the response. Defaults to 100 if not specified.")) -> dict[str, Any]:
    """Retrieve a list of all Created activities, which represent the time and method by which leads were initially created in the system. Results can be limited to control response size."""

    # Construct request model with validation
    try:
        _request = _models.GetV1ActivityCreatedRequest(
            query=_models.GetV1ActivityCreatedRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_created_activities: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/activity/created"
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

# Tags: Activities
@mcp.tool()
async def get_activity_created(id_: str = Field(..., alias="id", description="The unique identifier of the Created activity record to retrieve.")) -> dict[str, Any]:
    """Retrieve a single Created activity by ID. Created activities record when and how a lead was initially created in the system."""

    # Construct request model with validation
    try:
        _request = _models.GetV1ActivityCreatedIdRequest(
            path=_models.GetV1ActivityCreatedIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_activity_created: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/activity/created/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/activity/created/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_activity_created")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_activity_created", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_activity_created",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Activities
@mcp.tool()
async def list_email_activities(limit: int | None = Field(None, alias="_limit", description="Maximum number of email activities to return in the response. Must be at least 1.", ge=1)) -> dict[str, Any]:
    """Retrieve a list of email activities, with one object returned per email message. Use the limit parameter to control the number of results returned."""

    # Construct request model with validation
    try:
        _request = _models.GetV1ActivityEmailRequest(
            query=_models.GetV1ActivityEmailRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_email_activities: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/activity/email"
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

# Tags: Activities
@mcp.tool()
async def create_email_activity(
    status: Literal["inbox", "draft", "scheduled", "outbox", "sent", "error"] = Field(..., description="The current state of the email. Must be one of: inbox (received), draft (unsent), scheduled (queued for future send), outbox (pending send), sent (successfully delivered), or error (failed to send)."),
    followup_date: str | None = Field(None, description="Optional ISO 8601 date-time for when a follow-up task should be created if no response is received by that time."),
    template_id: str | None = Field(None, description="Optional ID of a pre-defined email template to render on the server side, which will populate the email content."),
    sender: str | None = Field(None, description="Optional sender email address. Can be a plain email address or formatted as 'Display Name' <email@example.com>."),
    attachments: list[_models.PostV1ActivityEmailBodyAttachmentsItem] | None = Field(None, description="Optional array of attachment objects to include with the email. Order is preserved as provided."),
) -> dict[str, Any]:
    """Create a new email activity with a specified status. Use this to log incoming emails, draft new messages, schedule sends, or record sent/outbox items."""

    # Construct request model with validation
    try:
        _request = _models.PostV1ActivityEmailRequest(
            body=_models.PostV1ActivityEmailRequestBody(status=status, followup_date=followup_date, template_id=template_id, sender=sender, attachments=attachments)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_email_activity: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/activity/email"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_email_activity")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_email_activity", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_email_activity",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Activities
@mcp.tool()
async def get_email_activity(id_: str = Field(..., alias="id", description="The unique identifier of the email activity record to retrieve.")) -> dict[str, Any]:
    """Retrieve a single email activity record by its unique identifier. Use this to fetch detailed information about a specific email interaction."""

    # Construct request model with validation
    try:
        _request = _models.GetV1ActivityEmailIdRequest(
            path=_models.GetV1ActivityEmailIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_email_activity: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/activity/email/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/activity/email/{id}"
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

# Tags: Activities
@mcp.tool()
async def update_email_activity(
    id_: str = Field(..., alias="id", description="The unique identifier of the email activity to update."),
    sender: str | None = Field(None, description="The sender's email address, optionally formatted as a display name with the email address (e.g., \"Name\" <email@example.com>). Required when changing the activity status to scheduled or outbox if not previously set."),
    followup_date: str | None = Field(None, description="The date and time for an associated follow-up task, specified in ISO 8601 format."),
) -> dict[str, Any]:
    """Update an email activity to modify draft content or change its status. Use this operation to transition emails between draft, scheduled, and outbox states, or to adjust follow-up timing."""

    # Construct request model with validation
    try:
        _request = _models.PutV1ActivityEmailIdRequest(
            path=_models.PutV1ActivityEmailIdRequestPath(id_=id_),
            body=_models.PutV1ActivityEmailIdRequestBody(sender=sender, followup_date=followup_date)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_email_activity: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/activity/email/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/activity/email/{id}"
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

# Tags: Activities
@mcp.tool()
async def delete_email_activity(id_: str = Field(..., alias="id", description="The unique identifier of the email activity to delete.")) -> dict[str, Any]:
    """Permanently delete an email activity record by its ID. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteV1ActivityEmailIdRequest(
            path=_models.DeleteV1ActivityEmailIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_email_activity: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/activity/email/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/activity/email/{id}"
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

# Tags: Activities
@mcp.tool()
async def list_email_threads(limit: int | None = Field(None, alias="_limit", description="Maximum number of email threads to return in the response; omit to retrieve all available results.")) -> dict[str, Any]:
    """Retrieve a list of email thread activities, with each result representing one email conversation typically grouped by subject line."""

    # Construct request model with validation
    try:
        _request = _models.GetV1ActivityEmailthreadRequest(
            query=_models.GetV1ActivityEmailthreadRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_email_threads: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/activity/emailthread"
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

# Tags: Activities
@mcp.tool()
async def get_email_thread(id_: str = Field(..., alias="id", description="The unique identifier of the email thread activity to retrieve.")) -> dict[str, Any]:
    """Retrieve a specific email thread activity by its unique identifier. Use this to fetch details about a single email thread conversation."""

    # Construct request model with validation
    try:
        _request = _models.GetV1ActivityEmailthreadIdRequest(
            path=_models.GetV1ActivityEmailthreadIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_email_thread: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/activity/emailthread/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/activity/emailthread/{id}"
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

# Tags: Activities
@mcp.tool()
async def delete_email_thread(id_: str = Field(..., alias="id", description="The unique identifier of the email thread activity to delete.")) -> dict[str, Any]:
    """Delete an email thread activity and all associated email activities within that thread. This is a permanent operation that removes the entire thread conversation."""

    # Construct request model with validation
    try:
        _request = _models.DeleteV1ActivityEmailthreadIdRequest(
            path=_models.DeleteV1ActivityEmailthreadIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_email_thread: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/activity/emailthread/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/activity/emailthread/{id}"
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

# Tags: Activities
@mcp.tool()
async def list_lead_status_changes(limit: int | None = Field(None, alias="_limit", description="Maximum number of results to return. Must be at least 1.", ge=1)) -> dict[str, Any]:
    """Retrieve a list of all lead status change activities, with optional filtering by result limit. Use this to track when and how lead statuses have been modified."""

    # Construct request model with validation
    try:
        _request = _models.GetV1ActivityStatusChangeLeadRequest(
            query=_models.GetV1ActivityStatusChangeLeadRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_lead_status_changes: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/activity/status_change/lead"
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

# Tags: Activities
@mcp.tool()
async def log_lead_status_change(
    lead_id: str = Field(..., description="The unique identifier of the lead for which to log the status change."),
    old_status_id: str | None = Field(None, description="The unique identifier of the status the lead was transitioning from. Optional if only recording the new status."),
    new_status_id: str | None = Field(None, description="The unique identifier of the status the lead was transitioning to. Optional if only recording the previous status."),
) -> dict[str, Any]:
    """Log a historical lead status change event in the activity feed without modifying the lead's current status. Use this operation to import status change records from another system or organization."""

    # Construct request model with validation
    try:
        _request = _models.PostV1ActivityStatusChangeLeadRequest(
            body=_models.PostV1ActivityStatusChangeLeadRequestBody(lead_id=lead_id, old_status_id=old_status_id, new_status_id=new_status_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for log_lead_status_change: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/activity/status_change/lead"
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

# Tags: Activities
@mcp.tool()
async def get_lead_status_change(id_: str = Field(..., alias="id", description="The unique identifier of the lead status change activity record to retrieve.")) -> dict[str, Any]:
    """Retrieve a specific lead status change activity record by its ID. Use this to view details about when and how a lead's status was modified."""

    # Construct request model with validation
    try:
        _request = _models.GetV1ActivityStatusChangeLeadIdRequest(
            path=_models.GetV1ActivityStatusChangeLeadIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_lead_status_change: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/activity/status_change/lead/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/activity/status_change/lead/{id}"
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

# Tags: Activities
@mcp.tool()
async def delete_lead_status_change(id_: str = Field(..., alias="id", description="The unique identifier of the LeadStatusChange activity to delete.")) -> dict[str, Any]:
    """Remove a LeadStatusChange activity from a lead's activity feed. This deletion only removes the status change event record and does not alter the lead's current status; use this when a status change event is irrelevant or causing integration issues with external systems."""

    # Construct request model with validation
    try:
        _request = _models.DeleteV1ActivityStatusChangeLeadIdRequest(
            path=_models.DeleteV1ActivityStatusChangeLeadIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_lead_status_change: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/activity/status_change/lead/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/activity/status_change/lead/{id}"
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
async def search_meeting_by_calendar_event(
    provider_calendar_event_id: str = Field(..., description="The unique identifier of the calendar event from the provider (Google, Microsoft, etc.) that the meeting was synced from. This is the primary search criterion."),
    provider_calendar_id: str | None = Field(None, description="The unique identifier of the calendar from the provider where the event originated. Use this to narrow results to a specific calendar."),
    provider_calendar_type: Literal["google", "microsoft"] | None = Field(None, description="The calendar provider type. Specify either 'google' for Google Calendar or 'microsoft' for Microsoft Outlook/Exchange."),
    starts_at: str | None = Field(None, description="The meeting start time in ISO 8601 format. Useful for distinguishing meetings created from different instances of recurring calendar events."),
) -> dict[str, Any]:
    """Search for meetings by their synced calendar event information. Use the provider calendar event ID along with optional filters like calendar ID, provider type, or start time to locate specific meetings."""

    # Construct request model with validation
    try:
        _request = _models.GetV1ActivityMeetingRequest(
            query=_models.GetV1ActivityMeetingRequestQuery(provider_calendar_event_id=provider_calendar_event_id, provider_calendar_id=provider_calendar_id, provider_calendar_type=provider_calendar_type, starts_at=starts_at)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_meeting_by_calendar_event: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/activity/meeting"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_meeting_by_calendar_event")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_meeting_by_calendar_event", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_meeting_by_calendar_event",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Activities
@mcp.tool()
async def get_meeting(id_: str = Field(..., alias="id", description="The unique identifier of the Meeting activity to retrieve.")) -> dict[str, Any]:
    """Retrieve a specific Meeting activity by its unique identifier. Use this to fetch details about a scheduled or completed meeting."""

    # Construct request model with validation
    try:
        _request = _models.GetV1ActivityMeetingIdRequest(
            path=_models.GetV1ActivityMeetingIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_meeting: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/activity/meeting/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/activity/meeting/{id}"
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

# Tags: Activities
@mcp.tool()
async def update_meeting(
    id_: str = Field(..., alias="id", description="The unique identifier of the Meeting activity to update."),
    user_note_html: str | None = Field(None, description="Rich text HTML content for meeting notes. Allows formatted text documentation of meeting details and discussion points."),
    outcome_id: str | None = Field(None, description="Custom outcome identifier to associate with the meeting, used for tracking meeting results or classifications."),
) -> dict[str, Any]:
    """Update a Meeting activity by modifying notes or outcome. Commonly used to record meeting notes in rich text format or assign a custom outcome to the meeting."""

    # Construct request model with validation
    try:
        _request = _models.PutV1ActivityMeetingIdRequest(
            path=_models.PutV1ActivityMeetingIdRequestPath(id_=id_),
            body=_models.PutV1ActivityMeetingIdRequestBody(user_note_html=user_note_html, outcome_id=outcome_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_meeting: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/activity/meeting/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/activity/meeting/{id}"
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

# Tags: Activities
@mcp.tool()
async def delete_meeting(id_: str = Field(..., alias="id", description="The unique identifier of the Meeting activity to delete.")) -> dict[str, Any]:
    """Permanently delete a specific Meeting activity by its ID. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteV1ActivityMeetingIdRequest(
            path=_models.DeleteV1ActivityMeetingIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_meeting: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/activity/meeting/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/activity/meeting/{id}"
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

# Tags: Activities
@mcp.tool()
async def create_or_update_meeting_integration(
    id_: str = Field(..., alias="id", description="The unique identifier of the meeting activity to integrate with a third-party service."),
    body: dict[str, Any] = Field(..., description="Integration configuration object. Submitting an empty object will not perform any action. The structure depends on the third-party service being integrated."),
) -> dict[str, Any]:
    """Create a new third-party meeting integration or update an existing one for a specific meeting activity. This operation is only available to OAuth applications; API key authentication will result in an error."""

    # Construct request model with validation
    try:
        _request = _models.PostV1ActivityMeetingIdIntegrationRequest(
            path=_models.PostV1ActivityMeetingIdIntegrationRequestPath(id_=id_),
            body=_models.PostV1ActivityMeetingIdIntegrationRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_or_update_meeting_integration: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/activity/meeting/{id}/integration", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/activity/meeting/{id}/integration"
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

# Tags: Activities
@mcp.tool()
async def list_activity_notes(limit: int | None = Field(None, alias="_limit", description="Maximum number of results to return per request. Must be at least 1.", ge=1)) -> dict[str, Any]:
    """Retrieve a list of Note activities with optional pagination. Use this to view all notes or filter results by applying additional query parameters."""

    # Construct request model with validation
    try:
        _request = _models.GetV1ActivityNoteRequest(
            query=_models.GetV1ActivityNoteRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_activity_notes: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/activity/note"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_activity_notes")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_activity_notes", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_activity_notes",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Activities
@mcp.tool()
async def create_note(
    attachments: list[_models.PostV1ActivityNoteBodyAttachmentsItem] | None = Field(None, description="Array of attachments to include with the note. Each attachment object should contain a URL from the Files API, filename, and content type. Attachments are displayed in the order provided."),
    pinned: bool | None = Field(None, description="Set to true to pin this note, making it appear at the top of the activity feed for easy reference."),
) -> dict[str, Any]:
    """Create a new Note activity with optional rich-text content, attachments, and pinning. Rich HTML content takes precedence over plain text if both are provided."""

    # Construct request model with validation
    try:
        _request = _models.PostV1ActivityNoteRequest(
            body=_models.PostV1ActivityNoteRequestBody(attachments=attachments, pinned=pinned)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_note: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/activity/note"
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

# Tags: Activities
@mcp.tool()
async def get_activity_note(id_: str = Field(..., alias="id", description="The unique identifier of the Note activity to retrieve.")) -> dict[str, Any]:
    """Retrieve a single Note activity by its unique identifier. Use this to fetch detailed information about a specific note entry."""

    # Construct request model with validation
    try:
        _request = _models.GetV1ActivityNoteIdRequest(
            path=_models.GetV1ActivityNoteIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_activity_note: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/activity/note/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/activity/note/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_activity_note")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_activity_note", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_activity_note",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Activities
@mcp.tool()
async def update_note(
    id_: str = Field(..., alias="id", description="The unique identifier of the note activity to update."),
    attachments: list[dict[str, Any]] | None = Field(None, description="List of attachment objects to associate with the note. Attachments are processed in the order provided."),
    pinned: bool | None = Field(None, description="Set to true to pin the note for visibility, or false to unpin it."),
) -> dict[str, Any]:
    """Update an existing note activity, including its content, attachments, and pin status. You can modify the note text, add or remove attachments, and pin or unpin the note."""

    # Construct request model with validation
    try:
        _request = _models.PutV1ActivityNoteIdRequest(
            path=_models.PutV1ActivityNoteIdRequestPath(id_=id_),
            body=_models.PutV1ActivityNoteIdRequestBody(attachments=attachments, pinned=pinned)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_note: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/activity/note/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/activity/note/{id}"
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

# Tags: Activities
@mcp.tool()
async def delete_activity_note(id_: str = Field(..., alias="id", description="The unique identifier of the Note activity to delete.")) -> dict[str, Any]:
    """Permanently delete a Note activity by its ID. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteV1ActivityNoteIdRequest(
            path=_models.DeleteV1ActivityNoteIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_activity_note: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/activity/note/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/activity/note/{id}"
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

# Tags: Activities
@mcp.tool()
async def list_opportunity_status_changes(
    opportunity_id: str | None = Field(None, description="Filter results to show status changes for a specific opportunity by its ID."),
    limit: int | None = Field(None, alias="_limit", description="Limit the number of status change records returned in the response."),
) -> dict[str, Any]:
    """Retrieve a list of opportunity status change activities with optional filtering by opportunity ID and result limits."""

    # Construct request model with validation
    try:
        _request = _models.GetV1ActivityStatusChangeOpportunityRequest(
            query=_models.GetV1ActivityStatusChangeOpportunityRequestQuery(opportunity_id=opportunity_id, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_opportunity_status_changes: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/activity/status_change/opportunity"
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

# Tags: Activities
@mcp.tool()
async def log_opportunity_status_change(body: dict[str, Any] = Field(..., description="The status change event details including the opportunity identifier, previous status, new status, and any additional context about the change.")) -> dict[str, Any]:
    """Log a historical opportunity status change event in the activity feed. This operation records a status change event without modifying the actual opportunity status, and is intended for importing historical status changes from external systems or organizations."""

    # Construct request model with validation
    try:
        _request = _models.PostV1ActivityStatusChangeOpportunityRequest(
            body=_models.PostV1ActivityStatusChangeOpportunityRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for log_opportunity_status_change: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/activity/status_change/opportunity"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
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

# Tags: Activities
@mcp.tool()
async def get_opportunity_status_change(id_: str = Field(..., alias="id", description="The unique identifier of the opportunity status change activity record to retrieve.")) -> dict[str, Any]:
    """Retrieve a single opportunity status change activity by its ID. Use this to fetch details about when and how an opportunity's status was modified."""

    # Construct request model with validation
    try:
        _request = _models.GetV1ActivityStatusChangeOpportunityIdRequest(
            path=_models.GetV1ActivityStatusChangeOpportunityIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_opportunity_status_change: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/activity/status_change/opportunity/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/activity/status_change/opportunity/{id}"
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

# Tags: Activities
@mcp.tool()
async def delete_opportunity_status_change(id_: str = Field(..., alias="id", description="The unique identifier of the OpportunityStatusChange activity to delete.")) -> dict[str, Any]:
    """Remove an OpportunityStatusChange activity from the activity feed. This deletion only removes the status change event record and does not affect the actual opportunity status; use this only when the status change event is irrelevant or causing integration issues with external systems."""

    # Construct request model with validation
    try:
        _request = _models.DeleteV1ActivityStatusChangeOpportunityIdRequest(
            path=_models.DeleteV1ActivityStatusChangeOpportunityIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_opportunity_status_change: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/activity/status_change/opportunity/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/activity/status_change/opportunity/{id}"
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

# Tags: Activities
@mcp.tool()
async def list_sms_activities(limit: int | None = Field(None, alias="_limit", description="Maximum number of SMS activity records to return in the response. Limits the result set size for pagination or performance optimization.")) -> dict[str, Any]:
    """Retrieve a list of SMS activities with optional filtering. Includes MMS messages (SMS with attachments) where attachments contain URLs, filenames, sizes, content types, and optional thumbnails accessible via authenticated S3 URLs."""

    # Construct request model with validation
    try:
        _request = _models.GetV1ActivitySmsRequest(
            query=_models.GetV1ActivitySmsRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_sms_activities: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/activity/sms"
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

# Tags: Activities
@mcp.tool()
async def create_sms_activity(
    status: Literal["inbox", "draft", "scheduled", "outbox", "sent"] = Field(..., description="The current status of the SMS activity. Use inbox to log a received SMS, draft to create an editable SMS, scheduled to send at a future date/time, outbox to send immediately, or sent to log an already-sent SMS."),
    send_to_inbox: bool | None = Field(None, description="When creating an SMS with inbox status, set to true to automatically generate a corresponding Inbox Notification for the SMS."),
    local_phone: str | None = Field(None, description="The phone number to send the SMS from. Must be associated with a Phone Number configured as type internal. Required unless using a template_id."),
    template_id: str | None = Field(None, description="The ID of an SMS template to use instead of providing raw text content."),
    direction: Literal["inbound", "outbound"] | None = Field(None, description="The direction of the SMS flow. Defaults to inbound when status is inbox, otherwise defaults to outbound."),
) -> dict[str, Any]:
    """Create an SMS activity with various statuses (inbox, draft, scheduled, outbox, or sent) to log, draft, schedule, or send SMS messages. Only draft SMS activities can be modified after creation."""

    # Construct request model with validation
    try:
        _request = _models.PostV1ActivitySmsRequest(
            query=_models.PostV1ActivitySmsRequestQuery(send_to_inbox=send_to_inbox),
            body=_models.PostV1ActivitySmsRequestBody(status=status, local_phone=local_phone, template_id=template_id, direction=direction)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_sms_activity: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/activity/sms"
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

# Tags: Activities
@mcp.tool()
async def get_sms_activity(id_: str = Field(..., alias="id", description="The unique identifier of the SMS activity record to retrieve.")) -> dict[str, Any]:
    """Retrieve details of a specific SMS activity by its unique identifier. Use this to fetch information about a single SMS message or communication event."""

    # Construct request model with validation
    try:
        _request = _models.GetV1ActivitySmsIdRequest(
            path=_models.GetV1ActivitySmsIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_sms_activity: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/activity/sms/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/activity/sms/{id}"
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

# Tags: Activities
@mcp.tool()
async def update_sms_activity(id_: str = Field(..., alias="id", description="The unique identifier of the SMS activity to update.")) -> dict[str, Any]:
    """Update an SMS activity to modify draft content or change its send status. Use this to send immediately by setting status to outbox, or schedule for later by setting status to scheduled with a date_scheduled value."""

    # Construct request model with validation
    try:
        _request = _models.PutV1ActivitySmsIdRequest(
            path=_models.PutV1ActivitySmsIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_sms_activity: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/activity/sms/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/activity/sms/{id}"
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

# Tags: Activities
@mcp.tool()
async def delete_sms_activity(id_: str = Field(..., alias="id", description="The unique identifier of the SMS activity to delete.")) -> dict[str, Any]:
    """Permanently delete a specific SMS activity record by its ID. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteV1ActivitySmsIdRequest(
            path=_models.DeleteV1ActivitySmsIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_sms_activity: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/activity/sms/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/activity/sms/{id}"
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

# Tags: Activities
@mcp.tool()
async def list_completed_tasks(limit: int | None = Field(None, alias="_limit", description="Maximum number of results to return in the response. Must be at least 1.", ge=1)) -> dict[str, Any]:
    """Retrieve a list of task completion activities. Task completed activities are generated when a task is marked as finished on a lead record."""

    # Construct request model with validation
    try:
        _request = _models.GetV1ActivityTaskCompletedRequest(
            query=_models.GetV1ActivityTaskCompletedRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_completed_tasks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/activity/task_completed/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_completed_tasks")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_completed_tasks", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_completed_tasks",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Activities
@mcp.tool()
async def get_completed_task(id_: str = Field(..., alias="id", description="The unique identifier of the completed task activity to retrieve.")) -> dict[str, Any]:
    """Retrieve details of a specific completed task activity by its unique identifier."""

    # Construct request model with validation
    try:
        _request = _models.GetV1ActivityTaskCompletedIdRequest(
            path=_models.GetV1ActivityTaskCompletedIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_completed_task: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/activity/task_completed/{id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/activity/task_completed/{id}/"
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

# Tags: Activities
@mcp.tool()
async def delete_completed_task(id_: str = Field(..., alias="id", description="The unique identifier of the TaskCompleted activity to delete.")) -> dict[str, Any]:
    """Remove a completed task activity from the system. This permanently deletes the TaskCompleted activity record identified by the provided ID."""

    # Construct request model with validation
    try:
        _request = _models.DeleteV1ActivityTaskCompletedIdRequest(
            path=_models.DeleteV1ActivityTaskCompletedIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_completed_task: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/activity/task_completed/{id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/activity/task_completed/{id}/"
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

# Tags: Activities
@mcp.tool()
async def list_lead_merges(limit: int | None = Field(None, alias="_limit", description="Maximum number of LeadMerge activities to return in the response. Useful for pagination or controlling result set size.")) -> dict[str, Any]:
    """Retrieve a list of LeadMerge activities, which are automatically created when one lead is merged into another. Use optional filtering to limit the number of results returned."""

    # Construct request model with validation
    try:
        _request = _models.GetV1ActivityLeadMergeRequest(
            query=_models.GetV1ActivityLeadMergeRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_lead_merges: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/activity/lead_merge/"
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

# Tags: Activities
@mcp.tool()
async def get_lead_merge(id_: str = Field(..., alias="id", description="The unique identifier of the LeadMerge activity record to retrieve.")) -> dict[str, Any]:
    """Retrieve a specific LeadMerge activity record by its unique identifier. Use this to fetch details about a lead merge operation."""

    # Construct request model with validation
    try:
        _request = _models.GetV1ActivityLeadMergeIdRequest(
            path=_models.GetV1ActivityLeadMergeIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_lead_merge: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/activity/lead_merge/{id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/activity/lead_merge/{id}/"
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

# Tags: Activities
@mcp.tool()
async def list_whatsapp_messages(external_whatsapp_message_id: str | None = Field(None, description="Filter results to a specific WhatsApp message by its external message ID. Useful for locating a particular message in Close that corresponds to a WhatsApp message ID.")) -> dict[str, Any]:
    """Retrieve WhatsApp message activities from Close, with optional filtering by external WhatsApp message ID. Use this to sync message data between WhatsApp and Close, or to locate specific messages for updates or deletion."""

    # Construct request model with validation
    try:
        _request = _models.GetV1ActivityWhatsappMessageRequest(
            query=_models.GetV1ActivityWhatsappMessageRequestQuery(external_whatsapp_message_id=external_whatsapp_message_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_whatsapp_messages: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/activity/whatsapp_message"
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

# Tags: Activities
@mcp.tool()
async def create_whatsapp_message(
    external_whatsapp_message_id: str = Field(..., description="The unique identifier of the message as assigned by WhatsApp. This is required to link the activity to the original message."),
    message_markdown: str = Field(..., description="The message content formatted using WhatsApp Markdown syntax. This is the body text that will be displayed in the activity."),
    send_to_inbox: bool | None = Field(None, description="When the message direction is set to 'incoming', set this to true to automatically create a corresponding Inbox Notification for the message."),
    attachments: list[_models.PostV1ActivityWhatsappMessageBodyAttachmentsItem] | None = Field(None, description="An optional array of file attachments previously uploaded via the Files API. Each attachment should include its URL, filename, and content type. The combined size of all attachments cannot exceed 25MB."),
    integration_link: str | None = Field(None, description="An optional URL provided by the integration partner that links back to this message in the external WhatsApp system, enabling cross-system navigation."),
    response_to_id: str | None = Field(None, description="The Close activity ID of another WhatsApp message activity that this message is replying to, establishing a conversation thread."),
) -> dict[str, Any]:
    """Create a new WhatsApp message activity in Close. The message must reference a valid WhatsApp message ID and include the message body in WhatsApp Markdown format. Any attachments must be pre-uploaded via the Files API and cannot exceed 25MB in total size."""

    # Construct request model with validation
    try:
        _request = _models.PostV1ActivityWhatsappMessageRequest(
            query=_models.PostV1ActivityWhatsappMessageRequestQuery(send_to_inbox=send_to_inbox),
            body=_models.PostV1ActivityWhatsappMessageRequestBody(external_whatsapp_message_id=external_whatsapp_message_id, message_markdown=message_markdown, attachments=attachments, integration_link=integration_link, response_to_id=response_to_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_whatsapp_message: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/activity/whatsapp_message"
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

# Tags: Activities
@mcp.tool()
async def get_whatsapp_message(id_: str = Field(..., alias="id", description="The unique identifier of the WhatsApp message activity to retrieve.")) -> dict[str, Any]:
    """Retrieve a specific WhatsApp message activity by its unique identifier. Use this to fetch details about a single WhatsApp message interaction."""

    # Construct request model with validation
    try:
        _request = _models.GetV1ActivityWhatsappMessageIdRequest(
            path=_models.GetV1ActivityWhatsappMessageIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_whatsapp_message: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/activity/whatsapp_message/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/activity/whatsapp_message/{id}"
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

# Tags: Activities
@mcp.tool()
async def update_whatsapp_message(
    id_: str = Field(..., alias="id", description="The unique identifier of the WhatsApp message activity to update."),
    message_markdown: str | None = Field(None, description="The message body formatted using WhatsApp Markdown syntax for text styling and formatting."),
    attachments: list[dict[str, Any]] | None = Field(None, description="An ordered array of file or media attachments to include with the message. Each attachment should specify its file reference or media identifier."),
) -> dict[str, Any]:
    """Update an existing WhatsApp message activity, including its text content and any attached files or media."""

    # Construct request model with validation
    try:
        _request = _models.PutV1ActivityWhatsappMessageIdRequest(
            path=_models.PutV1ActivityWhatsappMessageIdRequestPath(id_=id_),
            body=_models.PutV1ActivityWhatsappMessageIdRequestBody(message_markdown=message_markdown, attachments=attachments)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_whatsapp_message: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/activity/whatsapp_message/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/activity/whatsapp_message/{id}"
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

# Tags: Activities
@mcp.tool()
async def delete_whatsapp_message(id_: str = Field(..., alias="id", description="The unique identifier of the WhatsApp message activity to delete.")) -> dict[str, Any]:
    """Delete a WhatsApp message activity record. This removes the activity log entry for a specific WhatsApp message interaction."""

    # Construct request model with validation
    try:
        _request = _models.DeleteV1ActivityWhatsappMessageIdRequest(
            path=_models.DeleteV1ActivityWhatsappMessageIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_whatsapp_message: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/activity/whatsapp_message/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/activity/whatsapp_message/{id}"
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

# Tags: Activities
@mcp.tool()
async def list_form_submissions(
    organization_id: str | None = Field(None, description="Filter results to a specific organization. Only activities belonging to this organization will be returned."),
    form_id__in: list[str] | None = Field(None, description="Filter results to one or more specific forms by providing their IDs. Only submissions from the specified forms will be included in the results."),
    limit: int | None = Field(None, alias="_limit", description="Maximum number of results to return. Use this to control pagination and response size."),
) -> dict[str, Any]:
    """Retrieve a list of form submission activities, with support for filtering by organization and specific forms. Use standard activity filtering parameters along with form-specific filters to narrow results."""

    # Construct request model with validation
    try:
        _request = _models.GetV1ActivityFormSubmissionRequest(
            query=_models.GetV1ActivityFormSubmissionRequestQuery(organization_id=organization_id, form_id__in=form_id__in, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_form_submissions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/activity/form_submission/"
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

# Tags: Activities
@mcp.tool()
async def get_form_submission(id_: str = Field(..., alias="id", description="The unique identifier of the form submission activity to retrieve.")) -> dict[str, Any]:
    """Retrieve a specific form submission activity by its unique identifier. Use this to access details about a completed or in-progress form submission."""

    # Construct request model with validation
    try:
        _request = _models.GetV1ActivityFormSubmissionIdRequest(
            path=_models.GetV1ActivityFormSubmissionIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_form_submission: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/activity/form_submission/{id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/activity/form_submission/{id}/"
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

# Tags: Activities
@mcp.tool()
async def delete_form_submission(id_: str = Field(..., alias="id", description="The unique identifier of the FormSubmission activity to delete.")) -> dict[str, Any]:
    """Permanently delete a FormSubmission activity record. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteV1ActivityFormSubmissionIdRequest(
            path=_models.DeleteV1ActivityFormSubmissionIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_form_submission: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/activity/form_submission/{id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/activity/form_submission/{id}/"
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
    status_type: Literal["active", "won", "lost"] | None = Field(None, description="Filter opportunities by status. Use active for ongoing deals, won for closed-won, or lost for closed-lost. Multiple statuses can be specified together."),
    date_created__lte: str | None = Field(None, description="Filter opportunities created on or before this date (ISO 8601 format)."),
    date_created__gte: str | None = Field(None, description="Filter opportunities created on or after this date (ISO 8601 format)."),
    date_updated__lte: str | None = Field(None, description="Filter opportunities last updated on or before this date (ISO 8601 format)."),
    date_updated__gte: str | None = Field(None, description="Filter opportunities last updated on or after this date (ISO 8601 format)."),
    date_won__lte: str | None = Field(None, description="Filter opportunities won on or before this date (ISO 8601 format)."),
    date_won__gte: str | None = Field(None, description="Filter opportunities won on or after this date (ISO 8601 format)."),
    value_period: Literal["one_time", "monthly", "annual"] | None = Field(None, description="Filter opportunities by revenue period type: one_time for single payments, monthly for recurring monthly revenue, or annual for recurring annual revenue. Multiple periods can be specified together."),
    order_by: str | None = Field(None, alias="_order_by", description="Sort results by a specific field in ascending order, or prepend a minus sign for descending order. Sortable fields include date_won, date_updated, date_created, confidence, user_name, value, annualized_value, and annualized_expected_value."),
    group_by: str | None = Field(None, alias="_group_by", description="Group results by a dimension such as user_id or time-based periods (week, month, quarter, or year based on date_won). Grouping aggregates metrics across matching opportunities."),
    lead_saved_search_id: str | None = Field(None, description="Filter opportunities by a saved lead search (Smart View) ID to narrow results to leads matching that view."),
    limit: int | None = Field(None, alias="_limit", description="Maximum number of results to return. If not specified, all matching opportunities are returned."),
) -> dict[str, Any]:
    """Retrieve and filter opportunities with optional filtering by lead, user, status, and dates. Returns aggregated metrics for all matching opportunities."""

    # Construct request model with validation
    try:
        _request = _models.GetV1OpportunityRequest(
            query=_models.GetV1OpportunityRequestQuery(status_type=status_type, date_created__lte=date_created__lte, date_created__gte=date_created__gte, date_updated__lte=date_updated__lte, date_updated__gte=date_updated__gte, date_won__lte=date_won__lte, date_won__gte=date_won__gte, value_period=value_period, order_by=order_by, group_by=group_by, lead_saved_search_id=lead_saved_search_id, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_opportunities: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/opportunity"
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
async def create_opportunity() -> dict[str, Any]:
    """Create a new sales opportunity. If no lead_id is provided, a new lead will be automatically created and associated with the opportunity."""

    # Extract parameters for API call
    _http_path = "/v1/opportunity"
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
        headers=_http_headers,
    )

    return _response_data

# Tags: Opportunities
@mcp.tool()
async def get_opportunity(id_: str = Field(..., alias="id", description="The unique identifier of the opportunity to retrieve.")) -> dict[str, Any]:
    """Retrieve a single opportunity by its unique identifier. Use this to fetch detailed information about a specific opportunity."""

    # Construct request model with validation
    try:
        _request = _models.GetV1OpportunityIdRequest(
            path=_models.GetV1OpportunityIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_opportunity: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/opportunity/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/opportunity/{id}"
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
    date_won: str | None = Field(None, description="The date when the opportunity was won, specified in ISO 8601 date-time format. If omitted and the opportunity status is set to won, this will be automatically set to the current date."),
) -> dict[str, Any]:
    """Update an opportunity's details. Automatically sets the win date to today if the opportunity status is changed to won and no win date is explicitly provided."""

    # Construct request model with validation
    try:
        _request = _models.PutV1OpportunityIdRequest(
            path=_models.PutV1OpportunityIdRequestPath(id_=id_),
            body=_models.PutV1OpportunityIdRequestBody(date_won=date_won)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_opportunity: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/opportunity/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/opportunity/{id}"
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
    """Permanently delete an opportunity from the system by its ID. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteV1OpportunityIdRequest(
            path=_models.DeleteV1OpportunityIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_opportunity: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/opportunity/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/opportunity/{id}"
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
    date__lt: str | None = Field(None, description="Return only tasks with a due date before the specified date and time (ISO 8601 format)."),
    date__gt: str | None = Field(None, description="Return only tasks with a due date after the specified date and time (ISO 8601 format)."),
    date__lte: str | None = Field(None, description="Return only tasks with a due date on or before the specified date and time (ISO 8601 format)."),
    date__gte: str | None = Field(None, description="Return only tasks with a due date on or after the specified date and time (ISO 8601 format)."),
    date_created__lte: str | None = Field(None, description="Return only tasks created on or before the specified date and time (ISO 8601 format)."),
    date_created__gte: str | None = Field(None, description="Return only tasks created on or after the specified date and time (ISO 8601 format)."),
    view: Literal["inbox", "future", "archive"] | None = Field(None, description="Use a predefined view to quickly access common task categories: 'inbox' for incomplete tasks through end of day, 'future' for incomplete tasks starting tomorrow, or 'archive' for completed tasks only."),
    order_by: str | None = Field(None, alias="_order_by", description="Sort results by 'date' (due date) or 'date_created' (creation date). Prepend a minus sign for descending order (e.g., '-date' for newest first)."),
    limit: int | None = Field(None, alias="_limit", description="Maximum number of results to return. Must be at least 1.", ge=1),
) -> dict[str, Any]:
    """Retrieve and filter tasks with flexible viewing options. Use convenience views (inbox, future, archive) for quick access to common task categories, or apply custom date-based filters and sorting."""

    # Construct request model with validation
    try:
        _request = _models.GetV1TaskRequest(
            query=_models.GetV1TaskRequestQuery(id_=id_, date__lt=date__lt, date__gt=date__gt, date__lte=date__lte, date__gte=date__gte, date_created__lte=date_created__lte, date_created__gte=date_created__gte, view=view, order_by=order_by, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_tasks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/task"
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
async def create_task(type_: Literal["lead", "outgoing_call"] = Field(..., alias="type", description="The category of task to create. Choose 'lead' for lead-related tasks or 'outgoing_call' for call tracking tasks.")) -> dict[str, Any]:
    """Create a new task in the system. Supports task types for lead management and outgoing call tracking."""

    # Construct request model with validation
    try:
        _request = _models.PostV1TaskRequest(
            body=_models.PostV1TaskRequestBody(type_=type_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_task: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/task"
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
async def bulk_update_tasks(
    is_complete: bool | None = Field(None, description="Mark the task as complete or incomplete."),
    assigned_to: str | None = Field(None, description="The user ID to assign the task to."),
    date: str | None = Field(None, description="The task date in ISO 8601 format, either as a date only (YYYY-MM-DD) or as a full timestamp with timezone information."),
) -> dict[str, Any]:
    """Update multiple tasks at once by applying changes to tasks matching specified filter criteria. Supports bulk modifications of completion status, task assignment, and task dates."""

    # Construct request model with validation
    try:
        _request = _models.PutV1TaskRequest(
            body=_models.PutV1TaskRequestBody(is_complete=is_complete, assigned_to=assigned_to, date=date)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for bulk_update_tasks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/task"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("bulk_update_tasks")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("bulk_update_tasks", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="bulk_update_tasks",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tasks
@mcp.tool()
async def get_task(id_: str = Field(..., alias="id", description="The unique identifier of the task to retrieve.")) -> dict[str, Any]:
    """Retrieve detailed information about a specific task, including its current status, metadata, and associated data."""

    # Construct request model with validation
    try:
        _request = _models.GetV1TaskIdRequest(
            path=_models.GetV1TaskIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_task: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/task/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/task/{id}"
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
    date: str | None = Field(None, description="The task date in either date-only format (YYYY-MM-DD) or ISO 8601 date-time format with timezone information."),
) -> dict[str, Any]:
    """Update an existing task by ID. You can modify the assignee, date, and completion status on any task. For lead-type tasks, you can also update the task text."""

    # Construct request model with validation
    try:
        _request = _models.PutV1TaskIdRequest(
            path=_models.PutV1TaskIdRequestPath(id_=id_),
            body=_models.PutV1TaskIdRequestBody(date=date)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_task: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/task/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/task/{id}"
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
    """Permanently delete a task by its ID. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteV1TaskIdRequest(
            path=_models.DeleteV1TaskIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_task: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/task/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/task/{id}"
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
    _http_path = "/v1/outcome"
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
    name: str = Field(..., description="The display name for this outcome. This is what users will see when viewing or assigning outcomes."),
    applies_to: list[Literal["calls", "meetings"]] = Field(..., description="An array specifying which object types this outcome can be assigned to. Each item defines a valid target for this outcome."),
    description: str | None = Field(None, description="An optional explanation of what this outcome represents and the circumstances under which it should be used."),
) -> dict[str, Any]:
    """Create a new outcome for your organization. Outcomes define measurable results that can be assigned to specific object types to track progress and success."""

    # Construct request model with validation
    try:
        _request = _models.PostV1OutcomeRequest(
            body=_models.PostV1OutcomeRequestBody(name=name, applies_to=applies_to, description=description)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_outcome: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/outcome"
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
    """Retrieve a specific outcome by its unique identifier. Use this to fetch detailed information about a single outcome."""

    # Construct request model with validation
    try:
        _request = _models.GetV1OutcomeIdRequest(
            path=_models.GetV1OutcomeIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_outcome: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/outcome/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/outcome/{id}"
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
    description: str | None = Field(None, description="The new description providing details about the outcome."),
    applies_to: list[Literal["calls", "meetings"]] | None = Field(None, description="An updated list of objects or entities that this outcome applies to, specified as an array of objects."),
) -> dict[str, Any]:
    """Update an existing outcome by modifying its name, description, applicable scope, or type classification."""

    # Construct request model with validation
    try:
        _request = _models.PutV1OutcomeIdRequest(
            path=_models.PutV1OutcomeIdRequestPath(id_=id_),
            body=_models.PutV1OutcomeIdRequestBody(name=name, description=description, applies_to=applies_to)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_outcome: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/outcome/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/outcome/{id}"
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
    """Delete an existing outcome. Associated calls and meetings will retain their outcome references, but the outcome will no longer be available for assignment to new calls and meetings."""

    # Construct request model with validation
    try:
        _request = _models.DeleteV1OutcomeIdRequest(
            path=_models.DeleteV1OutcomeIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_outcome: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/outcome/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/outcome/{id}"
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
    role_id: Literal["admin", "superuser", "user", "restricteduser"] | None = Field(None, description="The role to assign to this membership. Can be a predefined role ('admin', 'superuser', 'user', or 'restricteduser') or a custom Role ID."),
    auto_record_calls: Literal["unset", "disabled", "enabled"] | None = Field(None, description="Controls automatic call recording behavior. Set to 'enabled' to record calls automatically, 'disabled' to prevent automatic recording, or 'unset' to use default settings."),
) -> dict[str, Any]:
    """Update a membership's role and automatic call recording settings. Allows modification of user permissions through role assignment and control over whether calls are automatically recorded."""

    # Construct request model with validation
    try:
        _request = _models.PutV1MembershipIdRequest(
            path=_models.PutV1MembershipIdRequestPath(id_=id_),
            body=_models.PutV1MembershipIdRequestBody(role_id=role_id, auto_record_calls=auto_record_calls)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_membership: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/membership/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/membership/{id}"
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
    role_id: Literal["admin", "superuser", "user", "restricteduser"] = Field(..., description="The role to assign to the user. Use one of the predefined roles ('admin', 'superuser', 'user', 'restricteduser') or provide a custom Role ID."),
) -> dict[str, Any]:
    """Provision or activate a membership for a user by email address. Creates a new user if they don't exist, or adds an existing user to your organization with the specified role. Requires 'Manage Organization' permissions and OAuth authentication."""

    # Construct request model with validation
    try:
        _request = _models.PostV1MembershipRequest(
            body=_models.PostV1MembershipRequestBody(email=email, role_id=role_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for provision_membership: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/membership"
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
    id__in: str = Field(..., description="Comma-separated list of membership IDs to update. All specified memberships will receive the same updates."),
    role_id: Literal["admin", "superuser", "user", "restricteduser"] | None = Field(None, description="Role to assign to the memberships. Can be a specific role ID or one of the predefined roles: admin, superuser, user, or restricteduser."),
    auto_record_calls: Literal["unset", "disabled", "enabled"] | None = Field(None, description="Automatic call recording setting for the memberships. Choose unset to clear the setting, disabled to turn off recording, or enabled to turn on recording."),
) -> dict[str, Any]:
    """Update multiple memberships in bulk with the same settings. Apply role assignments or call recording preferences across multiple membership IDs simultaneously."""

    # Construct request model with validation
    try:
        _request = _models.PutV1MembershipRequest(
            query=_models.PutV1MembershipRequestQuery(id__in=id__in),
            body=_models.PutV1MembershipRequestBody(role_id=role_id, auto_record_calls=auto_record_calls)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for bulk_update_memberships: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/membership"
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
    """Retrieve the ordered list of pinned views for a specific membership. Pinned views are displayed in a user-defined sequence for quick access."""

    # Construct request model with validation
    try:
        _request = _models.GetV1MembershipIdPinnedViewsRequest(
            path=_models.GetV1MembershipIdPinnedViewsRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_pinned_views: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/membership/{id}/pinned_views/", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/membership/{id}/pinned_views/"
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
    body: list[dict[str, Any]] = Field(..., description="An ordered array of view identifiers to pin for this membership. The order determines the display sequence, and providing this list will completely replace any existing pinned views."),
) -> dict[str, Any]:
    """Update the pinned views for a membership by providing an ordered list that completely replaces the current pinned views configuration."""

    # Construct request model with validation
    try:
        _request = _models.PutV1MembershipIdPinnedViewsRequest(
            path=_models.PutV1MembershipIdPinnedViewsRequestPath(id_=id_),
            body=_models.PutV1MembershipIdPinnedViewsRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for set_membership_pinned_views: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/membership/{id}/pinned_views/", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/membership/{id}/pinned_views/"
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
    """Retrieve information about the authenticated user, including their user ID and associated Organization ID. Use this to determine your current organizational context."""

    # Extract parameters for API call
    _http_path = "/v1/me"
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
async def get_user(id_: str = Field(..., alias="id", description="The unique identifier of the user to retrieve.")) -> dict[str, Any]:
    """Retrieve a single user by their unique identifier. Returns the complete user profile for the specified ID."""

    # Construct request model with validation
    try:
        _request = _models.GetV1UserIdRequest(
            path=_models.GetV1UserIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/user/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/user/{id}"
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
        _request = _models.GetV1UserRequest(
            query=_models.GetV1UserRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_users: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/user"
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
async def list_user_availability(organization_id: str | None = Field(None, description="Filter the availability results to a specific organization. If not provided, returns availability for all accessible users.")) -> dict[str, Any]:
    """Retrieve the current availability status of all users in an organization, including details about any active calls they are participating in."""

    # Construct request model with validation
    try:
        _request = _models.GetV1UserAvailabilityRequest(
            query=_models.GetV1UserAvailabilityRequestQuery(organization_id=organization_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_user_availability: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/user/availability"
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
async def get_organization(id_: str = Field(..., alias="id", description="The unique identifier of the organization to retrieve.")) -> dict[str, Any]:
    """Retrieve detailed information about an organization, including its current members, inactive members, and configured lead and opportunity statuses. By default, membership data includes user information with a user_ prefix; use the _expand parameter to nest full user objects instead."""

    # Construct request model with validation
    try:
        _request = _models.GetV1OrganizationIdRequest(
            path=_models.GetV1OrganizationIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_organization: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/organization/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/organization/{id}"
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
    name: str | None = Field(None, description="The new name for the organization. If provided, replaces the current organization name."),
    currency: str | None = Field(None, description="The currency code for the organization (e.g., USD, EUR, GBP). If provided, updates the organization's default currency."),
    lead_statuses: list[dict[str, Any]] | None = Field(None, description="An ordered array of lead status identifiers to reorder how statuses appear in the organization. The order in this array determines the sequence of lead statuses."),
) -> dict[str, Any]:
    """Update an organization's profile including its name, currency, and the ordering of lead statuses. Changes are applied immediately to the organization."""

    # Construct request model with validation
    try:
        _request = _models.PutV1OrganizationIdRequest(
            path=_models.PutV1OrganizationIdRequestPath(id_=id_),
            body=_models.PutV1OrganizationIdRequestBody(name=name, currency=currency, lead_statuses=lead_statuses)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_organization: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/organization/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/organization/{id}"
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
    """Retrieve a specific role by its unique identifier. Use this to fetch detailed information about a single role."""

    # Construct request model with validation
    try:
        _request = _models.GetV1RoleIdRequest(
            path=_models.GetV1RoleIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_role: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/role/{id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/role/{id}/"
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
    """Retrieve all roles defined in your organization. Use this to view available role definitions for access control and permission management."""

    # Extract parameters for API call
    _http_path = "/v1/role/"
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
async def create_role(visibility_user_lcf_behavior: Literal["require_assignment", "allow_unassigned"] | None = Field(None, description="Controls lead visibility behavior for unassigned leads when the role does not have view_all_leads permission. Choose 'require_assignment' to restrict visibility to assigned leads only, or 'allow_unassigned' to permit access to leads without assigned users. Leave empty if the role has view_all_leads permission.")) -> dict[str, Any]:
    """Create a new role with configurable lead visibility settings. Use this to define a new role and specify how users with this role can access leads that lack assigned users."""

    # Construct request model with validation
    try:
        _request = _models.PostV1RoleRequest(
            body=_models.PostV1RoleRequestBody(visibility_user_lcf_behavior=visibility_user_lcf_behavior)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_role: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/role/"
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
    body: dict[str, Any] = Field(..., description="The role configuration object containing the properties to update, such as name, description, permissions, and other role attributes."),
) -> dict[str, Any]:
    """Update an existing role with new configuration and properties. Specify the role to modify using its ID and provide the updated role details in the request body."""

    # Construct request model with validation
    try:
        _request = _models.PutV1RoleRoleIdRequest(
            path=_models.PutV1RoleRoleIdRequestPath(role_id=role_id),
            body=_models.PutV1RoleRoleIdRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_role: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/role/{role_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/role/{role_id}/"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
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
    """Permanently delete a role from the system. Ensure all users assigned to this role are reassigned to a different role before deletion, as roles cannot be deleted while users are still associated with them."""

    # Construct request model with validation
    try:
        _request = _models.DeleteV1RoleRoleIdRequest(
            path=_models.DeleteV1RoleRoleIdRequestPath(role_id=role_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_role: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/role/{role_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/role/{role_id}/"
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
    """Retrieve all available lead statuses configured for your organization. Use this to understand the different stages leads can progress through in your sales pipeline."""

    # Extract parameters for API call
    _http_path = "/v1/status/lead"
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
async def create_lead_status(name: str = Field(..., description="The display name for the lead status. This name will appear in lead management interfaces and status selection dropdowns.")) -> dict[str, Any]:
    """Create a new custom status that can be assigned to leads in your pipeline. This allows you to define custom workflow stages beyond default statuses."""

    # Construct request model with validation
    try:
        _request = _models.PostV1StatusLeadRequest(
            body=_models.PostV1StatusLeadRequestBody(name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_lead_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/status/lead"
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
    """Rename an existing lead status. This updates the display name of a status category used to organize leads in your pipeline."""

    # Construct request model with validation
    try:
        _request = _models.PutV1StatusLeadStatusIdRequest(
            path=_models.PutV1StatusLeadStatusIdRequestPath(status_id=status_id),
            body=_models.PutV1StatusLeadStatusIdRequestBody(name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for rename_lead_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/status/lead/{status_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/status/lead/{status_id}"
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
    """Delete a lead status from your system. Ensure no leads are currently assigned this status before deletion, as the operation will fail if the status is in use."""

    # Construct request model with validation
    try:
        _request = _models.DeleteV1StatusLeadStatusIdRequest(
            path=_models.DeleteV1StatusLeadStatusIdRequestPath(status_id=status_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_lead_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/status/lead/{status_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/status/lead/{status_id}"
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
    _http_path = "/v1/status/opportunity"
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
    label: str = Field(..., description="The display name for this opportunity status."),
    status_type: Literal["active", "won", "lost"] = Field(..., description="The category of this status: active for ongoing opportunities, won for successfully closed deals, or lost for unsuccessful deals."),
    pipeline_id: str | None = Field(None, description="Optional pipeline identifier to create this status within a specific pipeline. If omitted, the status is created at the account level."),
) -> dict[str, Any]:
    """Create a new opportunity status for tracking deal progression. Statuses can be classified as active (ongoing), won (closed successfully), or lost (closed unsuccessfully), and can optionally be scoped to a specific pipeline."""

    # Construct request model with validation
    try:
        _request = _models.PostV1StatusOpportunityRequest(
            body=_models.PostV1StatusOpportunityRequestBody(label=label, status_type=status_type, pipeline_id=pipeline_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_opportunity_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/status/opportunity"
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
    label: str = Field(..., description="The new display label for the opportunity status."),
) -> dict[str, Any]:
    """Rename an existing opportunity status by providing its ID and the new label. This updates the display name of the status in your opportunity pipeline."""

    # Construct request model with validation
    try:
        _request = _models.PutV1StatusOpportunityStatusIdRequest(
            path=_models.PutV1StatusOpportunityStatusIdRequestPath(status_id=status_id),
            body=_models.PutV1StatusOpportunityStatusIdRequestBody(label=label)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for rename_opportunity_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/status/opportunity/{status_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/status/opportunity/{status_id}"
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
        _request = _models.DeleteV1StatusOpportunityStatusIdRequest(
            path=_models.DeleteV1StatusOpportunityStatusIdRequestPath(status_id=status_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_opportunity_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/status/opportunity/{status_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/status/opportunity/{status_id}"
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
    """Retrieve all pipelines in your organization. Use this to view the complete list of available pipelines for management and monitoring."""

    # Extract parameters for API call
    _http_path = "/v1/pipeline"
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
async def create_pipeline(name: str = Field(..., description="The name identifier for the pipeline. Used to reference and organize the pipeline within your workspace.")) -> dict[str, Any]:
    """Create a new pipeline with the specified name. Pipelines serve as containers for organizing and executing workflows."""

    # Construct request model with validation
    try:
        _request = _models.PostV1PipelineRequest(
            body=_models.PostV1PipelineRequestBody(name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_pipeline: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/pipeline"
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
    name: str | None = Field(None, description="The new name for the pipeline. Provide a descriptive name to identify the pipeline."),
    statuses: list[_models.PutV1PipelinePipelineIdBodyStatusesItem] | None = Field(None, description="An ordered array of opportunity statuses for this pipeline. Each status should include its ID; to move a status from another pipeline, include an object with the status ID from the source pipeline. The order of statuses in the array determines their display sequence."),
) -> dict[str, Any]:
    """Update an existing pipeline by modifying its name, reordering opportunity statuses, or moving statuses from other pipelines into this one."""

    # Construct request model with validation
    try:
        _request = _models.PutV1PipelinePipelineIdRequest(
            path=_models.PutV1PipelinePipelineIdRequestPath(pipeline_id=pipeline_id),
            body=_models.PutV1PipelinePipelineIdRequestBody(name=name, statuses=statuses)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_pipeline: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/pipeline/{pipeline_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/pipeline/{pipeline_id}"
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
    """Delete a pipeline from your workspace. The pipeline must be empty of all opportunity statuses before deletion—migrate or remove any existing opportunity statuses first."""

    # Construct request model with validation
    try:
        _request = _models.DeleteV1PipelinePipelineIdRequest(
            path=_models.DeleteV1PipelinePipelineIdRequestPath(pipeline_id=pipeline_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_pipeline: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/pipeline/{pipeline_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/pipeline/{pipeline_id}"
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
async def list_groups(fields: str = Field(..., alias="_fields", description="Comma-separated list of fields to include in the response. Must include at least 'name' and 'members' to retrieve group information.")) -> dict[str, Any]:
    """Retrieve all groups in your organization. Use this endpoint for a complete group listing; for detailed member information, query individual groups separately."""

    # Construct request model with validation
    try:
        _request = _models.GetV1GroupRequest(
            query=_models.GetV1GroupRequestQuery(fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_groups: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/group/"
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
    name: str = Field(..., description="The name of the group to create."),
) -> dict[str, Any]:
    """Create a new empty group. Use the member endpoint to add or remove users from the group after creation."""

    # Construct request model with validation
    try:
        _request = _models.PostV1GroupRequest(
            query=_models.PostV1GroupRequestQuery(fields=fields),
            body=_models.PostV1GroupRequestBody(name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/group/"
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
    fields: str = Field(..., alias="_fields", description="Comma-separated list of fields to include in the response. Must include at least 'name' and 'members' to retrieve group details and membership information."),
) -> dict[str, Any]:
    """Retrieve a specific group by its ID, including group name and member information."""

    # Construct request model with validation
    try:
        _request = _models.GetV1GroupGroupIdRequest(
            path=_models.GetV1GroupGroupIdRequestPath(group_id=group_id),
            query=_models.GetV1GroupGroupIdRequestQuery(fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/group/{group_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/group/{group_id}/"
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
async def update_group(
    group_id: str = Field(..., description="The unique identifier of the group to update."),
    fields: str = Field(..., alias="_fields", description="Comma-separated list of fields to include in the response. Must include at least 'name' and 'members' to retrieve the updated group information."),
    name: str | None = Field(None, description="The new name for the group. Must be unique across all groups in the system."),
) -> dict[str, Any]:
    """Update an existing group's properties, such as renaming it. Group names must be unique within the system."""

    # Construct request model with validation
    try:
        _request = _models.PutV1GroupGroupIdRequest(
            path=_models.PutV1GroupGroupIdRequestPath(group_id=group_id),
            query=_models.PutV1GroupGroupIdRequestQuery(fields=fields),
            body=_models.PutV1GroupGroupIdRequestBody(name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/group/{group_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/group/{group_id}/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_group")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_group", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_group",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Groups
@mcp.tool()
async def delete_group(group_id: str = Field(..., description="The unique identifier of the group to delete.")) -> dict[str, Any]:
    """Delete a group from the system. This operation is only permitted if the group is not currently referenced by any saved reports or smart views."""

    # Construct request model with validation
    try:
        _request = _models.DeleteV1GroupGroupIdRequest(
            path=_models.DeleteV1GroupGroupIdRequestPath(group_id=group_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/group/{group_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/group/{group_id}/"
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
    group_id: str = Field(..., description="The unique identifier of the group to which the user will be added."),
    user_id: str = Field(..., description="The unique identifier of the user to add to the group."),
) -> dict[str, Any]:
    """Add a user to a group. If the user is already a member, the operation completes without making changes."""

    # Construct request model with validation
    try:
        _request = _models.PostV1GroupGroupIdMemberRequest(
            path=_models.PostV1GroupGroupIdMemberRequestPath(group_id=group_id),
            body=_models.PostV1GroupGroupIdMemberRequestBody(user_id=user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_user_to_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/group/{group_id}/member/", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/group/{group_id}/member/"
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
    """Remove a user from a group. If the user is not a member of the group, the operation completes without error."""

    # Construct request model with validation
    try:
        _request = _models.DeleteV1GroupGroupIdMemberUserIdRequest(
            path=_models.DeleteV1GroupGroupIdMemberUserIdRequestPath(group_id=group_id, user_id=user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_group_member: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/group/{group_id}/member/{user_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/group/{group_id}/member/{user_id}/"
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
    """Retrieve the predefined metrics available for use in activity reports. Use these metrics to configure and customize your activity report queries."""

    # Extract parameters for API call
    _http_path = "/v1/report/activity/metrics"
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
    type_: Literal["overview", "comparison"] = Field(..., alias="type", description="The report format: 'overview' for organization-wide metrics by time period, or 'comparison' for metrics broken down by individual users."),
    metrics: list[str] = Field(..., description="A list of metric names to include in the report. Specify which metrics you want calculated and returned in the results."),
    relative_range: Literal["today", "this-week", "this-month", "this-quarter", "this-year", "yesterday", "last-week", "last-month", "last-quarter", "last-year", "all-time"] | None = Field(None, description="A relative time range for the report data. Choose from predefined ranges like 'today', 'this-week', 'this-month', or 'all-time'. Either this or a specific datetime range must be provided."),
    saved_search_id: str | None = Field(None, description="The ID of a saved search to apply as a filter for the report results."),
    users: list[str] | None = Field(None, description="A list of user IDs to filter the report to specific users. When provided, the report will only include data for these users."),
) -> dict[str, Any]:
    """Generate an activity report showing organizational metrics aggregated by time period (overview) or broken down by user (comparison). Specify the time range and metrics to include in the report."""

    # Construct request model with validation
    try:
        _request = _models.PostV1ReportActivityRequest(
            body=_models.PostV1ReportActivityRequestBody(relative_range=relative_range, type_=type_, users=users, metrics=metrics,
                query=_models.PostV1ReportActivityRequestBodyQuery(saved_search_id=saved_search_id) if any(v is not None for v in [saved_search_id]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for generate_activity_report: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/report/activity"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

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
    date_start: str | None = Field(None, description="The start date for filtering the report results, specified in date format (YYYY-MM-DD). If provided, only emails sent on or after this date will be included."),
    date_end: str | None = Field(None, description="The end date for filtering the report results, specified in date format (YYYY-MM-DD). If provided, only emails sent on or before this date will be included."),
) -> dict[str, Any]:
    """Retrieve a report of sent emails grouped by template for an organization, optionally filtered by a date range."""

    # Construct request model with validation
    try:
        _request = _models.GetV1ReportSentEmailsOrganizationIdRequest(
            path=_models.GetV1ReportSentEmailsOrganizationIdRequestPath(organization_id=organization_id),
            query=_models.GetV1ReportSentEmailsOrganizationIdRequestQuery(date_start=date_start, date_end=date_end)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_sent_emails_report: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/report/sent_emails/{organization_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/report/sent_emails/{organization_id}"
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
    date_start: str | None = Field(None, description="The start date for the report period in date format. If omitted, the report begins from the earliest available data."),
    date_end: str | None = Field(None, description="The end date for the report period in date format. If omitted, the report extends to the most recent data."),
) -> dict[str, Any]:
    """Retrieve a report of lead status changes for an organization, optionally filtered by a specific date range. If no dates are specified, the report covers all historical data."""

    # Construct request model with validation
    try:
        _request = _models.GetV1ReportStatusesLeadOrganizationIdRequest(
            path=_models.GetV1ReportStatusesLeadOrganizationIdRequestPath(organization_id=organization_id),
            query=_models.GetV1ReportStatusesLeadOrganizationIdRequestQuery(date_start=date_start, date_end=date_end)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_lead_status_report: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/report/statuses/lead/{organization_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/report/statuses/lead/{organization_id}"
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
    organization_id: str = Field(..., description="The unique identifier for the organization whose opportunity status changes should be reported."),
    date_start: str | None = Field(None, description="The start date for the reporting period in date format (YYYY-MM-DD). Only status changes on or after this date will be included."),
    date_end: str | None = Field(None, description="The end date for the reporting period in date format (YYYY-MM-DD). Only status changes on or before this date will be included."),
    smart_view_id: str | None = Field(None, description="Filter the report to include only opportunities within a specific smart view, identified by its unique ID."),
) -> dict[str, Any]:
    """Retrieve a status change report for opportunities within an organization, showing how opportunities transitioned between different statuses over a specified time period. Results can be filtered by smart view to focus on specific opportunity subsets."""

    # Construct request model with validation
    try:
        _request = _models.GetV1ReportStatusesOpportunityOrganizationIdRequest(
            path=_models.GetV1ReportStatusesOpportunityOrganizationIdRequestPath(organization_id=organization_id),
            query=_models.GetV1ReportStatusesOpportunityOrganizationIdRequestQuery(date_start=date_start, date_end=date_end, smart_view_id=smart_view_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_opportunity_status_report: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/report/statuses/opportunity/{organization_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/report/statuses/opportunity/{organization_id}"
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
    organization_id: str = Field(..., description="The unique identifier for the organization whose data will be included in the report."),
    y: str | None = Field(None, description="The metric to display on the Y axis, such as lead.count, call.duration, or opportunity.value. Defaults to lead.count if not specified."),
    x: str | None = Field(None, description="The field to display on the X axis, such as lead.custom.MRR or opportunity.date_created. Can be time-based or numeric."),
    interval: str | None = Field(None, description="The granularity for bucketing data. For time-based X axes, use auto, hour, day, week, month, quarter, or year. For numeric X axes, specify an integer interval. Defaults to auto."),
    group_by: str | None = Field(None, description="Optional field name to segment the report data into separate series or groups."),
    transform_y: Literal["sum", "avg", "min", "max"] | None = Field(None, description="The aggregation function applied to Y-axis values. Choose from sum, avg, min, or max. Defaults to sum."),
    start: str | None = Field(None, description="The start of the X-axis range as a date or integer value. For dates, defaults to your organization's creation date if not provided."),
    end: str | None = Field(None, description="The end of the X-axis range as a date or integer value. For dates, defaults to the current date and time if not provided."),
) -> dict[str, Any]:
    """Generate a custom analytics report for any Close object with flexible metrics, grouping, and time-based or numeric axis configuration. Powers the Explorer visualization in the UI."""

    # Construct request model with validation
    try:
        _request = _models.GetV1ReportCustomOrganizationIdRequest(
            path=_models.GetV1ReportCustomOrganizationIdRequestPath(organization_id=organization_id),
            query=_models.GetV1ReportCustomOrganizationIdRequestQuery(y=y, x=x, interval=interval, group_by=group_by, transform_y=transform_y, start=start, end=end)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for generate_custom_report: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/report/custom/{organization_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/report/custom/{organization_id}"
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
    """Retrieve the complete list of available fields that can be used when building custom reports. Only numeric data type fields can be used for the y-axis parameter in custom report configurations."""

    # Extract parameters for API call
    _http_path = "/v1/report/custom/fields"
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
    pipeline: str = Field(..., description="The pipeline ID that defines the funnel stages used to categorize opportunities."),
    type_: Literal["created-cohort", "active-stage-cohort"] = Field(..., alias="type", description="The report type determining how opportunities are grouped: either by creation cohort or by their current active stage."),
    query_type: Literal["saved_search"] | None = Field(None, alias="queryType", description="The query type for filtering opportunities; use 'saved_search' to apply a predefined search filter."),
    report_datetime_range: dict[str, Any] | None = Field(None, description="The time range for which to fetch report data, specified as a date range object."),
    cohort_datetime_range: dict[str, Any] | None = Field(None, description="The time range defining which opportunities to include in the cohort, specified as a date range object."),
    compared_custom_range: dict[str, Any] | None = Field(None, description="An optional time range for fetching comparison data to analyze trends across different periods."),
    saved_search_id: str | None = Field(None, description="The ID of a saved search to apply as a filter when query.type is set to 'saved_search'."),
    users: list[str] | None = Field(None, description="A list of user IDs or group IDs to limit report results to specific team members or groups."),
) -> dict[str, Any]:
    """Retrieve aggregated pipeline funnel metrics for opportunities, with support for cohort analysis and optional per-user breakdowns. Results can be filtered by time ranges, saved searches, and specific users or groups."""

    # Construct request model with validation
    try:
        _request = _models.PostV1ReportFunnelOpportunityTotalsRequest(
            body=_models.PostV1ReportFunnelOpportunityTotalsRequestBody(pipeline=pipeline, type_=type_, report_datetime_range=report_datetime_range, cohort_datetime_range=cohort_datetime_range, compared_custom_range=compared_custom_range, users=users,
                query=_models.PostV1ReportFunnelOpportunityTotalsRequestBodyQuery(type_=query_type, saved_search_id=saved_search_id) if any(v is not None for v in [query_type, saved_search_id]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_funnel_opportunity_totals: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/report/funnel/opportunity/totals"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

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
    type_: Literal["created-cohort", "active-stage-cohort"] = Field(..., alias="type", description="The report type: either 'created-cohort' to analyze opportunities by creation date, or 'active-stage-cohort' to analyze opportunities by their current stage."),
    query_type: Literal["saved_search"] | None = Field(None, alias="queryType", description="Optional query type; when set to 'saved_search', applies a saved search filter to the report data."),
    report_datetime_range: dict[str, Any] | None = Field(None, description="Optional time range for fetching the report data. Specify as a date range object to limit results to a specific period."),
    cohort_datetime_range: dict[str, Any] | None = Field(None, description="Optional time range defining which opportunities to include in the cohort based on their creation date."),
    compared_custom_range: dict[str, Any] | None = Field(None, description="Optional time range for fetching comparison data to analyze trends or changes over different periods."),
    saved_search_id: str | None = Field(None, description="The ID of a saved search to apply as a filter; used when query.type is set to 'saved_search'."),
    users: list[str] | None = Field(None, description="Optional list of user IDs or group IDs to segment the report results by specific team members or groups."),
) -> dict[str, Any]:
    """Generate a funnel report analyzing pipeline stage metrics for opportunities. Returns aggregated metrics in JSON format, with optional per-user breakdowns available in JSON or CSV formats."""

    # Construct request model with validation
    try:
        _request = _models.PostV1ReportFunnelOpportunityStagesRequest(
            body=_models.PostV1ReportFunnelOpportunityStagesRequestBody(pipeline=pipeline, type_=type_, report_datetime_range=report_datetime_range, cohort_datetime_range=cohort_datetime_range, compared_custom_range=compared_custom_range, users=users,
                query=_models.PostV1ReportFunnelOpportunityStagesRequestBodyQuery(type_=query_type, saved_search_id=saved_search_id) if any(v is not None for v in [query_type, saved_search_id]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_opportunity_funnel_stages_report: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/report/funnel/opportunity/stages"
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
    limit: int | None = Field(None, alias="_limit", description="Limit the number of results returned in a single response. Must be at least 1. Use pagination to retrieve large template collections efficiently.", ge=1),
) -> dict[str, Any]:
    """Retrieve all email templates with optional filtering by archive status and pagination support. Use this to browse available templates for sending or management purposes."""

    # Construct request model with validation
    try:
        _request = _models.GetV1EmailTemplateRequest(
            query=_models.GetV1EmailTemplateRequestQuery(is_archived=is_archived, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_email_templates: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/email_template/"
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
    """Create a new email template that can be used for sending emails. Define the template structure, content, and variables for reuse across email communications."""

    # Construct request model with validation
    try:
        _request = _models.PostV1EmailTemplateRequest(
            body=_models.PostV1EmailTemplateRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_email_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/email_template/"
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
    """Retrieve a specific email template by its unique identifier. Use this to fetch template details for viewing or further processing."""

    # Construct request model with validation
    try:
        _request = _models.GetV1EmailTemplateIdRequest(
            path=_models.GetV1EmailTemplateIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_email_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/email_template/{id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/email_template/{id}/"
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
    body: dict[str, Any] = Field(..., description="The email template data to update, including fields such as subject, body, variables, and other template configuration."),
) -> dict[str, Any]:
    """Update an existing email template with new content, settings, or configuration. Specify the template ID and provide the updated template data in the request body."""

    # Construct request model with validation
    try:
        _request = _models.PutV1EmailTemplateIdRequest(
            path=_models.PutV1EmailTemplateIdRequestPath(id_=id_),
            body=_models.PutV1EmailTemplateIdRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_email_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/email_template/{id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/email_template/{id}/"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
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
    """Permanently delete an email template by its ID. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteV1EmailTemplateIdRequest(
            path=_models.DeleteV1EmailTemplateIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_email_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/email_template/{id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/email_template/{id}/"
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
    mode: Literal["lead", "contact"] | None = Field(None, description="Specifies which contact data to use for rendering: 'lead' renders the first contact associated with the lead (default), or 'contact' to render a specific contact by index."),
) -> dict[str, Any]:
    """Render an email template with actual data from a lead or contact to preview the final formatted output. Use this to see how the template will appear before sending."""

    # Construct request model with validation
    try:
        _request = _models.GetV1EmailTemplateIdRenderRequest(
            path=_models.GetV1EmailTemplateIdRenderRequestPath(id_=id_),
            query=_models.GetV1EmailTemplateIdRenderRequestQuery(mode=mode)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for render_email_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/email_template/{id}/render/", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/email_template/{id}/render/"
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
async def list_sms_templates(limit: int | None = Field(None, alias="_limit", description="Maximum number of SMS templates to return in the response. Useful for pagination or controlling result set size.")) -> dict[str, Any]:
    """Retrieve a list of SMS templates available in your account. Use the limit parameter to control the number of results returned."""

    # Construct request model with validation
    try:
        _request = _models.GetV1SmsTemplateRequest(
            query=_models.GetV1SmsTemplateRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_sms_templates: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/sms_template"
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
async def create_sms_template(body: dict[str, Any] = Field(..., description="Template configuration object containing the SMS template details such as name, content, and any variable placeholders for dynamic content.")) -> dict[str, Any]:
    """Create a new SMS template that can be used for sending templated SMS messages. Define the template content and configuration for reuse across multiple SMS campaigns."""

    # Construct request model with validation
    try:
        _request = _models.PostV1SmsTemplateRequest(
            body=_models.PostV1SmsTemplateRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_sms_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/sms_template"
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
        _request = _models.GetV1SmsTemplateIdRequest(
            path=_models.GetV1SmsTemplateIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_sms_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/sms_template/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/sms_template/{id}"
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
    body: dict[str, Any] = Field(..., description="The updated SMS template configuration and content."),
) -> dict[str, Any]:
    """Update an existing SMS template by ID. Modify the template content and configuration to reflect your current messaging needs."""

    # Construct request model with validation
    try:
        _request = _models.PutV1SmsTemplateIdRequest(
            path=_models.PutV1SmsTemplateIdRequestPath(id_=id_),
            body=_models.PutV1SmsTemplateIdRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_sms_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/sms_template/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/sms_template/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
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
    """Permanently delete an SMS template by its ID. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteV1SmsTemplateIdRequest(
            path=_models.DeleteV1SmsTemplateIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_sms_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/sms_template/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/sms_template/{id}"
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
    _http_path = "/v1/connected_account"
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
    """Retrieve details for a specific connected account by its unique identifier. Use this to fetch account information such as authentication status, configuration, and metadata."""

    # Construct request model with validation
    try:
        _request = _models.GetV1ConnectedAccountIdRequest(
            path=_models.GetV1ConnectedAccountIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_connected_account: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/connected_account/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/connected_account/{id}"
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
    allowing_user_id: str | None = Field(None, description="Filter associations by the user ID who is granting Send As permission. Must be your own user ID if provided."),
    allowed_user_id: str | None = Field(None, description="Filter associations by the user ID who is receiving Send As permission. Must be your own user ID if provided."),
) -> dict[str, Any]:
    """Retrieve all Send As associations for the authenticated user. You can filter by either the user granting permission (allowing_user_id) or the user receiving permission (allowed_user_id), and at least one must match your user ID."""

    # Construct request model with validation
    try:
        _request = _models.GetV1SendAsRequest(
            query=_models.GetV1SendAsRequestQuery(allowing_user_id=allowing_user_id, allowed_user_id=allowed_user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_send_as_associations: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/send_as/"
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
async def create_send_as_association(
    allowing_user_id: str = Field(..., description="Your user ID that will grant send-as permission to another user. This must match your own user ID."),
    allowed_user_id: str = Field(..., description="The user ID of the person who will be granted permission to send messages as the allowing user."),
) -> dict[str, Any]:
    """Grant another user permission to send messages on your behalf by creating a Send As Association. The allowing_user_id must match your own user ID."""

    # Construct request model with validation
    try:
        _request = _models.PostV1SendAsRequest(
            body=_models.PostV1SendAsRequestBody(allowing_user_id=allowing_user_id, allowed_user_id=allowed_user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_send_as_association: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/send_as/"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_send_as_association")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_send_as_association", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_send_as_association",
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
    allowing_user_id: str = Field(..., description="The user ID of the person who granted send-as permission. This must match your own user ID."),
    allowed_user_id: str = Field(..., description="The user ID of the person whose send-as permission is being revoked."),
) -> dict[str, Any]:
    """Revoke a user's permission to send emails on behalf of another user. Both the authorizing user and the authorized user must be specified to remove the association."""

    # Construct request model with validation
    try:
        _request = _models.DeleteV1SendAsRequest(
            query=_models.DeleteV1SendAsRequestQuery(allowing_user_id=allowing_user_id, allowed_user_id=allowed_user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for revoke_send_as_permission: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/send_as/"
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
    """Retrieve a single Send As Association by its unique identifier. Use this to fetch details about a specific email sending configuration."""

    # Construct request model with validation
    try:
        _request = _models.GetV1SendAsIdRequest(
            path=_models.GetV1SendAsIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_send_as: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/send_as/{id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/send_as/{id}/"
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
    """Remove a Send As Association by its ID, preventing further use of that sender identity."""

    # Construct request model with validation
    try:
        _request = _models.DeleteV1SendAsIdRequest(
            path=_models.DeleteV1SendAsIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_send_as: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/send_as/{id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/send_as/{id}/"
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
async def update_send_as_permissions_bulk(
    allow: list[str] | None = Field(None, description="List of user IDs to grant Send As permission to. These users will be able to send messages as you."),
    disallow: list[str] | None = Field(None, description="List of user IDs to revoke Send As permission from. These users will no longer be able to send messages as you."),
) -> dict[str, Any]:
    """Manage multiple Send As permissions in a single request by granting or revoking the ability for other users to send messages on your behalf. Returns all current Send As associations after the update is complete."""

    # Construct request model with validation
    try:
        _request = _models.PostV1SendAsBulkRequest(
            body=_models.PostV1SendAsBulkRequestBody(allow=allow, disallow=disallow)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_send_as_permissions_bulk: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/send_as/bulk/"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_send_as_permissions_bulk")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_send_as_permissions_bulk", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_send_as_permissions_bulk",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Sequences
@mcp.tool()
async def list_sequences(limit: int | None = Field(None, alias="_limit", description="Maximum number of sequences to return in a single request. Useful for controlling response size and implementing pagination.")) -> dict[str, Any]:
    """Retrieve a paginated list of all sequences. Use the limit parameter to control the maximum number of results returned."""

    # Construct request model with validation
    try:
        _request = _models.GetV1SequenceRequest(
            query=_models.GetV1SequenceRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_sequences: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/sequence"
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
        _request = _models.PostV1SequenceRequest(
            body=_models.PostV1SequenceRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_sequence: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/sequence"
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
async def get_sequence(id_: str = Field(..., alias="id", description="The unique identifier of the sequence to retrieve.")) -> dict[str, Any]:
    """Retrieve a specific sequence by its unique identifier. Use this operation to fetch detailed information about a sequence."""

    # Construct request model with validation
    try:
        _request = _models.GetV1SequenceIdRequest(
            path=_models.GetV1SequenceIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_sequence: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/sequence/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/sequence/{id}"
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
    body: dict[str, Any] = Field(..., description="The sequence configuration object containing the fields to update, including an optional steps array that defines the sequence's workflow steps."),
) -> dict[str, Any]:
    """Update an existing sequence by modifying its configuration. Any steps included in the request will replace the sequence's current steps; steps not included will be removed."""

    # Construct request model with validation
    try:
        _request = _models.PutV1SequenceIdRequest(
            path=_models.PutV1SequenceIdRequestPath(id_=id_),
            body=_models.PutV1SequenceIdRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_sequence: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/sequence/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/sequence/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
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
    """Permanently delete a sequence by its ID. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteV1SequenceIdRequest(
            path=_models.DeleteV1SequenceIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_sequence: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/sequence/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/sequence/{id}"
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
async def list_sequence_subscriptions(sequence_id: str | None = Field(None, description="Filter results to show subscriptions for a specific sequence. Use the sequence's unique identifier.")) -> dict[str, Any]:
    """Retrieve a list of sequence subscriptions filtered by sequence, contact, or lead. At least one filter parameter is required to execute this operation."""

    # Construct request model with validation
    try:
        _request = _models.GetV1SequenceSubscriptionRequest(
            query=_models.GetV1SequenceSubscriptionRequestQuery(sequence_id=sequence_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_sequence_subscriptions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/sequence_subscription"
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
async def subscribe_contact_to_sequence(body: dict[str, Any] = Field(..., description="The subscription details including the contact identifier and sequence to subscribe them to. This object should contain the necessary identifiers and configuration for the sequence subscription.")) -> dict[str, Any]:
    """Subscribe a contact to an automation sequence. This creates a new sequence subscription that will trigger the contact to receive the sequence's automated messages and actions."""

    # Construct request model with validation
    try:
        _request = _models.PostV1SequenceSubscriptionRequest(
            body=_models.PostV1SequenceSubscriptionRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for subscribe_contact_to_sequence: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/sequence_subscription"
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
    """Retrieve a specific sequence subscription by its unique identifier. Use this to fetch details about an individual sequence subscription."""

    # Construct request model with validation
    try:
        _request = _models.GetV1SequenceSubscriptionIdRequest(
            path=_models.GetV1SequenceSubscriptionIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_sequence_subscription: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/sequence_subscription/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/sequence_subscription/{id}"
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
    body: dict[str, Any] = Field(..., description="The subscription data to update. Include the fields you want to modify in the request body."),
) -> dict[str, Any]:
    """Update an existing sequence subscription with new configuration or settings. Modify subscription parameters such as status, frequency, or other subscription-specific properties."""

    # Construct request model with validation
    try:
        _request = _models.PutV1SequenceSubscriptionIdRequest(
            path=_models.PutV1SequenceSubscriptionIdRequestPath(id_=id_),
            body=_models.PutV1SequenceSubscriptionIdRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_sequence_subscription: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/sequence_subscription/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/sequence_subscription/{id}"
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
    source_value: str | None = Field(None, description="Filter results by the source identifier, which can be either a Smart View ID or Shared Entry ID depending on the source type."),
    source_type: Literal["saved-search", "shared-entry"] | None = Field(None, description="Filter results by source type. Must be either 'saved-search' for Smart View sources or 'shared-entry' for Shared Entry sources."),
    limit: int | None = Field(None, alias="_limit", description="Maximum number of dialer sessions to return in the response. Use this to control result set size."),
) -> dict[str, Any]:
    """Retrieve and filter dialer sessions with details about their source, type, and associated users. Use optional filters to narrow results by source value or type."""

    # Construct request model with validation
    try:
        _request = _models.GetV1DialerRequest(
            query=_models.GetV1DialerRequestQuery(source_value=source_value, source_type=source_type, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_dialer_sessions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/dialer"
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
async def get_dialer_session(id_: str = Field(..., alias="id", description="The unique identifier of the dialer session to retrieve.")) -> dict[str, Any]:
    """Retrieve details of a specific dialer session by its unique identifier. Use this to fetch current status, configuration, and activity information for an active or completed dialing session."""

    # Construct request model with validation
    try:
        _request = _models.GetV1DialerIdRequest(
            path=_models.GetV1DialerIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_dialer_session: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/dialer/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/dialer/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_dialer_session")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_dialer_session", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_dialer_session",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Smart Views
@mcp.tool()
async def list_smart_views() -> dict[str, Any]:
    """Retrieve all saved Smart Views, which are customizable filters for organizing and viewing leads or contacts. Use this to display available views to users or programmatically access saved filtering configurations."""

    # Extract parameters for API call
    _http_path = "/v1/saved_search"
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
        headers=_http_headers,
    )

    return _response_data

# Tags: Smart Views
@mcp.tool()
async def create_smart_view(
    name: str = Field(..., description="The display name for the Smart View. This is the label users will see when accessing their saved views."),
    query: dict[str, Any] = Field(..., description="A filter query object that defines which records appear in the Smart View. Must include an object_type clause specifying either 'Lead' or 'Contact' to determine the record type being filtered."),
) -> dict[str, Any]:
    """Create a new Smart View for organizing and filtering Leads or Contacts. Smart Views use advanced filtering queries to automatically group records based on specified criteria."""

    # Construct request model with validation
    try:
        _request = _models.PostV1SavedSearchRequest(
            body=_models.PostV1SavedSearchRequestBody(name=name, query=query)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_smart_view: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/saved_search"
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
    """Retrieve a specific Smart View by its unique identifier. Use this to fetch detailed information about a saved search view."""

    # Construct request model with validation
    try:
        _request = _models.GetV1SavedSearchIdRequest(
            path=_models.GetV1SavedSearchIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_smart_view: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/saved_search/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/saved_search/{id}"
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
    id_: str = Field(..., alias="id", description="The unique identifier of the Smart View to update."),
    name: str | None = Field(None, description="The new name for the Smart View. Provide a descriptive name to help identify this saved search."),
) -> dict[str, Any]:
    """Update an existing Smart View by modifying its name or other properties. Use the Smart View ID to identify which view to update."""

    # Construct request model with validation
    try:
        _request = _models.PutV1SavedSearchIdRequest(
            path=_models.PutV1SavedSearchIdRequestPath(id_=id_),
            body=_models.PutV1SavedSearchIdRequestBody(name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_smart_view: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/saved_search/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/saved_search/{id}"
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
    """Delete a Smart View by its unique identifier. This operation permanently removes the saved search and cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteV1SavedSearchIdRequest(
            path=_models.DeleteV1SavedSearchIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_smart_view: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/saved_search/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/saved_search/{id}"
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
    """Retrieve a list of all bulk email actions that have been created. This endpoint provides an overview of bulk email campaigns and their statuses."""

    # Extract parameters for API call
    _http_path = "/v1/bulk_action/email"
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
    s_query: dict[str, Any] = Field(..., description="Structured query object defining which leads to target, using the same filtering syntax as the Advanced Filtering API."),
    results_limit: int | None = Field(None, description="Maximum number of leads to include in this bulk email action. If not specified, all matching leads will be affected."),
    sort: list[dict[str, Any]] | None = Field(None, description="Sort order for the leads, specified as an array of sort criteria. Order matters and determines which leads are prioritized when results_limit is applied."),
    contact_preference: Literal["lead", "contact"] | None = Field(None, description="Determines email recipient scope: 'lead' sends to only the primary contact email of each lead, while 'contact' sends to the first contact email of each contact associated with the lead."),
    send_done_email: bool | None = Field(None, description="Whether to send a confirmation email upon completion of the bulk email action. Enabled by default."),
) -> dict[str, Any]:
    """Send bulk emails to leads matching specified criteria. Choose whether to email the primary lead contact or all contacts associated with each lead."""

    # Construct request model with validation
    try:
        _request = _models.PostV1BulkActionEmailRequest(
            body=_models.PostV1BulkActionEmailRequestBody(s_query=s_query, results_limit=results_limit, sort=sort, contact_preference=contact_preference, send_done_email=send_done_email)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for send_bulk_email: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/bulk_action/email"
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
    """Retrieve details of a specific bulk email action by its ID. Returns the complete configuration and status information for the bulk email operation."""

    # Construct request model with validation
    try:
        _request = _models.GetV1BulkActionEmailIdRequest(
            path=_models.GetV1BulkActionEmailIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_bulk_email: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/bulk_action/email/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/bulk_action/email/{id}"
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
    _http_path = "/v1/bulk_action/sequence_subscription"
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
async def bulk_subscribe_sequence(
    s_query: dict[str, Any] = Field(..., description="Structured query object that defines which leads or contacts to affect. Uses the same query format as the Advanced Filtering API to specify filtering, matching, and selection criteria."),
    action_type: Literal["subscribe", "resume", "resume_finished", "pause"] = Field(..., description="The subscription action to perform: 'subscribe' to add leads to a sequence, 'resume' to restart paused sequences, 'resume_finished' to restart completed sequences, or 'pause' to pause active sequences."),
    results_limit: int | None = Field(None, description="Maximum number of leads to process in this bulk action. If not specified, all matching leads will be affected."),
    sort: list[dict[str, Any]] | None = Field(None, description="Sort order for the results. Specify as an array of sort criteria to control which leads are prioritized when a results_limit is applied."),
    sequence_id: str | None = Field(None, description="The ID of the sequence to subscribe leads to. Required when action_type is 'subscribe'."),
    sender_account_id: str | None = Field(None, description="The account ID of the sender who will be associated with the sequence. Required when action_type is 'subscribe'."),
    contact_preference: Literal["lead", "contact"] | None = Field(None, description="Subscription scope: 'lead' to subscribe only the primary/first contact email, or 'contact' to subscribe the primary email of each contact in the lead record. Required when action_type is 'subscribe'."),
    sender: str | None = Field(None, description="Sender identity in RFC 5322 format: Name <email@domain>"),
) -> dict[str, Any]:
    """Bulk subscribe, resume, or pause contacts in a sequence. Use this operation to perform subscription actions on multiple leads or contacts matching your query criteria, such as subscribing them to a new sequence, resuming paused sequences, or pausing active sequences."""

    # Call helper functions
    sender_parsed = parse_sender(sender)

    # Construct request model with validation
    try:
        _request = _models.PostV1BulkActionSequenceSubscriptionRequest(
            body=_models.PostV1BulkActionSequenceSubscriptionRequestBody(s_query=s_query, results_limit=results_limit, sort=sort, action_type=action_type, sequence_id=sequence_id, sender_account_id=sender_account_id, contact_preference=contact_preference, sender_name=sender_parsed.get('sender_name') if sender_parsed else None, sender_email=sender_parsed.get('sender_email') if sender_parsed else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for bulk_subscribe_sequence: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/bulk_action/sequence_subscription"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("bulk_subscribe_sequence")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("bulk_subscribe_sequence", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="bulk_subscribe_sequence",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Bulk Actions
@mcp.tool()
async def get_bulk_sequence_subscription(id_: str = Field(..., alias="id", description="The unique identifier of the bulk sequence subscription action to retrieve.")) -> dict[str, Any]:
    """Retrieve details of a specific bulk sequence subscription, including its configuration and status."""

    # Construct request model with validation
    try:
        _request = _models.GetV1BulkActionSequenceSubscriptionIdRequest(
            path=_models.GetV1BulkActionSequenceSubscriptionIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_bulk_sequence_subscription: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/bulk_action/sequence_subscription/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/bulk_action/sequence_subscription/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_bulk_sequence_subscription")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_bulk_sequence_subscription", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_bulk_sequence_subscription",
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
    _http_path = "/v1/bulk_action/delete"
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
    s_query: dict[str, Any] = Field(..., description="Structured query object defining which leads to delete, using the same format as the Advanced Filtering API query field."),
    results_limit: int | None = Field(None, description="Maximum number of leads to delete in this operation; if not specified, all matching leads will be affected."),
    sort: list[dict[str, Any]] | None = Field(None, description="Sort specification to order results before deletion; order matters and determines which leads are affected when combined with results_limit."),
    send_done_email: bool | None = Field(None, description="Whether to send a confirmation email upon completion; defaults to true if not specified."),
) -> dict[str, Any]:
    """Initiate a bulk delete operation to remove multiple leads matching specified criteria. Optionally receive a confirmation email when the operation completes."""

    # Construct request model with validation
    try:
        _request = _models.PostV1BulkActionDeleteRequest(
            body=_models.PostV1BulkActionDeleteRequestBody(s_query=s_query, results_limit=results_limit, sort=sort, send_done_email=send_done_email)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_leads_bulk: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/bulk_action/delete"
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
async def get_bulk_delete_action(id_: str = Field(..., alias="id", description="The unique identifier of the bulk delete action to retrieve.")) -> dict[str, Any]:
    """Retrieve details of a specific bulk delete action, including its status, progress, and configuration."""

    # Construct request model with validation
    try:
        _request = _models.GetV1BulkActionDeleteIdRequest(
            path=_models.GetV1BulkActionDeleteIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_bulk_delete_action: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/bulk_action/delete/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/bulk_action/delete/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_bulk_delete_action")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_bulk_delete_action", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_bulk_delete_action",
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
    _http_path = "/v1/bulk_action/edit"
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
    s_query: dict[str, Any] = Field(..., description="Structured query object that defines which leads to target, using the same format as the Advanced Filtering API."),
    type_: Literal["set_lead_status", "clear_custom_field", "set_custom_field"] = Field(..., alias="type", description="The type of bulk edit to perform: 'set_lead_status' to change lead status, 'clear_custom_field' to remove a custom field value, or 'set_custom_field' to update a custom field value."),
    results_limit: int | None = Field(None, description="Maximum number of leads to affect with this bulk edit action. If not specified, all matching leads will be updated."),
    sort: list[dict[str, Any]] | None = Field(None, description="Sort specification to order the leads before applying the bulk edit. Specify as an array of sort criteria."),
    lead_status_id: str | None = Field(None, description="The ID of the Lead Status to assign. Required when type is 'set_lead_status'."),
    custom_field_name: str | None = Field(None, description="The name of the custom field to modify. Required when type is 'clear_custom_field' or 'set_custom_field', unless you provide custom_field_id instead."),
    custom_field_values: list[Any] | None = Field(None, description="Array of values to set for custom fields that support multiple values. Use with 'set_custom_field' type."),
    custom_field_operation: Literal["replace", "add", "remove"] | None = Field(None, description="How to apply values to multi-value custom fields: 'replace' to overwrite existing values, 'add' to append new values, or 'remove' to delete specific values. Defaults to 'replace'."),
    send_done_email: bool | None = Field(None, description="Whether to send a confirmation email when the bulk edit completes. Defaults to true; set to false to skip the notification."),
) -> dict[str, Any]:
    """Initiate a bulk edit action on leads matching your query criteria. Choose from updating lead status, clearing a custom field, or setting custom field values across multiple leads."""

    # Construct request model with validation
    try:
        _request = _models.PostV1BulkActionEditRequest(
            body=_models.PostV1BulkActionEditRequestBody(s_query=s_query, results_limit=results_limit, sort=sort, type_=type_, lead_status_id=lead_status_id, custom_field_name=custom_field_name, custom_field_values=custom_field_values, custom_field_operation=custom_field_operation, send_done_email=send_done_email)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for bulk_edit_leads: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/bulk_action/edit"
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
    """Retrieve the details and status of a specific bulk edit action by its ID."""

    # Construct request model with validation
    try:
        _request = _models.GetV1BulkActionEditIdRequest(
            path=_models.GetV1BulkActionEditIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_bulk_edit: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/bulk_action/edit/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/bulk_action/edit/{id}"
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
    """Retrieve all integration links configured for your organization. This returns a complete list of active integrations that enable data synchronization and connectivity with external services."""

    # Extract parameters for API call
    _http_path = "/v1/integration_link"
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
    url: str = Field(..., description="The URL template that defines where this integration link directs to. Use this to specify dynamic routing based on the integration type."),
    type_: Literal["lead", "contact", "opportunity"] = Field(..., alias="type", description="The entity type this integration link applies to. Must be one of: lead, contact, or opportunity."),
) -> dict[str, Any]:
    """Create a new integration link for your organization. This operation is restricted to organization administrators only."""

    # Construct request model with validation
    try:
        _request = _models.PostV1IntegrationLinkRequest(
            body=_models.PostV1IntegrationLinkRequestBody(name=name, url=url, type_=type_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_integration_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/integration_link"
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
        _request = _models.GetV1IntegrationLinkIdRequest(
            path=_models.GetV1IntegrationLinkIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_integration_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/integration_link/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/integration_link/{id}"
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
    url: str | None = Field(None, description="The URL template that defines the target destination, supporting dynamic variable substitution."),
) -> dict[str, Any]:
    """Update an existing integration link's display name and URL template. Requires organization admin privileges."""

    # Construct request model with validation
    try:
        _request = _models.PutV1IntegrationLinkIdRequest(
            path=_models.PutV1IntegrationLinkIdRequestPath(id_=id_),
            body=_models.PutV1IntegrationLinkIdRequestBody(name=name, url=url)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_integration_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/integration_link/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/integration_link/{id}"
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
    """Delete an integration link from your organization. This action is restricted to organization administrators only."""

    # Construct request model with validation
    try:
        _request = _models.DeleteV1IntegrationLinkIdRequest(
            path=_models.DeleteV1IntegrationLinkIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_integration_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/integration_link/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/integration_link/{id}"
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
async def export_records(
    format_: Literal["csv", "json"] = Field(..., alias="format", description="Output file format for the export. Choose between CSV or JSON."),
    type_: Literal["leads", "contacts", "lead_opps"] = Field(..., alias="type", description="Category of records to export: leads, contacts, or opportunities associated with leads."),
    send_done_email: bool = Field(..., description="Send a confirmation email when the export completes. Set to false to skip the notification email."),
    s_query: str | None = Field(None, description="Advanced search query to filter which records to export. Uses the Advanced Filtering API syntax to narrow results."),
    results_limit: int | None = Field(None, description="Maximum number of records to include in the export. Limits the result set size."),
    sort: str | None = Field(None, description="Field and direction to sort results by. Uses the Advanced Filtering API syntax (e.g., field name with optional sort order)."),
    date_format: Literal["original", "iso8601", "excel"] | None = Field(None, description="Date format for exported date fields in CSV exports. Choose original format, ISO 8601 standard, or Excel-compatible format. Only applies to CSV format."),
    fields: list[str] | None = Field(None, description="Specific fields to include in the export. If not specified, all available fields are included. Provide as a list of field names."),
    include_activities: bool | None = Field(None, description="Include activity records in the export. Only applies when exporting leads in JSON format."),
    include_smart_fields: bool | None = Field(None, description="Include smart fields (computed/derived fields) in the export. Supported for leads in JSON format or any record type in CSV format."),
) -> dict[str, Any]:
    """Export leads, contacts, or opportunities from Close as a compressed file. The export is processed asynchronously and delivered via email with a download link."""

    # Construct request model with validation
    try:
        _request = _models.PostV1ExportLeadRequest(
            query=_models.PostV1ExportLeadRequestQuery(s_query=s_query, results_limit=results_limit, sort=sort, format_=format_, type_=type_, date_format=date_format, fields=fields, include_activities=include_activities, include_smart_fields=include_smart_fields, send_done_email=send_done_email)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for export_records: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/export/lead"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("export_records")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("export_records", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="export_records",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Exports
@mcp.tool()
async def export_opportunities(
    format_: Literal["csv", "json"] = Field(..., alias="format", description="File format for the exported data. Choose between CSV or JSON format."),
    send_done_email: bool = Field(..., description="Whether to send a confirmation email when the export completes. Defaults to true; set to false to skip the notification email."),
    params: dict[str, Any] | None = Field(None, description="Filter criteria to narrow down which opportunities to export, using the same filter parameters supported by the opportunities endpoint."),
    date_format: Literal["original", "iso8601", "excel"] | None = Field(None, description="Date format for exported dates in CSV files only. Choose from original format, ISO 8601 standard format, or Excel-compatible format. Defaults to original format."),
    fields: list[str] | None = Field(None, description="Specific fields to include in the export. If not specified, all available fields are included in the export."),
) -> dict[str, Any]:
    """Export opportunities from Close as a file in your chosen format, with optional filtering and field selection. Optionally receive a confirmation email when the export completes."""

    # Construct request model with validation
    try:
        _request = _models.PostV1ExportOpportunityRequest(
            query=_models.PostV1ExportOpportunityRequestQuery(params=params, format_=format_, date_format=date_format, fields=fields, send_done_email=send_done_email)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for export_opportunities: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/export/opportunity"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
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
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Exports
@mcp.tool()
async def get_export(id_: str = Field(..., alias="id", description="The unique identifier of the export to retrieve.")) -> dict[str, Any]:
    """Retrieve a single export by ID to check its current status or obtain a download URL for the exported data."""

    # Construct request model with validation
    try:
        _request = _models.GetV1ExportIdRequest(
            path=_models.GetV1ExportIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_export: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/export/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/export/{id}"
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
async def list_exports(limit: int | None = Field(None, alias="_limit", description="Maximum number of exports to return in the response. Useful for pagination or reducing payload size.")) -> dict[str, Any]:
    """Retrieve a list of all exports. Use the limit parameter to control the number of results returned."""

    # Construct request model with validation
    try:
        _request = _models.GetV1ExportRequest(
            query=_models.GetV1ExportRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_exports: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/export"
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
    number: str | None = Field(None, description="Filter results to phone numbers matching this specific number value."),
    is_group_number: bool | None = Field(None, description="Filter results by group number status—set to true to show only group numbers, false to show only individual numbers."),
    limit: int | None = Field(None, alias="_limit", description="Maximum number of results to return in the response. Limits the result set size."),
) -> dict[str, Any]:
    """Retrieve a list of phone numbers in your organization, with optional filtering by number value or group status."""

    # Construct request model with validation
    try:
        _request = _models.GetV1PhoneNumberRequest(
            query=_models.GetV1PhoneNumberRequestQuery(number=number, is_group_number=is_group_number, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_phone_numbers: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/phone_number/"
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
    """Retrieve a single phone number by its ID. Use this operation to fetch detailed information about a specific phone number in your account."""

    # Construct request model with validation
    try:
        _request = _models.GetV1PhoneNumberIdRequest(
            path=_models.GetV1PhoneNumberIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_phone_number: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/phone_number/{id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/phone_number/{id}/"
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
    label: str | None = Field(None, description="A descriptive label or name for this phone number."),
    forward_to: str | None = Field(None, description="The phone number to forward incoming calls to when call forwarding is enabled."),
    forward_to_enabled: bool | None = Field(None, description="Enable or disable call forwarding to the specified phone number."),
    voicemail_greeting_url: str | None = Field(None, description="HTTPS URL pointing to an MP3 file to use as the voicemail greeting message."),
) -> dict[str, Any]:
    """Update phone number settings including label, call forwarding configuration, and voicemail greeting. Requires 'Manage Group Phone Numbers' permission for group numbers; personal numbers can only be updated by their owner."""

    # Construct request model with validation
    try:
        _request = _models.PutV1PhoneNumberIdRequest(
            path=_models.PutV1PhoneNumberIdRequestPath(id_=id_),
            body=_models.PutV1PhoneNumberIdRequestBody(label=label, forward_to=forward_to, forward_to_enabled=forward_to_enabled, voicemail_greeting_url=voicemail_greeting_url)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_phone_number: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/phone_number/{id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/phone_number/{id}/"
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
    """Delete a phone number from your account. Deleting group phone numbers requires the 'Manage Group Phone Numbers' permission, while personal numbers can only be deleted by their owner."""

    # Construct request model with validation
    try:
        _request = _models.DeleteV1PhoneNumberIdRequest(
            path=_models.DeleteV1PhoneNumberIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_phone_number: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/phone_number/{id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/phone_number/{id}/"
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
    country: str = Field(..., description="Two-letter ISO country code indicating where the phone number should be rented (e.g., US, GB, DE)."),
    sharing: Literal["personal", "group"] = Field(..., description="Determines whether the phone number is assigned to an individual user (personal) or shared across a group (group). Group numbers require 'Manage Group Phone Numbers' permission."),
    prefix: str | None = Field(None, description="Optional phone number prefix or area code, excluding the country code. Allows you to request a number from a specific region or area."),
    with_sms: bool | None = Field(None, description="Optional flag to request SMS capability for the phone number. Defaults based on country support if not specified."),
    with_mms: bool | None = Field(None, description="Optional flag to request MMS capability for the phone number. Defaults based on country support if not specified."),
) -> dict[str, Any]:
    """Rent an internal phone number for personal or group use. Renting a phone number incurs a cost and requires appropriate permissions for group numbers."""

    # Construct request model with validation
    try:
        _request = _models.PostV1PhoneNumberRequestInternalRequest(
            body=_models.PostV1PhoneNumberRequestInternalRequestBody(country=country, sharing=sharing, prefix=prefix, with_sms=with_sms, with_mms=with_mms)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for rent_phone_number: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/phone_number/request/internal/"
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
    filename: str = Field(..., description="The name of the file being uploaded, including its extension (e.g., image.jpg, document.pdf)."),
    content_type: str = Field(..., description="The MIME type of the file being uploaded (e.g., image/jpeg, application/pdf, text/plain)."),
) -> dict[str, Any]:
    """Generate signed S3 upload credentials for storing a file. Returns a pre-signed upload URL, form fields for multipart upload, and a download URL for referencing the file in subsequent API calls."""

    # Construct request model with validation
    try:
        _request = _models.PostV1FilesUploadRequest(
            body=_models.PostV1FilesUploadRequestBody(filename=filename, content_type=content_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for generate_file_upload_credentials: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/files/upload"
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
    limit: int | None = Field(None, alias="_limit", description="Maximum number of comment threads to return in the response. Must be a positive integer."),
) -> dict[str, Any]:
    """Retrieve multiple comment threads with optional filtering by the objects they reference or by specific thread identifiers."""

    # Construct request model with validation
    try:
        _request = _models.GetV1CommentThreadRequest(
            query=_models.GetV1CommentThreadRequestQuery(object_ids=object_ids, ids=ids, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_comment_threads: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/comment_thread"
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
async def get_comment_thread(thread_id: str = Field(..., description="The unique identifier of the comment thread to retrieve.")) -> dict[str, Any]:
    """Retrieve a specific comment thread by its ID. Use this to fetch the full details and content of an individual discussion thread."""

    # Construct request model with validation
    try:
        _request = _models.GetV1CommentThreadThreadIdRequest(
            path=_models.GetV1CommentThreadThreadIdRequestPath(thread_id=thread_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_comment_thread: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/comment_thread/{thread_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/comment_thread/{thread_id}"
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
    object_id: str | None = Field(None, description="Filter comments by the ID of the object that was commented on. Mutually exclusive with thread_id."),
    thread_id: str | None = Field(None, description="Filter comments by the ID of the discussion thread. Mutually exclusive with object_id."),
) -> dict[str, Any]:
    """Retrieve a list of comments filtered by either the object being commented on or the discussion thread. Provide exactly one filter to retrieve relevant comments."""

    # Construct request model with validation
    try:
        _request = _models.GetV1CommentRequest(
            query=_models.GetV1CommentRequestQuery(object_id=object_id, thread_id=thread_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_comments: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/comment"
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
    object_type: str = Field(..., description="The type of object being commented on (e.g., task, document, issue). This determines where the comment will be attached."),
    object_id: str = Field(..., description="The unique identifier of the object being commented on. Must correspond to an existing object of the specified type."),
    body: str = Field(..., description="The comment text formatted as rich text. This is the content that will be displayed in the comment thread."),
) -> dict[str, Any]:
    """Create a comment on an object. If a comment thread already exists on that object, a new comment is added to the existing thread; otherwise, a new thread is created automatically."""

    # Construct request model with validation
    try:
        _request = _models.PostV1CommentRequest(
            body=_models.PostV1CommentRequestBody(object_type=object_type, object_id=object_id, body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/comment"
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
        _request = _models.GetV1CommentCommentIdRequest(
            path=_models.GetV1CommentCommentIdRequestPath(comment_id=comment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/comment/{comment_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/comment/{comment_id}"
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
    comment_id: str = Field(..., description="The unique identifier of the comment to update."),
    body: str = Field(..., description="The new comment content formatted as rich text."),
) -> dict[str, Any]:
    """Edit the body of a comment. You can only update comments that you created."""

    # Construct request model with validation
    try:
        _request = _models.PutV1CommentCommentIdRequest(
            path=_models.PutV1CommentCommentIdRequestPath(comment_id=comment_id),
            body=_models.PutV1CommentCommentIdRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/comment/{comment_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/comment/{comment_id}"
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
    """Remove a comment from a thread. The comment body is deleted but the comment object persists until all comments in the thread are removed, at which point the entire thread is deleted. Deletion permissions are based on the user's ability to delete their own or other users' activities."""

    # Construct request model with validation
    try:
        _request = _models.DeleteV1CommentCommentIdRequest(
            path=_models.DeleteV1CommentCommentIdRequestPath(comment_id=comment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/comment/{comment_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/comment/{comment_id}"
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
    """Retrieve a single event by its unique identifier. Returns event details in the standard event format."""

    # Construct request model with validation
    try:
        _request = _models.GetV1EventIdRequest(
            path=_models.GetV1EventIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_event: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/event/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/event/{id}"
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
    date_updated__lte: str | None = Field(None, description="Filter to events updated on or before this date and time (ISO 8601 format)."),
    date_updated__gte: str | None = Field(None, description="Filter to events updated on or after this date and time (ISO 8601 format)."),
    object_type: str | None = Field(None, description="Filter to events for objects of a specific type (e.g., lead, contact, deal)."),
    object_id: str | None = Field(None, description="Filter to events for a specific object by its ID. Only events directly related to this object are returned, excluding related object events."),
    action: str | None = Field(None, description="Filter to events of a specific action type (e.g., created, updated, deleted)."),
    request_id: str | None = Field(None, description="Filter to events emitted during the processing of a specific API request."),
    limit: int | None = Field(None, alias="_limit", description="Maximum number of events to return per request. Must be between 1 and 50; defaults to 50.", ge=1, le=50),
) -> dict[str, Any]:
    """Retrieve a paginated list of events from the event log, filtered by object type, action, timing, and other criteria. Events are always ordered by date with the latest first."""

    # Construct request model with validation
    try:
        _request = _models.GetV1EventRequest(
            query=_models.GetV1EventRequestQuery(date_updated__lte=date_updated__lte, date_updated__gte=date_updated__gte, object_type=object_type, object_id=object_id, action=action, request_id=request_id, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_events: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/event"
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
    """Retrieve all webhook subscriptions configured for your organization. This shows the complete list of webhook endpoints and their subscription details."""

    # Extract parameters for API call
    _http_path = "/v1/webhook"
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
    events: list[_models.PostV1WebhookBodyEventsItem] = Field(..., description="List of events to subscribe to. Each event specifies an object_type and an action to monitor. Events are processed in the order provided."),
    verify_ssl: bool | None = Field(None, description="Whether to verify the SSL certificate of the destination webhook URL. Defaults to true for secure connections."),
) -> dict[str, Any]:
    """Create a new webhook subscription to receive event notifications at a specified URL. The webhook will send POST requests for each subscribed event."""

    # Construct request model with validation
    try:
        _request = _models.PostV1WebhookRequest(
            body=_models.PostV1WebhookRequestBody(url=url, events=events, verify_ssl=verify_ssl)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_webhook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/webhook"
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
    """Retrieve the details of a specific webhook subscription, including its configuration and status."""

    # Construct request model with validation
    try:
        _request = _models.GetV1WebhookIdRequest(
            path=_models.GetV1WebhookIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_webhook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/webhook/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/webhook/{id}"
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
    url: str | None = Field(None, description="The destination URL where webhook events will be sent. Must be a valid URI format."),
    events: list[_models.PutV1WebhookIdBodyEventsItem] | None = Field(None, description="A list of events to subscribe to. Each event specifies an object type and an action to trigger the webhook notification."),
    verify_ssl: bool | None = Field(None, description="Whether to verify the SSL certificate when sending webhook requests to the destination URL. Enable for production environments to ensure secure connections."),
) -> dict[str, Any]:
    """Update an existing webhook subscription with new configuration. Only provided parameters will be modified, allowing partial updates to the webhook's URL, subscribed events, or SSL verification settings."""

    # Construct request model with validation
    try:
        _request = _models.PutV1WebhookIdRequest(
            path=_models.PutV1WebhookIdRequestPath(id_=id_),
            body=_models.PutV1WebhookIdRequestBody(url=url, events=events, verify_ssl=verify_ssl)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_webhook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/webhook/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/webhook/{id}"
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
    """Remove a webhook subscription to stop receiving event notifications at the configured endpoint."""

    # Construct request model with validation
    try:
        _request = _models.DeleteV1WebhookIdRequest(
            path=_models.DeleteV1WebhookIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_webhook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/webhook/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/webhook/{id}"
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
    """Retrieve all scheduling links created by the authenticated user. Scheduling links allow others to book time with you based on your availability."""

    # Extract parameters for API call
    _http_path = "/v1/scheduling_link"
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
    name: str = Field(..., description="A descriptive name for the scheduling link to help identify its purpose or audience."),
    url: str = Field(..., description="The external URL where the scheduling link points to, typically a calendar or booking platform URL."),
    description: str | None = Field(None, description="An optional description providing additional context or details about the scheduling link's purpose."),
) -> dict[str, Any]:
    """Create a new scheduling link that can be shared with users to access your availability and book meetings. This generates a unique scheduling link with a custom name and optional description."""

    # Construct request model with validation
    try:
        _request = _models.PostV1SchedulingLinkRequest(
            body=_models.PostV1SchedulingLinkRequestBody(name=name, url=url, description=description)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_scheduling_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/scheduling_link"
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
    """Retrieve a scheduling link by its unique identifier. Use this to fetch details about a specific user's scheduling link."""

    # Construct request model with validation
    try:
        _request = _models.GetV1SchedulingLinkIdRequest(
            path=_models.GetV1SchedulingLinkIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_scheduling_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/scheduling_link/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/scheduling_link/{id}"
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
    name: str | None = Field(None, description="A display name for the scheduling link to help identify it."),
    url: str | None = Field(None, description="The external URL where the scheduling link is hosted or accessible."),
    description: str | None = Field(None, description="A detailed description explaining the purpose or details of the scheduling link."),
    source_id: str | None = Field(None, description="The identifier for this scheduling link at its source system or origin."),
    source_type: str | None = Field(None, description="A short descriptor categorizing the type or source of the scheduling link (e.g., 'calendly', 'acuity', 'custom')."),
    duration_in_minutes: int | None = Field(None, description="The default duration in minutes for meetings scheduled through this link."),
) -> dict[str, Any]:
    """Update an existing user scheduling link with new details such as name, URL, description, and meeting duration. This allows you to modify the properties of a scheduling link that users can access to book meetings."""

    # Construct request model with validation
    try:
        _request = _models.PutV1SchedulingLinkIdRequest(
            path=_models.PutV1SchedulingLinkIdRequestPath(id_=id_),
            body=_models.PutV1SchedulingLinkIdRequestBody(name=name, url=url, description=description, source_id=source_id, source_type=source_type, duration_in_minutes=duration_in_minutes)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_scheduling_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/scheduling_link/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/scheduling_link/{id}"
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
    """Delete a scheduling link by its ID. This removes the user's scheduling link and makes it unavailable for scheduling."""

    # Construct request model with validation
    try:
        _request = _models.DeleteV1SchedulingLinkIdRequest(
            path=_models.DeleteV1SchedulingLinkIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_scheduling_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/scheduling_link/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/scheduling_link/{id}"
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
async def create_or_update_scheduling_link(
    source_id: str = Field(..., description="Unique identifier from your integrating application used to identify and deduplicate this scheduling link."),
    name: str | None = Field(None, description="Display name for the scheduling link."),
    url: str | None = Field(None, description="Public-facing URL where users can access the scheduling link."),
    description: str | None = Field(None, description="Additional details or context about the scheduling link's purpose."),
    source_type: str | None = Field(None, description="Category or type classification for the scheduling link (e.g., 'meeting', 'consultation', 'demo')."),
    duration_in_minutes: int | None = Field(None, description="Default meeting duration in minutes for appointments scheduled through this link."),
) -> dict[str, Any]:
    """Create a new scheduling link or update an existing one through your OAuth application. The source_id field is used to identify and merge duplicate resources across integrations."""

    # Construct request model with validation
    try:
        _request = _models.PostV1SchedulingLinkIntegrationRequest(
            body=_models.PostV1SchedulingLinkIntegrationRequestBody(name=name, url=url, description=description, source_id=source_id, source_type=source_type, duration_in_minutes=duration_in_minutes)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_or_update_scheduling_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/scheduling_link/integration"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_or_update_scheduling_link")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_or_update_scheduling_link", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_or_update_scheduling_link",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Scheduling Links
@mcp.tool()
async def delete_scheduling_link_integration(source_id: str = Field(..., description="The unique source identifier of the scheduling link to delete. This ID was assigned when the scheduling link was originally created by your OAuth application.")) -> dict[str, Any]:
    """Delete a scheduling link that was created by your OAuth application using its source ID. This operation requires OAuth authentication and will permanently remove the scheduling link."""

    # Construct request model with validation
    try:
        _request = _models.DeleteV1SchedulingLinkIntegrationSourceIdRequest(
            path=_models.DeleteV1SchedulingLinkIntegrationSourceIdRequestPath(source_id=source_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_scheduling_link_integration: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/scheduling_link/integration/{source_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/scheduling_link/integration/{source_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_scheduling_link_integration")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_scheduling_link_integration", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_scheduling_link_integration",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Scheduling Links
@mcp.tool()
async def list_scheduling_links_shared() -> dict[str, Any]:
    """Retrieve all shared scheduling links available in your account. Use this to view and manage scheduling links that have been created for sharing with others."""

    # Extract parameters for API call
    _http_path = "/v1/shared_scheduling_link"
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
async def create_scheduling_link_shared(body: dict[str, Any] = Field(..., description="Configuration object for the scheduling link, including settings such as availability, duration, and access permissions.")) -> dict[str, Any]:
    """Create a new shared scheduling link that allows others to view and book time slots on your calendar."""

    # Construct request model with validation
    try:
        _request = _models.PostV1SharedSchedulingLinkRequest(
            body=_models.PostV1SharedSchedulingLinkRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_scheduling_link_shared: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/shared_scheduling_link"
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
    """Retrieve a shared scheduling link by its unique identifier. Use this to fetch the details and configuration of a previously created scheduling link."""

    # Construct request model with validation
    try:
        _request = _models.GetV1SharedSchedulingLinkIdRequest(
            path=_models.GetV1SharedSchedulingLinkIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_scheduling_link_shared: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/shared_scheduling_link/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/shared_scheduling_link/{id}"
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
    body: dict[str, Any] = Field(..., description="The updated scheduling link configuration containing the properties to modify."),
) -> dict[str, Any]:
    """Update the configuration and settings of an existing shared scheduling link. Modify properties such as availability, restrictions, or metadata associated with the link."""

    # Construct request model with validation
    try:
        _request = _models.PutV1SharedSchedulingLinkIdRequest(
            path=_models.PutV1SharedSchedulingLinkIdRequestPath(id_=id_),
            body=_models.PutV1SharedSchedulingLinkIdRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_scheduling_link_shared: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/shared_scheduling_link/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/shared_scheduling_link/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
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
    """Delete a shared scheduling link by its ID. This removes the link and prevents further access to the associated scheduling interface."""

    # Construct request model with validation
    try:
        _request = _models.DeleteV1SharedSchedulingLinkIdRequest(
            path=_models.DeleteV1SharedSchedulingLinkIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_scheduling_link_shared: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/shared_scheduling_link/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/shared_scheduling_link/{id}"
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
async def map_shared_scheduling_link(
    shared_scheduling_link_id: str = Field(..., description="The unique identifier of the shared scheduling link to be mapped."),
    user_scheduling_link_id: str | None = Field(None, description="The unique identifier of a user scheduling link to map the shared link to. Either this or a URL must be provided."),
    url: str | None = Field(None, description="A valid URI to map the shared link to. Either this or a user scheduling link ID must be provided."),
) -> dict[str, Any]:
    """Associate a shared scheduling link with either a user scheduling link or a custom URL to enable scheduling access through the mapped destination."""

    # Construct request model with validation
    try:
        _request = _models.PostV1SharedSchedulingLinkAssociationRequest(
            body=_models.PostV1SharedSchedulingLinkAssociationRequestBody(shared_scheduling_link_id=shared_scheduling_link_id, user_scheduling_link_id=user_scheduling_link_id, url=url)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for map_shared_scheduling_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/shared_scheduling_link_association"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("map_shared_scheduling_link")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("map_shared_scheduling_link", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="map_shared_scheduling_link",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Scheduling Links
@mcp.tool()
async def unmap_shared_scheduling_link(shared_scheduling_link_id: str = Field(..., description="The unique identifier of the shared scheduling link to unmap from its current association.")) -> dict[str, Any]:
    """Remove the association between a shared scheduling link and its mapped user scheduling link or URL, effectively disabling the shared link's access."""

    # Construct request model with validation
    try:
        _request = _models.PostV1SharedSchedulingLinkAssociationUnmapRequest(
            body=_models.PostV1SharedSchedulingLinkAssociationUnmapRequestBody(shared_scheduling_link_id=shared_scheduling_link_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for unmap_shared_scheduling_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/shared_scheduling_link_association/unmap/"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("unmap_shared_scheduling_link")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("unmap_shared_scheduling_link", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="unmap_shared_scheduling_link",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Fields
@mcp.tool()
async def list_lead_custom_fields(limit: int | None = Field(None, alias="_limit", description="Maximum number of lead custom fields to return in the response. Omit to retrieve all available custom fields.")) -> dict[str, Any]:
    """Retrieve all custom fields configured for leads in your organization. Use the optional limit parameter to control the number of results returned."""

    # Construct request model with validation
    try:
        _request = _models.GetV1CustomFieldLeadRequest(
            query=_models.GetV1CustomFieldLeadRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_lead_custom_fields: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/custom_field/lead"
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
    name: str = Field(..., description="The display name for the custom field that will appear in the lead interface."),
    type_: str = Field(..., alias="type", description="The data type of the custom field (e.g., text, number, date, choice) that determines how the field stores and validates data."),
    accepts_multiple_values: bool | None = Field(None, description="When enabled, allows the field to store multiple values instead of a single value."),
    editable_roles: list[str] | None = Field(None, description="A list of user roles that have permission to edit this custom field. If not specified, defaults to all roles or system defaults."),
    options: list[dict[str, Any]] | None = Field(None, description="An array of predefined choices available for selection-type fields. Each option represents a selectable value in the field."),
) -> dict[str, Any]:
    """Create a new custom field for leads with configurable type, multi-value support, and role-based edit permissions."""

    # Construct request model with validation
    try:
        _request = _models.PostV1CustomFieldLeadRequest(
            body=_models.PostV1CustomFieldLeadRequestBody(name=name, type_=type_, accepts_multiple_values=accepts_multiple_values, editable_roles=editable_roles, options=options)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_lead_custom_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/custom_field/lead"
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
    """Retrieve the details of a specific custom field associated with a lead. Use this to access custom field configuration and values for a particular lead."""

    # Construct request model with validation
    try:
        _request = _models.GetV1CustomFieldLeadIdRequest(
            path=_models.GetV1CustomFieldLeadIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_lead_custom_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/custom_field/lead/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/custom_field/lead/{id}"
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
    name: str | None = Field(None, description="The new name for the custom field."),
    accepts_multiple_values: bool | None = Field(None, description="Whether this field should accept multiple values (true) or a single value (false)."),
    editable_roles: list[str] | None = Field(None, description="Array of role identifiers that are permitted to edit this field's values. If specified, only users with these roles can modify the field."),
    options: list[dict[str, Any]] | None = Field(None, description="Array of updated choice options for fields with a choice/select type. Each option should include the option identifier and label."),
) -> dict[str, Any]:
    """Update an existing Lead Custom Field by modifying its name, value acceptance settings, role-based edit permissions, or choice options."""

    # Construct request model with validation
    try:
        _request = _models.PutV1CustomFieldLeadCustomFieldIdRequest(
            path=_models.PutV1CustomFieldLeadCustomFieldIdRequestPath(custom_field_id=custom_field_id),
            body=_models.PutV1CustomFieldLeadCustomFieldIdRequestBody(name=name, accepts_multiple_values=accepts_multiple_values, editable_roles=editable_roles, options=options)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_lead_custom_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/custom_field/lead/{custom_field_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/custom_field/lead/{custom_field_id}"
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
async def delete_lead_custom_field(custom_field_id: str = Field(..., description="The unique identifier of the lead custom field to delete.")) -> dict[str, Any]:
    """Permanently delete a custom field from your Lead records. The field will be immediately removed from all Lead API responses and cannot be recovered."""

    # Construct request model with validation
    try:
        _request = _models.DeleteV1CustomFieldLeadCustomFieldIdRequest(
            path=_models.DeleteV1CustomFieldLeadCustomFieldIdRequestPath(custom_field_id=custom_field_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_lead_custom_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/custom_field/lead/{custom_field_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/custom_field/lead/{custom_field_id}"
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
async def list_contact_custom_fields(limit: int | None = Field(None, alias="_limit", description="Maximum number of custom fields to return in the response. Omit to retrieve all available custom fields.")) -> dict[str, Any]:
    """Retrieve all custom fields configured for contacts in your organization. Use the optional limit parameter to control the number of results returned."""

    # Construct request model with validation
    try:
        _request = _models.GetV1CustomFieldContactRequest(
            query=_models.GetV1CustomFieldContactRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_contact_custom_fields: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/custom_field/contact/"
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
    name: str = Field(..., description="The display name for the custom field that will appear in contact forms and records."),
    type_: str = Field(..., alias="type", description="The data type of the custom field (e.g., text, number, date, choice), which determines how values are stored and validated."),
    accepts_multiple_values: bool | None = Field(None, description="When enabled, allows a single contact to have multiple values for this field; when disabled, only one value is permitted."),
    restricted_to_roles: bool | None = Field(None, description="When enabled, restricts editing permissions to users with specific roles; when disabled, all users with contact access can edit the field."),
    options: list[dict[str, Any]] | None = Field(None, description="A list of predefined values available for selection when the field type is choice-based. Order is preserved for display purposes."),
) -> dict[str, Any]:
    """Create a new custom field for contacts with configurable type, value constraints, and role-based access controls. This allows you to extend contact records with domain-specific attributes."""

    # Construct request model with validation
    try:
        _request = _models.PostV1CustomFieldContactRequest(
            body=_models.PostV1CustomFieldContactRequestBody(name=name, type_=type_, accepts_multiple_values=accepts_multiple_values, restricted_to_roles=restricted_to_roles, options=options)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_contact_custom_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/custom_field/contact/"
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
    """Retrieve the details of a specific custom field associated with a contact. Use this to access custom field configuration and values for a contact record."""

    # Construct request model with validation
    try:
        _request = _models.GetV1CustomFieldContactIdRequest(
            path=_models.GetV1CustomFieldContactIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_contact_custom_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/custom_field/contact/{id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/custom_field/contact/{id}/"
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
    name: str | None = Field(None, description="The new name for the custom field."),
    accepts_multiple_values: bool | None = Field(None, description="Whether this field should accept multiple values (true) or a single value (false)."),
    restricted_to_roles: bool | None = Field(None, description="Whether editing this field's values should be restricted to users with specific roles (true) or available to all users (false)."),
    options: list[dict[str, Any]] | None = Field(None, description="Array of available options for choice-type fields. Each option represents a selectable value that users can assign to this field."),
) -> dict[str, Any]:
    """Update an existing contact custom field by modifying its name, type configuration, multi-value support, role-based access restrictions, or choice options."""

    # Construct request model with validation
    try:
        _request = _models.PutV1CustomFieldContactCustomFieldIdRequest(
            path=_models.PutV1CustomFieldContactCustomFieldIdRequestPath(custom_field_id=custom_field_id),
            body=_models.PutV1CustomFieldContactCustomFieldIdRequestBody(name=name, accepts_multiple_values=accepts_multiple_values, restricted_to_roles=restricted_to_roles, options=options)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_contact_custom_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/custom_field/contact/{custom_field_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/custom_field/contact/{custom_field_id}/"
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
    """Permanently delete a custom field from your Contact records. The field will be immediately removed from all Contact API responses."""

    # Construct request model with validation
    try:
        _request = _models.DeleteV1CustomFieldContactCustomFieldIdRequest(
            path=_models.DeleteV1CustomFieldContactCustomFieldIdRequestPath(custom_field_id=custom_field_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_contact_custom_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/custom_field/contact/{custom_field_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/custom_field/contact/{custom_field_id}/"
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

# Tags: Custom Fields
@mcp.tool()
async def list_opportunity_custom_fields(limit: int | None = Field(None, alias="_limit", description="Maximum number of custom field records to return in the response. Useful for pagination or limiting result set size.")) -> dict[str, Any]:
    """Retrieve all custom fields configured for opportunities in your organization. Use the limit parameter to control the number of results returned."""

    # Construct request model with validation
    try:
        _request = _models.GetV1CustomFieldOpportunityRequest(
            query=_models.GetV1CustomFieldOpportunityRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_opportunity_custom_fields: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/custom_field/opportunity/"
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
async def create_opportunity_custom_field(body: dict[str, Any] = Field(..., description="The custom field configuration object containing the field definition, name, type, and any applicable settings for the new Opportunity custom field.")) -> dict[str, Any]:
    """Create a new custom field for Opportunity records. Custom fields allow you to extend the standard Opportunity data model with additional attributes tailored to your business needs."""

    # Construct request model with validation
    try:
        _request = _models.PostV1CustomFieldOpportunityRequest(
            body=_models.PostV1CustomFieldOpportunityRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_opportunity_custom_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/custom_field/opportunity/"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
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

# Tags: Custom Fields
@mcp.tool()
async def get_opportunity_custom_field(id_: str = Field(..., alias="id", description="The unique identifier of the custom field to retrieve. This ID specifies which custom field's details should be fetched.")) -> dict[str, Any]:
    """Retrieve detailed information about a specific custom field associated with an opportunity. Use this to access custom field configurations and values linked to a particular opportunity record."""

    # Construct request model with validation
    try:
        _request = _models.GetV1CustomFieldOpportunityIdRequest(
            path=_models.GetV1CustomFieldOpportunityIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_opportunity_custom_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/custom_field/opportunity/{id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/custom_field/opportunity/{id}/"
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

# Tags: Custom Fields
@mcp.tool()
async def update_opportunity_custom_field(
    custom_field_id: str = Field(..., description="The unique identifier of the custom field to update."),
    body: dict[str, Any] = Field(..., description="The updated custom field configuration, including name, type, multi-value setting, role restrictions, and choice options if applicable."),
) -> dict[str, Any]:
    """Update an existing Opportunity custom field, including its name, data type, multi-value support, role-based editing restrictions, and choice options."""

    # Construct request model with validation
    try:
        _request = _models.PutV1CustomFieldOpportunityCustomFieldIdRequest(
            path=_models.PutV1CustomFieldOpportunityCustomFieldIdRequestPath(custom_field_id=custom_field_id),
            body=_models.PutV1CustomFieldOpportunityCustomFieldIdRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_opportunity_custom_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/custom_field/opportunity/{custom_field_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/custom_field/opportunity/{custom_field_id}/"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
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

# Tags: Custom Fields
@mcp.tool()
async def delete_opportunity_custom_field(custom_field_id: str = Field(..., description="The unique identifier of the custom field to delete.")) -> dict[str, Any]:
    """Permanently delete a custom field from Opportunities. The field will be immediately removed from all Opportunity API responses and cannot be recovered."""

    # Construct request model with validation
    try:
        _request = _models.DeleteV1CustomFieldOpportunityCustomFieldIdRequest(
            path=_models.DeleteV1CustomFieldOpportunityCustomFieldIdRequestPath(custom_field_id=custom_field_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_opportunity_custom_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/custom_field/opportunity/{custom_field_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/custom_field/opportunity/{custom_field_id}/"
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
async def list_activity_custom_fields(limit: int | None = Field(None, alias="_limit", description="Maximum number of results to return in a single response for pagination purposes.")) -> dict[str, Any]:
    """Retrieve all Activity Custom Fields configured for your organization. Supports optional pagination to control the number of results returned."""

    # Construct request model with validation
    try:
        _request = _models.GetV1CustomFieldActivityRequest(
            query=_models.GetV1CustomFieldActivityRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_activity_custom_fields: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/custom_field/activity/"
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
    name: str = Field(..., description="The display name for the custom field."),
    type_: str = Field(..., alias="type", description="The data type of the field, such as text, number, date, or choices. The type determines how the field stores and validates data."),
    custom_activity_type_id: str = Field(..., description="The unique identifier of the Custom Activity Type that this field belongs to."),
    required: bool | None = Field(None, description="Whether this field must be populated before the activity can be published."),
    accepts_multiple_values: bool | None = Field(None, description="Whether this field can store multiple values simultaneously."),
    options: list[dict[str, Any]] | None = Field(None, description="A list of predefined options for choice-type fields. Required when the field type is set to choices."),
) -> dict[str, Any]:
    """Create a new custom field for Activity types. The field will be associated with a specific Custom Activity Type and can be configured as required or to accept multiple values."""

    # Construct request model with validation
    try:
        _request = _models.PostV1CustomFieldActivityRequest(
            body=_models.PostV1CustomFieldActivityRequestBody(name=name, type_=type_, custom_activity_type_id=custom_activity_type_id, required=required, accepts_multiple_values=accepts_multiple_values, options=options)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_activity_custom_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/custom_field/activity/"
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
    """Retrieve the details of a specific Activity Custom Field by its ID. Use this to fetch configuration and metadata for a custom field associated with activities."""

    # Construct request model with validation
    try:
        _request = _models.GetV1CustomFieldActivityIdRequest(
            path=_models.GetV1CustomFieldActivityIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_activity_custom_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/custom_field/activity/{id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/custom_field/activity/{id}/"
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
    name: str | None = Field(None, description="The new name for the custom field."),
    required: bool | None = Field(None, description="Whether this field must be populated when creating or editing activities."),
    accepts_multiple_values: bool | None = Field(None, description="Whether users can assign multiple values to this field."),
    restricted_to_roles: list[str] | None = Field(None, description="List of role identifiers that are permitted to edit this field. If specified, only users with these roles can modify the field value."),
    options: list[dict[str, Any]] | None = Field(None, description="Updated list of available options for choice-type fields. Each option should include its identifier and display label."),
) -> dict[str, Any]:
    """Update an existing Activity Custom Field by modifying its name, required status, multi-value acceptance, role-based editing restrictions, or choice field options. The field type and associated activity type cannot be changed."""

    # Construct request model with validation
    try:
        _request = _models.PutV1CustomFieldActivityCustomFieldIdRequest(
            path=_models.PutV1CustomFieldActivityCustomFieldIdRequestPath(custom_field_id=custom_field_id),
            body=_models.PutV1CustomFieldActivityCustomFieldIdRequestBody(name=name, required=required, accepts_multiple_values=accepts_multiple_values, restricted_to_roles=restricted_to_roles, options=options)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_activity_custom_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/custom_field/activity/{custom_field_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/custom_field/activity/{custom_field_id}/"
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
        _request = _models.DeleteV1CustomFieldActivityCustomFieldIdRequest(
            path=_models.DeleteV1CustomFieldActivityCustomFieldIdRequestPath(custom_field_id=custom_field_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_activity_custom_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/custom_field/activity/{custom_field_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/custom_field/activity/{custom_field_id}/"
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
    """Retrieve all custom fields associated with custom objects in your organization. This operation returns the complete list of custom fields configured for custom object types."""

    # Extract parameters for API call
    _http_path = "/v1/custom_field/custom_object_type"
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
    custom_object_type_id: str = Field(..., description="The unique identifier of the Custom Object Type that this field will belong to."),
    required: bool | None = Field(None, description="Whether this field must be populated when saving a custom object instance. When enabled, the field becomes mandatory for object creation and updates."),
) -> dict[str, Any]:
    """Create a new custom field for a specific Custom Object Type. Custom fields extend the data structure of custom objects with additional attributes and validation rules."""

    # Construct request model with validation
    try:
        _request = _models.PostV1CustomFieldCustomObjectTypeRequest(
            body=_models.PostV1CustomFieldCustomObjectTypeRequestBody(custom_object_type_id=custom_object_type_id, required=required)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_custom_object_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/custom_field/custom_object_type"
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
    """Retrieve detailed information about a specific custom field associated with a custom object type."""

    # Construct request model with validation
    try:
        _request = _models.GetV1CustomFieldCustomObjectTypeIdRequest(
            path=_models.GetV1CustomFieldCustomObjectTypeIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_custom_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/custom_field/custom_object_type/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/custom_field/custom_object_type/{id}"
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
async def update_custom_object_field(
    custom_field_id: str = Field(..., description="The unique identifier of the custom field to update."),
    body: dict[str, Any] = Field(..., description="The field configuration updates to apply, including name, multi-value flag, required flag, role restrictions, and choice options."),
) -> dict[str, Any]:
    """Update an existing custom field for a custom object type. Modify field properties such as name, multi-value support, required status, role-based editing restrictions, or choice options. The custom object type and field type cannot be changed after creation."""

    # Construct request model with validation
    try:
        _request = _models.PutV1CustomFieldCustomObjectTypeCustomFieldIdRequest(
            path=_models.PutV1CustomFieldCustomObjectTypeCustomFieldIdRequestPath(custom_field_id=custom_field_id),
            body=_models.PutV1CustomFieldCustomObjectTypeCustomFieldIdRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_custom_object_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/custom_field/custom_object_type/{custom_field_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/custom_field/custom_object_type/{custom_field_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_custom_object_field")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_custom_object_field", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_custom_object_field",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Fields
@mcp.tool()
async def delete_custom_object_field(custom_field_id: str = Field(..., description="The unique identifier of the custom field to delete.")) -> dict[str, Any]:
    """Permanently delete a custom field from your Custom Object schema. The field will be immediately removed from all Custom Object API responses."""

    # Construct request model with validation
    try:
        _request = _models.DeleteV1CustomFieldCustomObjectTypeCustomFieldIdRequest(
            path=_models.DeleteV1CustomFieldCustomObjectTypeCustomFieldIdRequestPath(custom_field_id=custom_field_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_custom_object_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/custom_field/custom_object_type/{custom_field_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/custom_field/custom_object_type/{custom_field_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_custom_object_field")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_custom_object_field", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_custom_object_field",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Fields
@mcp.tool()
async def list_shared_custom_fields() -> dict[str, Any]:
    """Retrieve all shared custom fields available across your organization. These fields can be used across multiple projects and resources."""

    # Extract parameters for API call
    _http_path = "/v1/custom_field/shared"
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
    name: str = Field(..., description="The display name for the custom field. This name will be visible when applying the field to objects."),
    type_: str = Field(..., alias="type", description="The data type of the custom field, which determines what kind of values it can store (e.g., text, number, date, dropdown)."),
    associations: list[dict[str, Any]] | None = Field(None, description="A list of object types this custom field can be applied to. Specify which objects in your system should have access to this field."),
) -> dict[str, Any]:
    """Create a new shared custom field that can be reused across your organization. Shared custom fields are available for use on specified object types throughout your workspace."""

    # Construct request model with validation
    try:
        _request = _models.PostV1CustomFieldSharedRequest(
            body=_models.PostV1CustomFieldSharedRequestBody(name=name, type_=type_, associations=associations)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_shared_custom_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/custom_field/shared"
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
    name: str | None = Field(None, description="The new name for the custom field. If provided, replaces the current name."),
    choices: list[str] | None = Field(None, description="Updated list of options for a choices field type. Each item represents a selectable choice option. Only applicable to fields with type 'choices'."),
) -> dict[str, Any]:
    """Update a shared custom field by renaming it or modifying its choice options. The field type cannot be changed after creation."""

    # Construct request model with validation
    try:
        _request = _models.PutV1CustomFieldSharedCustomFieldIdRequest(
            path=_models.PutV1CustomFieldSharedCustomFieldIdRequestPath(custom_field_id=custom_field_id),
            body=_models.PutV1CustomFieldSharedCustomFieldIdRequestBody(name=name, choices=choices)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_shared_custom_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/custom_field/shared/{custom_field_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/custom_field/shared/{custom_field_id}"
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
async def delete_shared_custom_field(custom_field_id: str = Field(..., description="The unique identifier of the shared custom field to delete.")) -> dict[str, Any]:
    """Permanently delete a shared custom field. The field will be immediately removed from all objects it was assigned to."""

    # Construct request model with validation
    try:
        _request = _models.DeleteV1CustomFieldSharedCustomFieldIdRequest(
            path=_models.DeleteV1CustomFieldSharedCustomFieldIdRequestPath(custom_field_id=custom_field_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_shared_custom_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/custom_field/shared/{custom_field_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/custom_field/shared/{custom_field_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_shared_custom_field")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_shared_custom_field", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_shared_custom_field",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Fields
@mcp.tool()
async def associate_shared_custom_field(
    shared_custom_field_id: str = Field(..., description="The unique identifier of the Shared Custom Field to associate."),
    object_type: Literal["lead", "contact", "opportunity", "custom_activity_type", "custom_object_type"] = Field(..., description="The object type to associate the field with. Must be one of: lead, contact, opportunity, custom_activity_type, or custom_object_type."),
    custom_activity_type_id: str | None = Field(None, description="The ID of the Custom Activity Type being associated. Required only when object_type is set to custom_activity_type."),
    custom_object_type_id: str | None = Field(None, description="The ID of the Custom Object Type being associated. Required only when object_type is set to custom_object_type."),
    editable_with_roles: list[str] | None = Field(None, description="A list of Role IDs that are permitted to edit the values of this field on the associated object type. If not specified, all roles may edit the field."),
    required: bool | None = Field(None, description="Whether a value must be provided for this field on the associated object. Only applicable when object_type is custom_activity_type or custom_object_type."),
) -> dict[str, Any]:
    """Associate a Shared Custom Field with a specific object type (Lead, Contact, Opportunity, or custom types) to enable the field for use on that object type. Once associated, the field can be set and managed on instances of that object type."""

    # Construct request model with validation
    try:
        _request = _models.PostV1CustomFieldSharedSharedCustomFieldIdAssociationRequest(
            path=_models.PostV1CustomFieldSharedSharedCustomFieldIdAssociationRequestPath(shared_custom_field_id=shared_custom_field_id),
            body=_models.PostV1CustomFieldSharedSharedCustomFieldIdAssociationRequestBody(object_type=object_type, custom_activity_type_id=custom_activity_type_id, custom_object_type_id=custom_object_type_id, editable_with_roles=editable_with_roles, required=required)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for associate_shared_custom_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/custom_field/shared/{shared_custom_field_id}/association", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/custom_field/shared/{shared_custom_field_id}/association"
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
    shared_custom_field_id: str = Field(..., description="The unique identifier of the shared custom field being updated."),
    object_type: str = Field(..., description="The type of object this association applies to: standard types (lead, contact, opportunity) or custom types using the format custom_activity_type/{id} or custom_object_type/{id}."),
    editable_with_roles: list[str] | None = Field(None, description="A list of role identifiers that are permitted to edit this custom field. Omit to leave unchanged."),
    required: bool | None = Field(None, description="Whether this custom field must be completed for the specified object type. Omit to leave unchanged."),
) -> dict[str, Any]:
    """Update an existing Shared Custom Field Association by modifying its editability permissions and requirement status. Specify which roles can edit the field and whether it should be required for the given object type."""

    # Construct request model with validation
    try:
        _request = _models.PutV1CustomFieldSharedSharedCustomFieldIdAssociationObjectTypeRequest(
            path=_models.PutV1CustomFieldSharedSharedCustomFieldIdAssociationObjectTypeRequestPath(shared_custom_field_id=shared_custom_field_id, object_type=object_type),
            body=_models.PutV1CustomFieldSharedSharedCustomFieldIdAssociationObjectTypeRequestBody(editable_with_roles=editable_with_roles, required=required)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_shared_custom_field_association: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/custom_field/shared/{shared_custom_field_id}/association/{object_type}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/custom_field/shared/{shared_custom_field_id}/association/{object_type}"
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
async def remove_custom_field_association(
    custom_field_id: str = Field(..., description="The unique identifier of the shared custom field to disassociate."),
    object_type: str = Field(..., description="The object type to disassociate from, specified as either a standard type (lead, contact, opportunity, custom_activity_type) or a custom type reference (custom_object_type/<cotype_id>)."),
) -> dict[str, Any]:
    """Remove a shared custom field from a specific object type (Lead, Contact, Opportunity, Custom Activity Type, or Custom Object Type). The field will be immediately removed from all objects of that type."""

    # Construct request model with validation
    try:
        _request = _models.DeleteV1CustomFieldSharedCustomFieldIdAssociationObjectTypeRequest(
            path=_models.DeleteV1CustomFieldSharedCustomFieldIdAssociationObjectTypeRequestPath(custom_field_id=custom_field_id, object_type=object_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_custom_field_association: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/custom_field/shared/{custom_field_id}/association/{object_type}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/custom_field/shared/{custom_field_id}/association/{object_type}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_custom_field_association")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_custom_field_association", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_custom_field_association",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Fields
@mcp.tool()
async def get_custom_field_schema(object_type: Literal["lead", "contact", "opportunity"] = Field(..., description="The type of object for which to retrieve the custom field schema. Must be one of: lead, contact, or opportunity.")) -> dict[str, Any]:
    """Retrieve the custom field schema for a specified object type, including all regular and shared custom fields in their defined order."""

    # Construct request model with validation
    try:
        _request = _models.GetV1CustomFieldSchemaObjectTypeRequest(
            path=_models.GetV1CustomFieldSchemaObjectTypeRequestPath(object_type=object_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_custom_field_schema: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/custom_field_schema/{object_type}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/custom_field_schema/{object_type}"
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
    object_type: Literal["lead", "contact", "opportunity"] = Field(..., description="The object type for which to reorder custom fields. Must be one of: lead, contact, or opportunity."),
    fields: list[_models.PutV1CustomFieldSchemaObjectTypeBodyFieldsItem] = Field(..., description="An ordered list of field objects containing their IDs. The order of this list determines the new field sequence; any fields omitted from this list will be appended after the specified fields."),
) -> dict[str, Any]:
    """Reorder custom fields within a schema by specifying field IDs in the desired order. Fields not included in the list are automatically appended to the end."""

    # Construct request model with validation
    try:
        _request = _models.PutV1CustomFieldSchemaObjectTypeRequest(
            path=_models.PutV1CustomFieldSchemaObjectTypeRequestPath(object_type=object_type),
            body=_models.PutV1CustomFieldSchemaObjectTypeRequestBody(fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for reorder_custom_fields: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/custom_field_schema/{object_type}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/custom_field_schema/{object_type}"
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
    object_type: Literal["lead", "contact"] = Field(..., description="The type of object to enrich, either a lead or contact."),
    object_id: str = Field(..., description="The unique identifier of the lead or contact record to enrich."),
    field_id: str = Field(..., description="The unique identifier of the custom field to enrich."),
    set_new_value: bool | None = Field(None, description="Whether to automatically update the field with the enriched value. Defaults to true."),
    overwrite_existing_value: bool | None = Field(None, description="Whether to overwrite the field if it already contains a value. Defaults to false, preserving existing data."),
) -> dict[str, Any]:
    """Enrich a specific field on a lead or contact using AI analysis. The operation intelligently populates or enhances the field by analyzing existing data and external sources, then returns the enriched value."""

    # Construct request model with validation
    try:
        _request = _models.PostV1EnrichFieldRequest(
            query=_models.PostV1EnrichFieldRequestQuery(organization_id=organization_id, object_type=object_type, object_id=object_id, field_id=field_id, set_new_value=set_new_value, overwrite_existing_value=overwrite_existing_value)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for enrich_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/enrich_field"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
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
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Activities
@mcp.tool()
async def list_custom_activity_types() -> dict[str, Any]:
    """Retrieve all Custom Activity Types configured for your organization, including their associated Custom Field metadata. Use this to understand available activity types and their field structures."""

    # Extract parameters for API call
    _http_path = "/v1/custom_activity"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_custom_activity_types")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_custom_activity_types", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_custom_activity_types",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Activities
@mcp.tool()
async def create_custom_activity_type(
    name: str = Field(..., description="The display name for the custom activity type. This identifies the type throughout the system."),
    description: str | None = Field(None, description="A detailed explanation of the custom activity type's purpose and usage."),
    api_create_only: bool | None = Field(None, description="When enabled, restricts creation of this activity type to API requests only, preventing creation through the user interface."),
    editable_with_roles: list[str] | None = Field(None, description="A list of user roles that have permission to edit this activity type. Roles are specified as strings in the array."),
    is_archived: bool | None = Field(None, description="When enabled, marks the activity type as archived, making it unavailable for new activities while preserving existing data."),
) -> dict[str, Any]:
    """Create a new custom activity type that serves as a foundation for adding custom fields to activities. The type must be established before any custom fields can be associated with it."""

    # Construct request model with validation
    try:
        _request = _models.PostV1CustomActivityRequest(
            body=_models.PostV1CustomActivityRequestBody(name=name, description=description, api_create_only=api_create_only, editable_with_roles=editable_with_roles, is_archived=is_archived)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_custom_activity_type: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/custom_activity"
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
async def get_custom_activity(id_: str = Field(..., alias="id", description="The unique identifier of the custom activity type to retrieve.")) -> dict[str, Any]:
    """Retrieve a specific custom activity type by its ID, including detailed custom field metadata and configuration."""

    # Construct request model with validation
    try:
        _request = _models.GetV1CustomActivityIdRequest(
            path=_models.GetV1CustomActivityIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_custom_activity: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/custom_activity/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/custom_activity/{id}"
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
    id_: str = Field(..., alias="id", description="The unique identifier of the custom activity type to update."),
    name: str | None = Field(None, description="The display name for the custom activity type."),
    description: str | None = Field(None, description="A detailed description of the custom activity type's purpose and usage."),
    api_create_only: bool | None = Field(None, description="When enabled, restricts creation of this activity type to API requests only, preventing creation through the user interface."),
    editable_with_roles: list[str] | None = Field(None, description="A list of role identifiers that are permitted to edit this activity type. Roles not included in this list will have read-only access."),
    is_archived: bool | None = Field(None, description="When enabled, archives the activity type and prevents it from being used for new activities while preserving existing data."),
    field_order: list[str] | None = Field(None, description="An ordered array of field identifiers that determines the sequence in which fields are displayed in the user interface and API responses."),
) -> dict[str, Any]:
    """Update an existing custom activity type's metadata including name, description, creation restrictions, edit permissions, and field display order. Field management (adding, modifying, or removing fields) must be done separately using the Custom Field API."""

    # Construct request model with validation
    try:
        _request = _models.PutV1CustomActivityIdRequest(
            path=_models.PutV1CustomActivityIdRequestPath(id_=id_),
            body=_models.PutV1CustomActivityIdRequestBody(name=name, description=description, api_create_only=api_create_only, editable_with_roles=editable_with_roles, is_archived=is_archived, field_order=field_order)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_custom_activity: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/custom_activity/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/custom_activity/{id}"
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
    """Permanently delete a custom activity type by its ID. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteV1CustomActivityIdRequest(
            path=_models.DeleteV1CustomActivityIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_custom_activity: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/custom_activity/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/custom_activity/{id}"
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
async def list_custom_activities(custom_activity_type_id: str | None = Field(None, description="Filter results to a specific custom activity type. When using this filter, the lead_id parameter is required.")) -> dict[str, Any]:
    """Retrieve and filter custom activity instances. Use custom_activity_type_id to narrow results by activity type; note that filtering by activity type requires the lead_id parameter to be specified."""

    # Construct request model with validation
    try:
        _request = _models.GetV1ActivityCustomRequest(
            query=_models.GetV1ActivityCustomRequestQuery(custom_activity_type_id=custom_activity_type_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_custom_activities: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/activity/custom"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
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
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Activities
@mcp.tool()
async def create_custom_activity(
    custom_activity_type_id: str = Field(..., description="The unique identifier of the custom activity type to instantiate."),
    lead_id: str = Field(..., description="The unique identifier of the lead associated with this activity."),
    pinned: bool | None = Field(None, description="Set to true to pin this activity, making it more prominent in the activity list."),
) -> dict[str, Any]:
    """Create a new custom activity instance for a lead. Activities are published by default with all required fields validated, or can be created as drafts to defer validation. Optionally pin the activity for visibility."""

    # Construct request model with validation
    try:
        _request = _models.PostV1ActivityCustomRequest(
            body=_models.PostV1ActivityCustomRequestBody(custom_activity_type_id=custom_activity_type_id, lead_id=lead_id, pinned=pinned)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_custom_activity: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/activity/custom"
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
    """Retrieve a specific Custom Activity instance by its unique identifier. Use this to fetch details about a single custom activity."""

    # Construct request model with validation
    try:
        _request = _models.GetV1ActivityCustomIdRequest(
            path=_models.GetV1ActivityCustomIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_custom_activity_instance: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/activity/custom/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/activity/custom/{id}"
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
    pinned: bool | None = Field(None, description="Whether to pin or unpin the activity. Set to true to pin the activity or false to unpin it."),
) -> dict[str, Any]:
    """Update a Custom Activity instance by modifying custom fields, changing its status between draft and published, or toggling its pinned state."""

    # Construct request model with validation
    try:
        _request = _models.PutV1ActivityCustomIdRequest(
            path=_models.PutV1ActivityCustomIdRequestPath(id_=id_),
            body=_models.PutV1ActivityCustomIdRequestBody(pinned=pinned)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_custom_activity_instance: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/activity/custom/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/activity/custom/{id}"
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
    """Delete a Custom Activity instance by its unique identifier. This operation permanently removes the specified custom activity from the system."""

    # Construct request model with validation
    try:
        _request = _models.DeleteV1ActivityCustomIdRequest(
            path=_models.DeleteV1ActivityCustomIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_custom_activity_instance: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/activity/custom/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/activity/custom/{id}"
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
    """Retrieve all Custom Object Types configured in your organization, including their associated Custom Fields and any back-references from other objects (Leads, Contacts, Opportunities, Custom Activities, or Custom Objects)."""

    # Extract parameters for API call
    _http_path = "/v1/custom_object_type"
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
    name_plural: str = Field(..., description="The plural form of the Custom Object Type name. This is used in UI elements and lists where multiple instances are displayed."),
    description: str | None = Field(None, description="An optional longer description that provides additional context about the purpose and use of this Custom Object Type."),
    api_create_only: bool | None = Field(None, description="When enabled, only API clients can create new instances of this type. UI-based creation is disabled. Defaults to false, allowing any user to create instances."),
    editable_with_roles: list[str] | None = Field(None, description="An optional list of user roles that are permitted to edit instances of this type. When specified, only users with at least one of these roles can make changes. If not specified, any user in your organization can edit instances."),
) -> dict[str, Any]:
    """Create a new Custom Object Type that serves as a blueprint for custom objects in your organization. Custom Object Types must be created before you can add custom fields to instances."""

    # Construct request model with validation
    try:
        _request = _models.PostV1CustomObjectTypeRequest(
            body=_models.PostV1CustomObjectTypeRequestBody(name=name, name_plural=name_plural, description=description, api_create_only=api_create_only, editable_with_roles=editable_with_roles)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_custom_object_type: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/custom_object_type"
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
async def get_custom_object_type(id_: str = Field(..., alias="id", description="The unique identifier of the Custom Object Type to retrieve.")) -> dict[str, Any]:
    """Retrieve a specific Custom Object Type by its ID, including detailed metadata about all associated Custom Fields."""

    # Construct request model with validation
    try:
        _request = _models.GetV1CustomObjectTypeIdRequest(
            path=_models.GetV1CustomObjectTypeIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_custom_object_type: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/custom_object_type/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/custom_object_type/{id}"
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
    name_plural: str | None = Field(None, description="The plural form of the Custom Object Type name, used in API responses and UI contexts."),
    description: str | None = Field(None, description="A detailed description explaining the purpose and use of this Custom Object Type."),
    api_create_only: bool | None = Field(None, description="When enabled, instances of this type can only be created through API clients, preventing creation through the user interface."),
    editable_with_roles: list[str] | None = Field(None, description="A list of role identifiers that are permitted to edit instances of this Custom Object Type. Order is not significant."),
) -> dict[str, Any]:
    """Update an existing Custom Object Type's metadata including name, description, and access controls. Field management must be handled separately through the Custom Object Custom Fields API."""

    # Construct request model with validation
    try:
        _request = _models.PutV1CustomObjectTypeIdRequest(
            path=_models.PutV1CustomObjectTypeIdRequestPath(id_=id_),
            body=_models.PutV1CustomObjectTypeIdRequestBody(name=name, name_plural=name_plural, description=description, api_create_only=api_create_only, editable_with_roles=editable_with_roles)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_custom_object_type: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/custom_object_type/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/custom_object_type/{id}"
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
    """Permanently delete a Custom Object Type by its ID. This action removes the custom object type definition and cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteV1CustomObjectTypeIdRequest(
            path=_models.DeleteV1CustomObjectTypeIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_custom_object_type: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/custom_object_type/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/custom_object_type/{id}"
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
    lead_id: str = Field(..., description="The unique identifier of the lead whose Custom Object instances should be retrieved. This parameter is required to filter results to a specific lead."),
    custom_object_type_id: str | None = Field(None, description="Optional filter to retrieve only Custom Object instances of a specific type. When omitted, all Custom Object types for the lead are returned."),
) -> dict[str, Any]:
    """Retrieve all Custom Object instances associated with a specific lead. Use Advanced Filtering to retrieve Custom Objects across multiple leads. Custom field values are returned in the format custom.{custom_field_id}."""

    # Construct request model with validation
    try:
        _request = _models.GetV1CustomObjectRequest(
            query=_models.GetV1CustomObjectRequestQuery(lead_id=lead_id, custom_object_type_id=custom_object_type_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_custom_objects: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/custom_object"
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
    custom_object_type_id: str = Field(..., description="The identifier of the Custom Object type being created, which determines which Custom Fields are available for this instance."),
    lead_id: str = Field(..., description="The identifier of the lead that this Custom Object instance will be associated with."),
    name: str = Field(..., description="A display name for this Custom Object instance."),
) -> dict[str, Any]:
    """Create a new Custom Object instance linked to a specific lead. Custom Field values can be set using the custom.{custom_field_id} format."""

    # Construct request model with validation
    try:
        _request = _models.PostV1CustomObjectRequest(
            body=_models.PostV1CustomObjectRequestBody(custom_object_type_id=custom_object_type_id, lead_id=lead_id, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_custom_object: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/custom_object"
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
    """Retrieve a single Custom Object instance by its unique identifier. Use this operation to fetch detailed information about a specific custom object."""

    # Construct request model with validation
    try:
        _request = _models.GetV1CustomObjectIdRequest(
            path=_models.GetV1CustomObjectIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_custom_object: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/custom_object/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/custom_object/{id}"
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
    body: dict[str, Any] = Field(..., description="The update payload containing the custom fields and/or name property to modify on the Custom Object instance."),
) -> dict[str, Any]:
    """Update an existing Custom Object instance by modifying its custom fields or name property. Supports adding, changing, or removing any custom fields associated with the object."""

    # Construct request model with validation
    try:
        _request = _models.PutV1CustomObjectIdRequest(
            path=_models.PutV1CustomObjectIdRequestPath(id_=id_),
            body=_models.PutV1CustomObjectIdRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_custom_object: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/custom_object/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/custom_object/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
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
    """Permanently delete a Custom Object instance by its ID. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteV1CustomObjectIdRequest(
            path=_models.DeleteV1CustomObjectIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_custom_object: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/custom_object/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/custom_object/{id}"
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
    """Retrieve a complete list of email addresses that have been unsubscribed from communications. Use this to manage your unsubscribe list and understand user preferences."""

    # Extract parameters for API call
    _http_path = "/v1/unsubscribe/email"
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
async def unsubscribe_email(email: str = Field(..., description="The email address to unsubscribe from Close messages. Must be a valid email format.")) -> dict[str, Any]:
    """Remove an email address from Close's messaging system. Use this operation when an email has unsubscribed through another channel and you need to sync that status with Close."""

    # Construct request model with validation
    try:
        _request = _models.PostV1UnsubscribeEmailRequest(
            body=_models.PostV1UnsubscribeEmailRequestBody(email=email)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for unsubscribe_email: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/unsubscribe/email"
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
    """Resubscribe an email address to receive messages from Close. Use this operation to restore messaging delivery for previously unsubscribed email addresses."""

    # Construct request model with validation
    try:
        _request = _models.DeleteV1UnsubscribeEmailEmailAddressRequest(
            path=_models.DeleteV1UnsubscribeEmailEmailAddressRequestPath(email_address=email_address)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for resubscribe_email: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/unsubscribe/email/{email_address}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/unsubscribe/email/{email_address}"
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
    query_type: Literal["and", "or", "id", "object_type", "text", "has_related", "field_condition"] = Field(..., alias="queryType", description="The root query type that determines how to interpret the query structure. Use 'and' or 'or' for combining multiple sub-queries, 'id' to search by object identifier, 'object_type' to filter by record type, 'text' for full-text search, 'has_related' to find records with related objects, or 'field_condition' to filter by specific field values."),
    field_type: Literal["regular_field", "custom_field"] | None = Field(None, alias="fieldType", description="Specifies whether the field is a standard system field or a custom field defined for your organization."),
    condition_type: Literal["boolean", "current_user", "exists", "text", "term", "reference", "number_range"] | None = Field(None, alias="conditionType", description="The type of condition to apply when filtering by field value. Choose 'boolean' for true/false fields, 'current_user' to match the authenticated user, 'exists' to check field presence, 'text' for text matching, 'term' for exact value matching, 'reference' for related record matching, or 'number_range' for numeric comparisons."),
    queries: list[dict[str, Any]] | None = Field(None, description="Array of nested query objects used with 'and' or 'or' query types to combine multiple filter conditions. Each sub-query follows the same structure as the parent query."),
    query_object_type: Literal["contact", "lead", "contact_phone", "contact_email", "contact_url", "address"] | None = Field(None, alias="queryObject_type", description="Filter results to a specific object type: 'contact' or 'lead' for primary records, or 'contact_phone', 'contact_email', 'contact_url', 'address' for related contact details."),
    field_object_type: str | None = Field(None, alias="fieldObject_type", description="The object type that contains the field being filtered, used when querying fields from related objects."),
    query_value: str | None = Field(None, alias="queryValue", description="The value to match for 'id' queries (object identifier) or 'text' queries (search term). For text queries, matching behavior is controlled by the 'mode' parameter."),
    condition_value: dict[str, Any] | None = Field(None, alias="conditionValue", description="The condition value to match against. Structure depends on the condition type: for 'boolean' use true/false, for 'term' use a single value, for 'number_range' use an object with comparison operators, for 'reference' use object IDs."),
    mode: Literal["full_words", "phrase"] | None = Field(None, description="Controls text search matching behavior: 'full_words' matches complete words only, 'phrase' matches the exact phrase as entered."),
    field_name: str | None = Field(None, description="The name of the regular (system) field to filter by. Use this when filtering standard fields like name, email, or phone."),
    values: list[str] | None = Field(None, description="Array of values to match against for 'term' conditions. Results include records where the field matches any value in this list."),
    gt: int | None = Field(None, description="Numeric lower bound (exclusive) for 'number_range' conditions. Use to filter fields with values greater than this number."),
    reference_type: str | None = Field(None, description="The type of object being referenced in a 'reference' condition, such as 'user' for user-related filters."),
    object_ids: list[str] | None = Field(None, description="Array of object IDs to match in 'reference' conditions. Results include records that reference any of these objects."),
    negate: bool | None = Field(None, description="When true, inverts the query logic to return records that do NOT match the specified conditions."),
    this_object_type: str | None = Field(None, description="The primary object type for 'has_related' queries. Specifies which object type you're searching (e.g., 'contact')."),
    related_object_type: str | None = Field(None, description="The related object type to check for in 'has_related' queries. Specifies what related records to look for (e.g., 'contact_email')."),
    related_query: dict[str, Any] | None = Field(None, description="A query object defining conditions to apply to the related objects in 'has_related' queries. Only primary records with related objects matching this query are returned."),
    fields: dict[str, Any] | None = Field(None, description="Specify which fields to include in results for each object type. Use an object with object type keys (e.g., 'contact', 'lead') and arrays of field names as values to customize response data."),
    limit: int | None = Field(None, description="Number of results to return per page. Defaults to 10 results. Use with 'cursor' for pagination through large result sets."),
    cursor: str | None = Field(None, description="Pagination cursor from a previous response to retrieve the next page of results. Omit for the first request."),
    results_limit: int | None = Field(None, description="Maximum total number of results to return across all pages. Limits the overall result set size regardless of pagination."),
    include_counts: bool | None = Field(None, description="When true, the response includes counts of total matching results for each object type, useful for understanding result scope before fetching all records."),
    sort: list[_models.PostApiV1DataSearchBodySortItem] | None = Field(None, description="Array of sort specifications to order results. Each entry specifies a field name and sort direction (ascending or descending) to organize results by your preferred criteria."),
) -> dict[str, Any]:
    """Search for Leads or Contacts using advanced filtering with support for complex query conditions, relationships, and pagination. Construct queries with logical operators (and/or), field conditions, text search, and related object filters to find records matching your criteria."""

    # Construct request model with validation
    try:
        _request = _models.PostApiV1DataSearchRequest(
            body=_models.PostApiV1DataSearchRequestBody(fields=fields, limit=limit, cursor=cursor, results_limit=results_limit, include_counts=include_counts, sort=sort,
                query=_models.PostApiV1DataSearchRequestBodyQuery(
                    type_=query_type, queries=queries, object_type=query_object_type, value=query_value, mode=mode, negate=negate, this_object_type=this_object_type, related_object_type=related_object_type, related_query=related_query,
                    field=_models.PostApiV1DataSearchRequestBodyQueryField(type_=field_type, object_type=field_object_type, field_name=field_name) if any(v is not None for v in [field_type, field_object_type, field_name]) else None,
                    condition=_models.PostApiV1DataSearchRequestBodyQueryCondition(type_=condition_type, value=condition_value, values=values, gt=gt, reference_type=reference_type, object_ids=object_ids) if any(v is not None for v in [condition_type, condition_value, values, gt, reference_type, object_ids]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_contacts_and_leads: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/data/search/"
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

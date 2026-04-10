#!/usr/bin/env python3
"""
Klaviyo MCP Server

API Info:
- API License: License (https://www.klaviyo.com/legal)
- Contact: Klaviyo Developer Experience Team <developers@klaviyo.com> (https://developers.klaviyo.com)
- Terms of Service: https://www.klaviyo.com/legal/api-terms

Generated: 2026-04-09 17:25:38 UTC
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

BASE_URL = os.getenv("BASE_URL", "https://a.klaviyo.com")
SERVER_NAME = "Klaviyo"
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
    'Klaviyo-API-Key',
]

# Initialize authentication handlers at server startup
_auth_handlers: dict[str, Any] = {}
try:
    _auth_handlers["Klaviyo-API-Key"] = _auth.APIKeyAuth(env_var="API_KEY", location="header", param_name="Authorization", prefix="Klaviyo-API-Key")
    logging.info("Authentication configured: Klaviyo-API-Key")
except ValueError as e:
    # Extract credential names from error message (first sentence before "Leave empty")
    error_msg = str(e).split("Leave empty")[0].strip()
    logging.warning(f"Credentials for Klaviyo-API-Key not configured: {error_msg}")
    _auth_handlers["Klaviyo-API-Key"] = None

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

mcp = FastMCP("Klaviyo", middleware=[_JsonCoercionMiddleware()])

# Tags: Accounts
@mcp.tool()
async def get_accounts(
    revision: str = Field(..., description="API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
    fields_account: list[Literal["contact_information", "contact_information.default_sender_email", "contact_information.default_sender_name", "contact_information.organization_name", "contact_information.street_address", "contact_information.street_address.address1", "contact_information.street_address.address2", "contact_information.street_address.city", "contact_information.street_address.country", "contact_information.street_address.region", "contact_information.street_address.zip", "contact_information.website_url", "industry", "locale", "preferred_currency", "public_api_key", "test_account", "timezone"]] | None = Field(None, alias="fieldsaccount", description="Specify which account fields to include in the response using sparse fieldsets for optimized data retrieval. See API documentation for available field names."),
) -> dict[str, Any]:
    """Retrieve account information associated with your private API key, including contact details, timezone, currency, and public API key. Use this to access account-specific data or verify API key ownership before performing other operations."""

    # Construct request model with validation
    try:
        _request = _models.GetAccountsRequest(
            query=_models.GetAccountsRequestQuery(fields_account=fields_account),
            header=_models.GetAccountsRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_accounts: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/accounts"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_query = _serialize_query(_http_query, {
        "fields[account]": ("form", False),
    })
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_accounts")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_accounts", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_accounts",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Accounts
@mcp.tool()
async def get_account(
    id_: str = Field(..., alias="id", description="The unique identifier of the account to retrieve (e.g., AbC123)."),
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
    fields_account: list[Literal["contact_information", "contact_information.default_sender_email", "contact_information.default_sender_name", "contact_information.organization_name", "contact_information.street_address", "contact_information.street_address.address1", "contact_information.street_address.address2", "contact_information.street_address.city", "contact_information.street_address.country", "contact_information.street_address.region", "contact_information.street_address.zip", "contact_information.website_url", "industry", "locale", "preferred_currency", "public_api_key", "test_account", "timezone"]] | None = Field(None, alias="fieldsaccount", description="Optional list of specific account fields to include in the response. Use sparse fieldsets to reduce payload size and improve performance. Refer to the API documentation for available field names."),
) -> dict[str, Any]:
    """Retrieve a single account object by its ID. You can only access the account associated with the private API key used for authentication."""

    # Construct request model with validation
    try:
        _request = _models.GetAccountRequest(
            path=_models.GetAccountRequestPath(id_=id_),
            query=_models.GetAccountRequestQuery(fields_account=fields_account),
            header=_models.GetAccountRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_account: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/accounts/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/accounts/{id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_query = _serialize_query(_http_query, {
        "fields[account]": ("form", False),
    })
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

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
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Campaigns
@mcp.tool()
async def list_campaigns(
    filter_: str = Field(..., alias="filter", description="Filter expression to narrow campaign results. A channel filter is required—use equals(messages.channel,'email'), equals(messages.channel,'sms'), or equals(messages.channel,'mobile_push'). You can combine with additional filters on id, name (contains), status, archived state, or timestamps (created_at, scheduled_at, updated_at). See API documentation for full filtering syntax."),
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format (or with optional suffix). Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve campaigns filtered by channel (email, SMS, or mobile push) and optional criteria like name, status, or date range. A channel filter is required to list campaigns."""

    # Construct request model with validation
    try:
        _request = _models.GetCampaignsRequest(
            query=_models.GetCampaignsRequestQuery(filter_=filter_),
            header=_models.GetCampaignsRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_campaigns: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/campaigns"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_campaigns")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_campaigns", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_campaigns",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Campaigns
@mcp.tool()
async def get_campaign(
    id_: str = Field(..., alias="id", description="The unique identifier of the campaign to retrieve."),
    revision: str = Field(..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15 if not specified)."),
) -> dict[str, Any]:
    """Retrieve a specific campaign by its ID. Returns detailed campaign information for the requested resource."""

    # Construct request model with validation
    try:
        _request = _models.GetCampaignRequest(
            path=_models.GetCampaignRequestPath(id_=id_),
            header=_models.GetCampaignRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_campaign: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/campaigns/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/campaigns/{id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_campaign")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_campaign", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_campaign",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Campaigns
@mcp.tool()
async def update_campaign(
    id_: str = Field(..., alias="id", description="The unique identifier of the campaign to update."),
    revision: str = Field(..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.v2). Defaults to 2026-01-15 if not specified."),
    data_id: str = Field(..., alias="dataId", description="The unique identifier of the campaign being updated; must match the path ID parameter."),
    type_: Literal["campaign"] = Field(..., alias="type", description="The resource type identifier; must be set to 'campaign'."),
    name: str | None = Field(None, description="The display name for the campaign (e.g., 'My new campaign')."),
    included: list[str] | None = Field(None, description="A list of audience IDs to include in the campaign. Providing this list will replace any previously included audiences. Order and format follow the audience ID system."),
    excluded: list[str] | None = Field(None, description="A list of audience IDs to exclude from the campaign. Providing this list will replace any previously excluded audiences. Order and format follow the audience ID system."),
    send_options: _models.EmailSendOptions | _models.SmsSendOptions | _models.PushSendOptions | None = Field(None, description="Configuration options that control how the campaign will be sent, including delivery timing and method preferences."),
    tracking_options: _models.CampaignsEmailTrackingOptions | _models.CampaignsSmsTrackingOptions | None = Field(None, description="Tracking configuration for the campaign, including metrics collection and event monitoring settings."),
    send_strategy: _models.StaticSendStrategy | _models.ThrottledSendStrategy | _models.ImmediateSendStrategy | _models.SmartSendTimeStrategy | None = Field(None, description="The delivery strategy that determines how the campaign will be distributed to recipients (e.g., immediate, scheduled, or progressive send)."),
) -> dict[str, Any]:
    """Update an existing campaign's configuration including name, audience targeting, send options, tracking, and delivery strategy. Requires the campaign ID and current revision for optimistic concurrency control."""

    # Construct request model with validation
    try:
        _request = _models.UpdateCampaignRequest(
            path=_models.UpdateCampaignRequestPath(id_=id_),
            header=_models.UpdateCampaignRequestHeader(revision=revision),
            body=_models.UpdateCampaignRequestBody(data=_models.UpdateCampaignRequestBodyData(
                    id_=data_id, type_=type_,
                    attributes=_models.UpdateCampaignRequestBodyDataAttributes(name=name, send_options=send_options, tracking_options=tracking_options, send_strategy=send_strategy,
                        audiences=_models.UpdateCampaignRequestBodyDataAttributesAudiences(included=included, excluded=excluded) if any(v is not None for v in [included, excluded]) else None) if any(v is not None for v in [name, included, excluded, send_options, tracking_options, send_strategy]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_campaign: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/campaigns/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/campaigns/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_campaign")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_campaign", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_campaign",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Campaigns
@mcp.tool()
async def delete_campaign(
    id_: str = Field(..., alias="id", description="The unique identifier of the campaign to delete."),
    revision: str = Field(..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15 if not specified)."),
) -> dict[str, Any]:
    """Permanently delete a campaign by its ID. This action cannot be undone and will remove all associated campaign data."""

    # Construct request model with validation
    try:
        _request = _models.DeleteCampaignRequest(
            path=_models.DeleteCampaignRequestPath(id_=id_),
            header=_models.DeleteCampaignRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_campaign: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/campaigns/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/campaigns/{id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_campaign")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_campaign", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_campaign",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Campaigns
@mcp.tool()
async def get_campaign_message(
    id_: str = Field(..., alias="id", description="The unique identifier of the campaign message to retrieve."),
    revision: str = Field(..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.v2). Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieves a specific campaign message by its ID. Returns the message details for the specified revision of the API."""

    # Construct request model with validation
    try:
        _request = _models.GetCampaignMessageRequest(
            path=_models.GetCampaignMessageRequestPath(id_=id_),
            header=_models.GetCampaignMessageRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_campaign_message: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/campaign-messages/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/campaign-messages/{id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_campaign_message")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_campaign_message", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_campaign_message",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Campaigns
@mcp.tool()
async def update_campaign_message(
    id_: str = Field(..., alias="id", description="The unique identifier of the campaign message to update."),
    revision: str = Field(..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix. Defaults to 2026-01-15 if not specified."),
    data_id: str = Field(..., alias="dataId", description="The unique identifier of the campaign message being updated. Must match the message ID in the URL path."),
    data_relationships_image_data_id: str = Field(..., alias="dataRelationshipsImageDataId", description="The unique identifier of the image to associate with this campaign message. Required for mobile_push message types."),
    type_: Literal["campaign-message"] = Field(..., alias="type", description="The resource type identifier for the campaign message. Must be set to 'campaign-message'."),
    image_data_type: Literal["image"] = Field(..., alias="imageDataType", description="The resource type identifier for the associated image. Must be set to 'image'."),
    definition: _models.EmailMessageDefinition | _models.SmsMessageDefinitionCreate | _models.MobilePushMessageStandardDefinitionUpdate | _models.MobilePushMessageSilentDefinitionUpdate | None = Field(None, description="The campaign message contents and configuration settings, including template variables, targeting rules, and delivery preferences."),
) -> dict[str, Any]:
    """Update an existing campaign message with new content and settings. Supports modifying message definition, associated images for mobile push notifications, and other campaign message properties."""

    # Construct request model with validation
    try:
        _request = _models.UpdateCampaignMessageRequest(
            path=_models.UpdateCampaignMessageRequestPath(id_=id_),
            header=_models.UpdateCampaignMessageRequestHeader(revision=revision),
            body=_models.UpdateCampaignMessageRequestBody(data=_models.UpdateCampaignMessageRequestBodyData(
                    id_=data_id, type_=type_,
                    relationships=_models.UpdateCampaignMessageRequestBodyDataRelationships(
                        image=_models.UpdateCampaignMessageRequestBodyDataRelationshipsImage(
                            data=_models.UpdateCampaignMessageRequestBodyDataRelationshipsImageData(id_=data_relationships_image_data_id, type_=image_data_type)
                        )
                    ),
                    attributes=_models.UpdateCampaignMessageRequestBodyDataAttributes(definition=definition) if any(v is not None for v in [definition]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_campaign_message: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/campaign-messages/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/campaign-messages/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_campaign_message")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_campaign_message", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_campaign_message",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Campaigns
@mcp.tool()
async def get_campaign_send_job(
    id_: str = Field(..., alias="id", description="The unique identifier of the campaign send job to retrieve."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format (with optional suffix). Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve details about a specific campaign send job by its ID. Use this to check the status and metadata of a campaign send operation."""

    # Construct request model with validation
    try:
        _request = _models.GetCampaignSendJobRequest(
            path=_models.GetCampaignSendJobRequestPath(id_=id_),
            header=_models.GetCampaignSendJobRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_campaign_send_job: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/campaign-send-jobs/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/campaign-send-jobs/{id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_campaign_send_job")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_campaign_send_job", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_campaign_send_job",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Campaigns
@mcp.tool()
async def update_campaign_send_job(
    id_: str = Field(..., alias="id", description="The unique identifier of the campaign send job to modify."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format (or with an optional suffix). Defaults to 2026-01-15."),
    data_id: str = Field(..., alias="dataId", description="The unique identifier of the campaign send job being modified; must match the path ID."),
    type_: Literal["campaign-send-job"] = Field(..., alias="type", description="The resource type identifier; must be 'campaign-send-job'."),
    action: Literal["cancel", "revert"] = Field(..., description="The action to perform: 'cancel' to permanently stop the send, or 'revert' to return the campaign to draft status."),
) -> dict[str, Any]:
    """Cancel an in-progress campaign send or revert it back to draft status. Use 'cancel' to permanently stop the send, or 'revert' to return the campaign to draft for further editing."""

    # Construct request model with validation
    try:
        _request = _models.CancelCampaignSendRequest(
            path=_models.CancelCampaignSendRequestPath(id_=id_),
            header=_models.CancelCampaignSendRequestHeader(revision=revision),
            body=_models.CancelCampaignSendRequestBody(data=_models.CancelCampaignSendRequestBodyData(
                    id_=data_id, type_=type_,
                    attributes=_models.CancelCampaignSendRequestBodyDataAttributes(action=action)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_campaign_send_job: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/campaign-send-jobs/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/campaign-send-jobs/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_campaign_send_job")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_campaign_send_job", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_campaign_send_job",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Campaigns
@mcp.tool()
async def get_campaign_recipient_estimation_job(
    id_: str = Field(..., alias="id", description="The unique identifier of the campaign recipient estimation job whose status you want to retrieve."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve the current status and results of a recipient estimation job for a campaign. Use this to poll the asynchronous job triggered by the Create Campaign Recipient Estimation Job endpoint."""

    # Construct request model with validation
    try:
        _request = _models.GetCampaignRecipientEstimationJobRequest(
            path=_models.GetCampaignRecipientEstimationJobRequestPath(id_=id_),
            header=_models.GetCampaignRecipientEstimationJobRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_campaign_recipient_estimation_job: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/campaign-recipient-estimation-jobs/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/campaign-recipient-estimation-jobs/{id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_campaign_recipient_estimation_job")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_campaign_recipient_estimation_job", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_campaign_recipient_estimation_job",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Campaigns
@mcp.tool()
async def get_campaign_recipient_estimation(
    id_: str = Field(..., alias="id", description="The unique identifier of the campaign for which to retrieve the estimated recipient count."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, optionally with a suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve the estimated recipient count for a campaign. Use the Create Campaign Recipient Estimation Job endpoint to refresh this estimate."""

    # Construct request model with validation
    try:
        _request = _models.GetCampaignRecipientEstimationRequest(
            path=_models.GetCampaignRecipientEstimationRequestPath(id_=id_),
            header=_models.GetCampaignRecipientEstimationRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_campaign_recipient_estimation: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/campaign-recipient-estimations/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/campaign-recipient-estimations/{id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_campaign_recipient_estimation")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_campaign_recipient_estimation", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_campaign_recipient_estimation",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Campaigns
@mcp.tool()
async def clone_campaign(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.beta). Defaults to 2026-01-15 if not specified."),
    type_: Literal["campaign"] = Field(..., alias="type", description="The resource type being cloned. Must be set to 'campaign' for this operation."),
    id_: str = Field(..., alias="id", description="The unique identifier of the campaign to clone."),
    new_name: str | None = Field(None, description="Optional custom name for the newly cloned campaign. If not provided, a default name will be generated based on the original campaign."),
) -> dict[str, Any]:
    """Creates a duplicate of an existing campaign with a new ID and optional custom name. The cloned campaign inherits all settings and configuration from the original."""

    # Construct request model with validation
    try:
        _request = _models.CreateCampaignCloneRequest(
            header=_models.CreateCampaignCloneRequestHeader(revision=revision),
            body=_models.CreateCampaignCloneRequestBody(data=_models.CreateCampaignCloneRequestBodyData(
                    type_=type_, id_=id_,
                    attributes=_models.CreateCampaignCloneRequestBodyDataAttributes(new_name=new_name) if any(v is not None for v in [new_name]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for clone_campaign: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/campaign-clone"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("clone_campaign")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("clone_campaign", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="clone_campaign",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Campaigns
@mcp.tool()
async def assign_template_to_campaign_message(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15). Defaults to 2026-01-15 if not specified."),
    type_: Literal["campaign-message"] = Field(..., alias="type", description="Resource type identifier for the campaign message. Must be set to 'campaign-message'."),
    template_data_type: Literal["template"] = Field(..., alias="templateDataType", description="Resource type identifier for the template relationship. Must be set to 'template'."),
    id_: str = Field(..., alias="id", description="The unique identifier of the campaign message that will receive the template assignment."),
    template_data_id: str = Field(..., alias="templateDataId", description="The unique identifier of the template to assign to the campaign message."),
) -> dict[str, Any]:
    """Assigns a template to a campaign message by creating a non-reusable copy of the template linked to that specific message. This operation requires campaigns:write scope and is subject to rate limits of 10 requests per second (burst) and 150 requests per minute (steady state)."""

    # Construct request model with validation
    try:
        _request = _models.AssignTemplateToCampaignMessageRequest(
            header=_models.AssignTemplateToCampaignMessageRequestHeader(revision=revision),
            body=_models.AssignTemplateToCampaignMessageRequestBody(data=_models.AssignTemplateToCampaignMessageRequestBodyData(
                    type_=type_, id_=id_,
                    relationships=_models.AssignTemplateToCampaignMessageRequestBodyDataRelationships(
                        template=_models.AssignTemplateToCampaignMessageRequestBodyDataRelationshipsTemplate(
                            data=_models.AssignTemplateToCampaignMessageRequestBodyDataRelationshipsTemplateData(type_=template_data_type, id_=template_data_id)
                        )
                    )
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for assign_template_to_campaign_message: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/campaign-message-assign-template"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("assign_template_to_campaign_message")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("assign_template_to_campaign_message", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="assign_template_to_campaign_message",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Campaigns
@mcp.tool()
async def send_campaign(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.v1). Defaults to 2026-01-15 if not specified."),
    type_: Literal["campaign-send-job"] = Field(..., alias="type", description="The resource type identifier for this operation, which must be 'campaign-send-job'."),
    id_: str = Field(..., alias="id", description="The unique identifier of the campaign to send. This campaign must exist and be in a valid state for sending."),
) -> dict[str, Any]:
    """Trigger an asynchronous campaign send job to deliver messages to recipients. The operation queues the campaign for processing and returns immediately."""

    # Construct request model with validation
    try:
        _request = _models.SendCampaignRequest(
            header=_models.SendCampaignRequestHeader(revision=revision),
            body=_models.SendCampaignRequestBody(data=_models.SendCampaignRequestBodyData(type_=type_, id_=id_))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for send_campaign: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/campaign-send-jobs"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("send_campaign")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("send_campaign", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="send_campaign",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Campaigns
@mcp.tool()
async def trigger_campaign_recipient_estimation(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15 if not specified)."),
    type_: Literal["campaign-recipient-estimation-job"] = Field(..., alias="type", description="Resource type identifier; must be set to 'campaign-recipient-estimation-job' to specify the job type being created."),
    id_: str = Field(..., alias="id", description="The unique identifier of the campaign for which to estimate recipient count."),
) -> dict[str, Any]:
    """Initiate an asynchronous job to recalculate the estimated recipient count for a campaign. Poll the job status endpoint or retrieve the final estimation once processing completes."""

    # Construct request model with validation
    try:
        _request = _models.RefreshCampaignRecipientEstimationRequest(
            header=_models.RefreshCampaignRecipientEstimationRequestHeader(revision=revision),
            body=_models.RefreshCampaignRecipientEstimationRequestBody(data=_models.RefreshCampaignRecipientEstimationRequestBodyData(type_=type_, id_=id_))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for trigger_campaign_recipient_estimation: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/campaign-recipient-estimation-jobs"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("trigger_campaign_recipient_estimation")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("trigger_campaign_recipient_estimation", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="trigger_campaign_recipient_estimation",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Campaigns
@mcp.tool()
async def get_campaign_for_campaign_message(
    id_: str = Field(..., alias="id", description="The unique identifier of the campaign message for which to retrieve the associated campaign."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve the campaign associated with a specific campaign message. This operation returns the parent campaign details for the given message."""

    # Construct request model with validation
    try:
        _request = _models.GetCampaignForCampaignMessageRequest(
            path=_models.GetCampaignForCampaignMessageRequestPath(id_=id_),
            header=_models.GetCampaignForCampaignMessageRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_campaign_for_campaign_message: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/campaign-messages/{id}/campaign", _request.path.model_dump(by_alias=True)) if _request.path else "/api/campaign-messages/{id}/campaign"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_campaign_for_campaign_message")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_campaign_for_campaign_message", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_campaign_for_campaign_message",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Campaigns
@mcp.tool()
async def get_campaign_id_for_campaign_message(
    id_: str = Field(..., alias="id", description="The unique identifier of the campaign message for which to retrieve the associated campaign ID."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve the ID of the campaign associated with a specific campaign message. This operation returns the relationship data linking a message to its parent campaign."""

    # Construct request model with validation
    try:
        _request = _models.GetCampaignIdForCampaignMessageRequest(
            path=_models.GetCampaignIdForCampaignMessageRequestPath(id_=id_),
            header=_models.GetCampaignIdForCampaignMessageRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_campaign_id_for_campaign_message: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/campaign-messages/{id}/relationships/campaign", _request.path.model_dump(by_alias=True)) if _request.path else "/api/campaign-messages/{id}/relationships/campaign"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_campaign_id_for_campaign_message")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_campaign_id_for_campaign_message", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_campaign_id_for_campaign_message",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Campaigns
@mcp.tool()
async def get_template_for_campaign_message(
    id_: str = Field(..., alias="id", description="The unique identifier of the campaign message whose template you want to retrieve."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve the template associated with a specific campaign message. Returns the template configuration used by the campaign message."""

    # Construct request model with validation
    try:
        _request = _models.GetTemplateForCampaignMessageRequest(
            path=_models.GetTemplateForCampaignMessageRequestPath(id_=id_),
            header=_models.GetTemplateForCampaignMessageRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_template_for_campaign_message: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/campaign-messages/{id}/template", _request.path.model_dump(by_alias=True)) if _request.path else "/api/campaign-messages/{id}/template"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_template_for_campaign_message")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_template_for_campaign_message", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_template_for_campaign_message",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Campaigns
@mcp.tool()
async def get_template_id_for_campaign_message(
    id_: str = Field(..., alias="id", description="The unique identifier of the campaign message for which to retrieve the related template ID."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve the ID of the template associated with a specific campaign message. This operation returns only the template relationship identifier, useful for determining which template is used by a campaign message."""

    # Construct request model with validation
    try:
        _request = _models.GetTemplateIdForCampaignMessageRequest(
            path=_models.GetTemplateIdForCampaignMessageRequestPath(id_=id_),
            header=_models.GetTemplateIdForCampaignMessageRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_template_id_for_campaign_message: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/campaign-messages/{id}/relationships/template", _request.path.model_dump(by_alias=True)) if _request.path else "/api/campaign-messages/{id}/relationships/template"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_template_id_for_campaign_message")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_template_id_for_campaign_message", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_template_id_for_campaign_message",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Campaigns
@mcp.tool()
async def get_image_for_campaign_message(
    id_: str = Field(..., alias="id", description="The unique identifier of the campaign message for which to retrieve the associated image."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve the image associated with a specific campaign message. Returns the image resource linked to the campaign message identified by the provided ID."""

    # Construct request model with validation
    try:
        _request = _models.GetImageForCampaignMessageRequest(
            path=_models.GetImageForCampaignMessageRequestPath(id_=id_),
            header=_models.GetImageForCampaignMessageRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_image_for_campaign_message: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/campaign-messages/{id}/image", _request.path.model_dump(by_alias=True)) if _request.path else "/api/campaign-messages/{id}/image"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_image_for_campaign_message")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_image_for_campaign_message", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_image_for_campaign_message",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Campaigns
@mcp.tool()
async def get_image_id_for_campaign_message(
    id_: str = Field(..., alias="id", description="The unique identifier of the campaign message whose related image ID you want to retrieve."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve the ID of the image associated with a specific campaign message. This operation returns only the image relationship identifier, not the full image resource."""

    # Construct request model with validation
    try:
        _request = _models.GetImageIdForCampaignMessageRequest(
            path=_models.GetImageIdForCampaignMessageRequestPath(id_=id_),
            header=_models.GetImageIdForCampaignMessageRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_image_id_for_campaign_message: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/campaign-messages/{id}/relationships/image", _request.path.model_dump(by_alias=True)) if _request.path else "/api/campaign-messages/{id}/relationships/image"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_image_id_for_campaign_message")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_image_id_for_campaign_message", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_image_id_for_campaign_message",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Campaigns
@mcp.tool()
async def update_image_for_campaign_message(
    id_: str = Field(..., alias="id", description="The unique identifier of the campaign message whose image should be updated."),
    revision: str = Field(..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15 if not specified)."),
    data_id: str = Field(..., alias="dataId", description="The unique identifier of the image to associate with the campaign message."),
    type_: Literal["image"] = Field(..., alias="type", description="The resource type identifier, which must be 'image' to specify the relationship type being updated."),
) -> dict[str, Any]:
    """Replace the image associated with a campaign message. Requires both the campaign message ID and the image ID to establish the relationship."""

    # Construct request model with validation
    try:
        _request = _models.UpdateImageForCampaignMessageRequest(
            path=_models.UpdateImageForCampaignMessageRequestPath(id_=id_),
            header=_models.UpdateImageForCampaignMessageRequestHeader(revision=revision),
            body=_models.UpdateImageForCampaignMessageRequestBody(data=_models.UpdateImageForCampaignMessageRequestBodyData(id_=data_id, type_=type_))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_image_for_campaign_message: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/campaign-messages/{id}/relationships/image", _request.path.model_dump(by_alias=True)) if _request.path else "/api/campaign-messages/{id}/relationships/image"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_image_for_campaign_message")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_image_for_campaign_message", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_image_for_campaign_message",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Campaigns
@mcp.tool()
async def list_tags_for_campaign(
    id_: str = Field(..., alias="id", description="The unique identifier of the campaign for which to retrieve tags."),
    revision: str = Field(..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15). Specifies which version of the API contract to use for this request."),
) -> dict[str, Any]:
    """Retrieve all tags associated with a specific campaign. Returns a collection of tags that have been assigned to the campaign."""

    # Construct request model with validation
    try:
        _request = _models.GetTagsForCampaignRequest(
            path=_models.GetTagsForCampaignRequestPath(id_=id_),
            header=_models.GetTagsForCampaignRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_tags_for_campaign: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/campaigns/{id}/tags", _request.path.model_dump(by_alias=True)) if _request.path else "/api/campaigns/{id}/tags"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_tags_for_campaign")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_tags_for_campaign", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_tags_for_campaign",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Campaigns
@mcp.tool()
async def list_tag_ids_for_campaign(
    id_: str = Field(..., alias="id", description="The unique identifier of the campaign for which to retrieve associated tag IDs."),
    revision: str = Field(..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15 if not specified)."),
) -> dict[str, Any]:
    """Retrieves all tag IDs associated with a specific campaign. Returns a collection of tag identifiers linked to the campaign."""

    # Construct request model with validation
    try:
        _request = _models.GetTagIdsForCampaignRequest(
            path=_models.GetTagIdsForCampaignRequestPath(id_=id_),
            header=_models.GetTagIdsForCampaignRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_tag_ids_for_campaign: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/campaigns/{id}/relationships/tags", _request.path.model_dump(by_alias=True)) if _request.path else "/api/campaigns/{id}/relationships/tags"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_tag_ids_for_campaign")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_tag_ids_for_campaign", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_tag_ids_for_campaign",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Campaigns
@mcp.tool()
async def list_messages_for_campaign(
    id_: str = Field(..., alias="id", description="The unique identifier of the campaign for which to retrieve messages."),
    revision: str = Field(..., description="The API endpoint revision in YYYY-MM-DD format (optionally with a suffix). Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve all messages associated with a specific campaign. Returns a collection of messages that have been created or assigned to the campaign."""

    # Construct request model with validation
    try:
        _request = _models.GetMessagesForCampaignRequest(
            path=_models.GetMessagesForCampaignRequestPath(id_=id_),
            header=_models.GetMessagesForCampaignRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_messages_for_campaign: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/campaigns/{id}/campaign-messages", _request.path.model_dump(by_alias=True)) if _request.path else "/api/campaigns/{id}/campaign-messages"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_messages_for_campaign")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_messages_for_campaign", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_messages_for_campaign",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Campaigns
@mcp.tool()
async def list_message_ids_for_campaign(
    id_: str = Field(..., alias="id", description="The unique identifier of the campaign whose associated message IDs you want to retrieve."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieves all message IDs associated with a specific campaign. Use this to discover which messages are linked to a campaign for further operations."""

    # Construct request model with validation
    try:
        _request = _models.GetMessageIdsForCampaignRequest(
            path=_models.GetMessageIdsForCampaignRequestPath(id_=id_),
            header=_models.GetMessageIdsForCampaignRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_message_ids_for_campaign: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/campaigns/{id}/relationships/campaign-messages", _request.path.model_dump(by_alias=True)) if _request.path else "/api/campaigns/{id}/relationships/campaign-messages"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_message_ids_for_campaign")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_message_ids_for_campaign", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_message_ids_for_campaign",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def list_catalog_items(
    revision: str = Field(..., description="API endpoint revision date in YYYY-MM-DD format (with optional suffix). Defaults to 2026-01-15 if not specified."),
    filter_: str | None = Field(None, alias="filter", description="Filter catalog items by specific criteria. Supports filtering by item IDs (using `any` operator), category ID (exact match), item title (partial match), or published status (exact match). Provide filters in the format specified by the API filtering documentation."),
) -> dict[str, Any]:
    """Retrieve all catalog items in your account with optional filtering and sorting. Returns up to 100 items per request."""

    # Construct request model with validation
    try:
        _request = _models.GetCatalogItemsRequest(
            query=_models.GetCatalogItemsRequestQuery(filter_=filter_),
            header=_models.GetCatalogItemsRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_catalog_items: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/catalog-items"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_catalog_items")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_catalog_items", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_catalog_items",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def create_catalog_item(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15). Defaults to 2026-01-15 if not specified."),
    type_: Literal["catalog-item"] = Field(..., alias="type", description="The resource type identifier. Must be set to 'catalog-item' to indicate this is a catalog item resource."),
    external_id: str = Field(..., description="A unique identifier for this catalog item in your external system or inventory management platform (e.g., SKU or product ID)."),
    title: str = Field(..., description="The display name of the catalog item. This title appears in email campaigns and customer-facing content."),
    description: str = Field(..., description="A detailed description of the catalog item, including key features and characteristics. This text is used in email content and product displays."),
    url: str = Field(..., description="The full URL to the catalog item's product page on your website. This link is used in emails and integrations to direct customers to the item."),
    integration_type: Literal["$custom"] | None = Field(None, description="The integration type for this catalog item. Currently only '$custom' is supported for custom integrations."),
    price: float | None = Field(None, description="The price of the catalog item displayed in emails and campaigns. If you have variants with different prices, update their prices separately using the variant endpoint."),
    images: list[str] | None = Field(None, description="An array of URLs pointing to product images. Include multiple images to provide different views or angles of the item."),
    custom_metadata: dict[str, Any] | None = Field(None, description="A flat JSON object containing custom metadata about the item (e.g., {'Top Pick': true, 'Season': 'Summer'}). Total size must not exceed 100KB."),
    published: bool | None = Field(None, description="Boolean flag indicating whether the catalog item is published and visible. Defaults to true if not specified."),
    data: list[_models.CreateCatalogItemBodyDataRelationshipsCategoriesDataItem] | None = Field(None, description="Additional data payload for the catalog item. Structure and usage depend on your integration requirements."),
) -> dict[str, Any]:
    """Create a new catalog item in your product catalog. The item will be assigned a unique identifier and can include pricing, images, and custom metadata for use in email campaigns and integrations."""

    # Construct request model with validation
    try:
        _request = _models.CreateCatalogItemRequest(
            header=_models.CreateCatalogItemRequestHeader(revision=revision),
            body=_models.CreateCatalogItemRequestBody(data=_models.CreateCatalogItemRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateCatalogItemRequestBodyDataAttributes(external_id=external_id, integration_type=integration_type, title=title, price=price, description=description, url=url, images=images, custom_metadata=custom_metadata, published=published),
                    relationships=_models.CreateCatalogItemRequestBodyDataRelationships(categories=_models.CreateCatalogItemRequestBodyDataRelationshipsCategories(data=data) if any(v is not None for v in [data]) else None) if any(v is not None for v in [data]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_catalog_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/catalog-items"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_catalog_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_catalog_item", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_catalog_item",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def get_catalog_item(
    id_: str = Field(..., alias="id", description="The compound identifier for the catalog item, formatted as `{integration}:::{catalog}:::{external_id}`. Use `$custom` for the integration type and `$default` for the catalog name, followed by your item's external identifier."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve a specific catalog item by its compound ID. The item ID combines integration type, catalog name, and external identifier in a structured format."""

    # Construct request model with validation
    try:
        _request = _models.GetCatalogItemRequest(
            path=_models.GetCatalogItemRequestPath(id_=id_),
            header=_models.GetCatalogItemRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_catalog_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/catalog-items/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/catalog-items/{id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_catalog_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_catalog_item", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_catalog_item",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def update_catalog_item(
    id_: str = Field(..., alias="id", description="The catalog item's compound ID in format `{integration}:::{catalog}:::{external_id}`. Use `$custom` for integration and `$default` for catalog, followed by your unique external item identifier."),
    revision: str = Field(..., description="API endpoint revision date in YYYY-MM-DD format (with optional suffix). Defaults to 2026-01-15 if not specified."),
    data_id: str = Field(..., alias="dataId", description="The catalog item's compound ID in format `{integration}:::{catalog}:::{external_id}`. Use `$custom` for integration and `$default` for catalog, followed by your unique external item identifier."),
    type_: Literal["catalog-item"] = Field(..., alias="type", description="The resource type identifier. Must be set to `catalog-item`."),
    title: str | None = Field(None, description="The display name of the catalog item."),
    price: float | None = Field(None, description="The item's price as a decimal number. This price is displayed in emails and should typically be updated alongside variant prices using the Update Catalog Variant endpoint."),
    description: str | None = Field(None, description="A text description of the catalog item's features, details, or other relevant information."),
    url: str | None = Field(None, description="A fully qualified URL pointing to the item's product page on your website."),
    images: list[str] | None = Field(None, description="An array of image URLs for the catalog item. Order may be significant for display purposes. Each URL should point to a valid image resource."),
    custom_metadata: dict[str, Any] | None = Field(None, description="A flat JSON object containing custom metadata about the item. Total size must not exceed 100 kilobytes."),
    published: bool | None = Field(None, description="Boolean flag indicating whether the catalog item is currently published and visible."),
    data: list[_models.UpdateCatalogItemBodyDataRelationshipsCategoriesDataItem] | None = Field(None, description="Reserved parameter for internal use."),
) -> dict[str, Any]:
    """Update an existing catalog item with new metadata, pricing, images, or publication status. Use the compound ID format to identify the item, and include the required revision date for API versioning."""

    # Construct request model with validation
    try:
        _request = _models.UpdateCatalogItemRequest(
            path=_models.UpdateCatalogItemRequestPath(id_=id_),
            header=_models.UpdateCatalogItemRequestHeader(revision=revision),
            body=_models.UpdateCatalogItemRequestBody(data=_models.UpdateCatalogItemRequestBodyData(
                    id_=data_id, type_=type_,
                    attributes=_models.UpdateCatalogItemRequestBodyDataAttributes(title=title, price=price, description=description, url=url, images=images, custom_metadata=custom_metadata, published=published) if any(v is not None for v in [title, price, description, url, images, custom_metadata, published]) else None,
                    relationships=_models.UpdateCatalogItemRequestBodyDataRelationships(categories=_models.UpdateCatalogItemRequestBodyDataRelationshipsCategories(data=data) if any(v is not None for v in [data]) else None) if any(v is not None for v in [data]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_catalog_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/catalog-items/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/catalog-items/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_catalog_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_catalog_item", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_catalog_item",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def delete_catalog_item(
    id_: str = Field(..., alias="id", description="The unique identifier for the catalog item in compound format: `{integration}:::{catalog}:::{external_id}`. Use `$custom` for the integration and `$default` for the catalog, followed by your item's external ID (e.g., `$custom:::$default:::SAMPLE-DATA-ITEM-1`)."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format (optionally with a suffix). Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Permanently delete a catalog item from the default catalog. Requires the item's compound ID and the API revision date to ensure consistency."""

    # Construct request model with validation
    try:
        _request = _models.DeleteCatalogItemRequest(
            path=_models.DeleteCatalogItemRequestPath(id_=id_),
            header=_models.DeleteCatalogItemRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_catalog_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/catalog-items/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/catalog-items/{id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_catalog_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_catalog_item", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_catalog_item",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def list_catalog_variants(
    revision: str = Field(..., description="API endpoint revision date in YYYY-MM-DD format (or with optional suffix). Defaults to 2026-01-15 if not specified."),
    filter_: str | None = Field(None, alias="filter", description="Filter variants by specific criteria using supported fields and operators. You can filter by variant IDs (using `any` operator), item ID, SKU, title (partial match), or publication status. Provide filters in the format specified by the API filtering documentation."),
) -> dict[str, Any]:
    """Retrieve all catalog variants in your account with optional filtering and sorting. Returns up to 100 variants per request."""

    # Construct request model with validation
    try:
        _request = _models.GetCatalogVariantsRequest(
            query=_models.GetCatalogVariantsRequestQuery(filter_=filter_),
            header=_models.GetCatalogVariantsRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_catalog_variants: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/catalog-variants"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_catalog_variants")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_catalog_variants", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_catalog_variants",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def create_catalog_variant(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix. Defaults to 2026-01-15."),
    type_: Literal["catalog-variant"] = Field(..., alias="type", description="Resource type identifier. Must be set to 'catalog-variant'."),
    item_data_type: Literal["catalog-item"] = Field(..., alias="itemDataType", description="Resource type for the parent catalog item relationship. Must be set to 'catalog-item'."),
    external_id: str = Field(..., description="Unique identifier for this variant in your external system (e.g., your inventory management or e-commerce platform)."),
    title: str = Field(..., description="Display name for the variant (e.g., 'Ocean Blue Shirt (Sample) Variant Medium'). Should be descriptive enough to distinguish this variant from others."),
    description: str = Field(..., description="Detailed description of the variant's characteristics, materials, fit, or other distinguishing features."),
    sku: str = Field(..., description="Stock keeping unit (SKU) code for inventory tracking and order fulfillment."),
    inventory_quantity: float = Field(..., description="Current stock quantity for this variant. Use a numeric value representing available units."),
    price: float = Field(..., description="Price displayed for this variant in emails and product blocks. Update the parent item's price separately if needed for consistency across your catalog."),
    url: str = Field(..., description="Direct URL to this variant's product page on your website."),
    id_: str = Field(..., alias="id", description="The ID of the parent catalog item for which this variant is being created."),
    integration_type: Literal["$custom"] | None = Field(None, description="Integration type for the variant source. Currently only '$custom' is supported for custom integrations."),
    inventory_policy: Literal[0, 1, 2] | None = Field(None, description="Controls variant visibility in dynamic product recommendation feeds. Use 1 to hide out-of-stock variants, or 0/2 to show regardless of inventory level. Defaults to 0."),
    images: list[str] | None = Field(None, description="Array of image URLs for the variant. Order matters—the first image is typically used as the primary product image."),
    custom_metadata: dict[str, Any] | None = Field(None, description="Custom metadata as a flat JSON object (max 100KB). Use for storing additional variant attributes not covered by standard fields."),
    published: bool | None = Field(None, description="Whether the variant is published and visible in your catalog. Defaults to true."),
) -> dict[str, Any]:
    """Create a new variant for a catalog item, such as a specific size, color, or SKU. Variants inherit from their parent catalog item and can have distinct pricing, inventory, and product URLs."""

    # Construct request model with validation
    try:
        _request = _models.CreateCatalogVariantRequest(
            header=_models.CreateCatalogVariantRequestHeader(revision=revision),
            body=_models.CreateCatalogVariantRequestBody(data=_models.CreateCatalogVariantRequestBodyData(
                    type_=type_,
                    relationships=_models.CreateCatalogVariantRequestBodyDataRelationships(
                        item=_models.CreateCatalogVariantRequestBodyDataRelationshipsItem(
                            data=_models.CreateCatalogVariantRequestBodyDataRelationshipsItemData(type_=item_data_type, id_=id_)
                        )
                    ),
                    attributes=_models.CreateCatalogVariantRequestBodyDataAttributes(external_id=external_id, integration_type=integration_type, title=title, description=description, sku=sku, inventory_policy=inventory_policy, inventory_quantity=inventory_quantity, price=price, url=url, images=images, custom_metadata=custom_metadata, published=published)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_catalog_variant: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/catalog-variants"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_catalog_variant")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_catalog_variant", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_catalog_variant",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def get_catalog_variant(
    id_: str = Field(..., alias="id", description="The compound identifier for the catalog variant, formatted as {integration}:::{catalog}:::{external_id}. Use $custom for the integration type and $default for the catalog name, followed by your external variant identifier."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve a specific catalog item variant by its compound ID. The variant ID combines integration type, catalog name, and external identifier in a structured format."""

    # Construct request model with validation
    try:
        _request = _models.GetCatalogVariantRequest(
            path=_models.GetCatalogVariantRequestPath(id_=id_),
            header=_models.GetCatalogVariantRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_catalog_variant: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/catalog-variants/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/catalog-variants/{id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_catalog_variant")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_catalog_variant", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_catalog_variant",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def update_catalog_variant(
    id_: str = Field(..., alias="id", description="The catalog variant's compound ID in format `{integration}:::{catalog}:::{external_id}`. Use `$custom` for integration and `$default` for catalog, followed by your unique external identifier."),
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15). Defaults to 2026-01-15."),
    data_id: str = Field(..., alias="dataId", description="The catalog variant's compound ID in format `{integration}:::{catalog}:::{external_id}`. Use `$custom` for integration and `$default` for catalog, followed by your unique external identifier."),
    type_: Literal["catalog-variant"] = Field(..., alias="type", description="Resource type identifier. Must be set to `catalog-variant`."),
    title: str | None = Field(None, description="The display name for this variant (e.g., 'Ocean Blue Shirt (Sample) Variant Medium')."),
    description: str | None = Field(None, description="A detailed description of the variant's features, materials, and characteristics."),
    sku: str | None = Field(None, description="The stock keeping unit (SKU) code for inventory and ordering purposes."),
    inventory_policy: Literal[0, 1, 2] | None = Field(None, description="Controls variant visibility in dynamic product feeds. Use `1` to hide out-of-stock items, or `0`/`2` to show regardless of inventory status."),
    inventory_quantity: float | None = Field(None, description="The current quantity of this variant in stock."),
    price: float | None = Field(None, description="The price displayed for this variant in emails and product blocks. Consider also updating the parent item's price for consistency."),
    url: str | None = Field(None, description="A direct URL to this variant's product page on your website."),
    images: list[str] | None = Field(None, description="An array of image URLs for this variant. Order matters—the first image is typically used as the primary product image."),
    custom_metadata: dict[str, Any] | None = Field(None, description="A flat JSON object for storing custom metadata about the variant (e.g., `{'Top Pick': true}`). Must not exceed 100KB."),
    published: bool | None = Field(None, description="Set to `true` to make this variant visible in your catalog, or `false` to hide it."),
) -> dict[str, Any]:
    """Update a catalog item variant by its compound ID. Modify variant details such as title, description, pricing, inventory, images, and custom metadata to keep your product catalog current."""

    # Construct request model with validation
    try:
        _request = _models.UpdateCatalogVariantRequest(
            path=_models.UpdateCatalogVariantRequestPath(id_=id_),
            header=_models.UpdateCatalogVariantRequestHeader(revision=revision),
            body=_models.UpdateCatalogVariantRequestBody(data=_models.UpdateCatalogVariantRequestBodyData(
                    id_=data_id, type_=type_,
                    attributes=_models.UpdateCatalogVariantRequestBodyDataAttributes(title=title, description=description, sku=sku, inventory_policy=inventory_policy, inventory_quantity=inventory_quantity, price=price, url=url, images=images, custom_metadata=custom_metadata, published=published) if any(v is not None for v in [title, description, sku, inventory_policy, inventory_quantity, price, url, images, custom_metadata, published]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_catalog_variant: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/catalog-variants/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/catalog-variants/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_catalog_variant")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_catalog_variant", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_catalog_variant",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def delete_catalog_variant(
    id_: str = Field(..., alias="id", description="The compound identifier for the catalog variant in the format {integration}:::{catalog}:::{external_id}. Use $custom as the integration type and $default as the catalog name, followed by your external variant identifier."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Permanently delete a catalog item variant by its compound ID. The variant ID must follow the format {integration}:::{catalog}:::{external_id}, where integration is $custom and catalog is $default."""

    # Construct request model with validation
    try:
        _request = _models.DeleteCatalogVariantRequest(
            path=_models.DeleteCatalogVariantRequestPath(id_=id_),
            header=_models.DeleteCatalogVariantRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_catalog_variant: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/catalog-variants/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/catalog-variants/{id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_catalog_variant")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_catalog_variant", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_catalog_variant",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def list_catalog_categories(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format (or with optional suffix). Defaults to 2026-01-15 if not specified."),
    filter_: str | None = Field(None, alias="filter", description="Filter results using supported fields and operators. You can filter by category IDs using the `any` operator, item IDs using `equals`, or category names using `contains` for partial matching."),
) -> dict[str, Any]:
    """Retrieve all catalog categories in your account. Returns up to 100 categories per request, supporting filtering by IDs, item IDs, or category names."""

    # Construct request model with validation
    try:
        _request = _models.GetCatalogCategoriesRequest(
            query=_models.GetCatalogCategoriesRequestQuery(filter_=filter_),
            header=_models.GetCatalogCategoriesRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_catalog_categories: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/catalog-categories"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_catalog_categories")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_catalog_categories", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_catalog_categories",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def create_catalog_category(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix. Defaults to 2026-01-15 if not specified."),
    type_: Literal["catalog-category"] = Field(..., alias="type", description="The resource type identifier. Must be set to 'catalog-category' for this operation."),
    external_id: str = Field(..., description="A unique identifier for this category in your external system. Use this to reference the category across integrations."),
    name: str = Field(..., description="The display name for the catalog category. This is the human-readable label shown in your catalog."),
    integration_type: Literal["$custom"] | None = Field(None, description="The integration type for this category. Currently only '$custom' is supported for custom integrations."),
    data: list[_models.CreateCatalogCategoryBodyDataRelationshipsItemsDataItem] | None = Field(None, description="Optional array of custom data fields to attach to this category. Item format and order significance depend on your integration requirements."),
) -> dict[str, Any]:
    """Create a new catalog category in your product catalog. The category will be identified by an external system ID and can include custom metadata."""

    # Construct request model with validation
    try:
        _request = _models.CreateCatalogCategoryRequest(
            header=_models.CreateCatalogCategoryRequestHeader(revision=revision),
            body=_models.CreateCatalogCategoryRequestBody(data=_models.CreateCatalogCategoryRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateCatalogCategoryRequestBodyDataAttributes(external_id=external_id, name=name, integration_type=integration_type),
                    relationships=_models.CreateCatalogCategoryRequestBodyDataRelationships(items=_models.CreateCatalogCategoryRequestBodyDataRelationshipsItems(data=data) if any(v is not None for v in [data]) else None) if any(v is not None for v in [data]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_catalog_category: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/catalog-categories"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_catalog_category")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_catalog_category", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_catalog_category",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def get_catalog_category(
    id_: str = Field(..., alias="id", description="The compound identifier for the catalog category, formatted as `{integration}:::{catalog}:::{external_id}`. Currently supports only the `$custom` integration type and `$default` catalog. The external ID is a custom string that uniquely identifies the category within the catalog."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, optionally followed by a suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve a specific catalog category by its compound ID. The category ID combines integration type, catalog name, and external identifier to uniquely identify the category."""

    # Construct request model with validation
    try:
        _request = _models.GetCatalogCategoryRequest(
            path=_models.GetCatalogCategoryRequestPath(id_=id_),
            header=_models.GetCatalogCategoryRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_catalog_category: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/catalog-categories/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/catalog-categories/{id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_catalog_category")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_catalog_category", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_catalog_category",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def update_catalog_category(
    id_: str = Field(..., alias="id", description="The catalog category identifier in compound format: {integration}:::{catalog}:::{external_id}. Use $custom for integration and $default for catalog, followed by your category's external ID (e.g., $custom:::$default:::SAMPLE-DATA-CATEGORY-APPAREL)."),
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix. Defaults to 2026-01-15 if not specified."),
    data_id: str = Field(..., alias="dataId", description="The catalog category identifier in compound format: {integration}:::{catalog}:::{external_id}. Must match the path ID and use $custom for integration and $default for catalog (e.g., $custom:::$default:::SAMPLE-DATA-CATEGORY-APPAREL)."),
    type_: Literal["catalog-category"] = Field(..., alias="type", description="The resource type identifier. Must be set to 'catalog-category' for this operation."),
    name: str | None = Field(None, description="The display name for the catalog category (e.g., 'Sample Data Category Apparel'). Optional field for updating category metadata."),
    data: list[_models.UpdateCatalogCategoryBodyDataRelationshipsItemsDataItem] | None = Field(None, description="Additional structured data for the catalog category. Format and contents depend on the specific catalog structure requirements."),
) -> dict[str, Any]:
    """Update an existing catalog category by ID. Modifies category metadata such as name while maintaining the compound ID structure."""

    # Construct request model with validation
    try:
        _request = _models.UpdateCatalogCategoryRequest(
            path=_models.UpdateCatalogCategoryRequestPath(id_=id_),
            header=_models.UpdateCatalogCategoryRequestHeader(revision=revision),
            body=_models.UpdateCatalogCategoryRequestBody(data=_models.UpdateCatalogCategoryRequestBodyData(
                    id_=data_id, type_=type_,
                    attributes=_models.UpdateCatalogCategoryRequestBodyDataAttributes(name=name) if any(v is not None for v in [name]) else None,
                    relationships=_models.UpdateCatalogCategoryRequestBodyDataRelationships(items=_models.UpdateCatalogCategoryRequestBodyDataRelationshipsItems(data=data) if any(v is not None for v in [data]) else None) if any(v is not None for v in [data]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_catalog_category: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/catalog-categories/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/catalog-categories/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_catalog_category")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_catalog_category", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_catalog_category",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def delete_catalog_category(
    id_: str = Field(..., alias="id", description="The compound identifier for the catalog category, formatted as {integration}:::{catalog}:::{external_id}. Use $custom as the integration and $default as the catalog name."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Permanently delete a catalog category by its compound ID. The category ID must follow the format {integration}:::{catalog}:::{external_id}, where integration is $custom and catalog is $default."""

    # Construct request model with validation
    try:
        _request = _models.DeleteCatalogCategoryRequest(
            path=_models.DeleteCatalogCategoryRequestPath(id_=id_),
            header=_models.DeleteCatalogCategoryRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_catalog_category: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/catalog-categories/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/catalog-categories/{id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_catalog_category")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_catalog_category", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_catalog_category",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def list_bulk_create_catalog_items_jobs(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix. Defaults to 2026-01-15 if not specified."),
    filter_: str | None = Field(None, alias="filter", description="Filter results by job status using the equals operator (e.g., to show only processing jobs). Supports the status field only."),
) -> dict[str, Any]:
    """Retrieve all catalog item bulk create jobs with optional filtering by status. Returns up to 100 jobs per request."""

    # Construct request model with validation
    try:
        _request = _models.GetBulkCreateCatalogItemsJobsRequest(
            query=_models.GetBulkCreateCatalogItemsJobsRequestQuery(filter_=filter_),
            header=_models.GetBulkCreateCatalogItemsJobsRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_bulk_create_catalog_items_jobs: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/catalog-item-bulk-create-jobs"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_bulk_create_catalog_items_jobs")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_bulk_create_catalog_items_jobs", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_bulk_create_catalog_items_jobs",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def create_catalog_items_bulk_job(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.v1). Defaults to 2026-01-15 if not specified."),
    type_: Literal["catalog-item-bulk-create-job"] = Field(..., alias="type", description="The job type identifier. Must be set to 'catalog-item-bulk-create-job' to specify this operation creates catalog items in bulk."),
    data: list[_models.CatalogItemCreateQueryResourceObject] = Field(..., description="Array of catalog item objects to create. Accepts up to 100 items per request. Each item must conform to the catalog item schema. Order is preserved in processing."),
) -> dict[str, Any]:
    """Initiate a bulk job to create up to 100 catalog items in a single request. The operation queues the job for asynchronous processing with a maximum payload size of 5MB and a limit of 500 concurrent jobs."""

    # Construct request model with validation
    try:
        _request = _models.BulkCreateCatalogItemsRequest(
            header=_models.BulkCreateCatalogItemsRequestHeader(revision=revision),
            body=_models.BulkCreateCatalogItemsRequestBody(data=_models.BulkCreateCatalogItemsRequestBodyData(
                    type_=type_,
                    attributes=_models.BulkCreateCatalogItemsRequestBodyDataAttributes(
                        items=_models.BulkCreateCatalogItemsRequestBodyDataAttributesItems(data=data)
                    )
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_catalog_items_bulk_job: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/catalog-item-bulk-create-jobs"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_catalog_items_bulk_job")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_catalog_items_bulk_job", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_catalog_items_bulk_job",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def get_bulk_create_catalog_items_job(
    job_id: str = Field(..., description="The unique identifier of the bulk create job to retrieve (e.g., 01GSQPBF74KQ5YTDEPP41T1BZH)."),
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15). Specifies which API version to use for this request."),
) -> dict[str, Any]:
    """Retrieve the status and details of a catalog item bulk create job by its ID. Optionally include related catalog items in the response."""

    # Construct request model with validation
    try:
        _request = _models.GetBulkCreateCatalogItemsJobRequest(
            path=_models.GetBulkCreateCatalogItemsJobRequestPath(job_id=job_id),
            header=_models.GetBulkCreateCatalogItemsJobRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_bulk_create_catalog_items_job: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/catalog-item-bulk-create-jobs/{job_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/catalog-item-bulk-create-jobs/{job_id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_bulk_create_catalog_items_job")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_bulk_create_catalog_items_job", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_bulk_create_catalog_items_job",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def list_catalog_item_bulk_update_jobs(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix. Defaults to 2026-01-15 if not specified."),
    filter_: str | None = Field(None, alias="filter", description="Filter results by job status using the equals operator (e.g., to retrieve only processing jobs). Supports the status field only."),
) -> dict[str, Any]:
    """Retrieve all catalog item bulk update jobs with optional filtering by status. Returns up to 100 jobs per request."""

    # Construct request model with validation
    try:
        _request = _models.GetBulkUpdateCatalogItemsJobsRequest(
            query=_models.GetBulkUpdateCatalogItemsJobsRequestQuery(filter_=filter_),
            header=_models.GetBulkUpdateCatalogItemsJobsRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_catalog_item_bulk_update_jobs: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/catalog-item-bulk-update-jobs"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_catalog_item_bulk_update_jobs")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_catalog_item_bulk_update_jobs", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_catalog_item_bulk_update_jobs",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def create_catalog_item_bulk_update_job(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.v1). Defaults to 2026-01-15 if not specified."),
    type_: Literal["catalog-item-bulk-update-job"] = Field(..., alias="type", description="The type of bulk operation job being created. Must be set to 'catalog-item-bulk-update-job' to indicate this is a catalog item update operation."),
    data: list[_models.CatalogItemUpdateQueryResourceObject] = Field(..., description="Array of catalog items to update. Each item should contain the fields to be modified. Maximum 100 items per request; total payload cannot exceed 5MB."),
) -> dict[str, Any]:
    """Create a bulk update job to modify up to 100 catalog items in a single request. The job processes asynchronously and you can have up to 500 jobs in progress simultaneously."""

    # Construct request model with validation
    try:
        _request = _models.BulkUpdateCatalogItemsRequest(
            header=_models.BulkUpdateCatalogItemsRequestHeader(revision=revision),
            body=_models.BulkUpdateCatalogItemsRequestBody(data=_models.BulkUpdateCatalogItemsRequestBodyData(
                    type_=type_,
                    attributes=_models.BulkUpdateCatalogItemsRequestBodyDataAttributes(
                        items=_models.BulkUpdateCatalogItemsRequestBodyDataAttributesItems(data=data)
                    )
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_catalog_item_bulk_update_job: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/catalog-item-bulk-update-jobs"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_catalog_item_bulk_update_job")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_catalog_item_bulk_update_job", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_catalog_item_bulk_update_job",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def get_bulk_update_catalog_items_job(
    job_id: str = Field(..., description="The unique identifier of the bulk update job to retrieve (e.g., 01GSQPBF74KQ5YTDEPP41T1BZH)."),
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15). Specifies which API version to use for this request."),
) -> dict[str, Any]:
    """Retrieve the status and details of a catalog item bulk update job by its ID. Optionally include related catalog items in the response."""

    # Construct request model with validation
    try:
        _request = _models.GetBulkUpdateCatalogItemsJobRequest(
            path=_models.GetBulkUpdateCatalogItemsJobRequestPath(job_id=job_id),
            header=_models.GetBulkUpdateCatalogItemsJobRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_bulk_update_catalog_items_job: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/catalog-item-bulk-update-jobs/{job_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/catalog-item-bulk-update-jobs/{job_id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_bulk_update_catalog_items_job")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_bulk_update_catalog_items_job", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_bulk_update_catalog_items_job",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def list_bulk_delete_catalog_items_jobs(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format (or with optional suffix). Defaults to 2026-01-15 if not specified."),
    filter_: str | None = Field(None, alias="filter", description="Filter results by job status using the equals operator (e.g., to show only processing jobs). Omit to retrieve jobs in all statuses."),
) -> dict[str, Any]:
    """Retrieve all catalog item bulk delete jobs with optional filtering by status. Returns up to 100 jobs per request."""

    # Construct request model with validation
    try:
        _request = _models.GetBulkDeleteCatalogItemsJobsRequest(
            query=_models.GetBulkDeleteCatalogItemsJobsRequestQuery(filter_=filter_),
            header=_models.GetBulkDeleteCatalogItemsJobsRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_bulk_delete_catalog_items_jobs: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/catalog-item-bulk-delete-jobs"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_bulk_delete_catalog_items_jobs")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_bulk_delete_catalog_items_jobs", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_bulk_delete_catalog_items_jobs",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def create_catalog_item_bulk_delete_job(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15). Specifies which API version to use for this operation."),
    type_: Literal["catalog-item-bulk-delete-job"] = Field(..., alias="type", description="The job type identifier. Must be set to 'catalog-item-bulk-delete-job' to indicate this is a bulk delete operation."),
    data: list[_models.CatalogItemDeleteQueryResourceObject] = Field(..., description="Array of catalog items to delete. Submit up to 100 items per request. Each item should contain the necessary identifiers for deletion."),
) -> dict[str, Any]:
    """Create a bulk delete job to remove a batch of catalog items. Submit up to 100 items per request with a maximum payload of 5MB, and maintain no more than 500 concurrent jobs."""

    # Construct request model with validation
    try:
        _request = _models.BulkDeleteCatalogItemsRequest(
            header=_models.BulkDeleteCatalogItemsRequestHeader(revision=revision),
            body=_models.BulkDeleteCatalogItemsRequestBody(data=_models.BulkDeleteCatalogItemsRequestBodyData(
                    type_=type_,
                    attributes=_models.BulkDeleteCatalogItemsRequestBodyDataAttributes(
                        items=_models.BulkDeleteCatalogItemsRequestBodyDataAttributesItems(data=data)
                    )
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_catalog_item_bulk_delete_job: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/catalog-item-bulk-delete-jobs"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_catalog_item_bulk_delete_job")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_catalog_item_bulk_delete_job", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_catalog_item_bulk_delete_job",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def get_bulk_delete_catalog_items_job(
    job_id: str = Field(..., description="The unique identifier of the bulk delete job to retrieve. This ID is returned when the bulk delete operation is initiated."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve the status and details of a catalog item bulk delete job by its ID. Use this to monitor the progress of an in-progress or completed bulk deletion operation."""

    # Construct request model with validation
    try:
        _request = _models.GetBulkDeleteCatalogItemsJobRequest(
            path=_models.GetBulkDeleteCatalogItemsJobRequestPath(job_id=job_id),
            header=_models.GetBulkDeleteCatalogItemsJobRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_bulk_delete_catalog_items_job: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/catalog-item-bulk-delete-jobs/{job_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/catalog-item-bulk-delete-jobs/{job_id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_bulk_delete_catalog_items_job")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_bulk_delete_catalog_items_job", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_bulk_delete_catalog_items_job",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def list_bulk_create_variants_jobs(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix. Defaults to 2026-01-15 if not specified."),
    filter_: str | None = Field(None, alias="filter", description="Filter results by job status using the equals operator (e.g., to retrieve only processing jobs). Omit to return jobs of all statuses."),
) -> dict[str, Any]:
    """Retrieve all catalog variant bulk create jobs with optional filtering by status. Returns up to 100 jobs per request."""

    # Construct request model with validation
    try:
        _request = _models.GetBulkCreateVariantsJobsRequest(
            query=_models.GetBulkCreateVariantsJobsRequestQuery(filter_=filter_),
            header=_models.GetBulkCreateVariantsJobsRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_bulk_create_variants_jobs: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/catalog-variant-bulk-create-jobs"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_bulk_create_variants_jobs")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_bulk_create_variants_jobs", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_bulk_create_variants_jobs",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def create_catalog_variants_bulk(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.beta). Defaults to 2026-01-15 if not specified."),
    type_: Literal["catalog-variant-bulk-create-job"] = Field(..., alias="type", description="The job type identifier. Must be set to 'catalog-variant-bulk-create-job' to specify this operation."),
    data: list[_models.CatalogVariantCreateQueryResourceObject] = Field(..., description="Array of catalog variant objects to create. Accepts up to 100 variants per request with a maximum payload size of 5MB. Each item represents a single catalog variant to be created."),
) -> dict[str, Any]:
    """Initiate a bulk job to create up to 100 catalog variants in a single request. The job processes asynchronously and allows up to 500 concurrent jobs per account."""

    # Construct request model with validation
    try:
        _request = _models.BulkCreateCatalogVariantsRequest(
            header=_models.BulkCreateCatalogVariantsRequestHeader(revision=revision),
            body=_models.BulkCreateCatalogVariantsRequestBody(data=_models.BulkCreateCatalogVariantsRequestBodyData(
                    type_=type_,
                    attributes=_models.BulkCreateCatalogVariantsRequestBodyDataAttributes(
                        variants=_models.BulkCreateCatalogVariantsRequestBodyDataAttributesVariants(data=data)
                    )
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_catalog_variants_bulk: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/catalog-variant-bulk-create-jobs"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_catalog_variants_bulk")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_catalog_variants_bulk", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_catalog_variants_bulk",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def get_bulk_create_variants_job(
    job_id: str = Field(..., description="The unique identifier of the bulk create job to retrieve (format: alphanumeric string)."),
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15 if not specified)."),
) -> dict[str, Any]:
    """Retrieve the status and details of a catalog variant bulk create job by its ID. Optionally include related variant data in the response."""

    # Construct request model with validation
    try:
        _request = _models.GetBulkCreateVariantsJobRequest(
            path=_models.GetBulkCreateVariantsJobRequestPath(job_id=job_id),
            header=_models.GetBulkCreateVariantsJobRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_bulk_create_variants_job: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/catalog-variant-bulk-create-jobs/{job_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/catalog-variant-bulk-create-jobs/{job_id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_bulk_create_variants_job")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_bulk_create_variants_job", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_bulk_create_variants_job",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def list_bulk_update_variants_jobs(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix. Defaults to 2026-01-15 if not specified."),
    filter_: str | None = Field(None, alias="filter", description="Filter results by job status using the equals operator (e.g., to retrieve only processing jobs). Supports filtering on the status field only."),
) -> dict[str, Any]:
    """Retrieve all catalog variant bulk update jobs with optional filtering by status. Returns up to 100 jobs per request."""

    # Construct request model with validation
    try:
        _request = _models.GetBulkUpdateVariantsJobsRequest(
            query=_models.GetBulkUpdateVariantsJobsRequestQuery(filter_=filter_),
            header=_models.GetBulkUpdateVariantsJobsRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_bulk_update_variants_jobs: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/catalog-variant-bulk-update-jobs"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_bulk_update_variants_jobs")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_bulk_update_variants_jobs", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_bulk_update_variants_jobs",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def create_catalog_variant_bulk_update_job(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.beta). Defaults to 2026-01-15 if not specified."),
    type_: Literal["catalog-variant-bulk-update-job"] = Field(..., alias="type", description="The job type identifier. Must be set to 'catalog-variant-bulk-update-job' to indicate this is a bulk variant update operation."),
    data: list[_models.CatalogVariantUpdateQueryResourceObject] = Field(..., description="Array of catalog variant objects to update. Accepts up to 100 variants per request with a maximum payload size of 5MB. Order is preserved for processing."),
) -> dict[str, Any]:
    """Create a bulk update job to modify up to 100 catalog variants in a single request. The job processes asynchronously with a maximum of 500 concurrent jobs allowed per account."""

    # Construct request model with validation
    try:
        _request = _models.BulkUpdateCatalogVariantsRequest(
            header=_models.BulkUpdateCatalogVariantsRequestHeader(revision=revision),
            body=_models.BulkUpdateCatalogVariantsRequestBody(data=_models.BulkUpdateCatalogVariantsRequestBodyData(
                    type_=type_,
                    attributes=_models.BulkUpdateCatalogVariantsRequestBodyDataAttributes(
                        variants=_models.BulkUpdateCatalogVariantsRequestBodyDataAttributesVariants(data=data)
                    )
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_catalog_variant_bulk_update_job: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/catalog-variant-bulk-update-jobs"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_catalog_variant_bulk_update_job")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_catalog_variant_bulk_update_job", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_catalog_variant_bulk_update_job",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def get_bulk_update_variants_job(
    job_id: str = Field(..., description="The unique identifier of the bulk update job to retrieve."),
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15)."),
) -> dict[str, Any]:
    """Retrieve the status and details of a catalog variant bulk update job by its ID. Optionally include related variant data in the response."""

    # Construct request model with validation
    try:
        _request = _models.GetBulkUpdateVariantsJobRequest(
            path=_models.GetBulkUpdateVariantsJobRequestPath(job_id=job_id),
            header=_models.GetBulkUpdateVariantsJobRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_bulk_update_variants_job: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/catalog-variant-bulk-update-jobs/{job_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/catalog-variant-bulk-update-jobs/{job_id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_bulk_update_variants_job")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_bulk_update_variants_job", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_bulk_update_variants_job",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def list_bulk_delete_variants_jobs(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix. Defaults to 2026-01-15 if not specified."),
    filter_: str | None = Field(None, alias="filter", description="Filter results by job status using the equals operator (e.g., to show only processing jobs). Omit to retrieve jobs in all statuses."),
) -> dict[str, Any]:
    """Retrieve all catalog variant bulk delete jobs with optional filtering by status. Returns up to 100 jobs per request."""

    # Construct request model with validation
    try:
        _request = _models.GetBulkDeleteVariantsJobsRequest(
            query=_models.GetBulkDeleteVariantsJobsRequestQuery(filter_=filter_),
            header=_models.GetBulkDeleteVariantsJobsRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_bulk_delete_variants_jobs: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/catalog-variant-bulk-delete-jobs"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_bulk_delete_variants_jobs")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_bulk_delete_variants_jobs", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_bulk_delete_variants_jobs",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def create_catalog_variant_bulk_delete_job(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15). Specifies which API version to use for this operation."),
    type_: Literal["catalog-variant-bulk-delete-job"] = Field(..., alias="type", description="The type of bulk job being created. Must be set to 'catalog-variant-bulk-delete-job' to indicate this is a variant deletion operation."),
    data: list[_models.CatalogVariantDeleteQueryResourceObject] = Field(..., description="Array of catalog variant identifiers to delete. Accepts up to 100 variants per request with a maximum payload size of 5MB. Order is not significant."),
) -> dict[str, Any]:
    """Create a bulk delete job to remove up to 100 catalog variants in a single request. The job is processed asynchronously, with a maximum of 500 jobs allowed in progress simultaneously."""

    # Construct request model with validation
    try:
        _request = _models.BulkDeleteCatalogVariantsRequest(
            header=_models.BulkDeleteCatalogVariantsRequestHeader(revision=revision),
            body=_models.BulkDeleteCatalogVariantsRequestBody(data=_models.BulkDeleteCatalogVariantsRequestBodyData(
                    type_=type_,
                    attributes=_models.BulkDeleteCatalogVariantsRequestBodyDataAttributes(
                        variants=_models.BulkDeleteCatalogVariantsRequestBodyDataAttributesVariants(data=data)
                    )
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_catalog_variant_bulk_delete_job: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/catalog-variant-bulk-delete-jobs"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_catalog_variant_bulk_delete_job")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_catalog_variant_bulk_delete_job", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_catalog_variant_bulk_delete_job",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def get_bulk_delete_variants_job(
    job_id: str = Field(..., description="The unique identifier of the bulk delete job to retrieve. This ID is returned when the job is initially created."),
    revision: str = Field(..., description="The API endpoint revision in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve the status and details of a catalog variant bulk delete job by its ID. Use this to monitor the progress and outcome of asynchronous variant deletion operations."""

    # Construct request model with validation
    try:
        _request = _models.GetBulkDeleteVariantsJobRequest(
            path=_models.GetBulkDeleteVariantsJobRequestPath(job_id=job_id),
            header=_models.GetBulkDeleteVariantsJobRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_bulk_delete_variants_job: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/catalog-variant-bulk-delete-jobs/{job_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/catalog-variant-bulk-delete-jobs/{job_id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_bulk_delete_variants_job")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_bulk_delete_variants_job", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_bulk_delete_variants_job",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def list_bulk_create_categories_jobs(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix. Defaults to 2026-01-15 if not specified."),
    filter_: str | None = Field(None, alias="filter", description="Filter results by job status using the equals operator (e.g., to retrieve only processing jobs). Supports the status field only."),
) -> dict[str, Any]:
    """Retrieve all catalog category bulk create jobs with optional filtering by status. Returns up to 100 jobs per request."""

    # Construct request model with validation
    try:
        _request = _models.GetBulkCreateCategoriesJobsRequest(
            query=_models.GetBulkCreateCategoriesJobsRequestQuery(filter_=filter_),
            header=_models.GetBulkCreateCategoriesJobsRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_bulk_create_categories_jobs: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/catalog-category-bulk-create-jobs"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_bulk_create_categories_jobs")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_bulk_create_categories_jobs", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_bulk_create_categories_jobs",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def create_catalog_categories_bulk_job(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.beta). Defaults to 2026-01-15 if not specified."),
    type_: Literal["catalog-category-bulk-create-job"] = Field(..., alias="type", description="The job type identifier. Must be set to 'catalog-category-bulk-create-job' to specify this operation creates catalog categories."),
    data: list[_models.CatalogCategoryCreateQueryResourceObject] = Field(..., description="Array of catalog category objects to create. Accepts up to 100 items per request with a maximum payload size of 5MB. Order is preserved for processing."),
) -> dict[str, Any]:
    """Initiate a bulk job to create up to 100 catalog categories in a single request. The job processes asynchronously and allows up to 500 concurrent jobs per account."""

    # Construct request model with validation
    try:
        _request = _models.BulkCreateCatalogCategoriesRequest(
            header=_models.BulkCreateCatalogCategoriesRequestHeader(revision=revision),
            body=_models.BulkCreateCatalogCategoriesRequestBody(data=_models.BulkCreateCatalogCategoriesRequestBodyData(
                    type_=type_,
                    attributes=_models.BulkCreateCatalogCategoriesRequestBodyDataAttributes(
                        categories=_models.BulkCreateCatalogCategoriesRequestBodyDataAttributesCategories(data=data)
                    )
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_catalog_categories_bulk_job: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/catalog-category-bulk-create-jobs"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_catalog_categories_bulk_job")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_catalog_categories_bulk_job", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_catalog_categories_bulk_job",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def get_bulk_create_categories_job(
    job_id: str = Field(..., description="The unique identifier of the bulk create job to retrieve (format: alphanumeric string)."),
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15 if not specified)."),
) -> dict[str, Any]:
    """Retrieve the status and details of a catalog category bulk create job by its ID. Optionally include related category resources in the response."""

    # Construct request model with validation
    try:
        _request = _models.GetBulkCreateCategoriesJobRequest(
            path=_models.GetBulkCreateCategoriesJobRequestPath(job_id=job_id),
            header=_models.GetBulkCreateCategoriesJobRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_bulk_create_categories_job: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/catalog-category-bulk-create-jobs/{job_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/catalog-category-bulk-create-jobs/{job_id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_bulk_create_categories_job")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_bulk_create_categories_job", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_bulk_create_categories_job",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def list_bulk_update_categories_jobs(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix. Defaults to 2026-01-15 if not specified."),
    filter_: str | None = Field(None, alias="filter", description="Filter results by job status using the equals operator (e.g., to retrieve only processing jobs). Supports filtering on the status field only."),
) -> dict[str, Any]:
    """Retrieve all catalog category bulk update jobs with optional filtering by status. Returns up to 100 jobs per request."""

    # Construct request model with validation
    try:
        _request = _models.GetBulkUpdateCategoriesJobsRequest(
            query=_models.GetBulkUpdateCategoriesJobsRequestQuery(filter_=filter_),
            header=_models.GetBulkUpdateCategoriesJobsRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_bulk_update_categories_jobs: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/catalog-category-bulk-update-jobs"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_bulk_update_categories_jobs")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_bulk_update_categories_jobs", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_bulk_update_categories_jobs",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def create_catalog_category_bulk_update_job(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.beta). Defaults to 2026-01-15 if not specified."),
    type_: Literal["catalog-category-bulk-update-job"] = Field(..., alias="type", description="The job type identifier. Must be set to 'catalog-category-bulk-update-job' to indicate this is a bulk category update operation."),
    data: list[_models.CatalogCategoryUpdateQueryResourceObject] = Field(..., description="Array of catalog category objects to update. Supports up to 100 categories per request with a maximum payload size of 5MB. Order is preserved for processing."),
) -> dict[str, Any]:
    """Create a bulk update job to modify up to 100 catalog categories in a single request. The job processes asynchronously with a maximum of 500 concurrent jobs allowed per account."""

    # Construct request model with validation
    try:
        _request = _models.BulkUpdateCatalogCategoriesRequest(
            header=_models.BulkUpdateCatalogCategoriesRequestHeader(revision=revision),
            body=_models.BulkUpdateCatalogCategoriesRequestBody(data=_models.BulkUpdateCatalogCategoriesRequestBodyData(
                    type_=type_,
                    attributes=_models.BulkUpdateCatalogCategoriesRequestBodyDataAttributes(
                        categories=_models.BulkUpdateCatalogCategoriesRequestBodyDataAttributesCategories(data=data)
                    )
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_catalog_category_bulk_update_job: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/catalog-category-bulk-update-jobs"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_catalog_category_bulk_update_job")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_catalog_category_bulk_update_job", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_catalog_category_bulk_update_job",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def get_bulk_update_categories_job(
    job_id: str = Field(..., description="The unique identifier of the bulk update job to retrieve (e.g., 01GSQPBF74KQ5YTDEPP41T1BZH)."),
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15 if not specified)."),
) -> dict[str, Any]:
    """Retrieve the status and details of a catalog category bulk update job by its ID. Optionally include related category data in the response."""

    # Construct request model with validation
    try:
        _request = _models.GetBulkUpdateCategoriesJobRequest(
            path=_models.GetBulkUpdateCategoriesJobRequestPath(job_id=job_id),
            header=_models.GetBulkUpdateCategoriesJobRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_bulk_update_categories_job: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/catalog-category-bulk-update-jobs/{job_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/catalog-category-bulk-update-jobs/{job_id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_bulk_update_categories_job")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_bulk_update_categories_job", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_bulk_update_categories_job",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def list_bulk_delete_categories_jobs(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix. Defaults to 2026-01-15 if not specified."),
    filter_: str | None = Field(None, alias="filter", description="Filter results by job status using the equals operator (e.g., to retrieve only processing jobs). Omit to return jobs in all statuses."),
) -> dict[str, Any]:
    """Retrieve all catalog category bulk delete jobs with optional filtering by status. Returns up to 100 jobs per request."""

    # Construct request model with validation
    try:
        _request = _models.GetBulkDeleteCategoriesJobsRequest(
            query=_models.GetBulkDeleteCategoriesJobsRequestQuery(filter_=filter_),
            header=_models.GetBulkDeleteCategoriesJobsRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_bulk_delete_categories_jobs: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/catalog-category-bulk-delete-jobs"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_bulk_delete_categories_jobs")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_bulk_delete_categories_jobs", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_bulk_delete_categories_jobs",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def create_catalog_category_bulk_delete_job(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.v1). Defaults to 2026-01-15 if not specified."),
    type_: Literal["catalog-category-bulk-delete-job"] = Field(..., alias="type", description="The type of bulk job being created. Must be set to 'catalog-category-bulk-delete-job' to indicate this is a catalog category deletion operation."),
    data: list[_models.CatalogCategoryDeleteQueryResourceObject] = Field(..., description="Array of catalog category identifiers to delete. Accepts up to 100 categories per request. The total payload size must not exceed 5MB."),
) -> dict[str, Any]:
    """Create a bulk delete job to remove up to 100 catalog categories in a single request. The job is processed asynchronously and you can have up to 500 jobs in progress simultaneously."""

    # Construct request model with validation
    try:
        _request = _models.BulkDeleteCatalogCategoriesRequest(
            header=_models.BulkDeleteCatalogCategoriesRequestHeader(revision=revision),
            body=_models.BulkDeleteCatalogCategoriesRequestBody(data=_models.BulkDeleteCatalogCategoriesRequestBodyData(
                    type_=type_,
                    attributes=_models.BulkDeleteCatalogCategoriesRequestBodyDataAttributes(
                        categories=_models.BulkDeleteCatalogCategoriesRequestBodyDataAttributesCategories(data=data)
                    )
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_catalog_category_bulk_delete_job: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/catalog-category-bulk-delete-jobs"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_catalog_category_bulk_delete_job")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_catalog_category_bulk_delete_job", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_catalog_category_bulk_delete_job",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def get_bulk_delete_categories_job(
    job_id: str = Field(..., description="The unique identifier of the bulk delete job to retrieve. This ID is returned when the bulk delete operation is initiated."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve the status and details of a catalog category bulk delete job by its ID. Use this to monitor the progress of an asynchronous bulk deletion operation."""

    # Construct request model with validation
    try:
        _request = _models.GetBulkDeleteCategoriesJobRequest(
            path=_models.GetBulkDeleteCategoriesJobRequestPath(job_id=job_id),
            header=_models.GetBulkDeleteCategoriesJobRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_bulk_delete_categories_job: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/catalog-category-bulk-delete-jobs/{job_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/catalog-category-bulk-delete-jobs/{job_id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_bulk_delete_categories_job")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_bulk_delete_categories_job", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_bulk_delete_categories_job",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def create_back_in_stock_subscription(
    revision: str = Field(..., description="API endpoint revision date in YYYY-MM-DD format with optional suffix. Defaults to 2026-01-15 if not specified."),
    type_: Literal["back-in-stock-subscription"] = Field(..., alias="type", description="Resource type identifier. Must be set to 'back-in-stock-subscription'."),
    profile_data_type: Literal["profile"] = Field(..., alias="profileDataType", description="Profile resource type identifier. Must be set to 'profile'."),
    variant_data_type: Literal["catalog-variant"] = Field(..., alias="variantDataType", description="Catalog variant resource type identifier. Must be set to 'catalog-variant'."),
    channels: list[Literal["EMAIL", "PUSH", "SMS", "WHATSAPP"]] = Field(..., description="One or more notification channels through which the profile will receive back in stock alerts. Valid channels are EMAIL and SMS. Multiple channels can be specified as a comma-separated list or array."),
    variant_data_id: str = Field(..., alias="variantDataId", description="The catalog variant ID for which to create the subscription. Format is integrationType:::catalogId:::externalId (e.g., $custom:::$default:::SAMPLE-DATA-ITEM-1-VARIANT-MEDIUM or $shopify:::$default:::33001893429341)."),
    profile_data_id: str | None = Field(None, alias="profileDataId", description="The unique identifier of the profile to subscribe. This is a Klaviyo-generated ID that uniquely identifies the profile in the system."),
    email: str | None = Field(None, description="The email address of the profile. Used to identify or create the profile if no profile ID is provided."),
    phone_number: str | None = Field(None, description="The phone number of the profile in E.164 format (e.g., +15005550006). Used to identify or create the profile if no profile ID is provided."),
    external_id: str | None = Field(None, description="An external identifier that links this Klaviyo profile to a profile in another system (such as a point-of-sale system). Format varies based on the external system."),
) -> dict[str, Any]:
    """Subscribe a profile to receive notifications when a catalog variant is back in stock. The profile can be identified by ID, email, phone number, or external ID, and will receive notifications through their preferred channels (email, SMS, or both)."""

    # Construct request model with validation
    try:
        _request = _models.CreateBackInStockSubscriptionRequest(
            header=_models.CreateBackInStockSubscriptionRequestHeader(revision=revision),
            body=_models.CreateBackInStockSubscriptionRequestBody(data=_models.CreateBackInStockSubscriptionRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateBackInStockSubscriptionRequestBodyDataAttributes(
                        channels=channels,
                        profile=_models.CreateBackInStockSubscriptionRequestBodyDataAttributesProfile(
                            data=_models.CreateBackInStockSubscriptionRequestBodyDataAttributesProfileData(
                                type_=profile_data_type, id_=profile_data_id,
                                attributes=_models.CreateBackInStockSubscriptionRequestBodyDataAttributesProfileDataAttributes(email=email, phone_number=phone_number, external_id=external_id) if any(v is not None for v in [email, phone_number, external_id]) else None
                            )
                        )
                    ),
                    relationships=_models.CreateBackInStockSubscriptionRequestBodyDataRelationships(
                        variant=_models.CreateBackInStockSubscriptionRequestBodyDataRelationshipsVariant(
                            data=_models.CreateBackInStockSubscriptionRequestBodyDataRelationshipsVariantData(type_=variant_data_type, id_=variant_data_id)
                        )
                    )
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_back_in_stock_subscription: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/back-in-stock-subscriptions"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_back_in_stock_subscription")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_back_in_stock_subscription", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_back_in_stock_subscription",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def list_items_for_catalog_category(
    id_: str | None = Field(..., alias="id", description="The catalog category identifier in compound format: `{integration}:::{catalog}:::{external_id}`. Use `$custom` for integration and `$default` for catalog, followed by your category's external ID (e.g., `$custom:::$default:::SAMPLE-DATA-CATEGORY-APPAREL`)."),
    revision: str = Field(..., description="API endpoint revision date in YYYY-MM-DD format (e.g., 2026-01-15). Defaults to the latest stable revision if not specified."),
    filter_: str | None = Field(None, alias="filter", description="Optional filter expression to narrow results. Supports filtering by item IDs (any match), category ID (exact match), item title (contains), or publication status (exact match). Use the format specified in Klaviyo's filtering documentation."),
) -> dict[str, Any]:
    """Retrieve all items in a specific catalog category. Results can be sorted by creation date and filtered by item IDs, category, title, or publication status, with a maximum of 100 items returned per request."""

    # Construct request model with validation
    try:
        _request = _models.GetItemsForCatalogCategoryRequest(
            path=_models.GetItemsForCatalogCategoryRequestPath(id_=id_),
            query=_models.GetItemsForCatalogCategoryRequestQuery(filter_=filter_),
            header=_models.GetItemsForCatalogCategoryRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_items_for_catalog_category: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/catalog-categories/{id}/items", _request.path.model_dump(by_alias=True)) if _request.path else "/api/catalog-categories/{id}/items"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_items_for_catalog_category")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_items_for_catalog_category", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_items_for_catalog_category",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def list_item_ids_for_catalog_category(
    id_: str | None = Field(..., alias="id", description="The catalog category identifier in compound format: `{integration}:::{catalog}:::{external_id}`. Use `$custom` for integration and `$default` for catalog, followed by your external category ID (e.g., `$custom:::$default:::SAMPLE-DATA-CATEGORY-APPAREL`)."),
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format (or with optional suffix). Defaults to 2026-01-15 if not specified."),
    filter_: str | None = Field(None, alias="filter", description="Optional filter expression to narrow results. Supports filtering by item IDs (any match), category ID (exact match), item title (contains), or published status (exact match). Use the format specified in Klaviyo's filtering documentation."),
) -> dict[str, Any]:
    """Retrieve all item IDs belonging to a specific catalog category. Returns up to 100 items per request and supports filtering by item IDs, category, title, or publication status."""

    # Construct request model with validation
    try:
        _request = _models.GetItemIdsForCatalogCategoryRequest(
            path=_models.GetItemIdsForCatalogCategoryRequestPath(id_=id_),
            query=_models.GetItemIdsForCatalogCategoryRequestQuery(filter_=filter_),
            header=_models.GetItemIdsForCatalogCategoryRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_item_ids_for_catalog_category: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/catalog-categories/{id}/relationships/items", _request.path.model_dump(by_alias=True)) if _request.path else "/api/catalog-categories/{id}/relationships/items"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_item_ids_for_catalog_category")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_item_ids_for_catalog_category", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_item_ids_for_catalog_category",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def add_items_to_catalog_category(
    id_: str = Field(..., alias="id", description="The catalog category identifier in compound format: `{integration}:::{catalog}:::{external_id}`. Use `$custom` for the integration and `$default` for the catalog, followed by your category's external ID (e.g., `$custom:::$default:::SAMPLE-DATA-CATEGORY-APPAREL`)."),
    revision: str = Field(..., description="The API revision date in YYYY-MM-DD format, optionally with a suffix. Defaults to 2026-01-15 if not specified."),
    data: list[_models.AddItemsToCatalogCategoryBodyDataItem] = Field(..., description="An array of item objects to associate with the category. Each item in the array will be linked to the specified catalog category."),
) -> dict[str, Any]:
    """Associate one or more items with a catalog category by creating item relationships. This operation links items to the specified category within your catalog."""

    # Construct request model with validation
    try:
        _request = _models.AddItemsToCatalogCategoryRequest(
            path=_models.AddItemsToCatalogCategoryRequestPath(id_=id_),
            header=_models.AddItemsToCatalogCategoryRequestHeader(revision=revision),
            body=_models.AddItemsToCatalogCategoryRequestBody(data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_items_to_catalog_category: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/catalog-categories/{id}/relationships/items", _request.path.model_dump(by_alias=True)) if _request.path else "/api/catalog-categories/{id}/relationships/items"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_items_to_catalog_category")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_items_to_catalog_category", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_items_to_catalog_category",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def update_items_for_catalog_category(
    id_: str = Field(..., alias="id", description="The catalog category identifier in compound format: {integration}:::{catalog}:::{external_id}. Use integration type `$custom` and catalog `$default` with your external category ID (e.g., `$custom:::$default:::SAMPLE-DATA-CATEGORY-APPAREL`)."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, optionally followed by a suffix. Defaults to 2026-01-15 if not specified."),
    data: list[_models.UpdateItemsForCatalogCategoryBodyDataItem] = Field(..., description="An array of item relationship objects to associate with the category. Order and structure follow the JSON:API relationships specification."),
) -> dict[str, Any]:
    """Update the item relationships associated with a catalog category. This operation modifies which items are linked to the specified category."""

    # Construct request model with validation
    try:
        _request = _models.UpdateItemsForCatalogCategoryRequest(
            path=_models.UpdateItemsForCatalogCategoryRequestPath(id_=id_),
            header=_models.UpdateItemsForCatalogCategoryRequestHeader(revision=revision),
            body=_models.UpdateItemsForCatalogCategoryRequestBody(data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_items_for_catalog_category: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/catalog-categories/{id}/relationships/items", _request.path.model_dump(by_alias=True)) if _request.path else "/api/catalog-categories/{id}/relationships/items"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_items_for_catalog_category")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_items_for_catalog_category", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_items_for_catalog_category",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def remove_items_from_catalog_category(
    id_: str = Field(..., alias="id", description="The catalog category identifier in compound format: {integration}:::{catalog}:::{external_id}. Use $custom as the integration and $default as the catalog, followed by your external category ID (e.g., $custom:::$default:::SAMPLE-DATA-CATEGORY-APPAREL)."),
    revision: str = Field(..., description="The API revision date in YYYY-MM-DD format, optionally with a suffix. Defaults to 2026-01-15 if not specified."),
    data: list[_models.RemoveItemsFromCatalogCategoryBodyDataItem] = Field(..., description="Array of item identifiers to remove from the category. Each item in the array will be unlinked from the specified category."),
) -> dict[str, Any]:
    """Remove item relationships from a catalog category. Deletes the specified items from the given category, identified by its compound ID."""

    # Construct request model with validation
    try:
        _request = _models.RemoveItemsFromCatalogCategoryRequest(
            path=_models.RemoveItemsFromCatalogCategoryRequestPath(id_=id_),
            header=_models.RemoveItemsFromCatalogCategoryRequestHeader(revision=revision),
            body=_models.RemoveItemsFromCatalogCategoryRequestBody(data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_items_from_catalog_category: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/catalog-categories/{id}/relationships/items", _request.path.model_dump(by_alias=True)) if _request.path else "/api/catalog-categories/{id}/relationships/items"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_items_from_catalog_category")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_items_from_catalog_category", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_items_from_catalog_category",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def list_variants_for_catalog_item(
    id_: str | None = Field(..., alias="id", description="The catalog item identifier in compound format: `{integration}:::{catalog}:::{external_id}`. Currently only `$custom` integration and `$default` catalog are supported (e.g., `$custom:::$default:::SAMPLE-DATA-ITEM-1`)."),
    revision: str = Field(..., description="API revision date in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15). Specifies which API version to use for this request."),
    filter_: str | None = Field(None, alias="filter", description="Optional filter expression to narrow results. Supports filtering by variant IDs (any match), item ID (exact match), SKU (exact match), title (partial match), and published status (exact match). Use the Klaviyo filtering syntax for complex queries."),
) -> dict[str, Any]:
    """Retrieve all variants associated with a catalog item. Results can be sorted by creation date and are limited to 100 variants per request."""

    # Construct request model with validation
    try:
        _request = _models.GetVariantsForCatalogItemRequest(
            path=_models.GetVariantsForCatalogItemRequestPath(id_=id_),
            query=_models.GetVariantsForCatalogItemRequestQuery(filter_=filter_),
            header=_models.GetVariantsForCatalogItemRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_variants_for_catalog_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/catalog-items/{id}/variants", _request.path.model_dump(by_alias=True)) if _request.path else "/api/catalog-items/{id}/variants"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_variants_for_catalog_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_variants_for_catalog_item", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_variants_for_catalog_item",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def list_variant_ids_for_catalog_item(
    id_: str | None = Field(..., alias="id", description="The catalog item identifier in compound format: `{integration}:::{catalog}:::{external_id}`. Use `$custom` for integration and `$default` for catalog, followed by your external item ID (e.g., `$custom:::$default:::SAMPLE-DATA-ITEM-1`)."),
    revision: str = Field(..., description="API revision date in YYYY-MM-DD format (or with optional suffix). Defaults to 2026-01-15 if not specified."),
    filter_: str | None = Field(None, alias="filter", description="Optional filter expression to narrow results. Supports filtering by variant IDs (any match), item ID (exact match), SKU (exact match), title (partial match), and published status (exact match). Use the format specified in Klaviyo's filtering documentation."),
) -> dict[str, Any]:
    """Retrieve all variant IDs associated with a specific catalog item. Results can be filtered and sorted by creation date, with a maximum of 100 variants returned per request."""

    # Construct request model with validation
    try:
        _request = _models.GetVariantIdsForCatalogItemRequest(
            path=_models.GetVariantIdsForCatalogItemRequestPath(id_=id_),
            query=_models.GetVariantIdsForCatalogItemRequestQuery(filter_=filter_),
            header=_models.GetVariantIdsForCatalogItemRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_variant_ids_for_catalog_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/catalog-items/{id}/relationships/variants", _request.path.model_dump(by_alias=True)) if _request.path else "/api/catalog-items/{id}/relationships/variants"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_variant_ids_for_catalog_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_variant_ids_for_catalog_item", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_variant_ids_for_catalog_item",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def list_categories_for_catalog_item(
    id_: str | None = Field(..., alias="id", description="The catalog item identifier in compound format: `{integration}:::{catalog}:::{external_id}`. Use `$custom` for integration and `$default` for catalog, followed by your item's external ID."),
    revision: str = Field(..., description="API revision date in YYYY-MM-DD format (or with optional suffix). Defaults to the latest stable revision if not specified."),
    filter_: str | None = Field(None, alias="filter", description="Optional filter expression to narrow results by category IDs, item ID, or category name. Supports `ids` (any match), `item.id` (exact match), and `name` (partial match) operators."),
) -> dict[str, Any]:
    """Retrieve all catalog categories that contain a specific catalog item. Results can be sorted by creation date and are limited to 100 categories per request."""

    # Construct request model with validation
    try:
        _request = _models.GetCategoriesForCatalogItemRequest(
            path=_models.GetCategoriesForCatalogItemRequestPath(id_=id_),
            query=_models.GetCategoriesForCatalogItemRequestQuery(filter_=filter_),
            header=_models.GetCategoriesForCatalogItemRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_categories_for_catalog_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/catalog-items/{id}/categories", _request.path.model_dump(by_alias=True)) if _request.path else "/api/catalog-items/{id}/categories"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_categories_for_catalog_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_categories_for_catalog_item", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_categories_for_catalog_item",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def list_category_ids_for_catalog_item(
    id_: str | None = Field(..., alias="id", description="The catalog item identifier in compound format: `{integration}:::{catalog}:::{external_id}`. Use `$custom` for integration and `$default` for catalog, followed by your item's external ID."),
    revision: str = Field(..., description="API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to the latest stable version."),
    filter_: str | None = Field(None, alias="filter", description="Optional filter to narrow results by category IDs, item ID, or category name. Supports `ids` (any match), `item.id` (exact match), and `name` (partial match) operators."),
) -> dict[str, Any]:
    """Retrieve all catalog categories assigned to a specific catalog item. Returns up to 100 categories per request."""

    # Construct request model with validation
    try:
        _request = _models.GetCategoryIdsForCatalogItemRequest(
            path=_models.GetCategoryIdsForCatalogItemRequestPath(id_=id_),
            query=_models.GetCategoryIdsForCatalogItemRequestQuery(filter_=filter_),
            header=_models.GetCategoryIdsForCatalogItemRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_category_ids_for_catalog_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/catalog-items/{id}/relationships/categories", _request.path.model_dump(by_alias=True)) if _request.path else "/api/catalog-items/{id}/relationships/categories"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_category_ids_for_catalog_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_category_ids_for_catalog_item", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_category_ids_for_catalog_item",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def add_categories_to_catalog_item(
    id_: str = Field(..., alias="id", description="The unique identifier for the catalog item, formatted as a compound ID with three colon-separated segments: integration type, catalog name, and external ID (e.g., $custom:::$default:::SAMPLE-DATA-ITEM-1). Currently only the $custom integration and $default catalog are supported."),
    revision: str = Field(..., description="The API revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
    data: list[_models.AddCategoriesToCatalogItemBodyDataItem] = Field(..., description="An array of category objects to associate with the catalog item. Each entry represents a category relationship to create."),
) -> dict[str, Any]:
    """Associate one or more categories with a catalog item by creating category relationships. This operation links existing categories to the specified item in your catalog."""

    # Construct request model with validation
    try:
        _request = _models.AddCategoriesToCatalogItemRequest(
            path=_models.AddCategoriesToCatalogItemRequestPath(id_=id_),
            header=_models.AddCategoriesToCatalogItemRequestHeader(revision=revision),
            body=_models.AddCategoriesToCatalogItemRequestBody(data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_categories_to_catalog_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/catalog-items/{id}/relationships/categories", _request.path.model_dump(by_alias=True)) if _request.path else "/api/catalog-items/{id}/relationships/categories"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_categories_to_catalog_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_categories_to_catalog_item", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_categories_to_catalog_item",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def update_categories_for_catalog_item(
    id_: str = Field(..., alias="id", description="The unique identifier for the catalog item, formatted as a compound ID with three colon-separated segments: integration type, catalog name, and external ID. Use the format `$custom:::$default:::` followed by your item's external identifier."),
    revision: str = Field(..., description="The API revision date in YYYY-MM-DD format (with optional suffix). Defaults to 2026-01-15 if not specified."),
    data: list[_models.UpdateCategoriesForCatalogItemBodyDataItem] = Field(..., description="An array of category objects to associate with the catalog item. Each element defines a category relationship to be added or updated."),
) -> dict[str, Any]:
    """Update the category relationships for a specific catalog item. This operation allows you to modify which categories are associated with an item in your catalog."""

    # Construct request model with validation
    try:
        _request = _models.UpdateCategoriesForCatalogItemRequest(
            path=_models.UpdateCategoriesForCatalogItemRequestPath(id_=id_),
            header=_models.UpdateCategoriesForCatalogItemRequestHeader(revision=revision),
            body=_models.UpdateCategoriesForCatalogItemRequestBody(data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_categories_for_catalog_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/catalog-items/{id}/relationships/categories", _request.path.model_dump(by_alias=True)) if _request.path else "/api/catalog-items/{id}/relationships/categories"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_categories_for_catalog_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_categories_for_catalog_item", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_categories_for_catalog_item",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def remove_categories_from_catalog_item(
    id_: str = Field(..., alias="id", description="The catalog item identifier in compound format: {integration}:::{catalog}:::{external_id}. Use $custom for integration and $default for catalog, followed by your item's external ID (e.g., $custom:::$default:::SAMPLE-DATA-ITEM-1)."),
    revision: str = Field(..., description="The API revision date in YYYY-MM-DD format, optionally with a suffix. Defaults to 2026-01-15 if not specified."),
    data: list[_models.RemoveCategoriesFromCatalogItemBodyDataItem] = Field(..., description="Array of category relationship objects to remove from the catalog item. Each entry specifies a category to unlink."),
) -> dict[str, Any]:
    """Remove category relationships from a catalog item. Specify which categories to unlink from the item using a compound ID that identifies the integration, catalog, and external item reference."""

    # Construct request model with validation
    try:
        _request = _models.RemoveCategoriesFromCatalogItemRequest(
            path=_models.RemoveCategoriesFromCatalogItemRequestPath(id_=id_),
            header=_models.RemoveCategoriesFromCatalogItemRequestHeader(revision=revision),
            body=_models.RemoveCategoriesFromCatalogItemRequestBody(data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_categories_from_catalog_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/catalog-items/{id}/relationships/categories", _request.path.model_dump(by_alias=True)) if _request.path else "/api/catalog-items/{id}/relationships/categories"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_categories_from_catalog_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_categories_from_catalog_item", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_categories_from_catalog_item",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Coupons
@mcp.tool()
async def list_coupons(revision: str = Field(..., description="API endpoint revision date in YYYY-MM-DD format (or with an optional suffix). Defaults to 2026-01-15 if not specified.")) -> dict[str, Any]:
    """Retrieve all coupons in your Klaviyo account. Use this to view your complete coupon inventory and their details."""

    # Construct request model with validation
    try:
        _request = _models.GetCouponsRequest(
            header=_models.GetCouponsRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_coupons: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/coupons"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_coupons")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_coupons", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_coupons",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Coupons
@mcp.tool()
async def create_coupon(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.v2). Defaults to 2026-01-15 if not specified."),
    type_: Literal["coupon"] = Field(..., alias="type", description="The resource type identifier. Must be set to 'coupon' to indicate this operation creates a coupon resource."),
    external_id: str = Field(..., description="A unique identifier for this coupon in your external systems (such as Shopify or Magento). This ID is used to sync and reference the coupon across integrations."),
    description: str | None = Field(None, description="A human-readable description of the coupon's purpose and terms (e.g., discount percentage, minimum purchase requirements, or promotional details)."),
    monitor_configuration: dict[str, Any] | None = Field(None, description="Configuration settings for monitoring coupon health and usage. Specify thresholds such as low_balance_threshold to trigger alerts when coupon balance falls below a specified amount."),
) -> dict[str, Any]:
    """Creates a new coupon for use in promotions and discounts. Requires a unique external identifier that maps to your integrated systems like Shopify or Magento."""

    # Construct request model with validation
    try:
        _request = _models.CreateCouponRequest(
            header=_models.CreateCouponRequestHeader(revision=revision),
            body=_models.CreateCouponRequestBody(data=_models.CreateCouponRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateCouponRequestBodyDataAttributes(external_id=external_id, description=description, monitor_configuration=monitor_configuration)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_coupon: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/coupons"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_coupon")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_coupon", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_coupon",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Coupons
@mcp.tool()
async def get_coupon(
    id_: str = Field(..., alias="id", description="The unique identifier of the coupon to retrieve (e.g., '10OFF'). This ID is consistent across internal and external integration systems."),
    revision: str = Field(..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15). Specifies which version of the API contract to use for this request."),
) -> dict[str, Any]:
    """Retrieve a specific coupon by its ID. The coupon ID matches both the internal identifier and the external ID stored in integrated systems."""

    # Construct request model with validation
    try:
        _request = _models.GetCouponRequest(
            path=_models.GetCouponRequestPath(id_=id_),
            header=_models.GetCouponRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_coupon: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/coupons/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/coupons/{id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_coupon")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_coupon", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_coupon",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Coupons
@mcp.tool()
async def update_coupon(
    id_: str = Field(..., alias="id", description="The unique identifier of the coupon to update (e.g., '10OFF'). This ID is consistent between the internal system and external integrations."),
    revision: str = Field(..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15). Specifies which API contract version to use for this request."),
    data_id: str = Field(..., alias="dataId", description="The unique identifier of the coupon being updated (e.g., '10OFF'). Must match the ID in the path parameter."),
    type_: Literal["coupon"] = Field(..., alias="type", description="The resource type, which must be 'coupon' to identify this as a coupon update operation."),
    description: str | None = Field(None, description="A human-readable description of the coupon's purpose or offer (e.g., '10% off for purchases over $50'). Optional field for documentation purposes."),
    monitor_configuration: dict[str, Any] | None = Field(None, description="Configuration settings for monitoring the coupon's usage and health, such as balance thresholds. Accepts an object with monitoring parameters like low_balance_threshold."),
) -> dict[str, Any]:
    """Update an existing coupon's properties such as description and monitoring configuration. Requires the coupon ID and current revision for optimistic concurrency control."""

    # Construct request model with validation
    try:
        _request = _models.UpdateCouponRequest(
            path=_models.UpdateCouponRequestPath(id_=id_),
            header=_models.UpdateCouponRequestHeader(revision=revision),
            body=_models.UpdateCouponRequestBody(data=_models.UpdateCouponRequestBodyData(
                    id_=data_id, type_=type_,
                    attributes=_models.UpdateCouponRequestBodyDataAttributes(description=description, monitor_configuration=monitor_configuration) if any(v is not None for v in [description, monitor_configuration]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_coupon: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/coupons/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/coupons/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_coupon")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_coupon", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_coupon",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Coupons
@mcp.tool()
async def delete_coupon(
    id_: str = Field(..., alias="id", description="The unique identifier of the coupon to delete. This ID matches both the internal system ID and the external ID used in integrations (e.g., '10OFF')."),
    revision: str = Field(..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15). Specifies which version of the API contract to use for this request."),
) -> dict[str, Any]:
    """Permanently delete a coupon by its ID. This operation requires the coupons:write scope and is subject to rate limits of 3 requests per second (burst) and 60 requests per minute (steady state)."""

    # Construct request model with validation
    try:
        _request = _models.DeleteCouponRequest(
            path=_models.DeleteCouponRequestPath(id_=id_),
            header=_models.DeleteCouponRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_coupon: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/coupons/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/coupons/{id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_coupon")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_coupon", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_coupon",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Coupons
@mcp.tool()
async def list_coupon_codes(
    filter_: str = Field(..., alias="filter", description="Filter expression to narrow results by coupon ID(s), profile ID(s), expiration date range, or status. At least one coupon or profile filter is required. Use 'any' operator to match multiple IDs, 'equals' for single matches, and comparison operators (greater-than, less-than, etc.) for date ranges. Format: operator(field,'value') or operator(field,'value1','value2',...)"),
    revision: str = Field(..., description="API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve coupon codes filtered by coupon ID(s) and/or profile ID(s). Use filter parameters to specify which coupons or customer profiles to retrieve codes for, and optionally filter by expiration date or status."""

    # Construct request model with validation
    try:
        _request = _models.GetCouponCodesRequest(
            query=_models.GetCouponCodesRequestQuery(filter_=filter_),
            header=_models.GetCouponCodesRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_coupon_codes: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/coupon-codes"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_coupon_codes")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_coupon_codes", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_coupon_codes",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Coupons
@mcp.tool()
async def create_coupon_code(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15). Specifies which API version to use for this request."),
    type_: Literal["coupon-code"] = Field(..., alias="type", description="Resource type identifier; must be set to 'coupon-code' to indicate this is a coupon code resource."),
    coupon_data_type: Literal["coupon"] = Field(..., alias="couponDataType", description="Related resource type identifier; must be set to 'coupon' to indicate the relationship points to a coupon resource."),
    unique_code: str = Field(..., description="A unique alphanumeric string assigned to each customer or profile to identify and track this specific coupon code instance."),
    id_: str = Field(..., alias="id", description="Unique identifier for the coupon code (e.g., '10OFF'). Used as a reference key for this coupon code resource."),
    expires_at: str | None = Field(None, description="Optional expiration date and time in ISO 8601 format (e.g., 2022-11-08T00:00:00+00:00). If omitted or null, the code automatically expires 1 year from creation."),
) -> dict[str, Any]:
    """Creates a unique coupon code linked to a specific coupon, enabling per-customer or per-profile discount distribution. The code will automatically expire after 1 year unless a custom expiration date is provided."""

    # Construct request model with validation
    try:
        _request = _models.CreateCouponCodeRequest(
            header=_models.CreateCouponCodeRequestHeader(revision=revision),
            body=_models.CreateCouponCodeRequestBody(data=_models.CreateCouponCodeRequestBodyData(
                    type_=type_,
                    relationships=_models.CreateCouponCodeRequestBodyDataRelationships(
                        coupon=_models.CreateCouponCodeRequestBodyDataRelationshipsCoupon(
                            data=_models.CreateCouponCodeRequestBodyDataRelationshipsCouponData(type_=coupon_data_type, id_=id_)
                        )
                    ),
                    attributes=_models.CreateCouponCodeRequestBodyDataAttributes(unique_code=unique_code, expires_at=expires_at)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_coupon_code: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/coupon-codes"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_coupon_code")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_coupon_code", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_coupon_code",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Coupons
@mcp.tool()
async def get_coupon_code(
    id_: str = Field(..., alias="id", description="The combined identifier for the coupon code, consisting of the unique code and its associated coupon ID (e.g., '10OFF-ASD325FHK324UJDOI2M3JNES99')."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, optionally with a suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve a specific coupon code by its combined identifier (code + coupon ID). Returns the full coupon code details including associated metadata."""

    # Construct request model with validation
    try:
        _request = _models.GetCouponCodeRequest(
            path=_models.GetCouponCodeRequestPath(id_=id_),
            header=_models.GetCouponCodeRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_coupon_code: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/coupon-codes/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/coupon-codes/{id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_coupon_code")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_coupon_code", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_coupon_code",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Coupons
@mcp.tool()
async def update_coupon_code(
    id_: str = Field(..., alias="id", description="The unique identifier for the coupon code, formatted as the coupon code combined with its associated coupon ID (e.g., '10OFF-ASD325FHK324UJDOI2M3JNES99')."),
    revision: str = Field(..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix. Defaults to 2026-01-15 if not specified."),
    data_id: str = Field(..., alias="dataId", description="The unique identifier for the coupon code being updated, formatted as the coupon code combined with its associated coupon ID (e.g., '10OFF-ASD325FHK324UJDOI2M3JNES99'). Must match the path ID."),
    type_: Literal["coupon-code"] = Field(..., alias="type", description="The resource type identifier. Must be set to 'coupon-code'."),
    status: Literal["ASSIGNED_TO_PROFILE", "DELETING", "PROCESSING", "UNASSIGNED", "USED", "VERSION_NOT_ACTIVE"] | None = Field(None, description="The current status of the coupon code in the system. Valid statuses include: ASSIGNED_TO_PROFILE (linked to a customer), UNASSIGNED (available for use), USED (already redeemed), PROCESSING (being created), DELETING (being removed), or VERSION_NOT_ACTIVE (associated coupon is inactive)."),
    expires_at: str | None = Field(None, description="The date and time when this coupon code expires, specified in ISO 8601 format with timezone (e.g., '2022-11-08T00:00:00+00:00'). If omitted or set to null, the expiration will automatically default to one year from the current date."),
) -> dict[str, Any]:
    """Update the status or expiration date of a coupon code. This operation allows you to modify coupon code lifecycle properties such as assignment status and expiration timing."""

    # Construct request model with validation
    try:
        _request = _models.UpdateCouponCodeRequest(
            path=_models.UpdateCouponCodeRequestPath(id_=id_),
            header=_models.UpdateCouponCodeRequestHeader(revision=revision),
            body=_models.UpdateCouponCodeRequestBody(data=_models.UpdateCouponCodeRequestBodyData(
                    id_=data_id, type_=type_,
                    attributes=_models.UpdateCouponCodeRequestBodyDataAttributes(status=status, expires_at=expires_at) if any(v is not None for v in [status, expires_at]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_coupon_code: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/coupon-codes/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/coupon-codes/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_coupon_code")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_coupon_code", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_coupon_code",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Coupons
@mcp.tool()
async def delete_coupon_code(
    id_: str = Field(..., alias="id", description="The unique identifier combining the coupon code and its associated coupon ID (e.g., '10OFF-ASD325FHK324UJDOI2M3JNES99')."),
    revision: str = Field(..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15 if not specified)."),
) -> dict[str, Any]:
    """Permanently deletes a coupon code by its identifier. The operation will fail if the coupon code has an assigned profile."""

    # Construct request model with validation
    try:
        _request = _models.DeleteCouponCodeRequest(
            path=_models.DeleteCouponCodeRequestPath(id_=id_),
            header=_models.DeleteCouponCodeRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_coupon_code: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/coupon-codes/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/coupon-codes/{id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_coupon_code")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_coupon_code", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_coupon_code",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Coupons
@mcp.tool()
async def list_coupon_code_bulk_create_jobs(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format (or with optional suffix). Defaults to 2026-01-15 if not specified."),
    filter_: str | None = Field(None, alias="filter", description="Filter results by job status using the equals operator (e.g., to retrieve only processing jobs). Supports filtering on the status field only."),
) -> dict[str, Any]:
    """Retrieve all coupon code bulk create jobs with optional filtering by status. Returns up to 100 jobs per request."""

    # Construct request model with validation
    try:
        _request = _models.GetBulkCreateCouponCodeJobsRequest(
            query=_models.GetBulkCreateCouponCodeJobsRequestQuery(filter_=filter_),
            header=_models.GetBulkCreateCouponCodeJobsRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_coupon_code_bulk_create_jobs: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/coupon-code-bulk-create-jobs"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_coupon_code_bulk_create_jobs")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_coupon_code_bulk_create_jobs", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_coupon_code_bulk_create_jobs",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Coupons
@mcp.tool()
async def create_coupon_code_bulk_job(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.v2). Defaults to 2026-01-15 if not specified."),
    type_: Literal["coupon-code-bulk-create-job"] = Field(..., alias="type", description="The job type identifier. Must be set to 'coupon-code-bulk-create-job' to specify this operation."),
    data: list[_models.CouponCodeCreateQueryResourceObject] = Field(..., description="Array of coupon code definitions to create in this bulk job. Maximum 1,000 items per job. Each item should contain the coupon code configuration details."),
) -> dict[str, Any]:
    """Initiate a bulk job to create up to 1,000 coupon codes at once. You can queue up to 100 jobs simultaneously, with rate limits of 75 requests per second (burst) or 700 per minute (steady state)."""

    # Construct request model with validation
    try:
        _request = _models.BulkCreateCouponCodesRequest(
            header=_models.BulkCreateCouponCodesRequestHeader(revision=revision),
            body=_models.BulkCreateCouponCodesRequestBody(data=_models.BulkCreateCouponCodesRequestBodyData(
                    type_=type_,
                    attributes=_models.BulkCreateCouponCodesRequestBodyDataAttributes(
                        coupon_codes=_models.BulkCreateCouponCodesRequestBodyDataAttributesCouponCodes(data=data)
                    )
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_coupon_code_bulk_job: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/coupon-code-bulk-create-jobs"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_coupon_code_bulk_job")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_coupon_code_bulk_job", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_coupon_code_bulk_job",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Coupons
@mcp.tool()
async def get_coupon_code_bulk_create_job(
    job_id: str = Field(..., description="The unique identifier of the bulk create job to retrieve (e.g., 01GSQPBF74KQ5YTDEPP41T1BZH)."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, optionally with a suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve the status and details of a coupon code bulk create job by its ID. Use this to monitor the progress and results of asynchronous bulk coupon code creation operations."""

    # Construct request model with validation
    try:
        _request = _models.GetBulkCreateCouponCodesJobRequest(
            path=_models.GetBulkCreateCouponCodesJobRequestPath(job_id=job_id),
            header=_models.GetBulkCreateCouponCodesJobRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_coupon_code_bulk_create_job: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/coupon-code-bulk-create-jobs/{job_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/coupon-code-bulk-create-jobs/{job_id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_coupon_code_bulk_create_job")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_coupon_code_bulk_create_job", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_coupon_code_bulk_create_job",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Coupons
@mcp.tool()
async def get_coupon_for_coupon_code(
    id_: str = Field(..., alias="id", description="The unique identifier of the coupon code to retrieve the associated coupon for (e.g., '10OFF')."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, optionally with a suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve the coupon associated with a specific coupon code ID. This operation allows you to look up the relationship between a coupon code and its corresponding coupon details."""

    # Construct request model with validation
    try:
        _request = _models.GetCouponForCouponCodeRequest(
            path=_models.GetCouponForCouponCodeRequestPath(id_=id_),
            header=_models.GetCouponForCouponCodeRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_coupon_for_coupon_code: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/coupon-codes/{id}/coupon", _request.path.model_dump(by_alias=True)) if _request.path else "/api/coupon-codes/{id}/coupon"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_coupon_for_coupon_code")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_coupon_for_coupon_code", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_coupon_for_coupon_code",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Coupons
@mcp.tool()
async def get_coupon_relationship_for_coupon_code(
    id_: str = Field(..., alias="id", description="The coupon code ID to look up (e.g., '10OFF'). This is the identifier of the coupon code whose associated coupon you want to retrieve."),
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15). Specifies which version of the API contract to use for this request."),
) -> dict[str, Any]:
    """Retrieves the coupon relationship associated with a specific coupon code. Use this to find which coupon is linked to a given coupon code ID."""

    # Construct request model with validation
    try:
        _request = _models.GetCouponIdForCouponCodeRequest(
            path=_models.GetCouponIdForCouponCodeRequestPath(id_=id_),
            header=_models.GetCouponIdForCouponCodeRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_coupon_relationship_for_coupon_code: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/coupon-codes/{id}/relationships/coupon", _request.path.model_dump(by_alias=True)) if _request.path else "/api/coupon-codes/{id}/relationships/coupon"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_coupon_relationship_for_coupon_code")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_coupon_relationship_for_coupon_code", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_coupon_relationship_for_coupon_code",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Coupons
@mcp.tool()
async def list_coupon_codes_for_coupon(
    id_: str = Field(..., alias="id", description="The unique identifier of the coupon to retrieve associated codes for (e.g., '10OFF')."),
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15)."),
    filter_: str | None = Field(None, alias="filter", description="Optional filter expression to narrow results by expiration date (using comparison operators), status, or related coupon/profile identifiers. Supports multiple filter conditions."),
) -> dict[str, Any]:
    """Retrieve all coupon codes associated with a specific coupon. Supports filtering by expiration date, status, and related coupon or profile IDs."""

    # Construct request model with validation
    try:
        _request = _models.GetCouponCodesForCouponRequest(
            path=_models.GetCouponCodesForCouponRequestPath(id_=id_),
            query=_models.GetCouponCodesForCouponRequestQuery(filter_=filter_),
            header=_models.GetCouponCodesForCouponRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_coupon_codes_for_coupon: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/coupons/{id}/coupon-codes", _request.path.model_dump(by_alias=True)) if _request.path else "/api/coupons/{id}/coupon-codes"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_coupon_codes_for_coupon")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_coupon_codes_for_coupon", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_coupon_codes_for_coupon",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Coupons
@mcp.tool()
async def list_coupon_code_ids_for_coupon(
    id_: str = Field(..., alias="id", description="The unique identifier of the coupon to retrieve associated coupon codes for (e.g., '10OFF')."),
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format (defaults to 2026-01-15). Specify a different revision date if needed for API version compatibility."),
    filter_: str | None = Field(None, alias="filter", description="Optional filter expression to narrow results. Supports filtering by expiration date (using comparison operators like less-than or greater-than), status (exact match), coupon ID, or profile ID. See API documentation for filter syntax details."),
) -> dict[str, Any]:
    """Retrieves the list of coupon code IDs associated with a specific coupon. Use optional filters to narrow results by expiration date, status, or related coupon/profile IDs."""

    # Construct request model with validation
    try:
        _request = _models.GetCouponCodeIdsForCouponRequest(
            path=_models.GetCouponCodeIdsForCouponRequestPath(id_=id_),
            query=_models.GetCouponCodeIdsForCouponRequestQuery(filter_=filter_),
            header=_models.GetCouponCodeIdsForCouponRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_coupon_code_ids_for_coupon: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/coupons/{id}/relationships/coupon-codes", _request.path.model_dump(by_alias=True)) if _request.path else "/api/coupons/{id}/relationships/coupon-codes"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_coupon_code_ids_for_coupon")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_coupon_code_ids_for_coupon", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_coupon_code_ids_for_coupon",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Objects
@mcp.tool()
async def list_data_sources(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format (optionally with a suffix). Defaults to 2026-01-15 if not specified."),
    fields_data_source: list[Literal["description", "namespace", "title", "visibility"]] | None = Field(None, alias="fieldsdata-source", description="Specify which data source fields to include in the response for sparse fieldset optimization. Omit to return all available fields."),
    page_size: int | None = Field(None, alias="pagesize", description="Number of data sources to return per page. Defaults to 20 results; valid range is 1 to 100 items per page.", ge=1, le=100),
) -> dict[str, Any]:
    """Retrieve all data sources configured in your account. Supports pagination and sparse fieldset selection to optimize response payload."""

    # Construct request model with validation
    try:
        _request = _models.GetDataSourcesRequest(
            query=_models.GetDataSourcesRequestQuery(fields_data_source=fields_data_source, page_size=page_size),
            header=_models.GetDataSourcesRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_data_sources: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/data-sources"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_query = _serialize_query(_http_query, {
        "fields[data-source]": ("form", False),
    })
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_data_sources")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_data_sources", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_data_sources",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Objects
@mcp.tool()
async def create_data_source(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.v1). Defaults to 2026-01-15 if not specified."),
    type_: Literal["data-source"] = Field(..., alias="type", description="The resource type identifier. Must be set to 'data-source' to indicate this operation creates a data source."),
    title: str = Field(..., description="A unique display name for the data source within its namespace. Must be between 1 and 255 characters long."),
    visibility: Literal["private", "shared"] | None = Field(None, description="Controls who can access this data source. Choose 'private' for account-only access or 'shared' for broader visibility. Defaults to 'private'."),
    description: str | None = Field(None, description="Optional descriptive text providing additional context about the data source's purpose or contents."),
    namespace: str | None = Field(None, description="The organizational container for this data source. Defaults to 'custom-objects' if not specified, which is the standard namespace for custom object definitions."),
) -> dict[str, Any]:
    """Create a new data source within an account namespace. Data sources serve as containers for custom object definitions and can be configured with different visibility levels."""

    # Construct request model with validation
    try:
        _request = _models.CreateDataSourceRequest(
            header=_models.CreateDataSourceRequestHeader(revision=revision),
            body=_models.CreateDataSourceRequestBody(data=_models.CreateDataSourceRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateDataSourceRequestBodyDataAttributes(title=title, visibility=visibility, description=description, namespace=namespace)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_data_source: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/data-sources"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_data_source")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_data_source", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_data_source",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Objects
@mcp.tool()
async def get_data_source(
    id_: str = Field(..., alias="id", description="The unique identifier of the data source to retrieve."),
    revision: str = Field(..., description="API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
    fields_data_source: list[Literal["description", "namespace", "title", "visibility"]] | None = Field(None, alias="fieldsdata-source", description="Optional list of specific data source fields to include in the response. Omit to retrieve all available fields. See API documentation for valid field names."),
) -> dict[str, Any]:
    """Retrieve a specific data source by ID from your account. Use this to fetch detailed information about a configured data source."""

    # Construct request model with validation
    try:
        _request = _models.GetDataSourceRequest(
            path=_models.GetDataSourceRequestPath(id_=id_),
            query=_models.GetDataSourceRequestQuery(fields_data_source=fields_data_source),
            header=_models.GetDataSourceRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_data_source: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/data-sources/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/data-sources/{id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_query = _serialize_query(_http_query, {
        "fields[data-source]": ("form", False),
    })
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_data_source")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_data_source", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_data_source",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Objects
@mcp.tool()
async def delete_data_source(
    id_: str = Field(..., alias="id", description="The unique identifier of the data source to delete."),
    revision: str = Field(..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.v1). Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Permanently delete a data source from your account. This operation requires the data source ID and the current API revision to ensure consistency."""

    # Construct request model with validation
    try:
        _request = _models.DeleteDataSourceRequest(
            path=_models.DeleteDataSourceRequestPath(id_=id_),
            header=_models.DeleteDataSourceRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_data_source: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/data-sources/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/data-sources/{id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_data_source")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_data_source", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_data_source",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Objects
@mcp.tool()
async def create_data_source_records_bulk(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format (or with optional suffix). Defaults to 2026-01-15 if not specified."),
    type_: Literal["data-source-record-bulk-create-job"] = Field(..., alias="type", description="The type identifier for this operation, which must be 'data-source-record-bulk-create-job'."),
    data_source_data_type: Literal["data-source"] = Field(..., alias="data_sourceDataType", description="The resource type identifier for the data source relationship, which must be 'data-source'."),
    data: list[_models.DataSourceRecordResourceObject] = Field(..., description="Array of record objects to import. Supports up to 500 records per request, with each record not exceeding 512KB in size."),
    id_: str = Field(..., alias="id", description="The unique identifier of the data source to which these records belong (e.g., '01J7C23V8XWMRG13FMD7VZN6GW')."),
) -> dict[str, Any]:
    """Initiate a bulk import job to create up to 500 data source records in a single request. The operation accepts a batch of records with a maximum payload size of 4MB total and 512KB per individual record."""

    # Construct request model with validation
    try:
        _request = _models.BulkCreateDataSourceRecordsRequest(
            header=_models.BulkCreateDataSourceRecordsRequestHeader(revision=revision),
            body=_models.BulkCreateDataSourceRecordsRequestBody(data=_models.BulkCreateDataSourceRecordsRequestBodyData(
                    type_=type_,
                    relationships=_models.BulkCreateDataSourceRecordsRequestBodyDataRelationships(
                        data_source=_models.BulkCreateDataSourceRecordsRequestBodyDataRelationshipsDataSource(
                            data=_models.BulkCreateDataSourceRecordsRequestBodyDataRelationshipsDataSourceData(type_=data_source_data_type, id_=id_)
                        )
                    ),
                    attributes=_models.BulkCreateDataSourceRecordsRequestBodyDataAttributes(
                        data_source_records=_models.BulkCreateDataSourceRecordsRequestBodyDataAttributesDataSourceRecords(data=data)
                    )
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_data_source_records_bulk: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/data-source-record-bulk-create-jobs"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_data_source_records_bulk")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_data_source_records_bulk", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_data_source_records_bulk",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Objects
@mcp.tool()
async def create_data_source_record(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format (with optional suffix). Defaults to 2026-01-15 if not specified."),
    type_: Literal["data-source-record-create-job"] = Field(..., alias="type", description="The type of job being created. Must be 'data-source-record-create-job'."),
    data_source_record_data_type: Literal["data-source-record"] = Field(..., alias="data_source_recordDataType", description="The type identifier for the data source record. Must be 'data-source-record'."),
    data_source_data_type: Literal["data-source"] = Field(..., alias="data_sourceDataType", description="The type identifier for the data source relationship. Must be 'data-source'."),
    record: dict[str, Any] = Field(..., description="The record object containing the data to be imported. Must not exceed 512KB in size."),
    id_: str = Field(..., alias="id", description="The unique identifier of the data source to which this record belongs (e.g., 01J7C23V8XWMRG13FMD7VZN6GW)."),
) -> dict[str, Any]:
    """Create a single data source record import job. The record payload must not exceed 512KB. Requires custom-objects:write scope."""

    # Construct request model with validation
    try:
        _request = _models.CreateDataSourceRecordRequest(
            header=_models.CreateDataSourceRecordRequestHeader(revision=revision),
            body=_models.CreateDataSourceRecordRequestBody(data=_models.CreateDataSourceRecordRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateDataSourceRecordRequestBodyDataAttributes(
                        data_source_record=_models.CreateDataSourceRecordRequestBodyDataAttributesDataSourceRecord(
                            data=_models.CreateDataSourceRecordRequestBodyDataAttributesDataSourceRecordData(
                                type_=data_source_record_data_type,
                                attributes=_models.CreateDataSourceRecordRequestBodyDataAttributesDataSourceRecordDataAttributes(record=record)
                            )
                        )
                    ),
                    relationships=_models.CreateDataSourceRecordRequestBodyDataRelationships(
                        data_source=_models.CreateDataSourceRecordRequestBodyDataRelationshipsDataSource(
                            data=_models.CreateDataSourceRecordRequestBodyDataRelationshipsDataSourceData(type_=data_source_data_type, id_=id_)
                        )
                    )
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_data_source_record: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/data-source-record-create-jobs"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_data_source_record")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_data_source_record", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_data_source_record",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Data Privacy
@mcp.tool()
async def create_profile_deletion_job(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix. Defaults to 2026-01-15."),
    type_: Literal["data-privacy-deletion-job"] = Field(..., alias="type", description="Resource type identifier for the deletion job request. Must be set to 'data-privacy-deletion-job'."),
    profile_data_type: Literal["profile"] = Field(..., alias="profileDataType", description="Resource type identifier for the profile being deleted. Must be set to 'profile'."),
    email: str | None = Field(None, description="Email address of the individual whose profile(s) should be deleted. Provide this, phone_number, or neither—but not multiple identifier types together."),
    phone_number: str | None = Field(None, description="Phone number in E.164 format (e.g., +1 country code and number) of the individual whose profile(s) should be deleted. Provide this, email, or neither—but not multiple identifier types together."),
) -> dict[str, Any]:
    """Request asynchronous deletion of all profiles matching a specified identifier (email, phone number, or profile ID). Only one identifier type may be provided per request. Deleted profiles will appear on the Deleted Profiles page once processing completes."""

    # Construct request model with validation
    try:
        _request = _models.RequestProfileDeletionRequest(
            header=_models.RequestProfileDeletionRequestHeader(revision=revision),
            body=_models.RequestProfileDeletionRequestBody(data=_models.RequestProfileDeletionRequestBodyData(
                    type_=type_,
                    attributes=_models.RequestProfileDeletionRequestBodyDataAttributes(
                        profile=_models.RequestProfileDeletionRequestBodyDataAttributesProfile(
                            data=_models.RequestProfileDeletionRequestBodyDataAttributesProfileData(
                                type_=profile_data_type,
                                attributes=_models.RequestProfileDeletionRequestBodyDataAttributesProfileDataAttributes(email=email, phone_number=phone_number) if any(v is not None for v in [email, phone_number]) else None
                            )
                        )
                    )
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_profile_deletion_job: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/data-privacy-deletion-jobs"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_profile_deletion_job")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_profile_deletion_job", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_profile_deletion_job",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Events
@mcp.tool()
async def list_events(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format (with optional suffix). Defaults to 2026-01-15."),
    filter_: str | None = Field(None, alias="filter", description="Filter events by specific criteria using comparison operators. Supports filtering by metric_id, profile_id, profile relationship, or datetime/timestamp ranges (e.g., events after a specific date). Custom metrics are not supported in metric_id filters. See API documentation for detailed filter syntax."),
    page_size: int | None = Field(None, alias="pagesize", description="Number of events to return per page. Defaults to 200 if not specified; must be between 1 and 1000.", ge=1, le=1000),
) -> dict[str, Any]:
    """Retrieve all events from an account with optional filtering by metric, profile, or datetime range. Returns up to 200 events per page."""

    # Construct request model with validation
    try:
        _request = _models.GetEventsRequest(
            query=_models.GetEventsRequestQuery(filter_=filter_, page_size=page_size),
            header=_models.GetEventsRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_events: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/events"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

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

# Tags: Events
@mcp.tool()
async def create_event(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix. Defaults to 2026-01-15 if not specified."),
    type_: Literal["event"] = Field(..., alias="type", description="Resource type identifier. Must be set to 'event'."),
    metric_data_type: Literal["metric"] = Field(..., alias="metricDataType", description="Metric resource type identifier. Must be set to 'metric'."),
    properties: dict[str, Any] = Field(..., description="Custom properties for this event. Supports up to 400 properties with a maximum payload size of 5 MB total and 100 KB per string value. Top-level non-object properties can be used to create segments; use the $extra property for non-segmentable values like HTML templates."),
    name: str = Field(..., description="Name of the event. Must be less than 128 characters."),
    time_: str | None = Field(None, alias="time", description="ISO 8601 timestamp indicating when the event occurred. If omitted, the server's current time is used. Timestamps are truncated to the second and must be after 2000 and no more than 1 year in the future."),
    value: float | None = Field(None, description="Numeric monetary value associated with the event, such as purchase amount or revenue."),
    value_currency: str | None = Field(None, description="ISO 4217 currency code for the event value (e.g., USD, EUR). Should be provided if a value is specified."),
    unique_id: str | None = Field(None, description="Unique identifier for deduplication. If the same unique_id is submitted for the same profile and metric, only the first processed event is recorded. Defaults to timestamp precision of one second, limiting one event per profile per second."),
    profile: _models.CreateEventBodyDataAttributesProfile | None = Field(None, description="Profile associated with the event: email, phone, name, location, and custom properties."),
) -> dict[str, Any]:
    """Track a profile's activity by creating a new event. This operation also allows you to create a new profile or update an existing profile's properties in a single request. The event is validated and queued for processing immediately, though processing may not complete instantly."""

    # Construct request model with validation
    try:
        _request = _models.CreateEventRequest(
            header=_models.CreateEventRequestHeader(revision=revision),
            body=_models.CreateEventRequestBody(data=_models.CreateEventRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateEventRequestBodyDataAttributes(
                        properties=properties, time_=time_, value=value, value_currency=value_currency, unique_id=unique_id, profile=profile,
                        metric=_models.CreateEventRequestBodyDataAttributesMetric(
                            data=_models.CreateEventRequestBodyDataAttributesMetricData(
                                type_=metric_data_type,
                                attributes=_models.CreateEventRequestBodyDataAttributesMetricDataAttributes(name=name)
                            )
                        )
                    )
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_event: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/events"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_event")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_event", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_event",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Events
@mcp.tool()
async def get_event(
    id_: str = Field(..., alias="id", description="The unique identifier of the event to retrieve."),
    revision: str = Field(..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.v1). Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve a specific event by its ID. Returns the complete event details for the requested event."""

    # Construct request model with validation
    try:
        _request = _models.GetEventRequest(
            path=_models.GetEventRequestPath(id_=id_),
            header=_models.GetEventRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_event: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/events/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/events/{id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

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

# Tags: Events
@mcp.tool()
async def create_events_bulk(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.v1). Defaults to 2026-01-15 if not specified."),
    type_: Literal["event-bulk-create-job"] = Field(..., alias="type", description="The type of bulk job being created. Must be set to 'event-bulk-create-job' to indicate this is an event creation operation."),
    data: list[_models.EventsBulkCreateQueryResourceObject] = Field(..., description="Array of event objects to create, with a maximum of 1,000 events per request and 5MB total payload size. Each event must include at least one profile identifier (id, email, or phone_number) and a metric name. Individual string values cannot exceed 100KB."),
) -> dict[str, Any]:
    """Create a batch of up to 1,000 events for one or more profiles in a single request. This operation supports creating new profiles or updating existing profile properties alongside event creation."""

    # Construct request model with validation
    try:
        _request = _models.BulkCreateEventsRequest(
            header=_models.BulkCreateEventsRequestHeader(revision=revision),
            body=_models.BulkCreateEventsRequestBody(data=_models.BulkCreateEventsRequestBodyData(
                    type_=type_,
                    attributes=_models.BulkCreateEventsRequestBodyDataAttributes(
                        events_bulk_create=_models.BulkCreateEventsRequestBodyDataAttributesEventsBulkCreate(data=data)
                    )
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_events_bulk: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/event-bulk-create-jobs"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_events_bulk")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_events_bulk", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_events_bulk",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Events
@mcp.tool()
async def get_metric_for_event(
    id_: str = Field(..., alias="id", description="The unique identifier of the event for which to retrieve the associated metric."),
    revision: str = Field(..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.v1). Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve the metric associated with a specific event. This operation returns metric data linked to the event identified by the provided event ID."""

    # Construct request model with validation
    try:
        _request = _models.GetMetricForEventRequest(
            path=_models.GetMetricForEventRequestPath(id_=id_),
            header=_models.GetMetricForEventRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_metric_for_event: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/events/{id}/metric", _request.path.model_dump(by_alias=True)) if _request.path else "/api/events/{id}/metric"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_metric_for_event")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_metric_for_event", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_metric_for_event",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Events
@mcp.tool()
async def list_metrics_for_event(
    id_: str = Field(..., alias="id", description="The unique identifier of the event for which to retrieve associated metrics."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, optionally with a suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve all metrics associated with a specific event. Returns a list of related metric identifiers linked to the event."""

    # Construct request model with validation
    try:
        _request = _models.GetMetricIdForEventRequest(
            path=_models.GetMetricIdForEventRequestPath(id_=id_),
            header=_models.GetMetricIdForEventRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_metrics_for_event: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/events/{id}/relationships/metric", _request.path.model_dump(by_alias=True)) if _request.path else "/api/events/{id}/relationships/metric"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_metrics_for_event")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_metrics_for_event", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_metrics_for_event",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Events
@mcp.tool()
async def get_profile_for_event(
    id_: str = Field(..., alias="id", description="The unique identifier of the event whose associated profile you want to retrieve."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, optionally followed by a suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve the profile associated with a specific event. Returns the profile data linked to the event identified by the provided event ID."""

    # Construct request model with validation
    try:
        _request = _models.GetProfileForEventRequest(
            path=_models.GetProfileForEventRequestPath(id_=id_),
            header=_models.GetProfileForEventRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_profile_for_event: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/events/{id}/profile", _request.path.model_dump(by_alias=True)) if _request.path else "/api/events/{id}/profile"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_profile_for_event")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_profile_for_event", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_profile_for_event",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Events
@mcp.tool()
async def get_profile_id_for_event(
    id_: str = Field(..., alias="id", description="The unique identifier of the event for which you want to retrieve the associated profile relationship."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve the profile relationship for a specific event, returning the associated profile ID. This operation allows you to identify which profile is linked to a given event."""

    # Construct request model with validation
    try:
        _request = _models.GetProfileIdForEventRequest(
            path=_models.GetProfileIdForEventRequestPath(id_=id_),
            header=_models.GetProfileIdForEventRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_profile_id_for_event: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/events/{id}/relationships/profile", _request.path.model_dump(by_alias=True)) if _request.path else "/api/events/{id}/relationships/profile"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_profile_id_for_event")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_profile_id_for_event", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_profile_id_for_event",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Flows
@mcp.tool()
async def list_flows(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format (with optional suffix). Defaults to 2026-01-15."),
    filter_: str | None = Field(None, alias="filter", description="Filter flows using comparison operators on specific fields. Supports filtering by id (any match), name (contains, starts-with, ends-with, equals), status (equals), archived status (equals), creation/update timestamps (equals, greater-than, greater-or-equal, less-than, less-or-equal), and trigger_type (equals). See API documentation for filter syntax."),
    page_size: int | None = Field(None, alias="pagesize", description="Number of flows to return per page. Must be between 1 and 50, defaults to 50.", ge=1, le=50),
) -> dict[str, Any]:
    """Retrieve all flows in an account with cursor-based pagination. Returns up to 50 flows per request, filterable by multiple criteria including name, status, and timestamps."""

    # Construct request model with validation
    try:
        _request = _models.GetFlowsRequest(
            query=_models.GetFlowsRequestQuery(filter_=filter_, page_size=page_size),
            header=_models.GetFlowsRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_flows: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/flows"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_flows")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_flows", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_flows",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Flows
@mcp.tool()
async def get_flow(
    id_: str = Field(..., alias="id", description="The unique identifier of the flow to retrieve."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve a specific flow by its ID. Returns the complete flow definition and configuration for the given flow identifier."""

    # Construct request model with validation
    try:
        _request = _models.GetFlowRequest(
            path=_models.GetFlowRequestPath(id_=id_),
            header=_models.GetFlowRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_flow: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/flows/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/flows/{id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_flow")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_flow", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_flow",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Flows
@mcp.tool()
async def update_flow_status(
    id_: str = Field(..., alias="id", description="The unique identifier of the flow to update (e.g., XVTP5Q)."),
    revision: str = Field(..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15)."),
    data_id: str = Field(..., alias="dataId", description="The unique identifier of the flow being updated; must match the flow ID in the path parameter."),
    type_: Literal["flow"] = Field(..., alias="type", description="The resource type identifier; must be set to 'flow'."),
    status: str = Field(..., description="The target status for the flow: 'draft' for unpublished changes, 'manual' for manual execution mode, or 'live' for active production status."),
) -> dict[str, Any]:
    """Update the status of a flow and all its associated actions. The flow can be transitioned to draft, manual, or live status."""

    # Construct request model with validation
    try:
        _request = _models.UpdateFlowRequest(
            path=_models.UpdateFlowRequestPath(id_=id_),
            header=_models.UpdateFlowRequestHeader(revision=revision),
            body=_models.UpdateFlowRequestBody(data=_models.UpdateFlowRequestBodyData(
                    id_=data_id, type_=type_,
                    attributes=_models.UpdateFlowRequestBodyDataAttributes(status=status)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_flow_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/flows/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/flows/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_flow_status")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_flow_status", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_flow_status",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Flows
@mcp.tool()
async def delete_flow(
    id_: str = Field(..., alias="id", description="The unique identifier of the flow to delete (e.g., XVTP5Q)."),
    revision: str = Field(..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15). Specify the revision to ensure compatibility with the intended API version."),
) -> dict[str, Any]:
    """Permanently delete a flow by its ID. This operation requires the flow's current revision to ensure safe deletion and prevent accidental overwrites in concurrent scenarios."""

    # Construct request model with validation
    try:
        _request = _models.DeleteFlowRequest(
            path=_models.DeleteFlowRequestPath(id_=id_),
            header=_models.DeleteFlowRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_flow: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/flows/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/flows/{id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_flow")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_flow", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_flow",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Flows
@mcp.tool()
async def get_flow_action(
    id_: str = Field(..., alias="id", description="The unique identifier of the flow action to retrieve."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format (with optional suffix). Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve a specific flow action by its ID. Returns the complete flow action details including configuration and metadata."""

    # Construct request model with validation
    try:
        _request = _models.GetFlowActionRequest(
            path=_models.GetFlowActionRequestPath(id_=id_),
            header=_models.GetFlowActionRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_flow_action: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/flow-actions/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/flow-actions/{id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_flow_action")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_flow_action", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_flow_action",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Flows
@mcp.tool()
async def get_flow_message(
    id_: str = Field(..., alias="id", description="The unique identifier of the flow message to retrieve."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format (with optional suffix). Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve a specific flow message by its ID. Returns the complete message details from the associated flow."""

    # Construct request model with validation
    try:
        _request = _models.GetFlowMessageRequest(
            path=_models.GetFlowMessageRequestPath(id_=id_),
            header=_models.GetFlowMessageRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_flow_message: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/flow-messages/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/flow-messages/{id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_flow_message")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_flow_message", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_flow_message",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Flows
@mcp.tool()
async def list_actions_for_flow(
    id_: str = Field(..., alias="id", description="The unique identifier of the flow for which to retrieve associated actions."),
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format (with optional suffix). Defaults to 2026-01-15."),
    filter_: str | None = Field(None, alias="filter", description="Filter results by action properties. Supports filtering on: id (any operator), action_type (any/equals), status (equals), and created/updated timestamps (equals, greater-or-equal, greater-than, less-or-equal, less-than operators). See API documentation for filter syntax details."),
    page_size: int | None = Field(None, alias="pagesize", description="Number of actions to return per page. Must be between 1 and 50, defaults to 50.", ge=1, le=50),
) -> dict[str, Any]:
    """Retrieve all flow actions associated with a specific flow. Results are paginated with a maximum of 50 actions per request using cursor-based pagination."""

    # Construct request model with validation
    try:
        _request = _models.GetActionsForFlowRequest(
            path=_models.GetActionsForFlowRequestPath(id_=id_),
            query=_models.GetActionsForFlowRequestQuery(filter_=filter_, page_size=page_size),
            header=_models.GetActionsForFlowRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_actions_for_flow: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/flows/{id}/flow-actions", _request.path.model_dump(by_alias=True)) if _request.path else "/api/flows/{id}/flow-actions"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_actions_for_flow")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_actions_for_flow", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_actions_for_flow",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Flows
@mcp.tool()
async def list_action_ids_for_flow(
    id_: str = Field(..., alias="id", description="The unique identifier of the flow for which to retrieve associated actions."),
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format (with optional suffix). Defaults to 2026-01-15."),
    filter_: str | None = Field(None, alias="filter", description="Filter results by action properties. Supports filtering on: id (any match), action_type (any or exact match), status (exact match), and created/updated timestamps (exact match or comparison operators). See API documentation for filter syntax."),
    page_size: int | None = Field(None, alias="pagesize", description="Number of results to return per page. Must be between 1 and 50, defaults to 50.", ge=1, le=50),
) -> dict[str, Any]:
    """Retrieve all action IDs associated with a specific flow. Returns up to 100 results per request with cursor-based pagination support."""

    # Construct request model with validation
    try:
        _request = _models.GetActionIdsForFlowRequest(
            path=_models.GetActionIdsForFlowRequestPath(id_=id_),
            query=_models.GetActionIdsForFlowRequestQuery(filter_=filter_, page_size=page_size),
            header=_models.GetActionIdsForFlowRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_action_ids_for_flow: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/flows/{id}/relationships/flow-actions", _request.path.model_dump(by_alias=True)) if _request.path else "/api/flows/{id}/relationships/flow-actions"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_action_ids_for_flow")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_action_ids_for_flow", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_action_ids_for_flow",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Flows
@mcp.tool()
async def get_tags_for_flow(
    id_: str = Field(..., alias="id", description="The unique identifier of the flow for which to retrieve associated tags."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve all tags associated with a specific flow. Returns a collection of tags linked to the flow identified by the provided ID."""

    # Construct request model with validation
    try:
        _request = _models.GetTagsForFlowRequest(
            path=_models.GetTagsForFlowRequestPath(id_=id_),
            header=_models.GetTagsForFlowRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_tags_for_flow: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/flows/{id}/tags", _request.path.model_dump(by_alias=True)) if _request.path else "/api/flows/{id}/tags"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_tags_for_flow")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_tags_for_flow", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_tags_for_flow",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Flows
@mcp.tool()
async def list_tag_ids_for_flow(
    id_: str = Field(..., alias="id", description="The unique identifier of the flow whose associated tags you want to retrieve."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve all tag IDs associated with a specific flow. Returns a collection of tag identifiers linked to the given flow resource."""

    # Construct request model with validation
    try:
        _request = _models.GetTagIdsForFlowRequest(
            path=_models.GetTagIdsForFlowRequestPath(id_=id_),
            header=_models.GetTagIdsForFlowRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_tag_ids_for_flow: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/flows/{id}/relationships/tags", _request.path.model_dump(by_alias=True)) if _request.path else "/api/flows/{id}/relationships/tags"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_tag_ids_for_flow")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_tag_ids_for_flow", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_tag_ids_for_flow",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Flows
@mcp.tool()
async def get_flow_for_flow_action(
    id_: str = Field(..., alias="id", description="The unique identifier of the flow action for which to retrieve the associated flow."),
    revision: str = Field(..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15). This parameter controls which version of the API contract is used for the request."),
) -> dict[str, Any]:
    """Retrieves the flow associated with a specific flow action by its ID. This operation requires the flows:read scope and is subject to rate limits of 3 requests per second (burst) and 60 requests per minute (steady state)."""

    # Construct request model with validation
    try:
        _request = _models.GetFlowForFlowActionRequest(
            path=_models.GetFlowForFlowActionRequestPath(id_=id_),
            header=_models.GetFlowForFlowActionRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_flow_for_flow_action: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/flow-actions/{id}/flow", _request.path.model_dump(by_alias=True)) if _request.path else "/api/flow-actions/{id}/flow"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_flow_for_flow_action")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_flow_for_flow_action", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_flow_for_flow_action",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Flows
@mcp.tool()
async def get_flow_relationship_for_flow_action(
    id_: str = Field(..., alias="id", description="The unique identifier of the flow action for which to retrieve the associated flow."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve the flow associated with a specific flow action by its ID. Returns the flow relationship data for the given action."""

    # Construct request model with validation
    try:
        _request = _models.GetFlowIdForFlowActionRequest(
            path=_models.GetFlowIdForFlowActionRequestPath(id_=id_),
            header=_models.GetFlowIdForFlowActionRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_flow_relationship_for_flow_action: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/flow-actions/{id}/relationships/flow", _request.path.model_dump(by_alias=True)) if _request.path else "/api/flow-actions/{id}/relationships/flow"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_flow_relationship_for_flow_action")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_flow_relationship_for_flow_action", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_flow_relationship_for_flow_action",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Flows
@mcp.tool()
async def list_flow_action_messages(
    id_: str = Field(..., alias="id", description="The unique identifier of the flow action for which to retrieve associated messages."),
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format (with optional suffix). Defaults to 2026-01-15."),
    filter_: str | None = Field(None, alias="filter", description="Filter results by message properties. Supports filtering on id (any operator), name (contains, ends-with, equals, starts-with), created timestamp, and updated timestamp (all timestamp filters support equals, greater-than, greater-or-equal, less-than, less-or-equal operators)."),
    page_size: int | None = Field(None, alias="pagesize", description="Number of messages to return per page. Must be between 1 and 50, defaults to 50.", ge=1, le=50),
) -> dict[str, Any]:
    """Retrieve all flow messages associated with a specific flow action. Returns up to 50 messages per request with cursor-based pagination support."""

    # Construct request model with validation
    try:
        _request = _models.GetFlowActionMessagesRequest(
            path=_models.GetFlowActionMessagesRequestPath(id_=id_),
            query=_models.GetFlowActionMessagesRequestQuery(filter_=filter_, page_size=page_size),
            header=_models.GetFlowActionMessagesRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_flow_action_messages: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/flow-actions/{id}/flow-messages", _request.path.model_dump(by_alias=True)) if _request.path else "/api/flow-actions/{id}/flow-messages"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_flow_action_messages")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_flow_action_messages", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_flow_action_messages",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Flows
@mcp.tool()
async def list_message_ids_for_flow_action(
    id_: str = Field(..., alias="id", description="The unique identifier of the flow action for which to retrieve associated message relationships."),
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format (with optional suffix). Defaults to 2026-01-15."),
    filter_: str | None = Field(None, alias="filter", description="Filter results by message properties. Supports filtering on `name` (contains, ends-with, equals, starts-with), `created` (equals, greater-or-equal, greater-than, less-or-equal, less-than), and `updated` (equals, greater-or-equal, greater-than, less-or-equal, less-than) fields."),
    page_size: int | None = Field(None, alias="pagesize", description="Number of message relationships to return per page. Must be between 1 and 50, defaults to 50.", ge=1, le=50),
) -> dict[str, Any]:
    """Retrieve all flow message IDs associated with a specific flow action. Results are paginated with a maximum of 50 relationships per request using cursor-based pagination."""

    # Construct request model with validation
    try:
        _request = _models.GetMessageIdsForFlowActionRequest(
            path=_models.GetMessageIdsForFlowActionRequestPath(id_=id_),
            query=_models.GetMessageIdsForFlowActionRequestQuery(filter_=filter_, page_size=page_size),
            header=_models.GetMessageIdsForFlowActionRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_message_ids_for_flow_action: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/flow-actions/{id}/relationships/flow-messages", _request.path.model_dump(by_alias=True)) if _request.path else "/api/flow-actions/{id}/relationships/flow-messages"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_message_ids_for_flow_action")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_message_ids_for_flow_action", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_message_ids_for_flow_action",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Flows
@mcp.tool()
async def get_flow_action_for_message(
    id_: str = Field(..., alias="id", description="The unique identifier of the flow message for which to retrieve the associated flow action."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve the flow action associated with a specific flow message. This operation returns the action configuration that should be executed for the given message within a flow."""

    # Construct request model with validation
    try:
        _request = _models.GetActionForFlowMessageRequest(
            path=_models.GetActionForFlowMessageRequestPath(id_=id_),
            header=_models.GetActionForFlowMessageRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_flow_action_for_message: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/flow-messages/{id}/flow-action", _request.path.model_dump(by_alias=True)) if _request.path else "/api/flow-messages/{id}/flow-action"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_flow_action_for_message")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_flow_action_for_message", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_flow_action_for_message",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Flows
@mcp.tool()
async def get_flow_action_for_flow_message(
    id_: str = Field(..., alias="id", description="The unique identifier of the flow message for which to retrieve the associated flow action relationship."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve the flow action relationship associated with a specific flow message. This returns the relationship link to the flow action that governs the behavior of the given flow message."""

    # Construct request model with validation
    try:
        _request = _models.GetActionIdForFlowMessageRequest(
            path=_models.GetActionIdForFlowMessageRequestPath(id_=id_),
            header=_models.GetActionIdForFlowMessageRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_flow_action_for_flow_message: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/flow-messages/{id}/relationships/flow-action", _request.path.model_dump(by_alias=True)) if _request.path else "/api/flow-messages/{id}/relationships/flow-action"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_flow_action_for_flow_message")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_flow_action_for_flow_message", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_flow_action_for_flow_message",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Flows
@mcp.tool()
async def get_template_for_flow_message(
    id_: str = Field(..., alias="id", description="The unique identifier of the flow message for which to retrieve the associated template."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve the template associated with a specific flow message. Returns the template configuration used by the flow message."""

    # Construct request model with validation
    try:
        _request = _models.GetTemplateForFlowMessageRequest(
            path=_models.GetTemplateForFlowMessageRequestPath(id_=id_),
            header=_models.GetTemplateForFlowMessageRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_template_for_flow_message: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/flow-messages/{id}/template", _request.path.model_dump(by_alias=True)) if _request.path else "/api/flow-messages/{id}/template"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_template_for_flow_message")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_template_for_flow_message", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_template_for_flow_message",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Flows
@mcp.tool()
async def get_template_id_for_flow_message(
    id_: str = Field(..., alias="id", description="The unique identifier of the flow message for which to retrieve the associated template ID."),
    revision: str = Field(..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15). Specifies which version of the API contract to use for this request."),
) -> dict[str, Any]:
    """Retrieves the ID of the template associated with a specific flow message. This operation returns the relationship between a flow message and its related template."""

    # Construct request model with validation
    try:
        _request = _models.GetTemplateIdForFlowMessageRequest(
            path=_models.GetTemplateIdForFlowMessageRequestPath(id_=id_),
            header=_models.GetTemplateIdForFlowMessageRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_template_id_for_flow_message: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/flow-messages/{id}/relationships/template", _request.path.model_dump(by_alias=True)) if _request.path else "/api/flow-messages/{id}/relationships/template"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_template_id_for_flow_message")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_template_id_for_flow_message", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_template_id_for_flow_message",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Forms
@mcp.tool()
async def list_forms(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format (with optional suffix). Required for version compatibility."),
    fields_form: list[Literal["ab_test", "created_at", "name", "status", "updated_at"]] | None = Field(None, alias="fieldsform", description="Specify which form fields to include in the response using sparse fieldsets for optimized data retrieval."),
    filter_: str | None = Field(None, alias="filter", description="Filter forms by id, name, ab_test status, creation/update timestamps, or status. Supports operators like equals, contains, any, and temporal comparisons (greater-than, less-than, etc.)."),
    page_size: int | None = Field(None, alias="pagesize", description="Number of forms to return per page. Must be between 1 and 100 items; defaults to 20.", ge=1, le=100),
) -> dict[str, Any]:
    """Retrieve all forms in an account with optional filtering, field selection, and pagination. Supports filtering by form properties like name, status, and timestamps."""

    # Construct request model with validation
    try:
        _request = _models.GetFormsRequest(
            query=_models.GetFormsRequestQuery(fields_form=fields_form, filter_=filter_, page_size=page_size),
            header=_models.GetFormsRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_forms: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/forms"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_query = _serialize_query(_http_query, {
        "fields[form]": ("form", False),
    })
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_forms")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_forms", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_forms",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Forms
@mcp.tool()
async def create_form(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.v1). Defaults to 2026-01-15 if not specified."),
    type_: Literal["form"] = Field(..., alias="type", description="The resource type, which must be 'form' for this operation."),
    versions: list[_models.Version] = Field(..., description="An array of form versions to associate with this form. Specify the versions in the order they should be applied or referenced."),
    status: Literal["draft", "live"] = Field(..., description="The initial status of the form: either 'draft' for unpublished forms or 'live' for published forms."),
    ab_test: bool = Field(..., description="A boolean flag indicating whether this form has an A/B test configured. Set to true to enable A/B testing for this form."),
    name: str = Field(..., description="The display name of the form. Use a descriptive name that identifies the form's purpose (e.g., 'Cyber Monday Deals')."),
) -> dict[str, Any]:
    """Create a new form with specified configuration, including versioning, status, and optional A/B testing setup. The form will be created in the specified status (draft or live) and can be configured for A/B testing."""

    # Construct request model with validation
    try:
        _request = _models.CreateFormRequest(
            header=_models.CreateFormRequestHeader(revision=revision),
            body=_models.CreateFormRequestBody(data=_models.CreateFormRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateFormRequestBodyDataAttributes(
                        status=status, ab_test=ab_test, name=name,
                        definition=_models.CreateFormRequestBodyDataAttributesDefinition(versions=versions)
                    )
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_form: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/forms"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_form")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_form", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_form",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Forms
@mcp.tool()
async def get_form(
    id_: str = Field(..., alias="id", description="The unique identifier of the form to retrieve (e.g., 'Y6nRLr')."),
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format, with optional suffix (defaults to 2026-01-15). Specifies which API version to use for this request."),
    fields_form: list[Literal["ab_test", "created_at", "definition", "definition.versions", "name", "status", "updated_at"]] | None = Field(None, alias="fieldsform", description="Optional sparse fieldset to limit returned form fields. See API documentation for supported field names and filtering syntax."),
) -> dict[str, Any]:
    """Retrieve a specific form by its ID. Use optional field filtering to customize the response payload."""

    # Construct request model with validation
    try:
        _request = _models.GetFormRequest(
            path=_models.GetFormRequestPath(id_=id_),
            query=_models.GetFormRequestQuery(fields_form=fields_form),
            header=_models.GetFormRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_form: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/forms/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/forms/{id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_query = _serialize_query(_http_query, {
        "fields[form]": ("form", False),
    })
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_form")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_form", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_form",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Forms
@mcp.tool()
async def delete_form(
    id_: str = Field(..., alias="id", description="The unique identifier of the form to delete (e.g., 'Y6nRLr')"),
    revision: str = Field(..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15 if not specified)"),
) -> dict[str, Any]:
    """Permanently delete a form by its ID. This operation requires the form ID and API revision to be specified."""

    # Construct request model with validation
    try:
        _request = _models.DeleteFormRequest(
            path=_models.DeleteFormRequestPath(id_=id_),
            header=_models.DeleteFormRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_form: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/forms/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/forms/{id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_form")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_form", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_form",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Forms
@mcp.tool()
async def get_form_version(
    id_: str = Field(..., alias="id", description="The unique identifier of the form version to retrieve (e.g., '1234567')."),
    revision: str = Field(..., description="API revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
    fields_form_version: list[Literal["ab_test", "ab_test.variation_name", "created_at", "form_type", "status", "updated_at", "variation_name"]] | None = Field(None, alias="fieldsform-version", description="Optional sparse fieldset to limit returned fields for the form-version resource. Reduces response payload by selecting only needed fields."),
) -> dict[str, Any]:
    """Retrieve a specific form version by its ID. Use optional field filtering to customize the response payload."""

    # Construct request model with validation
    try:
        _request = _models.GetFormVersionRequest(
            path=_models.GetFormVersionRequestPath(id_=id_),
            query=_models.GetFormVersionRequestQuery(fields_form_version=fields_form_version),
            header=_models.GetFormVersionRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_form_version: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/form-versions/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/form-versions/{id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_query = _serialize_query(_http_query, {
        "fields[form-version]": ("form", False),
    })
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_form_version")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_form_version", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_form_version",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Forms
@mcp.tool()
async def list_versions_for_form(
    id_: str | None = Field(..., alias="id", description="The unique identifier of the form whose versions you want to retrieve."),
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format (or with optional suffix). Defaults to 2026-01-15."),
    fields_form_version: list[Literal["ab_test", "ab_test.variation_name", "created_at", "form_type", "status", "updated_at", "variation_name"]] | None = Field(None, alias="fieldsform-version", description="Specify which form-version fields to include in the response to reduce payload size. Omit to return all fields."),
    filter_: str | None = Field(None, alias="filter", description="Filter results by form type (popup, embedded, etc.), status, or creation/update timestamps. Supports equality checks and date range comparisons (greater than, less than, etc.)."),
    page_size: int | None = Field(None, alias="pagesize", description="Number of results per page for pagination. Defaults to 20, with a range of 1 to 100 results.", ge=1, le=100),
) -> dict[str, Any]:
    """Retrieve all versions of a specific form, with optional filtering by form type, status, or date range, and support for sparse fieldsets and pagination."""

    # Construct request model with validation
    try:
        _request = _models.GetVersionsForFormRequest(
            path=_models.GetVersionsForFormRequestPath(id_=id_),
            query=_models.GetVersionsForFormRequestQuery(fields_form_version=fields_form_version, filter_=filter_, page_size=page_size),
            header=_models.GetVersionsForFormRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_versions_for_form: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/forms/{id}/form-versions", _request.path.model_dump(by_alias=True)) if _request.path else "/api/forms/{id}/form-versions"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_query = _serialize_query(_http_query, {
        "fields[form-version]": ("form", False),
    })
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_versions_for_form")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_versions_for_form", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_versions_for_form",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Forms
@mcp.tool()
async def list_version_ids_for_form(
    id_: str | None = Field(..., alias="id", description="The unique identifier of the form to retrieve versions for."),
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format (with optional suffix). Defaults to 2026-01-15."),
    filter_: str | None = Field(None, alias="filter", description="Filter results by form type (any or equals), status (equals), or timestamps (created_at/updated_at with greater-than, greater-or-equal, less-than, less-or-equal operators). See API documentation for filter syntax."),
    page_size: int | None = Field(None, alias="pagesize", description="Number of results per page. Must be between 1 and 100, defaults to 20.", ge=1, le=100),
) -> dict[str, Any]:
    """Retrieve the version IDs for a specific form. Supports filtering by form type, status, and creation/update timestamps, with pagination support."""

    # Construct request model with validation
    try:
        _request = _models.GetVersionIdsForFormRequest(
            path=_models.GetVersionIdsForFormRequestPath(id_=id_),
            query=_models.GetVersionIdsForFormRequestQuery(filter_=filter_, page_size=page_size),
            header=_models.GetVersionIdsForFormRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_version_ids_for_form: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/forms/{id}/relationships/form-versions", _request.path.model_dump(by_alias=True)) if _request.path else "/api/forms/{id}/relationships/form-versions"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_version_ids_for_form")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_version_ids_for_form", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_version_ids_for_form",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Forms
@mcp.tool()
async def get_form_for_form_version(
    id_: str = Field(..., alias="id", description="The unique identifier of the form version you want to retrieve the form for (e.g., '1234567')."),
    revision: str = Field(..., description="The API revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
    fields_form: list[Literal["ab_test", "created_at", "name", "status", "updated_at"]] | None = Field(None, alias="fieldsform", description="Optional sparse fieldset to limit which form fields are returned in the response. Specify an array of field names to include only those fields in the result."),
) -> dict[str, Any]:
    """Retrieve the form associated with a specific form version. Use this to access the complete form definition linked to a particular version."""

    # Construct request model with validation
    try:
        _request = _models.GetFormForFormVersionRequest(
            path=_models.GetFormForFormVersionRequestPath(id_=id_),
            query=_models.GetFormForFormVersionRequestQuery(fields_form=fields_form),
            header=_models.GetFormForFormVersionRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_form_for_form_version: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/form-versions/{id}/form", _request.path.model_dump(by_alias=True)) if _request.path else "/api/form-versions/{id}/form"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_query = _serialize_query(_http_query, {
        "fields[form]": ("form", False),
    })
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_form_for_form_version")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_form_for_form_version", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_form_for_form_version",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Forms
@mcp.tool()
async def get_form_id_for_form_version(
    id_: str = Field(..., alias="id", description="The unique identifier of the form version for which you want to retrieve the associated form ID."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve the ID of the form associated with a specific form version. This operation returns the relationship between a form version and its parent form."""

    # Construct request model with validation
    try:
        _request = _models.GetFormIdForFormVersionRequest(
            path=_models.GetFormIdForFormVersionRequestPath(id_=id_),
            header=_models.GetFormIdForFormVersionRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_form_id_for_form_version: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/form-versions/{id}/relationships/form", _request.path.model_dump(by_alias=True)) if _request.path else "/api/form-versions/{id}/relationships/form"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_form_id_for_form_version")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_form_id_for_form_version", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_form_id_for_form_version",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Images
@mcp.tool()
async def list_images(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format (with optional suffix). Defaults to 2026-01-15."),
    filter_: str | None = Field(None, alias="filter", description="Filter results using field-specific operators. Supports filtering by ID (any/equals), updated_at (comparison operators), format (any/equals), name (text matching), size (numeric comparison), and hidden status (any/equals). Provide filter expressions in the format: operator(field,'value')."),
    page_size: int | None = Field(None, alias="pagesize", description="Number of images to return per page. Defaults to 20 results; minimum is 1, maximum is 100.", ge=1, le=100),
) -> dict[str, Any]:
    """Retrieve all images in your account with optional filtering and pagination. Supports filtering by ID, update date, format, name, size, and visibility status."""

    # Construct request model with validation
    try:
        _request = _models.GetImagesRequest(
            query=_models.GetImagesRequestQuery(filter_=filter_, page_size=page_size),
            header=_models.GetImagesRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_images: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/images"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_images")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_images", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_images",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Images
@mcp.tool()
async def import_image_from_url(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.v1). Defaults to 2026-01-15 if not specified."),
    type_: Literal["image"] = Field(..., alias="type", description="Resource type identifier. Must be set to 'image' for this operation."),
    import_from_url: str = Field(..., description="The source URL or base64-encoded data URI for the image to import. Accepts standard HTTP/HTTPS URLs or data URIs in the format data:image/[format];base64,[encoded_data]. Supported formats are JPEG, PNG, and GIF, with a maximum file size of 5MB."),
    name: str | None = Field(None, description="Optional display name for the imported image. If omitted, the filename from the URL will be used. If the name matches an existing image, a numeric suffix will be automatically appended to ensure uniqueness."),
    hidden: bool | None = Field(None, description="Optional flag to exclude this image from the asset library UI. When true, the image is stored but not displayed in browsable asset lists. Defaults to false (image is visible)."),
) -> dict[str, Any]:
    """Import an image into your asset library from a publicly accessible URL or base64-encoded data URI. Supports JPEG, PNG, and GIF formats up to 5MB in size."""

    # Construct request model with validation
    try:
        _request = _models.UploadImageFromUrlRequest(
            header=_models.UploadImageFromUrlRequestHeader(revision=revision),
            body=_models.UploadImageFromUrlRequestBody(data=_models.UploadImageFromUrlRequestBodyData(
                    type_=type_,
                    attributes=_models.UploadImageFromUrlRequestBodyDataAttributes(name=name, import_from_url=import_from_url, hidden=hidden)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for import_image_from_url: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/images"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("import_image_from_url")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("import_image_from_url", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="import_image_from_url",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Images
@mcp.tool()
async def get_image(
    id_: str = Field(..., alias="id", description="The unique identifier of the image to retrieve (e.g., '7'). This ID must correspond to an existing image in the system."),
    revision: str = Field(..., description="The API endpoint revision to use for this request, specified in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15). This ensures compatibility with specific API versions."),
) -> dict[str, Any]:
    """Retrieve a specific image by its ID. Returns the image metadata and content for the requested image resource."""

    # Construct request model with validation
    try:
        _request = _models.GetImageRequest(
            path=_models.GetImageRequestPath(id_=id_),
            header=_models.GetImageRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_image: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/images/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/images/{id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_image")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_image", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_image",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Images
@mcp.tool()
async def update_image(
    id_: str = Field(..., alias="id", description="The unique identifier of the image to update (e.g., '7')"),
    revision: str = Field(..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15)"),
    data_id: str = Field(..., alias="dataId", description="The unique identifier of the image being updated; must match the ID in the path parameter (e.g., '7')"),
    type_: Literal["image"] = Field(..., alias="type", description="The resource type; must be set to 'image'"),
    name: str | None = Field(None, description="A display name for the image; optional and can be any string value"),
    hidden: bool | None = Field(None, description="Controls image visibility in the asset library; when true, the image is hidden from the library view"),
) -> dict[str, Any]:
    """Update an image's metadata, including its name and visibility settings. Requires the image ID and API revision to be specified."""

    # Construct request model with validation
    try:
        _request = _models.UpdateImageRequest(
            path=_models.UpdateImageRequestPath(id_=id_),
            header=_models.UpdateImageRequestHeader(revision=revision),
            body=_models.UpdateImageRequestBody(data=_models.UpdateImageRequestBodyData(
                    id_=data_id, type_=type_,
                    attributes=_models.UpdateImageRequestBodyDataAttributes(name=name, hidden=hidden) if any(v is not None for v in [name, hidden]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_image: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/images/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/images/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_image")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_image", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_image",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Images
@mcp.tool()
async def create_image_from_file(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15)."),
    file_: str = Field(..., alias="file", description="The image file to upload as binary data. Supported formats: JPEG, PNG, GIF. Maximum file size is 5MB."),
    name: str | None = Field(None, description="Optional name for the image. If not provided, defaults to the original filename. If the name matches an existing image, a numeric suffix will be automatically added."),
    hidden: bool | None = Field(None, description="If true, the image will be hidden from the asset library. Defaults to false."),
) -> dict[str, Any]:
    """Upload an image file to create a new image asset. Supports JPEG, PNG, and GIF formats up to 5MB. For importing images from URLs or data URIs, use the Upload Image From URL endpoint instead."""

    # Construct request model with validation
    try:
        _request = _models.UploadImageFromFileRequest(
            header=_models.UploadImageFromFileRequestHeader(revision=revision),
            body=_models.UploadImageFromFileRequestBody(file_=file_, name=name, hidden=hidden)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_image_from_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/image-upload"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_image_from_file")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_image_from_file", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_image_from_file",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: Lists
@mcp.tool()
async def list_lists(
    revision: str = Field(..., description="API version in YYYY-MM-DD format (e.g., 2026-01-15). Defaults to 2026-01-15 if not specified."),
    fields_list: list[Literal["created", "name", "opt_in_process", "updated"]] | None = Field(None, alias="fieldslist", description="Specify which list fields to include in the response for sparse fieldset optimization. Reduces payload size by returning only requested fields."),
    filter_: str | None = Field(None, alias="filter", description="Filter lists by name, id, creation date, or last update date. Supports exact matching for name and id, or date range queries using greater-than operators. Use the format: operator(field,[values])."),
) -> dict[str, Any]:
    """Retrieve all lists in your account with optional filtering and field selection. Results are paginated with a maximum of 10 lists per page."""

    # Construct request model with validation
    try:
        _request = _models.GetListsRequest(
            query=_models.GetListsRequestQuery(fields_list=fields_list, filter_=filter_),
            header=_models.GetListsRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_lists: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/lists"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_query = _serialize_query(_http_query, {
        "fields[list]": ("form", False),
    })
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

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
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Lists
@mcp.tool()
async def create_list(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15). Specifies which API version to use for this operation."),
    type_: Literal["list"] = Field(..., alias="type", description="The resource type being created. Must be set to 'list' for this operation."),
    name: str = Field(..., description="A descriptive name for the list to help identify it in your account (e.g., 'Newsletter', 'Product Updates'). Used for display and organization purposes."),
    opt_in_process: Literal["double_opt_in", "single_opt_in"] | None = Field(None, description="The subscriber opt-in verification method for this list: 'double_opt_in' requires confirmation via email, while 'single_opt_in' adds subscribers immediately. If not specified, your account's default opt-in process will be used."),
) -> dict[str, Any]:
    """Create a new mailing list for managing subscribers. The list will be configured with your specified name and opt-in process preference."""

    # Construct request model with validation
    try:
        _request = _models.CreateListRequest(
            header=_models.CreateListRequestHeader(revision=revision),
            body=_models.CreateListRequestBody(data=_models.CreateListRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateListRequestBodyDataAttributes(name=name, opt_in_process=opt_in_process)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_list: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/lists"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_list")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_list", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_list",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Lists
@mcp.tool()
async def get_list(
    id_: str = Field(..., alias="id", description="The unique identifier for the list, generated by Klaviyo (e.g., 'Y6nRLr')."),
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15). Specifies which API version to use for this request."),
    fields_list: list[Literal["created", "name", "opt_in_process", "profile_count", "updated"]] | None = Field(None, alias="fieldslist", description="Optional array of field names to include in the response for sparse fieldsets. Omit to return all default fields. See API documentation for available fields."),
) -> dict[str, Any]:
    """Retrieve a specific list by its ID. Use optional field selection to customize the response payload and control rate limit impact."""

    # Construct request model with validation
    try:
        _request = _models.GetListRequest(
            path=_models.GetListRequestPath(id_=id_),
            query=_models.GetListRequestQuery(fields_list=fields_list),
            header=_models.GetListRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_list: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/lists/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/lists/{id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_query = _serialize_query(_http_query, {
        "fields[list]": ("form", False),
    })
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_list")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_list", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_list",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Lists
@mcp.tool()
async def update_list(
    id_: str = Field(..., alias="id", description="The unique identifier of the list to update, generated by Klaviyo (e.g., 'Y6nRLr')."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format (or with an optional suffix). Defaults to 2026-01-15 if not specified."),
    data_id: str = Field(..., alias="dataId", description="The unique identifier of the list being updated in the request body. Must match the ID in the URL path."),
    type_: Literal["list"] = Field(..., alias="type", description="The resource type, which must be 'list' for this operation."),
    name: str | None = Field(None, description="A descriptive name for the list to help identify it (e.g., 'Newsletter'). Optional field."),
    opt_in_process: Literal["double_opt_in", "single_opt_in"] | None = Field(None, description="The opt-in process type for this list: 'double_opt_in' requires confirmation, while 'single_opt_in' adds subscribers immediately. Optional field."),
) -> dict[str, Any]:
    """Update a list's name and opt-in process settings. Requires the list ID in both the URL path and request body, along with the API revision date."""

    # Construct request model with validation
    try:
        _request = _models.UpdateListRequest(
            path=_models.UpdateListRequestPath(id_=id_),
            header=_models.UpdateListRequestHeader(revision=revision),
            body=_models.UpdateListRequestBody(data=_models.UpdateListRequestBodyData(
                    id_=data_id, type_=type_,
                    attributes=_models.UpdateListRequestBodyDataAttributes(name=name, opt_in_process=opt_in_process) if any(v is not None for v in [name, opt_in_process]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_list: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/lists/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/lists/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_list")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_list", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_list",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Lists
@mcp.tool()
async def delete_list(
    id_: str = Field(..., alias="id", description="The unique identifier of the list to delete, generated by Klaviyo (e.g., 'Y6nRLr')."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format (or with an optional suffix). Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Permanently delete a list by its ID. This action cannot be undone and will remove the list and all associated data."""

    # Construct request model with validation
    try:
        _request = _models.DeleteListRequest(
            path=_models.DeleteListRequestPath(id_=id_),
            header=_models.DeleteListRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_list: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/lists/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/lists/{id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_list")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_list", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_list",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Lists
@mcp.tool()
async def list_tags_for_list(
    id_: str = Field(..., alias="id", description="The unique identifier for the list, generated by Klaviyo (e.g., 'Y6nRLr')."),
    revision: str = Field(..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15 if not specified)."),
) -> dict[str, Any]:
    """Retrieve all tags associated with a specific list. Returns a collection of tags linked to the given list ID."""

    # Construct request model with validation
    try:
        _request = _models.GetTagsForListRequest(
            path=_models.GetTagsForListRequestPath(id_=id_),
            header=_models.GetTagsForListRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_tags_for_list: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/lists/{id}/tags", _request.path.model_dump(by_alias=True)) if _request.path else "/api/lists/{id}/tags"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_tags_for_list")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_tags_for_list", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_tags_for_list",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Lists
@mcp.tool()
async def list_tag_ids_for_list(
    id_: str = Field(..., alias="id", description="The unique identifier for the list, generated by Klaviyo (e.g., 'Y6nRLr')."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve all tags associated with a specific list. Returns tag IDs that are linked to the given list."""

    # Construct request model with validation
    try:
        _request = _models.GetTagIdsForListRequest(
            path=_models.GetTagIdsForListRequestPath(id_=id_),
            header=_models.GetTagIdsForListRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_tag_ids_for_list: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/lists/{id}/relationships/tags", _request.path.model_dump(by_alias=True)) if _request.path else "/api/lists/{id}/relationships/tags"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_tag_ids_for_list")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_tag_ids_for_list", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_tag_ids_for_list",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Lists
@mcp.tool()
async def list_profiles_for_list(
    id_: str = Field(..., alias="id", description="The unique identifier of the list (generated by Klaviyo). Example format: 'Y6nRLr'."),
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format (e.g., 2026-01-15). Defaults to the latest version if not specified."),
    filter_: str | None = Field(None, alias="filter", description="Filter profiles by email, phone number, push token, or join date. Supports exact matching and range operators (greater-than, less-than, etc.) for dates. Use the format specified in the API filtering guide."),
    page_size: int | None = Field(None, alias="pagesize", description="Number of profiles to return per page. Must be between 1 and 100. Defaults to 20 if not specified.", ge=1, le=100),
) -> dict[str, Any]:
    """Retrieve all profiles within a specific list. Optionally filter by email, phone number, push token, or group join date, and sort results by join date in ascending or descending order."""

    # Construct request model with validation
    try:
        _request = _models.GetProfilesForListRequest(
            path=_models.GetProfilesForListRequestPath(id_=id_),
            query=_models.GetProfilesForListRequestQuery(filter_=filter_, page_size=page_size),
            header=_models.GetProfilesForListRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_profiles_for_list: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/lists/{id}/profiles", _request.path.model_dump(by_alias=True)) if _request.path else "/api/lists/{id}/profiles"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_profiles_for_list")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_profiles_for_list", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_profiles_for_list",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Lists
@mcp.tool()
async def list_profile_ids_for_list(
    id_: str = Field(..., alias="id", description="The unique identifier of the list. This is a Klaviyo-generated ID (e.g., 'Y6nRLr')."),
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format (e.g., '2026-01-15'). Defaults to the latest version if not specified."),
    filter_: str | None = Field(None, alias="filter", description="Optional filter to narrow results by profile attributes. Supports filtering by email, phone number, push token, Klaviyo ID (_kx), or group join date. Use operators like 'equals', 'any', 'greater-than', or 'less-than' depending on the field. See API documentation for filter syntax."),
    page_size: int | None = Field(None, alias="pagesize", description="Number of results per page. Must be between 1 and 100. Defaults to 20 if not specified.", ge=1, le=100),
) -> dict[str, Any]:
    """Retrieve the profile IDs that are members of a specific list. Use filtering to narrow results by email, phone number, push token, or other profile attributes, and pagination to manage large result sets."""

    # Construct request model with validation
    try:
        _request = _models.GetProfileIdsForListRequest(
            path=_models.GetProfileIdsForListRequestPath(id_=id_),
            query=_models.GetProfileIdsForListRequestQuery(filter_=filter_, page_size=page_size),
            header=_models.GetProfileIdsForListRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_profile_ids_for_list: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/lists/{id}/relationships/profiles", _request.path.model_dump(by_alias=True)) if _request.path else "/api/lists/{id}/relationships/profiles"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_profile_ids_for_list")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_profile_ids_for_list", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_profile_ids_for_list",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Lists
@mcp.tool()
async def add_profiles_to_list(
    id_: str = Field(..., alias="id", description="The unique identifier of the list to which profiles will be added."),
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format (or with optional suffix). Defaults to 2026-01-15 if not specified."),
    data: list[_models.AddProfilesToListBodyDataItem] = Field(..., description="Array of profile objects to add to the list. Maximum 1000 profiles per request. Order is not significant."),
) -> dict[str, Any]:
    """Add one or more profiles to a list. Accepts up to 1000 profiles per request. For granting email or SMS marketing consent, use the Subscribe Profiles endpoint instead."""

    # Construct request model with validation
    try:
        _request = _models.AddProfilesToListRequest(
            path=_models.AddProfilesToListRequestPath(id_=id_),
            header=_models.AddProfilesToListRequestHeader(revision=revision),
            body=_models.AddProfilesToListRequestBody(data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_profiles_to_list: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/lists/{id}/relationships/profiles", _request.path.model_dump(by_alias=True)) if _request.path else "/api/lists/{id}/relationships/profiles"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_profiles_to_list")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_profiles_to_list", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_profiles_to_list",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Lists
@mcp.tool()
async def remove_profiles_from_list(
    id_: str = Field(..., alias="id", description="The unique identifier of the list from which profiles will be removed."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format (or with an optional suffix). Defaults to 2026-01-15 if not specified."),
    data: list[_models.RemoveProfilesFromListBodyDataItem] = Field(..., description="An array of profiles to remove from the list. Supports up to 1000 profiles per request. Each item should contain the profile identifier in the format expected by the API."),
) -> dict[str, Any]:
    """Remove one or more profiles from a marketing list. Removed profiles will no longer receive marketing communications from that list, but their overall consent and subscription status remain unchanged."""

    # Construct request model with validation
    try:
        _request = _models.RemoveProfilesFromListRequest(
            path=_models.RemoveProfilesFromListRequestPath(id_=id_),
            header=_models.RemoveProfilesFromListRequestHeader(revision=revision),
            body=_models.RemoveProfilesFromListRequestBody(data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_profiles_from_list: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/lists/{id}/relationships/profiles", _request.path.model_dump(by_alias=True)) if _request.path else "/api/lists/{id}/relationships/profiles"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_profiles_from_list")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_profiles_from_list", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_profiles_from_list",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Lists
@mcp.tool()
async def list_flows_triggered_by_list(
    id_: str = Field(..., alias="id", description="The unique identifier of the list (generated by Klaviyo) for which you want to find associated flow triggers."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format (or with an optional suffix). Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve all automation flows that are configured to trigger when the specified list is used as a trigger source. This helps identify which workflows depend on a particular list."""

    # Construct request model with validation
    try:
        _request = _models.GetFlowsTriggeredByListRequest(
            path=_models.GetFlowsTriggeredByListRequestPath(id_=id_),
            header=_models.GetFlowsTriggeredByListRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_flows_triggered_by_list: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/lists/{id}/flow-triggers", _request.path.model_dump(by_alias=True)) if _request.path else "/api/lists/{id}/flow-triggers"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_flows_triggered_by_list")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_flows_triggered_by_list", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_flows_triggered_by_list",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Lists
@mcp.tool()
async def list_flow_trigger_ids_for_list(
    id_: str = Field(..., alias="id", description="The unique identifier of the list, generated by Klaviyo (e.g., 'Y6nRLr'). This ID specifies which list's flow triggers you want to retrieve."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve the IDs of all flows that are triggered by a specific list. This helps identify which automation workflows depend on a given list as their trigger source."""

    # Construct request model with validation
    try:
        _request = _models.GetIdsForFlowsTriggeredByListRequest(
            path=_models.GetIdsForFlowsTriggeredByListRequestPath(id_=id_),
            header=_models.GetIdsForFlowsTriggeredByListRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_flow_trigger_ids_for_list: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/lists/{id}/relationships/flow-triggers", _request.path.model_dump(by_alias=True)) if _request.path else "/api/lists/{id}/relationships/flow-triggers"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_flow_trigger_ids_for_list")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_flow_trigger_ids_for_list", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_flow_trigger_ids_for_list",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Metrics
@mcp.tool()
async def list_metrics(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format (or with optional suffix). Defaults to 2026-01-15 if not specified."),
    filter_: str | None = Field(None, alias="filter", description="Filter metrics by integration name or category using equality operators. Specify as a filter expression (e.g., equals(integration.name,'value') or equals(integration.category,'value'))."),
) -> dict[str, Any]:
    """Retrieve all metrics in your account with optional filtering by integration name or category. Returns up to 200 results per page."""

    # Construct request model with validation
    try:
        _request = _models.GetMetricsRequest(
            query=_models.GetMetricsRequestQuery(filter_=filter_),
            header=_models.GetMetricsRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_metrics: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/metrics"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_metrics")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_metrics", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_metrics",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Metrics
@mcp.tool()
async def get_metric(
    id_: str = Field(..., alias="id", description="The unique identifier of the metric to retrieve."),
    revision: str = Field(..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.v1). Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve a specific metric by its ID. Returns the metric details for the specified metric identifier."""

    # Construct request model with validation
    try:
        _request = _models.GetMetricRequest(
            path=_models.GetMetricRequestPath(id_=id_),
            header=_models.GetMetricRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_metric: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/metrics/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/metrics/{id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_metric")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_metric", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_metric",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Metrics
@mcp.tool()
async def get_metric_property(
    id_: str = Field(..., alias="id", description="The unique identifier of the metric property to retrieve (UUID format)."),
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format (with optional suffix). Defaults to 2026-01-15 if not specified."),
    fields_metric_property: list[Literal["inferred_type", "label", "property", "sample_values"]] | None = Field(None, alias="fieldsmetric-property", description="Optional sparse fieldset to limit the response to specific metric property fields. Specify which fields to include in the response to optimize payload size."),
) -> dict[str, Any]:
    """Retrieve a specific metric property by its ID. Use this to fetch detailed information about a metric property for inspection or integration purposes."""

    # Construct request model with validation
    try:
        _request = _models.GetMetricPropertyRequest(
            path=_models.GetMetricPropertyRequestPath(id_=id_),
            query=_models.GetMetricPropertyRequestQuery(fields_metric_property=fields_metric_property),
            header=_models.GetMetricPropertyRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_metric_property: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/metric-properties/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/metric-properties/{id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_query = _serialize_query(_http_query, {
        "fields[metric-property]": ("form", False),
    })
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_metric_property")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_metric_property", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_metric_property",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Metrics
@mcp.tool()
async def list_custom_metrics(revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.v1). Defaults to 2026-01-15 if not specified.")) -> dict[str, Any]:
    """Retrieve all custom metrics configured in your account. This operation requires the metrics:read scope and is subject to rate limits of 3 requests per second (burst) and 60 requests per minute (steady state)."""

    # Construct request model with validation
    try:
        _request = _models.GetCustomMetricsRequest(
            header=_models.GetCustomMetricsRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_custom_metrics: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/custom-metrics"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_custom_metrics")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_custom_metrics", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_custom_metrics",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Metrics
@mcp.tool()
async def create_custom_metric(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15 if not specified)."),
    type_: Literal["custom-metric"] = Field(..., alias="type", description="Resource type identifier; must be set to 'custom-metric' for this operation."),
    name: str = Field(..., description="Unique name for the custom metric within your account. Duplicate names will be rejected with a 400 error."),
    aggregation_method: Literal["count", "value"] = Field(..., description="Aggregation method determining how metric measurements are combined. Use 'value' for revenue-based metrics (like Placed Order) or 'count' for conversion-based metrics (like Active on Site)."),
    metric_groups: list[_models.CustomMetricGroup] = Field(..., description="Array of metric groups to associate with this custom metric. Specifies the grouping categories for organizing metric data."),
) -> dict[str, Any]:
    """Create a new custom metric for tracking account-specific measurements. Custom metrics require a unique name and aggregation method to define how measurements are combined."""

    # Construct request model with validation
    try:
        _request = _models.CreateCustomMetricRequest(
            header=_models.CreateCustomMetricRequestHeader(revision=revision),
            body=_models.CreateCustomMetricRequestBody(data=_models.CreateCustomMetricRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateCustomMetricRequestBodyDataAttributes(
                        name=name,
                        definition=_models.CreateCustomMetricRequestBodyDataAttributesDefinition(aggregation_method=aggregation_method, metric_groups=metric_groups)
                    )
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_custom_metric: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/custom-metrics"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_custom_metric")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_custom_metric", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_custom_metric",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Metrics
@mcp.tool()
async def get_custom_metric(
    id_: str = Field(..., alias="id", description="The unique identifier of the custom metric to retrieve, formatted as a hexadecimal string."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format (with optional suffix). Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve a custom metric by its unique identifier. Returns the metric definition and configuration for the specified custom metric ID."""

    # Construct request model with validation
    try:
        _request = _models.GetCustomMetricRequest(
            path=_models.GetCustomMetricRequestPath(id_=id_),
            header=_models.GetCustomMetricRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_custom_metric: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/custom-metrics/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/custom-metrics/{id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_custom_metric")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_custom_metric", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_custom_metric",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Metrics
@mcp.tool()
async def update_custom_metric(
    id_: str = Field(..., alias="id", description="The unique identifier of the custom metric to update, formatted as a 32-character hexadecimal string."),
    revision: str = Field(..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.v1). Defaults to 2026-01-15 if not specified."),
    data_id: str = Field(..., alias="dataId", description="The unique identifier of the custom metric being updated; must match the path ID parameter."),
    type_: Literal["custom-metric"] = Field(..., alias="type", description="The resource type identifier; must be set to 'custom-metric' to indicate this is a custom metric resource."),
    aggregation_method: Literal["count", "value"] = Field(..., description="The aggregation method determines how metric measurements are combined. Use 'value' for revenue-based metrics (e.g., Placed Order) or 'count' for conversion-based metrics (e.g., Active on Site)."),
    metric_groups: list[_models.CustomMetricGroup] = Field(..., description="An array of metric group configurations associated with this custom metric. Specify the order and structure of each group as required by your metric definition."),
    name: str | None = Field(None, description="The display name for the custom metric. Names must be unique within your account; attempting to use a duplicate name will result in a 400 error."),
) -> dict[str, Any]:
    """Update an existing custom metric by ID. Modify the metric's name, aggregation method, and metric groups while maintaining the metric's identity and revision."""

    # Construct request model with validation
    try:
        _request = _models.UpdateCustomMetricRequest(
            path=_models.UpdateCustomMetricRequestPath(id_=id_),
            header=_models.UpdateCustomMetricRequestHeader(revision=revision),
            body=_models.UpdateCustomMetricRequestBody(data=_models.UpdateCustomMetricRequestBodyData(
                    id_=data_id, type_=type_,
                    attributes=_models.UpdateCustomMetricRequestBodyDataAttributes(
                        name=name,
                        definition=_models.UpdateCustomMetricRequestBodyDataAttributesDefinition(aggregation_method=aggregation_method, metric_groups=metric_groups)
                    )
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_custom_metric: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/custom-metrics/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/custom-metrics/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_custom_metric")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_custom_metric", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_custom_metric",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Metrics
@mcp.tool()
async def delete_custom_metric(
    id_: str = Field(..., alias="id", description="The unique identifier of the custom metric to delete, formatted as a 32-character hexadecimal string."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Permanently delete a custom metric by its ID. This operation requires the metrics:write scope and is subject to rate limits of 3 requests per second (burst) or 60 per minute (steady state)."""

    # Construct request model with validation
    try:
        _request = _models.DeleteCustomMetricRequest(
            path=_models.DeleteCustomMetricRequestPath(id_=id_),
            header=_models.DeleteCustomMetricRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_custom_metric: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/custom-metrics/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/custom-metrics/{id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_custom_metric")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_custom_metric", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_custom_metric",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Metrics
@mcp.tool()
async def list_mapped_metrics(revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with an optional suffix. Defaults to 2026-01-15 if not specified.")) -> dict[str, Any]:
    """Retrieve all mapped metrics configured in your account. This operation returns the complete set of metrics that have been mapped for use in your system."""

    # Construct request model with validation
    try:
        _request = _models.GetMappedMetricsRequest(
            header=_models.GetMappedMetricsRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_mapped_metrics: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/mapped-metrics"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_mapped_metrics")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_mapped_metrics", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_mapped_metrics",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Metrics
@mcp.tool()
async def get_mapped_metric(
    id_: Literal["added_to_cart", "cancelled_sales", "ordered_product", "refunded_sales", "revenue", "started_checkout", "viewed_product"] = Field(..., alias="id", description="The metric type identifier. Must be one of the supported conversion event types: added_to_cart, cancelled_sales, ordered_product, refunded_sales, revenue, started_checkout, or viewed_product."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve a mapped metric by its identifier. Mapped metrics represent conversion events tracked across your analytics platform, such as revenue, product views, or checkout initiations."""

    # Construct request model with validation
    try:
        _request = _models.GetMappedMetricRequest(
            path=_models.GetMappedMetricRequestPath(id_=id_),
            header=_models.GetMappedMetricRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_mapped_metric: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/mapped-metrics/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/mapped-metrics/{id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_mapped_metric")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_mapped_metric", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_mapped_metric",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Metrics
@mcp.tool()
async def update_mapped_metric(
    id_: Literal["added_to_cart", "cancelled_sales", "ordered_product", "refunded_sales", "revenue", "started_checkout", "viewed_product"] = Field(..., alias="id", description="The mapped metric type identifier being updated. Must be one of: added_to_cart, cancelled_sales, ordered_product, refunded_sales, revenue, started_checkout, or viewed_product."),
    revision: str = Field(..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15)."),
    data_id: Literal["added_to_cart", "cancelled_sales", "ordered_product", "refunded_sales", "revenue", "started_checkout", "viewed_product"] = Field(..., alias="dataId", description="The mapped metric type identifier in the request body. Must match the path ID and be one of: added_to_cart, cancelled_sales, ordered_product, refunded_sales, revenue, started_checkout, or viewed_product."),
    data_relationships_metric_data_id: str = Field(..., alias="dataRelationshipsMetricDataId", description="The ID of the standard metric to associate with this mapping. Pass null to remove the metric association."),
    data_relationships_custom_metric_data_id: str = Field(..., alias="dataRelationshipsCustom_metricDataId", description="The ID of the custom metric to associate with this mapping. Pass null to remove the custom metric association."),
    type_: Literal["mapped-metric"] = Field(..., alias="type", description="The resource type identifier. Must be set to 'mapped-metric'."),
    metric_data_type: Literal["metric"] = Field(..., alias="metricDataType", description="The resource type identifier for the metric relationship. Must be set to 'metric'."),
    custom_metric_data_type: Literal["custom-metric"] = Field(..., alias="custom_metricDataType", description="The resource type identifier for the custom metric relationship. Must be set to 'custom-metric'."),
) -> dict[str, Any]:
    """Update a mapped metric to change its associations with standard or custom metrics. Use null values to unset metric mappings."""

    # Construct request model with validation
    try:
        _request = _models.UpdateMappedMetricRequest(
            path=_models.UpdateMappedMetricRequestPath(id_=id_),
            header=_models.UpdateMappedMetricRequestHeader(revision=revision),
            body=_models.UpdateMappedMetricRequestBody(data=_models.UpdateMappedMetricRequestBodyData(
                    id_=data_id, type_=type_,
                    relationships=_models.UpdateMappedMetricRequestBodyDataRelationships(
                        metric=_models.UpdateMappedMetricRequestBodyDataRelationshipsMetric(
                            data=_models.UpdateMappedMetricRequestBodyDataRelationshipsMetricData(id_=data_relationships_metric_data_id, type_=metric_data_type)
                        ),
                        custom_metric=_models.UpdateMappedMetricRequestBodyDataRelationshipsCustomMetric(
                            data=_models.UpdateMappedMetricRequestBodyDataRelationshipsCustomMetricData(id_=data_relationships_custom_metric_data_id, type_=custom_metric_data_type)
                        )
                    )
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_mapped_metric: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/mapped-metrics/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/mapped-metrics/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_mapped_metric")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_mapped_metric", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_mapped_metric",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Metrics
@mcp.tool()
async def query_metric_aggregates(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix. Defaults to 2026-01-15."),
    type_: Literal["metric-aggregate"] = Field(..., alias="type", description="Resource type identifier. Must be set to 'metric-aggregate'."),
    metric_id: str = Field(..., description="The unique identifier of the metric to aggregate. Example: '0rG4eQ'."),
    measurements: list[Literal["count", "sum_value", "unique"]] = Field(..., description="One or more measurement types to calculate, such as 'count', 'unique', or 'sum_value'. Order is preserved in results."),
    filter_: list[str] = Field(..., alias="filter", description="Required list of filter conditions to constrain results. Must include a time range using ISO 8601 format (YYYY-MM-DDTHH:MM:SS.mmmmmm) with 'greater-or-equal' and 'less-than' operators on the 'datetime' field, plus any additional attribute filters."),
    interval: Literal["day", "hour", "month", "week"] | None = Field(None, description="Time interval for grouping aggregation results. Supported intervals are hour, day, week, or month. Defaults to day."),
    page_size: int | None = Field(None, description="Maximum number of result rows returned per page. Defaults to 500."),
    by: list[Literal["$attributed_channel", "$attributed_flow", "$attributed_message", "$attributed_variation", "$campaign_channel", "$flow", "$flow_channel", "$message", "$message_send_cohort", "$usage_amount", "$value_currency", "$variation", "$variation_send_cohort", "Bot Click", "Bounce Type", "Campaign Name", "Client Canonical", "Client Name", "Client Type", "Email Domain", "Failure Source", "Failure Type", "From Number", "From Phone Region", "Inbox Provider", "List", "Message Name", "Message Type", "Method", "Segment Count", "Subject", "To Number", "To Phone Region", "URL", "form_id"]] | None = Field(None, description="Optional attributes to partition results by, such as '$message' for message type. Enables multi-dimensional analysis of aggregated data."),
    return_fields: list[str] | None = Field(None, description="Optional list of fields to include in the response. If omitted, all available fields are returned."),
    timezone_: str | None = Field(None, alias="timezone", description="IANA timezone for query processing, such as 'America/New_York'. Defaults to UTC. Case-sensitive. Most timezones are supported except Factory, Europe/Kyiv, and Pacific/Kanton."),
) -> dict[str, Any]:
    """Query and aggregate event data for a metric across native Klaviyo metrics, integrations, and custom events. Results can be filtered by time range and grouped by time intervals, event properties, or profile dimensions."""

    # Construct request model with validation
    try:
        _request = _models.QueryMetricAggregatesRequest(
            header=_models.QueryMetricAggregatesRequestHeader(revision=revision),
            body=_models.QueryMetricAggregatesRequestBody(data=_models.QueryMetricAggregatesRequestBodyData(
                    type_=type_,
                    attributes=_models.QueryMetricAggregatesRequestBodyDataAttributes(metric_id=metric_id, measurements=measurements, interval=interval, page_size=page_size, by=by, return_fields=return_fields, filter_=filter_, timezone_=timezone_)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for query_metric_aggregates: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/metric-aggregates"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("query_metric_aggregates")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("query_metric_aggregates", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="query_metric_aggregates",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Metrics
@mcp.tool()
async def list_flows_triggered_by_metric(
    id_: str = Field(..., alias="id", description="The unique identifier of the metric to query for associated flow triggers."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve all workflows that use the specified metric as a trigger condition. This helps identify which flows depend on a particular metric for activation."""

    # Construct request model with validation
    try:
        _request = _models.GetFlowsTriggeredByMetricRequest(
            path=_models.GetFlowsTriggeredByMetricRequestPath(id_=id_),
            header=_models.GetFlowsTriggeredByMetricRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_flows_triggered_by_metric: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/metrics/{id}/flow-triggers", _request.path.model_dump(by_alias=True)) if _request.path else "/api/metrics/{id}/flow-triggers"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_flows_triggered_by_metric")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_flows_triggered_by_metric", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_flows_triggered_by_metric",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Metrics
@mcp.tool()
async def list_flow_ids_triggered_by_metric(
    id_: str = Field(..., alias="id", description="The unique identifier of the metric for which to retrieve triggered flows."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve the IDs of all flows that use the specified metric as their trigger condition. This allows you to identify which flows are dependent on a particular metric."""

    # Construct request model with validation
    try:
        _request = _models.GetIdsForFlowsTriggeredByMetricRequest(
            path=_models.GetIdsForFlowsTriggeredByMetricRequestPath(id_=id_),
            header=_models.GetIdsForFlowsTriggeredByMetricRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_flow_ids_triggered_by_metric: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/metrics/{id}/relationships/flow-triggers", _request.path.model_dump(by_alias=True)) if _request.path else "/api/metrics/{id}/relationships/flow-triggers"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_flow_ids_triggered_by_metric")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_flow_ids_triggered_by_metric", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_flow_ids_triggered_by_metric",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Metrics
@mcp.tool()
async def get_metric_properties(
    id_: str = Field(..., alias="id", description="The unique identifier of the metric to retrieve properties for (e.g., '925e38')."),
    revision: str = Field(..., description="API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
    fields_metric_property: list[Literal["inferred_type", "label", "property", "sample_values"]] | None = Field(None, alias="fieldsmetric-property", description="Optional list of specific metric-property fields to include in the response. When omitted, all available fields are returned. See API documentation for available field names."),
) -> dict[str, Any]:
    """Retrieve all properties associated with a specific metric by its ID. Use optional field filtering to request only specific metric property attributes."""

    # Construct request model with validation
    try:
        _request = _models.GetPropertiesForMetricRequest(
            path=_models.GetPropertiesForMetricRequestPath(id_=id_),
            query=_models.GetPropertiesForMetricRequestQuery(fields_metric_property=fields_metric_property),
            header=_models.GetPropertiesForMetricRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_metric_properties: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/metrics/{id}/metric-properties", _request.path.model_dump(by_alias=True)) if _request.path else "/api/metrics/{id}/metric-properties"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_query = _serialize_query(_http_query, {
        "fields[metric-property]": ("form", False),
    })
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_metric_properties")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_metric_properties", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_metric_properties",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Metrics
@mcp.tool()
async def list_property_ids_for_metric(
    id_: str = Field(..., alias="id", description="The unique identifier of the metric (e.g., '925e38'). This ID specifies which metric's properties you want to retrieve."),
    revision: str = Field(..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15). Specify a revision to ensure consistent API behavior across requests."),
) -> dict[str, Any]:
    """Retrieve the IDs of all metric properties associated with a specific metric. Use this to discover which properties are linked to a metric."""

    # Construct request model with validation
    try:
        _request = _models.GetPropertyIdsForMetricRequest(
            path=_models.GetPropertyIdsForMetricRequestPath(id_=id_),
            header=_models.GetPropertyIdsForMetricRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_property_ids_for_metric: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/metrics/{id}/relationships/metric-properties", _request.path.model_dump(by_alias=True)) if _request.path else "/api/metrics/{id}/relationships/metric-properties"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_property_ids_for_metric")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_property_ids_for_metric", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_property_ids_for_metric",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Metrics
@mcp.tool()
async def get_metric_for_metric_property(
    id_: str = Field(..., alias="id", description="The unique identifier of the metric property. Use the metric property ID to look up its associated metric."),
    revision: str = Field(..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.v1). Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve the metric associated with a specific metric property. This operation fetches the metric data linked to the given metric property ID."""

    # Construct request model with validation
    try:
        _request = _models.GetMetricForMetricPropertyRequest(
            path=_models.GetMetricForMetricPropertyRequestPath(id_=id_),
            header=_models.GetMetricForMetricPropertyRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_metric_for_metric_property: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/metric-properties/{id}/metric", _request.path.model_dump(by_alias=True)) if _request.path else "/api/metric-properties/{id}/metric"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_metric_for_metric_property")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_metric_for_metric_property", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_metric_for_metric_property",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Metrics
@mcp.tool()
async def get_metric_id_for_metric_property(
    id_: str = Field(..., alias="id", description="The unique identifier of the metric property. Use the metric property ID (a 32-character hexadecimal string) to specify which property's metric relationship you want to retrieve."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve the metric ID associated with a specific metric property. This operation resolves the relationship between a metric property and its parent metric."""

    # Construct request model with validation
    try:
        _request = _models.GetMetricIdForMetricPropertyRequest(
            path=_models.GetMetricIdForMetricPropertyRequestPath(id_=id_),
            header=_models.GetMetricIdForMetricPropertyRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_metric_id_for_metric_property: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/metric-properties/{id}/relationships/metric", _request.path.model_dump(by_alias=True)) if _request.path else "/api/metric-properties/{id}/relationships/metric"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_metric_id_for_metric_property")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_metric_id_for_metric_property", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_metric_id_for_metric_property",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Metrics
@mcp.tool()
async def get_metrics_for_custom_metric(
    id_: str = Field(..., alias="id", description="The unique identifier of the custom metric. Use the custom metric ID returned when the metric was created or retrieved from a list operation."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified, allowing you to control which API version behavior is used."),
) -> dict[str, Any]:
    """Retrieve all metrics associated with a specific custom metric by its ID. This operation allows you to fetch the complete set of metric data points for a given custom metric configuration."""

    # Construct request model with validation
    try:
        _request = _models.GetMetricsForCustomMetricRequest(
            path=_models.GetMetricsForCustomMetricRequestPath(id_=id_),
            header=_models.GetMetricsForCustomMetricRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_metrics_for_custom_metric: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/custom-metrics/{id}/metrics", _request.path.model_dump(by_alias=True)) if _request.path else "/api/custom-metrics/{id}/metrics"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_metrics_for_custom_metric")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_metrics_for_custom_metric", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_metrics_for_custom_metric",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Metrics
@mcp.tool()
async def list_metrics_for_custom_metric(
    id_: str = Field(..., alias="id", description="The unique identifier of the custom metric. This is a 32-character hexadecimal string that uniquely identifies the custom metric resource."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified, allowing you to target specific API versions."),
) -> dict[str, Any]:
    """Retrieve all metric IDs associated with a specific custom metric. Use this to discover which metrics are linked to a custom metric configuration."""

    # Construct request model with validation
    try:
        _request = _models.GetMetricIdsForCustomMetricRequest(
            path=_models.GetMetricIdsForCustomMetricRequestPath(id_=id_),
            header=_models.GetMetricIdsForCustomMetricRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_metrics_for_custom_metric: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/custom-metrics/{id}/relationships/metrics", _request.path.model_dump(by_alias=True)) if _request.path else "/api/custom-metrics/{id}/relationships/metrics"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_metrics_for_custom_metric")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_metrics_for_custom_metric", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_metrics_for_custom_metric",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Metrics
@mcp.tool()
async def get_metric_for_mapped_metric(
    id_: Literal["added_to_cart", "cancelled_sales", "ordered_product", "refunded_sales", "revenue", "started_checkout", "viewed_product"] = Field(..., alias="id", description="The mapped metric type identifier. Must be one of the predefined metric mapping types: added_to_cart, cancelled_sales, ordered_product, refunded_sales, revenue, started_checkout, or viewed_product."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve the metric associated with a specific mapped metric. This operation returns the underlying metric data for a given mapped metric ID, if one exists."""

    # Construct request model with validation
    try:
        _request = _models.GetMetricForMappedMetricRequest(
            path=_models.GetMetricForMappedMetricRequestPath(id_=id_),
            header=_models.GetMetricForMappedMetricRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_metric_for_mapped_metric: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/mapped-metrics/{id}/metric", _request.path.model_dump(by_alias=True)) if _request.path else "/api/mapped-metrics/{id}/metric"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_metric_for_mapped_metric")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_metric_for_mapped_metric", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_metric_for_mapped_metric",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Metrics
@mcp.tool()
async def get_metric_id_for_mapped_metric(
    id_: Literal["added_to_cart", "cancelled_sales", "ordered_product", "refunded_sales", "revenue", "started_checkout", "viewed_product"] = Field(..., alias="id", description="The type of mapped metric to query. Must be one of the predefined mapping types: added_to_cart, cancelled_sales, ordered_product, refunded_sales, revenue, started_checkout, or viewed_product."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve the metric ID associated with a specific mapped metric. This operation resolves the relationship between a mapped metric and its underlying metric."""

    # Construct request model with validation
    try:
        _request = _models.GetMetricIdForMappedMetricRequest(
            path=_models.GetMetricIdForMappedMetricRequestPath(id_=id_),
            header=_models.GetMetricIdForMappedMetricRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_metric_id_for_mapped_metric: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/mapped-metrics/{id}/relationships/metric", _request.path.model_dump(by_alias=True)) if _request.path else "/api/mapped-metrics/{id}/relationships/metric"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_metric_id_for_mapped_metric")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_metric_id_for_mapped_metric", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_metric_id_for_mapped_metric",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Metrics
@mcp.tool()
async def get_custom_metric_for_mapped_metric(
    id_: Literal["added_to_cart", "cancelled_sales", "ordered_product", "refunded_sales", "revenue", "started_checkout", "viewed_product"] = Field(..., alias="id", description="The mapped metric type identifier. Must be one of the predefined event types: added_to_cart, cancelled_sales, ordered_product, refunded_sales, revenue, started_checkout, or viewed_product."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve the custom metric associated with a specific mapped metric. Returns the custom metric details if one exists for the given mapped metric ID."""

    # Construct request model with validation
    try:
        _request = _models.GetCustomMetricForMappedMetricRequest(
            path=_models.GetCustomMetricForMappedMetricRequestPath(id_=id_),
            header=_models.GetCustomMetricForMappedMetricRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_custom_metric_for_mapped_metric: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/mapped-metrics/{id}/custom-metric", _request.path.model_dump(by_alias=True)) if _request.path else "/api/mapped-metrics/{id}/custom-metric"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_custom_metric_for_mapped_metric")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_custom_metric_for_mapped_metric", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_custom_metric_for_mapped_metric",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Metrics
@mcp.tool()
async def get_custom_metric_id_for_mapped_metric(
    id_: Literal["added_to_cart", "cancelled_sales", "ordered_product", "refunded_sales", "revenue", "started_checkout", "viewed_product"] = Field(..., alias="id", description="The type of metric mapping to query. Must be one of the predefined mapping types: added_to_cart, cancelled_sales, ordered_product, refunded_sales, revenue, started_checkout, or viewed_product."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve the custom metric ID associated with a specific mapped metric. This operation returns the relationship between a mapped metric and its underlying custom metric."""

    # Construct request model with validation
    try:
        _request = _models.GetCustomMetricIdForMappedMetricRequest(
            path=_models.GetCustomMetricIdForMappedMetricRequestPath(id_=id_),
            header=_models.GetCustomMetricIdForMappedMetricRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_custom_metric_id_for_mapped_metric: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/mapped-metrics/{id}/relationships/custom-metric", _request.path.model_dump(by_alias=True)) if _request.path else "/api/mapped-metrics/{id}/relationships/custom-metric"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_custom_metric_id_for_mapped_metric")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_custom_metric_id_for_mapped_metric", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_custom_metric_id_for_mapped_metric",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Profiles
@mcp.tool()
async def list_profiles(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format (required; defaults to 2026-01-15)."),
    fields_push_token: list[Literal["background", "created", "enablement_status", "metadata", "metadata.app_build", "metadata.app_id", "metadata.app_name", "metadata.app_version", "metadata.device_id", "metadata.device_model", "metadata.environment", "metadata.klaviyo_sdk", "metadata.manufacturer", "metadata.os_name", "metadata.os_version", "metadata.sdk_version", "platform", "recorded_date", "token", "vendor"]] | None = Field(None, alias="fieldspush-token", description="Specify which push token fields to include in the response using sparse fieldsets for optimized data retrieval."),
    filter_: str | None = Field(None, alias="filter", description="Filter profiles by id, email, phone_number, external_id, _kx identifier, creation/update timestamps, or email subscription and suppression details. Use operators like equals, any, greater-than, and less-than depending on the field."),
    page_size: int | None = Field(None, alias="pagesize", description="Number of profiles to return per page, between 1 and 100 (default: 20).", ge=1, le=100),
) -> dict[str, Any]:
    """Retrieve all profiles in an account with optional filtering, sorting, and enrichment. Supports subscriptions and predictive analytics data via the additional-fields parameter, with different rate limits depending on which enrichments are requested."""

    # Construct request model with validation
    try:
        _request = _models.GetProfilesRequest(
            query=_models.GetProfilesRequestQuery(fields_push_token=fields_push_token, filter_=filter_, page_size=page_size),
            header=_models.GetProfilesRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_profiles: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/profiles"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_query = _serialize_query(_http_query, {
        "fields[push-token]": ("form", False),
    })
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_profiles")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_profiles", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_profiles",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Profiles
@mcp.tool()
async def create_profile(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15)."),
    type_: Literal["profile"] = Field(..., alias="type", description="Profile resource type; must be set to 'profile'."),
    email: str | None = Field(None, description="Individual's email address (e.g., sarah.mason@klaviyo-demo.com)."),
    phone_number: str | None = Field(None, description="Individual's phone number in E.164 format (e.g., +15005550006)."),
    external_id: str | None = Field(None, description="Unique identifier to link this Klaviyo profile with an external system such as a point-of-sale platform; format varies by external system."),
    first_name: str | None = Field(None, description="Individual's first name."),
    last_name: str | None = Field(None, description="Individual's last name."),
    organization: str | None = Field(None, description="Name of the company or organization where the individual works."),
    locale: str | None = Field(None, description="Profile locale in IETF BCP 47 format (e.g., en-US for English-United States)."),
    title: str | None = Field(None, description="Individual's job title."),
    image: str | None = Field(None, description="URL pointing to the profile's image."),
    address1: str | None = Field(None, description="First line of the street address."),
    address2: str | None = Field(None, description="Second line of the street address (e.g., apartment or suite number)."),
    city: str | None = Field(None, description="City name."),
    country: str | None = Field(None, description="Country name."),
    latitude: str | None = Field(None, description="Latitude coordinate; provide at least four decimal places for precision. Accepts string or number format."),
    longitude: str | None = Field(None, description="Longitude coordinate; provide at least four decimal places for precision. Accepts string or number format."),
    region: str | None = Field(None, description="Region within a country, such as state or province (e.g., NY)."),
    zip_: str | None = Field(None, alias="zip", description="Zip or postal code."),
    timezone_: str | None = Field(None, alias="timezone", description="Time zone name using the IANA Time Zone Database (e.g., America/New_York)."),
    ip: str | None = Field(None, description="IP address of the individual."),
    properties: dict[str, Any] | None = Field(None, description="Custom key-value properties to attach to the profile (e.g., {'pseudonym': 'Dr. Octopus'})."),
) -> dict[str, Any]:
    """Create a new customer profile with contact information, location data, and custom properties. Use the `additional-fields` parameter to include subscriptions and predictive analytics in the response."""

    # Construct request model with validation
    try:
        _request = _models.CreateProfileRequest(
            header=_models.CreateProfileRequestHeader(revision=revision),
            body=_models.CreateProfileRequestBody(data=_models.CreateProfileRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateProfileRequestBodyDataAttributes(email=email, phone_number=phone_number, external_id=external_id, first_name=first_name, last_name=last_name, organization=organization, locale=locale, title=title, image=image, properties=properties,
                        location=_models.CreateProfileRequestBodyDataAttributesLocation(address1=address1, address2=address2, city=city, country=country, latitude=latitude, longitude=longitude, region=region, zip_=zip_, timezone_=timezone_, ip=ip) if any(v is not None for v in [address1, address2, city, country, latitude, longitude, region, zip_, timezone_, ip]) else None) if any(v is not None for v in [email, phone_number, external_id, first_name, last_name, organization, locale, title, image, address1, address2, city, country, latitude, longitude, region, zip_, timezone_, ip, properties]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_profile: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/profiles"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_profile")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_profile", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_profile",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Profiles
@mcp.tool()
async def get_profile(
    id_: str = Field(..., alias="id", description="The unique identifier of the profile to retrieve."),
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix. Defaults to 2026-01-15 if not specified."),
    fields_list: list[Literal["created", "name", "opt_in_process", "updated"]] | None = Field(None, alias="fieldslist", description="Optional sparse fieldset for list-related profile fields. Specify which fields to include in the response to optimize data transfer."),
    fields_push_token: list[Literal["background", "created", "enablement_status", "metadata", "metadata.app_build", "metadata.app_id", "metadata.app_name", "metadata.app_version", "metadata.device_id", "metadata.device_model", "metadata.environment", "metadata.klaviyo_sdk", "metadata.manufacturer", "metadata.os_name", "metadata.os_version", "metadata.sdk_version", "platform", "recorded_date", "token", "vendor"]] | None = Field(None, alias="fieldspush-token", description="Optional sparse fieldset for push-token-related profile fields. Specify which fields to include in the response to optimize data transfer."),
    fields_segment: list[Literal["created", "definition", "definition.condition_groups", "is_active", "is_processing", "is_starred", "name", "updated"]] | None = Field(None, alias="fieldssegment", description="Optional sparse fieldset for segment-related profile fields. Specify which fields to include in the response to optimize data transfer. Note: Using this parameter reduces rate limits to 1 request per second (burst) and 15 requests per minute (steady)."),
) -> dict[str, Any]:
    """Retrieve a profile by ID with optional support for subscriptions and predictive analytics data. Be aware of rate limits that vary based on the `fields` parameters used."""

    # Construct request model with validation
    try:
        _request = _models.GetProfileRequest(
            path=_models.GetProfileRequestPath(id_=id_),
            query=_models.GetProfileRequestQuery(fields_list=fields_list, fields_push_token=fields_push_token, fields_segment=fields_segment),
            header=_models.GetProfileRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_profile: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/profiles/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/profiles/{id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_query = _serialize_query(_http_query, {
        "fields[list]": ("form", False),
        "fields[push-token]": ("form", False),
        "fields[segment]": ("form", False),
    })
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_profile")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_profile", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_profile",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Profiles
@mcp.tool()
async def update_profile(
    id_: str = Field(..., alias="id", description="The unique profile identifier (Klaviyo-generated) that specifies which profile to update."),
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format (or with optional suffix). Defaults to 2026-01-15."),
    data_id: str = Field(..., alias="dataId", description="The unique profile identifier in the request body; must match the path ID."),
    type_: Literal["profile"] = Field(..., alias="type", description="The resource type; must be 'profile'."),
    email: str | None = Field(None, description="The individual's email address."),
    phone_number: str | None = Field(None, description="The individual's phone number in E.164 format (e.g., +1 followed by country and number)."),
    external_id: str | None = Field(None, description="A unique identifier from an external system (such as a point-of-sale system) to link this Klaviyo profile with external records."),
    first_name: str | None = Field(None, description="The individual's first name."),
    last_name: str | None = Field(None, description="The individual's last name."),
    organization: str | None = Field(None, description="The name of the company or organization where the individual works."),
    locale: str | None = Field(None, description="The profile's locale in IETF BCP 47 format (e.g., en-US for English-United States)."),
    title: str | None = Field(None, description="The individual's job title."),
    image: str | None = Field(None, description="A URL pointing to the profile's image."),
    address1: str | None = Field(None, description="The first line of the street address."),
    address2: str | None = Field(None, description="The second line of the street address (e.g., apartment or suite number)."),
    city: str | None = Field(None, description="The city name."),
    country: str | None = Field(None, description="The country name."),
    latitude: str | None = Field(None, description="The latitude coordinate; provide at least four decimal places for precision."),
    longitude: str | None = Field(None, description="The longitude coordinate; provide at least four decimal places for precision."),
    region: str | None = Field(None, description="The region within the country, such as a state or province."),
    zip_: str | None = Field(None, alias="zip", description="The postal or zip code."),
    timezone_: str | None = Field(None, alias="timezone", description="The time zone name using the IANA Time Zone Database (e.g., America/New_York)."),
    ip: str | None = Field(None, description="The IP address associated with the profile."),
    properties: dict[str, Any] | None = Field(None, description="A key-value object containing custom properties assigned to this profile."),
    append: dict[str, Any] | None = Field(None, description="Append one or more simple values to an existing property array (e.g., add SKUs to a list)."),
    unappend: dict[str, Any] | None = Field(None, description="Remove one or more simple values from an existing property array (e.g., remove SKUs from a list)."),
    unset: str | list[str] | None = Field(None, description="Remove one or more keys (and their values) completely from the properties object."),
) -> dict[str, Any]:
    """Update an existing customer profile with new or modified information. Use the `additional-fields` parameter to include subscriptions and predictive analytics data in the response. Setting a field to `null` clears it; omitting a field leaves it unchanged."""

    # Construct request model with validation
    try:
        _request = _models.UpdateProfileRequest(
            path=_models.UpdateProfileRequestPath(id_=id_),
            header=_models.UpdateProfileRequestHeader(revision=revision),
            body=_models.UpdateProfileRequestBody(data=_models.UpdateProfileRequestBodyData(
                    id_=data_id, type_=type_,
                    attributes=_models.UpdateProfileRequestBodyDataAttributes(email=email, phone_number=phone_number, external_id=external_id, first_name=first_name, last_name=last_name, organization=organization, locale=locale, title=title, image=image, properties=properties,
                        location=_models.UpdateProfileRequestBodyDataAttributesLocation(address1=address1, address2=address2, city=city, country=country, latitude=latitude, longitude=longitude, region=region, zip_=zip_, timezone_=timezone_, ip=ip) if any(v is not None for v in [address1, address2, city, country, latitude, longitude, region, zip_, timezone_, ip]) else None) if any(v is not None for v in [email, phone_number, external_id, first_name, last_name, organization, locale, title, image, address1, address2, city, country, latitude, longitude, region, zip_, timezone_, ip, properties]) else None,
                    meta=_models.UpdateProfileRequestBodyDataMeta(patch_properties=_models.UpdateProfileRequestBodyDataMetaPatchProperties(append=append, unappend=unappend, unset=unset) if any(v is not None for v in [append, unappend, unset]) else None) if any(v is not None for v in [append, unappend, unset]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_profile: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/profiles/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/profiles/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_profile")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_profile", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_profile",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Profiles
@mcp.tool()
async def list_bulk_import_profiles_jobs(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format (with optional suffix). Defaults to 2026-01-15."),
    fields_profile_bulk_import_job: list[Literal["completed_at", "completed_count", "created_at", "expires_at", "failed_count", "started_at", "status", "total_count"]] | None = Field(None, alias="fieldsprofile-bulk-import-job", description="Specify which fields to include in the response for each bulk import job. Supports sparse fieldsets to optimize payload size."),
    filter_: str | None = Field(None, alias="filter", description="Filter results by job status using equality or any-match operators. Supported field: `status` with operators `equals` and `any`."),
    page_size: int | None = Field(None, alias="pagesize", description="Number of jobs to return per page. Must be between 1 and 100, with a default of 20.", ge=1, le=100),
) -> dict[str, Any]:
    """Retrieve all bulk profile import jobs with optional filtering and pagination. Returns up to 100 jobs per request."""

    # Construct request model with validation
    try:
        _request = _models.GetBulkImportProfilesJobsRequest(
            query=_models.GetBulkImportProfilesJobsRequestQuery(fields_profile_bulk_import_job=fields_profile_bulk_import_job, filter_=filter_, page_size=page_size),
            header=_models.GetBulkImportProfilesJobsRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_bulk_import_profiles_jobs: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/profile-bulk-import-jobs"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_query = _serialize_query(_http_query, {
        "fields[profile-bulk-import-job]": ("form", False),
    })
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_bulk_import_profiles_jobs")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_bulk_import_profiles_jobs", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_bulk_import_profiles_jobs",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Profiles
@mcp.tool()
async def create_profile_bulk_import_job(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format (or with optional suffix). Defaults to 2026-01-15 if not specified."),
    type_: Literal["profile-bulk-import-job"] = Field(..., alias="type", description="Resource type identifier for this operation. Must be set to 'profile-bulk-import-job'."),
    profiles_data: list[_models.ProfileUpsertQueryResourceObject] = Field(..., alias="profilesData", description="Array of profile objects to import. Each profile can be up to 100KB. The array can contain up to 10,000 profiles per request. Order is preserved during processing."),
    lists_data: list[_models.BulkImportProfilesBodyDataRelationshipsListsDataItem] | None = Field(None, alias="listsData", description="Optional array of list identifiers to associate the imported profiles with. Profiles will be added to these lists upon successful import."),
) -> dict[str, Any]:
    """Create a bulk import job to efficiently create or update up to 10,000 profiles in a single request. The job processes profiles asynchronously and supports payloads up to 5MB total (100KB per profile)."""

    # Construct request model with validation
    try:
        _request = _models.BulkImportProfilesRequest(
            header=_models.BulkImportProfilesRequestHeader(revision=revision),
            body=_models.BulkImportProfilesRequestBody(data=_models.BulkImportProfilesRequestBodyData(
                    type_=type_,
                    attributes=_models.BulkImportProfilesRequestBodyDataAttributes(
                        profiles=_models.BulkImportProfilesRequestBodyDataAttributesProfiles(data=profiles_data)
                    ),
                    relationships=_models.BulkImportProfilesRequestBodyDataRelationships(lists=_models.BulkImportProfilesRequestBodyDataRelationshipsLists(data=lists_data) if any(v is not None for v in [lists_data]) else None) if any(v is not None for v in [lists_data]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_profile_bulk_import_job: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/profile-bulk-import-jobs"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_profile_bulk_import_job")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_profile_bulk_import_job", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_profile_bulk_import_job",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Profiles
@mcp.tool()
async def get_bulk_import_profiles_job(
    job_id: str = Field(..., description="The unique identifier of the bulk import job to retrieve (format: alphanumeric string)."),
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format (or with optional suffix). Defaults to 2026-01-15 if not specified."),
    fields_list: list[Literal["created", "name", "opt_in_process", "updated"]] | None = Field(None, alias="fieldslist", description="Optional list of top-level resource types to include in the response. Specify resource types to retrieve only those fields across all included resources."),
    fields_profile_bulk_import_job: list[Literal["completed_at", "completed_count", "created_at", "expires_at", "failed_count", "started_at", "status", "total_count"]] | None = Field(None, alias="fieldsprofile-bulk-import-job", description="Optional list of fields specific to the profile bulk import job resource. Specify field names to retrieve only those attributes for the job."),
) -> dict[str, Any]:
    """Retrieve the status and details of a bulk profile import job by its ID. Use this to monitor the progress and results of profile import operations."""

    # Construct request model with validation
    try:
        _request = _models.GetBulkImportProfilesJobRequest(
            path=_models.GetBulkImportProfilesJobRequestPath(job_id=job_id),
            query=_models.GetBulkImportProfilesJobRequestQuery(fields_list=fields_list, fields_profile_bulk_import_job=fields_profile_bulk_import_job),
            header=_models.GetBulkImportProfilesJobRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_bulk_import_profiles_job: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/profile-bulk-import-jobs/{job_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/profile-bulk-import-jobs/{job_id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_query = _serialize_query(_http_query, {
        "fields[list]": ("form", False),
        "fields[profile-bulk-import-job]": ("form", False),
    })
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_bulk_import_profiles_job")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_bulk_import_profiles_job", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_bulk_import_profiles_job",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Profiles
@mcp.tool()
async def list_bulk_suppress_profiles_jobs(
    revision: str = Field(..., description="API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
    filter_: str | None = Field(None, alias="filter", description="Filter results by job status, list ID, or segment ID using equality operators. Specify filters in the format `field_name=value` (e.g., `status=processing`)."),
) -> dict[str, Any]:
    """Retrieve the status of all bulk profile suppression jobs. Use filtering to narrow results by job status, list ID, or segment ID."""

    # Construct request model with validation
    try:
        _request = _models.GetBulkSuppressProfilesJobsRequest(
            query=_models.GetBulkSuppressProfilesJobsRequestQuery(filter_=filter_),
            header=_models.GetBulkSuppressProfilesJobsRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_bulk_suppress_profiles_jobs: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/profile-suppression-bulk-create-jobs"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_bulk_suppress_profiles_jobs")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_bulk_suppress_profiles_jobs", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_bulk_suppress_profiles_jobs",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Profiles
@mcp.tool()
async def create_profile_suppression_bulk_job(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format (or with optional suffix). Defaults to 2026-01-15."),
    type_: Literal["profile-suppression-bulk-create-job"] = Field(..., alias="type", description="Resource type identifier for the bulk suppression job. Must be set to 'profile-suppression-bulk-create-job'."),
    list_data_type: Literal["list"] = Field(..., alias="listDataType", description="Resource type identifier for list-based suppression. Must be set to 'list' when suppressing by list membership."),
    segment_data_type: Literal["segment"] = Field(..., alias="segmentDataType", description="Resource type identifier for segment-based suppression. Must be set to 'segment' when suppressing by segment membership."),
    data: list[_models.ProfileSuppressionCreateQueryResourceObject] = Field(..., description="Array of email addresses to suppress. Maximum 100 email addresses per request. Specify this to suppress individual profiles, or use list/segment ID instead to suppress all members of a group."),
    list_data_id: str = Field(..., alias="listDataId", description="ID of the list whose current members should be suppressed. Provide this to suppress all profiles in a specific list, or use the email addresses array for individual suppressions."),
    segment_data_id: str = Field(..., alias="segmentDataId", description="ID of the segment whose current members should be suppressed. Provide this to suppress all profiles in a specific segment, or use the email addresses array for individual suppressions."),
) -> dict[str, Any]:
    """Create a bulk job to suppress profiles from receiving email marketing. Suppress profiles by providing individual email addresses (up to 100 per request) or by specifying a segment or list ID to suppress all current members."""

    # Construct request model with validation
    try:
        _request = _models.BulkSuppressProfilesRequest(
            header=_models.BulkSuppressProfilesRequestHeader(revision=revision),
            body=_models.BulkSuppressProfilesRequestBody(data=_models.BulkSuppressProfilesRequestBodyData(
                    type_=type_,
                    relationships=_models.BulkSuppressProfilesRequestBodyDataRelationships(
                        list_=_models.BulkSuppressProfilesRequestBodyDataRelationshipsList(
                            data=_models.BulkSuppressProfilesRequestBodyDataRelationshipsListData(type_=list_data_type, id_=list_data_id)
                        ),
                        segment=_models.BulkSuppressProfilesRequestBodyDataRelationshipsSegment(
                            data=_models.BulkSuppressProfilesRequestBodyDataRelationshipsSegmentData(type_=segment_data_type, id_=segment_data_id)
                        )
                    ),
                    attributes=_models.BulkSuppressProfilesRequestBodyDataAttributes(
                        profiles=_models.BulkSuppressProfilesRequestBodyDataAttributesProfiles(data=data)
                    )
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_profile_suppression_bulk_job: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/profile-suppression-bulk-create-jobs"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_profile_suppression_bulk_job")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_profile_suppression_bulk_job", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_profile_suppression_bulk_job",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Profiles
@mcp.tool()
async def get_bulk_suppress_profiles_job(
    job_id: str = Field(..., description="The unique identifier of the bulk suppress profiles job to retrieve (e.g., 01GSQPBF74KQ5YTDEPP41T1BZH)."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, optionally with a suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve the status and details of a bulk suppress profiles job by its ID. Use this to monitor the progress and results of profile suppression operations."""

    # Construct request model with validation
    try:
        _request = _models.GetBulkSuppressProfilesJobRequest(
            path=_models.GetBulkSuppressProfilesJobRequestPath(job_id=job_id),
            header=_models.GetBulkSuppressProfilesJobRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_bulk_suppress_profiles_job: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/profile-suppression-bulk-create-jobs/{job_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/profile-suppression-bulk-create-jobs/{job_id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_bulk_suppress_profiles_job")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_bulk_suppress_profiles_job", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_bulk_suppress_profiles_job",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Profiles
@mcp.tool()
async def list_bulk_unsuppress_profiles_jobs(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format (or with optional suffix). Defaults to 2026-01-15 if not specified."),
    filter_: str | None = Field(None, alias="filter", description="Filter results by job status, list ID, or segment ID using equality operators. Specify filters in the format `field_name=value` (e.g., `status=processing` to show only processing jobs)."),
) -> dict[str, Any]:
    """Retrieve all bulk unsuppress profiles jobs with optional filtering by status, list ID, or segment ID. Use this to monitor the progress and status of profile unsuppression operations."""

    # Construct request model with validation
    try:
        _request = _models.GetBulkUnsuppressProfilesJobsRequest(
            query=_models.GetBulkUnsuppressProfilesJobsRequestQuery(filter_=filter_),
            header=_models.GetBulkUnsuppressProfilesJobsRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_bulk_unsuppress_profiles_jobs: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/profile-suppression-bulk-delete-jobs"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_bulk_unsuppress_profiles_jobs")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_bulk_unsuppress_profiles_jobs", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_bulk_unsuppress_profiles_jobs",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Profiles
@mcp.tool()
async def remove_profile_suppressions_bulk(
    revision: str = Field(..., description="API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15."),
    type_: Literal["profile-suppression-bulk-delete-job"] = Field(..., alias="type", description="Resource type identifier for the bulk suppression deletion job. Must be 'profile-suppression-bulk-delete-job'."),
    list_data_type: Literal["list"] = Field(..., alias="listDataType", description="Resource type identifier for list relationships. Must be 'list'."),
    segment_data_type: Literal["segment"] = Field(..., alias="segmentDataType", description="Resource type identifier for segment relationships. Must be 'segment'."),
    data: list[_models.ProfileSuppressionDeleteQueryResourceObject] = Field(..., description="Array of email addresses to unsuppress. Maximum 100 email addresses per request."),
    list_data_id: str = Field(..., alias="listDataId", description="The ID of the list whose current members should have suppressions removed. Provide either this or segment.data.id, not both."),
    segment_data_id: str = Field(..., alias="segmentDataId", description="The ID of the segment whose current members should have suppressions removed. Provide either this or list.data.id, not both."),
) -> dict[str, Any]:
    """Bulk remove USER_SUPPRESSED suppressions from profiles by email address or by unsuppressing all members of a specified segment or list. Other suppression reasons (unsubscribed, invalid email, hard bounce) are not affected."""

    # Construct request model with validation
    try:
        _request = _models.BulkUnsuppressProfilesRequest(
            header=_models.BulkUnsuppressProfilesRequestHeader(revision=revision),
            body=_models.BulkUnsuppressProfilesRequestBody(data=_models.BulkUnsuppressProfilesRequestBodyData(
                    type_=type_,
                    relationships=_models.BulkUnsuppressProfilesRequestBodyDataRelationships(
                        list_=_models.BulkUnsuppressProfilesRequestBodyDataRelationshipsList(
                            data=_models.BulkUnsuppressProfilesRequestBodyDataRelationshipsListData(type_=list_data_type, id_=list_data_id)
                        ),
                        segment=_models.BulkUnsuppressProfilesRequestBodyDataRelationshipsSegment(
                            data=_models.BulkUnsuppressProfilesRequestBodyDataRelationshipsSegmentData(type_=segment_data_type, id_=segment_data_id)
                        )
                    ),
                    attributes=_models.BulkUnsuppressProfilesRequestBodyDataAttributes(
                        profiles=_models.BulkUnsuppressProfilesRequestBodyDataAttributesProfiles(data=data)
                    )
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_profile_suppressions_bulk: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/profile-suppression-bulk-delete-jobs"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_profile_suppressions_bulk")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_profile_suppressions_bulk", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_profile_suppressions_bulk",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Profiles
@mcp.tool()
async def get_bulk_unsuppress_profiles_job(
    job_id: str = Field(..., description="The unique identifier of the bulk unsuppress job to retrieve (e.g., 01GSQPBF74KQ5YTDEPP41T1BZH)."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, optionally with a suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve the status and details of a bulk unsuppress profiles job by its ID. Use this to monitor the progress of profile unsuppression operations."""

    # Construct request model with validation
    try:
        _request = _models.GetBulkUnsuppressProfilesJobRequest(
            path=_models.GetBulkUnsuppressProfilesJobRequestPath(job_id=job_id),
            header=_models.GetBulkUnsuppressProfilesJobRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_bulk_unsuppress_profiles_job: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/profile-suppression-bulk-delete-jobs/{job_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/profile-suppression-bulk-delete-jobs/{job_id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_bulk_unsuppress_profiles_job")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_bulk_unsuppress_profiles_job", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_bulk_unsuppress_profiles_job",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Profiles
@mcp.tool()
async def list_push_tokens(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format (with optional suffix). Defaults to 2026-01-15 if not specified."),
    fields_push_token: list[Literal["background", "created", "enablement_status", "metadata", "metadata.app_build", "metadata.app_id", "metadata.app_name", "metadata.app_version", "metadata.device_id", "metadata.device_model", "metadata.environment", "metadata.klaviyo_sdk", "metadata.manufacturer", "metadata.os_name", "metadata.os_version", "metadata.sdk_version", "platform", "recorded_date", "token", "vendor"]] | None = Field(None, alias="fieldspush-token", description="Specify which push token fields to include in the response using sparse fieldsets for optimized payload size."),
    filter_: str | None = Field(None, alias="filter", description="Filter results by push token properties. Supported filters: token ID, associated profile ID, enablement status, or platform. Use equals operator with the format: field_name equals('value')."),
    page_size: int | None = Field(None, alias="pagesize", description="Number of results per page. Must be between 1 and 100 items. Defaults to 20 if not specified.", ge=1, le=100),
) -> dict[str, Any]:
    """Retrieve push tokens associated with your company account. Supports filtering by token ID, profile ID, enablement status, and platform, with optional sparse fieldset selection."""

    # Construct request model with validation
    try:
        _request = _models.GetPushTokensRequest(
            query=_models.GetPushTokensRequestQuery(fields_push_token=fields_push_token, filter_=filter_, page_size=page_size),
            header=_models.GetPushTokensRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_push_tokens: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/push-tokens"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_query = _serialize_query(_http_query, {
        "fields[push-token]": ("form", False),
    })
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_push_tokens")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_push_tokens", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_push_tokens",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Profiles
@mcp.tool()
async def create_or_update_push_token(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix. Defaults to 2026-01-15."),
    type_: Literal["push-token"] = Field(..., alias="type", description="Resource type identifier. Must be 'push-token'."),
    token: str = Field(..., description="The push token string from APNS (Apple) or FCM (Google). This is the credential needed to send push notifications to the device."),
    platform: Literal["android", "ios"] = Field(..., description="The mobile platform where the push token was generated. Must be either 'ios' or 'android'."),
    vendor: Literal["apns", "fcm"] = Field(..., description="The push service provider. Must be 'apns' for Apple devices or 'fcm' for Android devices."),
    enablement_status: Literal["AUTHORIZED", "DENIED", "NOT_DETERMINED", "PROVISIONAL", "UNAUTHORIZED"] | None = Field(None, description="Authorization status for this push token. Indicates whether the user has granted, denied, or not yet determined push notification permissions. Defaults to 'AUTHORIZED'."),
    background: Literal["AVAILABLE", "DENIED", "RESTRICTED"] | None = Field(None, description="Whether the device can receive background push notifications. Defaults to 'AVAILABLE'. Use 'DENIED' or 'RESTRICTED' if background delivery is not permitted."),
    device_metadata: _models.CreatePushTokenBodyDataAttributesDeviceMetadata | None = Field(None, description="Device metadata: device_id, model, OS, app info, SDK version, and environment."),
    profile: _models.CreatePushTokenBodyDataAttributesProfile | None = Field(None, description="Profile to associate with the push token: email, phone, name, location, and custom properties."),
) -> dict[str, Any]:
    """Create or update a push token for a user's device, enabling push notification delivery. This endpoint supports migrating push tokens from other platforms and accepts device metadata to enhance targeting and analytics."""

    # Construct request model with validation
    try:
        _request = _models.CreatePushTokenRequest(
            header=_models.CreatePushTokenRequestHeader(revision=revision),
            body=_models.CreatePushTokenRequestBody(data=_models.CreatePushTokenRequestBodyData(
                    type_=type_,
                    attributes=_models.CreatePushTokenRequestBodyDataAttributes(token=token, platform=platform, enablement_status=enablement_status, vendor=vendor, background=background, device_metadata=device_metadata, profile=profile)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_or_update_push_token: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/push-tokens"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_or_update_push_token")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_or_update_push_token", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_or_update_push_token",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Profiles
@mcp.tool()
async def get_push_token(
    id_: str = Field(..., alias="id", description="The unique identifier of the push token to retrieve."),
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format (or with optional suffix). Defaults to 2026-01-15 if not specified."),
    fields_push_token: list[Literal["background", "created", "enablement_status", "metadata", "metadata.app_build", "metadata.app_id", "metadata.app_name", "metadata.app_version", "metadata.device_id", "metadata.device_model", "metadata.environment", "metadata.klaviyo_sdk", "metadata.manufacturer", "metadata.os_name", "metadata.os_version", "metadata.sdk_version", "platform", "recorded_date", "token", "vendor"]] | None = Field(None, alias="fieldspush-token", description="Specify which fields to include in the push token response using sparse fieldsets. Omit to receive all available fields."),
) -> dict[str, Any]:
    """Retrieve a specific push token by its ID. Returns detailed information about the push token configuration and status."""

    # Construct request model with validation
    try:
        _request = _models.GetPushTokenRequest(
            path=_models.GetPushTokenRequestPath(id_=id_),
            query=_models.GetPushTokenRequestQuery(fields_push_token=fields_push_token),
            header=_models.GetPushTokenRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_push_token: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/push-tokens/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/push-tokens/{id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_query = _serialize_query(_http_query, {
        "fields[push-token]": ("form", False),
    })
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_push_token")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_push_token", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_push_token",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Profiles
@mcp.tool()
async def delete_push_token(
    id_: str = Field(..., alias="id", description="The unique identifier of the push token to delete, typically a 32-character hexadecimal string."),
    revision: str = Field(..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15 if not specified)."),
) -> dict[str, Any]:
    """Permanently delete a push token by its ID. This operation requires write access to push tokens and is subject to rate limits (3 requests per second burst, 60 per minute steady)."""

    # Construct request model with validation
    try:
        _request = _models.DeletePushTokenRequest(
            path=_models.DeletePushTokenRequestPath(id_=id_),
            header=_models.DeletePushTokenRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_push_token: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/push-tokens/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/push-tokens/{id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_push_token")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_push_token", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_push_token",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Profiles
@mcp.tool()
async def create_or_update_profile(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15)."),
    type_: Literal["profile"] = Field(..., alias="type", description="Resource type identifier; must be set to 'profile'."),
    email: str | None = Field(None, description="Individual's email address (e.g., sarah.mason@klaviyo-demo.com)."),
    phone_number: str | None = Field(None, description="Individual's phone number in E.164 format (e.g., +15005550006)."),
    external_id: str | None = Field(None, description="Unique external identifier to associate this Klaviyo profile with a profile in an external system such as a point-of-sale system. Format varies by external system."),
    kx: str | None = Field(None, description="Encrypted exchange identifier used by Klaviyo's web tracking to identify profiles. Can be used as a filter when retrieving profiles."),
    first_name: str | None = Field(None, description="Individual's first name."),
    last_name: str | None = Field(None, description="Individual's last name."),
    organization: str | None = Field(None, description="Name of the company or organization where the individual works."),
    locale: str | None = Field(None, description="Profile locale in IETF BCP 47 format (e.g., en-US for English-United States)."),
    title: str | None = Field(None, description="Individual's job title."),
    image: str | None = Field(None, description="URL pointing to the profile's image."),
    address1: str | None = Field(None, description="First line of the street address."),
    address2: str | None = Field(None, description="Second line of the street address (e.g., apartment or floor number)."),
    city: str | None = Field(None, description="City name."),
    country: str | None = Field(None, description="Country name."),
    latitude: str | None = Field(None, description="Latitude coordinate; recommend precision of four decimal places. Accepts string or number format."),
    longitude: str | None = Field(None, description="Longitude coordinate; recommend precision of four decimal places. Accepts string or number format."),
    region: str | None = Field(None, description="Region within a country, such as state or province (e.g., NY)."),
    zip_: str | None = Field(None, alias="zip", description="Zip or postal code."),
    timezone_: str | None = Field(None, alias="timezone", description="Time zone name using the IANA Time Zone Database format (e.g., America/New_York)."),
    ip: str | None = Field(None, description="IP address associated with the profile."),
    properties: dict[str, Any] | None = Field(None, description="Object containing custom key-value pairs for profile properties. Setting a field to null clears it; omitting a field leaves it unchanged."),
    append: dict[str, Any] | None = Field(None, description="Object specifying simple values to append to property arrays (e.g., add SKUs to an existing list)."),
    unappend: dict[str, Any] | None = Field(None, description="Object specifying simple values to remove from property arrays (e.g., remove SKUs from an existing list)."),
    unset: str | list[str] | None = Field(None, description="Array or string specifying property keys to remove completely from the profile, including all their values."),
) -> dict[str, Any]:
    """Create a new profile or update an existing one with the provided attributes. Returns 201 for newly created profiles and 200 for updates. Use the `additional-fields` parameter to include subscriptions and predictive analytics in the response."""

    # Construct request model with validation
    try:
        _request = _models.CreateOrUpdateProfileRequest(
            header=_models.CreateOrUpdateProfileRequestHeader(revision=revision),
            body=_models.CreateOrUpdateProfileRequestBody(data=_models.CreateOrUpdateProfileRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateOrUpdateProfileRequestBodyDataAttributes(email=email, phone_number=phone_number, external_id=external_id, kx=kx, first_name=first_name, last_name=last_name, organization=organization, locale=locale, title=title, image=image, properties=properties,
                        location=_models.CreateOrUpdateProfileRequestBodyDataAttributesLocation(address1=address1, address2=address2, city=city, country=country, latitude=latitude, longitude=longitude, region=region, zip_=zip_, timezone_=timezone_, ip=ip) if any(v is not None for v in [address1, address2, city, country, latitude, longitude, region, zip_, timezone_, ip]) else None) if any(v is not None for v in [email, phone_number, external_id, kx, first_name, last_name, organization, locale, title, image, address1, address2, city, country, latitude, longitude, region, zip_, timezone_, ip, properties]) else None,
                    meta=_models.CreateOrUpdateProfileRequestBodyDataMeta(patch_properties=_models.CreateOrUpdateProfileRequestBodyDataMetaPatchProperties(append=append, unappend=unappend, unset=unset) if any(v is not None for v in [append, unappend, unset]) else None) if any(v is not None for v in [append, unappend, unset]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_or_update_profile: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/profile-import"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_or_update_profile")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_or_update_profile", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_or_update_profile",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Profiles
@mcp.tool()
async def merge_profiles(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format (with optional suffix). Defaults to 2026-01-15 if not specified."),
    type_: Literal["profile-merge"] = Field(..., alias="type", description="The type of operation being performed. Must be set to 'profile-merge'."),
    id_: str = Field(..., alias="id", description="The unique identifier of the destination profile that will receive merged data from the source profile."),
    data: list[_models.MergeProfilesBodyDataRelationshipsProfilesDataItem] | None = Field(None, description="Array containing the source profile relationship to be merged into the destination profile. Only one source profile is accepted per request."),
) -> dict[str, Any]:
    """Merge a source profile into a destination profile by ID. This operation queues an asynchronous task that consolidates data from the source profile into the destination profile and deletes the source profile. Only one source profile can be merged per request."""

    # Construct request model with validation
    try:
        _request = _models.MergeProfilesRequest(
            header=_models.MergeProfilesRequestHeader(revision=revision),
            body=_models.MergeProfilesRequestBody(data=_models.MergeProfilesRequestBodyData(
                    type_=type_, id_=id_,
                    relationships=_models.MergeProfilesRequestBodyDataRelationships(profiles=_models.MergeProfilesRequestBodyDataRelationshipsProfiles(data=data) if any(v is not None for v in [data]) else None) if any(v is not None for v in [data]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for merge_profiles: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/profile-merge"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("merge_profiles")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("merge_profiles", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="merge_profiles",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Profiles
@mcp.tool()
async def subscribe_profiles_bulk(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15)."),
    type_: Literal["profile-subscription-bulk-create-job"] = Field(..., alias="type", description="Resource type identifier; must be 'profile-subscription-bulk-create-job'."),
    list_data_type: Literal["list"] = Field(..., alias="listDataType", description="Resource type for the list relationship; must be 'list'."),
    data: list[_models.ProfileSubscriptionCreateQueryResourceObject] = Field(..., description="Array of profile objects to subscribe. Each profile should include subscription channel preferences and optional push tokens. Maximum 1,000 profiles per request."),
    id_: str = Field(..., alias="id", description="The ID of the list to add newly subscribed profiles to (e.g., 'Y6nRLr')."),
    custom_source: str | None = Field(None, description="Optional custom label or source to record on consent records (e.g., 'Marketing Event'). Useful for tracking subscription origin."),
    historical_import: bool | None = Field(None, description="Set to true when importing historical subscription data where consent was already collected. When enabled, bypasses double opt-in emails and 'Added to list' flows, and requires the consented_at field in the past for each profile."),
) -> dict[str, Any]:
    """Subscribe up to 1,000 profiles to email, SMS, WhatsApp, or push marketing channels. Profiles will be immediately subscribed or sent a double opt-in confirmation based on list settings or account defaults. Removes any existing unsubscribe, spam report, or suppression flags from the profiles."""

    # Construct request model with validation
    try:
        _request = _models.BulkSubscribeProfilesRequest(
            header=_models.BulkSubscribeProfilesRequestHeader(revision=revision),
            body=_models.BulkSubscribeProfilesRequestBody(data=_models.BulkSubscribeProfilesRequestBodyData(
                    type_=type_,
                    relationships=_models.BulkSubscribeProfilesRequestBodyDataRelationships(
                        list_=_models.BulkSubscribeProfilesRequestBodyDataRelationshipsList(
                            data=_models.BulkSubscribeProfilesRequestBodyDataRelationshipsListData(type_=list_data_type, id_=id_)
                        )
                    ),
                    attributes=_models.BulkSubscribeProfilesRequestBodyDataAttributes(
                        custom_source=custom_source, historical_import=historical_import,
                        profiles=_models.BulkSubscribeProfilesRequestBodyDataAttributesProfiles(data=data)
                    )
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for subscribe_profiles_bulk: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/profile-subscription-bulk-create-jobs"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("subscribe_profiles_bulk")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("subscribe_profiles_bulk", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="subscribe_profiles_bulk",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Profiles
@mcp.tool()
async def unsubscribe_profiles_bulk(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format (with optional suffix). Defaults to 2026-01-15."),
    type_: Literal["profile-subscription-bulk-delete-job"] = Field(..., alias="type", description="The type of job being created. Must be 'profile-subscription-bulk-delete-job'."),
    list_data_type: Literal["list"] = Field(..., alias="listDataType", description="The type of resource being referenced. Must be 'list'."),
    data: list[_models.ProfileSubscriptionDeleteQueryResourceObject] = Field(..., description="Array of profile objects to unsubscribe. Maximum 100 profiles per request. Each profile should include the necessary identifiers for the unsubscribe operation."),
    id_: str = Field(..., alias="id", description="The unique identifier of the list from which to unsubscribe the profiles."),
) -> dict[str, Any]:
    """Bulk unsubscribe one or more profiles (up to 100 per request) from email marketing, SMS marketing, or both. ⚠️ Profiles not in the specified list will be globally unsubscribed—always verify list membership before calling to avoid unintended global unsubscribes."""

    # Construct request model with validation
    try:
        _request = _models.BulkUnsubscribeProfilesRequest(
            header=_models.BulkUnsubscribeProfilesRequestHeader(revision=revision),
            body=_models.BulkUnsubscribeProfilesRequestBody(data=_models.BulkUnsubscribeProfilesRequestBodyData(
                    type_=type_,
                    relationships=_models.BulkUnsubscribeProfilesRequestBodyDataRelationships(
                        list_=_models.BulkUnsubscribeProfilesRequestBodyDataRelationshipsList(
                            data=_models.BulkUnsubscribeProfilesRequestBodyDataRelationshipsListData(type_=list_data_type, id_=id_)
                        )
                    ),
                    attributes=_models.BulkUnsubscribeProfilesRequestBodyDataAttributes(
                        profiles=_models.BulkUnsubscribeProfilesRequestBodyDataAttributesProfiles(data=data)
                    )
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for unsubscribe_profiles_bulk: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/profile-subscription-bulk-delete-jobs"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("unsubscribe_profiles_bulk")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("unsubscribe_profiles_bulk", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="unsubscribe_profiles_bulk",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Profiles
@mcp.tool()
async def list_push_tokens_for_profile(
    id_: str = Field(..., alias="id", description="The unique identifier of the profile whose push tokens should be retrieved."),
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format (or with optional suffix). Defaults to 2026-01-15 if not specified."),
    fields_push_token: list[Literal["background", "created", "enablement_status", "metadata", "metadata.app_build", "metadata.app_id", "metadata.app_name", "metadata.app_version", "metadata.device_id", "metadata.device_model", "metadata.environment", "metadata.klaviyo_sdk", "metadata.manufacturer", "metadata.os_name", "metadata.os_version", "metadata.sdk_version", "platform", "recorded_date", "token", "vendor"]] | None = Field(None, alias="fieldspush-token", description="Optional sparse fieldset to limit which push token attributes are included in the response. Specify as a comma-separated list of field names."),
) -> dict[str, Any]:
    """Retrieve all push tokens associated with a specific profile. Use sparse fieldsets to customize which push token attributes are returned in the response."""

    # Construct request model with validation
    try:
        _request = _models.GetPushTokensForProfileRequest(
            path=_models.GetPushTokensForProfileRequestPath(id_=id_),
            query=_models.GetPushTokensForProfileRequestQuery(fields_push_token=fields_push_token),
            header=_models.GetPushTokensForProfileRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_push_tokens_for_profile: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/profiles/{id}/push-tokens", _request.path.model_dump(by_alias=True)) if _request.path else "/api/profiles/{id}/push-tokens"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_query = _serialize_query(_http_query, {
        "fields[push-token]": ("form", False),
    })
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_push_tokens_for_profile")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_push_tokens_for_profile", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_push_tokens_for_profile",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Profiles
@mcp.tool()
async def list_push_token_ids_for_profile(
    id_: str = Field(..., alias="id", description="The unique identifier of the profile for which to retrieve associated push token IDs."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve all push token IDs associated with a specific profile. Returns a collection of push token identifiers linked to the given profile."""

    # Construct request model with validation
    try:
        _request = _models.GetPushTokenIdsForProfileRequest(
            path=_models.GetPushTokenIdsForProfileRequestPath(id_=id_),
            header=_models.GetPushTokenIdsForProfileRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_push_token_ids_for_profile: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/profiles/{id}/relationships/push-tokens", _request.path.model_dump(by_alias=True)) if _request.path else "/api/profiles/{id}/relationships/push-tokens"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_push_token_ids_for_profile")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_push_token_ids_for_profile", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_push_token_ids_for_profile",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Profiles
@mcp.tool()
async def list_lists_for_profile(
    id_: str = Field(..., alias="id", description="The unique identifier of the profile whose list memberships you want to retrieve."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
    fields_list: list[Literal["created", "name", "opt_in_process", "updated"]] | None = Field(None, alias="fieldslist", description="Specify which fields to include in the response using sparse fieldsets. Omit to return default fields. See API documentation for available field names."),
) -> dict[str, Any]:
    """Retrieve all list memberships for a specific profile. Returns the lists that a profile belongs to, with support for sparse fieldsets to customize the response."""

    # Construct request model with validation
    try:
        _request = _models.GetListsForProfileRequest(
            path=_models.GetListsForProfileRequestPath(id_=id_),
            query=_models.GetListsForProfileRequestQuery(fields_list=fields_list),
            header=_models.GetListsForProfileRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_lists_for_profile: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/profiles/{id}/lists", _request.path.model_dump(by_alias=True)) if _request.path else "/api/profiles/{id}/lists"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_query = _serialize_query(_http_query, {
        "fields[list]": ("form", False),
    })
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_lists_for_profile")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_lists_for_profile", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_lists_for_profile",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Profiles
@mcp.tool()
async def get_lists_for_profile_relationship(
    id_: str = Field(..., alias="id", description="The unique identifier of the profile to retrieve list memberships for."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, optionally with a suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve all list memberships for a specific profile. Returns the IDs of lists that the profile belongs to."""

    # Construct request model with validation
    try:
        _request = _models.GetListIdsForProfileRequest(
            path=_models.GetListIdsForProfileRequestPath(id_=id_),
            header=_models.GetListIdsForProfileRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_lists_for_profile_relationship: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/profiles/{id}/relationships/lists", _request.path.model_dump(by_alias=True)) if _request.path else "/api/profiles/{id}/relationships/lists"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_lists_for_profile_relationship")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_lists_for_profile_relationship", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_lists_for_profile_relationship",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Profiles
@mcp.tool()
async def get_segments_for_profile(
    id_: str = Field(..., alias="id", description="The unique identifier of the profile to retrieve segments for."),
    revision: str = Field(..., description="API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
    fields_segment: list[Literal["created", "definition", "definition.condition_groups", "is_active", "is_processing", "is_starred", "name", "updated"]] | None = Field(None, alias="fieldssegment", description="Optional list of specific segment fields to include in the response. Use sparse fieldsets to reduce payload size and improve performance by requesting only needed fields."),
) -> dict[str, Any]:
    """Retrieve all segment memberships for a specific profile. Returns which segments the profile belongs to, with optional field filtering for sparse responses."""

    # Construct request model with validation
    try:
        _request = _models.GetSegmentsForProfileRequest(
            path=_models.GetSegmentsForProfileRequestPath(id_=id_),
            query=_models.GetSegmentsForProfileRequestQuery(fields_segment=fields_segment),
            header=_models.GetSegmentsForProfileRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_segments_for_profile: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/profiles/{id}/segments", _request.path.model_dump(by_alias=True)) if _request.path else "/api/profiles/{id}/segments"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_query = _serialize_query(_http_query, {
        "fields[segment]": ("form", False),
    })
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_segments_for_profile")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_segments_for_profile", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_segments_for_profile",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Profiles
@mcp.tool()
async def list_segment_ids_for_profile(
    id_: str = Field(..., alias="id", description="The unique identifier of the profile whose segment memberships you want to retrieve."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve all segment IDs that a profile is a member of. Returns the segment membership relationships for the specified profile."""

    # Construct request model with validation
    try:
        _request = _models.GetSegmentIdsForProfileRequest(
            path=_models.GetSegmentIdsForProfileRequestPath(id_=id_),
            header=_models.GetSegmentIdsForProfileRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_segment_ids_for_profile: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/profiles/{id}/relationships/segments", _request.path.model_dump(by_alias=True)) if _request.path else "/api/profiles/{id}/relationships/segments"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_segment_ids_for_profile")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_segment_ids_for_profile", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_segment_ids_for_profile",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Profiles
@mcp.tool()
async def get_lists_for_bulk_import_profiles_job(
    id_: str = Field(..., alias="id", description="The unique identifier of the bulk import profiles job."),
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format (or with optional suffix). Defaults to 2026-01-15 if not specified."),
    fields_list: list[Literal["created", "name", "opt_in_process", "updated"]] | None = Field(None, alias="fieldslist", description="Specify which fields to include in the response using sparse fieldsets. Omit to receive all available fields."),
) -> dict[str, Any]:
    """Retrieve the lists associated with a bulk profile import job. Use this to see which lists will receive the imported profiles."""

    # Construct request model with validation
    try:
        _request = _models.GetListForBulkImportProfilesJobRequest(
            path=_models.GetListForBulkImportProfilesJobRequestPath(id_=id_),
            query=_models.GetListForBulkImportProfilesJobRequestQuery(fields_list=fields_list),
            header=_models.GetListForBulkImportProfilesJobRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_lists_for_bulk_import_profiles_job: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/profile-bulk-import-jobs/{id}/lists", _request.path.model_dump(by_alias=True)) if _request.path else "/api/profile-bulk-import-jobs/{id}/lists"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_query = _serialize_query(_http_query, {
        "fields[list]": ("form", False),
    })
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_lists_for_bulk_import_profiles_job")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_lists_for_bulk_import_profiles_job", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_lists_for_bulk_import_profiles_job",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Profiles
@mcp.tool()
async def get_list_ids_for_bulk_import_profiles_job(
    id_: str = Field(..., alias="id", description="The unique identifier of the bulk profile import job for which to retrieve associated list IDs."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve the list IDs associated with a specific bulk profile import job. This operation returns the relationship between a bulk import job and its related lists."""

    # Construct request model with validation
    try:
        _request = _models.GetListIdsForBulkImportProfilesJobRequest(
            path=_models.GetListIdsForBulkImportProfilesJobRequestPath(id_=id_),
            header=_models.GetListIdsForBulkImportProfilesJobRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_list_ids_for_bulk_import_profiles_job: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/profile-bulk-import-jobs/{id}/relationships/lists", _request.path.model_dump(by_alias=True)) if _request.path else "/api/profile-bulk-import-jobs/{id}/relationships/lists"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_list_ids_for_bulk_import_profiles_job")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_list_ids_for_bulk_import_profiles_job", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_list_ids_for_bulk_import_profiles_job",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Profiles
@mcp.tool()
async def list_profiles_for_bulk_import_job(
    id_: str = Field(..., alias="id", description="The unique identifier of the bulk import job whose profiles you want to retrieve."),
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.v1). Defaults to 2026-01-15."),
    page_size: int | None = Field(None, alias="pagesize", description="Number of profiles to return per page. Defaults to 20 profiles; must be between 1 and 100.", ge=1, le=100),
) -> dict[str, Any]:
    """Retrieve profiles associated with a bulk profile import job. Results are paginated and support customizable page sizes."""

    # Construct request model with validation
    try:
        _request = _models.GetProfilesForBulkImportProfilesJobRequest(
            path=_models.GetProfilesForBulkImportProfilesJobRequestPath(id_=id_),
            query=_models.GetProfilesForBulkImportProfilesJobRequestQuery(page_size=page_size),
            header=_models.GetProfilesForBulkImportProfilesJobRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_profiles_for_bulk_import_job: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/profile-bulk-import-jobs/{id}/profiles", _request.path.model_dump(by_alias=True)) if _request.path else "/api/profile-bulk-import-jobs/{id}/profiles"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_profiles_for_bulk_import_job")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_profiles_for_bulk_import_job", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_profiles_for_bulk_import_job",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Profiles
@mcp.tool()
async def list_profile_ids_for_bulk_import_job(
    id_: str = Field(..., alias="id", description="The unique identifier of the bulk import profiles job."),
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.v1). Defaults to 2026-01-15."),
    page_size: int | None = Field(None, alias="pagesize", description="Number of profile IDs to return per page. Defaults to 20, with a maximum of 100 results per page.", ge=1, le=100),
) -> dict[str, Any]:
    """Retrieve the profile IDs associated with a bulk import job. Returns paginated profile relationships for the specified bulk profile import job."""

    # Construct request model with validation
    try:
        _request = _models.GetProfileIdsForBulkImportProfilesJobRequest(
            path=_models.GetProfileIdsForBulkImportProfilesJobRequestPath(id_=id_),
            query=_models.GetProfileIdsForBulkImportProfilesJobRequestQuery(page_size=page_size),
            header=_models.GetProfileIdsForBulkImportProfilesJobRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_profile_ids_for_bulk_import_job: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/profile-bulk-import-jobs/{id}/relationships/profiles", _request.path.model_dump(by_alias=True)) if _request.path else "/api/profile-bulk-import-jobs/{id}/relationships/profiles"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_profile_ids_for_bulk_import_job")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_profile_ids_for_bulk_import_job", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_profile_ids_for_bulk_import_job",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Profiles
@mcp.tool()
async def list_import_errors_for_bulk_import_profiles_job(
    id_: str = Field(..., alias="id", description="The unique identifier of the bulk import job to retrieve errors for."),
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (default: 2026-01-15). Determines the response schema version."),
    fields_import_error: list[Literal["code", "detail", "original_payload", "source", "source.pointer", "title"]] | None = Field(None, alias="fieldsimport-error", description="Specify which fields to include in the import-error response using sparse fieldsets. Omit to return all available fields."),
    page_size: int | None = Field(None, alias="pagesize", description="Number of errors to return per page. Must be between 1 and 100 (default: 20).", ge=1, le=100),
) -> dict[str, Any]:
    """Retrieve import errors for a bulk profile import job. Returns detailed error information for profiles that failed during the import process, with pagination support."""

    # Construct request model with validation
    try:
        _request = _models.GetErrorsForBulkImportProfilesJobRequest(
            path=_models.GetErrorsForBulkImportProfilesJobRequestPath(id_=id_),
            query=_models.GetErrorsForBulkImportProfilesJobRequestQuery(fields_import_error=fields_import_error, page_size=page_size),
            header=_models.GetErrorsForBulkImportProfilesJobRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_import_errors_for_bulk_import_profiles_job: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/profile-bulk-import-jobs/{id}/import-errors", _request.path.model_dump(by_alias=True)) if _request.path else "/api/profile-bulk-import-jobs/{id}/import-errors"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_query = _serialize_query(_http_query, {
        "fields[import-error]": ("form", False),
    })
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_import_errors_for_bulk_import_profiles_job")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_import_errors_for_bulk_import_profiles_job", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_import_errors_for_bulk_import_profiles_job",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Profiles
@mcp.tool()
async def get_profile_for_push_token(
    id_: str = Field(..., alias="id", description="The push token identifier whose associated profile you want to retrieve."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve the user profile associated with a specific push token. This operation allows you to look up profile information linked to a push notification token."""

    # Construct request model with validation
    try:
        _request = _models.GetProfileForPushTokenRequest(
            path=_models.GetProfileForPushTokenRequestPath(id_=id_),
            header=_models.GetProfileForPushTokenRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_profile_for_push_token: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/push-tokens/{id}/profile", _request.path.model_dump(by_alias=True)) if _request.path else "/api/push-tokens/{id}/profile"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_profile_for_push_token")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_profile_for_push_token", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_profile_for_push_token",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Profiles
@mcp.tool()
async def get_profile_id_for_push_token(
    id_: str = Field(..., alias="id", description="The unique identifier of the push token for which you want to retrieve the associated profile ID."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve the profile ID associated with a specific push token. This operation returns the relationship between a push token and its linked user profile."""

    # Construct request model with validation
    try:
        _request = _models.GetProfileIdForPushTokenRequest(
            path=_models.GetProfileIdForPushTokenRequestPath(id_=id_),
            header=_models.GetProfileIdForPushTokenRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_profile_id_for_push_token: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/push-tokens/{id}/relationships/profile", _request.path.model_dump(by_alias=True)) if _request.path else "/api/push-tokens/{id}/relationships/profile"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_profile_id_for_push_token")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_profile_id_for_push_token", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_profile_id_for_push_token",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Reporting
@mcp.tool()
async def query_campaign_values_report(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.v1). Defaults to 2026-01-15 if not specified."),
    type_: Literal["campaign-values-report"] = Field(..., alias="type", description="Report type identifier. Must be set to 'campaign-values-report' to query campaign analytics data."),
    statistics: list[Literal["average_order_value", "bounce_rate", "bounced", "bounced_or_failed", "bounced_or_failed_rate", "click_rate", "click_to_open_rate", "clicks", "clicks_unique", "conversion_rate", "conversion_uniques", "conversion_value", "conversions", "delivered", "delivery_rate", "failed", "failed_rate", "message_segment_count_sum", "open_rate", "opens", "opens_unique", "recipients", "revenue_per_recipient", "spam_complaint_rate", "spam_complaints", "text_message_credit_usage_amount", "text_message_roi", "text_message_spend", "unsubscribe_rate", "unsubscribe_uniques", "unsubscribes"]] = Field(..., description="Comma-separated list of metrics to retrieve (e.g., opens, open_rate, clicks, conversions). Rate-based statistics are returned as decimal values between 0.0 and 1.0."),
    timeframe: _models.Timeframe | _models.CustomTimeframe = Field(..., description="Time period for data retrieval in a supported timeframe format. Maximum span is 1 year. Refer to available timeframes documentation for valid formats."),
    conversion_metric_id: str = Field(..., description="Unique identifier of the conversion metric to use for calculating conversion-related statistics in the report."),
    group_by: list[Literal["campaign_id", "campaign_message_id", "campaign_message_name", "group", "group_name", "send_channel", "tag_id", "tag_name", "text_message_format", "variation", "variation_name"]] | None = Field(None, description="Optional list of dimensions to group results by. Supported dimensions include campaign_id, campaign_message_id, campaign_message_name, group, group_name, send_channel, tag_id, tag_name, text_message_format, variation, and variation_name. Campaign_id and campaign_message_id are required if grouping is specified. Defaults to grouping by campaign_id, campaign_message_id, and send_channel if omitted."),
    filter_: str | None = Field(None, alias="filter", description="Optional filter expression to narrow results using AND-combined conditions. Scalar attributes (send_channel, campaign_id, campaign_message_id, campaign_message_name, variation, variation_name, text_message_format) support equals and contains-any operators. List attributes (tag_id, tag_name) support contains-any and contains-all operators. Send_channel values are limited to email, sms, push-notification, and whatsapp. Maximum 100 items per list filter."),
) -> dict[str, Any]:
    """Retrieve campaign analytics data for specified statistics across a given timeframe, with optional grouping and filtering capabilities. Results include conversion metrics and can be segmented by campaign, channel, tags, and other dimensions."""

    # Construct request model with validation
    try:
        _request = _models.QueryCampaignValuesRequest(
            header=_models.QueryCampaignValuesRequestHeader(revision=revision),
            body=_models.QueryCampaignValuesRequestBody(data=_models.QueryCampaignValuesRequestBodyData(
                    type_=type_,
                    attributes=_models.QueryCampaignValuesRequestBodyDataAttributes(statistics=statistics, timeframe=timeframe, conversion_metric_id=conversion_metric_id, group_by=group_by, filter_=filter_)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for query_campaign_values_report: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/campaign-values-reports"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("query_campaign_values_report")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("query_campaign_values_report", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="query_campaign_values_report",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Reporting
@mcp.tool()
async def query_flow_values_report(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.1). Defaults to 2026-01-15 if not specified."),
    type_: Literal["flow-values-report"] = Field(..., alias="type", description="Report type identifier. Must be set to 'flow-values-report' to query flow analytics data."),
    statistics: list[Literal["average_order_value", "bounce_rate", "bounced", "bounced_or_failed", "bounced_or_failed_rate", "click_rate", "click_to_open_rate", "clicks", "clicks_unique", "conversion_rate", "conversion_uniques", "conversion_value", "conversions", "delivered", "delivery_rate", "failed", "failed_rate", "message_segment_count_sum", "open_rate", "opens", "opens_unique", "recipients", "revenue_per_recipient", "spam_complaint_rate", "spam_complaints", "text_message_credit_usage_amount", "text_message_roi", "text_message_spend", "unsubscribe_rate", "unsubscribe_uniques", "unsubscribes"]] = Field(..., description="List of metrics to retrieve for each result row. Rate-based statistics (like open_rate, click_rate) are returned as decimal values between 0.0 and 1.0. Examples include 'opens', 'clicks', 'open_rate', 'conversion_count'. Specify the exact metrics needed for your analysis."),
    timeframe: _models.Timeframe | _models.CustomTimeframe = Field(..., description="Time period for the report, with a maximum span of 1 year. Refer to the available time frames documentation for supported formats (e.g., relative ranges like 'last_30_days' or absolute date ranges)."),
    conversion_metric_id: str = Field(..., description="Metric ID used to calculate conversion-related statistics in the report. Provide the ID of the conversion metric you want to measure (e.g., 'RESQ6t')."),
    group_by: list[Literal["flow_id", "flow_message_id", "flow_message_name", "flow_name", "send_channel", "tag_id", "tag_name", "text_message_format", "variation", "variation_name"]] | None = Field(None, description="Optional list of attributes to group results by. Allowed values include flow_id, flow_message_id, flow_message_name, flow_name, send_channel, tag_id, tag_name, text_message_format, variation, and variation_name. The attributes flow_message_id and flow_id are always required in the grouping. If omitted, results default to grouping by flow_id, flow_message_id, and send_channel."),
    filter_: str | None = Field(None, alias="filter", description="Optional filter expression to narrow results. Use operators like 'equals' and 'contains-any' for scalar attributes (flow_id, flow_name, send_channel, flow_message_id, flow_message_name, text_message_format, variation, variation_name), and 'contains-any' or 'contains-all' for list attributes (tag_id, tag_name). Combine conditions with AND only. Limited to 100 items per list filter. For send_channel, valid values are email, sms, push-notification, and whatsapp."),
) -> dict[str, Any]:
    """Retrieve flow analytics data including performance metrics like opens, clicks, conversions, and engagement rates. Results can be filtered and grouped by flow, message, channel, tags, and other dimensions to analyze campaign performance over a specified time period."""

    # Construct request model with validation
    try:
        _request = _models.QueryFlowValuesRequest(
            header=_models.QueryFlowValuesRequestHeader(revision=revision),
            body=_models.QueryFlowValuesRequestBody(data=_models.QueryFlowValuesRequestBodyData(
                    type_=type_,
                    attributes=_models.QueryFlowValuesRequestBodyDataAttributes(statistics=statistics, timeframe=timeframe, conversion_metric_id=conversion_metric_id, group_by=group_by, filter_=filter_)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for query_flow_values_report: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/flow-values-reports"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("query_flow_values_report")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("query_flow_values_report", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="query_flow_values_report",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Reporting
@mcp.tool()
async def get_flow_series_analytics(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.beta). Defaults to 2026-01-15."),
    type_: Literal["flow-series-report"] = Field(..., alias="type", description="The type of report being requested. Must be 'flow-series-report'."),
    statistics: list[Literal["average_order_value", "bounce_rate", "bounced", "bounced_or_failed", "bounced_or_failed_rate", "click_rate", "click_to_open_rate", "clicks", "clicks_unique", "conversion_rate", "conversion_uniques", "conversion_value", "conversions", "delivered", "delivery_rate", "failed", "failed_rate", "message_segment_count_sum", "open_rate", "opens", "opens_unique", "recipients", "revenue_per_recipient", "spam_complaint_rate", "spam_complaints", "text_message_credit_usage_amount", "text_message_roi", "text_message_spend", "unsubscribe_rate", "unsubscribe_uniques", "unsubscribes"]] = Field(..., description="One or more statistics to retrieve for each data point. Rate statistics (like open_rate) are returned as decimals between 0.0 and 1.0. Examples: opens, open_rate, clicks, click_rate, conversions."),
    timeframe: _models.Timeframe | _models.CustomTimeframe = Field(..., description="The date range for the report, with a maximum span of 1 year. Refer to available time frames in the Klaviyo reporting API documentation for supported formats."),
    interval: Literal["daily", "hourly", "monthly", "weekly"] = Field(..., description="The time bucket size for aggregating data. Hourly intervals are limited to 7-day timeframes, daily to 60 days, and monthly to 52 weeks."),
    conversion_metric_id: str = Field(..., description="The metric ID used to calculate conversion statistics. This determines which conversion event is tracked in the results."),
    group_by: list[Literal["flow_id", "flow_message_id", "flow_message_name", "flow_name", "send_channel", "tag_id", "tag_name", "text_message_format", "variation", "variation_name"]] | None = Field(None, description="Optional list of attributes to group results by (e.g., flow_id, flow_name, send_channel, tag_name). Flow_message_id and flow_id are always required. If omitted, data defaults to grouping by flow_id, flow_message_id, and send_channel."),
    filter_: str | None = Field(None, alias="filter", description="Optional filter expression to narrow results by scalar attributes (flow_id, flow_name, send_channel, etc.) or list attributes (tag_id, tag_name). Use equals or contains-any for scalars, contains-any or contains-all for lists. Combine multiple filters with AND only. Maximum 100 items per list filter."),
) -> dict[str, Any]:
    """Retrieve time-series analytics data for flows, including performance metrics like opens, clicks, and conversions aggregated at your specified interval over a given timeframe."""

    # Construct request model with validation
    try:
        _request = _models.QueryFlowSeriesRequest(
            header=_models.QueryFlowSeriesRequestHeader(revision=revision),
            body=_models.QueryFlowSeriesRequestBody(data=_models.QueryFlowSeriesRequestBodyData(
                    type_=type_,
                    attributes=_models.QueryFlowSeriesRequestBodyDataAttributes(statistics=statistics, timeframe=timeframe, interval=interval, conversion_metric_id=conversion_metric_id, group_by=group_by, filter_=filter_)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_flow_series_analytics: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/flow-series-reports"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_flow_series_analytics")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_flow_series_analytics", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_flow_series_analytics",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Reporting
@mcp.tool()
async def query_form_values_report(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.v1). Defaults to 2026-01-15 if not specified."),
    type_: Literal["form-values-report"] = Field(..., alias="type", description="The type of report to query. Must be 'form-values-report' to retrieve form analytics data."),
    statistics: list[Literal["closed_form", "closed_form_uniques", "qualified_form", "qualified_form_uniques", "submit_rate", "submits", "submitted_form_step", "submitted_form_step_uniques", "viewed_form", "viewed_form_step", "viewed_form_step_uniques", "viewed_form_uniques"]] = Field(..., description="One or more statistics to retrieve for the specified time period. Rate statistics are returned as decimal values between 0.0 and 1.0. Examples include 'viewed_form' and 'submit_rate'."),
    timeframe: _models.Timeframe | _models.CustomTimeframe = Field(..., description="The time period for which to retrieve data, with a maximum span of 1 year. Use the available time frame formats documented in the reporting API overview."),
    group_by: list[Literal["form_id", "form_version_id"]] | None = Field(None, description="Optional list of attributes to group results by. Supported values are 'form_id' and 'form_version_id'. Defaults to 'form_id' if not provided. When grouping by 'form_version_id', 'form_id' must also be included."),
    filter_: str | None = Field(None, alias="filter", description="Optional filter expression to narrow results by form_id or form_version_id using equals or any operators. Combine multiple filters with AND. The 'any' operator supports up to 100 values per filter."),
) -> dict[str, Any]:
    """Retrieve form analytics data including submission rates, views, and other performance metrics. Results can be filtered by form and grouped by form or form version over a specified time period (up to 1 year)."""

    # Construct request model with validation
    try:
        _request = _models.QueryFormValuesRequest(
            header=_models.QueryFormValuesRequestHeader(revision=revision),
            body=_models.QueryFormValuesRequestBody(data=_models.QueryFormValuesRequestBodyData(
                    type_=type_,
                    attributes=_models.QueryFormValuesRequestBodyDataAttributes(statistics=statistics, timeframe=timeframe, group_by=group_by, filter_=filter_)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for query_form_values_report: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/form-values-reports"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("query_form_values_report")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("query_form_values_report", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="query_form_values_report",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Reporting
@mcp.tool()
async def get_form_series_analytics(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15)."),
    type_: Literal["form-series-report"] = Field(..., alias="type", description="The type of report to query; must be 'form-series-report'."),
    statistics: list[Literal["closed_form", "closed_form_uniques", "qualified_form", "qualified_form_uniques", "submit_rate", "submits", "submitted_form_step", "submitted_form_step_uniques", "viewed_form", "viewed_form_step", "viewed_form_step_uniques", "viewed_form_uniques"]] = Field(..., description="List of statistics to retrieve (e.g., 'viewed_form', 'submit_rate'). Rate statistics are returned as decimal values between 0.0 and 1.0."),
    timeframe: _models.Timeframe | _models.CustomTimeframe = Field(..., description="The time period for data retrieval, with a maximum span of 1 year. Refer to available time frames in the reporting API documentation."),
    interval: Literal["daily", "hourly", "monthly", "weekly"] = Field(..., description="Aggregation interval for the data series. Hourly intervals are limited to 7-day timeframes, daily to 60 days, and monthly to 52 weeks."),
    group_by: list[Literal["form_id", "form_version_id"]] | None = Field(None, description="Optional list of attributes to group results by (form_id or form_version_id). Defaults to form_id if not specified. When grouping by form_version_id, form_id must also be included."),
    filter_: str | None = Field(None, alias="filter", description="Optional filter expression to narrow results by form_id or form_version_id using equals or any operators. Combine multiple filters with AND; any operator supports up to 100 values."),
) -> dict[str, Any]:
    """Retrieve time-series analytics data for forms, including metrics like view counts and submission rates aggregated over your specified timeframe and interval."""

    # Construct request model with validation
    try:
        _request = _models.QueryFormSeriesRequest(
            header=_models.QueryFormSeriesRequestHeader(revision=revision),
            body=_models.QueryFormSeriesRequestBody(data=_models.QueryFormSeriesRequestBodyData(
                    type_=type_,
                    attributes=_models.QueryFormSeriesRequestBodyDataAttributes(statistics=statistics, timeframe=timeframe, interval=interval, group_by=group_by, filter_=filter_)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_form_series_analytics: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/form-series-reports"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_form_series_analytics")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_form_series_analytics", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_form_series_analytics",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Reporting
@mcp.tool()
async def get_segment_values_report(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15). Specifies which version of the API contract to use."),
    type_: Literal["segment-values-report"] = Field(..., alias="type", description="Report type identifier. Must be set to 'segment-values-report' to query segment analytics data."),
    statistics: list[Literal["members_added", "members_removed", "net_members_changed", "total_members"]] = Field(..., description="Array of metric names to retrieve for each segment. Examples include 'total_members' and 'net_members_changed'. At least one statistic is required."),
    timeframe: _models.Timeframe | _models.CustomTimeframe = Field(..., description="Time period for the report query. Must span no more than 1 year and cannot include dates before June 1st, 2023. Use ISO 8601 format or refer to available timeframe options in the API documentation."),
    filter_: str | None = Field(None, alias="filter", description="Optional filter to narrow results to specific segments. Use 'equals' operator for a single segment ID or 'any' operator to include up to 100 segment IDs. Only one filter per attribute is allowed."),
) -> dict[str, Any]:
    """Retrieve analytics data for segment values across specified statistics and timeframe. Returns aggregated metrics like member counts and changes for one or more segments."""

    # Construct request model with validation
    try:
        _request = _models.QuerySegmentValuesRequest(
            header=_models.QuerySegmentValuesRequestHeader(revision=revision),
            body=_models.QuerySegmentValuesRequestBody(data=_models.QuerySegmentValuesRequestBodyData(
                    type_=type_,
                    attributes=_models.QuerySegmentValuesRequestBodyDataAttributes(statistics=statistics, timeframe=timeframe, filter_=filter_)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_segment_values_report: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/segment-values-reports"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_segment_values_report")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_segment_values_report", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_segment_values_report",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Reporting
@mcp.tool()
async def get_segment_series_report(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15). Controls the API contract version used for this request."),
    type_: Literal["segment-series-report"] = Field(..., alias="type", description="Report type identifier. Must be set to 'segment-series-report' to query segment analytics series data."),
    statistics: list[Literal["members_added", "members_removed", "net_members_changed", "total_members"]] = Field(..., description="Array of metric names to retrieve for each time period. Common metrics include total_members and net_members_changed. Order is preserved in results."),
    timeframe: _models.Timeframe | _models.CustomTimeframe = Field(..., description="Time range for the report. Must span no longer than 1 year and cannot include dates before June 1st, 2023. Use ISO 8601 date format or relative time frame identifiers as documented in the reporting API overview."),
    interval: Literal["daily", "hourly", "monthly", "weekly"] = Field(..., description="Aggregation granularity for the time series. Hourly intervals are limited to 7-day windows, daily to 60 days, weekly to 1 year, and monthly to 52 weeks. Choose based on your timeframe and desired detail level."),
    filter_: str | None = Field(None, alias="filter", description="Optional filter to narrow results to specific segments. Use 'equals' for a single segment ID or 'any' to include up to 100 segment IDs. Format: any(segment_id,[\"id1\",\"id2\"]) or equals(segment_id,\"id\")."),
) -> dict[str, Any]:
    """Retrieve time-series analytics data for one or more segments, aggregated at your specified interval. Supports filtering by segment ID and covers data from June 1st, 2023 onward, with a maximum lookback period of 1 year."""

    # Construct request model with validation
    try:
        _request = _models.QuerySegmentSeriesRequest(
            header=_models.QuerySegmentSeriesRequestHeader(revision=revision),
            body=_models.QuerySegmentSeriesRequestBody(data=_models.QuerySegmentSeriesRequestBodyData(
                    type_=type_,
                    attributes=_models.QuerySegmentSeriesRequestBodyDataAttributes(statistics=statistics, timeframe=timeframe, interval=interval, filter_=filter_)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_segment_series_report: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/segment-series-reports"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_segment_series_report")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_segment_series_report", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_segment_series_report",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Reviews
@mcp.tool()
async def list_reviews(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format (with optional suffix). Defaults to 2026-01-15."),
    filter_: str | None = Field(None, alias="filter", description="Filter reviews using comparison and matching operators. Supports filtering by creation date (date range), rating (any value, equals, or range), IDs, content keywords, status, review type, and verification status. Use the format specified in the Klaviyo filtering documentation."),
    page_size: int | None = Field(None, alias="pagesize", description="Number of reviews to return per page. Defaults to 20 results; must be between 1 and 100.", ge=1, le=100),
) -> dict[str, Any]:
    """Retrieve all reviews with optional filtering and pagination. Supports filtering by creation date, rating, ID, item ID, content, status, review type, and verification status."""

    # Construct request model with validation
    try:
        _request = _models.GetReviewsRequest(
            query=_models.GetReviewsRequestQuery(filter_=filter_, page_size=page_size),
            header=_models.GetReviewsRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_reviews: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/reviews"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_reviews")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_reviews", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_reviews",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Reviews
@mcp.tool()
async def get_review(
    id_: str = Field(..., alias="id", description="The unique identifier of the review to retrieve (e.g., '2134228')"),
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15). Specifies which API version to use for this request."),
) -> dict[str, Any]:
    """Retrieve a specific review by its ID. Returns the full review details including content, metadata, and associated information."""

    # Construct request model with validation
    try:
        _request = _models.GetReviewRequest(
            path=_models.GetReviewRequestPath(id_=id_),
            header=_models.GetReviewRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_review: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/reviews/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/reviews/{id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_review")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_review", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_review",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Reviews
@mcp.tool()
async def update_review(
    id_: str = Field(..., alias="id", description="The unique identifier of the review to update. Must match the review ID provided in the request body."),
    revision: str = Field(..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15). Specifies which API version to use for this operation."),
    data_id: str = Field(..., alias="dataId", description="The unique identifier of the review being updated. Must match the path ID parameter."),
    type_: Literal["review"] = Field(..., alias="type", description="The resource type identifier. Must be set to 'review' to indicate this operation targets a review resource."),
    status: _models.ReviewStatusRejected | _models.ReviewStatusFeatured | _models.ReviewStatusPublished | _models.ReviewStatusUnpublished | _models.ReviewStatusPending | None = Field(None, description="The new status to assign to the review. Valid status values depend on the review workflow configuration."),
) -> dict[str, Any]:
    """Update an existing review by its ID. Requires the review:write scope and respects rate limits of 10 requests per second (burst) and 150 requests per minute (steady state)."""

    # Construct request model with validation
    try:
        _request = _models.UpdateReviewRequest(
            path=_models.UpdateReviewRequestPath(id_=id_),
            header=_models.UpdateReviewRequestHeader(revision=revision),
            body=_models.UpdateReviewRequestBody(data=_models.UpdateReviewRequestBodyData(
                    id_=data_id, type_=type_,
                    attributes=_models.UpdateReviewRequestBodyDataAttributes(status=status) if any(v is not None for v in [status]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_review: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/reviews/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/reviews/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_review")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_review", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_review",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Segments
@mcp.tool()
async def list_segments(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format (with optional suffix). Defaults to 2026-01-15 if not specified."),
    fields_segment: list[Literal["created", "definition", "definition.condition_groups", "is_active", "is_processing", "is_starred", "name", "updated"]] | None = Field(None, alias="fieldssegment", description="Specify which segment fields to include in the response using sparse fieldsets for optimized data retrieval."),
    filter_: str | None = Field(None, alias="filter", description="Filter segments by name, ID, creation date, update date, active status, or starred status. Supports exact matching and partial matching operators depending on the field."),
) -> dict[str, Any]:
    """Retrieve all segments in an account with optional filtering and field selection. Returns up to 10 results per page."""

    # Construct request model with validation
    try:
        _request = _models.GetSegmentsRequest(
            query=_models.GetSegmentsRequestQuery(fields_segment=fields_segment, filter_=filter_),
            header=_models.GetSegmentsRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_segments: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/segments"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_query = _serialize_query(_http_query, {
        "fields[segment]": ("form", False),
    })
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_segments")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_segments", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_segments",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Segments
@mcp.tool()
async def create_segment(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.v1). Defaults to 2026-01-15 if not specified."),
    type_: Literal["segment"] = Field(..., alias="type", description="The resource type, which must be 'segment' for this operation."),
    name: str = Field(..., description="A descriptive name for the segment that identifies its purpose or target audience."),
    condition_groups: list[_models.ConditionGroup] = Field(..., description="An array of condition groups that define the segment's matching criteria. Each group contains conditions that users must satisfy to be included in the segment."),
    is_starred: bool | None = Field(None, description="Optional flag to mark the segment as starred for quick access. Defaults to false if not specified."),
) -> dict[str, Any]:
    """Create a new audience segment defined by condition groups. Segments are used to target specific groups of users based on matching criteria."""

    # Construct request model with validation
    try:
        _request = _models.CreateSegmentRequest(
            header=_models.CreateSegmentRequestHeader(revision=revision),
            body=_models.CreateSegmentRequestBody(data=_models.CreateSegmentRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateSegmentRequestBodyDataAttributes(
                        name=name, is_starred=is_starred,
                        definition=_models.CreateSegmentRequestBodyDataAttributesDefinition(condition_groups=condition_groups)
                    )
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_segment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/segments"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_segment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_segment", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_segment",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Segments
@mcp.tool()
async def get_segment(
    id_: str = Field(..., alias="id", description="The unique identifier of the segment to retrieve."),
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format (e.g., 2026-01-15), optionally with a suffix. Defaults to 2026-01-15 if not specified."),
    fields_segment: list[Literal["created", "definition", "definition.condition_groups", "is_active", "is_processing", "is_starred", "name", "profile_count", "updated"]] | None = Field(None, alias="fieldssegment", description="Optional list of segment fields to include in the response. Use sparse fieldsets to optimize payload size and performance. Refer to the API overview documentation for available fields."),
) -> dict[str, Any]:
    """Retrieve a segment by its ID. Optionally include additional fields like profile count, which has stricter rate limits."""

    # Construct request model with validation
    try:
        _request = _models.GetSegmentRequest(
            path=_models.GetSegmentRequestPath(id_=id_),
            query=_models.GetSegmentRequestQuery(fields_segment=fields_segment),
            header=_models.GetSegmentRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_segment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/segments/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/segments/{id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_query = _serialize_query(_http_query, {
        "fields[segment]": ("form", False),
    })
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_segment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_segment", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_segment",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Segments
@mcp.tool()
async def update_segment(
    id_: str = Field(..., alias="id", description="The unique identifier of the segment to update."),
    revision: str = Field(..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15)."),
    data_id: str = Field(..., alias="dataId", description="The segment's unique identifier, must match the segment being updated."),
    type_: Literal["segment"] = Field(..., alias="type", description="The resource type, must be set to 'segment'."),
    condition_groups: list[_models.ConditionGroup] = Field(..., description="Array of condition groups that define the segment's membership criteria. Order may be significant for evaluation logic."),
    name: str | None = Field(None, description="Human-readable name for the segment."),
    is_starred: bool | None = Field(None, description="Whether to star/favorite this segment for quick access."),
    is_active: bool | None = Field(None, description="Activation status of the segment. Set to false to deactivate (this must be the only attribute in the request); set to true to reactivate. Deactivating impacts campaigns, flows, ad syncs, forms, helpdesk routing, and other dependent features."),
) -> dict[str, Any]:
    """Update an existing segment's configuration, including name, activation status, and condition groups. Note: deactivation must be performed as a standalone operation and cannot be combined with other updates."""

    # Construct request model with validation
    try:
        _request = _models.UpdateSegmentRequest(
            path=_models.UpdateSegmentRequestPath(id_=id_),
            header=_models.UpdateSegmentRequestHeader(revision=revision),
            body=_models.UpdateSegmentRequestBody(data=_models.UpdateSegmentRequestBodyData(
                    id_=data_id, type_=type_,
                    attributes=_models.UpdateSegmentRequestBodyDataAttributes(
                        name=name, is_starred=is_starred, is_active=is_active,
                        definition=_models.UpdateSegmentRequestBodyDataAttributesDefinition(condition_groups=condition_groups)
                    )
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_segment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/segments/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/segments/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_segment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_segment", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_segment",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Segments
@mcp.tool()
async def delete_segment(
    id_: str = Field(..., alias="id", description="The unique identifier of the segment to delete."),
    revision: str = Field(..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.v2). Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Permanently delete a segment by its ID. Requires the segment's current revision to ensure safe deletion and prevent conflicts from concurrent modifications."""

    # Construct request model with validation
    try:
        _request = _models.DeleteSegmentRequest(
            path=_models.DeleteSegmentRequestPath(id_=id_),
            header=_models.DeleteSegmentRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_segment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/segments/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/segments/{id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_segment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_segment", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_segment",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Segments
@mcp.tool()
async def list_tags_for_segment(
    id_: str = Field(..., alias="id", description="The unique identifier of the segment for which to retrieve associated tags."),
    revision: str = Field(..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15). Specifies which version of the API contract to use."),
) -> dict[str, Any]:
    """Retrieve all tags associated with a specific segment. Returns a collection of tags linked to the given segment ID."""

    # Construct request model with validation
    try:
        _request = _models.GetTagsForSegmentRequest(
            path=_models.GetTagsForSegmentRequestPath(id_=id_),
            header=_models.GetTagsForSegmentRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_tags_for_segment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/segments/{id}/tags", _request.path.model_dump(by_alias=True)) if _request.path else "/api/segments/{id}/tags"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_tags_for_segment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_tags_for_segment", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_tags_for_segment",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Segments
@mcp.tool()
async def list_tag_ids_for_segment(
    id_: str = Field(..., alias="id", description="The unique identifier of the segment for which to retrieve associated tag IDs."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve all tag IDs associated with a specific segment. Returns a collection of tag identifiers linked to the given segment."""

    # Construct request model with validation
    try:
        _request = _models.GetTagIdsForSegmentRequest(
            path=_models.GetTagIdsForSegmentRequestPath(id_=id_),
            header=_models.GetTagIdsForSegmentRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_tag_ids_for_segment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/segments/{id}/relationships/tags", _request.path.model_dump(by_alias=True)) if _request.path else "/api/segments/{id}/relationships/tags"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_tag_ids_for_segment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_tag_ids_for_segment", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_tag_ids_for_segment",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Segments
@mcp.tool()
async def list_profiles_for_segment(
    id_: str = Field(..., alias="id", description="The unique segment identifier generated by Klaviyo (e.g., 'Y6nRLr')."),
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format (default: 2026-01-15)."),
    filter_: str | None = Field(None, alias="filter", description="Filter profiles by profile_id, email, phone_number, push_token, _kx, or joined_group_at. Use operators like 'equals', 'any', 'greater-than', 'less-than', etc. For details on filter syntax, see the API documentation."),
    page_size: int | None = Field(None, alias="pagesize", description="Number of profiles to return per page. Must be between 1 and 100 (default: 20).", ge=1, le=100),
) -> dict[str, Any]:
    """Retrieve all profiles within a specific segment. Optionally filter and sort results to find profiles matching specific criteria like email, phone number, or join date."""

    # Construct request model with validation
    try:
        _request = _models.GetProfilesForSegmentRequest(
            path=_models.GetProfilesForSegmentRequestPath(id_=id_),
            query=_models.GetProfilesForSegmentRequestQuery(filter_=filter_, page_size=page_size),
            header=_models.GetProfilesForSegmentRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_profiles_for_segment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/segments/{id}/profiles", _request.path.model_dump(by_alias=True)) if _request.path else "/api/segments/{id}/profiles"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_profiles_for_segment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_profiles_for_segment", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_profiles_for_segment",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Segments
@mcp.tool()
async def list_profile_ids_for_segment(
    id_: str = Field(..., alias="id", description="The unique identifier of the segment. This is a Klaviyo-generated ID (e.g., 'Y6nRLr')."),
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format (e.g., '2026-01-15'). Defaults to the latest stable version."),
    filter_: str | None = Field(None, alias="filter", description="Filter results by profile attributes or membership metadata. Supports filtering by profile_id, email, phone_number, push_token, _kx identifier, or joined_group_at timestamp. Use operators like 'equals' for exact matches or 'any' for multiple values, and comparison operators (greater-than, less-than, etc.) for date ranges."),
    page_size: int | None = Field(None, alias="pagesize", description="Number of results per page. Must be between 1 and 100, with a default of 20.", ge=1, le=100),
) -> dict[str, Any]:
    """Retrieve all profile IDs that are members of a specific segment. Use filtering and pagination to narrow results and manage large datasets."""

    # Construct request model with validation
    try:
        _request = _models.GetProfileIdsForSegmentRequest(
            path=_models.GetProfileIdsForSegmentRequestPath(id_=id_),
            query=_models.GetProfileIdsForSegmentRequestQuery(filter_=filter_, page_size=page_size),
            header=_models.GetProfileIdsForSegmentRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_profile_ids_for_segment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/segments/{id}/relationships/profiles", _request.path.model_dump(by_alias=True)) if _request.path else "/api/segments/{id}/relationships/profiles"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_profile_ids_for_segment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_profile_ids_for_segment", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_profile_ids_for_segment",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Segments
@mcp.tool()
async def list_flows_triggered_by_segment(
    id_: str = Field(..., alias="id", description="The unique identifier of the segment. This is a Klaviyo-generated primary key (e.g., 'Y6nRLr')."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve all automation flows that are triggered by a specific segment. This operation identifies which flows use the given segment as their entry point trigger."""

    # Construct request model with validation
    try:
        _request = _models.GetFlowsTriggeredBySegmentRequest(
            path=_models.GetFlowsTriggeredBySegmentRequestPath(id_=id_),
            header=_models.GetFlowsTriggeredBySegmentRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_flows_triggered_by_segment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/segments/{id}/flow-triggers", _request.path.model_dump(by_alias=True)) if _request.path else "/api/segments/{id}/flow-triggers"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_flows_triggered_by_segment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_flows_triggered_by_segment", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_flows_triggered_by_segment",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Segments
@mcp.tool()
async def list_flow_ids_triggered_by_segment(
    id_: str = Field(..., alias="id", description="The unique identifier of the segment, generated by Klaviyo (e.g., 'Y6nRLr'). This segment will be checked to find all flows using it as a trigger."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format (or with an optional suffix). Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve the IDs of all flows that use the specified segment as their trigger condition. This helps identify which automation workflows are activated by a particular audience segment."""

    # Construct request model with validation
    try:
        _request = _models.GetIdsForFlowsTriggeredBySegmentRequest(
            path=_models.GetIdsForFlowsTriggeredBySegmentRequestPath(id_=id_),
            header=_models.GetIdsForFlowsTriggeredBySegmentRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_flow_ids_triggered_by_segment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/segments/{id}/relationships/flow-triggers", _request.path.model_dump(by_alias=True)) if _request.path else "/api/segments/{id}/relationships/flow-triggers"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_flow_ids_triggered_by_segment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_flow_ids_triggered_by_segment", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_flow_ids_triggered_by_segment",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tags
@mcp.tool()
async def list_tags(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format (or with optional suffix). Defaults to 2026-01-15 if not specified."),
    filter_: str | None = Field(None, alias="filter", description="Filter tags by name using comparison operators (equals, contains, starts-with, ends-with). For example, filter by exact name match or partial name patterns."),
) -> dict[str, Any]:
    """Retrieve all tags in an account with optional filtering and sorting. Results are paginated with a maximum of 50 tags per request."""

    # Construct request model with validation
    try:
        _request = _models.GetTagsRequest(
            query=_models.GetTagsRequestQuery(filter_=filter_),
            header=_models.GetTagsRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_tags: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/tags"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_tags")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_tags", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_tags",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tags
@mcp.tool()
async def create_tag(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format (or with optional suffix). Defaults to 2026-01-15 if not specified."),
    type_: Literal["tag"] = Field(..., alias="type", description="The resource type identifier. Must be set to 'tag'."),
    tag_group_data_type: Literal["tag-group"] = Field(..., alias="tag_groupDataType", description="The resource type identifier for the tag group relationship. Must be set to 'tag-group'."),
    name: str = Field(..., description="The name of the tag being created. This is a user-facing label for organizing and categorizing items."),
    id_: str = Field(..., alias="id", description="The ID of the tag group to associate this tag with. If omitted, the tag will be assigned to your account's default tag group. Provide a UUID-formatted identifier."),
) -> dict[str, Any]:
    """Create a new tag within your account. Tags are organized into tag groups; if no tag group is specified, the tag will be added to your account's default tag group. Note: accounts are limited to 500 unique tags."""

    # Construct request model with validation
    try:
        _request = _models.CreateTagRequest(
            header=_models.CreateTagRequestHeader(revision=revision),
            body=_models.CreateTagRequestBody(data=_models.CreateTagRequestBodyData(
                    type_=type_,
                    relationships=_models.CreateTagRequestBodyDataRelationships(
                        tag_group=_models.CreateTagRequestBodyDataRelationshipsTagGroup(
                            data=_models.CreateTagRequestBodyDataRelationshipsTagGroupData(type_=tag_group_data_type, id_=id_)
                        )
                    ),
                    attributes=_models.CreateTagRequestBodyDataAttributes(name=name)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_tag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/tags"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_tag")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_tag", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_tag",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Tags
@mcp.tool()
async def get_tag(
    id_: str = Field(..., alias="id", description="The unique identifier for the tag to retrieve, formatted as a UUID (e.g., abcd1234-ef56-gh78-ij90-abcdef123456)."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, optionally followed by a suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve a specific tag by its ID. Requires the tags:read scope and is subject to rate limits of 3 requests per second (burst) and 60 requests per minute (steady state)."""

    # Construct request model with validation
    try:
        _request = _models.GetTagRequest(
            path=_models.GetTagRequestPath(id_=id_),
            header=_models.GetTagRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_tag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/tags/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/tags/{id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_tag")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_tag", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_tag",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tags
@mcp.tool()
async def update_tag(
    id_: str = Field(..., alias="id", description="The unique identifier of the tag to update, formatted as a UUID (e.g., abcd1234-ef56-gh78-ij90-abcdef123456)."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
    data_id: str = Field(..., alias="dataId", description="The unique identifier of the tag being updated, formatted as a UUID. Must match the tag ID in the path parameter."),
    type_: Literal["tag"] = Field(..., alias="type", description="The resource type identifier. Must be set to 'tag' for this operation."),
    name: str = Field(..., description="The new name for the tag. Can be any string value (e.g., 'My Tag')."),
) -> dict[str, Any]:
    """Update a tag's name by its ID. Only the tag name can be modified; tags cannot be moved between tag groups."""

    # Construct request model with validation
    try:
        _request = _models.UpdateTagRequest(
            path=_models.UpdateTagRequestPath(id_=id_),
            header=_models.UpdateTagRequestHeader(revision=revision),
            body=_models.UpdateTagRequestBody(data=_models.UpdateTagRequestBodyData(
                    id_=data_id, type_=type_,
                    attributes=_models.UpdateTagRequestBodyDataAttributes(name=name)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_tag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/tags/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/tags/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_tag")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_tag", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_tag",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Tags
@mcp.tool()
async def delete_tag(
    id_: str = Field(..., alias="id", description="The unique identifier of the tag to delete, formatted as a UUID (e.g., abcd1234-ef56-gh78-ij90-abcdef123456)."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, optionally followed by a suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Permanently delete a tag by its ID. This operation removes the tag and all its associations with other resources."""

    # Construct request model with validation
    try:
        _request = _models.DeleteTagRequest(
            path=_models.DeleteTagRequestPath(id_=id_),
            header=_models.DeleteTagRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_tag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/tags/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/tags/{id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_tag")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_tag", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_tag",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tags
@mcp.tool()
async def list_tag_groups(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format (with optional suffix). Defaults to 2026-01-15 if not specified."),
    filter_: str | None = Field(None, alias="filter", description="Filter tag groups by name (using contains, ends-with, equals, or starts-with matching), exclusivity status, or default status. Provide filter expressions in the format: operator(field,'value')."),
) -> dict[str, Any]:
    """Retrieve all tag groups in an account with optional filtering and sorting. Every account includes one default tag group, and results are paginated with a maximum of 25 tag groups per request."""

    # Construct request model with validation
    try:
        _request = _models.GetTagGroupsRequest(
            query=_models.GetTagGroupsRequestQuery(filter_=filter_),
            header=_models.GetTagGroupsRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_tag_groups: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/tag-groups"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_tag_groups")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_tag_groups", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_tag_groups",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tags
@mcp.tool()
async def create_tag_group(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix. Defaults to 2026-01-15 if not specified."),
    type_: Literal["tag-group"] = Field(..., alias="type", description="The resource type identifier. Must be set to 'tag-group' for this operation."),
    name: str = Field(..., description="A descriptive name for the tag group. This is the human-readable identifier used to reference the tag group."),
    exclusive: bool | None = Field(None, description="Controls whether resources can be linked to multiple tags within this group. When true, resources can only be linked to one tag; when false (default), resources can be linked to multiple tags from this group."),
) -> dict[str, Any]:
    """Create a new tag group to organize and categorize tags within your account. Tag groups can be configured as exclusive (allowing only one tag per resource) or non-exclusive (allowing multiple tags per resource). Accounts are limited to 50 unique tag groups."""

    # Construct request model with validation
    try:
        _request = _models.CreateTagGroupRequest(
            header=_models.CreateTagGroupRequestHeader(revision=revision),
            body=_models.CreateTagGroupRequestBody(data=_models.CreateTagGroupRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateTagGroupRequestBodyDataAttributes(name=name, exclusive=exclusive)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_tag_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/tag-groups"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_tag_group")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_tag_group", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_tag_group",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Tags
@mcp.tool()
async def get_tag_group(
    id_: str = Field(..., alias="id", description="The unique identifier of the tag group to retrieve, formatted as a UUID (e.g., zyxw9876-vu54-ts32-rq10-zyxwvu654321)."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve a specific tag group by its ID. Requires read access to tags and supports API versioning through the revision parameter."""

    # Construct request model with validation
    try:
        _request = _models.GetTagGroupRequest(
            path=_models.GetTagGroupRequestPath(id_=id_),
            header=_models.GetTagGroupRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_tag_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/tag-groups/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/tag-groups/{id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_tag_group")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_tag_group", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_tag_group",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tags
@mcp.tool()
async def update_tag_group(
    id_: str = Field(..., alias="id", description="The unique identifier of the tag group to update, formatted as a UUID."),
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15)."),
    data_id: str = Field(..., alias="dataId", description="The tag group ID being updated; must match the ID in the path parameter."),
    type_: Literal["tag-group"] = Field(..., alias="type", description="Resource type identifier; must be set to 'tag-group'."),
    name: str = Field(..., description="The new name for the tag group. This is the only updatable field."),
    return_fields: list[str] | None = Field(None, description="Optional list of fields to include in the response. If not specified, default fields are returned."),
) -> dict[str, Any]:
    """Update a tag group's name by ID. Only the name field can be modified; exclusive and default properties are immutable after creation."""

    # Construct request model with validation
    try:
        _request = _models.UpdateTagGroupRequest(
            path=_models.UpdateTagGroupRequestPath(id_=id_),
            header=_models.UpdateTagGroupRequestHeader(revision=revision),
            body=_models.UpdateTagGroupRequestBody(data=_models.UpdateTagGroupRequestBodyData(
                    id_=data_id, type_=type_,
                    attributes=_models.UpdateTagGroupRequestBodyDataAttributes(name=name, return_fields=return_fields)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_tag_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/tag-groups/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/tag-groups/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_tag_group")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_tag_group", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_tag_group",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Tags
@mcp.tool()
async def delete_tag_group(
    id_: str = Field(..., alias="id", description="The unique identifier of the tag group to delete, formatted as a UUID (e.g., zyxw9876-vu54-ts32-rq10-zyxwvu654321)."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Permanently delete a tag group and all associated tags and their relationships with other resources. Note that the default tag group cannot be deleted."""

    # Construct request model with validation
    try:
        _request = _models.DeleteTagGroupRequest(
            path=_models.DeleteTagGroupRequestPath(id_=id_),
            header=_models.DeleteTagGroupRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_tag_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/tag-groups/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/tag-groups/{id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_tag_group")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_tag_group", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_tag_group",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tags
@mcp.tool()
async def list_flows_for_tag(
    id_: str = Field(..., alias="id", description="The unique identifier of the tag. Must be a valid UUID in the format xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve all flow IDs associated with a specific tag. Returns a collection of flow identifiers linked to the given tag."""

    # Construct request model with validation
    try:
        _request = _models.GetFlowIdsForTagRequest(
            path=_models.GetFlowIdsForTagRequestPath(id_=id_),
            header=_models.GetFlowIdsForTagRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_flows_for_tag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/tags/{id}/relationships/flows", _request.path.model_dump(by_alias=True)) if _request.path else "/api/tags/{id}/relationships/flows"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_flows_for_tag")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_flows_for_tag", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_flows_for_tag",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tags
@mcp.tool()
async def add_flows_to_tag(
    id_: str = Field(..., alias="id", description="The unique identifier of the tag to associate with flows, formatted as a UUID (e.g., abcd1234-ef56-gh78-ij90-abcdef123456)."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15 if not specified)."),
    data: list[_models.TagFlowsBodyDataItem] = Field(..., description="Array of flow IDs to associate with the tag. Each ID should be a valid flow identifier; order is not significant."),
) -> dict[str, Any]:
    """Associate one or more flows with a tag. Each flow can be tagged with up to 100 tags maximum."""

    # Construct request model with validation
    try:
        _request = _models.TagFlowsRequest(
            path=_models.TagFlowsRequestPath(id_=id_),
            header=_models.TagFlowsRequestHeader(revision=revision),
            body=_models.TagFlowsRequestBody(data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_flows_to_tag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/tags/{id}/relationships/flows", _request.path.model_dump(by_alias=True)) if _request.path else "/api/tags/{id}/relationships/flows"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_flows_to_tag")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_flows_to_tag", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_flows_to_tag",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Tags
@mcp.tool()
async def remove_tag_from_flows(
    id_: str = Field(..., alias="id", description="The unique identifier of the tag to remove from flows, formatted as a UUID (e.g., abcd1234-ef56-gh78-ij90-abcdef123456)."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
    data: list[_models.RemoveTagFromFlowsBodyDataItem] = Field(..., description="An array of flow IDs to remove the tag association from. Each item should be a flow ID string. Order is not significant."),
) -> dict[str, Any]:
    """Remove a tag's association with one or more flows by specifying the flow IDs in the request body. This operation breaks the relationship between the tag and the specified flows."""

    # Construct request model with validation
    try:
        _request = _models.RemoveTagFromFlowsRequest(
            path=_models.RemoveTagFromFlowsRequestPath(id_=id_),
            header=_models.RemoveTagFromFlowsRequestHeader(revision=revision),
            body=_models.RemoveTagFromFlowsRequestBody(data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_tag_from_flows: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/tags/{id}/relationships/flows", _request.path.model_dump(by_alias=True)) if _request.path else "/api/tags/{id}/relationships/flows"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_tag_from_flows")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_tag_from_flows", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_tag_from_flows",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Tags
@mcp.tool()
async def list_campaign_ids_for_tag(
    id_: str = Field(..., alias="id", description="The unique identifier of the tag. Must be a valid UUID in the format xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve all campaign IDs associated with a specific tag. Use this to discover which campaigns are linked to a given tag."""

    # Construct request model with validation
    try:
        _request = _models.GetCampaignIdsForTagRequest(
            path=_models.GetCampaignIdsForTagRequestPath(id_=id_),
            header=_models.GetCampaignIdsForTagRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_campaign_ids_for_tag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/tags/{id}/relationships/campaigns", _request.path.model_dump(by_alias=True)) if _request.path else "/api/tags/{id}/relationships/campaigns"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_campaign_ids_for_tag")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_campaign_ids_for_tag", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_campaign_ids_for_tag",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tags
@mcp.tool()
async def add_campaigns_to_tag(
    id_: str = Field(..., alias="id", description="The unique identifier of the tag to associate with campaigns. Use UUID format (e.g., abcd1234-ef56-gh78-ij90-abcdef123456)."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
    data: list[_models.TagCampaignsBodyDataItem] = Field(..., description="Array of campaign IDs to associate with the tag. Each ID should be a valid campaign identifier. Order is not significant."),
) -> dict[str, Any]:
    """Associate one or more campaigns with a tag. Each campaign can be tagged with up to 100 tags maximum."""

    # Construct request model with validation
    try:
        _request = _models.TagCampaignsRequest(
            path=_models.TagCampaignsRequestPath(id_=id_),
            header=_models.TagCampaignsRequestHeader(revision=revision),
            body=_models.TagCampaignsRequestBody(data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_campaigns_to_tag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/tags/{id}/relationships/campaigns", _request.path.model_dump(by_alias=True)) if _request.path else "/api/tags/{id}/relationships/campaigns"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_campaigns_to_tag")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_campaigns_to_tag", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_campaigns_to_tag",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Tags
@mcp.tool()
async def remove_tag_from_campaigns(
    id_: str = Field(..., alias="id", description="The unique identifier of the tag to disassociate from campaigns, formatted as a UUID (e.g., abcd1234-ef56-gh78-ij90-abcdef123456)."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
    data: list[_models.RemoveTagFromCampaignsBodyDataItem] = Field(..., description="An array of campaign IDs to remove from the tag's associations. Each item should be a campaign identifier."),
) -> dict[str, Any]:
    """Remove a tag's association with one or more campaigns by specifying the campaign IDs in the request body."""

    # Construct request model with validation
    try:
        _request = _models.RemoveTagFromCampaignsRequest(
            path=_models.RemoveTagFromCampaignsRequestPath(id_=id_),
            header=_models.RemoveTagFromCampaignsRequestHeader(revision=revision),
            body=_models.RemoveTagFromCampaignsRequestBody(data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_tag_from_campaigns: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/tags/{id}/relationships/campaigns", _request.path.model_dump(by_alias=True)) if _request.path else "/api/tags/{id}/relationships/campaigns"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_tag_from_campaigns")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_tag_from_campaigns", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_tag_from_campaigns",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Tags
@mcp.tool()
async def list_lists_for_tag(
    id_: str = Field(..., alias="id", description="The unique identifier of the tag. Must be a valid UUID in the format xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve all list IDs associated with a specific tag. Returns a collection of list identifiers linked to the given tag."""

    # Construct request model with validation
    try:
        _request = _models.GetListIdsForTagRequest(
            path=_models.GetListIdsForTagRequestPath(id_=id_),
            header=_models.GetListIdsForTagRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_lists_for_tag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/tags/{id}/relationships/lists", _request.path.model_dump(by_alias=True)) if _request.path else "/api/tags/{id}/relationships/lists"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_lists_for_tag")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_lists_for_tag", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_lists_for_tag",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tags
@mcp.tool()
async def associate_lists_with_tag(
    id_: str = Field(..., alias="id", description="The unique identifier of the tag to associate with lists, formatted as a UUID (e.g., abcd1234-ef56-gh78-ij90-abcdef123456)."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
    data: list[_models.TagListsBodyDataItem] = Field(..., description="An array of list IDs to associate with the tag. Each ID should be a valid list identifier."),
) -> dict[str, Any]:
    """Associate one or more lists with a tag. Each list can be associated with a maximum of 100 tags."""

    # Construct request model with validation
    try:
        _request = _models.TagListsRequest(
            path=_models.TagListsRequestPath(id_=id_),
            header=_models.TagListsRequestHeader(revision=revision),
            body=_models.TagListsRequestBody(data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for associate_lists_with_tag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/tags/{id}/relationships/lists", _request.path.model_dump(by_alias=True)) if _request.path else "/api/tags/{id}/relationships/lists"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("associate_lists_with_tag")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("associate_lists_with_tag", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="associate_lists_with_tag",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Tags
@mcp.tool()
async def remove_tag_from_lists(
    id_: str = Field(..., alias="id", description="The unique identifier of the tag to remove from lists, formatted as a UUID (e.g., abcd1234-ef56-gh78-ij90-abcdef123456)."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15 if not specified)."),
    data: list[_models.RemoveTagFromListsBodyDataItem] = Field(..., description="An array of list IDs to disassociate from the tag. Each item should be a list identifier; order is not significant."),
) -> dict[str, Any]:
    """Remove a tag's association with one or more lists by specifying the list IDs in the request body."""

    # Construct request model with validation
    try:
        _request = _models.RemoveTagFromListsRequest(
            path=_models.RemoveTagFromListsRequestPath(id_=id_),
            header=_models.RemoveTagFromListsRequestHeader(revision=revision),
            body=_models.RemoveTagFromListsRequestBody(data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_tag_from_lists: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/tags/{id}/relationships/lists", _request.path.model_dump(by_alias=True)) if _request.path else "/api/tags/{id}/relationships/lists"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_tag_from_lists")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_tag_from_lists", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_tag_from_lists",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Tags
@mcp.tool()
async def list_segment_ids_for_tag(
    id_: str = Field(..., alias="id", description="The unique identifier of the tag. Must be a valid UUID in the format xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve all segment IDs associated with a specific tag. Returns a collection of segment identifiers linked to the given tag."""

    # Construct request model with validation
    try:
        _request = _models.GetSegmentIdsForTagRequest(
            path=_models.GetSegmentIdsForTagRequestPath(id_=id_),
            header=_models.GetSegmentIdsForTagRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_segment_ids_for_tag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/tags/{id}/relationships/segments", _request.path.model_dump(by_alias=True)) if _request.path else "/api/tags/{id}/relationships/segments"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_segment_ids_for_tag")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_segment_ids_for_tag", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_segment_ids_for_tag",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tags
@mcp.tool()
async def add_segments_to_tag(
    id_: str = Field(..., alias="id", description="The unique identifier of the tag to associate with segments. Use UUID format (e.g., abcd1234-ef56-gh78-ij90-abcdef123456)."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
    data: list[_models.TagSegmentsBodyDataItem] = Field(..., description="Array of segment IDs to associate with the tag. Each ID should be a valid segment identifier. Order is not significant."),
) -> dict[str, Any]:
    """Associate one or more segments with a tag. Each segment can be tagged with a maximum of 100 tags total."""

    # Construct request model with validation
    try:
        _request = _models.TagSegmentsRequest(
            path=_models.TagSegmentsRequestPath(id_=id_),
            header=_models.TagSegmentsRequestHeader(revision=revision),
            body=_models.TagSegmentsRequestBody(data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_segments_to_tag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/tags/{id}/relationships/segments", _request.path.model_dump(by_alias=True)) if _request.path else "/api/tags/{id}/relationships/segments"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_segments_to_tag")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_segments_to_tag", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_segments_to_tag",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Tags
@mcp.tool()
async def remove_tag_from_segments(
    id_: str = Field(..., alias="id", description="The unique identifier of the tag to disassociate from segments, formatted as a UUID (e.g., abcd1234-ef56-gh78-ij90-abcdef123456)."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
    data: list[_models.RemoveTagFromSegmentsBodyDataItem] = Field(..., description="An array of segment IDs to remove from the tag's associations. Each item should be a segment identifier."),
) -> dict[str, Any]:
    """Remove a tag's association with one or more segments by specifying the segment IDs in the request body."""

    # Construct request model with validation
    try:
        _request = _models.RemoveTagFromSegmentsRequest(
            path=_models.RemoveTagFromSegmentsRequestPath(id_=id_),
            header=_models.RemoveTagFromSegmentsRequestHeader(revision=revision),
            body=_models.RemoveTagFromSegmentsRequestBody(data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_tag_from_segments: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/tags/{id}/relationships/segments", _request.path.model_dump(by_alias=True)) if _request.path else "/api/tags/{id}/relationships/segments"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_tag_from_segments")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_tag_from_segments", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_tag_from_segments",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Tags
@mcp.tool()
async def get_tag_group_for_tag(
    id_: str = Field(..., alias="id", description="The unique identifier of the tag in UUID format (e.g., abcd1234-ef56-gh78-ij90-abcdef123456)."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, optionally followed by a suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieves the tag group resource associated with a specific tag. Use this to find the parent group classification for a given tag ID."""

    # Construct request model with validation
    try:
        _request = _models.GetTagGroupForTagRequest(
            path=_models.GetTagGroupForTagRequestPath(id_=id_),
            header=_models.GetTagGroupForTagRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_tag_group_for_tag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/tags/{id}/tag-group", _request.path.model_dump(by_alias=True)) if _request.path else "/api/tags/{id}/tag-group"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_tag_group_for_tag")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_tag_group_for_tag", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_tag_group_for_tag",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tags
@mcp.tool()
async def get_tag_group_id_for_tag(
    id_: str = Field(..., alias="id", description="The unique identifier of the tag in UUID format (e.g., abcd1234-ef56-gh78-ij90-abcdef123456)."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, optionally followed by a suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieves the ID of the tag group associated with a specific tag. Use this to determine which tag group a tag belongs to."""

    # Construct request model with validation
    try:
        _request = _models.GetTagGroupIdForTagRequest(
            path=_models.GetTagGroupIdForTagRequestPath(id_=id_),
            header=_models.GetTagGroupIdForTagRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_tag_group_id_for_tag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/tags/{id}/relationships/tag-group", _request.path.model_dump(by_alias=True)) if _request.path else "/api/tags/{id}/relationships/tag-group"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_tag_group_id_for_tag")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_tag_group_id_for_tag", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_tag_group_id_for_tag",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tags
@mcp.tool()
async def list_tags_for_tag_group(
    id_: str = Field(..., alias="id", description="The unique identifier of the tag group. Use the tag group ID in UUID format (e.g., zyxw9876-vu54-ts32-rq10-zyxwvu654321)."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve all tags associated with a specific tag group. Returns a collection of tags organized under the given tag group ID."""

    # Construct request model with validation
    try:
        _request = _models.GetTagsForTagGroupRequest(
            path=_models.GetTagsForTagGroupRequestPath(id_=id_),
            header=_models.GetTagsForTagGroupRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_tags_for_tag_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/tag-groups/{id}/tags", _request.path.model_dump(by_alias=True)) if _request.path else "/api/tag-groups/{id}/tags"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_tags_for_tag_group")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_tags_for_tag_group", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_tags_for_tag_group",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tags
@mcp.tool()
async def list_tag_ids_for_tag_group(
    id_: str = Field(..., alias="id", description="The unique identifier of the tag group. Use the tag group ID in UUID format (e.g., zyxw9876-vu54-ts32-rq10-zyxwvu654321)."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, optionally followed by a suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve all tag IDs contained within a specific tag group. This operation returns a collection of tag identifiers that belong to the given tag group."""

    # Construct request model with validation
    try:
        _request = _models.GetTagIdsForTagGroupRequest(
            path=_models.GetTagIdsForTagGroupRequestPath(id_=id_),
            header=_models.GetTagIdsForTagGroupRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_tag_ids_for_tag_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/tag-groups/{id}/relationships/tags", _request.path.model_dump(by_alias=True)) if _request.path else "/api/tag-groups/{id}/relationships/tags"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_tag_ids_for_tag_group")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_tag_ids_for_tag_group", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_tag_ids_for_tag_group",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Templates
@mcp.tool()
async def list_templates(
    revision: str = Field(..., description="API revision date in YYYY-MM-DD format (or with optional suffix). Defaults to 2026-01-15 if not specified."),
    filter_: str | None = Field(None, alias="filter", description="Filter templates by id, name, created date, or updated date. Supports exact matching, partial text search, and date range comparisons. See API documentation for filter syntax details."),
) -> dict[str, Any]:
    """Retrieve all templates in your account with optional filtering and sorting. Results are paginated with a maximum of 10 templates per page."""

    # Construct request model with validation
    try:
        _request = _models.GetTemplatesRequest(
            query=_models.GetTemplatesRequestQuery(filter_=filter_),
            header=_models.GetTemplatesRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_templates: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/templates"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

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

# Tags: Templates
@mcp.tool()
async def create_template(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format (or with optional suffix). Defaults to 2026-01-15."),
    type_: Literal["template"] = Field(..., alias="type", description="Resource type identifier. Must be set to 'template'."),
    name: str = Field(..., description="Human-readable name for the template (e.g., 'Monthly Newsletter Template')."),
    editor_type: str = Field(..., description="Template editor type. Must be either CODE (for custom HTML editing) or USER_DRAGGABLE (for visual drag-and-drop editor)."),
    html: str | None = Field(None, description="The HTML markup content of the template. Provide a complete, valid HTML document structure."),
    text: str | None = Field(None, description="Plain text version of the template content, used as a fallback for email clients that don't support HTML."),
    amp: str | None = Field(None, description="AMP (Accelerated Mobile Pages) version of the template for dynamic email content. Requires AMP Email to be enabled in your account; refer to the AMP Email setup guide for configuration details."),
) -> dict[str, Any]:
    """Create a new custom HTML email template. Note that accounts are limited to 1,000 templates via the API; creation will fail if this limit is reached."""

    # Construct request model with validation
    try:
        _request = _models.CreateTemplateRequest(
            header=_models.CreateTemplateRequestHeader(revision=revision),
            body=_models.CreateTemplateRequestBody(data=_models.CreateTemplateRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateTemplateRequestBodyDataAttributes(name=name, editor_type=editor_type, html=html, text=text, amp=amp)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/templates"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

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
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Templates
@mcp.tool()
async def get_template(
    id_: str = Field(..., alias="id", description="The unique identifier of the template to retrieve."),
    revision: str = Field(..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.v1). Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Retrieve a specific template by its ID. Returns the template configuration and metadata for the requested template."""

    # Construct request model with validation
    try:
        _request = _models.GetTemplateRequest(
            path=_models.GetTemplateRequestPath(id_=id_),
            header=_models.GetTemplateRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/templates/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/templates/{id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

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

# Tags: Templates
@mcp.tool()
async def update_template(
    id_: str = Field(..., alias="id", description="The unique identifier of the template to update. Must match the ID provided in the request body."),
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15). Defaults to 2026-01-15 if not specified."),
    data_id: str = Field(..., alias="dataId", description="The unique identifier of the template being updated. Must match the path ID parameter."),
    type_: Literal["template"] = Field(..., alias="type", description="The resource type identifier. Must be set to 'template'."),
    name: str | None = Field(None, description="The display name for the template (e.g., 'Monthly Newsletter Template'). Optional field for updating template identification."),
    html: str | None = Field(None, description="The HTML markup content of the template. Provide complete, valid HTML structure. Optional field for updating template rendering."),
    text: str | None = Field(None, description="The plaintext version of the template content. Used as fallback for email clients that don't support HTML. Optional field for updating template text representation."),
    amp: str | None = Field(None, description="The AMP for Email version of the template. Requires AMP Email to be enabled in your Klaviyo account to use. Refer to the AMP Email setup guide for implementation details. Optional field for updating dynamic email content."),
) -> dict[str, Any]:
    """Update an existing email template by ID. Allows modification of template name, HTML content, plaintext version, and AMP email format. Note: drag & drop templates are not currently supported for updates."""

    # Construct request model with validation
    try:
        _request = _models.UpdateTemplateRequest(
            path=_models.UpdateTemplateRequestPath(id_=id_),
            header=_models.UpdateTemplateRequestHeader(revision=revision),
            body=_models.UpdateTemplateRequestBody(data=_models.UpdateTemplateRequestBodyData(
                    id_=data_id, type_=type_,
                    attributes=_models.UpdateTemplateRequestBodyDataAttributes(name=name, html=html, text=text, amp=amp) if any(v is not None for v in [name, html, text, amp]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/templates/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/templates/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_template", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_template",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Templates
@mcp.tool()
async def delete_template(
    id_: str = Field(..., alias="id", description="The unique identifier of the template to delete."),
    revision: str = Field(..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15 if not specified)."),
) -> dict[str, Any]:
    """Permanently delete a template by its ID. This operation requires the template ID and API revision to ensure the correct version is targeted."""

    # Construct request model with validation
    try:
        _request = _models.DeleteTemplateRequest(
            path=_models.DeleteTemplateRequestPath(id_=id_),
            header=_models.DeleteTemplateRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/templates/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/templates/{id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

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

# Tags: Templates
@mcp.tool()
async def list_universal_content(
    revision: str = Field(..., description="API revision date in YYYY-MM-DD format (with optional suffix). Defaults to 2026-01-15 if not provided."),
    filter_: str | None = Field(None, alias="filter", description="Filter results using Klaviyo's filter syntax. Supports filtering by ID, name, creation/update timestamps (with comparison operators), content type, and definition type. See Klaviyo's filtering documentation for syntax details."),
    page_size: int | None = Field(None, alias="pagesize", description="Number of results to return per page. Must be between 1 and 100 items; defaults to 20 if not specified.", ge=1, le=100),
) -> dict[str, Any]:
    """Retrieve all universal content items in your account. Supports filtering by ID, name, creation/update dates, and content type, with pagination for managing large result sets."""

    # Construct request model with validation
    try:
        _request = _models.GetAllUniversalContentRequest(
            query=_models.GetAllUniversalContentRequestQuery(filter_=filter_, page_size=page_size),
            header=_models.GetAllUniversalContentRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_universal_content: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/template-universal-content"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_universal_content")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_universal_content", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_universal_content",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Templates
@mcp.tool()
async def create_universal_content(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15 if not specified)"),
    type_: Literal["template-universal-content"] = Field(..., alias="type", description="The resource type identifier, must be set to 'template-universal-content'"),
    name: str = Field(..., description="A descriptive name for this universal content block"),
    definition: _models.ButtonBlock | _models.DropShadowBlock | _models.HorizontalRuleBlock | _models.HtmlBlock | _models.ImageBlock | _models.SpacerBlock | _models.TextBlock = Field(..., description="The block configuration object defining the content structure and properties. Supported block types are: button, drop_shadow, horizontal_rule, html, image, spacer, and text"),
) -> dict[str, Any]:
    """Create a universal content block for use in templates. Supports multiple block types including buttons, images, text, HTML, spacing elements, and decorative components."""

    # Construct request model with validation
    try:
        _request = _models.CreateUniversalContentRequest(
            header=_models.CreateUniversalContentRequestHeader(revision=revision),
            body=_models.CreateUniversalContentRequestBody(data=_models.CreateUniversalContentRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateUniversalContentRequestBodyDataAttributes(name=name, definition=definition)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_universal_content: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/template-universal-content"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_universal_content")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_universal_content", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_universal_content",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Templates
@mcp.tool()
async def get_universal_content(
    id_: str = Field(..., alias="id", description="The unique identifier of the universal content template to retrieve (e.g., 01HWWWKAW4RHXQJCMW4R2KRYR4)."),
    revision: str = Field(..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15 if not specified)."),
) -> dict[str, Any]:
    """Retrieve a specific universal content template by its ID. Returns the template configuration and content for the specified revision."""

    # Construct request model with validation
    try:
        _request = _models.GetUniversalContentRequest(
            path=_models.GetUniversalContentRequestPath(id_=id_),
            header=_models.GetUniversalContentRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_universal_content: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/template-universal-content/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/template-universal-content/{id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_universal_content")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_universal_content", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_universal_content",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Templates
@mcp.tool()
async def update_template_universal_content(
    id_: str = Field(..., alias="id", description="The unique identifier of the template universal content to update, formatted as a ULID."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
    data_id: str = Field(..., alias="dataId", description="The unique identifier of the template universal content being updated; must match the path ID parameter."),
    type_: Literal["template-universal-content"] = Field(..., alias="type", description="The resource type identifier; must be set to 'template-universal-content'."),
    name: str | None = Field(None, description="A human-readable name for this template universal content."),
    definition: _models.ButtonBlock | _models.DropShadowBlock | _models.HorizontalRuleBlock | _models.HtmlBlock | _models.ImageBlock | _models.SpacerBlock | _models.TextBlock | None = Field(None, description="The block definition configuration. Only supported for button, drop_shadow, horizontal_rule, html, image, spacer, and text block types."),
) -> dict[str, Any]:
    """Update universal content within a template. Only specific block types (button, drop_shadow, horizontal_rule, html, image, spacer, and text) support definition field updates."""

    # Construct request model with validation
    try:
        _request = _models.UpdateUniversalContentRequest(
            path=_models.UpdateUniversalContentRequestPath(id_=id_),
            header=_models.UpdateUniversalContentRequestHeader(revision=revision),
            body=_models.UpdateUniversalContentRequestBody(data=_models.UpdateUniversalContentRequestBodyData(
                    id_=data_id, type_=type_,
                    attributes=_models.UpdateUniversalContentRequestBodyDataAttributes(name=name, definition=definition) if any(v is not None for v in [name, definition]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_template_universal_content: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/template-universal-content/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/template-universal-content/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_template_universal_content")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_template_universal_content", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_template_universal_content",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Templates
@mcp.tool()
async def delete_universal_content(
    id_: str = Field(..., alias="id", description="The unique identifier of the template universal content to delete. Use the full ID string (e.g., 01HWWWKAW4RHXQJCMW4R2KRYR4)."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, optionally followed by a suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Permanently delete a universal content template by its ID. This operation requires the templates:write scope and is subject to rate limits of 75 requests per second (burst) or 700 per minute (steady state)."""

    # Construct request model with validation
    try:
        _request = _models.DeleteUniversalContentRequest(
            path=_models.DeleteUniversalContentRequestPath(id_=id_),
            header=_models.DeleteUniversalContentRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_universal_content: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/template-universal-content/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/template-universal-content/{id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_universal_content")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_universal_content", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_universal_content",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Templates
@mcp.tool()
async def render_template(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix. Defaults to 2026-01-15 if not specified."),
    type_: Literal["template"] = Field(..., alias="type", description="Resource type identifier. Must be set to 'template' to specify this operation targets email templates."),
    id_: str = Field(..., alias="id", description="The unique identifier of the email template to render."),
    context: dict[str, Any] = Field(..., description="A JSON object containing template variable values. Use dot notation to reference nested properties (e.g., user.first_name). Variables without corresponding context values render as empty. See Klaviyo template documentation for supported tag syntax."),
) -> dict[str, Any]:
    """Render an email template with provided context variables, returning AMP, HTML, and plain text versions. Template variables use dot notation for nested access and are treated as false when missing from context."""

    # Construct request model with validation
    try:
        _request = _models.RenderTemplateRequest(
            header=_models.RenderTemplateRequestHeader(revision=revision),
            body=_models.RenderTemplateRequestBody(data=_models.RenderTemplateRequestBodyData(
                    type_=type_, id_=id_,
                    attributes=_models.RenderTemplateRequestBodyDataAttributes(context=context)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for render_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/template-render"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("render_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("render_template", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="render_template",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Templates
@mcp.tool()
async def create_template_clone(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15 if not specified)."),
    type_: Literal["template"] = Field(..., alias="type", description="Resource type identifier; must be set to 'template' for this operation."),
    id_: str = Field(..., alias="id", description="The unique identifier of the template to clone."),
    name: str | None = Field(None, description="Optional custom name for the cloned template. If not provided, the system will assign a default name."),
) -> dict[str, Any]:
    """Create a duplicate of an existing template by its ID. Note that accounts are limited to 1,000 templates created via API; cloning will fail if this limit is reached."""

    # Construct request model with validation
    try:
        _request = _models.CloneTemplateRequest(
            header=_models.CloneTemplateRequestHeader(revision=revision),
            body=_models.CloneTemplateRequestBody(data=_models.CloneTemplateRequestBodyData(
                    type_=type_, id_=id_,
                    attributes=_models.CloneTemplateRequestBodyDataAttributes(name=name) if any(v is not None for v in [name]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_template_clone: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/template-clone"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_template_clone")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_template_clone", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_template_clone",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Tracking Settings
@mcp.tool()
async def get_tracking_settings(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format (optionally with a suffix). Defaults to the latest stable revision."),
    fields_tracking_setting: list[Literal["auto_add_parameters", "custom_parameters", "utm_campaign", "utm_campaign.campaign", "utm_campaign.campaign.type", "utm_campaign.campaign.value", "utm_campaign.flow", "utm_campaign.flow.type", "utm_campaign.flow.value", "utm_id", "utm_id.campaign", "utm_id.campaign.type", "utm_id.campaign.value", "utm_id.flow", "utm_id.flow.type", "utm_id.flow.value", "utm_medium", "utm_medium.campaign", "utm_medium.campaign.type", "utm_medium.campaign.value", "utm_medium.flow", "utm_medium.flow.type", "utm_medium.flow.value", "utm_source", "utm_source.campaign", "utm_source.campaign.type", "utm_source.campaign.value", "utm_source.flow", "utm_source.flow.type", "utm_source.flow.value", "utm_term", "utm_term.campaign", "utm_term.campaign.type", "utm_term.campaign.value", "utm_term.flow", "utm_term.flow.type", "utm_term.flow.value"]] | None = Field(None, alias="fieldstracking-setting", description="Specify which fields to include in the response for each tracking setting. Use sparse fieldsets to optimize payload size by requesting only the fields you need."),
    page_size: int | None = Field(None, alias="pagesize", description="Number of results to return per page. This endpoint supports only a single result, so the maximum value is 1.", ge=1, le=1),
) -> dict[str, Any]:
    """Retrieve all UTM tracking settings configured for your Klaviyo account. Returns an array containing the account's tracking setting configuration."""

    # Construct request model with validation
    try:
        _request = _models.GetTrackingSettingsRequest(
            query=_models.GetTrackingSettingsRequestQuery(fields_tracking_setting=fields_tracking_setting, page_size=page_size),
            header=_models.GetTrackingSettingsRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_tracking_settings: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/tracking-settings"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_query = _serialize_query(_http_query, {
        "fields[tracking-setting]": ("form", False),
    })
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_tracking_settings")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_tracking_settings", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_tracking_settings",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tracking Settings
@mcp.tool()
async def get_tracking_setting(
    id_: str = Field(..., alias="id", description="The account ID of the tracking setting to retrieve (e.g., 'abCdEf')."),
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified."),
    fields_tracking_setting: list[Literal["auto_add_parameters", "custom_parameters", "utm_campaign", "utm_campaign.campaign", "utm_campaign.campaign.type", "utm_campaign.campaign.value", "utm_campaign.flow", "utm_campaign.flow.type", "utm_campaign.flow.value", "utm_id", "utm_id.campaign", "utm_id.campaign.type", "utm_id.campaign.value", "utm_id.flow", "utm_id.flow.type", "utm_id.flow.value", "utm_medium", "utm_medium.campaign", "utm_medium.campaign.type", "utm_medium.campaign.value", "utm_medium.flow", "utm_medium.flow.type", "utm_medium.flow.value", "utm_source", "utm_source.campaign", "utm_source.campaign.type", "utm_source.campaign.value", "utm_source.flow", "utm_source.flow.type", "utm_source.flow.value", "utm_term", "utm_term.campaign", "utm_term.campaign.type", "utm_term.campaign.value", "utm_term.flow", "utm_term.flow.type", "utm_term.flow.value"]] | None = Field(None, alias="fieldstracking-setting", description="Specify which fields to include in the response for the tracking-setting resource. Use sparse fieldsets to optimize payload size by requesting only needed fields."),
) -> dict[str, Any]:
    """Retrieve a UTM tracking setting by account ID. Returns the tracking configuration for the specified account, which controls how UTM parameters are captured and processed."""

    # Construct request model with validation
    try:
        _request = _models.GetTrackingSettingRequest(
            path=_models.GetTrackingSettingRequestPath(id_=id_),
            query=_models.GetTrackingSettingRequestQuery(fields_tracking_setting=fields_tracking_setting),
            header=_models.GetTrackingSettingRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_tracking_setting: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/tracking-settings/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/tracking-settings/{id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_query = _serialize_query(_http_query, {
        "fields[tracking-setting]": ("form", False),
    })
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_tracking_setting")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_tracking_setting", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_tracking_setting",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Web Feeds
@mcp.tool()
async def list_web_feeds(
    revision: str = Field(..., description="API version in YYYY-MM-DD format (optionally with a suffix). Defaults to 2026-01-15 if not provided."),
    filter_: str | None = Field(None, alias="filter", description="Filter results using comparison operators on feed name, creation date, or last update date. Supports exact matching, partial text matching, and date range queries. See API documentation for detailed filter syntax."),
    page_size: int | None = Field(None, alias="pagesize", description="Number of results to return per page. Must be between 1 and 20 items; defaults to 5 if not specified.", ge=1, le=20),
) -> dict[str, Any]:
    """Retrieve all web feeds configured for your account. Supports filtering by name, creation date, or last update, with pagination to manage large result sets."""

    # Construct request model with validation
    try:
        _request = _models.GetWebFeedsRequest(
            query=_models.GetWebFeedsRequestQuery(filter_=filter_, page_size=page_size),
            header=_models.GetWebFeedsRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_web_feeds: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/web-feeds"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_web_feeds")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_web_feeds", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_web_feeds",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Web Feeds
@mcp.tool()
async def create_web_feed(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15 if not specified)."),
    type_: Literal["web-feed"] = Field(..., alias="type", description="The resource type identifier; must be set to 'web-feed'."),
    name: str = Field(..., description="A descriptive name for this web feed (e.g., 'Blog_posts'). Used for identification and display purposes."),
    url: str = Field(..., description="The URL endpoint from which to fetch the web feed content (e.g., 'https://help.klaviyo.com/api/v2/help_center/en-us/articles.json')."),
    request_method: Literal["get", "post"] = Field(..., description="The HTTP method to use when requesting the feed; either 'get' for standard retrieval or 'post' for feeds requiring POST requests."),
    content_type: Literal["json", "xml"] = Field(..., description="The expected content format of the feed; either 'json' for JSON-formatted feeds or 'xml' for XML-formatted feeds."),
) -> dict[str, Any]:
    """Create a new web feed to aggregate content from a specified URL. The feed will be polled using the specified HTTP method and parsed according to the declared content type."""

    # Construct request model with validation
    try:
        _request = _models.CreateWebFeedRequest(
            header=_models.CreateWebFeedRequestHeader(revision=revision),
            body=_models.CreateWebFeedRequestBody(data=_models.CreateWebFeedRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateWebFeedRequestBodyDataAttributes(name=name, url=url, request_method=request_method, content_type=content_type)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_web_feed: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/web-feeds"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_web_feed")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_web_feed", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_web_feed",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Web Feeds
@mcp.tool()
async def get_web_feed(
    id_: str = Field(..., alias="id", description="The unique identifier of the web feed to retrieve (e.g., '925e385b52fb')"),
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15 if not specified)"),
) -> dict[str, Any]:
    """Retrieve a specific web feed by its ID. Returns the complete feed configuration and metadata for the given feed identifier."""

    # Construct request model with validation
    try:
        _request = _models.GetWebFeedRequest(
            path=_models.GetWebFeedRequestPath(id_=id_),
            header=_models.GetWebFeedRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_web_feed: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/web-feeds/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/web-feeds/{id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_web_feed")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_web_feed", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_web_feed",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Web Feeds
@mcp.tool()
async def update_web_feed(
    id_: str = Field(..., alias="id", description="The unique identifier of the web feed to update (e.g., '925e385b52fb')"),
    revision: str = Field(..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15)"),
    data_id: str = Field(..., alias="dataId", description="The unique identifier of the web feed being updated; must match the ID in the URL path (e.g., '925e385b52fb')"),
    type_: Literal["web-feed"] = Field(..., alias="type", description="The resource type identifier; must be set to 'web-feed'"),
    name: str | None = Field(None, description="A descriptive name for the web feed (e.g., 'Blog_posts')"),
    url: str | None = Field(None, description="The URL endpoint from which to fetch the web feed content (e.g., 'https://help.klaviyo.com/api/v2/help_center/en-us/articles.json')"),
    request_method: Literal["get", "post"] | None = Field(None, description="The HTTP method to use when requesting the web feed; either 'get' or 'post'"),
    content_type: Literal["json", "xml"] | None = Field(None, description="The expected content format of the web feed; either 'json' or 'xml'"),
) -> dict[str, Any]:
    """Update an existing web feed configuration, including its name, URL, request method, and content type. Requires the feed ID and current API revision for the request."""

    # Construct request model with validation
    try:
        _request = _models.UpdateWebFeedRequest(
            path=_models.UpdateWebFeedRequestPath(id_=id_),
            header=_models.UpdateWebFeedRequestHeader(revision=revision),
            body=_models.UpdateWebFeedRequestBody(data=_models.UpdateWebFeedRequestBodyData(
                    id_=data_id, type_=type_,
                    attributes=_models.UpdateWebFeedRequestBodyDataAttributes(name=name, url=url, request_method=request_method, content_type=content_type) if any(v is not None for v in [name, url, request_method, content_type]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_web_feed: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/web-feeds/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/web-feeds/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_web_feed")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_web_feed", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_web_feed",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Web Feeds
@mcp.tool()
async def delete_web_feed(
    id_: str = Field(..., alias="id", description="The unique identifier of the web feed to delete (e.g., '925e385b52fb')"),
    revision: str = Field(..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15 if not specified)"),
) -> dict[str, Any]:
    """Permanently delete a web feed by its ID. This operation requires the feed ID and API revision to ensure safe deletion."""

    # Construct request model with validation
    try:
        _request = _models.DeleteWebFeedRequest(
            path=_models.DeleteWebFeedRequestPath(id_=id_),
            header=_models.DeleteWebFeedRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_web_feed: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/web-feeds/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/web-feeds/{id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_web_feed")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_web_feed", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_web_feed",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Webhooks
@mcp.tool()
async def list_webhooks(
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format (or with optional suffix). Defaults to 2026-01-15 if not specified."),
    fields_webhook: list[Literal["created_at", "description", "enabled", "endpoint_url", "name", "updated_at"]] | None = Field(None, alias="fieldswebhook", description="Specify which webhook fields to include in the response using sparse fieldsets for optimized payload size. Provide as an array of field names."),
) -> dict[str, Any]:
    """Retrieve all webhooks configured in the account. Use optional field filtering to customize the response payload."""

    # Construct request model with validation
    try:
        _request = _models.GetWebhooksRequest(
            query=_models.GetWebhooksRequestQuery(fields_webhook=fields_webhook),
            header=_models.GetWebhooksRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_webhooks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/webhooks"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_query = _serialize_query(_http_query, {
        "fields[webhook]": ("form", False),
    })
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

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
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Webhooks
@mcp.tool()
async def get_webhook(
    id_: str = Field(..., alias="id", description="The unique identifier of the webhook to retrieve."),
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format (optionally with a suffix). Defaults to 2026-01-15 if not specified."),
    fields_webhook: list[Literal["created_at", "description", "enabled", "endpoint_url", "name", "updated_at"]] | None = Field(None, alias="fieldswebhook", description="Optional array of specific webhook fields to include in the response. Use sparse fieldsets to reduce payload size and improve performance by requesting only needed fields."),
) -> dict[str, Any]:
    """Retrieve a specific webhook by its ID. Returns the webhook configuration and settings for the given identifier."""

    # Construct request model with validation
    try:
        _request = _models.GetWebhookRequest(
            path=_models.GetWebhookRequestPath(id_=id_),
            query=_models.GetWebhookRequestQuery(fields_webhook=fields_webhook),
            header=_models.GetWebhookRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_webhook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/webhooks/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/webhooks/{id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_query = _serialize_query(_http_query, {
        "fields[webhook]": ("form", False),
    })
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

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
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Webhooks
@mcp.tool()
async def update_webhook(
    id_: str = Field(..., alias="id", description="The unique identifier of the webhook to update."),
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.v1). Defaults to 2026-01-15 if not specified."),
    data_id: str = Field(..., alias="dataId", description="The unique identifier of the webhook being updated; must match the ID in the path parameter."),
    type_: Literal["webhook"] = Field(..., alias="type", description="The resource type; must be set to 'webhook'."),
    name: str | None = Field(None, description="A human-readable name for the webhook to help identify its purpose."),
    description: str | None = Field(None, description="A detailed description explaining what this webhook does or when it triggers."),
    endpoint_url: str | None = Field(None, description="The HTTPS URL where webhook events will be sent. Must use the HTTPS protocol for security."),
    secret_key: str | None = Field(None, description="A secret key used to cryptographically sign webhook requests, allowing the receiver to verify authenticity."),
    enabled: bool | None = Field(None, description="Whether the webhook is active and should send events. Set to true to enable or false to disable."),
    data: list[_models.UpdateWebhookBodyDataRelationshipsWebhookTopicsDataItem] | None = Field(None, description="Additional structured data associated with the webhook. Order and format depend on the webhook configuration schema."),
) -> dict[str, Any]:
    """Update an existing webhook configuration by ID. Modify webhook properties such as name, description, endpoint URL, secret key, and enabled status."""

    # Construct request model with validation
    try:
        _request = _models.UpdateWebhookRequest(
            path=_models.UpdateWebhookRequestPath(id_=id_),
            header=_models.UpdateWebhookRequestHeader(revision=revision),
            body=_models.UpdateWebhookRequestBody(data=_models.UpdateWebhookRequestBodyData(
                    id_=data_id, type_=type_,
                    attributes=_models.UpdateWebhookRequestBodyDataAttributes(name=name, description=description, endpoint_url=endpoint_url, secret_key=secret_key, enabled=enabled) if any(v is not None for v in [name, description, endpoint_url, secret_key, enabled]) else None,
                    relationships=_models.UpdateWebhookRequestBodyDataRelationships(webhook_topics=_models.UpdateWebhookRequestBodyDataRelationshipsWebhookTopics(data=data) if any(v is not None for v in [data]) else None) if any(v is not None for v in [data]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_webhook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/webhooks/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/webhooks/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_webhook")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_webhook", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_webhook",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Webhooks
@mcp.tool()
async def delete_webhook(
    id_: str = Field(..., alias="id", description="The unique identifier of the webhook to delete."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, optionally with a suffix. Defaults to 2026-01-15 if not specified."),
) -> dict[str, Any]:
    """Permanently delete a webhook by its ID. This action cannot be undone and will stop all event deliveries to the webhook's configured endpoint."""

    # Construct request model with validation
    try:
        _request = _models.DeleteWebhookRequest(
            path=_models.DeleteWebhookRequestPath(id_=id_),
            header=_models.DeleteWebhookRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_webhook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/webhooks/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/webhooks/{id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

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

# Tags: Webhooks
@mcp.tool()
async def list_webhook_topics(revision: str = Field(..., description="API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")) -> dict[str, Any]:
    """Retrieve all available webhook topics in a Klaviyo account. Webhook topics define the events that can trigger webhooks for your integration."""

    # Construct request model with validation
    try:
        _request = _models.GetWebhookTopicsRequest(
            header=_models.GetWebhookTopicsRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_webhook_topics: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/webhook-topics"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_webhook_topics")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_webhook_topics", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_webhook_topics",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Webhooks
@mcp.tool()
async def get_webhook_topic(
    id_: str = Field(..., alias="id", description="The unique identifier of the webhook topic to retrieve (e.g., 'event:klaviyo.sent_sms'). Use this ID to fetch the specific topic's configuration."),
    revision: str = Field(..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified, ensuring compatibility with the desired API version."),
) -> dict[str, Any]:
    """Retrieve a specific webhook topic by its ID to view its configuration and details. Useful for inspecting webhook topic settings before subscribing to events."""

    # Construct request model with validation
    try:
        _request = _models.GetWebhookTopicRequest(
            path=_models.GetWebhookTopicRequestPath(id_=id_),
            header=_models.GetWebhookTopicRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_webhook_topic: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/webhook-topics/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/webhook-topics/{id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_webhook_topic")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_webhook_topic", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_webhook_topic",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Client
@mcp.tool()
async def list_client_review_values_reports(
    company_id: str = Field(..., description="Your Klaviyo Public API Key / Site ID, used to identify your account. See Klaviyo documentation for details on locating this identifier."),
    group_by: Literal["company_id", "product_id"] = Field(..., description="Required grouping dimension for the report. Choose 'company_id' to aggregate across your entire account or 'product_id' to break down metrics by individual product."),
    statistics: str = Field(..., description="Required comma-separated list of statistics to calculate for each group, such as 'average_rating' or 'total_reviews'. Specify all metrics you need in a single value."),
    timeframe: Literal["all_time", "last_30_days", "last_365_days", "last_90_days"] = Field(..., description="Required timeframe window for the report. Choose from 'all_time', 'last_30_days', 'last_90_days', or 'last_365_days' to define the data collection period."),
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format (with optional suffix). Defaults to the latest stable version if not specified."),
    fields_review_values_report: list[Literal["results"]] | None = Field(None, alias="fieldsreview-values-report", description="Optional sparse fieldset to limit which fields are returned in the review-values-report objects. Specify as a comma-separated list of field names."),
    filter_: str | None = Field(None, alias="filter", description="Optional filter to narrow results by product external IDs. Supports 'equals' for exact match or 'any' to match multiple IDs. Use comma-separated format for multiple values with the 'any' operator."),
    page_size: int | None = Field(None, alias="pagesize", description="Optional page size for results, ranging from 1 to 100 items per page. Defaults to 20 if not specified.", ge=1, le=100),
) -> dict[str, Any]:
    """Retrieve aggregated review metrics reports for your account, grouped by company or product with customizable statistics and timeframe filtering."""

    # Construct request model with validation
    try:
        _request = _models.GetClientReviewValuesReportsRequest(
            query=_models.GetClientReviewValuesReportsRequestQuery(company_id=company_id, fields_review_values_report=fields_review_values_report, filter_=filter_, group_by=group_by, page_size=page_size, statistics=statistics, timeframe=timeframe),
            header=_models.GetClientReviewValuesReportsRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_client_review_values_reports: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/client/review-values-reports"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_query = _serialize_query(_http_query, {
        "fields[review-values-report]": ("form", False),
    })
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_client_review_values_reports")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_client_review_values_reports", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_client_review_values_reports",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Client
@mcp.tool()
async def list_client_reviews(
    company_id: str = Field(..., description="Your Public API Key or Site ID, used to identify your account. See the Klaviyo help article for instructions on locating this value."),
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format (with optional suffix). Defaults to 2026-01-15 if not specified."),
    filter_: str | None = Field(None, alias="filter", description="Filter reviews by specific criteria such as status, rating, review type, verification status, or content properties. Supports operators like equals, contains, has, and range comparisons (greater-or-equal, less-or-equal). For detailed filtering syntax, see the API overview documentation."),
    page_size: int | None = Field(None, alias="pagesize", description="Number of reviews to return per page. Must be between 1 and 100; defaults to 20 if not specified.", ge=1, le=100),
) -> dict[str, Any]:
    """Retrieve all product reviews for a client-side environment. Use this endpoint for client-side applications; for server-side implementations, refer to the server-side reviews endpoint."""

    # Construct request model with validation
    try:
        _request = _models.GetClientReviewsRequest(
            query=_models.GetClientReviewsRequestQuery(company_id=company_id, filter_=filter_, page_size=page_size),
            header=_models.GetClientReviewsRequestHeader(revision=revision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_client_reviews: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/client/reviews"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_client_reviews")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_client_reviews", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_client_reviews",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Client
@mcp.tool()
async def create_client_review(
    company_id: str = Field(..., description="Your Public API Key / Site ID used to identify your Klaviyo account. This is required for authentication."),
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15). Defaults to 2026-01-15 if not specified."),
    type_: Literal["review"] = Field(..., alias="type", description="Fixed resource type identifier. Must be set to 'review'."),
    order_data_type: Literal["order"] = Field(..., alias="orderDataType", description="Fixed relationship type identifier for the associated order. Must be set to 'order'."),
    review_type: Literal["question", "rating", "review", "store"] = Field(..., description="Classifies the submission type: 'review' for product reviews, 'rating' for ratings only, 'question' for customer questions, or 'store' for store-level reviews."),
    email: str = Field(..., description="Email address of the review author. Used to identify and contact the reviewer."),
    author: str = Field(..., description="Display name of the review author. This is shown publicly with the review."),
    content: str = Field(..., description="Main text content of the review or question. Provide detailed feedback about the product or ask a specific question."),
    external_id: str = Field(..., description="Unique product identifier from your e-commerce platform (e.g., Shopify product ID). Used to link the review to the correct product."),
    integration_key: Literal["shopify", "woocommerce"] = Field(..., description="Integration platform identifier in lowercase. Specifies whether the product comes from Shopify, WooCommerce, or another supported platform."),
    id_: str = Field(..., alias="id", description="Order ID that this review is associated with. Links the review to a specific customer purchase."),
    incentive_type: Literal["coupon_or_discount", "employee_review", "free_product", "loyalty_points", "other", "paid_promotion", "sweepstakes_entry"] | None = Field(None, description="Optional classification of how the reviewer was incentivized, if at all. Valid types include coupon/discount, free product, loyalty points, employee review, paid promotion, sweepstakes entry, or other."),
    rating: Literal[1, 2, 3, 4, 5] | None = Field(None, description="Numeric rating on a scale of 1 to 5, where 1 is lowest and 5 is highest. Only applicable for review and rating types; null for question types."),
    title: str | None = Field(None, description="Optional headline or summary for the review. Provides a brief overview of the reviewer's main point."),
    custom_questions: list[_models.CustomQuestionDto] | None = Field(None, description="Optional array of custom question responses. Each item contains a question ID and an array of selected answers (e.g., size or color selections)."),
    images: list[str] | None = Field(None, description="Optional list of image URLs or base-64 encoded data URIs attached to the review. Supports multiple images; empty array if no images provided."),
) -> dict[str, Any]:
    """Submit a product review from a client-side environment. This endpoint creates a review or question for a product associated with an order, supporting ratings, custom questions, and image attachments."""

    # Construct request model with validation
    try:
        _request = _models.CreateClientReviewRequest(
            query=_models.CreateClientReviewRequestQuery(company_id=company_id),
            header=_models.CreateClientReviewRequestHeader(revision=revision),
            body=_models.CreateClientReviewRequestBody(data=_models.CreateClientReviewRequestBodyData(
                    type_=type_,
                    relationships=_models.CreateClientReviewRequestBodyDataRelationships(
                        order=_models.CreateClientReviewRequestBodyDataRelationshipsOrder(
                            data=_models.CreateClientReviewRequestBodyDataRelationshipsOrderData(type_=order_data_type, id_=id_)
                        )
                    ),
                    attributes=_models.CreateClientReviewRequestBodyDataAttributes(
                        review_type=review_type, email=email, author=author, content=content, incentive_type=incentive_type, rating=rating, title=title, custom_questions=custom_questions, images=images,
                        product=_models.CreateClientReviewRequestBodyDataAttributesProduct(external_id=external_id, integration_key=integration_key)
                    )
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_client_review: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/client/reviews"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_client_review")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_client_review", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_client_review",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Client
@mcp.tool()
async def create_client_subscription(
    company_id: str = Field(..., description="Your public API key (site ID) for client-side authentication. Required for all requests to this endpoint."),
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix. Defaults to 2026-01-15 if not specified."),
    type_: Literal["subscription"] = Field(..., alias="type", description="Resource type identifier. Must be set to 'subscription'."),
    list_data_type: Literal["list"] = Field(..., alias="listDataType", description="List resource type identifier. Must be set to 'list'."),
    id_: str = Field(..., alias="id", description="The ID of the list to add the newly subscribed profile to. Required to associate the subscription with a specific audience list."),
    custom_source: str | None = Field(None, description="Optional custom source or method detail to record on the consent records, such as 'Homepage footer signup form' or other signup origin."),
    profile: _models.CreateClientSubscriptionBodyDataAttributesProfile | None = Field(None, description="Profile to subscribe: email, phone, name, location, subscription consents, and custom properties."),
) -> dict[str, Any]:
    """Subscribe a contact to email and/or SMS marketing channels by creating a subscription and consent record. Must be called from client-side environments only using a public API key. Provide either an email address or phone number (or both) to identify the contact."""

    # Construct request model with validation
    try:
        _request = _models.CreateClientSubscriptionRequest(
            query=_models.CreateClientSubscriptionRequestQuery(company_id=company_id),
            header=_models.CreateClientSubscriptionRequestHeader(revision=revision),
            body=_models.CreateClientSubscriptionRequestBody(data=_models.CreateClientSubscriptionRequestBodyData(
                    type_=type_,
                    relationships=_models.CreateClientSubscriptionRequestBodyDataRelationships(
                        list_=_models.CreateClientSubscriptionRequestBodyDataRelationshipsList(
                            data=_models.CreateClientSubscriptionRequestBodyDataRelationshipsListData(type_=list_data_type, id_=id_)
                        )
                    ),
                    attributes=_models.CreateClientSubscriptionRequestBodyDataAttributes(custom_source=custom_source, profile=profile) if any(v is not None for v in [custom_source, profile]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_client_subscription: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/client/subscriptions"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_client_subscription")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_client_subscription", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_client_subscription",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Client
@mcp.tool()
async def create_or_update_client_profile(
    company_id: str = Field(..., description="Your public API key (also called Site ID), required to authenticate client-side requests. Obtain this from your Klaviyo account settings."),
    revision: str = Field(..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15). Defaults to the latest stable version."),
    type_: Literal["profile"] = Field(..., alias="type", description="Resource type identifier. Must be set to 'profile' for this operation."),
    email: str | None = Field(None, description="Individual's email address. Use this as a primary identifier for profile matching and updates."),
    phone_number: str | None = Field(None, description="Individual's phone number in E.164 format (e.g., +1 country code followed by number). Use this as an alternative or supplementary identifier."),
    external_id: str | None = Field(None, description="A unique identifier from an external system (such as a point-of-sale or CRM system) to link Klaviyo profiles with your internal records. Format depends on your external system."),
    anonymous_id: str | None = Field(None, description="An anonymous identifier used when profile identity is not yet known. Useful for tracking before email or phone collection."),
    kx: str | None = Field(None, description="Encrypted exchange identifier (kx) used by Klaviyo's web tracking to identify profiles. Can be used as a filter when retrieving profiles."),
    first_name: str | None = Field(None, description="Individual's first name."),
    last_name: str | None = Field(None, description="Individual's last name."),
    organization: str | None = Field(None, description="Name of the company or organization where the individual works."),
    locale: str | None = Field(None, description="Profile's locale in IETF BCP 47 format (e.g., en-US, fr-FR). Follows ISO 639-1/2 language codes and ISO 3166 country codes."),
    title: str | None = Field(None, description="Individual's job title or professional role."),
    image: str | None = Field(None, description="URL pointing to a profile image or avatar."),
    address1: str | None = Field(None, description="First line of the street address."),
    address2: str | None = Field(None, description="Second line of the street address (e.g., apartment, suite, or floor number)."),
    city: str | None = Field(None, description="City name."),
    country: str | None = Field(None, description="Country name."),
    latitude: str | None = Field(None, description="Latitude coordinate for geographic location. Provide with four decimal places precision for accuracy. Accepts string or numeric format."),
    longitude: str | None = Field(None, description="Longitude coordinate for geographic location. Provide with four decimal places precision for accuracy. Accepts string or numeric format."),
    region: str | None = Field(None, description="Region, state, or province within the country."),
    zip_: str | None = Field(None, alias="zip", description="Postal or zip code."),
    timezone_: str | None = Field(None, alias="timezone", description="Time zone name using the IANA Time Zone Database format (e.g., America/New_York, Europe/London). Used for scheduling and localization."),
    ip: str | None = Field(None, description="IP address of the profile (IPv4 or IPv6 format). Useful for geolocation and fraud detection."),
    properties: dict[str, Any] | None = Field(None, description="Custom properties as key-value pairs. Use this to store additional profile attributes specific to your business (e.g., customer tier, preferences, or metadata)."),
    append: dict[str, Any] | None = Field(None, description="Append values to existing array properties. Specify property names with values to add. Useful for accumulating list-based attributes without replacing existing data."),
    unappend: dict[str, Any] | None = Field(None, description="Remove specific values from existing array properties. Specify property names with values to remove. Useful for cleaning up list-based attributes."),
    unset: str | list[str] | None = Field(None, description="Remove one or more properties entirely from the profile. Specify property names as a string or array to delete them and their values completely."),
) -> dict[str, Any]:
    """Create or update a customer profile with identity and property information from client-side environments. This endpoint requires a public API key and is designed for browser-based implementations; use server-side endpoints for identifier updates or server applications."""

    # Construct request model with validation
    try:
        _request = _models.CreateClientProfileRequest(
            query=_models.CreateClientProfileRequestQuery(company_id=company_id),
            header=_models.CreateClientProfileRequestHeader(revision=revision),
            body=_models.CreateClientProfileRequestBody(data=_models.CreateClientProfileRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateClientProfileRequestBodyDataAttributes(email=email, phone_number=phone_number, external_id=external_id, anonymous_id=anonymous_id, kx=kx, first_name=first_name, last_name=last_name, organization=organization, locale=locale, title=title, image=image, properties=properties,
                        location=_models.CreateClientProfileRequestBodyDataAttributesLocation(address1=address1, address2=address2, city=city, country=country, latitude=latitude, longitude=longitude, region=region, zip_=zip_, timezone_=timezone_, ip=ip) if any(v is not None for v in [address1, address2, city, country, latitude, longitude, region, zip_, timezone_, ip]) else None) if any(v is not None for v in [email, phone_number, external_id, anonymous_id, kx, first_name, last_name, organization, locale, title, image, address1, address2, city, country, latitude, longitude, region, zip_, timezone_, ip, properties]) else None,
                    meta=_models.CreateClientProfileRequestBodyDataMeta(patch_properties=_models.CreateClientProfileRequestBodyDataMetaPatchProperties(append=append, unappend=unappend, unset=unset) if any(v is not None for v in [append, unappend, unset]) else None) if any(v is not None for v in [append, unappend, unset]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_or_update_client_profile: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/client/profiles"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_or_update_client_profile")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_or_update_client_profile", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_or_update_client_profile",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Client
@mcp.tool()
async def subscribe_profile_to_back_in_stock_notifications(
    company_id: str = Field(..., description="Your public API key (also called Site ID), which identifies your Klaviyo account. Required for client-side authentication."),
    revision: str = Field(..., description="API endpoint revision date in YYYY-MM-DD format (with optional suffix). Defaults to 2026-01-15 if not specified."),
    type_: Literal["back-in-stock-subscription"] = Field(..., alias="type", description="Fixed value that identifies this as a back-in-stock-subscription resource type."),
    profile_data_type: Literal["profile"] = Field(..., alias="profileDataType", description="Fixed value that identifies the nested profile object type."),
    variant_data_type: Literal["catalog-variant"] = Field(..., alias="variantDataType", description="Fixed value that identifies the catalog variant object type in the relationship."),
    channels: list[Literal["EMAIL", "PUSH", "SMS", "WHATSAPP"]] = Field(..., description="One or more notification channels the profile prefers to receive back-in-stock alerts through. Valid options are EMAIL, SMS, or both as an array."),
    variant_data_id: str = Field(..., alias="variantDataId", description="The catalog variant ID in the format integrationType:::catalogId:::externalId (e.g., $custom:::$default:::VARIANT-ID or $shopify:::$default:::33001893429341). Identifies which product variant the profile is subscribing to."),
    profile_data_id: str | None = Field(None, alias="profileDataId", description="The unique Klaviyo profile ID (generated by Klaviyo) if subscribing an existing profile. Either this or email/phone_number must be provided to identify the profile."),
    email: str | None = Field(None, description="The profile's email address. Use this to identify or create a profile if profile ID is not provided."),
    phone_number: str | None = Field(None, description="The profile's phone number in E.164 format (e.g., +1 country code and number). Use this to identify or create a profile if profile ID is not provided."),
    external_id: str | None = Field(None, description="An external identifier from your system (such as a customer ID from your point-of-sale or CRM) to link this Klaviyo profile with your internal records."),
) -> dict[str, Any]:
    """Subscribe a customer profile to receive back-in-stock notifications for a specific product variant through their preferred channels (email, SMS, or both). This client-side endpoint requires a public API key and is designed for browser-based implementations."""

    # Construct request model with validation
    try:
        _request = _models.CreateClientBackInStockSubscriptionRequest(
            query=_models.CreateClientBackInStockSubscriptionRequestQuery(company_id=company_id),
            header=_models.CreateClientBackInStockSubscriptionRequestHeader(revision=revision),
            body=_models.CreateClientBackInStockSubscriptionRequestBody(data=_models.CreateClientBackInStockSubscriptionRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateClientBackInStockSubscriptionRequestBodyDataAttributes(
                        channels=channels,
                        profile=_models.CreateClientBackInStockSubscriptionRequestBodyDataAttributesProfile(
                            data=_models.CreateClientBackInStockSubscriptionRequestBodyDataAttributesProfileData(
                                type_=profile_data_type, id_=profile_data_id,
                                attributes=_models.CreateClientBackInStockSubscriptionRequestBodyDataAttributesProfileDataAttributes(email=email, phone_number=phone_number, external_id=external_id) if any(v is not None for v in [email, phone_number, external_id]) else None
                            )
                        )
                    ),
                    relationships=_models.CreateClientBackInStockSubscriptionRequestBodyDataRelationships(
                        variant=_models.CreateClientBackInStockSubscriptionRequestBodyDataRelationshipsVariant(
                            data=_models.CreateClientBackInStockSubscriptionRequestBodyDataRelationshipsVariantData(type_=variant_data_type, id_=variant_data_id)
                        )
                    )
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for subscribe_profile_to_back_in_stock_notifications: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/client/back-in-stock-subscriptions"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("subscribe_profile_to_back_in_stock_notifications")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("subscribe_profile_to_back_in_stock_notifications", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="subscribe_profile_to_back_in_stock_notifications",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/vnd.api+json",
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
        print("  python klaviyo_api_server.py", file=sys.stderr)
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

    parser = argparse.ArgumentParser(description="Klaviyo MCP Server")

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
    logger.info("Starting Klaviyo MCP Server")
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

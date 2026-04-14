#!/usr/bin/env python3
"""
Google Drive MCP Server

API Info:
- API License: Creative Commons Attribution 3.0 (http://creativecommons.org/licenses/by/3.0/)
- Contact: Google (https://google.com)
- Terms of Service: https://developers.google.com/terms/

Generated: 2026-04-14 18:23:24 UTC
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
from pydantic import Field

BASE_URL = os.getenv("BASE_URL", "https://www.googleapis.com/drive/v3")
SERVER_NAME = "Google Drive"
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

def build_anchor(anchor_start_index: int | None = None, anchor_end_index: int | None = None) -> str | None:
    """Helper function for parameter transformation"""
    if anchor_start_index is None and anchor_end_index is None:
        return None
    try:
        anchor_dict = {}
        if anchor_start_index is not None:
            anchor_dict['startIndex'] = anchor_start_index
        if anchor_end_index is not None:
            anchor_dict['endIndex'] = anchor_end_index
        return json.dumps(anchor_dict)
    except Exception as e:
        raise ValueError(f"Failed to build anchor JSON: {e}") from e

def parse_video_dimensions(value: str | None = None) -> dict | None:
    """Helper function for parameter transformation"""
    if value is None:
        return None
    try:
        parts = value.split('x')
        if len(parts) != 2:
            raise ValueError('Invalid format')
        return {'width': int(parts[0]), 'height': int(parts[1])}
    except (ValueError, IndexError) as e:
        raise ValueError(f'Video dimensions must be in WIDTHxHEIGHT format (e.g., "1920x1080"), got: {value}') from e

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

mcp = FastMCP("Google Drive", middleware=[_JsonCoercionMiddleware()])

# Tags: about
@mcp.tool()
async def get_user_info(fields: str | None = Field(None, description="Selector specifying which fields to include in a partial response.")) -> dict[str, Any]:
    """Retrieves information about the authenticated user, their Drive, and system capabilities. Use the `fields` parameter to specify which user properties and Drive details to return."""

    # Construct request model with validation
    try:
        _request = _models.AboutGetRequest(
            query=_models.AboutGetRequestQuery(fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_user_info: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/about"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_user_info")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_user_info", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_user_info",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: accessproposals
@mcp.tool()
async def get_access_proposal(
    file_id: str = Field(..., alias="fileId", description="The unique identifier of the file or item associated with the access proposal."),
    proposal_id: str = Field(..., alias="proposalId", description="The unique identifier of the access proposal to retrieve."),
) -> dict[str, Any]:
    """Retrieves a specific access proposal for a file by its ID. Use this to check the status and details of pending access requests."""

    # Construct request model with validation
    try:
        _request = _models.AccessproposalsGetRequest(
            path=_models.AccessproposalsGetRequestPath(file_id=file_id, proposal_id=proposal_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_access_proposal: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{fileId}/accessproposals/{proposalId}", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{fileId}/accessproposals/{proposalId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_access_proposal")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_access_proposal", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_access_proposal",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: accessproposals
@mcp.tool()
async def list_access_proposals(
    file_id: str = Field(..., alias="fileId", description="The unique identifier of the file for which to list access proposals."),
    page_size: int | None = Field(None, alias="pageSize", description="The maximum number of access proposals to return per page. Defaults to a server-defined limit if not specified."),
    page_token: str | None = Field(None, alias="pageToken", description="A continuation token from a previous paginated response to retrieve the next set of results."),
) -> dict[str, Any]:
    """Retrieve pending access proposals for a file. Only users with approver permissions can list access proposals; other users will receive a 403 error."""

    # Construct request model with validation
    try:
        _request = _models.AccessproposalsListRequest(
            path=_models.AccessproposalsListRequestPath(file_id=file_id),
            query=_models.AccessproposalsListRequestQuery(page_size=page_size, page_token=page_token)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_access_proposals: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{fileId}/accessproposals", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{fileId}/accessproposals"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_access_proposals")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_access_proposals", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_access_proposals",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: accessproposals
@mcp.tool()
async def resolve_access_proposal(
    file_id: str = Field(..., alias="fileId", description="The ID of the file associated with the access proposal."),
    proposal_id: str = Field(..., alias="proposalId", description="The ID of the access proposal to resolve."),
    action: Literal["ACTION_UNSPECIFIED", "ACCEPT", "DENY"] | None = Field(None, description="The action to take on the access proposal: accept to grant access, deny to reject it, or unspecified for no action."),
    role: list[str] | None = Field(None, description="The roles to grant the requester when accepting the proposal. Required when action is ACCEPT. Specify as an array of role identifiers."),
    send_notification: bool | None = Field(None, alias="sendNotification", description="Whether to send an email notification to the requester when the proposal is accepted or denied."),
    view: str | None = Field(None, description="The view context for this proposal, if it belongs to a view. Only the published view is supported."),
) -> dict[str, Any]:
    """Approves or denies a pending access proposal for a file. The approver can specify allowed roles when accepting and optionally notify the requester of the decision."""

    # Construct request model with validation
    try:
        _request = _models.AccessproposalsResolveRequest(
            path=_models.AccessproposalsResolveRequestPath(file_id=file_id, proposal_id=proposal_id),
            body=_models.AccessproposalsResolveRequestBody(action=action, role=role, send_notification=send_notification, view=view)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for resolve_access_proposal: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{fileId}/accessproposals/{proposalId}:resolve", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{fileId}/accessproposals/{proposalId}:resolve"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("resolve_access_proposal")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("resolve_access_proposal", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="resolve_access_proposal",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: approvals
@mcp.tool()
async def get_approval(
    file_id: str = Field(..., alias="fileId", description="The unique identifier of the file containing the approval."),
    approval_id: str = Field(..., alias="approvalId", description="The unique identifier of the approval to retrieve."),
) -> dict[str, Any]:
    """Retrieves a specific approval by its ID from a file. Use this to fetch details about an approval request or decision."""

    # Construct request model with validation
    try:
        _request = _models.ApprovalsGetRequest(
            path=_models.ApprovalsGetRequestPath(file_id=file_id, approval_id=approval_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_approval: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{fileId}/approvals/{approvalId}", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{fileId}/approvals/{approvalId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_approval")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_approval", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_approval",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: approvals
@mcp.tool()
async def list_approvals(
    file_id: str = Field(..., alias="fileId", description="The unique identifier of the file for which to retrieve approvals."),
    page_size: int | None = Field(None, alias="pageSize", description="The maximum number of approvals to return per page. Defaults to 100 if not specified."),
    page_token: str | None = Field(None, alias="pageToken", description="A pagination token from a previous response's nextPageToken field to retrieve the next page of results."),
) -> dict[str, Any]:
    """Retrieves a paginated list of approvals associated with a specific file. Use pagination parameters to control result size and navigate through multiple pages."""

    # Construct request model with validation
    try:
        _request = _models.ApprovalsListRequest(
            path=_models.ApprovalsListRequestPath(file_id=file_id),
            query=_models.ApprovalsListRequestQuery(page_size=page_size, page_token=page_token)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_approvals: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{fileId}/approvals", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{fileId}/approvals"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_approvals")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_approvals", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_approvals",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: changes
@mcp.tool()
async def get_change_start_page_token() -> dict[str, Any]:
    """Retrieves the starting page token for listing future changes in Google Drive. Use this token to begin monitoring changes that occur after the current moment."""

    # Extract parameters for API call
    _http_path = "/changes/startPageToken"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_change_start_page_token")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_change_start_page_token", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_change_start_page_token",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: changes
@mcp.tool()
async def list_changes(
    page_token: str = Field(..., alias="pageToken", description="Pagination token from the previous response's nextPageToken field or from getStartPageToken to continue listing changes on the next page."),
    include_corpus_removals: bool | None = Field(None, alias="includeCorpusRemovals", description="Include the file resource in results even when removed from the changes list, provided the file remains accessible to the user at request time."),
    include_items_from_all_drives: bool | None = Field(None, alias="includeItemsFromAllDrives", description="Include changes from both My Drive and shared drives in the results."),
    include_labels: str | None = Field(None, alias="includeLabels", description="Comma-separated list of label IDs to include detailed label information in the response."),
    include_permissions_for_view: str | None = Field(None, alias="includePermissionsForView", description="Specifies which additional view's permissions to include in the response."),
    include_removed: bool | None = Field(None, alias="includeRemoved", description="Include change entries indicating items have been removed, such as through deletion or loss of access."),
    page_size: int | None = Field(None, alias="pageSize", description="Maximum number of changes to return per page.", ge=1, le=1000),
    restrict_to_my_drive: bool | None = Field(None, alias="restrictToMyDrive", description="Restrict results to changes within the My Drive hierarchy, excluding changes to application data or shared files not added to My Drive."),
) -> dict[str, Any]:
    """Retrieves a list of changes for a user's My Drive or shared drive, enabling tracking of file modifications, deletions, and access changes. Use page tokens to iterate through results."""

    # Construct request model with validation
    try:
        _request = _models.ChangesListRequest(
            query=_models.ChangesListRequestQuery(page_token=page_token, include_corpus_removals=include_corpus_removals, include_items_from_all_drives=include_items_from_all_drives, include_labels=include_labels, include_permissions_for_view=include_permissions_for_view, include_removed=include_removed, page_size=page_size, restrict_to_my_drive=restrict_to_my_drive)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_changes: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/changes"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_changes")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_changes", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_changes",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: comments
@mcp.tool()
async def list_comments(
    file_id: str = Field(..., alias="fileId", description="The unique identifier of the file whose comments should be retrieved."),
    include_deleted: bool | None = Field(None, alias="includeDeleted", description="Whether to include deleted comments in the results. Deleted comments will not contain their original content."),
    page_size: int | None = Field(None, alias="pageSize", description="The maximum number of comments to return in a single page of results.", ge=1, le=100),
    page_token: str | None = Field(None, alias="pageToken", description="A pagination token from a previous response's `nextPageToken` field to retrieve the next page of results."),
    start_modified_time: str | None = Field(None, alias="startModifiedTime", description="Filter results to only include comments modified on or after this timestamp, specified in RFC 3339 date-time format."),
    fields: str | None = Field(None, description="Selector specifying which fields to include in a partial response."),
) -> dict[str, Any]:
    """Retrieves all comments on a file, with options to filter by modification time and include deleted comments. The `fields` parameter must be specified to define which comment fields to return."""

    # Construct request model with validation
    try:
        _request = _models.CommentsListRequest(
            path=_models.CommentsListRequestPath(file_id=file_id),
            query=_models.CommentsListRequestQuery(include_deleted=include_deleted, page_size=page_size, page_token=page_token, start_modified_time=start_modified_time, fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_comments: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{fileId}/comments", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{fileId}/comments"
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

# Tags: comments
@mcp.tool()
async def create_comment(
    file_id: str = Field(..., alias="fileId", description="The unique identifier of the file on which to create the comment."),
    fields: str | None = Field(None, description="Selector specifying which fields to include in a partial response."),
    content: str | None = Field(None, description="The plain text content of the comment. HTML content will be generated from this plain text for display purposes."),
    anchor_start_index: int | None = Field(None, description="The start index of the anchor region in the document"),
    anchor_end_index: int | None = Field(None, description="The end index of the anchor region in the document"),
) -> dict[str, Any]:
    """Creates a comment on a file in Google Drive. The `fields` parameter must be set to specify which fields to return in the response."""

    # Call helper functions
    anchor = build_anchor(anchor_start_index, anchor_end_index)

    # Construct request model with validation
    try:
        _request = _models.CommentsCreateRequest(
            path=_models.CommentsCreateRequestPath(file_id=file_id),
            query=_models.CommentsCreateRequestQuery(fields=fields),
            body=_models.CommentsCreateRequestBody(content=content, anchor=anchor)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{fileId}/comments", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{fileId}/comments"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
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
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: comments
@mcp.tool()
async def get_comment(
    file_id: str = Field(..., alias="fileId", description="The unique identifier of the file containing the comment."),
    comment_id: str = Field(..., alias="commentId", description="The unique identifier of the comment to retrieve."),
    include_deleted: bool | None = Field(None, alias="includeDeleted", description="Whether to include deleted comments in the response. Deleted comments will be returned without their original content."),
    fields: str | None = Field(None, description="Selector specifying which fields to include in a partial response."),
) -> dict[str, Any]:
    """Retrieves a specific comment from a file by its ID. Supports optional retrieval of deleted comments, which will have their original content removed."""

    # Construct request model with validation
    try:
        _request = _models.CommentsGetRequest(
            path=_models.CommentsGetRequestPath(file_id=file_id, comment_id=comment_id),
            query=_models.CommentsGetRequestQuery(include_deleted=include_deleted, fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{fileId}/comments/{commentId}", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{fileId}/comments/{commentId}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
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
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: comments
@mcp.tool()
async def update_comment(
    file_id: str = Field(..., alias="fileId", description="The unique identifier of the file containing the comment to update."),
    comment_id: str = Field(..., alias="commentId", description="The unique identifier of the comment to update."),
    fields: str | None = Field(None, description="Selector specifying which fields to include in a partial response."),
    content: str | None = Field(None, description="The plain text content to set for the comment. This field updates the comment's text content."),
    anchor_start_index: int | None = Field(None, description="The start index of the anchor region in the document"),
    anchor_end_index: int | None = Field(None, description="The end index of the anchor region in the document"),
) -> dict[str, Any]:
    """Updates an existing comment in a file using patch semantics, allowing you to modify the comment's content. The `fields` parameter must be set to specify which fields to return in the response."""

    # Call helper functions
    anchor = build_anchor(anchor_start_index, anchor_end_index)

    # Construct request model with validation
    try:
        _request = _models.CommentsUpdateRequest(
            path=_models.CommentsUpdateRequestPath(file_id=file_id, comment_id=comment_id),
            query=_models.CommentsUpdateRequestQuery(fields=fields),
            body=_models.CommentsUpdateRequestBody(content=content, anchor=anchor)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{fileId}/comments/{commentId}", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{fileId}/comments/{commentId}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_comment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_comment", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_comment",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: comments
@mcp.tool()
async def delete_comment(
    file_id: str = Field(..., alias="fileId", description="The unique identifier of the file containing the comment to delete."),
    comment_id: str = Field(..., alias="commentId", description="The unique identifier of the comment to delete."),
    fields: str | None = Field(None, description="Selector specifying which fields to include in a partial response."),
) -> dict[str, Any]:
    """Deletes a comment from a file. The comment and all associated replies will be permanently removed."""

    # Construct request model with validation
    try:
        _request = _models.CommentsDeleteRequest(
            path=_models.CommentsDeleteRequestPath(file_id=file_id, comment_id=comment_id),
            query=_models.CommentsDeleteRequestQuery(fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{fileId}/comments/{commentId}", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{fileId}/comments/{commentId}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
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
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: drives
@mcp.tool()
async def list_shared_drives(
    page_size: int | None = Field(None, alias="pageSize", description="Maximum number of shared drives to return in a single page of results. Useful for controlling response size and implementing pagination.", ge=1, le=100),
    page_token: str | None = Field(None, alias="pageToken", description="Token for retrieving the next page of results. Use the pageToken from the previous response to continue pagination."),
    q: str | None = Field(None, description="Search query to filter shared drives by name, description, or other attributes. Supports combining multiple search terms for refined results."),
    use_domain_admin_access: bool | None = Field(None, alias="useDomainAdminAccess", description="When set to true, issues the request with domain administrator privileges to retrieve all shared drives within the administrator's domain, rather than only user-accessible drives."),
) -> dict[str, Any]:
    """Retrieves a list of shared drives accessible to the user, with optional filtering by search query and pagination support. Domain administrators can retrieve all shared drives within their domain by setting useDomainAdminAccess to true."""

    # Construct request model with validation
    try:
        _request = _models.DrivesListRequest(
            query=_models.DrivesListRequestQuery(page_size=page_size, page_token=page_token, q=q, use_domain_admin_access=use_domain_admin_access)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_shared_drives: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/drives"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_shared_drives")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_shared_drives", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_shared_drives",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: drives
@mcp.tool()
async def create_shared_drive(
    request_id: str = Field(..., alias="requestId", description="A unique identifier (such as a UUID) that ensures idempotent creation. If the same requestId is used in a repeated request, the operation will not create a duplicate shared drive; instead, it will return a 409 error if the drive already exists."),
    color_rgb: str | None = Field(None, alias="colorRgb", description="The color of the shared drive as an RGB hex string. Can only be set when themeId is not specified."),
    hidden: bool | None = Field(None, description="Whether the shared drive should be hidden from the default view in the user interface."),
    name: str | None = Field(None, description="The display name of the shared drive."),
    admin_managed_restrictions: bool | None = Field(None, alias="adminManagedRestrictions", description="Whether administrative privileges are required to modify restrictions on this shared drive."),
    copy_requires_writer_permission: bool | None = Field(None, alias="copyRequiresWriterPermission", description="Whether copying, printing, and downloading files inside this shared drive should be disabled for readers and commenters. When enabled, this overrides the same restriction setting for individual files within the drive."),
    domain_users_only: bool | None = Field(None, alias="domainUsersOnly", description="Whether access to this shared drive and its contents is restricted to users of the domain that owns the drive. Other sharing policies outside this drive may override this restriction."),
    drive_members_only: bool | None = Field(None, alias="driveMembersOnly", description="Whether access to items inside this shared drive is restricted exclusively to its members."),
    sharing_folders_requires_organizer_permission: bool | None = Field(None, alias="sharingFoldersRequiresOrganizerPermission", description="Whether only users with the organizer role can share folders. If false, both organizer and file organizer roles can share folders."),
    theme_id: str | None = Field(None, alias="themeId", description="The ID of a predefined theme that sets the background image and color for the shared drive. Available themes can be retrieved from the drive.about.get endpoint. Cannot be used together with colorRgb or backgroundImageFile."),
) -> dict[str, Any]:
    """Creates a new shared drive with specified configuration and access restrictions. Use a unique requestId to ensure idempotent creation and avoid duplicates."""

    # Construct request model with validation
    try:
        _request = _models.DrivesCreateRequest(
            query=_models.DrivesCreateRequestQuery(request_id=request_id),
            body=_models.DrivesCreateRequestBody(color_rgb=color_rgb, hidden=hidden, name=name, theme_id=theme_id,
                restrictions=_models.DrivesCreateRequestBodyRestrictions(admin_managed_restrictions=admin_managed_restrictions, copy_requires_writer_permission=copy_requires_writer_permission, domain_users_only=domain_users_only, drive_members_only=drive_members_only, sharing_folders_requires_organizer_permission=sharing_folders_requires_organizer_permission) if any(v is not None for v in [admin_managed_restrictions, copy_requires_writer_permission, domain_users_only, drive_members_only, sharing_folders_requires_organizer_permission]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_shared_drive: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/drives"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_shared_drive")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_shared_drive", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_shared_drive",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: drives
@mcp.tool()
async def get_shared_drive(
    drive_id: str = Field(..., alias="driveId", description="The unique identifier of the shared drive to retrieve."),
    use_domain_admin_access: bool | None = Field(None, alias="useDomainAdminAccess", description="If true, issues the request with domain administrator privileges, allowing access to shared drives within your domain even if you're not a direct member."),
) -> dict[str, Any]:
    """Retrieves metadata for a shared drive by its ID. Use domain administrator access to retrieve drives belonging to your organization's domain."""

    # Construct request model with validation
    try:
        _request = _models.DrivesGetRequest(
            path=_models.DrivesGetRequestPath(drive_id=drive_id),
            query=_models.DrivesGetRequestQuery(use_domain_admin_access=use_domain_admin_access)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_shared_drive: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/drives/{driveId}", _request.path.model_dump(by_alias=True)) if _request.path else "/drives/{driveId}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_shared_drive")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_shared_drive", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_shared_drive",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: drives
@mcp.tool()
async def update_shared_drive(
    drive_id: str = Field(..., alias="driveId", description="The unique identifier of the shared drive to update."),
    use_domain_admin_access: bool | None = Field(None, alias="useDomainAdminAccess", description="If true, allows a domain administrator to update the shared drive even if they are not a member, provided they administer the domain to which the shared drive belongs."),
    id_: str | None = Field(None, alias="id", description="The ID of an image file stored in Google Drive to set as the shared drive's background image. The image must be accessible to the requester."),
    color_rgb: str | None = Field(None, alias="colorRgb", description="The color of the shared drive as a hexadecimal RGB value. Cannot be used together with themeId in the same request."),
    hidden: bool | None = Field(None, description="If true, hides the shared drive from the default view in Google Drive, though it remains accessible via direct links and search."),
    name: str | None = Field(None, description="The display name of the shared drive. This is the name visible to all members."),
    admin_managed_restrictions: bool | None = Field(None, alias="adminManagedRestrictions", description="If true, only administrators of the shared drive can modify access restrictions and other administrative settings."),
    copy_requires_writer_permission: bool | None = Field(None, alias="copyRequiresWriterPermission", description="If true, disables copy, print, and download options for readers and commenters on all files within the shared drive. This restriction overrides file-level settings."),
    domain_users_only: bool | None = Field(None, alias="domainUsersOnly", description="If true, restricts access to the shared drive and all its contents to users belonging to the same domain as the shared drive. Other sharing policies may override this restriction."),
    drive_members_only: bool | None = Field(None, alias="driveMembersOnly", description="If true, restricts access to items within the shared drive to its members only, preventing external sharing."),
    sharing_folders_requires_organizer_permission: bool | None = Field(None, alias="sharingFoldersRequiresOrganizerPermission", description="If true, only users with the organizer role can share folders within the shared drive. If false, both organizer and file organizer roles can share folders."),
    theme_id: str | None = Field(None, alias="themeId", description="The ID of a predefined theme to apply to the shared drive, which sets both the background image and color. Available themes can be retrieved from the drive.about.get endpoint. This is a write-only field and cannot be used together with colorRgb or backgroundImageFile in the same request."),
) -> dict[str, Any]:
    """Updates the metadata and settings for a shared drive, including name, appearance, visibility, and access restrictions. Requires the shared drive ID and appropriate permissions to modify the specified properties."""

    # Construct request model with validation
    try:
        _request = _models.DrivesUpdateRequest(
            path=_models.DrivesUpdateRequestPath(drive_id=drive_id),
            query=_models.DrivesUpdateRequestQuery(use_domain_admin_access=use_domain_admin_access),
            body=_models.DrivesUpdateRequestBody(color_rgb=color_rgb, hidden=hidden, name=name, theme_id=theme_id,
                background_image_file=_models.DrivesUpdateRequestBodyBackgroundImageFile(id_=id_) if any(v is not None for v in [id_]) else None,
                restrictions=_models.DrivesUpdateRequestBodyRestrictions(admin_managed_restrictions=admin_managed_restrictions, copy_requires_writer_permission=copy_requires_writer_permission, domain_users_only=domain_users_only, drive_members_only=drive_members_only, sharing_folders_requires_organizer_permission=sharing_folders_requires_organizer_permission) if any(v is not None for v in [admin_managed_restrictions, copy_requires_writer_permission, domain_users_only, drive_members_only, sharing_folders_requires_organizer_permission]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_shared_drive: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/drives/{driveId}", _request.path.model_dump(by_alias=True)) if _request.path else "/drives/{driveId}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_shared_drive")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_shared_drive", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_shared_drive",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: drives
@mcp.tool()
async def delete_shared_drive(
    drive_id: str = Field(..., alias="driveId", description="The unique identifier of the shared drive to delete."),
    allow_item_deletion: bool | None = Field(None, alias="allowItemDeletion", description="Whether to automatically delete all items contained within the shared drive. This option requires domain admin access to be enabled and is only applicable when the requester has domain administrator privileges."),
    use_domain_admin_access: bool | None = Field(None, alias="useDomainAdminAccess", description="Whether to issue the request with domain administrator privileges. When enabled, the requester must be an administrator of the domain to which the shared drive belongs, granting access to perform administrative operations."),
) -> dict[str, Any]:
    """Permanently deletes a shared drive for which the user is an organizer. The shared drive must not contain any untrashed items unless item deletion is explicitly enabled with domain admin access."""

    # Construct request model with validation
    try:
        _request = _models.DrivesDeleteRequest(
            path=_models.DrivesDeleteRequestPath(drive_id=drive_id),
            query=_models.DrivesDeleteRequestQuery(allow_item_deletion=allow_item_deletion, use_domain_admin_access=use_domain_admin_access)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_shared_drive: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/drives/{driveId}", _request.path.model_dump(by_alias=True)) if _request.path else "/drives/{driveId}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_shared_drive")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_shared_drive", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_shared_drive",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: drives
@mcp.tool()
async def hide_shared_drive(drive_id: str = Field(..., alias="driveId", description="The unique identifier of the shared drive to hide.")) -> dict[str, Any]:
    """Hides a shared drive from the default view, removing it from the user's primary shared drive list. The drive remains accessible but is no longer displayed in standard navigation."""

    # Construct request model with validation
    try:
        _request = _models.DrivesHideRequest(
            path=_models.DrivesHideRequestPath(drive_id=drive_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for hide_shared_drive: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/drives/{driveId}/hide", _request.path.model_dump(by_alias=True)) if _request.path else "/drives/{driveId}/hide"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("hide_shared_drive")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("hide_shared_drive", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="hide_shared_drive",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: drives
@mcp.tool()
async def unhide_shared_drive(drive_id: str = Field(..., alias="driveId", description="The unique identifier of the shared drive to restore to the default view.")) -> dict[str, Any]:
    """Restores a shared drive to the default view, making it visible in the shared drives list. Use this operation to unhide a shared drive that was previously hidden from view."""

    # Construct request model with validation
    try:
        _request = _models.DrivesUnhideRequest(
            path=_models.DrivesUnhideRequestPath(drive_id=drive_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for unhide_shared_drive: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/drives/{driveId}/unhide", _request.path.model_dump(by_alias=True)) if _request.path else "/drives/{driveId}/unhide"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("unhide_shared_drive")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("unhide_shared_drive", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="unhide_shared_drive",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: files
@mcp.tool()
async def copy_file(
    file_id: str = Field(..., alias="fileId", description="The unique identifier of the file to copy."),
    ignore_default_visibility: bool | None = Field(None, alias="ignoreDefaultVisibility", description="Whether to bypass the domain's default visibility settings for the copied file. When enabled, the file's visibility is not automatically set to domain-wide visibility, though parent folder permissions are still inherited."),
    include_labels: str | None = Field(None, alias="includeLabels", description="A comma-separated list of label IDs to include in the labelInfo section of the response."),
    include_permissions_for_view: str | None = Field(None, alias="includePermissionsForView", description="Specifies which additional view's permissions to include in the response. Only the published view is currently supported."),
    keep_revision_forever: bool | None = Field(None, alias="keepRevisionForever", description="Whether to mark the new head revision to be kept forever. Only applicable to files with binary content. A maximum of 200 revisions per file can be kept permanently; delete pinned revisions if this limit is reached."),
    ocr_language: str | None = Field(None, alias="ocrLanguage", description="A language hint for OCR processing during image import, specified as an ISO 639-1 language code."),
    app_properties: dict[str, str] | None = Field(None, alias="appProperties", description="Custom key-value pairs private to the requesting application. Entries with null values are cleared during copy operations. Requires OAuth 2 authentication to retrieve; API keys cannot access private properties."),
    indexable_text: str | None = Field(None, alias="indexableText", description="Text content to be indexed for improved fullText search results. Limited to 128 KB and may contain HTML elements."),
    image: str | None = Field(None, description="The thumbnail image data encoded using URL-safe Base64 format."),
    thumbnail_mime_type: str | None = Field(None, alias="thumbnailMimeType", description="The MIME type of the thumbnail image."),
    mime_type: str | None = Field(None, alias="mimeType", description="The MIME type of the file. Google Drive automatically detects an appropriate MIME type from uploaded content if not provided. The value cannot be changed unless a new revision is uploaded. Files created with Google Doc MIME types have their content imported if supported."),
    content_restrictions: list[_models.ContentRestriction] | None = Field(None, alias="contentRestrictions", description="Restrictions applied to file content access. Only populated when content restrictions are in effect."),
    copy_requires_writer_permission: bool | None = Field(None, alias="copyRequiresWriterPermission", description="Whether copying, printing, and downloading options are disabled for readers and commenters."),
    description: str | None = Field(None, description="A brief description or summary of the file's contents."),
    restricted_for_readers: bool | None = Field(None, alias="restrictedForReaders", description="Whether download and copy operations are restricted for readers."),
    restricted_for_writers: bool | None = Field(None, alias="restrictedForWriters", description="Whether download and copy operations are restricted for writers. When enabled, download is also restricted for readers."),
    folder_color_rgb: str | None = Field(None, alias="folderColorRgb", description="The color for a folder or folder shortcut as an RGB hex string. Supported colors are published in the folderColorPalette field of the about resource; unsupported colors are replaced with the closest available color."),
    inherited_permissions_disabled: bool | None = Field(None, alias="inheritedPermissionsDisabled", description="Whether inherited permissions are disabled for this file. Inherited permissions are enabled by default."),
    name: str | None = Field(None, description="The display name of the file. Not necessarily unique within a folder. For immutable items like shared drive roots and system folders, the name is constant."),
    parents: list[str] | None = Field(None, description="The ID of the parent folder containing the copied file. A file can have only one parent folder. If not specified, the file inherits the discoverable parent of the source file or is placed in the user's My Drive."),
    properties: dict[str, str] | None = Field(None, description="Custom key-value pairs visible to all applications. Entries with null values are cleared during copy operations."),
    target_id: str | None = Field(None, alias="targetId", description="The ID of the file that this shortcut points to. Only applicable to shortcut creation requests."),
    starred: bool | None = Field(None, description="Whether the file is marked as starred by the user."),
    trashed: bool | None = Field(None, description="Whether the file is in the trash, either directly or through a trashed parent folder. Only the file owner can trash files; other users cannot view files in the owner's trash."),
    writers_can_share: bool | None = Field(None, alias="writersCanShare", description="Whether users with writer-only permission can modify the file's sharing permissions. Not applicable to files in shared drives."),
    video_dimensions: str | None = Field(None, description="Video dimensions in WIDTHxHEIGHT format (e.g., '1920x1080')"),
) -> dict[str, Any]:
    """Creates a copy of a file with optional updates applied using patch semantics. The copied file inherits permissions from its parent folder unless otherwise specified."""

    # Call helper functions
    video_dimensions_parsed = parse_video_dimensions(video_dimensions)

    # Construct request model with validation
    try:
        _request = _models.FilesCopyRequest(
            path=_models.FilesCopyRequestPath(file_id=file_id),
            query=_models.FilesCopyRequestQuery(ignore_default_visibility=ignore_default_visibility, include_labels=include_labels, include_permissions_for_view=include_permissions_for_view, keep_revision_forever=keep_revision_forever, ocr_language=ocr_language),
            body=_models.FilesCopyRequestBody(app_properties=app_properties, mime_type=mime_type, content_restrictions=content_restrictions, copy_requires_writer_permission=copy_requires_writer_permission, description=description, folder_color_rgb=folder_color_rgb, inherited_permissions_disabled=inherited_permissions_disabled, name=name, parents=parents, properties=properties, starred=starred, trashed=trashed, writers_can_share=writers_can_share,
                content_hints=_models.FilesCopyRequestBodyContentHints(indexable_text=indexable_text,
                    thumbnail=_models.FilesCopyRequestBodyContentHintsThumbnail(image=image, mime_type=thumbnail_mime_type) if any(v is not None for v in [image, thumbnail_mime_type]) else None) if any(v is not None for v in [indexable_text, image, thumbnail_mime_type]) else None,
                download_restrictions=_models.FilesCopyRequestBodyDownloadRestrictions(item_download_restriction=_models.FilesCopyRequestBodyDownloadRestrictionsItemDownloadRestriction(restricted_for_readers=restricted_for_readers, restricted_for_writers=restricted_for_writers) if any(v is not None for v in [restricted_for_readers, restricted_for_writers]) else None) if any(v is not None for v in [restricted_for_readers, restricted_for_writers]) else None,
                shortcut_details=_models.FilesCopyRequestBodyShortcutDetails(target_id=target_id) if any(v is not None for v in [target_id]) else None,
                video_media_metadata=_models.FilesCopyRequestBodyVideoMediaMetadata(width=video_dimensions_parsed.get('width') if video_dimensions_parsed else None, height=video_dimensions_parsed.get('height') if video_dimensions_parsed else None) if any(v is not None for v in [video_dimensions_parsed.get('width') if video_dimensions_parsed else None, video_dimensions_parsed.get('height') if video_dimensions_parsed else None]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for copy_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{fileId}/copy", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{fileId}/copy"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("copy_file")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("copy_file", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="copy_file",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: files
@mcp.tool()
async def list_files(
    include_items_from_all_drives: bool | None = Field(None, alias="includeItemsFromAllDrives", description="Whether to include items from both My Drive and shared drives in the results."),
    include_labels: str | None = Field(None, alias="includeLabels", description="A comma-separated list of label IDs to include detailed label information in the response."),
    include_permissions_for_view: str | None = Field(None, alias="includePermissionsForView", description="Specifies which additional view's permissions to include in the response."),
    order_by: str | None = Field(None, alias="orderBy", description="A comma-separated list of sort keys to order results. Each key sorts ascending by default; append 'desc' to reverse order. Valid keys include createdTime, folder, modifiedByMeTime, modifiedTime, name, name_natural, quotaBytesUsed, recency, sharedWithMeTime, starred, and viewedByMeTime."),
    page_size: int | None = Field(None, alias="pageSize", description="The maximum number of files to return per page. Partial or empty result pages may be returned before reaching the end of the file list.", ge=1, le=1000),
    page_token: str | None = Field(None, alias="pageToken", description="The pagination token from a previous response's nextPageToken field to retrieve the next page of results."),
    q: str | None = Field(None, description="A search query to filter file results using supported search syntax for files and folders."),
) -> dict[str, Any]:
    """Retrieves a list of the user's files with support for searching, filtering, and sorting. By default, all files including trashed items are returned; use the trashed parameter to exclude deleted files."""

    # Construct request model with validation
    try:
        _request = _models.FilesListRequest(
            query=_models.FilesListRequestQuery(include_items_from_all_drives=include_items_from_all_drives, include_labels=include_labels, include_permissions_for_view=include_permissions_for_view, order_by=order_by, page_size=page_size, page_token=page_token, q=q)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_files: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/files"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_files")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_files", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_files",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: files
@mcp.tool()
async def create_file(
    ignore_default_visibility: bool | None = Field(None, alias="ignoreDefaultVisibility", description="Bypass the domain's default visibility settings for this file. When enabled, the file's visibility is not automatically set to domain-wide; permissions are still inherited from parent folders."),
    include_labels: str | None = Field(None, alias="includeLabels", description="Comma-separated list of label IDs to include in the response's labelInfo section."),
    include_permissions_for_view: str | None = Field(None, alias="includePermissionsForView", description="Include additional view permissions in the response. Currently only 'published' is supported."),
    keep_revision_forever: bool | None = Field(None, alias="keepRevisionForever", description="Preserve the current file revision indefinitely. Only applicable to files with binary content; limited to 200 pinned revisions per file."),
    ocr_language: str | None = Field(None, alias="ocrLanguage", description="Language hint for optical character recognition during image import, specified as an ISO 639-1 language code."),
    use_content_as_indexable_text: bool | None = Field(None, alias="useContentAsIndexableText", description="Use the uploaded file content as searchable indexable text to improve full-text query results."),
    app_properties: dict[str, str] | None = Field(None, alias="appProperties", description="Custom key-value pairs private to your application. Entries with null values are removed during updates. Requires OAuth 2 authentication to retrieve."),
    indexable_text: str | None = Field(None, alias="indexableText", description="Text content to index for improved full-text search results. Limited to 128 KB and may contain HTML elements."),
    image: str | None = Field(None, description="Thumbnail image data encoded as URL-safe Base64."),
    thumbnail_mime_type: str | None = Field(None, alias="thumbnailMimeType", description="MIME type of the thumbnail image."),
    mime_type: str | None = Field(None, alias="mimeType", description="MIME type of the file. Google Drive automatically detects an appropriate type from uploaded content if not specified. Cannot be changed unless a new revision is uploaded. Google Docs MIME types trigger content import if supported."),
    content_restrictions: list[_models.ContentRestriction] | None = Field(None, alias="contentRestrictions", description="Content access restrictions applied to the file. Only populated if restrictions exist."),
    copy_requires_writer_permission: bool | None = Field(None, alias="copyRequiresWriterPermission", description="Disable copy, print, and download options for readers and commenters."),
    description: str | None = Field(None, description="Brief description or summary of the file's contents."),
    restricted_for_readers: bool | None = Field(None, alias="restrictedForReaders", description="Restrict download and copy access for readers."),
    restricted_for_writers: bool | None = Field(None, alias="restrictedForWriters", description="Restrict download and copy access for writers. When enabled, download is also restricted for readers."),
    folder_color_rgb: str | None = Field(None, alias="folderColorRgb", description="RGB hex color code for folder or folder shortcut appearance. Supported colors are available in the about resource's folderColorPalette; unsupported colors default to the closest available option."),
    image_media_metadata_height: str | None = Field(None, alias="imageMediaMetadataHeight", description="Height of the image in pixels."),
    video_media_metadata_height: str | None = Field(None, alias="videoMediaMetadataHeight", description="Height of the video in pixels."),
    image_media_metadata_width: str | None = Field(None, alias="imageMediaMetadataWidth", description="Width of the image in pixels."),
    video_media_metadata_width: str | None = Field(None, alias="videoMediaMetadataWidth", description="Width of the video in pixels."),
    inherited_permissions_disabled: bool | None = Field(None, alias="inheritedPermissionsDisabled", description="Disable inherited permissions for this file. By default, files inherit permissions from their parent folder."),
    name: str | None = Field(None, description="Display name of the file. Not required to be unique within a folder. For immutable items like shared drive roots, this value is constant."),
    parents: list[str] | None = Field(None, description="ID of the parent folder containing the file. A file can have only one parent. If omitted during creation, the file is placed in the user's My Drive root folder."),
    properties: dict[str, str] | None = Field(None, description="Custom key-value pairs visible to all applications. Entries with null values are removed during updates."),
    target_id: str | None = Field(None, alias="targetId", description="ID of the file this shortcut points to. Only applicable when creating shortcuts with MIME type 'application/vnd.google-apps.shortcut'."),
    starred: bool | None = Field(None, description="Mark the file as starred in the user's Drive."),
    trashed: bool | None = Field(None, description="Move the file to trash. Only the file owner can trash files; other users cannot see trashed files in the owner's trash."),
    writers_can_share: bool | None = Field(None, alias="writersCanShare", description="Allow users with writer permission to modify the file's sharing permissions. Not applicable to files in shared drives."),
) -> dict[str, Any]:
    """Creates a new file in Google Drive with optional metadata, content restrictions, and organizational properties. Supports file uploads up to 5,120 GB with any valid MIME type, and allows creation of shortcuts to existing files."""

    _image_media_metadata_height = _parse_int(image_media_metadata_height)
    _video_media_metadata_height = _parse_int(video_media_metadata_height)
    _image_media_metadata_width = _parse_int(image_media_metadata_width)
    _video_media_metadata_width = _parse_int(video_media_metadata_width)

    # Construct request model with validation
    try:
        _request = _models.FilesCreateRequest(
            query=_models.FilesCreateRequestQuery(ignore_default_visibility=ignore_default_visibility, include_labels=include_labels, include_permissions_for_view=include_permissions_for_view, keep_revision_forever=keep_revision_forever, ocr_language=ocr_language, use_content_as_indexable_text=use_content_as_indexable_text),
            body=_models.FilesCreateRequestBody(app_properties=app_properties, mime_type=mime_type, content_restrictions=content_restrictions, copy_requires_writer_permission=copy_requires_writer_permission, description=description, folder_color_rgb=folder_color_rgb, inherited_permissions_disabled=inherited_permissions_disabled, name=name, parents=parents, properties=properties, starred=starred, trashed=trashed, writers_can_share=writers_can_share,
                content_hints=_models.FilesCreateRequestBodyContentHints(indexable_text=indexable_text,
                    thumbnail=_models.FilesCreateRequestBodyContentHintsThumbnail(image=image, mime_type=thumbnail_mime_type) if any(v is not None for v in [image, thumbnail_mime_type]) else None) if any(v is not None for v in [indexable_text, image, thumbnail_mime_type]) else None,
                download_restrictions=_models.FilesCreateRequestBodyDownloadRestrictions(item_download_restriction=_models.FilesCreateRequestBodyDownloadRestrictionsItemDownloadRestriction(restricted_for_readers=restricted_for_readers, restricted_for_writers=restricted_for_writers) if any(v is not None for v in [restricted_for_readers, restricted_for_writers]) else None) if any(v is not None for v in [restricted_for_readers, restricted_for_writers]) else None,
                image_media_metadata=_models.FilesCreateRequestBodyImageMediaMetadata(height=_image_media_metadata_height, width=_image_media_metadata_width) if any(v is not None for v in [image_media_metadata_height, image_media_metadata_width]) else None,
                video_media_metadata=_models.FilesCreateRequestBodyVideoMediaMetadata(height=_video_media_metadata_height, width=_video_media_metadata_width) if any(v is not None for v in [video_media_metadata_height, video_media_metadata_width]) else None,
                shortcut_details=_models.FilesCreateRequestBodyShortcutDetails(target_id=target_id) if any(v is not None for v in [target_id]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/files"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_file")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_file", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_file",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: files
@mcp.tool()
async def get_file(
    file_id: str = Field(..., alias="fileId", description="The unique identifier of the file to retrieve."),
    include_labels: str | None = Field(None, alias="includeLabels", description="Comma-separated list of label IDs to include in the labelInfo section of the response."),
    include_permissions_for_view: str | None = Field(None, alias="includePermissionsForView", description="Specifies which additional view's permissions to include in the response."),
) -> dict[str, Any]:
    """Retrieve a file's metadata or content by ID. Use alt=media to download file contents, or use the export operation for Google Docs, Sheets, and Slides formats."""

    # Construct request model with validation
    try:
        _request = _models.FilesGetRequest(
            path=_models.FilesGetRequestPath(file_id=file_id),
            query=_models.FilesGetRequestQuery(include_labels=include_labels, include_permissions_for_view=include_permissions_for_view)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{fileId}", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{fileId}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_file")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_file", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_file",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: files
@mcp.tool()
async def update_file(
    file_id: str = Field(..., alias="fileId", description="The unique identifier of the file to update."),
    add_parents: str | None = Field(None, alias="addParents", description="Comma-separated list of parent folder IDs to add to the file."),
    include_labels: str | None = Field(None, alias="includeLabels", description="Comma-separated list of label IDs to include in the labelInfo section of the response."),
    include_permissions_for_view: str | None = Field(None, alias="includePermissionsForView", description="Specifies which additional view's permissions to include in the response."),
    keep_revision_forever: bool | None = Field(None, alias="keepRevisionForever", description="Whether to set the keepForever field in the new head revision for binary files. Limited to 200 revisions per file; delete pinned revisions if limit is reached."),
    ocr_language: str | None = Field(None, alias="ocrLanguage", description="Language hint for OCR processing during image import, specified as an ISO 639-1 code."),
    remove_parents: str | None = Field(None, alias="removeParents", description="Comma-separated list of parent folder IDs to remove from the file."),
    use_content_as_indexable_text: bool | None = Field(None, alias="useContentAsIndexableText", description="Whether to use the uploaded content as indexable text for fullText search queries."),
    app_properties: dict[str, str] | None = Field(None, alias="appProperties", description="Arbitrary key-value pairs private to the requesting app. Entries with null values are cleared. Requires OAuth 2 authentication; API keys cannot retrieve private properties."),
    indexable_text: str | None = Field(None, alias="indexableText", description="Text to be indexed for improved fullText search queries. Limited to 128 KB and may contain HTML elements."),
    image: str | None = Field(None, description="Thumbnail data encoded with URL-safe Base64."),
    thumbnail_mime_type: str | None = Field(None, alias="thumbnailMimeType", description="The MIME type of the thumbnail image."),
    mime_type: str | None = Field(None, alias="mimeType", description="The MIME type of the file. Google Drive auto-detects if not provided. Cannot be changed unless a new revision is uploaded. Google Doc MIME types trigger content import if supported."),
    content_restrictions: list[_models.ContentRestriction] | None = Field(None, alias="contentRestrictions", description="Restrictions for accessing the file's content. Only populated if restrictions exist."),
    copy_requires_writer_permission: bool | None = Field(None, alias="copyRequiresWriterPermission", description="Whether copying, printing, or downloading should be disabled for readers and commenters."),
    description: str | None = Field(None, description="A short description of the file's purpose or content."),
    restricted_for_readers: bool | None = Field(None, alias="restrictedForReaders", description="Whether download and copy are restricted for readers."),
    restricted_for_writers: bool | None = Field(None, alias="restrictedForWriters", description="Whether download and copy are restricted for writers. If true, download is also restricted for readers."),
    folder_color_rgb: str | None = Field(None, alias="folderColorRgb", description="The color for a folder or folder shortcut as an RGB hex string. Uses the closest supported color if an unsupported color is specified."),
    inherited_permissions_disabled: bool | None = Field(None, alias="inheritedPermissionsDisabled", description="Whether inherited permissions are disabled for this file. Inherited permissions are enabled by default."),
    name: str | None = Field(None, description="The name of the file. Not necessarily unique within a folder. Immutable for top-level shared drive folders, My Drive root, and Application Data folder."),
    parents: list[str] | None = Field(None, description="The ID of the parent folder containing the file. A file can have only one parent. Use addParents and removeParents parameters to modify the parents list in update requests."),
    properties: dict[str, str] | None = Field(None, description="Arbitrary key-value pairs visible to all apps. Entries with null values are cleared in update requests."),
    target_id: str | None = Field(None, alias="targetId", description="The ID of the file that this shortcut points to. Can only be set during file creation."),
    starred: bool | None = Field(None, description="Whether the user has starred the file."),
    trashed: bool | None = Field(None, description="Whether the file has been trashed, either explicitly or from a trashed parent folder. Only the owner can trash files; other users cannot see files in the owner's trash."),
    writers_can_share: bool | None = Field(None, alias="writersCanShare", description="Whether users with writer permission can modify the file's permissions. Not populated for items in shared drives."),
) -> dict[str, Any]:
    """Updates a file's metadata, content, or both using patch semantics. Only populate fields you want to modify; some fields like modifiedDate are updated automatically. Supports file uploads up to 5,120 GB."""

    # Construct request model with validation
    try:
        _request = _models.FilesUpdateRequest(
            path=_models.FilesUpdateRequestPath(file_id=file_id),
            query=_models.FilesUpdateRequestQuery(add_parents=add_parents, include_labels=include_labels, include_permissions_for_view=include_permissions_for_view, keep_revision_forever=keep_revision_forever, ocr_language=ocr_language, remove_parents=remove_parents, use_content_as_indexable_text=use_content_as_indexable_text),
            body=_models.FilesUpdateRequestBody(app_properties=app_properties, mime_type=mime_type, content_restrictions=content_restrictions, copy_requires_writer_permission=copy_requires_writer_permission, description=description, folder_color_rgb=folder_color_rgb, inherited_permissions_disabled=inherited_permissions_disabled, name=name, parents=parents, properties=properties, starred=starred, trashed=trashed, writers_can_share=writers_can_share,
                content_hints=_models.FilesUpdateRequestBodyContentHints(indexable_text=indexable_text,
                    thumbnail=_models.FilesUpdateRequestBodyContentHintsThumbnail(image=image, mime_type=thumbnail_mime_type) if any(v is not None for v in [image, thumbnail_mime_type]) else None) if any(v is not None for v in [indexable_text, image, thumbnail_mime_type]) else None,
                download_restrictions=_models.FilesUpdateRequestBodyDownloadRestrictions(item_download_restriction=_models.FilesUpdateRequestBodyDownloadRestrictionsItemDownloadRestriction(restricted_for_readers=restricted_for_readers, restricted_for_writers=restricted_for_writers) if any(v is not None for v in [restricted_for_readers, restricted_for_writers]) else None) if any(v is not None for v in [restricted_for_readers, restricted_for_writers]) else None,
                shortcut_details=_models.FilesUpdateRequestBodyShortcutDetails(target_id=target_id) if any(v is not None for v in [target_id]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{fileId}", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{fileId}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_file")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_file", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_file",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: files
@mcp.tool()
async def delete_file(file_id: str = Field(..., alias="fileId", description="The unique identifier of the file to delete.")) -> dict[str, Any]:
    """Permanently deletes a file owned by the user without moving it to trash. If the file is a folder, all descendants owned by the user are also deleted. For shared drives, the user must be an organizer on the parent folder."""

    # Construct request model with validation
    try:
        _request = _models.FilesDeleteRequest(
            path=_models.FilesDeleteRequestPath(file_id=file_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{fileId}", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{fileId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_file")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_file", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_file",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: files
@mcp.tool()
async def download_file(
    file_id: str = Field(..., alias="fileId", description="The unique identifier of the file to download."),
    revision_id: str | None = Field(None, alias="revisionId", description="The specific revision of the file to download. Only applicable for blob files, Google Docs, and Google Sheets. Returns an error if the file type does not support revision-specific downloads."),
) -> dict[str, Any]:
    """Downloads the content of a file from Google Drive. Operations are valid for 24 hours from the time of creation."""

    # Construct request model with validation
    try:
        _request = _models.FilesDownloadRequest(
            path=_models.FilesDownloadRequestPath(file_id=file_id),
            query=_models.FilesDownloadRequestQuery(revision_id=revision_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for download_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{fileId}/download", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{fileId}/download"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("download_file")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("download_file", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="download_file",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: files
@mcp.tool()
async def empty_trash() -> dict[str, Any]:
    """Permanently deletes all of the user's trashed files. This action cannot be undone and will remove all items currently in the trash."""

    # Extract parameters for API call
    _http_path = "/files/trash"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("empty_trash")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("empty_trash", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="empty_trash",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: files
@mcp.tool()
async def export_document(
    file_id: str = Field(..., alias="fileId", description="The unique identifier of the file to export."),
    mime_type: str = Field(..., alias="mimeType", description="The MIME type format for the exported document. Refer to the supported export formats for Google Workspace documents to determine valid MIME types for your file type."),
) -> dict[str, Any]:
    """Exports a Google Workspace document to a specified format and returns the exported content as bytes. The exported content is limited to 10 MB."""

    # Construct request model with validation
    try:
        _request = _models.FilesExportRequest(
            path=_models.FilesExportRequestPath(file_id=file_id),
            query=_models.FilesExportRequestQuery(mime_type=mime_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for export_document: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{fileId}/export", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{fileId}/export"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("export_document")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("export_document", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="export_document",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: files
@mcp.tool()
async def generate_file_ids(
    count: int | None = Field(None, description="The number of file IDs to generate. Must be between 1 and 1000 IDs per request.", ge=1, le=1000),
    space: str | None = Field(None, description="The storage space where generated IDs can be used to create files. Defaults to 'drive' for standard Google Drive storage."),
) -> dict[str, Any]:
    """Generates a batch of file IDs for use in subsequent file creation or copy operations. These pre-generated IDs enable efficient file management workflows in Google Drive or App Data Folder."""

    # Construct request model with validation
    try:
        _request = _models.FilesGenerateIdsRequest(
            query=_models.FilesGenerateIdsRequestQuery(count=count, space=space)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for generate_file_ids: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/files/generateIds"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("generate_file_ids")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("generate_file_ids", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="generate_file_ids",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: files
@mcp.tool()
async def list_file_labels(
    file_id: str = Field(..., alias="fileId", description="The unique identifier of the file whose labels you want to retrieve."),
    max_results: int | None = Field(None, alias="maxResults", description="The maximum number of labels to return in a single page of results. Defaults to 100 if not specified.", ge=1, le=100),
    page_token: str | None = Field(None, alias="pageToken", description="A pagination token from a previous response's nextPageToken field to retrieve the next page of results."),
) -> dict[str, Any]:
    """Retrieves all labels applied to a specific file. Supports pagination to handle large label sets across multiple pages."""

    # Construct request model with validation
    try:
        _request = _models.FilesListLabelsRequest(
            path=_models.FilesListLabelsRequestPath(file_id=file_id),
            query=_models.FilesListLabelsRequestQuery(max_results=max_results, page_token=page_token)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_file_labels: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{fileId}/listLabels", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{fileId}/listLabels"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_file_labels")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_file_labels", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_file_labels",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: files
@mcp.tool()
async def update_file_labels(
    file_id: str = Field(..., alias="fileId", description="The unique identifier of the file whose labels should be modified."),
    label_modifications: list[_models.LabelModification] | None = Field(None, alias="labelModifications", description="An ordered list of label modifications to apply to the file. Each modification specifies a label field and the values to set, add, or remove."),
) -> dict[str, Any]:
    """Updates the labels applied to a file by adding, modifying, or removing label fields. Returns the list of labels that were successfully added or modified."""

    # Construct request model with validation
    try:
        _request = _models.FilesModifyLabelsRequest(
            path=_models.FilesModifyLabelsRequestPath(file_id=file_id),
            body=_models.FilesModifyLabelsRequestBody(label_modifications=label_modifications)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_file_labels: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{fileId}/modifyLabels", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{fileId}/modifyLabels"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_file_labels")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_file_labels", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_file_labels",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: permissions
@mcp.tool()
async def list_file_permissions(
    file_id: str = Field(..., alias="fileId", description="The unique identifier of the file or shared drive whose permissions you want to retrieve."),
    include_permissions_for_view: str | None = Field(None, alias="includePermissionsForView", description="Specifies which additional view's permissions to include in the response. Use 'published' to include permissions for the published view of the file."),
    page_size: int | None = Field(None, alias="pageSize", description="The maximum number of permissions to return per page. For shared drive files, defaults to 100 if not specified; for other files, returns the entire list.", ge=1, le=100),
    page_token: str | None = Field(None, alias="pageToken", description="The pagination token from a previous response's nextPageToken field. Use this to retrieve the next page of results."),
    use_domain_admin_access: bool | None = Field(None, alias="useDomainAdminAccess", description="When set to true, issues the request with domain administrator privileges. Only applicable when the fileId refers to a shared drive and the requester is a domain administrator."),
    fields: str | None = Field(None, description="Selector specifying which fields to include in a partial response."),
) -> dict[str, Any]:
    """Retrieves all permissions for a file or shared drive, including access levels and sharing settings. Supports pagination and optional filtering for published views."""

    # Construct request model with validation
    try:
        _request = _models.PermissionsListRequest(
            path=_models.PermissionsListRequestPath(file_id=file_id),
            query=_models.PermissionsListRequestQuery(include_permissions_for_view=include_permissions_for_view, page_size=page_size, page_token=page_token, use_domain_admin_access=use_domain_admin_access, fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_file_permissions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{fileId}/permissions", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{fileId}/permissions"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_file_permissions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_file_permissions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_file_permissions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: permissions
@mcp.tool()
async def create_file_permission(
    file_id: str = Field(..., alias="fileId", description="The ID of the file or shared drive to which the permission applies."),
    email_message: str | None = Field(None, alias="emailMessage", description="Custom message text to include in the sharing notification email sent to recipients."),
    move_to_new_owners_root: bool | None = Field(None, alias="moveToNewOwnersRoot", description="When transferring ownership of a file outside a shared drive, set to true to move the file to the new owner's root folder and remove all previous parent folders. Set to false to preserve the folder hierarchy."),
    send_notification_email: bool | None = Field(None, alias="sendNotificationEmail", description="Whether to send a notification email to the recipient. Defaults to true for users and groups. Cannot be disabled for ownership transfers."),
    transfer_ownership: bool | None = Field(None, alias="transferOwnership", description="Whether to transfer file ownership to the specified user and downgrade the current owner to a writer role. Required as an acknowledgment of the ownership change side effects."),
    use_domain_admin_access: bool | None = Field(None, alias="useDomainAdminAccess", description="When set to true, issue the request as a domain administrator. Only applicable when the file ID refers to a shared drive and the requester is a domain administrator."),
    allow_file_discovery: bool | None = Field(None, alias="allowFileDiscovery", description="Whether the permission allows the file to be discovered through search results. Only applies to permissions with type domain or anyone."),
    domain: str | None = Field(None, description="The domain name to which this permission applies. Used when granting access to an entire domain."),
    email_address: str | None = Field(None, alias="emailAddress", description="The email address of the user or group receiving this permission."),
    expiration_time: str | None = Field(None, alias="expirationTime", description="The date and time when this permission automatically expires. Must be a future date no more than one year away. Only applicable to user and group permissions."),
    inherited_permissions_disabled: bool | None = Field(None, alias="inheritedPermissionsDisabled", description="When set to true, only organizers, owners, and users with direct permissions can access the item. Inherited permissions from parent folders are disabled."),
    role: str | None = Field(None, description="The access level granted by this permission. Common roles include owner, organizer, fileOrganizer, writer, commenter, and reader."),
    view: str | None = Field(None, description="The view scope for this permission. Published indicates a publishedReader role; metadata indicates the item is visible only in the metadata view with limited access. Metadata view is only supported on folders."),
    type_: str | None = Field(None, alias="type", description="The type of the grantee. Supported values include: * `user` * `group` * `domain` * `anyone` When creating a permission, if `type` is `user` or `group`, you must provide an `emailAddress` for the user or group. If `type` is `domain`, you must provide a `domain`. If `type` is `anyone`, no extra information is required."),
) -> dict[str, Any]:
    """Grants access to a file or shared drive by creating a new permission. Supports sharing with users, groups, domains, or the public, with optional ownership transfer and notification settings."""

    # Construct request model with validation
    try:
        _request = _models.PermissionsCreateRequest(
            path=_models.PermissionsCreateRequestPath(file_id=file_id),
            query=_models.PermissionsCreateRequestQuery(email_message=email_message, move_to_new_owners_root=move_to_new_owners_root, send_notification_email=send_notification_email, transfer_ownership=transfer_ownership, use_domain_admin_access=use_domain_admin_access),
            body=_models.PermissionsCreateRequestBody(allow_file_discovery=allow_file_discovery, domain=domain, email_address=email_address, expiration_time=expiration_time, inherited_permissions_disabled=inherited_permissions_disabled, role=role, view=view, type_=type_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_file_permission: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{fileId}/permissions", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{fileId}/permissions"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_file_permission")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_file_permission", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_file_permission",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: permissions
@mcp.tool()
async def get_permission(
    file_id: str = Field(..., alias="fileId", description="The unique identifier of the file for which you want to retrieve the permission."),
    permission_id: str = Field(..., alias="permissionId", description="The unique identifier of the permission to retrieve."),
    use_domain_admin_access: bool | None = Field(None, alias="useDomainAdminAccess", description="If true, issues the request as a domain administrator, granting access when the file is a shared drive and the requester is an administrator of that shared drive's domain."),
    fields: str | None = Field(None, description="Selector specifying which fields to include in a partial response."),
) -> dict[str, Any]:
    """Retrieves a specific permission for a file by its ID. Use this to inspect sharing settings and access details for a particular file permission."""

    # Construct request model with validation
    try:
        _request = _models.PermissionsGetRequest(
            path=_models.PermissionsGetRequestPath(file_id=file_id, permission_id=permission_id),
            query=_models.PermissionsGetRequestQuery(use_domain_admin_access=use_domain_admin_access, fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_permission: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{fileId}/permissions/{permissionId}", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{fileId}/permissions/{permissionId}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_permission")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_permission", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_permission",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: permissions
@mcp.tool()
async def update_file_permission(
    file_id: str = Field(..., alias="fileId", description="The ID of the file or shared drive containing the permission to update."),
    permission_id: str = Field(..., alias="permissionId", description="The ID of the permission to update."),
    remove_expiration: bool | None = Field(None, alias="removeExpiration", description="Whether to remove the expiration date from this permission."),
    transfer_ownership: bool | None = Field(None, alias="transferOwnership", description="Whether to transfer ownership of the file to the specified user and downgrade the current owner to a writer role. This parameter must be explicitly set to acknowledge the ownership change side effect."),
    use_domain_admin_access: bool | None = Field(None, alias="useDomainAdminAccess", description="Whether to issue this request as a domain administrator. Only applicable when the file ID refers to a shared drive and the requester is an administrator of that domain."),
    fields: str | None = Field(None, description="Selector specifying which fields to include in a partial response."),
    allow_file_discovery: bool | None = Field(None, alias="allowFileDiscovery", description="Whether this permission allows the file to be discovered through search. Only applicable for permissions of type 'domain' or 'anyone'."),
    domain: str | None = Field(None, description="The domain to which this permission applies."),
    email_address: str | None = Field(None, alias="emailAddress", description="The email address of the user or group to which this permission applies."),
    expiration_time: str | None = Field(None, alias="expirationTime", description="The expiration date and time for this permission in RFC 3339 format. Can only be set on user and group permissions, must be in the future, and cannot exceed one year from now."),
    inherited_permissions_disabled: bool | None = Field(None, alias="inheritedPermissionsDisabled", description="When true, restricts access to only organizers, owners, and users with permissions added directly on the item. Inherited permissions are disabled."),
    role: str | None = Field(None, description="The role granted by this permission. Valid roles include: owner, organizer, fileOrganizer, writer, commenter, and reader."),
    view: str | None = Field(None, description="The view scope for this permission. Supported values are 'published' (permission role is publishedReader) and 'metadata' (item visible only to metadata view with limited access). The metadata view is only supported on folders."),
) -> dict[str, Any]:
    """Updates a file or shared drive permission using patch semantics. Supports modifying role, expiration, ownership transfer, and access settings. Note: Concurrent operations on the same file are not supported; only the last update applies."""

    # Construct request model with validation
    try:
        _request = _models.PermissionsUpdateRequest(
            path=_models.PermissionsUpdateRequestPath(file_id=file_id, permission_id=permission_id),
            query=_models.PermissionsUpdateRequestQuery(remove_expiration=remove_expiration, transfer_ownership=transfer_ownership, use_domain_admin_access=use_domain_admin_access, fields=fields),
            body=_models.PermissionsUpdateRequestBody(allow_file_discovery=allow_file_discovery, domain=domain, email_address=email_address, expiration_time=expiration_time, inherited_permissions_disabled=inherited_permissions_disabled, role=role, view=view)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_file_permission: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{fileId}/permissions/{permissionId}", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{fileId}/permissions/{permissionId}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_file_permission")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_file_permission", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_file_permission",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: permissions
@mcp.tool()
async def delete_permission(
    file_id: str = Field(..., alias="fileId", description="The unique identifier of the file or shared drive from which the permission will be removed."),
    permission_id: str = Field(..., alias="permissionId", description="The unique identifier of the permission to be deleted."),
    use_domain_admin_access: bool | None = Field(None, alias="useDomainAdminAccess", description="When set to true, issues the request with domain administrator privileges. Requires the file to be a shared drive and the requester to be a domain administrator of the domain owning that shared drive."),
    fields: str | None = Field(None, description="Selector specifying which fields to include in a partial response."),
) -> dict[str, Any]:
    """Removes a specific permission from a file or shared drive. Note that concurrent permission operations on the same file are not supported; only the last update will be applied."""

    # Construct request model with validation
    try:
        _request = _models.PermissionsDeleteRequest(
            path=_models.PermissionsDeleteRequestPath(file_id=file_id, permission_id=permission_id),
            query=_models.PermissionsDeleteRequestQuery(use_domain_admin_access=use_domain_admin_access, fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_permission: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{fileId}/permissions/{permissionId}", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{fileId}/permissions/{permissionId}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_permission")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_permission", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_permission",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: replies
@mcp.tool()
async def list_replies(
    file_id: str = Field(..., alias="fileId", description="The unique identifier of the file containing the comment."),
    comment_id: str = Field(..., alias="commentId", description="The unique identifier of the comment whose replies should be listed."),
    include_deleted: bool | None = Field(None, alias="includeDeleted", description="Whether to include deleted replies in the results. Deleted replies will not contain their original content."),
    page_size: int | None = Field(None, alias="pageSize", description="Maximum number of replies to return in a single page of results.", ge=1, le=100),
    page_token: str | None = Field(None, alias="pageToken", description="Pagination token from the previous response's nextPageToken field to retrieve the next page of results."),
    fields: str | None = Field(None, description="Selector specifying which fields to include in a partial response."),
) -> dict[str, Any]:
    """Retrieves all replies to a specific comment on a file. Supports pagination and optional inclusion of deleted replies."""

    # Construct request model with validation
    try:
        _request = _models.RepliesListRequest(
            path=_models.RepliesListRequestPath(file_id=file_id, comment_id=comment_id),
            query=_models.RepliesListRequestQuery(include_deleted=include_deleted, page_size=page_size, page_token=page_token, fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_replies: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{fileId}/comments/{commentId}/replies", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{fileId}/comments/{commentId}/replies"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_replies")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_replies", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_replies",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: replies
@mcp.tool()
async def create_comment_reply(
    file_id: str = Field(..., alias="fileId", description="The unique identifier of the file containing the comment."),
    comment_id: str = Field(..., alias="commentId", description="The unique identifier of the comment to which the reply is being added."),
    fields: str | None = Field(None, description="Selector specifying which fields to include in a partial response."),
    action: str | None = Field(None, description="The action to perform on the parent comment. Use this to resolve or reopen a comment instead of adding reply content."),
    content: str | None = Field(None, description="The plain text content of the reply. Required if no action is specified. The content will be displayed as plain text in the API response."),
) -> dict[str, Any]:
    """Creates a reply to an existing comment on a file. Replies can either add content or perform actions like resolving or reopening the parent comment."""

    # Construct request model with validation
    try:
        _request = _models.RepliesCreateRequest(
            path=_models.RepliesCreateRequestPath(file_id=file_id, comment_id=comment_id),
            query=_models.RepliesCreateRequestQuery(fields=fields),
            body=_models.RepliesCreateRequestBody(action=action, content=content)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_comment_reply: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{fileId}/comments/{commentId}/replies", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{fileId}/comments/{commentId}/replies"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
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
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: replies
@mcp.tool()
async def get_reply(
    file_id: str = Field(..., alias="fileId", description="The unique identifier of the file containing the comment and reply."),
    comment_id: str = Field(..., alias="commentId", description="The unique identifier of the comment that contains the reply."),
    reply_id: str = Field(..., alias="replyId", description="The unique identifier of the reply to retrieve."),
    include_deleted: bool | None = Field(None, alias="includeDeleted", description="Whether to include deleted replies in the response. Deleted replies are returned without their original content."),
    fields: str | None = Field(None, description="Selector specifying which fields to include in a partial response."),
) -> dict[str, Any]:
    """Retrieves a specific reply to a comment on a file. Optionally includes deleted replies, which are returned without their original content."""

    # Construct request model with validation
    try:
        _request = _models.RepliesGetRequest(
            path=_models.RepliesGetRequestPath(file_id=file_id, comment_id=comment_id, reply_id=reply_id),
            query=_models.RepliesGetRequestQuery(include_deleted=include_deleted, fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_reply: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{fileId}/comments/{commentId}/replies/{replyId}", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{fileId}/comments/{commentId}/replies/{replyId}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_reply")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_reply", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_reply",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: replies
@mcp.tool()
async def update_reply(
    file_id: str = Field(..., alias="fileId", description="The unique identifier of the file containing the comment and reply."),
    comment_id: str = Field(..., alias="commentId", description="The unique identifier of the comment that contains the reply being updated."),
    reply_id: str = Field(..., alias="replyId", description="The unique identifier of the reply to update."),
    fields: str | None = Field(None, description="Selector specifying which fields to include in a partial response."),
    action: str | None = Field(None, description="The action this reply performs on the parent comment. Use to resolve or reopen a comment thread."),
    content: str | None = Field(None, description="The plain text content of the reply. Required if no action is specified. Note: use htmlContent for display purposes."),
) -> dict[str, Any]:
    """Updates a reply on a comment in a file using patch semantics. Supports modifying reply content or changing the reply's action status (resolve/reopen) relative to the parent comment."""

    # Construct request model with validation
    try:
        _request = _models.RepliesUpdateRequest(
            path=_models.RepliesUpdateRequestPath(file_id=file_id, comment_id=comment_id, reply_id=reply_id),
            query=_models.RepliesUpdateRequestQuery(fields=fields),
            body=_models.RepliesUpdateRequestBody(action=action, content=content)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_reply: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{fileId}/comments/{commentId}/replies/{replyId}", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{fileId}/comments/{commentId}/replies/{replyId}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_reply")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_reply", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_reply",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: replies
@mcp.tool()
async def delete_reply(
    file_id: str = Field(..., alias="fileId", description="The unique identifier of the file containing the comment with the reply to delete."),
    comment_id: str = Field(..., alias="commentId", description="The unique identifier of the comment containing the reply to delete."),
    reply_id: str = Field(..., alias="replyId", description="The unique identifier of the reply to delete."),
    fields: str | None = Field(None, description="Selector specifying which fields to include in a partial response."),
) -> dict[str, Any]:
    """Deletes a reply from a comment on a file. This operation permanently removes the specified reply and cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.RepliesDeleteRequest(
            path=_models.RepliesDeleteRequestPath(file_id=file_id, comment_id=comment_id, reply_id=reply_id),
            query=_models.RepliesDeleteRequestQuery(fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_reply: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{fileId}/comments/{commentId}/replies/{replyId}", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{fileId}/comments/{commentId}/replies/{replyId}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_reply")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_reply", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_reply",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: revisions
@mcp.tool()
async def get_file_revision(
    file_id: str = Field(..., alias="fileId", description="The unique identifier of the file containing the revision."),
    revision_id: str = Field(..., alias="revisionId", description="The unique identifier of the specific revision to retrieve."),
) -> dict[str, Any]:
    """Retrieves a specific file revision's metadata or content by its ID. Use this to access historical versions of a file for review, recovery, or comparison purposes."""

    # Construct request model with validation
    try:
        _request = _models.RevisionsGetRequest(
            path=_models.RevisionsGetRequestPath(file_id=file_id, revision_id=revision_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_file_revision: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{fileId}/revisions/{revisionId}", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{fileId}/revisions/{revisionId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_file_revision")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_file_revision", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_file_revision",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: revisions
@mcp.tool()
async def update_file_revision(
    file_id: str = Field(..., alias="fileId", description="The unique identifier of the file containing the revision to update."),
    revision_id: str = Field(..., alias="revisionId", description="The unique identifier of the revision to update."),
    keep_forever: bool | None = Field(None, alias="keepForever", description="Whether to permanently retain this revision in the file's history. When enabled, the revision will not be automatically deleted after 30 days. Limited to a maximum of 200 retained revisions per file. Only applicable to files with binary content in Drive."),
    publish_auto: bool | None = Field(None, alias="publishAuto", description="Whether to automatically republish subsequent revisions of this file. Only applicable to Google Docs, Sheets, and Slides files."),
) -> dict[str, Any]:
    """Updates a file revision's metadata using patch semantics, allowing you to preserve revisions indefinitely or configure auto-republishing behavior for Docs Editors files."""

    # Construct request model with validation
    try:
        _request = _models.RevisionsUpdateRequest(
            path=_models.RevisionsUpdateRequestPath(file_id=file_id, revision_id=revision_id),
            body=_models.RevisionsUpdateRequestBody(keep_forever=keep_forever, publish_auto=publish_auto)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_file_revision: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{fileId}/revisions/{revisionId}", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{fileId}/revisions/{revisionId}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_file_revision")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_file_revision", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_file_revision",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: revisions
@mcp.tool()
async def delete_file_revision(
    file_id: str = Field(..., alias="fileId", description="The unique identifier of the file containing the revision to delete."),
    revision_id: str = Field(..., alias="revisionId", description="The unique identifier of the specific file revision to permanently delete."),
) -> dict[str, Any]:
    """Permanently deletes a specific version of a file. Only binary files (images, videos, etc.) support revision deletion; revisions for Google Docs, Sheets, and the last remaining file version cannot be deleted."""

    # Construct request model with validation
    try:
        _request = _models.RevisionsDeleteRequest(
            path=_models.RevisionsDeleteRequestPath(file_id=file_id, revision_id=revision_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_file_revision: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{fileId}/revisions/{revisionId}", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{fileId}/revisions/{revisionId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_file_revision")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_file_revision", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_file_revision",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: revisions
@mcp.tool()
async def list_file_revisions(
    file_id: str = Field(..., alias="fileId", description="The unique identifier of the file whose revisions you want to list."),
    page_size: int | None = Field(None, alias="pageSize", description="The maximum number of revisions to return in a single page of results.", ge=1, le=1000),
    page_token: str | None = Field(None, alias="pageToken", description="A pagination token from a previous response to retrieve the next page of results. Use the 'nextPageToken' value returned from the prior request."),
) -> dict[str, Any]:
    """Retrieves a list of revisions for a specified file. Note that the revision history may be incomplete for files with extensive revision histories, and older revisions might be omitted from the response."""

    # Construct request model with validation
    try:
        _request = _models.RevisionsListRequest(
            path=_models.RevisionsListRequestPath(file_id=file_id),
            query=_models.RevisionsListRequestQuery(page_size=page_size, page_token=page_token)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_file_revisions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{fileId}/revisions", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{fileId}/revisions"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_file_revisions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_file_revisions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_file_revisions",
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
        print("  python google_drive_server.py", file=sys.stderr)
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

    parser = argparse.ArgumentParser(description="Google Drive MCP Server")

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
    logger.info("Starting Google Drive MCP Server")
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

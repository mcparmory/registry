#!/usr/bin/env python3
"""
ClickUp MCP Server
Generated: 2026-04-09 17:17:41 UTC
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
from datetime import datetime, timezone
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

BASE_URL = os.getenv("BASE_URL", "https://api.clickup.com/api")
SERVER_NAME = "ClickUp"
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

def parse_due(value: str | None = None) -> dict | None:
    """Helper function for parameter transformation"""
    if value is None:
        return None
    value = value.strip()
    if 'T' in value or ' ' in value:
        dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        due_date_time = True
    else:
        dt = datetime.fromisoformat(value)
        dt = dt.replace(tzinfo=timezone.utc)
        due_date_time = False
    due_date = int(dt.timestamp() * 1000)
    return {'due_date': due_date, 'due_date_time': due_date_time}

def build_custom_fields(custom_fields_field_ids: list[str] | None = None, custom_fields_operators: list[str] | None = None, custom_fields_values: list[str] | None = None) -> str | None:
    """Helper function for parameter transformation"""
    try:
        if custom_fields_field_ids is None and custom_fields_operators is None and custom_fields_values is None:
            return None
        if not custom_fields_field_ids:
            raise ValueError("custom_fields_field_ids must be provided when specifying custom field filters")
        operators = custom_fields_operators or []
        values = custom_fields_values or []
        if len(operators) != len(custom_fields_field_ids):
            raise ValueError("custom_fields_operators length must match custom_fields_field_ids length")
        if len(values) != len(custom_fields_field_ids):
            raise ValueError("custom_fields_values length must match custom_fields_field_ids length")
        entries = []
        for field_id, operator, value in zip(custom_fields_field_ids, operators, values):
            entries.append({"field_id": field_id, "operator": operator, "value": value})
        return json.dumps(entries)
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to build custom_fields filter: {e}")


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
    'Authorization_Token',
]

# Initialize authentication handlers at server startup
_auth_handlers: dict[str, Any] = {}
try:
    _auth_handlers["Authorization_Token"] = _auth.APIKeyAuth(env_var="API_KEY", location="header", param_name="Authorization")
    logging.info("Authentication configured: Authorization_Token")
except ValueError as e:
    # Extract credential names from error message (first sentence before "Leave empty")
    error_msg = str(e).split("Leave empty")[0].strip()
    logging.warning(f"Credentials for Authorization_Token not configured: {error_msg}")
    _auth_handlers["Authorization_Token"] = None

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

mcp = FastMCP("ClickUp", middleware=[_JsonCoercionMiddleware()])

# Tags: Attachments
@mcp.tool()
async def upload_task_attachment(
    task_id: str = Field(..., description="The unique identifier of the task to which the file will be attached."),
    custom_task_ids: bool | None = Field(None, description="Set to true to reference the task by its custom task ID instead of the default system-generated task ID."),
    team_id: float | None = Field(None, description="The Workspace ID required when referencing a task by its custom task ID. Must be provided alongside custom_task_ids=true."),
    attachment: list[Any] | None = Field(None, description="The file content to upload as a multipart/form-data attachment. Each item represents a part of the multipart payload for the file being attached."),
) -> dict[str, Any]:
    """Upload a local file to a task as an attachment using multipart/form-data. Note that cloud-hosted files are not supported; only locally accessible files can be attached."""

    # Construct request model with validation
    try:
        _request = _models.CreateTaskAttachmentRequest(
            path=_models.CreateTaskAttachmentRequestPath(task_id=task_id),
            query=_models.CreateTaskAttachmentRequestQuery(custom_task_ids=custom_task_ids, team_id=team_id),
            body=_models.CreateTaskAttachmentRequestBody(attachment=attachment)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for upload_task_attachment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/task/{task_id}/attachment", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/task/{task_id}/attachment"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("upload_task_attachment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("upload_task_attachment", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="upload_task_attachment",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: Authorization
@mcp.tool()
async def get_current_user() -> dict[str, Any]:
    """Retrieves the profile and account details of the currently authenticated ClickUp user. Useful for confirming identity, retrieving user ID, and accessing account-level information."""

    # Extract parameters for API call
    _http_path = "/v2/user"
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

# Tags: Workspaces
@mcp.tool()
async def list_workspaces() -> dict[str, Any]:
    """Retrieves all workspaces accessible to the currently authenticated user. Use this to discover available workspaces before performing workspace-specific operations."""

    # Extract parameters for API call
    _http_path = "/v2/team"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_workspaces")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_workspaces", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_workspaces",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Task Checklists
@mcp.tool()
async def create_checklist(
    task_id: str = Field(..., description="The unique identifier of the task to which the checklist will be added."),
    name: str = Field(..., description="The display name for the new checklist."),
    custom_task_ids: bool | None = Field(None, description="Set to true if referencing the task by its custom task ID instead of the default system-generated task ID."),
    team_id: float | None = Field(None, description="The Workspace ID required when using custom task IDs; must be provided alongside custom_task_ids=true."),
) -> dict[str, Any]:
    """Add a new named checklist to a specified task, allowing you to track subtasks or steps within that task."""

    # Construct request model with validation
    try:
        _request = _models.CreateChecklistRequest(
            path=_models.CreateChecklistRequestPath(task_id=task_id),
            query=_models.CreateChecklistRequestQuery(custom_task_ids=custom_task_ids, team_id=team_id),
            body=_models.CreateChecklistRequestBody(name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_checklist: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/task/{task_id}/checklist", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/task/{task_id}/checklist"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_checklist")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_checklist", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_checklist",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Task Checklists
@mcp.tool()
async def update_checklist(
    checklist_id: str = Field(..., description="The unique identifier (UUID) of the checklist to update."),
    name: str | None = Field(None, description="The new display name for the checklist."),
    position: int | None = Field(None, description="The zero-based display order of the checklist among all checklists on the task, where 0 places it at the top."),
) -> dict[str, Any]:
    """Rename a checklist or change its display order relative to other checklists on a task. Provide a new name, a new position, or both."""

    # Construct request model with validation
    try:
        _request = _models.EditChecklistRequest(
            path=_models.EditChecklistRequestPath(checklist_id=checklist_id),
            body=_models.EditChecklistRequestBody(name=name, position=position)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_checklist: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/checklist/{checklist_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/checklist/{checklist_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_checklist")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_checklist", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_checklist",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Task Checklists
@mcp.tool()
async def delete_checklist(checklist_id: str = Field(..., description="The unique identifier (UUID) of the checklist to delete.")) -> dict[str, Any]:
    """Permanently deletes a checklist from a task. This action is irreversible and removes the checklist along with all its items."""

    # Construct request model with validation
    try:
        _request = _models.DeleteChecklistRequest(
            path=_models.DeleteChecklistRequestPath(checklist_id=checklist_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_checklist: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/checklist/{checklist_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/checklist/{checklist_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_checklist")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_checklist", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_checklist",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Task Checklists
@mcp.tool()
async def create_checklist_item(
    checklist_id: str = Field(..., description="The unique identifier of the checklist to which the new item will be added."),
    name: str | None = Field(None, description="The display name or label for the checklist item."),
    assignee: int | None = Field(None, description="The numeric user ID of the team member to assign this checklist item to."),
) -> dict[str, Any]:
    """Adds a new line item to an existing task checklist. Optionally assign the item to a specific user by their ID."""

    # Construct request model with validation
    try:
        _request = _models.CreateChecklistItemRequest(
            path=_models.CreateChecklistItemRequestPath(checklist_id=checklist_id),
            body=_models.CreateChecklistItemRequestBody(name=name, assignee=assignee)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_checklist_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/checklist/{checklist_id}/checklist_item", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/checklist/{checklist_id}/checklist_item"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_checklist_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_checklist_item", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_checklist_item",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Task Checklists
@mcp.tool()
async def update_checklist_item(
    checklist_id: str = Field(..., description="The unique identifier of the checklist that contains the item to be updated."),
    checklist_item_id: str = Field(..., description="The unique identifier of the specific checklist item to update."),
    name: str | None = Field(None, description="The updated display name or label for the checklist item."),
    assignee: str | None = Field(None, description="The user ID of the team member to assign to this checklist item."),
    resolved: bool | None = Field(None, description="Whether the checklist item is marked as completed; set to true to resolve it or false to reopen it."),
    parent: str | None = Field(None, description="The checklist item ID of the parent item under which this item should be nested, enabling hierarchical checklist structures."),
) -> dict[str, Any]:
    """Update an individual item within a task checklist, allowing you to rename it, reassign it, mark it as resolved or unresolved, or nest it under another checklist item as a child."""

    # Construct request model with validation
    try:
        _request = _models.EditChecklistItemRequest(
            path=_models.EditChecklistItemRequestPath(checklist_id=checklist_id, checklist_item_id=checklist_item_id),
            body=_models.EditChecklistItemRequestBody(name=name, assignee=assignee, resolved=resolved, parent=parent)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_checklist_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/checklist/{checklist_id}/checklist_item/{checklist_item_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/checklist/{checklist_id}/checklist_item/{checklist_item_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_checklist_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_checklist_item", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_checklist_item",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Task Checklists
@mcp.tool()
async def delete_checklist_item(
    checklist_id: str = Field(..., description="The unique identifier (UUID) of the checklist from which the item will be deleted."),
    checklist_item_id: str = Field(..., description="The unique identifier (UUID) of the specific checklist item to be deleted."),
) -> dict[str, Any]:
    """Permanently removes a specific line item from a task checklist. This action cannot be undone and will delete the item and its associated data."""

    # Construct request model with validation
    try:
        _request = _models.DeleteChecklistItemRequest(
            path=_models.DeleteChecklistItemRequestPath(checklist_id=checklist_id, checklist_item_id=checklist_item_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_checklist_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/checklist/{checklist_id}/checklist_item/{checklist_item_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/checklist/{checklist_id}/checklist_item/{checklist_item_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_checklist_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_checklist_item", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_checklist_item",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Comments
@mcp.tool()
async def list_task_comments(
    task_id: str = Field(..., description="The unique identifier of the task whose comments you want to retrieve."),
    custom_task_ids: bool | None = Field(None, description="Set to `true` if referencing the task by its custom task ID instead of the default ClickUp task ID."),
    team_id: float | None = Field(None, description="The Workspace ID (team ID) required when `custom_task_ids` is set to `true` to correctly resolve the custom task ID."),
) -> dict[str, Any]:
    """Retrieve comments for a specific task, returned in reverse chronological order (newest to oldest). By default returns the 25 most recent comments; use the `start` and `start_id` parameters together with the last comment of the current response to paginate through older comments."""

    # Construct request model with validation
    try:
        _request = _models.GetTaskCommentsRequest(
            path=_models.GetTaskCommentsRequestPath(task_id=task_id),
            query=_models.GetTaskCommentsRequestQuery(custom_task_ids=custom_task_ids, team_id=team_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_task_comments: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/task/{task_id}/comment", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/task/{task_id}/comment"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_task_comments")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_task_comments", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_task_comments",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Comments
@mcp.tool()
async def add_task_comment(
    task_id: str = Field(..., description="The unique identifier of the task to which the comment will be added."),
    comment_text: str = Field(..., description="The text content of the comment to be added to the task."),
    notify_all: bool = Field(..., description="When true, the comment creator is also notified in addition to task assignees and watchers, who are always notified regardless of this setting."),
    custom_task_ids: bool | None = Field(None, description="Set to true if referencing the task by its custom task ID instead of the default system-generated ID."),
    team_id: float | None = Field(None, description="The Workspace ID required when using custom task IDs. Must be provided alongside custom_task_ids=true."),
    assignee: int | None = Field(None, description="The user ID of the individual to assign to this comment."),
    group_assignee: str | None = Field(None, description="The ID of the group to assign to this comment."),
) -> dict[str, Any]:
    """Add a new comment to a specified task, with options to assign the comment to a user or group and notify all relevant parties."""

    # Construct request model with validation
    try:
        _request = _models.CreateTaskCommentRequest(
            path=_models.CreateTaskCommentRequestPath(task_id=task_id),
            query=_models.CreateTaskCommentRequestQuery(custom_task_ids=custom_task_ids, team_id=team_id),
            body=_models.CreateTaskCommentRequestBody(comment_text=comment_text, assignee=assignee, group_assignee=group_assignee, notify_all=notify_all)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_task_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/task/{task_id}/comment", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/task/{task_id}/comment"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_task_comment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_task_comment", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_task_comment",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Comments
@mcp.tool()
async def list_chat_view_comments(
    view_id: str = Field(..., description="The unique identifier of the Chat view whose comments you want to retrieve."),
    start: int | None = Field(None, description="The timestamp of a Chat view comment to paginate from, expressed as Unix time in milliseconds. Use the date of the oldest comment from the previous response to retrieve the next page of comments."),
    start_id: str | None = Field(None, description="The unique identifier of a Chat view comment to paginate from. Use the ID of the oldest comment from the previous response alongside the `start` parameter to retrieve the next page of comments."),
) -> dict[str, Any]:
    """Retrieve comments from a Chat view, returning the most recent 25 comments by default. Use the date and ID of the oldest comment from a previous response to paginate and retrieve the next 25 comments."""

    # Construct request model with validation
    try:
        _request = _models.GetChatViewCommentsRequest(
            path=_models.GetChatViewCommentsRequestPath(view_id=view_id),
            query=_models.GetChatViewCommentsRequestQuery(start=start, start_id=start_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_chat_view_comments: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/view/{view_id}/comment", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/view/{view_id}/comment"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_chat_view_comments")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_chat_view_comments", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_chat_view_comments",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Comments
@mcp.tool()
async def create_chat_view_comment(
    view_id: str = Field(..., description="The unique identifier of the Chat view to which the comment will be added."),
    comment_text: str = Field(..., description="The text content of the comment to post on the Chat view."),
    notify_all: bool = Field(..., description="When set to true, the creator of the comment is also notified upon posting. Assignees and watchers on the view are always notified regardless of this setting."),
) -> dict[str, Any]:
    """Adds a new comment to a specified Chat view. Optionally notifies the comment creator in addition to the assignees and watchers who are always notified."""

    # Construct request model with validation
    try:
        _request = _models.CreateChatViewCommentRequest(
            path=_models.CreateChatViewCommentRequestPath(view_id=view_id),
            body=_models.CreateChatViewCommentRequestBody(comment_text=comment_text, notify_all=notify_all)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_chat_view_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/view/{view_id}/comment", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/view/{view_id}/comment"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_chat_view_comment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_chat_view_comment", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_chat_view_comment",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Comments
@mcp.tool()
async def list_comments(
    list_id: float = Field(..., description="The unique identifier of the List whose comments you want to retrieve."),
    start: int | None = Field(None, description="The timestamp of the oldest comment from the previous page, used to paginate to the next set of 25 comments. Provide as Unix time in milliseconds."),
    start_id: str | None = Field(None, description="The unique comment ID of the oldest comment from the previous page, used alongside the start timestamp to paginate to the next set of 25 comments."),
) -> dict[str, Any]:
    """Retrieve comments added to a specific List, returning the most recent 25 by default. Use the oldest comment's date and ID as pagination cursors to fetch earlier comments in batches of 25."""

    # Construct request model with validation
    try:
        _request = _models.GetListCommentsRequest(
            path=_models.GetListCommentsRequestPath(list_id=list_id),
            query=_models.GetListCommentsRequestQuery(start=start, start_id=start_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_comments: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/list/{list_id}/comment", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/list/{list_id}/comment"
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
async def add_list_comment(
    list_id: float = Field(..., description="The unique identifier of the List to which the comment will be added."),
    comment_text: str = Field(..., description="The text content of the comment to be posted on the List."),
    assignee: int = Field(..., description="The user ID of the individual to assign to this comment."),
    notify_all: bool = Field(..., description="When set to true, the creator of the comment will also receive a notification. Assignees and watchers on the List are always notified regardless of this setting."),
) -> dict[str, Any]:
    """Adds a comment to a specified List, optionally notifying the comment creator in addition to the standard assignees and watchers who are always notified."""

    # Construct request model with validation
    try:
        _request = _models.CreateListCommentRequest(
            path=_models.CreateListCommentRequestPath(list_id=list_id),
            body=_models.CreateListCommentRequestBody(comment_text=comment_text, assignee=assignee, notify_all=notify_all)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_list_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/list/{list_id}/comment", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/list/{list_id}/comment"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_list_comment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_list_comment", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_list_comment",
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
    comment_id: float = Field(..., description="The unique identifier of the comment to update."),
    comment_text: str = Field(..., description="The updated text content to replace the existing comment body."),
    assignee: int = Field(..., description="The user ID of the individual to assign the comment to."),
    resolved: bool = Field(..., description="Set to true to mark the comment as resolved, or false to mark it as unresolved."),
    group_assignee: int | None = Field(None, description="The group ID to assign the comment to, used when assigning to a team or group rather than an individual."),
) -> dict[str, Any]:
    """Update an existing task comment by modifying its text, assigning it to a user or group, or marking it as resolved. All core fields must be provided in the request."""

    # Construct request model with validation
    try:
        _request = _models.UpdateCommentRequest(
            path=_models.UpdateCommentRequestPath(comment_id=comment_id),
            body=_models.UpdateCommentRequestBody(comment_text=comment_text, assignee=assignee, group_assignee=group_assignee, resolved=resolved)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/comment/{comment_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/comment/{comment_id}"
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
async def delete_comment(comment_id: float = Field(..., description="The unique numeric identifier of the comment to delete.")) -> dict[str, Any]:
    """Permanently deletes a specific task comment by its unique identifier. This action is irreversible and removes the comment from the task."""

    # Construct request model with validation
    try:
        _request = _models.DeleteCommentRequest(
            path=_models.DeleteCommentRequestPath(comment_id=comment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/comment/{comment_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/comment/{comment_id}"
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

# Tags: Comments
@mcp.tool()
async def list_comment_replies(comment_id: float = Field(..., description="The unique identifier of the parent comment whose threaded replies should be retrieved.")) -> dict[str, Any]:
    """Retrieves all threaded reply comments nested under a specified parent comment. The parent comment itself is excluded from the returned results."""

    # Construct request model with validation
    try:
        _request = _models.GetThreadedCommentsRequest(
            path=_models.GetThreadedCommentsRequestPath(comment_id=comment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_comment_replies: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/comment/{comment_id}/reply", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/comment/{comment_id}/reply"
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
        headers=_http_headers,
    )

    return _response_data

# Tags: Comments
@mcp.tool()
async def reply_to_comment(
    comment_id: float = Field(..., description="The unique identifier of the parent comment to reply to."),
    comment_text: str = Field(..., description="The text content of the threaded reply comment."),
    notify_all: bool = Field(..., description="When true, the original comment creator is also notified of this reply. Assignees and task watchers are always notified regardless of this setting."),
    assignee: int | None = Field(None, description="The user ID of the individual to assign this comment to."),
    group_assignee: str | None = Field(None, description="The identifier of the group to assign this comment to."),
) -> dict[str, Any]:
    """Create a threaded reply to an existing comment on a task. Supports assigning the reply to a user or group and controlling notification behavior."""

    # Construct request model with validation
    try:
        _request = _models.CreateThreadedCommentRequest(
            path=_models.CreateThreadedCommentRequestPath(comment_id=comment_id),
            body=_models.CreateThreadedCommentRequestBody(comment_text=comment_text, assignee=assignee, group_assignee=group_assignee, notify_all=notify_all)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for reply_to_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/comment/{comment_id}/reply", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/comment/{comment_id}/reply"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("reply_to_comment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("reply_to_comment", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="reply_to_comment",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Fields
@mcp.tool()
async def list_custom_fields(
    list_id: float = Field(..., description="The unique numeric identifier of the List whose Custom Fields you want to retrieve."),
    content_type: Literal["application/json"] = Field(..., alias="Content-Type", description="The media type format for the request, indicating the content format expected by the API."),
) -> dict[str, Any]:
    """Retrieves all Custom Fields accessible to the authenticated user within a specific List. Use this to discover available field definitions before reading or writing custom field data."""

    # Construct request model with validation
    try:
        _request = _models.GetAccessibleCustomFieldsRequest(
            path=_models.GetAccessibleCustomFieldsRequestPath(list_id=list_id),
            header=_models.GetAccessibleCustomFieldsRequestHeader(content_type=content_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_custom_fields: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/list/{list_id}/field", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/list/{list_id}/field"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

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

# Tags: Custom Fields
@mcp.tool()
async def list_folder_custom_fields(
    folder_id: float = Field(..., description="The unique numeric identifier of the folder whose custom fields you want to retrieve."),
    content_type: Literal["application/json"] = Field(..., alias="Content-Type", description="The media type of the request payload, used to indicate the format of the data being sent to the server."),
) -> dict[str, Any]:
    """Retrieves all Custom Fields created at the Folder level for the specified folder. Note that Custom Fields created at the List level within the folder are not included in the results."""

    # Construct request model with validation
    try:
        _request = _models.GetFolderAvailableFieldsRequest(
            path=_models.GetFolderAvailableFieldsRequestPath(folder_id=folder_id),
            header=_models.GetFolderAvailableFieldsRequestHeader(content_type=content_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_folder_custom_fields: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/folder/{folder_id}/field", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/folder/{folder_id}/field"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_folder_custom_fields")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_folder_custom_fields", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_folder_custom_fields",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Fields
@mcp.tool()
async def list_space_custom_fields(
    space_id: float = Field(..., description="The unique identifier of the Space whose Custom Fields you want to retrieve."),
    content_type: Literal["application/json"] = Field(..., alias="Content-Type", description="The media type of the request payload, used to indicate the format of the data being sent."),
) -> dict[str, Any]:
    """Retrieves all Custom Fields created at the Space level for a specific Space. Note that Custom Fields created at the Folder or List level are not included in the results."""

    # Construct request model with validation
    try:
        _request = _models.GetSpaceAvailableFieldsRequest(
            path=_models.GetSpaceAvailableFieldsRequestPath(space_id=space_id),
            header=_models.GetSpaceAvailableFieldsRequestHeader(content_type=content_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_space_custom_fields: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/space/{space_id}/field", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/space/{space_id}/field"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_space_custom_fields")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_space_custom_fields", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_space_custom_fields",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Fields
@mcp.tool()
async def list_workspace_custom_fields(
    team_id: float = Field(..., description="The unique identifier of the Workspace whose Workspace-level Custom Fields you want to retrieve."),
    content_type: Literal["application/json"] = Field(..., alias="Content-Type", description="The media type of the request payload, indicating the format of the request body sent to the API."),
) -> dict[str, Any]:
    """Retrieves all Custom Fields created at the Workspace level for a specific Workspace. Note that Custom Fields created at the Space, Folder, or List level are not included in the results."""

    # Construct request model with validation
    try:
        _request = _models.GetTeamAvailableFieldsRequest(
            path=_models.GetTeamAvailableFieldsRequestPath(team_id=team_id),
            header=_models.GetTeamAvailableFieldsRequestHeader(content_type=content_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_workspace_custom_fields: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/team/{team_id}/field", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/team/{team_id}/field"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_workspace_custom_fields")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_workspace_custom_fields", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_workspace_custom_fields",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Fields
@mcp.tool()
async def set_task_custom_field_value(
    task_id: str = Field(..., description="The unique identifier of the task you want to update with a Custom Field value."),
    field_id: str = Field(..., description="The universally unique identifier (UUID) of the Custom Field you want to set. Retrieve this from the Get Accessible Custom Fields or Get Task endpoints."),
    custom_task_ids: bool | None = Field(None, description="Set to true if you are referencing the task by its Custom Task ID instead of the standard task ID."),
    team_id: float | None = Field(None, description="The Workspace ID required when referencing a task by its Custom Task ID. Must be provided alongside custom_task_ids=true."),
    body: _models.SetCustomFieldValueBodyV0 | _models.SetCustomFieldValueBodyV1 | _models.SetCustomFieldValueBodyV2 | _models.SetCustomFieldValueBodyV3 | _models.SetCustomFieldValueBodyV4 | _models.SetCustomFieldValueBodyV5 | _models.SetCustomFieldValueBodyV6 | _models.SetCustomFieldValueBodyV7 | _models.SetCustomFieldValueBodyV8 | _models.SetCustomFieldValueBodyV9 | _models.SetCustomFieldValueBodyV10 | _models.SetCustomFieldValueBodyV11 | _models.SetCustomFieldValueBodyV12 | _models.SetCustomFieldValueBodyV13 | _models.SetCustomFieldValueBodyV14 | _models.SetCustomFieldValueBodyV15 | None = Field(None, description="The request body containing the value to set for the Custom Field. The shape of the value varies by field type — supported types include URLs, UUIDs, email addresses, phone numbers, dates (millisecond timestamps), text, numbers, currency, user lists, label lists, dropdowns, progress, file lists, location objects, and booleans."),
) -> dict[str, Any]:
    """Set or update the value of a specific Custom Field on a task. Requires the task ID and the UUID of the Custom Field to update."""

    # Construct request model with validation
    try:
        _request = _models.SetCustomFieldValueRequest(
            path=_models.SetCustomFieldValueRequestPath(task_id=task_id, field_id=field_id),
            query=_models.SetCustomFieldValueRequestQuery(custom_task_ids=custom_task_ids, team_id=team_id),
            body=_models.SetCustomFieldValueRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for set_task_custom_field_value: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/task/{task_id}/field/{field_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/task/{task_id}/field/{field_id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("set_task_custom_field_value")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("set_task_custom_field_value", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="set_task_custom_field_value",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Fields
@mcp.tool()
async def clear_task_custom_field_value(
    task_id: str = Field(..., description="The unique identifier of the task from which the Custom Field value will be cleared."),
    field_id: str = Field(..., description="The UUID of the Custom Field whose value should be removed from the task."),
    custom_task_ids: bool | None = Field(None, description="Set to true to reference the task by its custom task ID instead of the default ClickUp task ID."),
    team_id: float | None = Field(None, description="The Workspace ID (team_id) required when using custom task IDs; must be paired with custom_task_ids=true."),
) -> dict[str, Any]:
    """Clears the stored value of a specific Custom Field on a task without deleting the Custom Field definition or its available options."""

    # Construct request model with validation
    try:
        _request = _models.RemoveCustomFieldValueRequest(
            path=_models.RemoveCustomFieldValueRequestPath(task_id=task_id, field_id=field_id),
            query=_models.RemoveCustomFieldValueRequestQuery(custom_task_ids=custom_task_ids, team_id=team_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for clear_task_custom_field_value: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/task/{task_id}/field/{field_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/task/{task_id}/field/{field_id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("clear_task_custom_field_value")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("clear_task_custom_field_value", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="clear_task_custom_field_value",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Task Relationships
@mcp.tool()
async def add_task_dependency(
    task_id: str = Field(..., description="The ID of the task for which the dependency relationship is being defined — either the task that is waiting on another task or the task that is blocking another task."),
    custom_task_ids: bool | None = Field(None, description="Set to true to reference tasks by their custom task IDs instead of their default system-generated IDs. Requires `team_id` to also be provided."),
    team_id: float | None = Field(None, description="The Workspace ID required when `custom_task_ids` is true, used to resolve custom task IDs within the correct Workspace scope."),
    depends_on: str | None = Field(None, description="The ID of the task that the specified task (`task_id`) is waiting on — i.e., the task that must be completed before `task_id` can proceed."),
    dependency_of: str | None = Field(None, description="The ID of the task that the specified task (`task_id`) is blocking — i.e., the task that cannot proceed until `task_id` is completed."),
) -> dict[str, Any]:
    """Create a dependency relationship between two tasks, setting one task as waiting on or blocking another. Use `depends_on` to specify a task this task is waiting on, or `dependency_of` to specify a task this task is blocking."""

    # Construct request model with validation
    try:
        _request = _models.AddDependencyRequest(
            path=_models.AddDependencyRequestPath(task_id=task_id),
            query=_models.AddDependencyRequestQuery(custom_task_ids=custom_task_ids, team_id=team_id),
            body=_models.AddDependencyRequestBody(depends_on=depends_on, dependency_of=dependency_of)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_task_dependency: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/task/{task_id}/dependency", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/task/{task_id}/dependency"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_task_dependency")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_task_dependency", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_task_dependency",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Task Relationships
@mcp.tool()
async def delete_task_dependency(
    task_id: str = Field(..., description="The unique identifier of the primary task whose dependency relationship is being removed."),
    depends_on: str = Field(..., description="The ID of the task that the primary task depends on — i.e., the prerequisite task to be unlinked."),
    dependency_of: str = Field(..., description="The ID of the task that depends on the primary task — i.e., the downstream task to be unlinked."),
    custom_task_ids: bool | None = Field(None, description="Set to true to reference tasks by their custom task IDs instead of their system-generated IDs. Requires the team_id parameter to also be provided."),
    team_id: float | None = Field(None, description="The Workspace ID (team) required when using custom task IDs. Must be provided alongside custom_task_ids=true to correctly resolve custom task references."),
) -> dict[str, Any]:
    """Remove a dependency relationship between two tasks, unlinking them so that one no longer depends on the other. Both the target task and the related dependent or prerequisite task must be specified."""

    # Construct request model with validation
    try:
        _request = _models.DeleteDependencyRequest(
            path=_models.DeleteDependencyRequestPath(task_id=task_id),
            query=_models.DeleteDependencyRequestQuery(depends_on=depends_on, dependency_of=dependency_of, custom_task_ids=custom_task_ids, team_id=team_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_task_dependency: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/task/{task_id}/dependency", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/task/{task_id}/dependency"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_task_dependency")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_task_dependency", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_task_dependency",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Task Relationships
@mcp.tool()
async def link_task(
    task_id: str = Field(..., description="The ID of the task initiating the link (the source task)."),
    links_to: str = Field(..., description="The ID of the task to link to (the target task)."),
    custom_task_ids: bool | None = Field(None, description="Set to true to reference tasks by their custom task IDs instead of their default system IDs. Requires team_id to also be provided when enabled."),
    team_id: float | None = Field(None, description="The Workspace ID (team) required when custom_task_ids is set to true, used to resolve custom task IDs within the correct workspace scope."),
) -> dict[str, Any]:
    """Creates a directional link between two tasks, equivalent to using the Task Links feature in the task's right-hand sidebar. Only task-to-task links are supported; general or cross-object links are not."""

    # Construct request model with validation
    try:
        _request = _models.AddTaskLinkRequest(
            path=_models.AddTaskLinkRequestPath(task_id=task_id, links_to=links_to),
            query=_models.AddTaskLinkRequestQuery(custom_task_ids=custom_task_ids, team_id=team_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for link_task: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/task/{task_id}/link/{links_to}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/task/{task_id}/link/{links_to}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("link_task")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("link_task", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="link_task",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Task Relationships
@mcp.tool()
async def delete_task_link(
    task_id: str = Field(..., description="The unique identifier of the source task from which the link will be removed."),
    links_to: str = Field(..., description="The unique identifier of the target task that is currently linked to the source task."),
    custom_task_ids: bool | None = Field(None, description="Set to true to reference tasks by their custom task IDs instead of their default system-generated IDs. Requires the team_id parameter to also be provided."),
    team_id: float | None = Field(None, description="The Workspace ID required when using custom task IDs. Must be provided alongside custom_task_ids=true to correctly resolve tasks within the specified Workspace."),
) -> dict[str, Any]:
    """Removes the dependency or relationship link between two tasks. Both task IDs must be provided to identify the specific link to delete."""

    # Construct request model with validation
    try:
        _request = _models.DeleteTaskLinkRequest(
            path=_models.DeleteTaskLinkRequestPath(task_id=task_id, links_to=links_to),
            query=_models.DeleteTaskLinkRequestQuery(custom_task_ids=custom_task_ids, team_id=team_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_task_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/task/{task_id}/link/{links_to}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/task/{task_id}/link/{links_to}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_task_link")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_task_link", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_task_link",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Folders
@mcp.tool()
async def list_folders(
    space_id: float = Field(..., description="The unique identifier of the Space whose Folders you want to retrieve."),
    archived: bool | None = Field(None, description="When set to true, returns only archived Folders; when false or omitted, returns only active Folders."),
) -> dict[str, Any]:
    """Retrieve all Folders within a specified Space. Optionally include archived Folders in the results."""

    # Construct request model with validation
    try:
        _request = _models.GetFoldersRequest(
            path=_models.GetFoldersRequestPath(space_id=space_id),
            query=_models.GetFoldersRequestQuery(archived=archived)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_folders: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/space/{space_id}/folder", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/space/{space_id}/folder"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_folders")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_folders", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_folders",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Folders
@mcp.tool()
async def create_folder(
    space_id: float = Field(..., description="The unique identifier of the Space in which the new folder will be created."),
    name: str = Field(..., description="The display name for the new folder, used to identify it within the Space."),
) -> dict[str, Any]:
    """Creates a new folder within a specified Space to organize lists and tasks. Folders help structure your workspace hierarchy beneath a Space."""

    # Construct request model with validation
    try:
        _request = _models.CreateFolderRequest(
            path=_models.CreateFolderRequestPath(space_id=space_id),
            body=_models.CreateFolderRequestBody(name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_folder: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/space/{space_id}/folder", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/space/{space_id}/folder"
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

# Tags: Folders
@mcp.tool()
async def get_folder(folder_id: float = Field(..., description="The unique numeric identifier of the folder to retrieve.")) -> dict[str, Any]:
    """Retrieves a folder and the Lists contained within it. Use this to inspect the structure and contents of a specific folder."""

    # Construct request model with validation
    try:
        _request = _models.GetFolderRequest(
            path=_models.GetFolderRequestPath(folder_id=folder_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_folder: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/folder/{folder_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/folder/{folder_id}"
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

# Tags: Folders
@mcp.tool()
async def rename_folder(
    folder_id: float = Field(..., description="The unique numeric identifier of the folder to rename."),
    name: str = Field(..., description="The new name to assign to the folder."),
) -> dict[str, Any]:
    """Renames an existing folder by updating its display name. The folder's contents and structure remain unchanged."""

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
    _http_path = _build_path("/v2/folder/{folder_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/folder/{folder_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("rename_folder")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("rename_folder", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="rename_folder",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Folders
@mcp.tool()
async def delete_folder(folder_id: float = Field(..., description="The unique numeric identifier of the folder to be deleted.")) -> dict[str, Any]:
    """Permanently deletes a folder from your Workspace. This action cannot be undone, so ensure the correct folder ID is specified before proceeding."""

    # Construct request model with validation
    try:
        _request = _models.DeleteFolderRequest(
            path=_models.DeleteFolderRequestPath(folder_id=folder_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_folder: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/folder/{folder_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/folder/{folder_id}"
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

# Tags: Goals
@mcp.tool()
async def list_goals(
    team_id: float = Field(..., description="The unique identifier of the Workspace whose Goals you want to retrieve."),
    include_completed: bool | None = Field(None, description="When set to true, completed Goals are included in the response alongside active ones; omitting this parameter or setting it to false returns only active Goals."),
) -> dict[str, Any]:
    """Retrieves all Goals available in a specified Workspace, with an option to include completed Goals in the results."""

    # Construct request model with validation
    try:
        _request = _models.GetGoalsRequest(
            path=_models.GetGoalsRequestPath(team_id=team_id),
            query=_models.GetGoalsRequestQuery(include_completed=include_completed)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_goals: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/team/{team_id}/goal", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/team/{team_id}/goal"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_goals")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_goals", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_goals",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Goals
@mcp.tool()
async def create_goal(
    team_id: float = Field(..., description="The unique identifier of the Workspace where the Goal will be created."),
    name: str = Field(..., description="The display name of the Goal."),
    due_date: int = Field(..., description="The deadline for the Goal expressed as a Unix timestamp in milliseconds."),
    description: str = Field(..., description="A detailed description providing context or additional information about the Goal."),
    multiple_owners: bool = Field(..., description="Set to true to allow multiple users to own this Goal simultaneously, or false to restrict to a single owner."),
    owners: list[int] = Field(..., description="List of user IDs assigned as owners of the Goal. Order is not significant; each item should be a valid integer user ID."),
    color: str = Field(..., description="A color used to visually identify the Goal in the UI, specified as a hex color code."),
) -> dict[str, Any]:
    """Creates a new Goal within a specified Workspace, allowing you to define objectives with ownership, due dates, and visual categorization."""

    # Construct request model with validation
    try:
        _request = _models.CreateGoalRequest(
            path=_models.CreateGoalRequestPath(team_id=team_id),
            body=_models.CreateGoalRequestBody(name=name, due_date=due_date, description=description, multiple_owners=multiple_owners, owners=owners, color=color)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_goal: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/team/{team_id}/goal", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/team/{team_id}/goal"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_goal")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_goal", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_goal",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Goals
@mcp.tool()
async def get_goal(goal_id: str = Field(..., description="The unique UUID identifier of the goal to retrieve.")) -> dict[str, Any]:
    """Retrieves the full details of a specific goal, including its associated targets and current progress. Use this to inspect a goal's configuration and status by its unique identifier."""

    # Construct request model with validation
    try:
        _request = _models.GetGoalRequest(
            path=_models.GetGoalRequestPath(goal_id=goal_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_goal: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/goal/{goal_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/goal/{goal_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_goal")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_goal", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_goal",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Goals
@mcp.tool()
async def update_goal(
    goal_id: str = Field(..., description="The unique identifier (UUID) of the Goal to update."),
    name: str = Field(..., description="The new display name for the Goal."),
    due_date: int = Field(..., description="The due date for the Goal, represented as a Unix timestamp in milliseconds."),
    description: str = Field(..., description="The full replacement description for the Goal. This overwrites the existing description entirely."),
    rem_owners: list[int] = Field(..., description="List of user IDs to remove as owners of the Goal. Order is not significant; each item should be a valid user ID integer."),
    add_owners: list[int] = Field(..., description="List of user IDs to add as owners of the Goal. Order is not significant; each item should be a valid user ID integer."),
    color: str = Field(..., description="The color to assign to the Goal, used for visual categorization in the UI. Provide a valid hex color code."),
) -> dict[str, Any]:
    """Update an existing Goal's properties, including its name, due date, description, color, and ownership. Use this to rename a Goal, adjust its deadline, modify its description, or add and remove assigned owners."""

    # Construct request model with validation
    try:
        _request = _models.UpdateGoalRequest(
            path=_models.UpdateGoalRequestPath(goal_id=goal_id),
            body=_models.UpdateGoalRequestBody(name=name, due_date=due_date, description=description, rem_owners=rem_owners, add_owners=add_owners, color=color)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_goal: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/goal/{goal_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/goal/{goal_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_goal")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_goal", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_goal",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Goals
@mcp.tool()
async def delete_goal(
    goal_id: str = Field(..., description="The unique identifier (UUID) of the Goal to be deleted."),
    content_type: Literal["application/json"] = Field(..., alias="Content-Type", description="The media type of the request body, used to indicate the format of the data being sent."),
) -> dict[str, Any]:
    """Permanently removes a specified Goal from your Workspace. This action is irreversible and will delete all associated goal data."""

    # Construct request model with validation
    try:
        _request = _models.DeleteGoalRequest(
            path=_models.DeleteGoalRequestPath(goal_id=goal_id),
            header=_models.DeleteGoalRequestHeader(content_type=content_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_goal: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/goal/{goal_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/goal/{goal_id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_goal")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_goal", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_goal",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Goals
@mcp.tool()
async def create_key_result(
    goal_id: str = Field(..., description="The unique identifier of the goal to which this key result will be added."),
    name: str = Field(..., description="The display name of the key result that describes the measurable target."),
    owners: list[int] = Field(..., description="An array of user IDs representing the owners responsible for this key result. Order is not significant."),
    type_: str = Field(..., alias="type", description="The measurement type for this key result. Valid values are: `number` (numeric count), `currency` (monetary value), `boolean` (true/false completion), `percentage` (0–100 scale), or `automatic` (derived from linked tasks or lists)."),
    steps_start: int = Field(..., description="The starting value of the target range, representing the baseline or initial progress point."),
    steps_end: int = Field(..., description="The ending value of the target range, representing the goal completion threshold."),
    unit: str = Field(..., description="The unit label associated with the key result value (e.g., a currency code or custom unit name), applicable when the type is `number` or `currency`."),
    task_ids: list[str] = Field(..., description="An array of task IDs to link with this key result, allowing progress to be tracked automatically based on task completion. Order is not significant."),
    list_ids: list[str] = Field(..., description="An array of List IDs to link with this key result, allowing progress to be tracked automatically based on list task completion. Order is not significant."),
) -> dict[str, Any]:
    """Create a new key result (target) within a specified goal to define measurable outcomes. Supports multiple target types including numeric, currency, boolean, percentage, and automatic tracking."""

    # Construct request model with validation
    try:
        _request = _models.CreateKeyResultRequest(
            path=_models.CreateKeyResultRequestPath(goal_id=goal_id),
            body=_models.CreateKeyResultRequestBody(name=name, owners=owners, type_=type_, steps_start=steps_start, steps_end=steps_end, unit=unit, task_ids=task_ids, list_ids=list_ids)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_key_result: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/goal/{goal_id}/key_result", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/goal/{goal_id}/key_result"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_key_result")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_key_result", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_key_result",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Goals
@mcp.tool()
async def update_key_result(
    key_result_id: str = Field(..., description="The unique identifier of the key result to update."),
    steps_current: int = Field(..., description="The current number of steps completed toward the key result target. Should reflect the latest progress value."),
    note: str = Field(..., description="A note or comment describing the current status, blockers, or context for this progress update."),
) -> dict[str, Any]:
    """Update the progress and notes for an existing key result. Use this to record current step completion and add contextual notes to track advancement toward a goal."""

    # Construct request model with validation
    try:
        _request = _models.EditKeyResultRequest(
            path=_models.EditKeyResultRequestPath(key_result_id=key_result_id),
            body=_models.EditKeyResultRequestBody(steps_current=steps_current, note=note)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_key_result: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/key_result/{key_result_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/key_result/{key_result_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_key_result")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_key_result", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_key_result",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Goals
@mcp.tool()
async def delete_key_result(key_result_id: str = Field(..., description="The unique identifier (UUID) of the key result to delete.")) -> dict[str, Any]:
    """Permanently deletes a key result (target) from a Goal. This action is irreversible and removes the specified key result and its associated data."""

    # Construct request model with validation
    try:
        _request = _models.DeleteKeyResultRequest(
            path=_models.DeleteKeyResultRequestPath(key_result_id=key_result_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_key_result: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/key_result/{key_result_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/key_result/{key_result_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_key_result")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_key_result", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_key_result",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Guests
@mcp.tool()
async def invite_workspace_guest(
    team_id: float = Field(..., description="The unique identifier of the Workspace to which the guest will be invited."),
    email: str = Field(..., description="The email address of the guest to invite to the Workspace."),
    can_edit_tags: bool | None = Field(None, description="Whether the guest is permitted to edit tags within the Workspace."),
    can_see_time_spent: bool | None = Field(None, description="Whether the guest can view time spent on tasks."),
    can_see_time_estimated: bool | None = Field(None, description="Whether the guest can view time estimates on tasks."),
    can_create_views: bool | None = Field(None, description="Whether the guest is allowed to create new views."),
    can_see_points_estimated: bool | None = Field(None, description="Whether the guest can view point estimates on tasks."),
    custom_role_id: int | None = Field(None, description="The ID of a custom role to assign to the guest upon invitation."),
) -> dict[str, Any]:
    """Invites a guest user to a Workspace by email on an Enterprise Plan. After inviting, grant the guest access to specific Folders, Lists, or Tasks using the corresponding add-guest endpoints."""

    # Construct request model with validation
    try:
        _request = _models.InviteGuestToWorkspaceRequest(
            path=_models.InviteGuestToWorkspaceRequestPath(team_id=team_id),
            body=_models.InviteGuestToWorkspaceRequestBody(email=email, can_edit_tags=can_edit_tags, can_see_time_spent=can_see_time_spent, can_see_time_estimated=can_see_time_estimated, can_create_views=can_create_views, can_see_points_estimated=can_see_points_estimated, custom_role_id=custom_role_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for invite_workspace_guest: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/team/{team_id}/guest", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/team/{team_id}/guest"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("invite_workspace_guest")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("invite_workspace_guest", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="invite_workspace_guest",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Guests
@mcp.tool()
async def get_guest(
    team_id: float = Field(..., description="The unique identifier of the Workspace (team) containing the guest."),
    guest_id: float = Field(..., description="The unique identifier of the guest user to retrieve."),
) -> dict[str, Any]:
    """Retrieves detailed information about a specific guest user within a Workspace. Available exclusively on the Enterprise Plan."""

    # Construct request model with validation
    try:
        _request = _models.GetGuestRequest(
            path=_models.GetGuestRequestPath(team_id=team_id, guest_id=guest_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_guest: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/team/{team_id}/guest/{guest_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/team/{team_id}/guest/{guest_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_guest")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_guest", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_guest",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Guests
@mcp.tool()
async def update_workspace_guest(
    team_id: float = Field(..., description="The unique identifier of the Workspace where the guest resides."),
    guest_id: float = Field(..., description="The unique identifier of the guest whose settings are being updated."),
    can_see_points_estimated: bool | None = Field(None, description="Whether the guest is allowed to view point estimations on tasks."),
    can_edit_tags: bool | None = Field(None, description="Whether the guest is allowed to create, edit, and delete tags."),
    can_see_time_spent: bool | None = Field(None, description="Whether the guest is allowed to view time tracked (spent) on tasks."),
    can_see_time_estimated: bool | None = Field(None, description="Whether the guest is allowed to view time estimations on tasks."),
    can_create_views: bool | None = Field(None, description="Whether the guest is allowed to create new views within the Workspace."),
    custom_role_id: int | None = Field(None, description="The ID of a custom role to assign to the guest, controlling their permission level within the Workspace."),
) -> dict[str, Any]:
    """Update permission settings and role assignment for a guest on a Workspace. This endpoint is only available on the Enterprise Plan."""

    # Construct request model with validation
    try:
        _request = _models.EditGuestOnWorkspaceRequest(
            path=_models.EditGuestOnWorkspaceRequestPath(team_id=team_id, guest_id=guest_id),
            body=_models.EditGuestOnWorkspaceRequestBody(can_see_points_estimated=can_see_points_estimated, can_edit_tags=can_edit_tags, can_see_time_spent=can_see_time_spent, can_see_time_estimated=can_see_time_estimated, can_create_views=can_create_views, custom_role_id=custom_role_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_workspace_guest: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/team/{team_id}/guest/{guest_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/team/{team_id}/guest/{guest_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_workspace_guest")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_workspace_guest", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_workspace_guest",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Guests
@mcp.tool()
async def remove_workspace_guest(
    team_id: float = Field(..., description="The unique identifier of the Workspace from which the guest will be removed."),
    guest_id: float = Field(..., description="The unique identifier of the guest whose Workspace access will be revoked."),
) -> dict[str, Any]:
    """Revokes a guest's access to the specified Workspace, removing all associated permissions. This endpoint is only available on the Enterprise Plan."""

    # Construct request model with validation
    try:
        _request = _models.RemoveGuestFromWorkspaceRequest(
            path=_models.RemoveGuestFromWorkspaceRequestPath(team_id=team_id, guest_id=guest_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_workspace_guest: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/team/{team_id}/guest/{guest_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/team/{team_id}/guest/{guest_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_workspace_guest")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_workspace_guest", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_workspace_guest",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Guests
@mcp.tool()
async def add_guest_to_task(
    task_id: str = Field(..., description="The unique identifier of the task to share with the guest."),
    guest_id: float = Field(..., description="The unique numeric identifier of the guest user to add to the task."),
    permission_level: str = Field(..., description="The access level granted to the guest on this task. Accepted values are: read (view only), comment, edit, or create (full access)."),
    include_shared: bool | None = Field(None, description="Whether to include details of items shared with the guest in the response. Set to false to exclude shared item details; defaults to true."),
) -> dict[str, Any]:
    """Share a task with a guest user by granting them a specific permission level. This endpoint is only available to Workspaces on the Enterprise Plan."""

    # Construct request model with validation
    try:
        _request = _models.AddGuestToTaskRequest(
            path=_models.AddGuestToTaskRequestPath(task_id=task_id, guest_id=guest_id),
            query=_models.AddGuestToTaskRequestQuery(include_shared=include_shared),
            body=_models.AddGuestToTaskRequestBody(permission_level=permission_level)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_guest_to_task: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/task/{task_id}/guest/{guest_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/task/{task_id}/guest/{guest_id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_guest_to_task")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_guest_to_task", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_guest_to_task",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Guests
@mcp.tool()
async def remove_task_guest(
    task_id: str = Field(..., description="The unique identifier of the task from which the guest's access will be revoked."),
    guest_id: float = Field(..., description="The numeric identifier of the guest user whose access to the task will be removed."),
    include_shared: bool | None = Field(None, description="Controls whether the response includes details of other items shared with the guest. Set to false to exclude shared item details; defaults to true."),
    custom_task_ids: bool | None = Field(None, description="Set to true to reference the task by its custom task ID instead of the standard ClickUp task ID."),
    team_id: float | None = Field(None, description="The Workspace ID required when using custom task IDs. Must be provided alongside custom_task_ids=true to correctly resolve the task."),
) -> dict[str, Any]:
    """Revoke a guest's access to a specific task, removing their ability to view or interact with it. This endpoint is only available on the Enterprise Plan."""

    # Construct request model with validation
    try:
        _request = _models.RemoveGuestFromTaskRequest(
            path=_models.RemoveGuestFromTaskRequestPath(task_id=task_id, guest_id=guest_id),
            query=_models.RemoveGuestFromTaskRequestQuery(include_shared=include_shared, custom_task_ids=custom_task_ids, team_id=team_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_task_guest: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/task/{task_id}/guest/{guest_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/task/{task_id}/guest/{guest_id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_task_guest")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_task_guest", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_task_guest",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Guests
@mcp.tool()
async def add_guest_to_list(
    list_id: float = Field(..., description="The unique identifier of the List to share with the guest."),
    guest_id: float = Field(..., description="The unique identifier of the guest user to add to the List."),
    permission_level: str = Field(..., description="The access level granted to the guest on this List. Accepted values are: read (view only), comment, edit, or create (full access)."),
    include_shared: bool | None = Field(None, description="Whether to include details of items already shared with the guest. Set to false to exclude shared item details; defaults to true."),
) -> dict[str, Any]:
    """Share a List with a guest user by granting them a specific permission level. This endpoint is exclusively available to Workspaces on the Enterprise Plan."""

    # Construct request model with validation
    try:
        _request = _models.AddGuestToListRequest(
            path=_models.AddGuestToListRequestPath(list_id=list_id, guest_id=guest_id),
            query=_models.AddGuestToListRequestQuery(include_shared=include_shared),
            body=_models.AddGuestToListRequestBody(permission_level=permission_level)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_guest_to_list: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/list/{list_id}/guest/{guest_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/list/{list_id}/guest/{guest_id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_guest_to_list")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_guest_to_list", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_guest_to_list",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Guests
@mcp.tool()
async def remove_list_guest(
    list_id: float = Field(..., description="The unique identifier of the List from which the guest's access will be revoked."),
    guest_id: float = Field(..., description="The unique identifier of the guest whose access to the List will be removed."),
    include_shared: bool | None = Field(None, description="Controls whether the response includes details of items shared with the guest. Set to false to exclude shared item details; defaults to true."),
) -> dict[str, Any]:
    """Revokes a guest's access to a specific List, removing their ability to view or interact with it. This endpoint is exclusively available to Workspaces on the Enterprise Plan."""

    # Construct request model with validation
    try:
        _request = _models.RemoveGuestFromListRequest(
            path=_models.RemoveGuestFromListRequestPath(list_id=list_id, guest_id=guest_id),
            query=_models.RemoveGuestFromListRequestQuery(include_shared=include_shared)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_list_guest: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/list/{list_id}/guest/{guest_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/list/{list_id}/guest/{guest_id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_list_guest")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_list_guest", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_list_guest",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Guests
@mcp.tool()
async def add_guest_to_folder(
    folder_id: float = Field(..., description="The unique identifier of the folder to share with the guest."),
    guest_id: float = Field(..., description="The unique identifier of the guest user to whom folder access will be granted."),
    permission_level: str = Field(..., description="The access level granted to the guest for this folder. Accepted values are: read (view only), comment, edit, or create (full access)."),
    include_shared: bool | None = Field(None, description="Whether to include details of items already shared with the guest in the response. Set to false to exclude shared item details."),
) -> dict[str, Any]:
    """Share a folder with a guest user by granting them a specific permission level. This endpoint is only available on the Enterprise Plan."""

    # Construct request model with validation
    try:
        _request = _models.AddGuestToFolderRequest(
            path=_models.AddGuestToFolderRequestPath(folder_id=folder_id, guest_id=guest_id),
            query=_models.AddGuestToFolderRequestQuery(include_shared=include_shared),
            body=_models.AddGuestToFolderRequestBody(permission_level=permission_level)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_guest_to_folder: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/folder/{folder_id}/guest/{guest_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/folder/{folder_id}/guest/{guest_id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_guest_to_folder")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_guest_to_folder", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_guest_to_folder",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Guests
@mcp.tool()
async def remove_folder_guest(
    folder_id: float = Field(..., description="The unique numeric identifier of the Folder from which the guest's access will be revoked."),
    guest_id: float = Field(..., description="The unique numeric identifier of the guest whose access to the Folder will be removed."),
    include_shared: bool | None = Field(None, description="When set to false, the response excludes details of items shared with the guest; defaults to true to include shared item details."),
) -> dict[str, Any]:
    """Revoke a guest's access to a specific Folder, removing their ability to view or interact with its contents. This endpoint is only available on the Enterprise Plan."""

    # Construct request model with validation
    try:
        _request = _models.RemoveGuestFromFolderRequest(
            path=_models.RemoveGuestFromFolderRequestPath(folder_id=folder_id, guest_id=guest_id),
            query=_models.RemoveGuestFromFolderRequestQuery(include_shared=include_shared)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_folder_guest: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/folder/{folder_id}/guest/{guest_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/folder/{folder_id}/guest/{guest_id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_folder_guest")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_folder_guest", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_folder_guest",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Lists
@mcp.tool()
async def list_folder_lists(
    folder_id: float = Field(..., description="The unique identifier of the Folder whose Lists you want to retrieve."),
    archived: bool | None = Field(None, description="When set to true, includes archived Lists in the response alongside active ones. Defaults to false, returning only active Lists."),
) -> dict[str, Any]:
    """Retrieve all Lists contained within a specified Folder. Optionally include archived Lists in the results."""

    # Construct request model with validation
    try:
        _request = _models.GetListsRequest(
            path=_models.GetListsRequestPath(folder_id=folder_id),
            query=_models.GetListsRequestQuery(archived=archived)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_folder_lists: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/folder/{folder_id}/list", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/folder/{folder_id}/list"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_folder_lists")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_folder_lists", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_folder_lists",
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
    folder_id: float = Field(..., description="The unique identifier of the Folder in which the new List will be created."),
    name: str = Field(..., description="The display name for the new List."),
    markdown_content: str | None = Field(None, description="Optional description for the List, formatted using Markdown. Use this field instead of a plain-text content field to apply rich formatting."),
    due_date: int | None = Field(None, description="The due date for the List, expressed as a Unix timestamp in milliseconds."),
    due_date_time: bool | None = Field(None, description="When set to true, the due date includes a specific time component; when false, only the date is considered."),
    priority: int | None = Field(None, description="The priority level for the List, represented as an integer (e.g., 1 = urgent, 2 = high, 3 = normal, 4 = low)."),
    assignee: int | None = Field(None, description="The user ID of the member to assign as the owner of this List."),
    status: str | None = Field(None, description="The color status of the List, which represents a visual label rather than task-level statuses defined within the List."),
) -> dict[str, Any]:
    """Creates a new List inside a specified Folder, allowing you to organize tasks with optional metadata such as due dates, priority, assignee, and a color status."""

    # Construct request model with validation
    try:
        _request = _models.CreateListRequest(
            path=_models.CreateListRequestPath(folder_id=folder_id),
            body=_models.CreateListRequestBody(name=name, markdown_content=markdown_content, due_date=due_date, due_date_time=due_date_time, priority=priority, assignee=assignee, status=status)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_list: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/folder/{folder_id}/list", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/folder/{folder_id}/list"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

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
        headers=_http_headers,
    )

    return _response_data

# Tags: Folders
@mcp.tool()
async def create_folder_from_template(
    space_id: str = Field(..., description="The unique identifier of the Space where the new Folder will be created."),
    template_id: str = Field(..., description="The unique identifier of the Folder template to apply, always prefixed with `t-`. Retrieve available template IDs using the Get Folder Templates endpoint."),
    name: str = Field(..., description="The display name to assign to the newly created Folder."),
    return_immediately: bool | None = Field(None, description="When true, returns the new Folder ID immediately after access checks without waiting for all nested assets to finish being created. When false, the request waits until the Folder and all its contents are fully created before responding."),
    content: str | None = Field(None, description="Optional description text to apply to the new Folder."),
    time_estimate: bool | None = Field(None, description="When true, imports time estimate data (hours, minutes, and seconds) from the template tasks."),
    automation: bool | None = Field(None, description="When true, imports automation rules defined in the template."),
    include_views: bool | None = Field(None, description="When true, imports view configurations defined in the template."),
    old_due_date: bool | None = Field(None, description="When true, imports the original due dates from template tasks."),
    old_start_date: bool | None = Field(None, description="When true, imports the original start dates from template tasks."),
    old_followers: bool | None = Field(None, description="When true, imports the watcher (follower) assignments from template tasks."),
    comment_attachments: bool | None = Field(None, description="When true, imports file attachments from task comments in the template."),
    recur_settings: bool | None = Field(None, description="When true, imports recurring task settings from the template."),
    old_tags: bool | None = Field(None, description="When true, imports tags assigned to tasks in the template."),
    old_statuses: bool | None = Field(None, description="When true, imports the status configuration (status types and workflow) from the template."),
    subtasks: bool | None = Field(None, description="When true, imports subtask structures from the template tasks."),
    custom_type: bool | None = Field(None, description="When true, imports custom task type definitions from the template."),
    old_assignees: bool | None = Field(None, description="When true, imports assignee assignments from template tasks."),
    attachments: bool | None = Field(None, description="When true, imports file attachments from template tasks."),
    comment: bool | None = Field(None, description="When true, imports comments from template tasks."),
    old_status: bool | None = Field(None, description="When true, imports the current status values of tasks from the template."),
    external_dependencies: bool | None = Field(None, description="When true, imports external task dependency relationships from the template."),
    internal_dependencies: bool | None = Field(None, description="When true, imports internal task dependency relationships from the template."),
    priority: bool | None = Field(None, description="When true, imports priority levels assigned to tasks in the template."),
    custom_fields: bool | None = Field(None, description="When true, imports Custom Field definitions and values from template tasks."),
    old_checklists: bool | None = Field(None, description="When true, imports checklist items from template tasks."),
    relationships: bool | None = Field(None, description="When true, imports task relationship links (e.g., linked tasks) from the template."),
    old_subtask_assignees: bool | None = Field(None, description="When true, imports both subtask structures and their assignee assignments together from the template."),
    start_date: str | None = Field(None, description="The project start date used as the anchor point for remapping task dates from the template. Must be provided in ISO 8601 date-time format."),
    due_date: str | None = Field(None, description="The project due date used as the anchor point for remapping task dates from the template. Must be provided in ISO 8601 date-time format."),
    remap_start_date: bool | None = Field(None, description="When true, recalculates and remaps task start dates relative to the provided project start or due date."),
    skip_weekends: bool | None = Field(None, description="When true, excludes Saturday and Sunday when calculating remapped task dates."),
    archived: Literal[1, 2] | None = Field(None, description="Controls whether archived tasks are included: 1 includes archived tasks, 2 includes only archived tasks, and null excludes archived tasks."),
) -> dict[str, Any]:
    """Create a new Folder within a Space using a predefined Folder template, optionally importing nested assets such as lists, tasks, subtasks, custom fields, and more. Supports both synchronous and asynchronous creation via the `return_immediately` parameter."""

    # Construct request model with validation
    try:
        _request = _models.CreateFolderFromTemplateRequest(
            path=_models.CreateFolderFromTemplateRequestPath(space_id=space_id, template_id=template_id),
            body=_models.CreateFolderFromTemplateRequestBody(name=name,
                options=_models.CreateFolderFromTemplateRequestBodyOptions(return_immediately=return_immediately, content=content, time_estimate=time_estimate, automation=automation, include_views=include_views, old_due_date=old_due_date, old_start_date=old_start_date, old_followers=old_followers, comment_attachments=comment_attachments, recur_settings=recur_settings, old_tags=old_tags, old_statuses=old_statuses, subtasks=subtasks, custom_type=custom_type, old_assignees=old_assignees, attachments=attachments, comment=comment, old_status=old_status, external_dependencies=external_dependencies, internal_dependencies=internal_dependencies, priority=priority, custom_fields=custom_fields, old_checklists=old_checklists, relationships=relationships, old_subtask_assignees=old_subtask_assignees, start_date=start_date, due_date=due_date, remap_start_date=remap_start_date, skip_weekends=skip_weekends, archived=archived) if any(v is not None for v in [return_immediately, content, time_estimate, automation, include_views, old_due_date, old_start_date, old_followers, comment_attachments, recur_settings, old_tags, old_statuses, subtasks, custom_type, old_assignees, attachments, comment, old_status, external_dependencies, internal_dependencies, priority, custom_fields, old_checklists, relationships, old_subtask_assignees, start_date, due_date, remap_start_date, skip_weekends, archived]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_folder_from_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/space/{space_id}/folder_template/{template_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/space/{space_id}/folder_template/{template_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_folder_from_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_folder_from_template", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_folder_from_template",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Lists
@mcp.tool()
async def list_folderless_lists(
    space_id: float = Field(..., description="The unique identifier of the Space whose folderless Lists you want to retrieve."),
    archived: bool | None = Field(None, description="When set to true, includes archived Lists in the response alongside active ones."),
) -> dict[str, Any]:
    """Retrieves all Lists within a Space that are not organized inside a Folder. Optionally includes archived Lists in the results."""

    # Construct request model with validation
    try:
        _request = _models.GetFolderlessListsRequest(
            path=_models.GetFolderlessListsRequestPath(space_id=space_id),
            query=_models.GetFolderlessListsRequestQuery(archived=archived)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_folderless_lists: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/space/{space_id}/list", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/space/{space_id}/list"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_folderless_lists")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_folderless_lists", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_folderless_lists",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Lists
@mcp.tool()
async def create_folderless_list(
    space_id: float = Field(..., description="The unique identifier of the Space in which the new List will be created."),
    name: str = Field(..., description="The display name for the new List."),
    markdown_content: str | None = Field(None, description="Description body for the List, formatted in Markdown. Use this field instead of `content` when rich text formatting is needed."),
    due_date: int | None = Field(None, description="The due date for the List, expressed as a Unix timestamp in milliseconds."),
    due_date_time: bool | None = Field(None, description="When set to true, the due date includes a specific time component; when false, only the date is considered."),
    priority: int | None = Field(None, description="The priority level for the List, represented as an integer (e.g., 1 = Urgent, 2 = High, 3 = Normal, 4 = Low)."),
    assignee: int | None = Field(None, description="The user ID of the member to assign as the owner of this List."),
    status: str | None = Field(None, description="Sets the color of the List, which is referred to as its status. This is distinct from the task-level statuses available within the List."),
) -> dict[str, Any]:
    """Creates a new List directly within a Space, without placing it inside a Folder. Use this when you want a top-level List organization within the Space."""

    # Construct request model with validation
    try:
        _request = _models.CreateFolderlessListRequest(
            path=_models.CreateFolderlessListRequestPath(space_id=space_id),
            body=_models.CreateFolderlessListRequestBody(name=name, markdown_content=markdown_content, due_date=due_date, due_date_time=due_date_time, priority=priority, assignee=assignee, status=status)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_folderless_list: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/space/{space_id}/list", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/space/{space_id}/list"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_folderless_list")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_folderless_list", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_folderless_list",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Lists
@mcp.tool()
async def get_list(list_id: float = Field(..., description="The unique numeric identifier of the List to retrieve. To locate this ID, right-click the List in your Sidebar, select Copy link, and extract the last segment of the pasted URL.")) -> dict[str, Any]:
    """Retrieves detailed information about a specific List, including its settings, members, and configuration. Use this to inspect or reference a List's properties by its unique ID."""

    # Construct request model with validation
    try:
        _request = _models.GetListRequest(
            path=_models.GetListRequestPath(list_id=list_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_list: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/list/{list_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/list/{list_id}"
    _http_headers = {}

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
        headers=_http_headers,
    )

    return _response_data

# Tags: Lists
@mcp.tool()
async def update_list(
    list_id: str = Field(..., description="The unique identifier of the List to update."),
    name: str = Field(..., description="The new display name for the List."),
    markdown_content: str | None = Field(None, description="The List's description body formatted in Markdown. Use this field instead of `content` to apply rich text formatting."),
    priority: int | None = Field(None, description="The priority level for the List, represented as an integer (e.g., 1 = urgent, 2 = high, 3 = normal, 4 = low)."),
    assignee: str | None = Field(None, description="The user ID of the member to assign as the List's default assignee."),
    status: str | None = Field(None, description="The color applied to the List, referred to as its status. This controls the List's color indicator, not the task statuses within the List."),
    unset_status: bool | None = Field(None, description="When set to true, removes the currently applied color from the List. Defaults to false, which preserves the existing color."),
    due: str | None = Field(None, description="Due date in ISO 8601 format. Include time (e.g. '2024-06-15T14:30:00') to set due_date_time=true, or date only (e.g. '2024-06-15') for due_date_time=false."),
) -> dict[str, Any]:
    """Update a List's properties including its name, description, priority, assignee, due date, and color. Use this to rename a List or modify any of its metadata fields."""

    # Call helper functions
    due_parsed = parse_due(due)

    # Construct request model with validation
    try:
        _request = _models.UpdateListRequest(
            path=_models.UpdateListRequestPath(list_id=list_id),
            body=_models.UpdateListRequestBody(name=name, markdown_content=markdown_content, priority=priority, assignee=assignee, status=status, unset_status=unset_status, due_date=due_parsed.get('due_date') if due_parsed else None, due_date_time=due_parsed.get('due_date_time') if due_parsed else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_list: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/list/{list_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/list/{list_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_list")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_list", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_list",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Lists
@mcp.tool()
async def delete_list(
    list_id: float = Field(..., description="The unique numeric identifier of the List to be deleted."),
    content_type: Literal["application/json"] = Field(..., alias="Content-Type", description="The media type of the request body, used to indicate the format of the data being sent."),
) -> dict[str, Any]:
    """Permanently deletes a specified List from your Workspace. This action is irreversible and removes the List along with its associated data."""

    # Construct request model with validation
    try:
        _request = _models.DeleteListRequest(
            path=_models.DeleteListRequestPath(list_id=list_id),
            header=_models.DeleteListRequestHeader(content_type=content_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_list: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/list/{list_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/list/{list_id}"
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
async def add_task_to_list(
    list_id: float = Field(..., description="The unique numeric identifier of the list to which the task will be added."),
    task_id: str = Field(..., description="The unique string identifier of the task to add to the specified list."),
) -> dict[str, Any]:
    """Adds an existing task to an additional list, enabling the task to appear in multiple lists simultaneously. Requires the Tasks in Multiple Lists ClickApp to be enabled in the workspace."""

    # Construct request model with validation
    try:
        _request = _models.AddTaskToListRequest(
            path=_models.AddTaskToListRequestPath(list_id=list_id, task_id=task_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_task_to_list: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/list/{list_id}/task/{task_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/list/{list_id}/task/{task_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_task_to_list")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_task_to_list", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_task_to_list",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Lists
@mcp.tool()
async def remove_task_from_list(
    list_id: float = Field(..., description="The unique numeric identifier of the List from which the task should be removed. Must not be the task's home List."),
    task_id: str = Field(..., description="The unique string identifier of the task to remove from the specified List."),
) -> dict[str, Any]:
    """Removes a task from an additional (non-home) List it has been added to. Requires the Tasks in Multiple Lists ClickApp to be enabled; a task cannot be removed from its original home List."""

    # Construct request model with validation
    try:
        _request = _models.RemoveTaskFromListRequest(
            path=_models.RemoveTaskFromListRequestPath(list_id=list_id, task_id=task_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_task_from_list: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/list/{list_id}/task/{task_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/list/{list_id}/task/{task_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_task_from_list")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_task_from_list", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_task_from_list",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Members
@mcp.tool()
async def list_task_members(task_id: str = Field(..., description="The unique identifier of the task whose explicit members you want to retrieve.")) -> dict[str, Any]:
    """Retrieves Workspace members who have been explicitly granted direct access to a specific task. Note: this does not include members with access via a Team, List, Folder, or Space."""

    # Construct request model with validation
    try:
        _request = _models.GetTaskMembersRequest(
            path=_models.GetTaskMembersRequestPath(task_id=task_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_task_members: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/task/{task_id}/member", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/task/{task_id}/member"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_task_members")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_task_members", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_task_members",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Members
@mcp.tool()
async def list_list_members(list_id: float = Field(..., description="The unique numeric identifier of the List whose explicit members you want to retrieve.")) -> dict[str, Any]:
    """Retrieves Workspace members who have been explicitly granted access to a specific List. Note: this does not include members with inherited access via a Team, Folder, or Space."""

    # Construct request model with validation
    try:
        _request = _models.GetListMembersRequest(
            path=_models.GetListMembersRequestPath(list_id=list_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_list_members: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/list/{list_id}/member", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/list/{list_id}/member"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_list_members")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_list_members", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_list_members",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Roles
@mcp.tool()
async def list_custom_roles(
    team_id: float = Field(..., description="The unique identifier of the Workspace whose Custom Roles you want to retrieve."),
    include_members: bool | None = Field(None, description="When set to true, the response will include the list of members assigned to each Custom Role."),
) -> dict[str, Any]:
    """Retrieves all Custom Roles available in the specified Workspace, allowing you to review role definitions and optionally include their member assignments."""

    # Construct request model with validation
    try:
        _request = _models.GetCustomRolesRequest(
            path=_models.GetCustomRolesRequestPath(team_id=team_id),
            query=_models.GetCustomRolesRequestQuery(include_members=include_members)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_custom_roles: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/team/{team_id}/customroles", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/team/{team_id}/customroles"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_custom_roles")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_custom_roles", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_custom_roles",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Shared Hierarchy
@mcp.tool()
async def list_shared_hierarchy(team_id: float = Field(..., description="The unique identifier of the workspace whose shared content you want to retrieve.")) -> dict[str, Any]:
    """Retrieves all tasks, Lists, and Folders that have been shared with the authenticated user within a specified workspace. Useful for discovering shared content accessible to the current user."""

    # Construct request model with validation
    try:
        _request = _models.SharedHierarchyRequest(
            path=_models.SharedHierarchyRequestPath(team_id=team_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_shared_hierarchy: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/team/{team_id}/shared", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/team/{team_id}/shared"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_shared_hierarchy")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_shared_hierarchy", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_shared_hierarchy",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Spaces
@mcp.tool()
async def list_spaces(
    team_id: float = Field(..., description="The unique identifier of the Workspace whose Spaces you want to retrieve."),
    archived: bool | None = Field(None, description="When set to true, returns only archived Spaces; when false or omitted, returns only active Spaces."),
) -> dict[str, Any]:
    """Retrieves all Spaces available within a specified Workspace. Member details are only accessible for private Spaces the authenticated user belongs to."""

    # Construct request model with validation
    try:
        _request = _models.GetSpacesRequest(
            path=_models.GetSpacesRequestPath(team_id=team_id),
            query=_models.GetSpacesRequestQuery(archived=archived)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_spaces: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/team/{team_id}/space", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/team/{team_id}/space"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_spaces")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_spaces", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_spaces",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Spaces
@mcp.tool()
async def create_space(
    team_id: float = Field(..., description="The unique identifier of the Workspace (team) in which the new Space will be created."),
    name: str = Field(..., description="The display name for the new Space."),
    multiple_assignees: bool = Field(..., description="Whether tasks in this Space can be assigned to more than one user simultaneously."),
    due_dates_enabled: bool = Field(..., alias="due_datesEnabled", description="Whether the due dates feature is enabled for tasks in this Space."),
    time_tracking_enabled: bool = Field(..., alias="time_trackingEnabled", description="Whether time tracking is enabled for tasks in this Space."),
    tags_enabled: bool = Field(..., alias="tagsEnabled", description="Whether tags are enabled for tasks in this Space."),
    time_estimates_enabled: bool = Field(..., alias="time_estimatesEnabled", description="Whether time estimates are enabled for tasks in this Space."),
    checklists_enabled: bool = Field(..., alias="checklistsEnabled", description="Whether checklists are enabled for tasks in this Space."),
    custom_fields_enabled: bool = Field(..., alias="custom_fieldsEnabled", description="Whether custom fields are enabled for tasks in this Space."),
    remap_dependencies_enabled: bool = Field(..., alias="remap_dependenciesEnabled", description="Whether dependency dates are automatically remapped when a dependent task's date changes in this Space."),
    dependency_warning_enabled: bool = Field(..., alias="dependency_warningEnabled", description="Whether a warning is shown when a task has unresolved dependencies in this Space."),
    portfolios_enabled: bool = Field(..., alias="portfoliosEnabled", description="Whether the Portfolios feature is enabled for this Space."),
    start_date: bool = Field(..., description="Whether start dates are enabled for tasks in this Space."),
    remap_due_dates: bool = Field(..., description="Whether due dates are automatically remapped for dependent tasks when a parent task's due date changes."),
    remap_closed_due_date: bool = Field(..., description="Whether due dates on closed tasks are remapped when rescheduling dependent tasks in this Space."),
) -> dict[str, Any]:
    """Creates a new Space within a specified Workspace, allowing configuration of its name, assignee settings, and feature toggles such as due dates, time tracking, tags, and dependencies."""

    # Construct request model with validation
    try:
        _request = _models.CreateSpaceRequest(
            path=_models.CreateSpaceRequestPath(team_id=team_id),
            body=_models.CreateSpaceRequestBody(name=name, multiple_assignees=multiple_assignees,
                features=_models.CreateSpaceRequestBodyFeatures(
                    due_dates=_models.CreateSpaceRequestBodyFeaturesDueDates(enabled=due_dates_enabled, start_date=start_date, remap_due_dates=remap_due_dates, remap_closed_due_date=remap_closed_due_date),
                    time_tracking=_models.CreateSpaceRequestBodyFeaturesTimeTracking(enabled=time_tracking_enabled),
                    tags=_models.CreateSpaceRequestBodyFeaturesTags(enabled=tags_enabled),
                    time_estimates=_models.CreateSpaceRequestBodyFeaturesTimeEstimates(enabled=time_estimates_enabled),
                    checklists=_models.CreateSpaceRequestBodyFeaturesChecklists(enabled=checklists_enabled),
                    custom_fields=_models.CreateSpaceRequestBodyFeaturesCustomFields(enabled=custom_fields_enabled),
                    remap_dependencies=_models.CreateSpaceRequestBodyFeaturesRemapDependencies(enabled=remap_dependencies_enabled),
                    dependency_warning=_models.CreateSpaceRequestBodyFeaturesDependencyWarning(enabled=dependency_warning_enabled),
                    portfolios=_models.CreateSpaceRequestBodyFeaturesPortfolios(enabled=portfolios_enabled)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_space: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/team/{team_id}/space", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/team/{team_id}/space"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_space")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_space", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_space",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Spaces
@mcp.tool()
async def get_space(space_id: float = Field(..., description="The unique numeric identifier of the Space to retrieve.")) -> dict[str, Any]:
    """Retrieves details for a specific Space within a Workspace, including its settings and configuration."""

    # Construct request model with validation
    try:
        _request = _models.GetSpaceRequest(
            path=_models.GetSpaceRequestPath(space_id=space_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_space: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/space/{space_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/space/{space_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_space")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_space", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_space",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Spaces
@mcp.tool()
async def update_space(
    space_id: float = Field(..., description="The unique identifier of the Space to update."),
    name: str = Field(..., description="The new display name for the Space."),
    color: str = Field(..., description="The color associated with the Space, used for visual identification in the UI."),
    private: bool = Field(..., description="Whether the Space is private; private Spaces are only visible to invited members."),
    admin_can_manage: bool = Field(..., description="Whether workspace admins are permitted to manage this private Space. Enabling or restricting this setting is an Enterprise Plan feature."),
    multiple_assignees: bool = Field(..., description="Whether tasks in this Space can be assigned to multiple members simultaneously."),
    due_dates_enabled: bool = Field(..., alias="due_datesEnabled", description="Whether the Due Dates ClickApp is enabled for this Space, allowing tasks to have due date fields."),
    time_tracking_enabled: bool = Field(..., alias="time_trackingEnabled", description="Whether the Time Tracking ClickApp is enabled for this Space, allowing members to log time on tasks."),
    tags_enabled: bool = Field(..., alias="tagsEnabled", description="Whether the Tags ClickApp is enabled for this Space, allowing tasks to be labeled with tags."),
    time_estimates_enabled: bool = Field(..., alias="time_estimatesEnabled", description="Whether the Time Estimates ClickApp is enabled for this Space, allowing estimated time to be set on tasks."),
    checklists_enabled: bool = Field(..., alias="checklistsEnabled", description="Whether the Checklists ClickApp is enabled for this Space, allowing checklist items to be added to tasks."),
    custom_fields_enabled: bool = Field(..., alias="custom_fieldsEnabled", description="Whether the Custom Fields ClickApp is enabled for this Space, allowing custom data fields to be defined on tasks."),
    remap_dependencies_enabled: bool = Field(..., alias="remap_dependenciesEnabled", description="Whether dependency remapping is enabled, automatically adjusting dependent task dates when a predecessor's dates change."),
    dependency_warning_enabled: bool = Field(..., alias="dependency_warningEnabled", description="Whether a warning is shown when a task with unresolved dependencies is marked complete."),
    portfolios_enabled: bool = Field(..., alias="portfoliosEnabled", description="Whether the Portfolios ClickApp is enabled for this Space, allowing tasks and lists to be tracked in portfolio views."),
    start_date: bool = Field(..., description="Whether tasks in this Space support a start date field in addition to a due date."),
    remap_due_dates: bool = Field(..., description="Whether due dates on dependent tasks are automatically remapped when a predecessor task's due date changes."),
    remap_closed_due_date: bool = Field(..., description="Whether due dates on closed dependent tasks are also remapped when a predecessor task's due date changes."),
) -> dict[str, Any]:
    """Update a Space's settings including its name, color, privacy, and enabled ClickApps such as due dates, time tracking, tags, and custom fields."""

    # Construct request model with validation
    try:
        _request = _models.UpdateSpaceRequest(
            path=_models.UpdateSpaceRequestPath(space_id=space_id),
            body=_models.UpdateSpaceRequestBody(name=name, color=color, private=private, admin_can_manage=admin_can_manage, multiple_assignees=multiple_assignees,
                features=_models.UpdateSpaceRequestBodyFeatures(
                    due_dates=_models.UpdateSpaceRequestBodyFeaturesDueDates(enabled=due_dates_enabled, start_date=start_date, remap_due_dates=remap_due_dates, remap_closed_due_date=remap_closed_due_date),
                    time_tracking=_models.UpdateSpaceRequestBodyFeaturesTimeTracking(enabled=time_tracking_enabled),
                    tags=_models.UpdateSpaceRequestBodyFeaturesTags(enabled=tags_enabled),
                    time_estimates=_models.UpdateSpaceRequestBodyFeaturesTimeEstimates(enabled=time_estimates_enabled),
                    checklists=_models.UpdateSpaceRequestBodyFeaturesChecklists(enabled=checklists_enabled),
                    custom_fields=_models.UpdateSpaceRequestBodyFeaturesCustomFields(enabled=custom_fields_enabled),
                    remap_dependencies=_models.UpdateSpaceRequestBodyFeaturesRemapDependencies(enabled=remap_dependencies_enabled),
                    dependency_warning=_models.UpdateSpaceRequestBodyFeaturesDependencyWarning(enabled=dependency_warning_enabled),
                    portfolios=_models.UpdateSpaceRequestBodyFeaturesPortfolios(enabled=portfolios_enabled)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_space: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/space/{space_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/space/{space_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_space")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_space", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_space",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Spaces
@mcp.tool()
async def delete_space(space_id: float = Field(..., description="The unique numeric identifier of the Space to be deleted.")) -> dict[str, Any]:
    """Permanently deletes a Space from your Workspace. This action is irreversible and removes the Space along with its associated data."""

    # Construct request model with validation
    try:
        _request = _models.DeleteSpaceRequest(
            path=_models.DeleteSpaceRequestPath(space_id=space_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_space: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/space/{space_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/space/{space_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_space")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_space", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_space",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tags
@mcp.tool()
async def list_space_tags(
    space_id: float = Field(..., description="The unique identifier of the Space whose tags you want to retrieve."),
    content_type: Literal["application/json"] = Field(..., alias="Content-Type", description="The media type format for the request, indicating the content should be sent as JSON."),
) -> dict[str, Any]:
    """Retrieve all task tags available in a specified Space. Use this to discover tags that can be applied to tasks within the Space."""

    # Construct request model with validation
    try:
        _request = _models.GetSpaceTagsRequest(
            path=_models.GetSpaceTagsRequestPath(space_id=space_id),
            header=_models.GetSpaceTagsRequestHeader(content_type=content_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_space_tags: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/space/{space_id}/tag", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/space/{space_id}/tag"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_space_tags")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_space_tags", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_space_tags",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tags
@mcp.tool()
async def create_space_tag(
    space_id: float = Field(..., description="The unique identifier of the Space where the new tag will be created."),
    name: str = Field(..., description="The display name of the tag as it will appear throughout the Space."),
    tag_fg: str = Field(..., description="The foreground (text) color of the tag, specified as a hex color code."),
    tag_bg: str = Field(..., description="The background color of the tag, specified as a hex color code."),
) -> dict[str, Any]:
    """Creates a new tag in the specified Space, allowing tasks within that Space to be categorized and labeled with custom colors."""

    # Construct request model with validation
    try:
        _request = _models.CreateSpaceTagRequest(
            path=_models.CreateSpaceTagRequestPath(space_id=space_id),
            body=_models.CreateSpaceTagRequestBody(tag=_models.CreateSpaceTagRequestBodyTag(name=name, tag_fg=tag_fg, tag_bg=tag_bg))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_space_tag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/space/{space_id}/tag", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/space/{space_id}/tag"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_space_tag")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_space_tag", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_space_tag",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tags
@mcp.tool()
async def update_space_tag(
    space_id: float = Field(..., description="The unique identifier of the space that contains the tag to be updated."),
    tag_name: str = Field(..., description="The current name of the tag to be edited, used to identify the tag within the space."),
    name: str = Field(..., description="The new display name to assign to the tag."),
    fg_color: str = Field(..., description="The foreground (text) color for the tag, typically provided as a hex color code."),
    bg_color: str = Field(..., description="The background color for the tag, typically provided as a hex color code."),
) -> dict[str, Any]:
    """Updates the name and color properties of an existing tag within a specified space. Use this to rename a tag or change its foreground and background display colors."""

    # Construct request model with validation
    try:
        _request = _models.EditSpaceTagRequest(
            path=_models.EditSpaceTagRequestPath(space_id=space_id, tag_name=tag_name),
            body=_models.EditSpaceTagRequestBody(tag=_models.EditSpaceTagRequestBodyTag(name=name, fg_color=fg_color, bg_color=bg_color))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_space_tag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/space/{space_id}/tag/{tag_name}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/space/{space_id}/tag/{tag_name}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_space_tag")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_space_tag", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_space_tag",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tags
@mcp.tool()
async def delete_space_tag(
    space_id: float = Field(..., description="The unique numeric identifier of the Space from which the tag will be deleted."),
    tag_name: str = Field(..., description="The URL path identifier of the tag to delete, typically matching the tag's display name."),
    name: str = Field(..., description="The display name of the tag being deleted, used to identify the tag in the request body."),
    tag_fg: str = Field(..., description="The foreground (text) color of the tag, specified as a hex color code."),
    tag_bg: str = Field(..., description="The background color of the tag, specified as a hex color code."),
) -> dict[str, Any]:
    """Permanently removes a task tag from a specified Space. The tag will no longer be available for tasks within that Space."""

    # Construct request model with validation
    try:
        _request = _models.DeleteSpaceTagRequest(
            path=_models.DeleteSpaceTagRequestPath(space_id=space_id, tag_name=tag_name),
            body=_models.DeleteSpaceTagRequestBody(tag=_models.DeleteSpaceTagRequestBodyTag(name=name, tag_fg=tag_fg, tag_bg=tag_bg))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_space_tag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/space/{space_id}/tag/{tag_name}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/space/{space_id}/tag/{tag_name}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_space_tag")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_space_tag", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_space_tag",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tags
@mcp.tool()
async def add_tag_to_task(
    task_id: str = Field(..., description="The unique identifier of the task to which the tag will be added."),
    tag_name: str = Field(..., description="The name of the tag to add to the task. Must match an existing tag name exactly."),
    content_type: Literal["application/json"] = Field(..., alias="Content-Type", description="The media type of the request body, which must indicate JSON format."),
    custom_task_ids: bool | None = Field(None, description="Set to true to reference the task by its custom task ID instead of the default system-generated task ID."),
    team_id: float | None = Field(None, description="The Workspace ID required when using custom task IDs. Must be provided alongside custom_task_ids=true to correctly resolve the task."),
) -> dict[str, Any]:
    """Adds an existing tag to a specified task, associating it for organization and filtering purposes. Supports referencing tasks by custom task ID when the appropriate parameters are provided."""

    # Construct request model with validation
    try:
        _request = _models.AddTagToTaskRequest(
            path=_models.AddTagToTaskRequestPath(task_id=task_id, tag_name=tag_name),
            query=_models.AddTagToTaskRequestQuery(custom_task_ids=custom_task_ids, team_id=team_id),
            header=_models.AddTagToTaskRequestHeader(content_type=content_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_tag_to_task: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/task/{task_id}/tag/{tag_name}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/task/{task_id}/tag/{tag_name}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_tag_to_task")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_tag_to_task", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_tag_to_task",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tags
@mcp.tool()
async def remove_task_tag(
    task_id: str = Field(..., description="The unique identifier of the task from which the tag will be removed."),
    tag_name: str = Field(..., description="The name of the tag to remove from the task. Must match the tag name exactly as it exists in the Space."),
    content_type: Literal["application/json"] = Field(..., alias="Content-Type", description="The media type of the request body, indicating the format of the payload being sent."),
    custom_task_ids: bool | None = Field(None, description="Set to true if referencing the task by its custom task ID instead of the default ClickUp task ID. Must be used in conjunction with the team_id parameter."),
    team_id: float | None = Field(None, description="The Workspace ID (team) required when custom_task_ids is set to true. Used to resolve the correct task when referencing by custom task ID."),
) -> dict[str, Any]:
    """Removes a specific tag from a task without deleting the tag from the Space. The tag remains available for use on other tasks within the Space."""

    # Construct request model with validation
    try:
        _request = _models.RemoveTagFromTaskRequest(
            path=_models.RemoveTagFromTaskRequestPath(task_id=task_id, tag_name=tag_name),
            query=_models.RemoveTagFromTaskRequestQuery(custom_task_ids=custom_task_ids, team_id=team_id),
            header=_models.RemoveTagFromTaskRequestHeader(content_type=content_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_task_tag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/task/{task_id}/tag/{tag_name}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/task/{task_id}/tag/{tag_name}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_task_tag")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_task_tag", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_task_tag",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tasks
@mcp.tool()
async def list_tasks(
    list_id: float = Field(..., description="The unique numeric ID of the List whose tasks you want to retrieve. To find it, hover over the List in the Sidebar, click the ellipsis menu, select Copy link, and extract the number following '/li' in the URL."),
    archived: bool | None = Field(None, description="When true, includes archived tasks in the response. Archived tasks are excluded by default."),
    include_markdown_description: bool | None = Field(None, description="When true, task descriptions are returned in Markdown format instead of plain text."),
    page: int | None = Field(None, description="Zero-based page number for paginated results. Increment to retrieve subsequent pages of up to 100 tasks each."),
    order_by: str | None = Field(None, description="Field by which to sort the returned tasks. Defaults to 'created' if not specified."),
    reverse: bool | None = Field(None, description="When true, reverses the sort order of the returned tasks."),
    subtasks: bool | None = Field(None, description="When true, subtasks are included in the response alongside top-level tasks. Subtasks are excluded by default."),
    statuses: list[str] | None = Field(None, description="Array of status names to filter tasks by. Only tasks matching one of the provided statuses are returned. To include closed tasks, also set include_closed to true."),
    include_closed: bool | None = Field(None, description="When true, closed tasks are included in the response. Closed tasks are excluded by default."),
    include_timl: bool | None = Field(None, description="When true, tasks that belong to multiple Lists (Tasks in Multiple Lists) are included in the response, even if their home List differs from the specified list_id. Excluded by default."),
    assignees: list[str] | None = Field(None, description="Array of assignee user IDs to filter tasks by. Only tasks assigned to at least one of the specified users are returned."),
    watchers: list[str] | None = Field(None, description="Array of watcher user IDs to filter tasks by. Only tasks watched by at least one of the specified users are returned."),
    tags: list[str] | None = Field(None, description="Array of tag names to filter tasks by. Only tasks that have at least one of the specified tags are returned."),
    due_date_gt: int | None = Field(None, description="Returns only tasks with a due date strictly after this Unix timestamp in milliseconds."),
    due_date_lt: int | None = Field(None, description="Returns only tasks with a due date strictly before this Unix timestamp in milliseconds."),
    date_created_gt: int | None = Field(None, description="Returns only tasks created strictly after this Unix timestamp in milliseconds."),
    date_created_lt: int | None = Field(None, description="Returns only tasks created strictly before this Unix timestamp in milliseconds."),
    date_updated_gt: int | None = Field(None, description="Returns only tasks last updated strictly after this Unix timestamp in milliseconds."),
    date_updated_lt: int | None = Field(None, description="Returns only tasks last updated strictly before this Unix timestamp in milliseconds."),
    date_done_gt: int | None = Field(None, description="Returns only tasks marked done strictly after this Unix timestamp in milliseconds."),
    date_done_lt: int | None = Field(None, description="Returns only tasks marked done strictly before this Unix timestamp in milliseconds."),
    custom_fields: list[str] | None = Field(None, description="Array of Custom Field filter objects for filtering tasks across multiple Custom Fields simultaneously. Each object must specify a field_id, an operator, and a value. Use custom_field instead when filtering on a single Custom Field."),
    custom_field: list[str] | None = Field(None, description="Array representing a single Custom Field filter, used when filtering tasks by exactly one Custom Field or Custom Relationship. Use custom_fields when filtering across multiple Custom Fields at once."),
    custom_items: list[float] | None = Field(None, description="Array of custom task type identifiers to filter by. Use 0 for standard tasks, 1 for Milestones, or any other workspace-defined custom task type ID."),
) -> dict[str, Any]:
    """Retrieve up to 100 tasks per page from a specified List, returning only tasks whose home List matches the given list_id by default. Use filtering, sorting, and pagination parameters to narrow results by status, assignee, tags, dates, custom fields, and more."""

    # Construct request model with validation
    try:
        _request = _models.GetTasksRequest(
            path=_models.GetTasksRequestPath(list_id=list_id),
            query=_models.GetTasksRequestQuery(archived=archived, include_markdown_description=include_markdown_description, page=page, order_by=order_by, reverse=reverse, subtasks=subtasks, statuses=statuses, include_closed=include_closed, include_timl=include_timl, assignees=assignees, watchers=watchers, tags=tags, due_date_gt=due_date_gt, due_date_lt=due_date_lt, date_created_gt=date_created_gt, date_created_lt=date_created_lt, date_updated_gt=date_updated_gt, date_updated_lt=date_updated_lt, date_done_gt=date_done_gt, date_done_lt=date_done_lt, custom_fields=custom_fields, custom_field=custom_field, custom_items=custom_items)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_tasks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/list/{list_id}/task", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/list/{list_id}/task"
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
    list_id: float = Field(..., description="The unique numeric ID of the list in which the task will be created."),
    name: str = Field(..., description="The display name of the task."),
    assignees: list[int] | None = Field(None, description="List of user IDs to assign to the task. Order is not significant."),
    archived: bool | None = Field(None, description="Whether the task should be created in an archived state."),
    group_assignees: list[str] | None = Field(None, description="List of user group IDs to assign to the task. Order is not significant."),
    tags: list[str] | None = Field(None, description="List of tag names to apply to the task. Order is not significant."),
    status: str | None = Field(None, description="The status to assign to the task. Must match an existing status name defined in the list."),
    priority: int | None = Field(None, description="The priority level for the task, where 1 is urgent, 2 is high, 3 is normal, and 4 is low."),
    due_date: int | None = Field(None, description="The due date for the task as a Unix timestamp in milliseconds."),
    due_date_time: bool | None = Field(None, description="Set to true to include a specific time component with the due date, or false to treat it as a date-only value."),
    time_estimate: int | None = Field(None, description="The estimated time to complete the task, expressed in milliseconds."),
    start_date: int | None = Field(None, description="The start date for the task as a Unix timestamp in milliseconds."),
    start_date_time: bool | None = Field(None, description="Set to true to include a specific time component with the start date, or false to treat it as a date-only value."),
    points: float | None = Field(None, description="The number of sprint points to assign to the task."),
    notify_all: bool | None = Field(None, description="When true, the task creator is also notified upon creation; all other assignees and watchers are always notified regardless of this setting."),
    parent: str | None = Field(None, description="The ID of an existing task to nest this new task under as a subtask. The parent task must reside in the same list specified in the path and may itself be a subtask."),
    markdown_content: str | None = Field(None, description="Markdown-formatted description for the task. Takes precedence over the plain-text description field if both are provided."),
    links_to: str | None = Field(None, description="The ID of an existing task to create a linked dependency relationship with the new task."),
    check_required_custom_fields: bool | None = Field(None, description="When true, enforces validation of any required Custom Fields on the task; by default required Custom Fields are ignored during API task creation."),
    custom_fields: list[_models.CreateTaskBodyCustomFieldsItemV0 | _models.CreateTaskBodyCustomFieldsItemV1 | _models.CreateTaskBodyCustomFieldsItemV2 | _models.CreateTaskBodyCustomFieldsItemV3 | _models.CreateTaskBodyCustomFieldsItemV4 | _models.CreateTaskBodyCustomFieldsItemV5 | _models.CreateTaskBodyCustomFieldsItemV6 | _models.CreateTaskBodyCustomFieldsItemV7 | _models.CreateTaskBodyCustomFieldsItemV8 | _models.CreateTaskBodyCustomFieldsItemV9 | _models.CreateTaskBodyCustomFieldsItemV10 | _models.CreateTaskBodyCustomFieldsItemV11 | _models.CreateTaskBodyCustomFieldsItemV12 | _models.CreateTaskBodyCustomFieldsItemV13 | _models.CreateTaskBodyCustomFieldsItemV14] | None = Field(None, description="List of Custom Field objects to populate on the new task, each specifying a field ID and its value. Object and array type fields can be cleared by passing a null value."),
    custom_item_id: float | None = Field(None, description="The custom task type ID to apply to this task. Omit or pass null to create a standard task; retrieve available custom type IDs using the Get Custom Task Types endpoint."),
) -> dict[str, Any]:
    """Creates a new task in the specified list, supporting full configuration including assignees, scheduling, custom fields, subtask relationships, and sprint points."""

    # Construct request model with validation
    try:
        _request = _models.CreateTaskRequest(
            path=_models.CreateTaskRequestPath(list_id=list_id),
            body=_models.CreateTaskRequestBody(name=name, assignees=assignees, archived=archived, group_assignees=group_assignees, tags=tags, status=status, priority=priority, due_date=due_date, due_date_time=due_date_time, time_estimate=time_estimate, start_date=start_date, start_date_time=start_date_time, points=points, notify_all=notify_all, parent=parent, markdown_content=markdown_content, links_to=links_to, check_required_custom_fields=check_required_custom_fields, custom_fields=custom_fields, custom_item_id=custom_item_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_task: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/list/{list_id}/task", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/list/{list_id}/task"
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
async def get_task(
    task_id: str = Field(..., description="The unique identifier of the task to retrieve. When using custom task IDs, set custom_task_ids to true and provide the team_id."),
    custom_task_ids: bool | None = Field(None, description="Set to true to reference the task by its custom task ID instead of the default ClickUp task ID. Must be used together with the team_id parameter."),
    team_id: float | None = Field(None, description="The Workspace ID required when custom_task_ids is set to true. Identifies which Workspace the custom task ID belongs to."),
    include_subtasks: bool | None = Field(None, description="Set to true to include all subtasks nested under the task in the response. Defaults to false."),
    include_markdown_description: bool | None = Field(None, description="Set to true to return the task description formatted in Markdown instead of plain text."),
    custom_fields: list[str] | None = Field(None, description="Filter or include tasks matching specific Custom Field values using a JSON array of field conditions. Each condition specifies a field_id, a comparison operator, and a value. Supports Custom Relationships."),
) -> dict[str, Any]:
    """Retrieve detailed information about a specific task, including its fields, assignees, status, and attachments. Docs attached to the task are not returned."""

    # Construct request model with validation
    try:
        _request = _models.GetTaskRequest(
            path=_models.GetTaskRequestPath(task_id=task_id),
            query=_models.GetTaskRequestQuery(custom_task_ids=custom_task_ids, team_id=team_id, include_subtasks=include_subtasks, include_markdown_description=include_markdown_description, custom_fields=custom_fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_task: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/task/{task_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/task/{task_id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
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
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tasks
@mcp.tool()
async def update_task(
    task_id: str = Field(..., description="The unique identifier of the task to update."),
    assignees_add: list[int] = Field(..., alias="assigneesAdd", description="List of user IDs to add as assignees to the task. Order is not significant."),
    watchers_add: list[int] = Field(..., alias="watchersAdd", description="List of user IDs to add as watchers on the task. Order is not significant."),
    assignees_rem: list[int] = Field(..., alias="assigneesRem", description="List of user IDs to remove from the task's assignees. Order is not significant."),
    watchers_rem: list[int] = Field(..., alias="watchersRem", description="List of user IDs to remove from the task's watchers. Order is not significant."),
    custom_item_id: float | None = Field(None, description="The custom task type ID to assign to this task. Set to null to use the default 'Task' type. Retrieve available custom task type IDs using the Get Custom Task Types endpoint."),
    name: str | None = Field(None, description="The display name of the task."),
    markdown_content: str | None = Field(None, description="Markdown-formatted description for the task. Takes precedence over the plain-text description field if both are provided."),
    status: str | None = Field(None, description="The status of the task. Must match a valid status name defined in the task's list."),
    priority: int | None = Field(None, description="The priority level of the task, where 1 is urgent, 2 is high, 3 is normal, and 4 is low."),
    due_date: int | None = Field(None, description="The due date for the task as a Unix timestamp in milliseconds."),
    due_date_time: bool | None = Field(None, description="Set to true if the due date includes a specific time component, or false if it is a date-only value."),
    parent: str | None = Field(None, description="The task ID of the parent task to move this subtask under. Cannot be used to convert a subtask back into a top-level task by passing null."),
    time_estimate: int | None = Field(None, description="The estimated time to complete the task, in milliseconds."),
    start_date: int | None = Field(None, description="The start date for the task as a Unix timestamp in milliseconds."),
    start_date_time: bool | None = Field(None, description="Set to true if the start date includes a specific time component, or false if it is a date-only value."),
    points: float | None = Field(None, description="The number of Sprint Points to assign to this task."),
    group_assignees_add: list[str] | None = Field(None, alias="group_assigneesAdd", description="List of group (team) IDs to add as group assignees to the task. Order is not significant."),
    group_assignees_rem: list[str] | None = Field(None, alias="group_assigneesRem", description="List of group (team) IDs to remove from the task's group assignees. Order is not significant."),
    archived: bool | None = Field(None, description="Set to true to archive the task, or false to unarchive it."),
) -> dict[str, Any]:
    """Update one or more fields on an existing task by its task ID. Supports updating metadata, assignments, dates, status, priority, and more."""

    # Construct request model with validation
    try:
        _request = _models.UpdateTaskRequest(
            path=_models.UpdateTaskRequestPath(task_id=task_id),
            body=_models.UpdateTaskRequestBody(custom_item_id=custom_item_id, name=name, markdown_content=markdown_content, status=status, priority=priority, due_date=due_date, due_date_time=due_date_time, parent=parent, time_estimate=time_estimate, start_date=start_date, start_date_time=start_date_time, points=points, archived=archived,
                assignees=_models.UpdateTaskRequestBodyAssignees(add=assignees_add, rem=assignees_rem),
                group_assignees=_models.UpdateTaskRequestBodyGroupAssignees(add=group_assignees_add, rem=group_assignees_rem) if any(v is not None for v in [group_assignees_add, group_assignees_rem]) else None,
                watchers=_models.UpdateTaskRequestBodyWatchers(add=watchers_add, rem=watchers_rem))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_task: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/task/{task_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/task/{task_id}"
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
async def delete_task(
    task_id: str = Field(..., description="The unique identifier of the task to delete. Use the task's custom ID instead if the custom_task_ids parameter is set to true."),
    content_type: Literal["application/json"] = Field(..., alias="Content-Type", description="The media type of the request body, which must be set to indicate JSON-formatted content."),
    custom_task_ids: bool | None = Field(None, description="Set to true to reference the task using its custom task ID rather than the default system-generated task ID."),
    team_id: float | None = Field(None, description="The Workspace ID (team ID) required when using custom task IDs. Must be provided alongside custom_task_ids=true to correctly resolve the task."),
) -> dict[str, Any]:
    """Permanently deletes a task from your Workspace by its task ID. This action is irreversible and removes the task and its associated data."""

    # Construct request model with validation
    try:
        _request = _models.DeleteTaskRequest(
            path=_models.DeleteTaskRequestPath(task_id=task_id),
            query=_models.DeleteTaskRequestQuery(custom_task_ids=custom_task_ids, team_id=team_id),
            header=_models.DeleteTaskRequestHeader(content_type=content_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_task: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/task/{task_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/task/{task_id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

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
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tasks
@mcp.tool()
async def list_tasks_by_team(
    team_id: float = Field(..., alias="team_Id", description="The unique numeric ID of the Workspace (team) from which to retrieve tasks."),
    page: int | None = Field(None, description="Zero-based page number for paginated results; begin with 0 for the first page and increment to retrieve subsequent pages."),
    order_by: str | None = Field(None, description="Field by which to sort the returned tasks. Defaults to `created` if not specified. Accepted values are `id`, `created`, `updated`, and `due_date`."),
    reverse: bool | None = Field(None, description="When set to true, reverses the sort order of the results so that the most recent or highest-value items appear first."),
    subtasks: bool | None = Field(None, description="When set to true, includes subtasks in the response. Subtasks are excluded by default."),
    space_ids: list[str] | None = Field(None, description="Array of Space IDs used to filter tasks to only those belonging to the specified Spaces. Multiple values are supported."),
    project_ids: list[str] | None = Field(None, description="Array of Folder IDs (referred to as `project_ids` in the API) used to filter tasks to only those within the specified Folders. Multiple values are supported."),
    list_ids: list[str] | None = Field(None, description="Array of List IDs used to filter tasks to only those belonging to the specified Lists. Multiple values are supported."),
    statuses: list[str] | None = Field(None, description="Array of status names used to filter tasks by their current status. Use URL encoding for status names that contain spaces (e.g., a space character is represented as `%20`)."),
    include_closed: bool | None = Field(None, description="When set to true, includes closed tasks in the response alongside open tasks. Closed tasks are excluded by default."),
    assignees: list[str] | None = Field(None, description="Array of ClickUp user IDs used to filter tasks by assignee. Multiple assignee IDs can be provided to match tasks assigned to any of the specified users."),
    tags: list[str] | None = Field(None, description="Array of tag names used to filter tasks that have all specified tags applied. Use URL encoding for tag names containing spaces (e.g., a space character is represented as `%20`)."),
    due_date_gt: int | None = Field(None, description="Returns only tasks with a due date strictly after this value, expressed as a Unix timestamp in milliseconds."),
    due_date_lt: int | None = Field(None, description="Returns only tasks with a due date strictly before this value, expressed as a Unix timestamp in milliseconds."),
    date_created_gt: int | None = Field(None, description="Returns only tasks created strictly after this value, expressed as a Unix timestamp in milliseconds."),
    date_created_lt: int | None = Field(None, description="Returns only tasks created strictly before this value, expressed as a Unix timestamp in milliseconds."),
    date_updated_gt: int | None = Field(None, description="Returns only tasks last updated strictly after this value, expressed as a Unix timestamp in milliseconds."),
    date_updated_lt: int | None = Field(None, description="Returns only tasks last updated strictly before this value, expressed as a Unix timestamp in milliseconds."),
    date_done_gt: int | None = Field(None, description="Returns only tasks marked as done strictly after this value, expressed as a Unix timestamp in milliseconds."),
    date_done_lt: int | None = Field(None, description="Returns only tasks marked as done strictly before this value, expressed as a Unix timestamp in milliseconds."),
    parent: str | None = Field(None, description="The ID of a parent task; when provided, the response returns the subtasks belonging to that parent task rather than top-level tasks."),
    include_markdown_description: bool | None = Field(None, description="When set to true, task description fields in the response are returned in Markdown format instead of plain text."),
    custom_items: list[float] | None = Field(None, description="Array of custom task type identifiers used to filter results. Use `0` for standard tasks, `1` for Milestones, or any other numeric ID corresponding to a custom task type defined in the Workspace."),
    custom_fields_field_ids: list[str] | None = Field(None, description="List of Custom Field IDs to filter by (one per filter entry)."),
    custom_fields_operators: list[str] | None = Field(None, description="List of operators for each Custom Field filter (e.g. '=', '<', '>', '!='). Must match length of custom_fields_field_ids."),
    custom_fields_values: list[str] | None = Field(None, description="List of values for each Custom Field filter. Must match length of custom_fields_field_ids."),
) -> dict[str, Any]:
    """Retrieve tasks from a Workspace that match specified filter criteria such as status, assignee, due date, tags, and location (Space, Folder, or List). Results are paginated at 100 tasks per page and limited to tasks the authenticated user can access."""

    # Call helper functions
    custom_fields = build_custom_fields(custom_fields_field_ids, custom_fields_operators, custom_fields_values)

    # Construct request model with validation
    try:
        _request = _models.GetFilteredTeamTasksRequest(
            path=_models.GetFilteredTeamTasksRequestPath(team_id=team_id),
            query=_models.GetFilteredTeamTasksRequestQuery(page=page, order_by=order_by, reverse=reverse, subtasks=subtasks, space_ids=space_ids, project_ids=project_ids, list_ids=list_ids, statuses=statuses, include_closed=include_closed, assignees=assignees, tags=tags, due_date_gt=due_date_gt, due_date_lt=due_date_lt, date_created_gt=date_created_gt, date_created_lt=date_created_lt, date_updated_gt=date_updated_gt, date_updated_lt=date_updated_lt, date_done_gt=date_done_gt, date_done_lt=date_done_lt, parent=parent, include_markdown_description=include_markdown_description, custom_items=custom_items, custom_fields=custom_fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_tasks_by_team: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/team/{team_Id}/task", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/team/{team_Id}/task"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_tasks_by_team")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_tasks_by_team", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_tasks_by_team",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tasks
@mcp.tool()
async def merge_tasks(
    task_id: str = Field(..., description="The unique ID of the target task that all source tasks will be merged into. Must be a valid internal task ID; Custom Task IDs are not supported."),
    source_task_ids: list[str] = Field(..., description="An array of IDs representing the source tasks to merge into the target task. Order is not significant; all listed tasks will be merged. Custom Task IDs are not supported."),
) -> dict[str, Any]:
    """Merges one or more source tasks into a specified target task, consolidating their content and history. Source tasks are provided in the request body, and Custom Task IDs are not supported."""

    # Construct request model with validation
    try:
        _request = _models.MergeTasksRequest(
            path=_models.MergeTasksRequestPath(task_id=task_id),
            body=_models.MergeTasksRequestBody(source_task_ids=source_task_ids)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for merge_tasks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/task/{task_id}/merge", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/task/{task_id}/merge"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("merge_tasks")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("merge_tasks", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="merge_tasks",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tasks
@mcp.tool()
async def get_task_time_in_status(
    task_id: str = Field(..., description="The unique identifier of the task for which to retrieve time-in-status data."),
    content_type: Literal["application/json"] = Field(..., alias="Content-Type", description="The media type of the request payload, used to indicate the format of the request body sent to the API."),
    custom_task_ids: bool | None = Field(None, description="Set to true to reference the task by its custom task ID instead of the default ClickUp task ID."),
    team_id: float | None = Field(None, description="The Workspace ID (team_id) required when using custom task IDs. Must be provided alongside custom_task_ids=true."),
) -> dict[str, Any]:
    """Retrieves how long a task has spent in each status, providing a breakdown of time per status stage. Requires the Total Time in Status ClickApp to be enabled by a Workspace owner or admin."""

    # Construct request model with validation
    try:
        _request = _models.GetTaskSTimeinStatusRequest(
            path=_models.GetTaskSTimeinStatusRequestPath(task_id=task_id),
            query=_models.GetTaskSTimeinStatusRequestQuery(custom_task_ids=custom_task_ids, team_id=team_id),
            header=_models.GetTaskSTimeinStatusRequestHeader(content_type=content_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_task_time_in_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/task/{task_id}/time_in_status", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/task/{task_id}/time_in_status"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_task_time_in_status")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_task_time_in_status", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_task_time_in_status",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tasks
@mcp.tool()
async def get_bulk_tasks_time_in_status(
    task_ids: str = Field(..., description="One or more task IDs to query; include this parameter once per task ID, with a maximum of 100 task IDs per request."),
    content_type: Literal["application/json"] = Field(..., alias="Content-Type", description="The media type of the request payload sent to the API."),
    custom_task_ids: bool | None = Field(None, description="Set to true if referencing tasks by their custom task IDs instead of default system IDs."),
    team_id: float | None = Field(None, description="The Workspace ID required when custom_task_ids is set to true; must be provided alongside that parameter."),
) -> dict[str, Any]:
    """Retrieves how long two or more tasks have spent in each status. Requires the Total Time in Status ClickApp to be enabled by a Workspace owner or admin."""

    # Construct request model with validation
    try:
        _request = _models.GetBulkTasksTimeinStatusRequest(
            query=_models.GetBulkTasksTimeinStatusRequestQuery(task_ids=task_ids, custom_task_ids=custom_task_ids, team_id=team_id),
            header=_models.GetBulkTasksTimeinStatusRequestHeader(content_type=content_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_bulk_tasks_time_in_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v2/task/bulk_time_in_status/task_ids"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_bulk_tasks_time_in_status")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_bulk_tasks_time_in_status", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_bulk_tasks_time_in_status",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Templates
@mcp.tool()
async def list_task_templates(
    team_id: float = Field(..., description="The unique identifier of the Workspace whose task templates you want to retrieve."),
    page: int = Field(..., description="The zero-based page number for paginating through task template results, where 0 returns the first page."),
    content_type: Literal["application/json"] = Field(..., alias="Content-Type", description="The media type format for the request body, which must be set to indicate JSON content."),
) -> dict[str, Any]:
    """Retrieves a paginated list of task templates available in the specified Workspace, which can be used to standardize task creation across teams."""

    # Construct request model with validation
    try:
        _request = _models.GetTaskTemplatesRequest(
            path=_models.GetTaskTemplatesRequestPath(team_id=team_id),
            query=_models.GetTaskTemplatesRequestQuery(page=page),
            header=_models.GetTaskTemplatesRequestHeader(content_type=content_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_task_templates: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/team/{team_id}/taskTemplate", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/team/{team_id}/taskTemplate"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_task_templates")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_task_templates", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_task_templates",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Templates
@mcp.tool()
async def list_templates(
    team_id: float = Field(..., description="The unique identifier of the Workspace whose List templates you want to retrieve."),
    page: int = Field(..., description="Zero-indexed page number for paginating through template results; start at 0 for the first page."),
    content_type: Literal["application/json"] = Field(..., alias="Content-Type", description="MIME type for the request body, indicating the format of the data being sent."),
) -> dict[str, Any]:
    """Retrieves all List templates available in a Workspace, returning their IDs and metadata. Use the returned template IDs (prefixed with `t-`) to create Lists from templates in a Folder or Space."""

    # Construct request model with validation
    try:
        _request = _models.GetListTemplatesRequest(
            path=_models.GetListTemplatesRequestPath(team_id=team_id),
            query=_models.GetListTemplatesRequestQuery(page=page),
            header=_models.GetListTemplatesRequestHeader(content_type=content_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_templates: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/team/{team_id}/list_template", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/team/{team_id}/list_template"
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
async def list_folder_templates(
    team_id: float = Field(..., description="The unique identifier of the Workspace whose Folder templates you want to retrieve."),
    page: int = Field(..., description="Zero-indexed page number for paginating through Folder template results; start at 0 for the first page."),
    content_type: Literal["application/json"] = Field(..., alias="Content-Type", description="The media type of the request body sent to the API."),
) -> dict[str, Any]:
    """Retrieves all Folder templates available in a Workspace, including their template IDs. Use the returned template IDs (prefixed with `t-`) with the Create Folder From Template endpoint to instantiate new Folders."""

    # Construct request model with validation
    try:
        _request = _models.GetFolderTemplatesRequest(
            path=_models.GetFolderTemplatesRequestPath(team_id=team_id),
            query=_models.GetFolderTemplatesRequestQuery(page=page),
            header=_models.GetFolderTemplatesRequestHeader(content_type=content_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_folder_templates: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/team/{team_id}/folder_template", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/team/{team_id}/folder_template"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_folder_templates")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_folder_templates", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_folder_templates",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tasks
@mcp.tool()
async def create_task_from_template(
    list_id: float = Field(..., description="The unique numeric identifier of the list where the new task will be created."),
    template_id: str = Field(..., description="The unique string identifier of the task template to use when creating the task."),
    name: str = Field(..., description="The display name to assign to the newly created task."),
) -> dict[str, Any]:
    """Create a new task in a specified list using a pre-defined task template from your workspace. Publicly shared templates must be added to your workspace library before they can be used via the API."""

    # Construct request model with validation
    try:
        _request = _models.CreateTaskFromTemplateRequest(
            path=_models.CreateTaskFromTemplateRequestPath(list_id=list_id, template_id=template_id),
            body=_models.CreateTaskFromTemplateRequestBody(name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_task_from_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/list/{list_id}/taskTemplate/{template_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/list/{list_id}/taskTemplate/{template_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_task_from_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_task_from_template", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_task_from_template",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Lists
@mcp.tool()
async def create_list_from_template_in_folder(
    folder_id: str = Field(..., description="The ID of the Folder in which the new List will be created."),
    template_id: str = Field(..., description="The ID of the List template to apply. Template IDs include a 't-' prefix. Retrieve available template IDs using the Get List Templates endpoint."),
    name: str = Field(..., description="The display name to assign to the newly created List."),
    return_immediately: bool | None = Field(None, description="When true (default), the new List's ID is returned immediately before all nested template objects are fully created. When false, the request waits until the List and all sub-objects are fully applied before responding."),
    content: str | None = Field(None, description="Optional description or body text for the new List."),
    time_estimate: float | None = Field(None, description="Whether to import time estimate values (hours, minutes, and seconds) from the template's tasks."),
    automation: bool | None = Field(None, description="Whether to import automation rules defined in the template."),
    include_views: bool | None = Field(None, description="Whether to import view configurations (e.g., Board, Calendar) from the template."),
    old_due_date: bool | None = Field(None, description="Whether to import the original due dates from the template's tasks."),
    old_start_date: bool | None = Field(None, description="Whether to import the original start dates from the template's tasks."),
    old_followers: bool | None = Field(None, description="Whether to import the watcher (follower) assignments from the template's tasks."),
    comment_attachments: bool | None = Field(None, description="Whether to import file attachments that are embedded in task comments from the template."),
    recur_settings: bool | None = Field(None, description="Whether to import recurring task settings from the template's tasks."),
    old_tags: bool | None = Field(None, description="Whether to import tags from the template's tasks."),
    old_statuses: bool | None = Field(None, description="Whether to import the status configuration (status columns/workflow) from the template."),
    subtasks: bool | None = Field(None, description="Whether to import subtasks from the template's tasks."),
    custom_type: bool | None = Field(None, description="Whether to import custom task type definitions from the template's tasks."),
    old_assignees: bool | None = Field(None, description="Whether to import assignee assignments from the template's tasks."),
    attachments: bool | None = Field(None, description="Whether to import file attachments from the template's tasks."),
    comment: bool | None = Field(None, description="Whether to import comments from the template's tasks."),
    old_status: bool | None = Field(None, description="Whether to import the current status values set on the template's tasks."),
    external_dependencies: bool | None = Field(None, description="Whether to import external dependency links from the template's tasks."),
    internal_dependencies: bool | None = Field(None, description="Whether to import internal dependency links between tasks from the template."),
    priority: bool | None = Field(None, description="Whether to import priority levels from the template's tasks."),
    custom_fields: bool | None = Field(None, description="Whether to import Custom Field definitions and values from the template's tasks."),
    old_checklists: bool | None = Field(None, description="Whether to import checklist items from the template's tasks."),
    relationships: bool | None = Field(None, description="Whether to import task relationship links (e.g., blocked by, related to) from the template."),
    old_subtask_assignees: bool | None = Field(None, description="Whether to import assignees on subtasks from the template's tasks."),
    start_date: str | None = Field(None, description="The project start date used as the anchor when remapping task dates from the template. Must be an ISO 8601 date-time string."),
    due_date: str | None = Field(None, description="The project due date used as the anchor when remapping task dates from the template. Must be an ISO 8601 date-time string."),
    remap_start_date: bool | None = Field(None, description="Whether to remap task start dates relative to the new project start date provided in 'start_date'."),
    skip_weekends: bool | None = Field(None, description="Whether to skip weekend days (Saturday and Sunday) when calculating remapped task dates."),
    archived: Literal[1, 2] | None = Field(None, description="Controls inclusion of archived tasks from the template: 1 includes archived tasks, 2 excludes them. Omit to use the default behavior."),
) -> dict[str, Any]:
    """Create a new List inside a specified Folder using an existing List template, optionally controlling which task properties (assignees, due dates, custom fields, etc.) are imported from the template. By default the request returns immediately with the future List ID, though the List and its nested objects may still be generating in the background."""

    # Construct request model with validation
    try:
        _request = _models.CreateFolderListFromTemplateRequest(
            path=_models.CreateFolderListFromTemplateRequestPath(folder_id=folder_id, template_id=template_id),
            body=_models.CreateFolderListFromTemplateRequestBody(name=name,
                options=_models.CreateFolderListFromTemplateRequestBodyOptions(return_immediately=return_immediately, content=content, time_estimate=time_estimate, automation=automation, include_views=include_views, old_due_date=old_due_date, old_start_date=old_start_date, old_followers=old_followers, comment_attachments=comment_attachments, recur_settings=recur_settings, old_tags=old_tags, old_statuses=old_statuses, subtasks=subtasks, custom_type=custom_type, old_assignees=old_assignees, attachments=attachments, comment=comment, old_status=old_status, external_dependencies=external_dependencies, internal_dependencies=internal_dependencies, priority=priority, custom_fields=custom_fields, old_checklists=old_checklists, relationships=relationships, old_subtask_assignees=old_subtask_assignees, start_date=start_date, due_date=due_date, remap_start_date=remap_start_date, skip_weekends=skip_weekends, archived=archived) if any(v is not None for v in [return_immediately, content, time_estimate, automation, include_views, old_due_date, old_start_date, old_followers, comment_attachments, recur_settings, old_tags, old_statuses, subtasks, custom_type, old_assignees, attachments, comment, old_status, external_dependencies, internal_dependencies, priority, custom_fields, old_checklists, relationships, old_subtask_assignees, start_date, due_date, remap_start_date, skip_weekends, archived]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_list_from_template_in_folder: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/folder/{folder_id}/list_template/{template_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/folder/{folder_id}/list_template/{template_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_list_from_template_in_folder")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_list_from_template_in_folder", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_list_from_template_in_folder",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Lists
@mcp.tool()
async def create_list_from_template(
    space_id: str = Field(..., description="The unique identifier of the Space where the new List will be created."),
    template_id: str = Field(..., description="The unique identifier of the List template to apply, always prefixed with `t-`. Retrieve available template IDs using the Get List Templates endpoint."),
    name: str = Field(..., description="The display name to assign to the newly created List."),
    return_immediately: bool | None = Field(None, description="When true, returns the new object ID immediately after access checks without waiting for all nested assets to finish being created. When false, the request waits until the List and all its contents are fully created before responding."),
    content: str | None = Field(None, description="Optional description or body text for the new List."),
    time_estimate: float | None = Field(None, description="Whether to import time estimate values (hours, minutes, and seconds) from the template's tasks."),
    automation: bool | None = Field(None, description="Whether to import automation rules defined in the template."),
    include_views: bool | None = Field(None, description="Whether to import views configured in the template."),
    old_due_date: bool | None = Field(None, description="Whether to import due dates from the template's tasks."),
    old_start_date: bool | None = Field(None, description="Whether to import start dates from the template's tasks."),
    old_followers: bool | None = Field(None, description="Whether to import watchers (followers) from the template's tasks."),
    comment_attachments: bool | None = Field(None, description="Whether to import comment attachments from the template's tasks."),
    recur_settings: bool | None = Field(None, description="Whether to import recurring task settings from the template's tasks."),
    old_tags: bool | None = Field(None, description="Whether to import tags from the template's tasks."),
    old_statuses: bool | None = Field(None, description="Whether to import status configuration settings from the template's tasks."),
    subtasks: bool | None = Field(None, description="Whether to import subtasks from the template's tasks."),
    custom_type: bool | None = Field(None, description="Whether to import custom task type definitions from the template's tasks."),
    old_assignees: bool | None = Field(None, description="Whether to import assignees from the template's tasks."),
    attachments: bool | None = Field(None, description="Whether to import file attachments from the template's tasks."),
    comment: bool | None = Field(None, description="Whether to import comments from the template's tasks."),
    old_status: bool | None = Field(None, description="Whether to import the current status values of the template's tasks."),
    external_dependencies: bool | None = Field(None, description="Whether to import external task dependencies from the template's tasks."),
    internal_dependencies: bool | None = Field(None, description="Whether to import internal task dependencies from the template's tasks."),
    priority: bool | None = Field(None, description="Whether to import priority settings from the template's tasks."),
    custom_fields: bool | None = Field(None, description="Whether to import Custom Field definitions and values from the template's tasks."),
    old_checklists: bool | None = Field(None, description="Whether to import checklists from the template's tasks."),
    relationships: bool | None = Field(None, description="Whether to import task relationship links from the template's tasks."),
    old_subtask_assignees: bool | None = Field(None, description="Whether to import assignees on subtasks from the template's tasks."),
    start_date: str | None = Field(None, description="The project start date used as the anchor point when remapping task dates, provided in ISO 8601 date-time format."),
    due_date: str | None = Field(None, description="The project due date used as the anchor point when remapping task dates, provided in ISO 8601 date-time format."),
    remap_start_date: bool | None = Field(None, description="Whether to remap task start dates relative to the new project start date."),
    skip_weekends: bool | None = Field(None, description="Whether to skip weekend days when calculating remapped task dates."),
    archived: Literal[1, 2] | None = Field(None, description="Controls inclusion of archived tasks: use 1 to include archived tasks, 2 to include only archived tasks, or omit for no archived tasks."),
) -> dict[str, Any]:
    """Create a new List within a Space using an existing List template, importing selected task properties such as assignees, due dates, custom fields, and more. Supports both synchronous and asynchronous creation via the `return_immediately` parameter."""

    # Construct request model with validation
    try:
        _request = _models.CreateSpaceListFromTemplateRequest(
            path=_models.CreateSpaceListFromTemplateRequestPath(space_id=space_id, template_id=template_id),
            body=_models.CreateSpaceListFromTemplateRequestBody(name=name,
                options=_models.CreateSpaceListFromTemplateRequestBodyOptions(return_immediately=return_immediately, content=content, time_estimate=time_estimate, automation=automation, include_views=include_views, old_due_date=old_due_date, old_start_date=old_start_date, old_followers=old_followers, comment_attachments=comment_attachments, recur_settings=recur_settings, old_tags=old_tags, old_statuses=old_statuses, subtasks=subtasks, custom_type=custom_type, old_assignees=old_assignees, attachments=attachments, comment=comment, old_status=old_status, external_dependencies=external_dependencies, internal_dependencies=internal_dependencies, priority=priority, custom_fields=custom_fields, old_checklists=old_checklists, relationships=relationships, old_subtask_assignees=old_subtask_assignees, start_date=start_date, due_date=due_date, remap_start_date=remap_start_date, skip_weekends=skip_weekends, archived=archived) if any(v is not None for v in [return_immediately, content, time_estimate, automation, include_views, old_due_date, old_start_date, old_followers, comment_attachments, recur_settings, old_tags, old_statuses, subtasks, custom_type, old_assignees, attachments, comment, old_status, external_dependencies, internal_dependencies, priority, custom_fields, old_checklists, relationships, old_subtask_assignees, start_date, due_date, remap_start_date, skip_weekends, archived]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_list_from_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/space/{space_id}/list_template/{template_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/space/{space_id}/list_template/{template_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_list_from_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_list_from_template", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_list_from_template",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Workspaces
@mcp.tool()
async def get_workspace_seats(team_id: str = Field(..., description="The unique identifier of the Workspace whose seat information you want to retrieve.")) -> dict[str, Any]:
    """Retrieves seat usage information for a Workspace, including the number of used, total, and available seats for both members and guests."""

    # Construct request model with validation
    try:
        _request = _models.GetWorkspaceseatsRequest(
            path=_models.GetWorkspaceseatsRequestPath(team_id=team_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_workspace_seats: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/team/{team_id}/seats", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/team/{team_id}/seats"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_workspace_seats")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_workspace_seats", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_workspace_seats",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Workspaces
@mcp.tool()
async def get_workspace_plan(team_id: str = Field(..., description="The unique identifier of the Workspace whose plan information you want to retrieve.")) -> dict[str, Any]:
    """Retrieves the current subscription plan details for the specified Workspace, including plan tier and associated features."""

    # Construct request model with validation
    try:
        _request = _models.GetWorkspaceplanRequest(
            path=_models.GetWorkspaceplanRequestPath(team_id=team_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_workspace_plan: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/team/{team_id}/plan", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/team/{team_id}/plan"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_workspace_plan")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_workspace_plan", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_workspace_plan",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: User Groups
@mcp.tool()
async def create_user_group(
    team_id: float = Field(..., description="The unique identifier of the Workspace (referred to as team_id in the API) where the User Group will be created."),
    name: str = Field(..., description="The display name for the new User Group, used to identify it within the Workspace."),
    members: list[int] = Field(..., description="A list of user objects to include as members of the new User Group; order is not significant and each item should represent a user to be added."),
    handle: str | None = Field(None, description="An optional short identifier or alias for the User Group, typically used as a reference handle within the Workspace."),
) -> dict[str, Any]:
    """Creates a User Group within a Workspace to organize and manage users collectively. Note that adding a guest with view-only permissions automatically converts them to a paid guest, which may incur prorated charges if additional seats are needed."""

    # Construct request model with validation
    try:
        _request = _models.CreateUserGroupRequest(
            path=_models.CreateUserGroupRequestPath(team_id=team_id),
            body=_models.CreateUserGroupRequestBody(name=name, handle=handle, members=members)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_user_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/team/{team_id}/group", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/team/{team_id}/group"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_user_group")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_user_group", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_user_group",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Task Types
@mcp.tool()
async def list_custom_task_types(team_id: float = Field(..., description="The unique identifier of the Workspace whose custom task types you want to retrieve.")) -> dict[str, Any]:
    """Retrieves all custom task types defined in a Workspace, allowing you to see available task type options for organizing and categorizing work."""

    # Construct request model with validation
    try:
        _request = _models.GetCustomItemsRequest(
            path=_models.GetCustomItemsRequestPath(team_id=team_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_custom_task_types: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/team/{team_id}/custom_item", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/team/{team_id}/custom_item"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_custom_task_types")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_custom_task_types", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_custom_task_types",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: User Groups
@mcp.tool()
async def update_user_group(
    group_id: str = Field(..., description="The unique identifier of the User Group to update."),
    add: list[int] = Field(..., description="List of user IDs to add to the User Group. Each item should be a valid user ID string."),
    rem: list[int] = Field(..., description="List of user IDs to remove from the User Group. Each item should be a valid user ID string."),
    name: str | None = Field(None, description="The new display name for the User Group."),
    handle: str | None = Field(None, description="The new handle (short identifier or alias) for the User Group."),
) -> dict[str, Any]:
    """Updates a User Group's name, handle, or membership within a Workspace. Note that adding a guest with view-only permissions automatically converts them to a paid guest, which may incur prorated billing charges."""

    # Construct request model with validation
    try:
        _request = _models.UpdateTeamRequest(
            path=_models.UpdateTeamRequestPath(group_id=group_id),
            body=_models.UpdateTeamRequestBody(name=name, handle=handle,
                members=_models.UpdateTeamRequestBodyMembers(add=add, rem=rem))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_user_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/group/{group_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/group/{group_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_user_group")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_user_group", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_user_group",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: User Groups
@mcp.tool()
async def delete_user_group(group_id: str = Field(..., description="The unique identifier of the user group to delete from the Workspace.")) -> dict[str, Any]:
    """Permanently removes a user group from the Workspace. Note that in the API, 'group_id' refers to a user group, while 'team_id' refers to the Workspace."""

    # Construct request model with validation
    try:
        _request = _models.DeleteTeamRequest(
            path=_models.DeleteTeamRequestPath(group_id=group_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_user_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/group/{group_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/group/{group_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_user_group")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_user_group", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_user_group",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: User Groups
@mcp.tool()
async def list_user_groups(
    team_id: float = Field(..., description="The unique ID of the Workspace whose User Groups you want to retrieve."),
    group_ids: list[str] | None = Field(None, description="An optional list of User Group IDs to filter results to specific groups; omit to return all User Groups in the Workspace. Each item should be a valid User Group ID string. Order is not significant."),
) -> dict[str, Any]:
    """Retrieves User Groups within a specified Workspace, optionally filtered to one or more specific groups. Note: in the API, 'team_id' refers to the Workspace ID and 'group_id' refers to a User Group ID."""

    # Construct request model with validation
    try:
        _request = _models.GetTeams1Request(
            query=_models.GetTeams1RequestQuery(team_id=team_id, group_ids=group_ids)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_user_groups: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v2/group"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_user_groups")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_user_groups", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_user_groups",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Time Tracking (Legacy)
@mcp.tool()
async def get_task_tracked_time(
    task_id: str = Field(..., description="The unique identifier of the task whose tracked time entries you want to retrieve."),
    content_type: Literal["application/json"] = Field(..., alias="Content-Type", description="The media type of the request payload, indicating the format of the data being sent."),
    custom_task_ids: bool | None = Field(None, description="Set to true if referencing the task by its custom task ID instead of the default ClickUp task ID."),
    team_id: float | None = Field(None, description="The Workspace ID required when using custom task IDs; must be provided alongside custom_task_ids=true."),
) -> dict[str, Any]:
    """Retrieves all tracked time entries associated with a specific task. Note: This is a legacy endpoint; the Time Tracking API is recommended for managing time entries."""

    # Construct request model with validation
    try:
        _request = _models.GettrackedtimeRequest(
            path=_models.GettrackedtimeRequestPath(task_id=task_id),
            query=_models.GettrackedtimeRequestQuery(custom_task_ids=custom_task_ids, team_id=team_id),
            header=_models.GettrackedtimeRequestHeader(content_type=content_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_task_tracked_time: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/task/{task_id}/time", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/task/{task_id}/time"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_task_tracked_time")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_task_tracked_time", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_task_tracked_time",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Time Tracking (Legacy)
@mcp.tool()
async def track_task_time(
    task_id: str = Field(..., description="The unique identifier of the task to log time against."),
    start: int = Field(..., description="The start time of the tracked time entry as a Unix timestamp in milliseconds."),
    end: int = Field(..., description="The end time of the tracked time entry as a Unix timestamp in milliseconds. Must be greater than the start value."),
    time_: int = Field(..., alias="time", description="The total duration of the time entry in milliseconds."),
    custom_task_ids: bool | None = Field(None, description="Set to true if referencing the task by its custom task ID rather than the default system-generated ID."),
    team_id: float | None = Field(None, description="The Workspace ID required when using custom task IDs. Must be provided alongside custom_task_ids=true."),
) -> dict[str, Any]:
    """Records a time entry against a specific task using the legacy time tracking endpoint. For new integrations, the dedicated Time Tracking API endpoints are recommended instead."""

    # Construct request model with validation
    try:
        _request = _models.TracktimeRequest(
            path=_models.TracktimeRequestPath(task_id=task_id),
            query=_models.TracktimeRequestQuery(custom_task_ids=custom_task_ids, team_id=team_id),
            body=_models.TracktimeRequestBody(start=start, end=end, time_=time_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for track_task_time: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/task/{task_id}/time", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/task/{task_id}/time"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("track_task_time")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("track_task_time", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="track_task_time",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Time Tracking (Legacy)
@mcp.tool()
async def update_time_entry_legacy(
    task_id: str = Field(..., description="The unique identifier of the task containing the time interval to update."),
    interval_id: str = Field(..., description="The unique identifier of the specific time interval to edit."),
    start: int = Field(..., description="The start time of the tracked interval as a Unix timestamp in milliseconds."),
    end: int = Field(..., description="The end time of the tracked interval as a Unix timestamp in milliseconds. Must be greater than the start value."),
    time_: int = Field(..., alias="time", description="The total duration of the tracked time interval in milliseconds."),
    custom_task_ids: bool | None = Field(None, description="Set to true to reference the task by its custom task ID instead of its default system ID."),
    team_id: float | None = Field(None, description="The Workspace ID required when using custom task IDs. Must be provided alongside custom_task_ids=true."),
) -> dict[str, Any]:
    """Updates an existing tracked time interval on a task by modifying its start time, end time, or duration. Note: This is a legacy endpoint; the Time Tracking API is recommended for managing time entries."""

    # Construct request model with validation
    try:
        _request = _models.EdittimetrackedRequest(
            path=_models.EdittimetrackedRequestPath(task_id=task_id, interval_id=interval_id),
            query=_models.EdittimetrackedRequestQuery(custom_task_ids=custom_task_ids, team_id=team_id),
            body=_models.EdittimetrackedRequestBody(start=start, end=end, time_=time_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_time_entry_legacy: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/task/{task_id}/time/{interval_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/task/{task_id}/time/{interval_id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_time_entry_legacy")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_time_entry_legacy", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_time_entry_legacy",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Time Tracking (Legacy)
@mcp.tool()
async def delete_tracked_time_interval(
    task_id: str = Field(..., description="The unique identifier of the task from which the tracked time interval will be deleted."),
    interval_id: str = Field(..., description="The unique identifier of the tracked time interval to delete."),
    content_type: Literal["application/json"] = Field(..., alias="Content-Type", description="The MIME type of the request body, indicating the format of the data being sent."),
    custom_task_ids: bool | None = Field(None, description="Set to true to reference the task by its custom task ID instead of the default ClickUp task ID."),
    team_id: float | None = Field(None, description="The Workspace ID required when referencing a task by its custom task ID; must be provided alongside custom_task_ids=true."),
) -> dict[str, Any]:
    """Deletes a specific tracked time interval from a task using its interval ID. Note: This is a legacy endpoint; the Time Tracking API is recommended for managing time entries."""

    # Construct request model with validation
    try:
        _request = _models.DeletetimetrackedRequest(
            path=_models.DeletetimetrackedRequestPath(task_id=task_id, interval_id=interval_id),
            query=_models.DeletetimetrackedRequestQuery(custom_task_ids=custom_task_ids, team_id=team_id),
            header=_models.DeletetimetrackedRequestHeader(content_type=content_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_tracked_time_interval: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/task/{task_id}/time/{interval_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/task/{task_id}/time/{interval_id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_tracked_time_interval")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_tracked_time_interval", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_tracked_time_interval",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Time Tracking
@mcp.tool()
async def list_time_entries(
    team_id: float = Field(..., alias="team_Id", description="The unique identifier of the workspace from which to retrieve time entries."),
    content_type: Literal["application/json"] = Field(..., alias="Content-Type", description="The media type of the request payload, which must be set to indicate JSON content."),
    start_date: float | None = Field(None, description="The beginning of the date range filter expressed as a Unix timestamp in milliseconds. Defaults to 30 days before the current time if omitted."),
    end_date: float | None = Field(None, description="The end of the date range filter expressed as a Unix timestamp in milliseconds. Defaults to the current time if omitted."),
    assignee: float | None = Field(None, description="Filter results to one or more specific users by their user IDs, supplied as a comma-separated list. Only Workspace Owners and Admins may retrieve entries for users other than themselves."),
    include_task_tags: bool | None = Field(None, description="When set to true, includes any tags associated with the task linked to each time entry in the response."),
    include_location_names: bool | None = Field(None, description="When set to true, enriches each time entry with the human-readable names of its associated List, Folder, and Space alongside their respective IDs."),
    include_approval_history: bool | None = Field(None, description="When set to true, includes the full approval history for each time entry, including status changes, reviewer notes, and approver details."),
    include_approval_details: bool | None = Field(None, description="When set to true, includes current approval details for each time entry such as the approver ID, approval timestamp, list of approvers, and current approval status."),
    space_id: float | None = Field(None, description="Restricts results to time entries linked to tasks within the specified Space. Cannot be combined with folder_id, list_id, or task_id."),
    folder_id: float | None = Field(None, description="Restricts results to time entries linked to tasks within the specified Folder. Cannot be combined with space_id, list_id, or task_id."),
    list_id: float | None = Field(None, description="Restricts results to time entries linked to tasks within the specified List. Cannot be combined with space_id, folder_id, or task_id."),
    task_id: str | None = Field(None, description="Restricts results to time entries linked to a single specific task. Cannot be combined with space_id, folder_id, or list_id."),
    custom_task_ids: bool | None = Field(None, description="Set to true to reference the target task using its custom task ID instead of its standard ClickUp task ID. Must be used together with the team_id parameter."),
    team_id2: float | None = Field(None, alias="team_id", description="The workspace ID required when custom_task_ids is set to true, used to resolve the custom task ID to the correct task within the workspace."),
    is_billable: bool | None = Field(None, description="Filters results by billing status: set to true to return only billable time entries, or false to return only non-billable time entries. Omit to return all entries regardless of billing status."),
) -> dict[str, Any]:
    """Retrieve time entries for a workspace filtered by a date range, location, assignee, and billing status. Defaults to the last 30 days for the authenticated user; only one location filter (space, folder, list, or task) may be applied at a time."""

    # Construct request model with validation
    try:
        _request = _models.GettimeentrieswithinadaterangeRequest(
            path=_models.GettimeentrieswithinadaterangeRequestPath(team_id=team_id),
            query=_models.GettimeentrieswithinadaterangeRequestQuery(start_date=start_date, end_date=end_date, assignee=assignee, include_task_tags=include_task_tags, include_location_names=include_location_names, include_approval_history=include_approval_history, include_approval_details=include_approval_details, space_id=space_id, folder_id=folder_id, list_id=list_id, task_id=task_id, custom_task_ids=custom_task_ids, team_id2=team_id2, is_billable=is_billable),
            header=_models.GettimeentrieswithinadaterangeRequestHeader(content_type=content_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_time_entries: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/team/{team_Id}/time_entries", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/team/{team_Id}/time_entries"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_time_entries")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_time_entries", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_time_entries",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Time Tracking
@mcp.tool()
async def create_time_entry(
    team_id: float = Field(..., alias="team_Id", description="The unique identifier of the workspace where the time entry will be created."),
    start: int = Field(..., description="The start time of the time entry as a Unix timestamp in milliseconds."),
    duration: int = Field(..., description="The duration of the time entry in milliseconds. Used as an alternative to the stop parameter; ignored when both start and stop values are present. A negative value indicates a currently running timer."),
    custom_task_ids: bool | None = Field(None, description="Set to true to reference the associated task by its custom task ID instead of its standard ClickUp task ID."),
    team_id2: float | None = Field(None, alias="team_id", description="The workspace ID required when using custom task IDs. Must be provided alongside custom_task_ids=true to correctly resolve the custom task reference."),
    description: str | None = Field(None, description="An optional text description or note to associate with the time entry."),
    tags: list[_models.CreateatimeentryBodyTagsItem] | None = Field(None, description="A list of time tracking label objects to attach to the entry. Available to users on the Business Plan and above; each item should represent a valid time tracking tag."),
    stop: int | None = Field(None, description="The end time of the time entry as a Unix timestamp in milliseconds. Can be used instead of the duration parameter; if both stop and start are provided, duration is ignored."),
    billable: bool | None = Field(None, description="Marks the time entry as billable when set to true."),
    assignee: int | None = Field(None, description="The user ID to assign the time entry to. Workspace owners and admins may specify any user ID; members may only specify their own user ID."),
    tid: str | None = Field(None, description="The ID of the task to associate with this time entry."),
) -> dict[str, Any]:
    """Creates a time entry for a user in the specified workspace, supporting both completed entries (with start and stop/duration) and actively running timers. A negative duration indicates a timer is currently running for that user."""

    # Construct request model with validation
    try:
        _request = _models.CreateatimeentryRequest(
            path=_models.CreateatimeentryRequestPath(team_id=team_id),
            query=_models.CreateatimeentryRequestQuery(custom_task_ids=custom_task_ids, team_id2=team_id2),
            body=_models.CreateatimeentryRequestBody(description=description, tags=tags, start=start, stop=stop, billable=billable, duration=duration, assignee=assignee, tid=tid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_time_entry: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/team/{team_Id}/time_entries", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/team/{team_Id}/time_entries"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_time_entry")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_time_entry", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_time_entry",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Time Tracking
@mcp.tool()
async def get_time_entry(
    team_id: float = Field(..., description="The unique numeric ID of the workspace containing the time entry."),
    timer_id: str = Field(..., description="The unique ID of the time entry to retrieve. Time entry IDs can be obtained from the Get Time Entries Within a Date Range endpoint."),
    content_type: Literal["application/json"] = Field(..., alias="Content-Type", description="The media type of the request body, indicating the format of the payload being sent."),
    include_task_tags: bool | None = Field(None, description="When true, includes any task tags associated with the time entry in the response."),
    include_location_names: bool | None = Field(None, description="When true, includes the human-readable names of the List, Folder, and Space alongside their respective IDs in the response."),
    include_approval_history: bool | None = Field(None, description="When true, includes the full approval history for the time entry, showing past approval state changes."),
    include_approval_details: bool | None = Field(None, description="When true, includes detailed information about the current approval state and approver for the time entry."),
) -> dict[str, Any]:
    """Retrieves a single time entry by its ID within a workspace. Note that a time entry with a negative duration indicates the timer is currently running for that user."""

    # Construct request model with validation
    try:
        _request = _models.GetsingulartimeentryRequest(
            path=_models.GetsingulartimeentryRequestPath(team_id=team_id, timer_id=timer_id),
            query=_models.GetsingulartimeentryRequestQuery(include_task_tags=include_task_tags, include_location_names=include_location_names, include_approval_history=include_approval_history, include_approval_details=include_approval_details),
            header=_models.GetsingulartimeentryRequestHeader(content_type=content_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_time_entry: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/team/{team_id}/time_entries/{timer_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/team/{team_id}/time_entries/{timer_id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_time_entry")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_time_entry", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_time_entry",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Time Tracking
@mcp.tool()
async def update_time_entry(
    team_id: float = Field(..., description="The unique identifier of the workspace containing the time entry."),
    timer_id: float = Field(..., description="The unique identifier of the time entry to update."),
    tags: list[_models.UpdateatimeEntryBodyTagsItem] = Field(..., description="A list of time tracking label objects to apply to the time entry. Available on Business Plan and above. Order is not significant; each item should be a valid tag object."),
    tid: str = Field(..., description="The unique identifier of the task to associate with this time entry."),
    custom_task_ids: bool | None = Field(None, description="Set to true to reference the associated task by its custom task ID instead of its default ClickUp task ID."),
    description: str | None = Field(None, description="A text description or note to associate with the time entry."),
    tag_action: str | None = Field(None, description="Specifies how the provided tags should be applied — for example, whether to replace existing tags or add to them."),
    start: int | None = Field(None, description="The start time of the time entry as a Unix timestamp in milliseconds. Must be provided together with the end parameter."),
    end: int | None = Field(None, description="The end time of the time entry as a Unix timestamp in milliseconds. Must be provided together with the start parameter."),
    billable: bool | None = Field(None, description="Indicates whether the time entry should be marked as billable."),
    duration: int | None = Field(None, description="The duration of the time entry in milliseconds. Use this to set a fixed duration rather than deriving it from start and end times."),
) -> dict[str, Any]:
    """Update the details of an existing time entry in a workspace, including its description, tags, start/end times, duration, and billable status."""

    # Construct request model with validation
    try:
        _request = _models.UpdateatimeEntryRequest(
            path=_models.UpdateatimeEntryRequestPath(team_id=team_id, timer_id=timer_id),
            query=_models.UpdateatimeEntryRequestQuery(custom_task_ids=custom_task_ids),
            body=_models.UpdateatimeEntryRequestBody(description=description, tags=tags, tag_action=tag_action, start=start, end=end, tid=tid, billable=billable, duration=duration)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_time_entry: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/team/{team_id}/time_entries/{timer_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/team/{team_id}/time_entries/{timer_id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_time_entry")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_time_entry", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_time_entry",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Time Tracking
@mcp.tool()
async def delete_time_entry(
    team_id: float = Field(..., description="The unique identifier of the Workspace from which the time entries will be deleted."),
    timer_id: float = Field(..., description="The unique identifier of the time entry to delete. To delete multiple entries at once, provide a comma-separated list of timer IDs."),
    content_type: Literal["application/json"] = Field(..., alias="Content-Type", description="The media type of the request body, indicating the format in which the data is being sent."),
) -> dict[str, Any]:
    """Permanently deletes one or more time entries from a specified Workspace. Multiple time entries can be removed in a single request by providing a comma-separated list of timer IDs."""

    # Construct request model with validation
    try:
        _request = _models.DeleteatimeEntryRequest(
            path=_models.DeleteatimeEntryRequestPath(team_id=team_id, timer_id=timer_id),
            header=_models.DeleteatimeEntryRequestHeader(content_type=content_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_time_entry: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/team/{team_id}/time_entries/{timer_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/team/{team_id}/time_entries/{timer_id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_time_entry")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_time_entry", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_time_entry",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Time Tracking
@mcp.tool()
async def get_time_entry_history(
    team_id: float = Field(..., description="The unique numeric ID of the workspace containing the time entry."),
    timer_id: str = Field(..., description="The unique ID of the time entry whose history you want to retrieve. Can be obtained from the Get Time Entries Within a Date Range endpoint."),
    content_type: Literal["application/json"] = Field(..., alias="Content-Type", description="The media type of the request body, indicating the format of the data being sent."),
) -> dict[str, Any]:
    """Retrieves the change history for a specific time entry, showing a chronological list of modifications made to it."""

    # Construct request model with validation
    try:
        _request = _models.GettimeentryhistoryRequest(
            path=_models.GettimeentryhistoryRequestPath(team_id=team_id, timer_id=timer_id),
            header=_models.GettimeentryhistoryRequestHeader(content_type=content_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_time_entry_history: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/team/{team_id}/time_entries/{timer_id}/history", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/team/{team_id}/time_entries/{timer_id}/history"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_time_entry_history")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_time_entry_history", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_time_entry_history",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Time Tracking
@mcp.tool()
async def get_running_time_entry(
    team_id: float = Field(..., description="The unique identifier of the workspace in which to look up the running time entry."),
    content_type: Literal["application/json"] = Field(..., alias="Content-Type", description="The media type of the request payload, indicating the format in which data is being sent to the API."),
    assignee: float | None = Field(None, description="The user ID of a specific team member whose running time entry should be retrieved; defaults to the authenticated user if omitted."),
) -> dict[str, Any]:
    """Retrieves the currently active (running) time entry for the authenticated user in the specified workspace. A time entry with a negative duration indicates the timer is actively tracking time."""

    # Construct request model with validation
    try:
        _request = _models.GetrunningtimeentryRequest(
            path=_models.GetrunningtimeentryRequestPath(team_id=team_id),
            query=_models.GetrunningtimeentryRequestQuery(assignee=assignee),
            header=_models.GetrunningtimeentryRequestHeader(content_type=content_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_running_time_entry: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/team/{team_id}/time_entries/current", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/team/{team_id}/time_entries/current"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_running_time_entry")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_running_time_entry", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_running_time_entry",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Time Tracking
@mcp.tool()
async def list_time_entry_tags(
    team_id: float = Field(..., description="The unique identifier of the Workspace whose time entry tags you want to retrieve."),
    content_type: Literal["application/json"] = Field(..., alias="Content-Type", description="The media type of the request payload, indicating the format in which data is being sent to the server."),
) -> dict[str, Any]:
    """Retrieves all labels (tags) that have been applied to time entries within a specified Workspace. Useful for auditing or filtering time entry categorization across a team."""

    # Construct request model with validation
    try:
        _request = _models.GetalltagsfromtimeentriesRequest(
            path=_models.GetalltagsfromtimeentriesRequestPath(team_id=team_id),
            header=_models.GetalltagsfromtimeentriesRequestHeader(content_type=content_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_time_entry_tags: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/team/{team_id}/time_entries/tags", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/team/{team_id}/time_entries/tags"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_time_entry_tags")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_time_entry_tags", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_time_entry_tags",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Time Tracking
@mcp.tool()
async def add_tags_to_time_entries(
    team_id: float = Field(..., description="The unique identifier of the workspace containing the time entries."),
    time_entry_ids: list[str] = Field(..., description="List of time entry IDs to which the tags will be applied. Order is not significant; each ID should be a valid time entry identifier within the workspace."),
    tags: list[_models.AddtagsfromtimeentriesBodyTagsItem] = Field(..., description="List of tag names to attach to the specified time entries. Order is not significant; each item should be a tag name string."),
) -> dict[str, Any]:
    """Add one or more tags to a set of time entries in a workspace. Useful for bulk-labeling time entries for categorization or reporting purposes."""

    # Construct request model with validation
    try:
        _request = _models.AddtagsfromtimeentriesRequest(
            path=_models.AddtagsfromtimeentriesRequestPath(team_id=team_id),
            body=_models.AddtagsfromtimeentriesRequestBody(time_entry_ids=time_entry_ids, tags=tags)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_tags_to_time_entries: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/team/{team_id}/time_entries/tags", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/team/{team_id}/time_entries/tags"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_tags_to_time_entries")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_tags_to_time_entries", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_tags_to_time_entries",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Time Tracking
@mcp.tool()
async def rename_time_entry_tag(
    team_id: float = Field(..., description="The unique identifier of the workspace containing the time entry tags to update."),
    name: str = Field(..., description="The current name of the tag to be renamed."),
    new_name: str = Field(..., description="The new name to assign to the tag, replacing the current name across all associated time entries."),
    tag_bg: str = Field(..., description="The background color for the tag, specified as a hex color code."),
    tag_fg: str = Field(..., description="The foreground (text) color for the tag, specified as a hex color code."),
) -> dict[str, Any]:
    """Rename an existing time entry tag within a workspace, updating its display name and color styling. All time entries using the old tag name will reflect the updated tag."""

    # Construct request model with validation
    try:
        _request = _models.ChangetagnamesfromtimeentriesRequest(
            path=_models.ChangetagnamesfromtimeentriesRequestPath(team_id=team_id),
            body=_models.ChangetagnamesfromtimeentriesRequestBody(name=name, new_name=new_name, tag_bg=tag_bg, tag_fg=tag_fg)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for rename_time_entry_tag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/team/{team_id}/time_entries/tags", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/team/{team_id}/time_entries/tags"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("rename_time_entry_tag")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("rename_time_entry_tag", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="rename_time_entry_tag",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Time Tracking
@mcp.tool()
async def remove_tags_from_time_entries(
    team_id: float = Field(..., description="The unique identifier of the workspace containing the time entries."),
    time_entry_ids: list[str] = Field(..., description="List of time entry IDs from which the specified tags will be removed. Order is not significant."),
    tags: list[_models.RemovetagsfromtimeentriesBodyTagsItem] = Field(..., description="List of tag objects to remove from the specified time entries. Order is not significant; each item should represent a valid tag associated with the workspace."),
) -> dict[str, Any]:
    """Remove one or more tags from specified time entries in a workspace. This disassociates the labels from the time entries without deleting the tags from the workspace."""

    # Construct request model with validation
    try:
        _request = _models.RemovetagsfromtimeentriesRequest(
            path=_models.RemovetagsfromtimeentriesRequestPath(team_id=team_id),
            body=_models.RemovetagsfromtimeentriesRequestBody(time_entry_ids=time_entry_ids, tags=tags)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_tags_from_time_entries: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/team/{team_id}/time_entries/tags", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/team/{team_id}/time_entries/tags"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_tags_from_time_entries")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_tags_from_time_entries", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_tags_from_time_entries",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Time Tracking
@mcp.tool()
async def start_time_entry(
    team_id: float = Field(..., alias="team_Id", description="The unique identifier of the workspace in which to start the time entry."),
    custom_task_ids: bool | None = Field(None, description="Set to true if the task is being referenced by its custom task ID rather than its default system-generated ID."),
    description: str | None = Field(None, description="A brief label or note describing what the time entry is tracking."),
    tags: list[_models.StartatimeEntryBodyTagsItem] | None = Field(None, description="A list of time tracking label objects to associate with this entry; available to Business Plan users and above. Order is not significant."),
    tid: str | None = Field(None, description="The ID of the task to associate with this time entry."),
    billable: bool | None = Field(None, description="Indicates whether the time being tracked should be marked as billable."),
) -> dict[str, Any]:
    """Starts a running timer for the authenticated user within the specified workspace. Optionally associates the entry with a task, tags, and billable status."""

    # Construct request model with validation
    try:
        _request = _models.StartatimeEntryRequest(
            path=_models.StartatimeEntryRequestPath(team_id=team_id),
            query=_models.StartatimeEntryRequestQuery(custom_task_ids=custom_task_ids),
            body=_models.StartatimeEntryRequestBody(description=description, tags=tags, tid=tid, billable=billable)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for start_time_entry: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/team/{team_Id}/time_entries/start", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/team/{team_Id}/time_entries/start"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("start_time_entry")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("start_time_entry", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="start_time_entry",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Time Tracking
@mcp.tool()
async def stop_time_entry(
    team_id: float = Field(..., description="The unique identifier of the workspace in which to stop the active time entry."),
    content_type: Literal["application/json"] = Field(..., alias="Content-Type", description="The media type of the request body, which must be set to indicate JSON formatting."),
) -> dict[str, Any]:
    """Stops the currently running timer for the authenticated user in the specified workspace. Only one active timer can be running at a time, and this operation halts it immediately."""

    # Construct request model with validation
    try:
        _request = _models.StopatimeEntryRequest(
            path=_models.StopatimeEntryRequestPath(team_id=team_id),
            header=_models.StopatimeEntryRequestHeader(content_type=content_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for stop_time_entry: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/team/{team_id}/time_entries/stop", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/team/{team_id}/time_entries/stop"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("stop_time_entry")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("stop_time_entry", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="stop_time_entry",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Users
@mcp.tool()
async def invite_workspace_member(
    team_id: float = Field(..., description="The unique identifier of the Workspace to which the user will be invited."),
    email: str = Field(..., description="The email address of the person to invite to the Workspace."),
    admin: bool = Field(..., description="Set to true to grant the invited user admin-level permissions in the Workspace, or false for standard member permissions."),
    custom_role_id: int | None = Field(None, description="The ID of a custom role to assign to the invited user upon joining, if your Workspace has custom roles configured. Omit to use the default member role."),
) -> dict[str, Any]:
    """Invites a user to join a Workspace as a full member via email. This endpoint is exclusive to Enterprise Plan Workspaces; use the Invite Guest endpoint to add guest-level users instead."""

    # Construct request model with validation
    try:
        _request = _models.InviteUserToWorkspaceRequest(
            path=_models.InviteUserToWorkspaceRequestPath(team_id=team_id),
            body=_models.InviteUserToWorkspaceRequestBody(email=email, admin=admin, custom_role_id=custom_role_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for invite_workspace_member: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/team/{team_id}/user", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/team/{team_id}/user"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("invite_workspace_member")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("invite_workspace_member", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="invite_workspace_member",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Users
@mcp.tool()
async def get_workspace_user(
    team_id: float = Field(..., description="The unique numeric ID of the Workspace (also referred to as a team) containing the user."),
    user_id: float = Field(..., description="The unique numeric ID of the user to retrieve within the specified Workspace."),
    include_shared: bool | None = Field(None, description="When set to false, excludes details of items shared with the user as a guest; defaults to true to include all shared item details."),
) -> dict[str, Any]:
    """Retrieves detailed profile and role information for a specific user within a Workspace. Available exclusively on the Enterprise Plan."""

    # Construct request model with validation
    try:
        _request = _models.GetUserRequest(
            path=_models.GetUserRequestPath(team_id=team_id, user_id=user_id),
            query=_models.GetUserRequestQuery(include_shared=include_shared)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_workspace_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/team/{team_id}/user/{user_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/team/{team_id}/user/{user_id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_workspace_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_workspace_user", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_workspace_user",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Users
@mcp.tool()
async def update_workspace_user(
    team_id: float = Field(..., description="The unique identifier of the Workspace (team) in which the user will be updated."),
    user_id: float = Field(..., description="The unique identifier of the user to be updated within the specified Workspace."),
    username: str = Field(..., description="The new display name to assign to the user within the Workspace."),
    admin: bool = Field(..., description="Whether the user should be granted admin-level privileges in the Workspace. Set to true to grant admin access, false to revoke it."),
    custom_role_id: int = Field(..., description="The identifier of the custom role to assign to the user, as defined in the Workspace's Enterprise role configuration."),
) -> dict[str, Any]:
    """Update a workspace user's display name, admin status, and custom role assignment. This endpoint is exclusively available to Workspaces on the Enterprise Plan."""

    # Construct request model with validation
    try:
        _request = _models.EditUserOnWorkspaceRequest(
            path=_models.EditUserOnWorkspaceRequestPath(team_id=team_id, user_id=user_id),
            body=_models.EditUserOnWorkspaceRequestBody(username=username, admin=admin, custom_role_id=custom_role_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_workspace_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/team/{team_id}/user/{user_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/team/{team_id}/user/{user_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_workspace_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_workspace_user", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_workspace_user",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Users
@mcp.tool()
async def remove_workspace_user(
    team_id: float = Field(..., description="The unique identifier of the Workspace (team) from which the user will be removed."),
    user_id: float = Field(..., description="The unique identifier of the user to be deactivated and removed from the Workspace."),
) -> dict[str, Any]:
    """Deactivates and removes a user from the specified Workspace, revoking their access. This endpoint is exclusively available to Workspaces on the Enterprise Plan."""

    # Construct request model with validation
    try:
        _request = _models.RemoveUserFromWorkspaceRequest(
            path=_models.RemoveUserFromWorkspaceRequestPath(team_id=team_id, user_id=user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_workspace_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/team/{team_id}/user/{user_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/team/{team_id}/user/{user_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_workspace_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_workspace_user", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_workspace_user",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Views
@mcp.tool()
async def list_workspace_views(team_id: float = Field(..., description="The unique identifier of the Workspace whose Everything-level views you want to retrieve.")) -> dict[str, Any]:
    """Retrieves all task and page views available at the Everything level of a Workspace, providing a top-level overview of all views across the entire Workspace."""

    # Construct request model with validation
    try:
        _request = _models.GetTeamViewsRequest(
            path=_models.GetTeamViewsRequestPath(team_id=team_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_workspace_views: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/team/{team_id}/view", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/team/{team_id}/view"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_workspace_views")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_workspace_views", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_workspace_views",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Views
@mcp.tool()
async def create_workspace_view(
    team_id: float = Field(..., description="The unique identifier of the Workspace in which to create the view."),
    name: str = Field(..., description="The display name for the new view."),
    type_: str = Field(..., alias="type", description="The view type to create. Determines the visual layout and available features for the view."),
    grouping_field: str = Field(..., alias="groupingField", description="The field by which tasks in the view are grouped. Use 'none' to disable grouping."),
    grouping_dir: int = Field(..., alias="groupingDir", description="The sort direction for groups. Use 1 for ascending order (e.g., urgent priority at top) or -1 for descending order (e.g., no priority at top)."),
    grouping_collapsed: list[str] = Field(..., alias="groupingCollapsed", description="An array of group identifiers that should be rendered in a collapsed state by default. Order is not significant; each item is a group identifier string."),
    divide_collapsed: list[str] = Field(..., alias="divideCollapsed", description="An array of division identifiers that should be rendered in a collapsed state by default. Order is not significant; each item is a division identifier string."),
    ignore: bool = Field(..., description="When true, certain default behaviors or validations are bypassed during view creation."),
    sorting_fields: list[str] = Field(..., alias="sortingFields", description="An ordered array of field objects specifying the sort fields and their directions. Supports the same fields available when filtering a view."),
    filters_fields: list[str] = Field(..., alias="filtersFields", description="An array of filter field objects defining which fields and conditions are used to filter tasks displayed in the view. Refer to the filter-views documentation for available fields."),
    columns_fields: list[str] = Field(..., alias="columnsFields", description="An array of column field objects controlling which columns are visible in the view. Custom Fields must use the 'cf_' prefix and be formatted as a JSON object with the Custom Field ID."),
    op: str = Field(..., description="The logical operator used to combine multiple filter conditions. Use 'AND' to require all conditions to match, or 'OR' to require any condition to match."),
    search: str = Field(..., description="A search string used to filter tasks displayed in the view by matching task names or content."),
    show_closed: bool = Field(..., description="When true, closed tasks are included in the view alongside open tasks."),
    assignees: list[str] = Field(..., description="An array of assignee identifiers used to filter tasks shown in the view to only those assigned to the specified users."),
    assigned_comments: bool = Field(..., description="When true, the view displays comments that are assigned to users."),
    unassigned_tasks: bool = Field(..., description="When true, tasks with no assignee are included in the view."),
    show_task_locations: bool = Field(..., description="When true, the location (List, Folder, Space) of each task is displayed within the view."),
    show_subtasks: int = Field(..., description="Controls how subtasks are displayed. Use 1 to show subtasks separately, 2 to show them expanded inline, or 3 to show them collapsed inline."),
    show_subtask_parent_names: bool = Field(..., description="When true, the parent task name is shown alongside each subtask in the view."),
    show_closed_subtasks: bool = Field(..., description="When true, closed subtasks are included in the view."),
    show_assignees: bool = Field(..., description="When true, assignee avatars or names are displayed on task cards or rows within the view."),
    show_images: bool = Field(..., description="When true, image attachments are displayed as previews on task cards or rows within the view."),
    collapse_empty_columns: str | None = Field(..., description="Controls whether empty columns are collapsed in the view. Applicable primarily to Board-type views."),
    me_comments: bool = Field(..., description="When true, the view is filtered to show only comments that mention or are assigned to the current user."),
    me_subtasks: bool = Field(..., description="When true, the view is filtered to show only subtasks assigned to or created by the current user."),
    me_checklists: bool = Field(..., description="When true, the view is filtered to show only checklists assigned to or created by the current user."),
    divide_field: None = Field(None, alias="divideField", description="The field used to divide tasks within groups. Set to null to disable division."),
    divide_dir: None = Field(None, alias="divideDir", description="The sort direction for divided groups. Set to null to disable."),
) -> dict[str, Any]:
    """Create a new view at the Everything (Workspace) level, supporting view types such as List, Board, Calendar, Table, Timeline, Workload, Activity, Map, Chat, or Gantt. Configure grouping, sorting, filtering, and display settings for the view."""

    # Construct request model with validation
    try:
        _request = _models.CreateTeamViewRequest(
            path=_models.CreateTeamViewRequestPath(team_id=team_id),
            body=_models.CreateTeamViewRequestBody(name=name, type_=type_,
                grouping=_models.CreateTeamViewRequestBodyGrouping(field=grouping_field, dir_=grouping_dir, collapsed=grouping_collapsed, ignore=ignore),
                divide=_models.CreateTeamViewRequestBodyDivide(field=divide_field, dir_=divide_dir, collapsed=divide_collapsed),
                sorting=_models.CreateTeamViewRequestBodySorting(fields=sorting_fields),
                filters=_models.CreateTeamViewRequestBodyFilters(fields=filters_fields, op=op, search=search, show_closed=show_closed),
                columns=_models.CreateTeamViewRequestBodyColumns(fields=columns_fields),
                team_sidebar=_models.CreateTeamViewRequestBodyTeamSidebar(assignees=assignees, assigned_comments=assigned_comments, unassigned_tasks=unassigned_tasks),
                settings=_models.CreateTeamViewRequestBodySettings(show_task_locations=show_task_locations, show_subtasks=show_subtasks, show_subtask_parent_names=show_subtask_parent_names, show_closed_subtasks=show_closed_subtasks, show_assignees=show_assignees, show_images=show_images, collapse_empty_columns=collapse_empty_columns, me_comments=me_comments, me_subtasks=me_subtasks, me_checklists=me_checklists))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_workspace_view: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/team/{team_id}/view", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/team/{team_id}/view"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_workspace_view")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_workspace_view", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_workspace_view",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Views
@mcp.tool()
async def list_space_views(space_id: float = Field(..., description="The unique identifier of the Space whose views you want to retrieve.")) -> dict[str, Any]:
    """Retrieve all task and page views available within a specific Space. Useful for discovering how work is organized and displayed within a Space."""

    # Construct request model with validation
    try:
        _request = _models.GetSpaceViewsRequest(
            path=_models.GetSpaceViewsRequestPath(space_id=space_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_space_views: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/space/{space_id}/view", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/space/{space_id}/view"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_space_views")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_space_views", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_space_views",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Views
@mcp.tool()
async def create_space_view(
    space_id: float = Field(..., description="The unique identifier of the Space where the new view will be created."),
    name: str = Field(..., description="The display name for the new view."),
    type_: str = Field(..., alias="type", description="The view type to create. Determines the layout and interaction model for tasks in this view."),
    grouping_field: str = Field(..., alias="groupingField", description="The field by which tasks in the view are grouped. Use 'none' to disable grouping."),
    grouping_dir: int = Field(..., alias="groupingDir", description="Sort direction for groups. Use 1 for ascending order (e.g., urgent priority at top) or -1 for descending order (e.g., no priority at top)."),
    grouping_collapsed: list[str] = Field(..., alias="groupingCollapsed", description="An array of group identifiers that should be rendered in a collapsed state by default in this view."),
    divide_collapsed: list[str] = Field(..., alias="divideCollapsed", description="An array of division identifiers that should be rendered in a collapsed state by default in this view."),
    ignore: bool = Field(..., description="When true, certain default behaviors or validations are bypassed during view creation."),
    sorting_fields: list[str] = Field(..., alias="sortingFields", description="An ordered array of field objects specifying the sort criteria for tasks in the view. Supports the same fields available when filtering a view."),
    filters_fields: list[str] = Field(..., alias="filtersFields", description="An array of filter field objects that restrict which tasks appear in the view. Refer to the filter-views documentation for the full list of supported fields."),
    columns_fields: list[str] = Field(..., alias="columnsFields", description="An array of column field objects controlling which columns are visible in the view. Custom Fields must use the 'cf_' prefix and be formatted as a JSON object with the Custom Field ID."),
    op: str = Field(..., description="Logical operator applied to combine multiple filter conditions. Use 'AND' to require all conditions, or 'OR' to require any one condition."),
    search: str = Field(..., description="A search string used to filter tasks displayed in the view by matching text content."),
    show_closed: bool = Field(..., description="When true, closed tasks are included in the view alongside open tasks."),
    assignees: list[str] = Field(..., description="An array of assignee identifiers used to filter tasks shown in the view to only those assigned to the specified users."),
    assigned_comments: bool = Field(..., description="When true, the view displays tasks that have comments assigned to specific users."),
    unassigned_tasks: bool = Field(..., description="When true, tasks with no assignee are included in the view."),
    show_task_locations: bool = Field(..., description="When true, the location (List, Folder, Space) of each task is displayed within the view."),
    show_subtasks: int = Field(..., description="Controls how subtasks are displayed. Use 1 to show subtasks separately, 2 to show them expanded inline, or 3 to show them collapsed inline."),
    show_subtask_parent_names: bool = Field(..., description="When true, the parent task name is shown alongside each subtask in the view for additional context."),
    show_closed_subtasks: bool = Field(..., description="When true, closed subtasks are included in the view."),
    show_assignees: bool = Field(..., description="When true, assignee avatars or names are displayed on task cards within the view."),
    show_images: bool = Field(..., description="When true, image attachments are previewed directly on task cards within the view."),
    collapse_empty_columns: str | None = Field(..., description="Controls whether empty columns are collapsed in applicable view types such as Board."),
    me_comments: bool = Field(..., description="When true, the view is filtered to show only tasks that have comments from the currently authenticated user."),
    me_subtasks: bool = Field(..., description="When true, the view is filtered to show only tasks that have subtasks assigned to the currently authenticated user."),
    me_checklists: bool = Field(..., description="When true, the view is filtered to show only tasks that have checklist items assigned to the currently authenticated user."),
    divide_field: None = Field(None, alias="divideField", description="The field used to divide tasks within groups. Set to null to disable division."),
    divide_dir: None = Field(None, alias="divideDir", description="Sort direction for divided groups. Set to null to disable."),
) -> dict[str, Any]:
    """Create a new view (List, Board, Calendar, Table, Timeline, Workload, Activity, Map, Chat, or Gantt) within a specified Space, with full control over grouping, sorting, filtering, and display settings."""

    # Construct request model with validation
    try:
        _request = _models.CreateSpaceViewRequest(
            path=_models.CreateSpaceViewRequestPath(space_id=space_id),
            body=_models.CreateSpaceViewRequestBody(name=name, type_=type_,
                grouping=_models.CreateSpaceViewRequestBodyGrouping(field=grouping_field, dir_=grouping_dir, collapsed=grouping_collapsed, ignore=ignore),
                divide=_models.CreateSpaceViewRequestBodyDivide(field=divide_field, dir_=divide_dir, collapsed=divide_collapsed),
                sorting=_models.CreateSpaceViewRequestBodySorting(fields=sorting_fields),
                filters=_models.CreateSpaceViewRequestBodyFilters(fields=filters_fields, op=op, search=search, show_closed=show_closed),
                columns=_models.CreateSpaceViewRequestBodyColumns(fields=columns_fields),
                team_sidebar=_models.CreateSpaceViewRequestBodyTeamSidebar(assignees=assignees, assigned_comments=assigned_comments, unassigned_tasks=unassigned_tasks),
                settings=_models.CreateSpaceViewRequestBodySettings(show_task_locations=show_task_locations, show_subtasks=show_subtasks, show_subtask_parent_names=show_subtask_parent_names, show_closed_subtasks=show_closed_subtasks, show_assignees=show_assignees, show_images=show_images, collapse_empty_columns=collapse_empty_columns, me_comments=me_comments, me_subtasks=me_subtasks, me_checklists=me_checklists))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_space_view: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/space/{space_id}/view", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/space/{space_id}/view"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_space_view")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_space_view", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_space_view",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Views
@mcp.tool()
async def list_folder_views(folder_id: float = Field(..., description="The unique identifier of the Folder whose views you want to retrieve.")) -> dict[str, Any]:
    """Retrieves all task and page views available within a specific Folder. Use this to discover the views configured for organizing and displaying folder content."""

    # Construct request model with validation
    try:
        _request = _models.GetFolderViewsRequest(
            path=_models.GetFolderViewsRequestPath(folder_id=folder_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_folder_views: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/folder/{folder_id}/view", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/folder/{folder_id}/view"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_folder_views")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_folder_views", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_folder_views",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Views
@mcp.tool()
async def create_folder_view(
    folder_id: float = Field(..., description="The unique numeric identifier of the folder where the new view will be created."),
    name: str = Field(..., description="The display name for the new view."),
    type_: str = Field(..., alias="type", description="The view type to create. Must be one of the supported layout types: list, board, calendar, table, timeline, workload, activity, map, conversation, or gantt."),
    grouping_field: str = Field(..., alias="groupingField", description="The field by which tasks in the view are grouped. Accepted values are none, status, priority, assignee, tag, or dueDate."),
    grouping_dir: int = Field(..., alias="groupingDir", description="Sort direction for the grouping field. Use 1 for ascending order (e.g., urgent priority at top) or -1 for descending order (e.g., no priority at top)."),
    grouping_collapsed: list[str] = Field(..., alias="groupingCollapsed", description="An array of group identifiers that should appear collapsed by default in the view. Order is not significant; each item represents a group to collapse."),
    divide_collapsed: list[str] = Field(..., alias="divideCollapsed", description="An array of divide group identifiers that should appear collapsed by default. Order is not significant; each item represents a divide group to collapse."),
    ignore: bool = Field(..., description="When true, certain default behaviors or notifications for this view are ignored. Consult ClickUp documentation for the specific behavior this flag suppresses."),
    sorting_fields: list[str] = Field(..., alias="sortingFields", description="An ordered array of field objects defining the sort sequence applied to tasks in the view. Supports the same fields available when filtering a view; earlier entries in the array take sort precedence."),
    filters_fields: list[str] = Field(..., alias="filtersFields", description="An array of filter field objects that restrict which tasks appear in the view. Refer to the ClickUp filter-views documentation for the full list of supported field identifiers."),
    columns_fields: list[str] = Field(..., alias="columnsFields", description="An array of column field objects controlling which columns are visible in the view. Custom Fields must use the cf_ prefix and be formatted as a JSON object with the Custom Field ID."),
    op: str = Field(..., description="Logical operator applied to combine multiple filter conditions. Use AND to require all filters to match, or OR to require at least one filter to match."),
    search: str = Field(..., description="A search string used to filter tasks displayed in the view by matching against task names or content."),
    show_closed: bool = Field(..., description="When true, closed tasks are included in the view alongside open tasks."),
    assignees: list[str] = Field(..., description="An array of assignee user IDs used to filter tasks shown in the view to only those assigned to the specified users."),
    assigned_comments: bool = Field(..., description="When true, the view displays tasks that have comments assigned to users."),
    unassigned_tasks: bool = Field(..., description="When true, tasks with no assignee are included in the view."),
    show_task_locations: bool = Field(..., description="When true, the location (Space, Folder, List) of each task is shown within the view."),
    show_subtasks: int = Field(..., description="Controls how subtasks are displayed. Use 1 to show subtasks separately, 2 to show them expanded inline, or 3 to show them collapsed inline."),
    show_subtask_parent_names: bool = Field(..., description="When true, the parent task name is displayed alongside each subtask in the view for additional context."),
    show_closed_subtasks: bool = Field(..., description="When true, closed subtasks are included in the view."),
    show_assignees: bool = Field(..., description="When true, assignee avatars or names are shown on task cards within the view."),
    show_images: bool = Field(..., description="When true, image attachments are displayed inline on task cards within the view."),
    collapse_empty_columns: str | None = Field(..., description="Controls whether empty columns are collapsed in the view. Provide the desired collapse behavior as a string value."),
    me_comments: bool = Field(..., description="When true, the view is filtered to show only tasks that have comments from the currently authenticated user."),
    me_subtasks: bool = Field(..., description="When true, the view is filtered to show only subtasks assigned to or created by the currently authenticated user."),
    me_checklists: bool = Field(..., description="When true, the view is filtered to show only tasks with checklists belonging to the currently authenticated user."),
    divide_field: None = Field(None, alias="divideField", description="The field used to divide tasks within the view. Set to null to disable division."),
    divide_dir: None = Field(None, alias="divideDir", description="Sort direction for the divide field. Set to null to disable divide sorting."),
) -> dict[str, Any]:
    """Create a new view (List, Board, Calendar, Table, Timeline, Workload, Activity, Map, Chat, or Gantt) inside a specified Folder, with full control over grouping, sorting, filtering, and display settings."""

    # Construct request model with validation
    try:
        _request = _models.CreateFolderViewRequest(
            path=_models.CreateFolderViewRequestPath(folder_id=folder_id),
            body=_models.CreateFolderViewRequestBody(name=name, type_=type_,
                grouping=_models.CreateFolderViewRequestBodyGrouping(field=grouping_field, dir_=grouping_dir, collapsed=grouping_collapsed, ignore=ignore),
                divide=_models.CreateFolderViewRequestBodyDivide(field=divide_field, dir_=divide_dir, collapsed=divide_collapsed),
                sorting=_models.CreateFolderViewRequestBodySorting(fields=sorting_fields),
                filters=_models.CreateFolderViewRequestBodyFilters(fields=filters_fields, op=op, search=search, show_closed=show_closed),
                columns=_models.CreateFolderViewRequestBodyColumns(fields=columns_fields),
                team_sidebar=_models.CreateFolderViewRequestBodyTeamSidebar(assignees=assignees, assigned_comments=assigned_comments, unassigned_tasks=unassigned_tasks),
                settings=_models.CreateFolderViewRequestBodySettings(show_task_locations=show_task_locations, show_subtasks=show_subtasks, show_subtask_parent_names=show_subtask_parent_names, show_closed_subtasks=show_closed_subtasks, show_assignees=show_assignees, show_images=show_images, collapse_empty_columns=collapse_empty_columns, me_comments=me_comments, me_subtasks=me_subtasks, me_checklists=me_checklists))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_folder_view: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/folder/{folder_id}/view", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/folder/{folder_id}/view"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_folder_view")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_folder_view", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_folder_view",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Views
@mcp.tool()
async def list_views(list_id: float = Field(..., description="The unique identifier of the List whose views you want to retrieve.")) -> dict[str, Any]:
    """Retrieves all task and page views available for a specified List. Returns standard views and required views as separate response groups."""

    # Construct request model with validation
    try:
        _request = _models.GetListViewsRequest(
            path=_models.GetListViewsRequestPath(list_id=list_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_views: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/list/{list_id}/view", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/list/{list_id}/view"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_views")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_views", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_views",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Views
@mcp.tool()
async def create_list_view(
    list_id: float = Field(..., description="The unique identifier of the List in which to create the new view."),
    name: str = Field(..., description="The display name for the new view."),
    type_: str = Field(..., alias="type", description="The view type to create. Determines the visual layout and available features for the view."),
    grouping_field: str = Field(..., alias="groupingField", description="The field by which tasks in the view are grouped. Use 'none' to disable grouping."),
    grouping_dir: int = Field(..., alias="groupingDir", description="The sort direction for groups. Use 1 for ascending order (e.g., urgent priority at top) or -1 for descending order (e.g., no priority at top)."),
    grouping_collapsed: list[str] = Field(..., alias="groupingCollapsed", description="An array of group identifiers that should be rendered in a collapsed state by default in the view."),
    divide_collapsed: list[str] = Field(..., alias="divideCollapsed", description="An array of divide-group identifiers that should be rendered in a collapsed state by default in the view."),
    ignore: bool = Field(..., description="When true, certain default behaviors or inherited settings are ignored when creating the view."),
    sorting_fields: list[str] = Field(..., alias="sortingFields", description="An ordered array of field definitions specifying which fields to sort by and in what direction. Supports the same fields available when filtering a view."),
    filters_fields: list[str] = Field(..., alias="filtersFields", description="An array of filter field definitions to apply to the view, limiting which tasks are displayed. Refer to the filter-views documentation for available fields."),
    columns_fields: list[str] = Field(..., alias="columnsFields", description="An array of column field definitions to display in the view. Custom Fields must use the 'cf_' prefix and be formatted as a JSON object with the Custom Field ID."),
    op: str = Field(..., description="The logical operator used to combine multiple filter conditions. Use 'AND' to require all conditions, or 'OR' to require any condition."),
    search: str = Field(..., description="A search string used to filter tasks displayed in the view by matching text content."),
    show_closed: bool = Field(..., description="When true, closed tasks are included in the view alongside open tasks."),
    assignees: list[str] = Field(..., description="An array of assignee identifiers used to filter the view to tasks assigned to specific users."),
    assigned_comments: bool = Field(..., description="When true, the view displays comments that have been assigned to users."),
    unassigned_tasks: bool = Field(..., description="When true, tasks with no assignee are included in the view."),
    show_task_locations: bool = Field(..., description="When true, the location (Space, Folder, List) of each task is shown within the view."),
    show_subtasks: int = Field(..., description="Controls how subtasks are displayed. Use 1 to show subtasks separately, 2 to show them expanded inline, or 3 to show them collapsed inline."),
    show_subtask_parent_names: bool = Field(..., description="When true, the parent task name is displayed alongside each subtask in the view."),
    show_closed_subtasks: bool = Field(..., description="When true, closed subtasks are included in the view."),
    show_assignees: bool = Field(..., description="When true, assignee avatars or names are shown on task cards or rows within the view."),
    show_images: bool = Field(..., description="When true, image attachments are previewed directly on task cards or rows within the view."),
    collapse_empty_columns: str | None = Field(..., description="Controls whether empty columns are collapsed in the view, reducing visual clutter."),
    me_comments: bool = Field(..., description="When true, the view is filtered to show only tasks that have comments from the current user."),
    me_subtasks: bool = Field(..., description="When true, the view is filtered to show only tasks that have subtasks assigned to or created by the current user."),
    me_checklists: bool = Field(..., description="When true, the view is filtered to show only tasks that have checklist items assigned to the current user."),
    divide_field: None = Field(None, alias="divideField", description="The field used to divide tasks within the view. Set to null to disable division."),
    divide_dir: None = Field(None, alias="divideDir", description="The sort direction for the divide field. Set to null to disable."),
) -> dict[str, Any]:
    """Create a new view (List, Board, Calendar, Table, Timeline, Workload, Activity, Map, Chat, or Gantt) within a specified List, configuring grouping, sorting, filtering, and display options."""

    # Construct request model with validation
    try:
        _request = _models.CreateListViewRequest(
            path=_models.CreateListViewRequestPath(list_id=list_id),
            body=_models.CreateListViewRequestBody(name=name, type_=type_,
                grouping=_models.CreateListViewRequestBodyGrouping(field=grouping_field, dir_=grouping_dir, collapsed=grouping_collapsed, ignore=ignore),
                divide=_models.CreateListViewRequestBodyDivide(field=divide_field, dir_=divide_dir, collapsed=divide_collapsed),
                sorting=_models.CreateListViewRequestBodySorting(fields=sorting_fields),
                filters=_models.CreateListViewRequestBodyFilters(fields=filters_fields, op=op, search=search, show_closed=show_closed),
                columns=_models.CreateListViewRequestBodyColumns(fields=columns_fields),
                team_sidebar=_models.CreateListViewRequestBodyTeamSidebar(assignees=assignees, assigned_comments=assigned_comments, unassigned_tasks=unassigned_tasks),
                settings=_models.CreateListViewRequestBodySettings(show_task_locations=show_task_locations, show_subtasks=show_subtasks, show_subtask_parent_names=show_subtask_parent_names, show_closed_subtasks=show_closed_subtasks, show_assignees=show_assignees, show_images=show_images, collapse_empty_columns=collapse_empty_columns, me_comments=me_comments, me_subtasks=me_subtasks, me_checklists=me_checklists))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_list_view: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/list/{list_id}/view", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/list/{list_id}/view"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_list_view")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_list_view", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_list_view",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Views
@mcp.tool()
async def get_view(view_id: str = Field(..., description="The unique identifier of the view to retrieve. Corresponds to a specific task or page view within the workspace.")) -> dict[str, Any]:
    """Retrieves metadata and configuration details for a specific task or page view by its unique identifier. The fields returned vary depending on the view type."""

    # Construct request model with validation
    try:
        _request = _models.GetViewRequest(
            path=_models.GetViewRequestPath(view_id=view_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_view: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/view/{view_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/view/{view_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_view")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_view", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_view",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Views
@mcp.tool()
async def update_view(
    view_id: str = Field(..., description="The unique identifier of the view to update."),
    name: str = Field(..., description="The new display name for the view."),
    type_: str = Field(..., alias="type", description="The type of view being updated (e.g., list, board, calendar)."),
    parent_type: int = Field(..., alias="parentType", description="The hierarchy level of the parent location where the view resides. Use 7 for Workspace, 4 for Space, 5 for Folder, or 6 for List."),
    id_: str = Field(..., alias="id", description="The unique identifier of the Workspace, Space, Folder, or List that contains this view."),
    grouping_field: str = Field(..., alias="groupingField", description="The field by which tasks in the view are grouped. Accepted values are none, status, priority, assignee, tag, or dueDate."),
    grouping_dir: int = Field(..., alias="groupingDir", description="The sort direction for grouping. Use 1 for ascending order (e.g., urgent priority at top) or -1 for descending order (e.g., no priority at top)."),
    grouping_collapsed: list[str] = Field(..., alias="groupingCollapsed", description="An array of group identifiers that should be rendered in a collapsed state within the view."),
    divide_collapsed: list[str] = Field(..., alias="divideCollapsed", description="An array of divide group identifiers that should be rendered in a collapsed state within the view."),
    ignore: bool = Field(..., description="When true, ignores the default view settings and applies only the explicitly provided configuration."),
    sorting_fields: list[str] = Field(..., alias="sortingFields", description="An ordered array of field objects defining the sort criteria for the view. Each item specifies a field and sort direction; refer to the filter-views documentation for supported field names."),
    filters_fields: list[str] = Field(..., alias="filtersFields", description="An array of filter field objects applied to the view to restrict which tasks are displayed. Refer to the filter-views documentation for the full list of supported fields."),
    columns_fields: list[str] = Field(..., alias="columnsFields", description="An array of column field objects defining which columns are visible in the view. Custom Fields must use the cf_ prefix and be formatted as a JSON object with the field's UUID."),
    op: str = Field(..., description="The logical operator used to combine multiple filter conditions. Use AND to require all conditions to match, or OR to require at least one condition to match."),
    search: str = Field(..., description="A text search string used to filter tasks displayed in the view by keyword."),
    show_closed: bool = Field(..., description="When true, closed tasks are included in the view alongside open tasks."),
    assignees: list[str] = Field(..., description="An array of assignee user IDs used to filter tasks shown in the view to only those assigned to the specified users."),
    assigned_comments: bool = Field(..., description="When true, the view displays only tasks that have comments assigned to a user."),
    unassigned_tasks: bool = Field(..., description="When true, tasks with no assignee are included in the view."),
    show_task_locations: bool = Field(..., description="When true, the location (Space, Folder, List) of each task is displayed within the view."),
    show_subtasks: int = Field(..., description="Controls how subtasks are displayed. Use 1 to show subtasks separately, 2 to show them expanded inline, or 3 to show them collapsed inline."),
    show_subtask_parent_names: bool = Field(..., description="When true, the parent task name is shown alongside each subtask in the view."),
    show_closed_subtasks: bool = Field(..., description="When true, closed subtasks are included in the view."),
    show_assignees: bool = Field(..., description="When true, assignee avatars or names are displayed on task cards within the view."),
    show_images: bool = Field(..., description="When true, image attachments are previewed directly on task cards within the view."),
    collapse_empty_columns: str | None = Field(..., description="Controls whether empty columns are collapsed in the view. Applicable primarily to Board views."),
    me_comments: bool = Field(..., description="When true, the view filters to show only tasks that have comments from the currently authenticated user."),
    me_subtasks: bool = Field(..., description="When true, the view filters to show only tasks that have subtasks assigned to the currently authenticated user."),
    me_checklists: bool = Field(..., description="When true, the view filters to show only tasks that have checklist items assigned to the currently authenticated user."),
    divide_field: None = Field(None, alias="divideField", description="The field used to divide tasks within the view. Set to null to disable division."),
    divide_dir: None = Field(None, alias="divideDir", description="The sort direction for the divide field. Set to null to disable."),
) -> dict[str, Any]:
    """Update an existing view by renaming it or modifying its grouping, sorting, filters, columns, and display settings. Supports all view types within a Workspace, Space, Folder, or List."""

    # Construct request model with validation
    try:
        _request = _models.UpdateViewRequest(
            path=_models.UpdateViewRequestPath(view_id=view_id),
            body=_models.UpdateViewRequestBody(name=name, type_=type_,
                parent=_models.UpdateViewRequestBodyParent(type_=parent_type, id_=id_),
                grouping=_models.UpdateViewRequestBodyGrouping(field=grouping_field, dir_=grouping_dir, collapsed=grouping_collapsed, ignore=ignore),
                divide=_models.UpdateViewRequestBodyDivide(field=divide_field, dir_=divide_dir, collapsed=divide_collapsed),
                sorting=_models.UpdateViewRequestBodySorting(fields=sorting_fields),
                filters=_models.UpdateViewRequestBodyFilters(fields=filters_fields, op=op, search=search, show_closed=show_closed),
                columns=_models.UpdateViewRequestBodyColumns(fields=columns_fields),
                team_sidebar=_models.UpdateViewRequestBodyTeamSidebar(assignees=assignees, assigned_comments=assigned_comments, unassigned_tasks=unassigned_tasks),
                settings=_models.UpdateViewRequestBodySettings(show_task_locations=show_task_locations, show_subtasks=show_subtasks, show_subtask_parent_names=show_subtask_parent_names, show_closed_subtasks=show_closed_subtasks, show_assignees=show_assignees, show_images=show_images, collapse_empty_columns=collapse_empty_columns, me_comments=me_comments, me_subtasks=me_subtasks, me_checklists=me_checklists))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_view: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/view/{view_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/view/{view_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_view")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_view", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_view",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Views
@mcp.tool()
async def delete_view(view_id: str = Field(..., description="The unique identifier of the view to be deleted.")) -> dict[str, Any]:
    """Permanently deletes a specified view by its unique identifier. This action is irreversible and removes the view and its configuration from the system."""

    # Construct request model with validation
    try:
        _request = _models.DeleteViewRequest(
            path=_models.DeleteViewRequestPath(view_id=view_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_view: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/view/{view_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/view/{view_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_view")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_view", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_view",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Views
@mcp.tool()
async def list_view_tasks(
    view_id: str = Field(..., description="The unique identifier of the view whose tasks you want to retrieve."),
    page: int = Field(..., description="The zero-based page number to retrieve for paginated results, where 0 returns the first page."),
) -> dict[str, Any]:
    """Retrieve all visible tasks within a specific ClickUp view, returned in paginated results."""

    # Construct request model with validation
    try:
        _request = _models.GetViewTasksRequest(
            path=_models.GetViewTasksRequestPath(view_id=view_id),
            query=_models.GetViewTasksRequestQuery(page=page)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_view_tasks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/view/{view_id}/task", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/view/{view_id}/task"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_view_tasks")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_view_tasks", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_view_tasks",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Webhooks
@mcp.tool()
async def list_webhooks(team_id: float = Field(..., description="The unique identifier of the Workspace whose webhooks you want to retrieve.")) -> dict[str, Any]:
    """Retrieves all webhooks created via the API for a specified Workspace. Only webhooks created by the authenticated user are returned."""

    # Construct request model with validation
    try:
        _request = _models.GetWebhooksRequest(
            path=_models.GetWebhooksRequestPath(team_id=team_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_webhooks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/team/{team_id}/webhook", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/team/{team_id}/webhook"
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

# Tags: Webhooks
@mcp.tool()
async def delete_webhook(webhook_id: str = Field(..., description="The unique identifier (UUID) of the webhook to delete.")) -> dict[str, Any]:
    """Permanently deletes a webhook, stopping all event monitoring and location tracking associated with it. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteWebhookRequest(
            path=_models.DeleteWebhookRequestPath(webhook_id=webhook_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_webhook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/webhook/{webhook_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/webhook/{webhook_id}"
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
        print("  python click_up_server.py", file=sys.stderr)
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

    parser = argparse.ArgumentParser(description="ClickUp MCP Server")

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
    logger.info("Starting ClickUp MCP Server")
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

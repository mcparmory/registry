#!/usr/bin/env python3
"""
Polygon API MCP Server
Generated: 2026-04-23 21:37:40 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

import argparse
import asyncio
import contextlib
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
from typing import Any, Literal, cast, overload

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
from fastmcp.tools import ToolResult
from pydantic import Field

BASE_URL = os.getenv("BASE_URL", "https://api.massive.com")
SERVER_NAME = "Polygon API"
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

class UpstreamAPIError(Exception):
    """Expected upstream API error that should not become a server traceback."""

    def __init__(
        self,
        *,
        status_code: int,
        request_id: str | None,
        method: str,
        path: str,
        tool_name: str | None,
        error_data: dict[str, Any],
        error_message: str,
    ) -> None:
        super().__init__(error_message)
        self.status_code = status_code
        self.request_id = request_id
        self.method = method
        self.path = path
        self.tool_name = tool_name
        self.error_data = error_data
        self.error_message = error_message


async def _make_request(
    method: str,
    path: str,
    params: dict[str, Any] | None = None,
    body: Any = None,
    body_content_type: str | None = None,
    multipart_file_fields: list[str] | None = None,
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
    if (
        body is not None
        and method.upper() in ("POST", "PUT", "PATCH")
        and (body_content_type is None or body_content_type == "application/json")
    ):
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
            _form_content = None
            if body_content_type == "application/x-www-form-urlencoded":
                _data = body if isinstance(body, dict) else None
                if isinstance(body, bytearray):
                    _form_content = bytes(body)
                elif isinstance(body, (bytes, str)):
                    _form_content = body
                elif body is not None and not isinstance(body, dict):
                    _form_content = str(body)
                else:
                    _form_content = None
            else:
                _data = None
            _files = None
            if body_content_type == "multipart/form-data":
                _multipart_parts: list[tuple[str, tuple[str | None, Any] | tuple[str, Any, str]]] = []
                _file_fields = set(multipart_file_fields or [])
                if isinstance(body, dict):
                    for _key, _value in body.items():
                        if _value is None:
                            continue
                        if _key in _file_fields:
                            _file_values = _value if isinstance(_value, (list, tuple)) else [_value]
                            for _file_item in _file_values:
                                if _file_item is None:
                                    continue
                                if isinstance(_file_item, str):
                                    _file_content = _file_item.encode("utf-8")
                                elif isinstance(_file_item, (bytes, bytearray)):
                                    _file_content = bytes(_file_item)
                                else:
                                    raise ValueError(
                                        f"Unsupported multipart file field '{_key}': "
                                        "expected str, bytes, or list of str/bytes, got "
                                        f"{type(_file_item).__name__}"
                                    )
                                _multipart_parts.append(
                                    (_key, (f"{_key}.bin", _file_content, "application/octet-stream"))
                                )
                        else:
                            if isinstance(_value, (dict, list)):
                                _part_value = json.dumps(_value)
                            elif isinstance(_value, bool):
                                _part_value = "true" if _value else "false"
                            else:
                                _part_value = str(_value)
                            _multipart_parts.append((_key, (None, _part_value)))
                elif body is not None:
                    if isinstance(body, str):
                        _file_content = body.encode("utf-8")
                    elif isinstance(body, (bytes, bytearray)):
                        _file_content = bytes(body)
                    else:
                        raise ValueError(
                            "Unsupported multipart file body: expected str or bytes "
                            f"for file part, got {type(body).__name__}"
                        )
                    _field_name = next(iter(_file_fields), "file")
                    _multipart_parts.append(
                        (_field_name, (f"{_field_name}.bin", _file_content, "application/octet-stream"))
                    )
                _files = _multipart_parts
            _content = None
            if body_content_type is not None and body_content_type not in ("application/json", "application/x-www-form-urlencoded", "multipart/form-data"):
                _raw = body
                if isinstance(_raw, (dict, list)):
                    _content = json.dumps(_raw).encode()
                elif isinstance(_raw, bytearray):
                    _content = bytes(_raw)
                else:
                    _content = _raw
            elif _form_content is not None:
                _content = _form_content
            response = await client.request(
                method=method,
                url=path,
                params=params,
                json=_json,
                data=_data,
                files=_files,
                content=cast(Any, _content),
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
                    raise UpstreamAPIError(
                        status_code=status_code,
                        request_id=request_id,
                        method=method,
                        path=path,
                        tool_name=tool_name,
                        error_data=sanitized_data,
                        error_message=error_message,
                    )

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

        except UpstreamAPIError:
            # Expected upstream HTTP error — already logged above.
            raise

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
        raise UpstreamAPIError(
            status_code=last_error.response.status_code,
            request_id=request_id,
            method=method,
            path=path,
            tool_name=tool_name,
            error_data=sanitized_error,
            error_message=error_message,
        )

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
                    with contextlib.suppress(json.JSONDecodeError, ValueError):
                        context.message.arguments[key] = json.loads(value)
        return await call_next(context)


# ============================================================================
# Helper Functions
# ============================================================================

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
    multipart_file_fields: list[str] | None = None,
    headers: dict[str, str] | None = None,
    cookies: dict[str, str] | None = None,
    raw_querystring: str | None = None,
) -> tuple[dict[str, Any] | ToolResult, int]:
    """
    Execute tool request with timeout handling and metrics recording.

    Returns:
        Tuple of (normalized_response_data_or_tool_result, status_code).
        Successful responses are normalized to dict format for Pydantic validation.
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
                multipart_file_fields=multipart_file_fields,
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

    except UpstreamAPIError as e:
        latency_ms = (time.time() - start_time) * 1000.0
        return ToolResult(
            content=e.error_message,
            structured_content={
                "ok": False,
                "status": e.status_code,
                "request_id": e.request_id,
                "method": e.method,
                "path": e.path,
                "error": e.error_message,
                "details": e.error_data,
            },
        ), e.status_code

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
    'BearerAuth',
]

# Initialize authentication handlers at server startup
_auth_handlers: dict[str, Any] = {}
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

mcp = FastMCP("Polygon API", middleware=[_JsonCoercionMiddleware()])

# Tags: benzinga
@mcp.tool()
async def list_analyst_insights(
    firm_any_of: str | None = Field(None, alias="firm.any_of", description="Filter results to analyst firms matching any of the specified values. Use comma-separated list for multiple firms."),
    firm_gt: str | None = Field(None, alias="firm.gt", description="Filter results to analyst firms lexicographically greater than the specified value."),
    firm_gte: str | None = Field(None, alias="firm.gte", description="Filter results to analyst firms lexicographically greater than or equal to the specified value."),
    firm_lt: str | None = Field(None, alias="firm.lt", description="Filter results to analyst firms lexicographically less than the specified value."),
    firm_lte: str | None = Field(None, alias="firm.lte", description="Filter results to analyst firms lexicographically less than or equal to the specified value."),
    rating_action_any_of: str | None = Field(None, alias="rating_action.any_of", description="Filter results to rating actions matching any of the specified values. Use comma-separated list for multiple actions (e.g., upgrade, downgrade, initiate)."),
    rating_action_gt: str | None = Field(None, alias="rating_action.gt", description="Filter results to rating actions lexicographically greater than the specified value."),
    rating_action_gte: str | None = Field(None, alias="rating_action.gte", description="Filter results to rating actions lexicographically greater than or equal to the specified value."),
    rating_action_lt: str | None = Field(None, alias="rating_action.lt", description="Filter results to rating actions lexicographically less than the specified value."),
    rating_action_lte: str | None = Field(None, alias="rating_action.lte", description="Filter results to rating actions lexicographically less than or equal to the specified value."),
    benzinga_rating_id_any_of: str | None = Field(None, alias="benzinga_rating_id.any_of", description="Filter results to Benzinga rating IDs matching any of the specified values. Use comma-separated list for multiple IDs."),
    benzinga_rating_id_gt: str | None = Field(None, alias="benzinga_rating_id.gt", description="Filter results to Benzinga rating IDs numerically greater than the specified value."),
    benzinga_rating_id_gte: str | None = Field(None, alias="benzinga_rating_id.gte", description="Filter results to Benzinga rating IDs numerically greater than or equal to the specified value."),
    benzinga_rating_id_lt: str | None = Field(None, alias="benzinga_rating_id.lt", description="Filter results to Benzinga rating IDs numerically less than the specified value."),
    benzinga_rating_id_lte: str | None = Field(None, alias="benzinga_rating_id.lte", description="Filter results to Benzinga rating IDs numerically less than or equal to the specified value."),
    limit: int | None = Field(None, description="Maximum number of results to return. Defaults to 100 if not specified. Maximum allowed value is 50,000.", ge=1, le=50001),
    sort: str | None = Field(None, description="Comma-separated list of columns to sort by, with sort direction appended to each column using '.asc' or '.desc'. Defaults to sorting by 'last_updated' in descending order if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve analyst insights and ratings for publicly traded companies, including recommendations and price targets from financial analysts. Filter by analyst firm, rating actions, or Benzinga rating IDs, with support for sorting and pagination."""

    # Construct request model with validation
    try:
        _request = _models.GetBenzingaV1AnalystInsightsRequest(
            query=_models.GetBenzingaV1AnalystInsightsRequestQuery(firm_any_of=firm_any_of, firm_gt=firm_gt, firm_gte=firm_gte, firm_lt=firm_lt, firm_lte=firm_lte, rating_action_any_of=rating_action_any_of, rating_action_gt=rating_action_gt, rating_action_gte=rating_action_gte, rating_action_lt=rating_action_lt, rating_action_lte=rating_action_lte, benzinga_rating_id_any_of=benzinga_rating_id_any_of, benzinga_rating_id_gt=benzinga_rating_id_gt, benzinga_rating_id_gte=benzinga_rating_id_gte, benzinga_rating_id_lt=benzinga_rating_id_lt, benzinga_rating_id_lte=benzinga_rating_id_lte, limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_analyst_insights: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/benzinga/v1/analyst-insights"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_analyst_insights")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_analyst_insights", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_analyst_insights",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: benzinga
@mcp.tool()
async def list_analysts(
    firm_name: str | None = Field(None, description="Filter results to analysts from a specific research firm or investment bank. Optional filter that narrows results to a single firm."),
    full_name: str | None = Field(None, description="Filter results to a specific analyst by their full name. Optional filter that narrows results to matching analysts."),
    limit: int | None = Field(None, description="Maximum number of results to return in the response. Defaults to 100 if not specified. Must be between 1 and 50,000.", ge=1, le=50001),
    sort: str | None = Field(None, description="Comma-separated list of columns to sort by, with sort direction specified per column using '.asc' or '.desc' suffix. Defaults to sorting by full_name in ascending order if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a comprehensive list of financial analysts with their performance metrics and identification details. Filter by research firm or analyst name, and customize sorting and result limits."""

    # Construct request model with validation
    try:
        _request = _models.GetBenzingaV1AnalystsRequest(
            query=_models.GetBenzingaV1AnalystsRequestQuery(firm_name=firm_name, full_name=full_name, limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_analysts: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/benzinga/v1/analysts"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_analysts")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_analysts", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_analysts",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: benzinga
@mcp.tool()
async def list_bulls_bears_say(
    limit: int | None = Field(None, description="Maximum number of results to return in the response, ranging from 1 to 5000. Defaults to 100 if not specified.", ge=1, le=5001),
    sort: str | None = Field(None, description="Comma-separated list of columns to sort results by, with each column followed by '.asc' or '.desc' to specify ascending or descending order. Defaults to sorting by ticker in descending order if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve analyst bull and bear case summaries for publicly traded companies, enabling investors to review both bullish and bearish investment arguments for informed decision-making."""

    # Construct request model with validation
    try:
        _request = _models.GetBenzingaV1BullsBearsSayRequest(
            query=_models.GetBenzingaV1BullsBearsSayRequestQuery(limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_bulls_bears_say: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/benzinga/v1/bulls-bears-say"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_bulls_bears_say")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_bulls_bears_say", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_bulls_bears_say",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: benzinga
@mcp.tool()
async def get_consensus_ratings(
    ticker: str = Field(..., description="The stock ticker symbol for which to retrieve consensus ratings."),
    limit: int | None = Field(None, description="Maximum number of results to return, ranging from 1 to 50,000. Defaults to 100 if not specified.", ge=1, le=50001),
) -> dict[str, Any] | ToolResult:
    """Retrieve aggregated analyst consensus ratings and price targets for a stock ticker, including detailed rating breakdowns and statistical insights across multiple analysts."""

    # Construct request model with validation
    try:
        _request = _models.GetBenzingaV1ConsensusRatingsRequest(
            path=_models.GetBenzingaV1ConsensusRatingsRequestPath(ticker=ticker),
            query=_models.GetBenzingaV1ConsensusRatingsRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_consensus_ratings: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/benzinga/v1/consensus-ratings/{ticker}", _request.path.model_dump(by_alias=True)) if _request.path else "/benzinga/v1/consensus-ratings/{ticker}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_consensus_ratings")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_consensus_ratings", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_consensus_ratings",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: benzinga
@mcp.tool()
async def list_earnings(
    date_status_any_of: str | None = Field(None, alias="date_status.any_of", description="Filter results to earnings records with a date_status matching any of the specified values. Use comma-separated values to filter by multiple statuses."),
    date_status_gt: str | None = Field(None, alias="date_status.gt", description="Filter results to earnings records where date_status is strictly greater than the specified value."),
    date_status_gte: str | None = Field(None, alias="date_status.gte", description="Filter results to earnings records where date_status is greater than or equal to the specified value."),
    date_status_lt: str | None = Field(None, alias="date_status.lt", description="Filter results to earnings records where date_status is strictly less than the specified value."),
    date_status_lte: str | None = Field(None, alias="date_status.lte", description="Filter results to earnings records where date_status is less than or equal to the specified value."),
    eps_surprise_percent_any_of: str | None = Field(None, alias="eps_surprise_percent.any_of", description="Filter results to earnings records with an EPS surprise percent matching any of the specified values. Use comma-separated floating-point numbers to filter by multiple surprise percentages."),
    eps_surprise_percent_gt: float | None = Field(None, alias="eps_surprise_percent.gt", description="Filter results to earnings records where EPS surprise percent is strictly greater than the specified value."),
    eps_surprise_percent_gte: float | None = Field(None, alias="eps_surprise_percent.gte", description="Filter results to earnings records where EPS surprise percent is greater than or equal to the specified value."),
    eps_surprise_percent_lt: float | None = Field(None, alias="eps_surprise_percent.lt", description="Filter results to earnings records where EPS surprise percent is strictly less than the specified value."),
    eps_surprise_percent_lte: float | None = Field(None, alias="eps_surprise_percent.lte", description="Filter results to earnings records where EPS surprise percent is less than or equal to the specified value."),
    revenue_surprise_percent_any_of: str | None = Field(None, alias="revenue_surprise_percent.any_of", description="Filter results to earnings records with a revenue surprise percent matching any of the specified values. Use comma-separated floating-point numbers to filter by multiple surprise percentages."),
    revenue_surprise_percent_gt: float | None = Field(None, alias="revenue_surprise_percent.gt", description="Filter results to earnings records where revenue surprise percent is strictly greater than the specified value."),
    revenue_surprise_percent_gte: float | None = Field(None, alias="revenue_surprise_percent.gte", description="Filter results to earnings records where revenue surprise percent is greater than or equal to the specified value."),
    revenue_surprise_percent_lt: float | None = Field(None, alias="revenue_surprise_percent.lt", description="Filter results to earnings records where revenue surprise percent is strictly less than the specified value."),
    revenue_surprise_percent_lte: float | None = Field(None, alias="revenue_surprise_percent.lte", description="Filter results to earnings records where revenue surprise percent is less than or equal to the specified value."),
    limit: int | None = Field(None, description="Maximum number of earnings records to return in the response. Defaults to 100 if not specified; maximum allowed is 50,000.", ge=1, le=50001),
    sort: str | None = Field(None, description="Comma-separated list of columns to sort results by. Append '.asc' or '.desc' to each column to specify sort direction. Defaults to sorting by 'last_updated' in descending order if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve earnings data from Benzinga for publicly traded companies, including actual and estimated EPS and revenue figures with surprise calculations. Filter by date status, earnings surprises, and customize result ordering and limits."""

    # Construct request model with validation
    try:
        _request = _models.GetBenzingaV1EarningsRequest(
            query=_models.GetBenzingaV1EarningsRequestQuery(date_status_any_of=date_status_any_of, date_status_gt=date_status_gt, date_status_gte=date_status_gte, date_status_lt=date_status_lt, date_status_lte=date_status_lte, eps_surprise_percent_any_of=eps_surprise_percent_any_of, eps_surprise_percent_gt=eps_surprise_percent_gt, eps_surprise_percent_gte=eps_surprise_percent_gte, eps_surprise_percent_lt=eps_surprise_percent_lt, eps_surprise_percent_lte=eps_surprise_percent_lte, revenue_surprise_percent_any_of=revenue_surprise_percent_any_of, revenue_surprise_percent_gt=revenue_surprise_percent_gt, revenue_surprise_percent_gte=revenue_surprise_percent_gte, revenue_surprise_percent_lt=revenue_surprise_percent_lt, revenue_surprise_percent_lte=revenue_surprise_percent_lte, limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_earnings: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/benzinga/v1/earnings"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_earnings")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_earnings", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_earnings",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: benzinga
@mcp.tool()
async def list_firms(
    limit: int | None = Field(None, description="Maximum number of results to return in a single response. Defaults to 100 if not specified. Must be between 1 and 50,000.", ge=1, le=50001),
    sort: str | None = Field(None, description="Comma-separated list of columns to sort results by, with sort direction specified per column using '.asc' or '.desc' suffix. Defaults to sorting by firm name in ascending order if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a list of financial firms from a comprehensive database of financial institutions and research firms, with support for pagination and custom sorting."""

    # Construct request model with validation
    try:
        _request = _models.GetBenzingaV1FirmsRequest(
            query=_models.GetBenzingaV1FirmsRequestQuery(limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_firms: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/benzinga/v1/firms"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_firms")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_firms", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_firms",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: benzinga
@mcp.tool()
async def list_guidance(
    positioning: str | None = Field(None, description="Filter guidance by presentation type: 'primary' for the company's emphasized figure or 'secondary' for supporting or alternate figures."),
    limit: int | None = Field(None, description="Maximum number of results to return, between 1 and 50,000. Defaults to 100 if not specified.", ge=1, le=50001),
    sort: str | None = Field(None, description="Comma-separated list of columns to sort by, with '.asc' or '.desc' appended to each column to specify direction. Defaults to sorting by date in descending order."),
) -> dict[str, Any] | ToolResult:
    """Retrieve financial guidance and earnings estimates for companies, including EPS and revenue projections across different fiscal periods."""

    # Construct request model with validation
    try:
        _request = _models.GetBenzingaV1GuidanceRequest(
            query=_models.GetBenzingaV1GuidanceRequestQuery(positioning=positioning, limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_guidance: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/benzinga/v1/guidance"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_guidance")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_guidance", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_guidance",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: benzinga
@mcp.tool()
async def list_analyst_ratings(
    rating_action_any_of: str | None = Field(None, alias="rating_action.any_of", description="Filter ratings by action type. Accepts one or more comma-separated values (e.g., 'upgrade,downgrade,initiate'). Use this to find specific types of rating changes."),
    rating_action_gt: str | None = Field(None, alias="rating_action.gt", description="Filter ratings by action type using greater-than comparison. Useful for alphabetical or numeric ordering of action types."),
    rating_action_gte: str | None = Field(None, alias="rating_action.gte", description="Filter ratings by action type using greater-than-or-equal comparison. Useful for alphabetical or numeric ordering of action types."),
    rating_action_lt: str | None = Field(None, alias="rating_action.lt", description="Filter ratings by action type using less-than comparison. Useful for alphabetical or numeric ordering of action types."),
    rating_action_lte: str | None = Field(None, alias="rating_action.lte", description="Filter ratings by action type using less-than-or-equal comparison. Useful for alphabetical or numeric ordering of action types."),
    price_target_action_any_of: str | None = Field(None, alias="price_target_action.any_of", description="Filter price target changes by action type. Accepts one or more comma-separated values (e.g., 'raised,lowered,initiated'). Use this to find specific types of price target adjustments."),
    price_target_action_gt: str | None = Field(None, alias="price_target_action.gt", description="Filter price target changes by action type using greater-than comparison. Useful for alphabetical or numeric ordering of action types."),
    price_target_action_gte: str | None = Field(None, alias="price_target_action.gte", description="Filter price target changes by action type using greater-than-or-equal comparison. Useful for alphabetical or numeric ordering of action types."),
    price_target_action_lt: str | None = Field(None, alias="price_target_action.lt", description="Filter price target changes by action type using less-than comparison. Useful for alphabetical or numeric ordering of action types."),
    price_target_action_lte: str | None = Field(None, alias="price_target_action.lte", description="Filter price target changes by action type using less-than-or-equal comparison. Useful for alphabetical or numeric ordering of action types."),
    benzinga_analyst_id_any_of: str | None = Field(None, alias="benzinga_analyst_id.any_of", description="Filter results by analyst identifier. Accepts one or more comma-separated analyst IDs to retrieve ratings from specific analysts."),
    benzinga_analyst_id_gt: str | None = Field(None, alias="benzinga_analyst_id.gt", description="Filter analysts by ID using greater-than comparison. Useful for numeric filtering of analyst identifiers."),
    benzinga_analyst_id_gte: str | None = Field(None, alias="benzinga_analyst_id.gte", description="Filter analysts by ID using greater-than-or-equal comparison. Useful for numeric filtering of analyst identifiers."),
    benzinga_analyst_id_lt: str | None = Field(None, alias="benzinga_analyst_id.lt", description="Filter analysts by ID using less-than comparison. Useful for numeric filtering of analyst identifiers."),
    benzinga_analyst_id_lte: str | None = Field(None, alias="benzinga_analyst_id.lte", description="Filter analysts by ID using less-than-or-equal comparison. Useful for numeric filtering of analyst identifiers."),
    limit: int | None = Field(None, description="Maximum number of results to return. Defaults to 100 if not specified. Maximum allowed value is 50,000.", ge=1, le=50001),
    sort: str | None = Field(None, description="Comma-separated list of columns to sort by, with sort direction appended to each column (e.g., 'last_updated.desc,rating_action.asc'). Defaults to 'last_updated.desc' if not specified. Append '.asc' for ascending or '.desc' for descending order."),
) -> dict[str, Any] | ToolResult:
    """Retrieve analyst ratings and price target data from investment firms, including rating changes (upgrades, downgrades, initiations) and price target adjustments for publicly traded companies. Results can be filtered by rating action, price target action, and analyst ID, with customizable sorting and pagination."""

    # Construct request model with validation
    try:
        _request = _models.GetBenzingaV1RatingsRequest(
            query=_models.GetBenzingaV1RatingsRequestQuery(rating_action_any_of=rating_action_any_of, rating_action_gt=rating_action_gt, rating_action_gte=rating_action_gte, rating_action_lt=rating_action_lt, rating_action_lte=rating_action_lte, price_target_action_any_of=price_target_action_any_of, price_target_action_gt=price_target_action_gt, price_target_action_gte=price_target_action_gte, price_target_action_lt=price_target_action_lt, price_target_action_lte=price_target_action_lte, benzinga_analyst_id_any_of=benzinga_analyst_id_any_of, benzinga_analyst_id_gt=benzinga_analyst_id_gt, benzinga_analyst_id_gte=benzinga_analyst_id_gte, benzinga_analyst_id_lt=benzinga_analyst_id_lt, benzinga_analyst_id_lte=benzinga_analyst_id_lte, limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_analyst_ratings: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/benzinga/v1/ratings"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_analyst_ratings")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_analyst_ratings", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_analyst_ratings",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: benzinga
@mcp.tool()
async def search_financial_news(
    published: str | None = Field(None, description="Filter articles by exact publication date. Accepts ISO 8601 timestamps, RFC 3339 format, or simple date strings (yyyy-mm-dd)."),
    published_gt: str | None = Field(None, alias="published.gt", description="Filter for articles published after this date. Accepts ISO 8601 timestamps, RFC 3339 format, or simple date strings (yyyy-mm-dd)."),
    published_gte: str | None = Field(None, alias="published.gte", description="Filter for articles published on or after this date. Accepts ISO 8601 timestamps, RFC 3339 format, or simple date strings (yyyy-mm-dd)."),
    published_lt: str | None = Field(None, alias="published.lt", description="Filter for articles published before this date. Accepts ISO 8601 timestamps, RFC 3339 format, or simple date strings (yyyy-mm-dd)."),
    published_lte: str | None = Field(None, alias="published.lte", description="Filter for articles published on or before this date. Accepts ISO 8601 timestamps, RFC 3339 format, or simple date strings (yyyy-mm-dd)."),
    channels_all_of: str | None = Field(None, alias="channels.all_of", description="Filter for articles that contain all specified channels. Provide multiple channels as a comma-separated list."),
    channels_any_of: str | None = Field(None, alias="channels.any_of", description="Filter for articles that contain any of the specified channels. Provide multiple channels as a comma-separated list."),
    tags_all_of: str | None = Field(None, alias="tags.all_of", description="Filter for articles that contain all specified tags. Provide multiple tags as a comma-separated list."),
    tags_any_of: str | None = Field(None, alias="tags.any_of", description="Filter for articles that contain any of the specified tags. Provide multiple tags as a comma-separated list."),
    author_any_of: str | None = Field(None, alias="author.any_of", description="Filter for articles by any of the specified authors. Provide multiple authors as a comma-separated list."),
    author_gt: str | None = Field(None, alias="author.gt", description="Filter for authors whose names come after this value alphabetically."),
    author_gte: str | None = Field(None, alias="author.gte", description="Filter for authors whose names come after or equal to this value alphabetically."),
    author_lt: str | None = Field(None, alias="author.lt", description="Filter for authors whose names come before this value alphabetically."),
    author_lte: str | None = Field(None, alias="author.lte", description="Filter for authors whose names come before or equal to this value alphabetically."),
    stocks_all_of: str | None = Field(None, alias="stocks.all_of", description="Filter for articles that mention all specified stock symbols. Provide multiple symbols as a comma-separated list."),
    stocks_any_of: str | None = Field(None, alias="stocks.any_of", description="Filter for articles that mention any of the specified stock symbols. Provide multiple symbols as a comma-separated list."),
    limit: int | None = Field(None, description="Maximum number of results to return. Defaults to 100 if not specified; maximum allowed is 50,000.", ge=1, le=50001),
    sort: str | None = Field(None, description="Sort results by one or more columns in ascending or descending order. Use comma-separated format with '.asc' or '.desc' suffix (e.g., 'published.desc,author.asc'). Defaults to 'published.desc' if not specified."),
) -> dict[str, Any] | ToolResult:
    """Search and retrieve financial news articles from Benzinga's comprehensive database, with filtering by publication date, channels, tags, authors, and related stocks."""

    # Construct request model with validation
    try:
        _request = _models.GetBenzingaV2NewsRequest(
            query=_models.GetBenzingaV2NewsRequestQuery(published=published, published_gt=published_gt, published_gte=published_gte, published_lt=published_lt, published_lte=published_lte, channels_all_of=channels_all_of, channels_any_of=channels_any_of, tags_all_of=tags_all_of, tags_any_of=tags_any_of, author_any_of=author_any_of, author_gt=author_gt, author_gte=author_gte, author_lt=author_lt, author_lte=author_lte, stocks_all_of=stocks_all_of, stocks_any_of=stocks_any_of, limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_financial_news: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/benzinga/v2/news"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_financial_news")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_financial_news", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_financial_news",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: fable
@mcp.tool()
async def list_merchant_aggregates_eu(
    transaction_date_gt: str | None = Field(None, alias="transaction_date.gt", description="Filter transactions occurring after this date (exclusive). Use ISO 8601 format (yyyy-mm-dd)."),
    transaction_date_gte: str | None = Field(None, alias="transaction_date.gte", description="Filter transactions occurring on or after this date (inclusive). Use ISO 8601 format (yyyy-mm-dd)."),
    transaction_date_lt: str | None = Field(None, alias="transaction_date.lt", description="Filter transactions occurring before this date (exclusive). Use ISO 8601 format (yyyy-mm-dd)."),
    transaction_date_lte: str | None = Field(None, alias="transaction_date.lte", description="Filter transactions occurring on or before this date (inclusive). Use ISO 8601 format (yyyy-mm-dd)."),
    name_any_of: str | None = Field(None, alias="name.any_of", description="Filter by merchant or payment processor name. Accepts multiple comma-separated values for matching any of the specified names."),
    user_country_any_of: Literal["UK", "DE", "FR", "ES", "IT", "AT", "unknown"] | None = Field(None, alias="user_country.any_of", description="Filter by consumer country. Accepts multiple comma-separated values from: UK, DE, FR, ES, IT, AT, or unknown."),
    channel_any_of: Literal["online", "offline", "bnpl"] | None = Field(None, alias="channel.any_of", description="Filter by transaction channel. Accepts multiple comma-separated values: online, offline, or bnpl (buy-now-pay-later)."),
    consumer_type_any_of: Literal["consumer_credit", "consumer_debit", "open_banking"] | None = Field(None, alias="consumer_type.any_of", description="Filter by consumer transaction type. Accepts multiple comma-separated values: consumer_credit (credit card), consumer_debit (debit card), or open_banking."),
    parent_name_any_of: str | None = Field(None, alias="parent_name.any_of", description="Filter by parent company name. Accepts multiple comma-separated values for matching any of the specified parent entities."),
    limit: int | None = Field(None, description="Maximum number of results to return. Must be between 1 and 5000; defaults to 100 if not specified.", ge=1, le=5001),
    sort: str | None = Field(None, description="Comma-separated list of columns to sort by, with .asc or .desc appended to each column name to specify direction. Defaults to transaction_date.desc if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve aggregated consumer spending data from European credit card and open banking panels, segmented by merchant, currency, country, and transaction channel. Data reflects daily transactions with a 7-day lag and includes user counts for custom normalization across 250+ US public companies."""

    # Construct request model with validation
    try:
        _request = _models.GetConsumerSpendingEuV1MerchantAggregatesRequest(
            query=_models.GetConsumerSpendingEuV1MerchantAggregatesRequestQuery(transaction_date_gt=transaction_date_gt, transaction_date_gte=transaction_date_gte, transaction_date_lt=transaction_date_lt, transaction_date_lte=transaction_date_lte, name_any_of=name_any_of, user_country_any_of=user_country_any_of, channel_any_of=channel_any_of, consumer_type_any_of=consumer_type_any_of, parent_name_any_of=parent_name_any_of, limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_merchant_aggregates_eu: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/consumer-spending/eu/v1/merchant-aggregates"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_merchant_aggregates_eu")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_merchant_aggregates_eu", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_merchant_aggregates_eu",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: fable
@mcp.tool()
async def list_merchant_hierarchy(
    lookup_name_any_of: str | None = Field(None, alias="lookup_name.any_of", description="Filter merchants by exact name match or multiple names using comma-separated values."),
    lookup_name_gt: str | None = Field(None, alias="lookup_name.gt", description="Filter merchants by name lexicographically greater than the specified value."),
    lookup_name_gte: str | None = Field(None, alias="lookup_name.gte", description="Filter merchants by name lexicographically greater than or equal to the specified value."),
    lookup_name_lt: str | None = Field(None, alias="lookup_name.lt", description="Filter merchants by name lexicographically less than the specified value."),
    lookup_name_lte: str | None = Field(None, alias="lookup_name.lte", description="Filter merchants by name lexicographically less than or equal to the specified value."),
    listing_status_any_of: Literal["public", "private"] | None = Field(None, alias="listing_status.any_of", description="Filter by parent company listing status: 'public' for publicly traded companies or 'private' for private companies. Specify multiple values as comma-separated list."),
    active_from_gt: str | None = Field(None, alias="active_from.gt", description="Filter merchants with active_from date strictly after the specified date (format: yyyy-mm-dd)."),
    active_from_gte: str | None = Field(None, alias="active_from.gte", description="Filter merchants with active_from date on or after the specified date (format: yyyy-mm-dd)."),
    active_from_lt: str | None = Field(None, alias="active_from.lt", description="Filter merchants with active_from date strictly before the specified date (format: yyyy-mm-dd)."),
    active_from_lte: str | None = Field(None, alias="active_from.lte", description="Filter merchants with active_from date on or before the specified date (format: yyyy-mm-dd)."),
    active_to_gt: str | None = Field(None, alias="active_to.gt", description="Filter merchants with active_to date strictly after the specified date (format: yyyy-mm-dd)."),
    active_to_gte: str | None = Field(None, alias="active_to.gte", description="Filter merchants with active_to date on or after the specified date (format: yyyy-mm-dd). Use this to find merchants active on a specific transaction date."),
    active_to_lt: str | None = Field(None, alias="active_to.lt", description="Filter merchants with active_to date strictly before the specified date (format: yyyy-mm-dd)."),
    active_to_lte: str | None = Field(None, alias="active_to.lte", description="Filter merchants with active_to date on or before the specified date (format: yyyy-mm-dd)."),
    limit: int | None = Field(None, description="Maximum number of results to return. Defaults to 100 if not specified; maximum allowed is 50,000.", ge=1, le=50001),
    sort: str | None = Field(None, description="Sort results by one or more columns in ascending or descending order using comma-separated format (e.g., 'lookup_name.asc,active_from.desc'). Defaults to 'lookup_name.asc' if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve merchant reference data with corporate hierarchy, ticker symbols, sectors, and industries for European consumer transactions. Use this to enrich transaction data by joining on merchant name and filtering by active date ranges to match specific transaction dates."""

    # Construct request model with validation
    try:
        _request = _models.GetConsumerSpendingEuV1MerchantHierarchyRequest(
            query=_models.GetConsumerSpendingEuV1MerchantHierarchyRequestQuery(lookup_name_any_of=lookup_name_any_of, lookup_name_gt=lookup_name_gt, lookup_name_gte=lookup_name_gte, lookup_name_lt=lookup_name_lt, lookup_name_lte=lookup_name_lte, listing_status_any_of=listing_status_any_of, active_from_gt=active_from_gt, active_from_gte=active_from_gte, active_from_lt=active_from_lt, active_from_lte=active_from_lte, active_to_gt=active_to_gt, active_to_gte=active_to_gte, active_to_lt=active_to_lt, active_to_lte=active_to_lte, limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_merchant_hierarchy: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/consumer-spending/eu/v1/merchant-hierarchy"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_merchant_hierarchy")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_merchant_hierarchy", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_merchant_hierarchy",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: etfglobal
@mcp.tool()
async def list_etf_analytics(
    risk_total_score_gt: float | None = Field(None, alias="risk_total_score.gt", description="Filter ETFs with total risk score greater than this value (floating point number)."),
    risk_total_score_gte: float | None = Field(None, alias="risk_total_score.gte", description="Filter ETFs with total risk score greater than or equal to this value (floating point number)."),
    risk_total_score_lt: float | None = Field(None, alias="risk_total_score.lt", description="Filter ETFs with total risk score less than this value (floating point number)."),
    risk_total_score_lte: float | None = Field(None, alias="risk_total_score.lte", description="Filter ETFs with total risk score less than or equal to this value (floating point number)."),
    reward_score_gt: float | None = Field(None, alias="reward_score.gt", description="Filter ETFs with reward score greater than this value (floating point number)."),
    reward_score_gte: float | None = Field(None, alias="reward_score.gte", description="Filter ETFs with reward score greater than or equal to this value (floating point number)."),
    reward_score_lt: float | None = Field(None, alias="reward_score.lt", description="Filter ETFs with reward score less than this value (floating point number)."),
    reward_score_lte: float | None = Field(None, alias="reward_score.lte", description="Filter ETFs with reward score less than or equal to this value (floating point number)."),
    quant_total_score_gt: float | None = Field(None, alias="quant_total_score.gt", description="Filter ETFs with quantitative total score greater than this value (floating point number)."),
    quant_total_score_gte: float | None = Field(None, alias="quant_total_score.gte", description="Filter ETFs with quantitative total score greater than or equal to this value (floating point number)."),
    quant_total_score_lt: float | None = Field(None, alias="quant_total_score.lt", description="Filter ETFs with quantitative total score less than this value (floating point number)."),
    quant_total_score_lte: float | None = Field(None, alias="quant_total_score.lte", description="Filter ETFs with quantitative total score less than or equal to this value (floating point number)."),
    quant_grade_any_of: str | None = Field(None, alias="quant_grade.any_of", description="Filter ETFs by quantitative grade using one or more values (comma-separated list for multiple grades)."),
    quant_grade_gt: str | None = Field(None, alias="quant_grade.gt", description="Filter ETFs with quantitative grade greater than this value (alphabetically ordered)."),
    quant_grade_gte: str | None = Field(None, alias="quant_grade.gte", description="Filter ETFs with quantitative grade greater than or equal to this value (alphabetically ordered)."),
    quant_grade_lt: str | None = Field(None, alias="quant_grade.lt", description="Filter ETFs with quantitative grade less than this value (alphabetically ordered)."),
    quant_grade_lte: str | None = Field(None, alias="quant_grade.lte", description="Filter ETFs with quantitative grade less than or equal to this value (alphabetically ordered)."),
    quant_composite_technical_gt: float | None = Field(None, alias="quant_composite_technical.gt", description="Filter ETFs with composite technical score greater than this value (floating point number)."),
    quant_composite_technical_gte: float | None = Field(None, alias="quant_composite_technical.gte", description="Filter ETFs with composite technical score greater than or equal to this value (floating point number)."),
    quant_composite_technical_lt: float | None = Field(None, alias="quant_composite_technical.lt", description="Filter ETFs with composite technical score less than this value (floating point number)."),
    quant_composite_technical_lte: float | None = Field(None, alias="quant_composite_technical.lte", description="Filter ETFs with composite technical score less than or equal to this value (floating point number)."),
    quant_composite_sentiment_gt: float | None = Field(None, alias="quant_composite_sentiment.gt", description="Filter ETFs with composite sentiment score greater than this value (floating point number)."),
    quant_composite_sentiment_gte: float | None = Field(None, alias="quant_composite_sentiment.gte", description="Filter ETFs with composite sentiment score greater than or equal to this value (floating point number)."),
    quant_composite_sentiment_lt: float | None = Field(None, alias="quant_composite_sentiment.lt", description="Filter ETFs with composite sentiment score less than this value (floating point number)."),
    quant_composite_sentiment_lte: float | None = Field(None, alias="quant_composite_sentiment.lte", description="Filter ETFs with composite sentiment score less than or equal to this value (floating point number)."),
    quant_composite_behavioral_gt: float | None = Field(None, alias="quant_composite_behavioral.gt", description="Filter ETFs with composite behavioral score greater than this value (floating point number)."),
    quant_composite_behavioral_gte: float | None = Field(None, alias="quant_composite_behavioral.gte", description="Filter ETFs with composite behavioral score greater than or equal to this value (floating point number)."),
    quant_composite_behavioral_lt: float | None = Field(None, alias="quant_composite_behavioral.lt", description="Filter ETFs with composite behavioral score less than this value (floating point number)."),
    quant_composite_behavioral_lte: float | None = Field(None, alias="quant_composite_behavioral.lte", description="Filter ETFs with composite behavioral score less than or equal to this value (floating point number)."),
    quant_composite_fundamental_gt: float | None = Field(None, alias="quant_composite_fundamental.gt", description="Filter ETFs with composite fundamental score greater than this value (floating point number)."),
    quant_composite_fundamental_gte: float | None = Field(None, alias="quant_composite_fundamental.gte", description="Filter ETFs with composite fundamental score greater than or equal to this value (floating point number)."),
    quant_composite_fundamental_lt: float | None = Field(None, alias="quant_composite_fundamental.lt", description="Filter ETFs with composite fundamental score less than this value (floating point number)."),
    quant_composite_fundamental_lte: float | None = Field(None, alias="quant_composite_fundamental.lte", description="Filter ETFs with composite fundamental score less than or equal to this value (floating point number)."),
    quant_composite_global_gt: float | None = Field(None, alias="quant_composite_global.gt", description="Filter ETFs with composite global score greater than this value (floating point number)."),
    quant_composite_global_gte: float | None = Field(None, alias="quant_composite_global.gte", description="Filter ETFs with composite global score greater than or equal to this value (floating point number)."),
    quant_composite_global_lt: float | None = Field(None, alias="quant_composite_global.lt", description="Filter ETFs with composite global score less than this value (floating point number)."),
    quant_composite_global_lte: float | None = Field(None, alias="quant_composite_global.lte", description="Filter ETFs with composite global score less than or equal to this value (floating point number)."),
    quant_composite_quality_gt: float | None = Field(None, alias="quant_composite_quality.gt", description="Filter ETFs with composite quality score greater than this value (floating point number)."),
    quant_composite_quality_gte: float | None = Field(None, alias="quant_composite_quality.gte", description="Filter ETFs with composite quality score greater than or equal to this value (floating point number)."),
    quant_composite_quality_lt: float | None = Field(None, alias="quant_composite_quality.lt", description="Filter ETFs with composite quality score less than this value (floating point number)."),
    quant_composite_quality_lte: float | None = Field(None, alias="quant_composite_quality.lte", description="Filter ETFs with composite quality score less than or equal to this value (floating point number)."),
    limit: int | None = Field(None, description="Maximum number of results to return (1 to 5000, defaults to 100 if not specified).", ge=1, le=5001),
    sort: str | None = Field(None, description="Comma-separated list of columns to sort by, with '.asc' or '.desc' appended to each column to specify direction. Defaults to sorting by composite_ticker in ascending order."),
) -> dict[str, Any] | ToolResult:
    """Retrieve ETF Global analytics data with risk scores, reward metrics, and quantitative analysis across multiple dimensions. Filter and sort results by performance indicators, risk profiles, and composite grades."""

    # Construct request model with validation
    try:
        _request = _models.GetEtfGlobalV1AnalyticsRequest(
            query=_models.GetEtfGlobalV1AnalyticsRequestQuery(risk_total_score_gt=risk_total_score_gt, risk_total_score_gte=risk_total_score_gte, risk_total_score_lt=risk_total_score_lt, risk_total_score_lte=risk_total_score_lte, reward_score_gt=reward_score_gt, reward_score_gte=reward_score_gte, reward_score_lt=reward_score_lt, reward_score_lte=reward_score_lte, quant_total_score_gt=quant_total_score_gt, quant_total_score_gte=quant_total_score_gte, quant_total_score_lt=quant_total_score_lt, quant_total_score_lte=quant_total_score_lte, quant_grade_any_of=quant_grade_any_of, quant_grade_gt=quant_grade_gt, quant_grade_gte=quant_grade_gte, quant_grade_lt=quant_grade_lt, quant_grade_lte=quant_grade_lte, quant_composite_technical_gt=quant_composite_technical_gt, quant_composite_technical_gte=quant_composite_technical_gte, quant_composite_technical_lt=quant_composite_technical_lt, quant_composite_technical_lte=quant_composite_technical_lte, quant_composite_sentiment_gt=quant_composite_sentiment_gt, quant_composite_sentiment_gte=quant_composite_sentiment_gte, quant_composite_sentiment_lt=quant_composite_sentiment_lt, quant_composite_sentiment_lte=quant_composite_sentiment_lte, quant_composite_behavioral_gt=quant_composite_behavioral_gt, quant_composite_behavioral_gte=quant_composite_behavioral_gte, quant_composite_behavioral_lt=quant_composite_behavioral_lt, quant_composite_behavioral_lte=quant_composite_behavioral_lte, quant_composite_fundamental_gt=quant_composite_fundamental_gt, quant_composite_fundamental_gte=quant_composite_fundamental_gte, quant_composite_fundamental_lt=quant_composite_fundamental_lt, quant_composite_fundamental_lte=quant_composite_fundamental_lte, quant_composite_global_gt=quant_composite_global_gt, quant_composite_global_gte=quant_composite_global_gte, quant_composite_global_lt=quant_composite_global_lt, quant_composite_global_lte=quant_composite_global_lte, quant_composite_quality_gt=quant_composite_quality_gt, quant_composite_quality_gte=quant_composite_quality_gte, quant_composite_quality_lt=quant_composite_quality_lt, quant_composite_quality_lte=quant_composite_quality_lte, limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_etf_analytics: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/etf-global/v1/analytics"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_etf_analytics")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_etf_analytics", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_etf_analytics",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: etfglobal
@mcp.tool()
async def list_etf_constituents(
    limit: int | None = Field(None, description="Maximum number of constituent records to return per request, ranging from 1 to 5000. Defaults to 100 if not specified.", ge=1, le=5001),
    sort: str | None = Field(None, description="Comma-separated list of fields to sort results by, with each field suffixed by '.asc' or '.desc' to specify ascending or descending order. Defaults to sorting by composite_ticker in ascending order if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about securities held within ETFs, including their weights, market values, and identifiers. Results can be paginated and sorted by any constituent field."""

    # Construct request model with validation
    try:
        _request = _models.GetEtfGlobalV1ConstituentsRequest(
            query=_models.GetEtfGlobalV1ConstituentsRequestQuery(limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_etf_constituents: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/etf-global/v1/constituents"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_etf_constituents")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_etf_constituents", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_etf_constituents",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: etfglobal
@mcp.tool()
async def list_etf_fund_flows(
    limit: int | None = Field(None, description="Maximum number of results to return per request, ranging from 1 to 5000. Defaults to 100 if not specified.", ge=1, le=5001),
    sort: str | None = Field(None, description="Comma-separated list of columns to sort by, with each column followed by '.asc' or '.desc' to specify ascending or descending order. Defaults to sorting by composite_ticker in ascending order if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve ETF Global fund flow data including share movements, net asset values, and flow metrics across ETFs. Results can be paginated and sorted by multiple columns."""

    # Construct request model with validation
    try:
        _request = _models.GetEtfGlobalV1FundFlowsRequest(
            query=_models.GetEtfGlobalV1FundFlowsRequestQuery(limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_etf_fund_flows: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/etf-global/v1/fund-flows"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_etf_fund_flows")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_etf_fund_flows", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_etf_fund_flows",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: etfglobal
@mcp.tool()
async def list_etf_profiles(
    limit: int | None = Field(None, description="Maximum number of ETF profiles to return in a single response. Must be between 1 and 5000, defaults to 100 if not specified.", ge=1, le=5001),
    sort: str | None = Field(None, description="Comma-separated list of fields to sort results by, with each field followed by '.asc' or '.desc' to specify ascending or descending order. Defaults to sorting by composite_ticker in ascending order if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve comprehensive ETF Global industry profile data including financial metrics, operational details, and exposure information. Results can be paginated and sorted by any profile field."""

    # Construct request model with validation
    try:
        _request = _models.GetEtfGlobalV1ProfilesRequest(
            query=_models.GetEtfGlobalV1ProfilesRequestQuery(limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_etf_profiles: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/etf-global/v1/profiles"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_etf_profiles")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_etf_profiles", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_etf_profiles",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: etfglobal
@mcp.tool()
async def list_etf_taxonomies(
    limit: int | None = Field(None, description="Maximum number of taxonomy records to return in the response. Defaults to 100 if not specified. Must be between 1 and 5000.", ge=1, le=5001),
    sort: str | None = Field(None, description="Comma-separated list of columns to sort results by, with each column followed by '.asc' or '.desc' to specify ascending or descending order. Defaults to sorting by 'composite_ticker' in ascending order if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve ETF Global taxonomy data containing detailed classification and categorization information for ETFs, including investment strategy, methodology, and structural characteristics."""

    # Construct request model with validation
    try:
        _request = _models.GetEtfGlobalV1TaxonomiesRequest(
            query=_models.GetEtfGlobalV1TaxonomiesRequestQuery(limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_etf_taxonomies: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/etf-global/v1/taxonomies"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_etf_taxonomies")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_etf_taxonomies", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_etf_taxonomies",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: fed
@mcp.tool()
async def list_inflation_metrics(
    limit: int | None = Field(None, description="Maximum number of results to return in a single response. Accepts values from 1 to 50,000, with a default of 100 results if not specified.", ge=1, le=50001),
    sort: str | None = Field(None, description="Comma-separated list of columns to sort results by, with sort direction specified per column using '.asc' or '.desc' suffix. Defaults to sorting by date in ascending order if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve historical inflation and price index data, including Consumer Price Index (CPI) and Personal Consumption Expenditures (PCE) metrics. Results can be sorted and paginated for flexible data access."""

    # Construct request model with validation
    try:
        _request = _models.GetFedV1InflationRequest(
            query=_models.GetFedV1InflationRequestQuery(limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_inflation_metrics: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/fed/v1/inflation"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_inflation_metrics")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_inflation_metrics", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_inflation_metrics",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: fed
@mcp.tool()
async def list_inflation_expectations(
    limit: int | None = Field(None, description="Maximum number of results to return in a single response, ranging from 1 to 50,000. Defaults to 100 if not specified.", ge=1, le=50001),
    sort: str | None = Field(None, description="Comma-separated list of columns to sort by, with each column followed by '.asc' or '.desc' to specify ascending or descending order. Defaults to sorting by date in ascending order if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve inflation expectations data from both market-based and economic model perspectives across multiple time horizons. Results can be paginated and sorted by any available column."""

    # Construct request model with validation
    try:
        _request = _models.GetFedV1InflationExpectationsRequest(
            query=_models.GetFedV1InflationExpectationsRequestQuery(limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_inflation_expectations: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/fed/v1/inflation-expectations"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_inflation_expectations")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_inflation_expectations", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_inflation_expectations",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: fed
@mcp.tool()
async def list_labor_market_indicators(
    limit: int | None = Field(None, description="Maximum number of results to return in a single response, ranging from 1 to 50,000. Defaults to 100 if not specified.", ge=1, le=50001),
    sort: str | None = Field(None, description="Comma-separated list of columns to sort by, with each column followed by '.asc' or '.desc' to specify ascending or descending order. Defaults to sorting by date in ascending order if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve Federal Reserve labor market indicators including unemployment rate, labor force participation, average hourly earnings, and job openings data. Results are paginated and sortable by date or other available fields."""

    # Construct request model with validation
    try:
        _request = _models.GetFedV1LaborMarketRequest(
            query=_models.GetFedV1LaborMarketRequestQuery(limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_labor_market_indicators: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/fed/v1/labor-market"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_labor_market_indicators")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_labor_market_indicators", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_labor_market_indicators",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: fed
@mcp.tool()
async def list_treasury_yields(
    limit: int | None = Field(None, description="Maximum number of results to return in a single response. Accepts values from 1 to 50,000, with a default of 100 results if not specified.", ge=1, le=50001),
    sort: str | None = Field(None, description="Comma-separated list of columns to sort results by, with sort direction specified per column using '.asc' or '.desc' suffix. Defaults to sorting by date in ascending order if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve historical U.S. Treasury bond yields across various maturity periods, providing a comprehensive view of government securities interest rates from short-term to long-term instruments."""

    # Construct request model with validation
    try:
        _request = _models.GetFedV1TreasuryYieldsRequest(
            query=_models.GetFedV1TreasuryYieldsRequestQuery(limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_treasury_yields: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/fed/v1/treasury-yields"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_treasury_yields")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_treasury_yields", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_treasury_yields",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: futures:aggregates
@mcp.tool()
async def get_futures_aggregates(
    ticker: str = Field(..., description="The futures contract identifier including base symbol and expiration month/year (e.g., GCJ5 for April 2025 gold futures)."),
    resolution: str | None = Field(None, description="The candle size as a number with unit: seconds (sec), minutes (min), hours (hour), trading sessions (session), weeks (week), months (month), quarters (quarter), or years (year). Each unit has a maximum multiplier (e.g., up to 59min before switching to hours). Defaults to one trading session."),
    window_start: str | None = Field(None, description="Filter candles by start time using a date (YYYY-MM-DD format) or nanosecond Unix timestamp. Supports comparison operators: gte (greater than or equal), gt (greater than), lte (less than or equal), lt (less than) for range queries. When omitted, returns the most recent candles up to the specified limit."),
    limit: int | None = Field(None, description="Maximum number of results to return per page. Must be between 1 and 50,000, defaults to 1,000.", ge=1, le=50000),
    sort: Literal["window_start.asc", "window_start.desc"] | None = Field(None, description="Sort results by window_start in ascending or descending order. Defaults to descending (most recent first)."),
) -> dict[str, Any] | ToolResult:
    """Retrieve OHLCV aggregates (candles) for a futures contract over a specified time range. Supports flexible time windows and multiple resolution granularities from seconds to years."""

    # Construct request model with validation
    try:
        _request = _models.AggregatesV1Request(
            path=_models.AggregatesV1RequestPath(ticker=ticker),
            query=_models.AggregatesV1RequestQuery(resolution=resolution, window_start=window_start, limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_futures_aggregates: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/futures/v1/aggs/{ticker}", _request.path.model_dump(by_alias=True)) if _request.path else "/futures/v1/aggs/{ticker}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_futures_aggregates")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_futures_aggregates", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_futures_aggregates",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: futures:aggregates
@mcp.tool()
async def get_futures_aggregates_vx(
    ticker: str = Field(..., description="The futures contract identifier including base symbol and expiration month/year (e.g., GCJ5 for April 2025 gold futures)."),
    resolution: str | None = Field(None, description="The candle interval size as a number with unit: seconds (sec), minutes (min), hours (hour), trading sessions (session), weeks (week), months (month), quarters (quarter), or years (year). Each unit has a maximum multiplier (e.g., up to 59min before switching to hours). Defaults to one trading session."),
    window_start: str | None = Field(None, description="Filter candles by start time using a date (YYYY-MM-DD format) or nanosecond Unix timestamp. Use comparison operators (gte, gt, lte, lt) to define ranges. When omitted, returns the most recent candles up to the specified limit."),
    limit: int | None = Field(None, description="Maximum number of candles to return per request, between 1 and 50,000. Defaults to 1,000 results.", ge=1, le=50000),
    sort: Literal["window_start.asc", "window_start.desc"] | None = Field(None, description="Sort results by window_start timestamp in ascending or descending order. Defaults to descending (most recent first)."),
) -> dict[str, Any] | ToolResult:
    """Retrieve OHLCV candle data for a futures contract over a specified time range. Supports flexible time windows and multiple resolution granularities from seconds to years."""

    # Construct request model with validation
    try:
        _request = _models.AggregatesRequest(
            path=_models.AggregatesRequestPath(ticker=ticker),
            query=_models.AggregatesRequestQuery(resolution=resolution, window_start=window_start, limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_futures_aggregates_vx: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/futures/vX/aggs/{ticker}", _request.path.model_dump(by_alias=True)) if _request.path else "/futures/vX/aggs/{ticker}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_futures_aggregates_vx")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_futures_aggregates_vx", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_futures_aggregates_vx",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: us_futures
@mcp.tool()
async def list_futures_contracts(
    active: bool | None = Field(None, description="Filter results to only include contracts that were actively tradeable on the specified date. A contract is active when its first trade date is on or before the query date and its last trade date is on or after the query date."),
    limit: int | None = Field(None, description="Maximum number of results to return per request, ranging from 1 to 1000. Defaults to 100 if not specified.", ge=1, le=1001),
    sort: str | None = Field(None, description="Comma-separated list of columns to sort by, with each column followed by '.asc' or '.desc' to specify direction. Defaults to sorting by product_code in ascending order if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of futures contracts with optional filtering by active status and custom sorting. Use this to discover all listed contracts, access complete contract specifications, or perform point-in-time lookups of contract definitions."""

    # Construct request model with validation
    try:
        _request = _models.GetFuturesVXContractsRequest(
            query=_models.GetFuturesVXContractsRequestQuery(active=active, limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_futures_contracts: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/futures/vX/contracts"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_futures_contracts")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_futures_contracts", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_futures_contracts",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: us_futures
@mcp.tool()
async def list_futures_exchanges(limit: int | None = Field(None, description="Maximum number of results to return in the response. Accepts values between 1 and 1,000, with a default of 100 if not specified.", ge=1, le=1000)) -> dict[str, Any] | ToolResult:
    """Retrieve a list of US futures exchanges and trading venues, including major derivatives exchanges (CME, CBOT, NYMEX, COMEX) and other futures market infrastructure for commodity, financial, and derivative contract trading."""

    # Construct request model with validation
    try:
        _request = _models.GetFuturesVXExchangesRequest(
            query=_models.GetFuturesVXExchangesRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_futures_exchanges: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/futures/vX/exchanges"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_futures_exchanges")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_futures_exchanges", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_futures_exchanges",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: us_futures
@mcp.tool()
async def list_futures_market_statuses(limit: int | None = Field(None, description="Maximum number of market status records to return in the response. Must be between 1 and 100, defaults to 10 if not specified.", ge=1, le=100)) -> dict[str, Any] | ToolResult:
    """Retrieve the current market status for futures products, including real-time operational indicators (open, pause, close) with exchange and product codes. Use this to monitor market conditions and adjust trading strategies in real-time."""

    # Construct request model with validation
    try:
        _request = _models.GetFuturesVXMarketStatusRequest(
            query=_models.GetFuturesVXMarketStatusRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_futures_market_statuses: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/futures/vX/market-status"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_futures_market_statuses")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_futures_market_statuses", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_futures_market_statuses",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: us_futures
@mcp.tool()
async def list_futures_products(
    name_any_of: str | None = Field(None, alias="name.any_of", description="Filter products by name. Accepts multiple comma-separated values to match any of the specified product names."),
    sector_any_of: Literal["asia", "base", "biofuels", "coal", "cross_rates", "crude_oil", "custom_index", "dairy", "dj_ubs_ci", "electricity", "emissions", "europe", "fertilizer", "forestry", "grains_and_oilseeds", "intl_index", "liq_nat_gas_lng", "livestock", "long_term_gov", "long_term_non_gov", "majors", "minors", "nat_gas", "nat_gas_liq_petro", "precious", "refined_products", "s_and_p_gsci", "sel_sector_index", "short_term_gov", "short_term_non_gov", "softs", "us", "us_index", "wet_bulk"] | None = Field(None, alias="sector.any_of", description="Filter products by sector classification. Accepts multiple comma-separated values from predefined sectors including commodities (crude oil, natural gas, metals, grains), financials (indices, interest rates, currencies), and specialized categories (emissions, forestry, weather)."),
    sub_sector_any_of: Literal["asian", "canadian", "cat", "cooling_degree_days", "ercot", "european", "gulf", "heating_degree_days", "iso_ne", "large_cap_index", "mid_cap_index", "miso", "north_american", "nyiso", "pjm", "small_cap_index", "west", "western_power"] | None = Field(None, alias="sub_sector.any_of", description="Filter products by sub-sector classification. Accepts multiple comma-separated values for granular categorization such as geographic regions (Asian, European, North American), grid operators (ERCOT, MISO, PJM), or index sizes (large-cap, mid-cap, small-cap)."),
    asset_class_any_of: Literal["alt_investment", "commodity", "financials"] | None = Field(None, alias="asset_class.any_of", description="Filter products by asset class. Accepts multiple comma-separated values: commodities, financials, or alternative investments."),
    asset_sub_class_any_of: Literal["agricultural", "commodity_index", "energy", "equity", "foreign_exchange", "freight", "housing", "interest_rate", "metals", "weather"] | None = Field(None, alias="asset_sub_class.any_of", description="Filter products by asset sub-class. Accepts multiple comma-separated values including agricultural, energy, metals, equity, foreign exchange, interest rates, freight, housing, commodity indices, and weather."),
    limit: int | None = Field(None, description="Limit the number of results returned. Must be between 1 and 50,000; defaults to 100 if not specified.", ge=1, le=50001),
    sort: str | None = Field(None, description="Sort results by one or more columns in ascending or descending order. Specify columns as comma-separated values with '.asc' or '.desc' suffix (e.g., 'name.asc,date.desc'). Defaults to 'date.asc' if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve the complete universe of supported futures products with full specifications including codes, names, exchange identifiers, classifications, settlement methods, and pricing details. Filter by product attributes or retrieve specifications for a single product to support trading system integration, risk management, and historical reconciliation."""

    # Construct request model with validation
    try:
        _request = _models.GetFuturesVXProductsRequest(
            query=_models.GetFuturesVXProductsRequestQuery(name_any_of=name_any_of, sector_any_of=sector_any_of, sub_sector_any_of=sub_sector_any_of, asset_class_any_of=asset_class_any_of, asset_sub_class_any_of=asset_sub_class_any_of, limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_futures_products: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/futures/vX/products"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_futures_products")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_futures_products", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_futures_products",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: us_futures
@mcp.tool()
async def get_futures_quotes(
    ticker: str = Field(..., description="The futures contract identifier combining the base symbol and expiration month/year (e.g., GCJ5 for April 2025 gold futures)."),
    limit: int | None = Field(None, description="Maximum number of quote records to return, ranging from 1 to 50,000. Defaults to 100 if not specified.", ge=1, le=50000),
    sort: str | None = Field(None, description="Comma-separated list of columns to sort by, with each column suffixed by '.asc' or '.desc' to specify direction. Defaults to sorting by timestamp in descending order."),
) -> dict[str, Any] | ToolResult:
    """Retrieve real-time quote data for a specified futures contract, including best bid/offer prices, sizes, and timestamps to analyze price dynamics and liquidity conditions."""

    # Construct request model with validation
    try:
        _request = _models.GetFuturesVXQuotesRequest(
            path=_models.GetFuturesVXQuotesRequestPath(ticker=ticker),
            query=_models.GetFuturesVXQuotesRequestQuery(limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_futures_quotes: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/futures/vX/quotes/{ticker}", _request.path.model_dump(by_alias=True)) if _request.path else "/futures/vX/quotes/{ticker}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_futures_quotes")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_futures_quotes", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_futures_quotes",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: us_futures
@mcp.tool()
async def list_futures_schedules(
    session_end_date_gt: str | None = Field(None, alias="session_end_date.gt", description="Filter schedules to those with session end dates strictly after this date (formatted as yyyy-mm-dd). Use this to find schedules starting from a specific point in time."),
    session_end_date_gte: str | None = Field(None, alias="session_end_date.gte", description="Filter schedules to those with session end dates on or after this date (formatted as yyyy-mm-dd). Use this to include schedules from a specific date forward."),
    session_end_date_lt: str | None = Field(None, alias="session_end_date.lt", description="Filter schedules to those with session end dates strictly before this date (formatted as yyyy-mm-dd). Use this to find schedules up to a specific point in time."),
    session_end_date_lte: str | None = Field(None, alias="session_end_date.lte", description="Filter schedules to those with session end dates on or before this date (formatted as yyyy-mm-dd). Use this to include schedules up through a specific date."),
    limit: int | None = Field(None, description="Maximum number of results to return in the response. Defaults to 10 if not specified; maximum allowed is 1000.", ge=1, le=1001),
    sort: str | None = Field(None, description="Comma-separated list of columns to sort by, with each column followed by '.asc' or '.desc' to specify direction (e.g., 'product_code.asc,session_end_date.desc'). Defaults to sorting by product_code in ascending order."),
) -> dict[str, Any] | ToolResult:
    """Retrieve trading schedules for futures markets with session open/close times, intraday breaks, and holiday adjustments. All times are returned in UTC to support cross-system alignment for trading, execution, and operations workflows."""

    # Construct request model with validation
    try:
        _request = _models.GetFuturesVXSchedulesRequest(
            query=_models.GetFuturesVXSchedulesRequestQuery(session_end_date_gt=session_end_date_gt, session_end_date_gte=session_end_date_gte, session_end_date_lt=session_end_date_lt, session_end_date_lte=session_end_date_lte, limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_futures_schedules: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/futures/vX/schedules"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_futures_schedules")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_futures_schedules", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_futures_schedules",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: us_futures
@mcp.tool()
async def list_futures_snapshots(
    limit: int | None = Field(None, description="Maximum number of results to return in the response. Must be between 1 and 50,000, defaults to 100 if not specified.", ge=1, le=50001),
    sort: str | None = Field(None, description="Comma-separated list of columns to sort by, with each column followed by '.asc' or '.desc' to specify direction. Defaults to sorting by 'ticker' in ascending order if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a snapshot of the most recent futures contract data with optional pagination and sorting capabilities."""

    # Construct request model with validation
    try:
        _request = _models.GetFuturesVXSnapshotRequest(
            query=_models.GetFuturesVXSnapshotRequestQuery(limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_futures_snapshots: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/futures/vX/snapshot"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_futures_snapshots")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_futures_snapshots", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_futures_snapshots",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: us_futures
@mcp.tool()
async def list_futures_trades(
    ticker: str = Field(..., description="The futures contract identifier, including the base symbol and contract expiration month/year (e.g., GCJ5 for April 2025 gold contract)."),
    limit: int | None = Field(None, description="Maximum number of trade records to return in the response. Defaults to 10 if not specified; maximum allowed is 49,999 records per request.", ge=1, le=50000),
    sort: str | None = Field(None, description="Comma-separated list of columns to sort by, with each column followed by '.asc' or '.desc' to specify direction. Defaults to sorting by timestamp in descending order (most recent first) if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve tick-level trade data for a specified futures contract over a defined time range. Each record captures individual trade events with price, size, session date, and precise timestamps, enabling detailed intraday analysis, backtesting, and algorithmic strategy development."""

    # Construct request model with validation
    try:
        _request = _models.GetFuturesVXTradesRequest(
            path=_models.GetFuturesVXTradesRequestPath(ticker=ticker),
            query=_models.GetFuturesVXTradesRequestQuery(limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_futures_trades: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/futures/vX/trades/{ticker}", _request.path.model_dump(by_alias=True)) if _request.path else "/futures/vX/trades/{ticker}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_futures_trades")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_futures_trades", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_futures_trades",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: reference
@mcp.tool()
async def list_stock_filings_10_k_sections(
    section: Literal["business", "risk_factors"] | None = Field(None, description="Filter results by standardized section type. Valid options are 'business' (company operations and segments) or 'risk_factors' (identified business risks). Omit to retrieve all available sections."),
    limit: int | None = Field(None, description="Maximum number of filing sections to return in the response. Must be between 1 and 100, defaults to 10 if not specified.", ge=1, le=100),
    sort: str | None = Field(None, description="Sort results by one or more columns using comma-separated format, with each column followed by '.asc' or '.desc' to specify ascending or descending order. Defaults to sorting by 'period_end' in descending order (most recent first) if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve raw text content from specific sections of SEC 10-K filings. Returns standardized section excerpts from corporate annual reports, useful for extracting business descriptions, risk disclosures, and other regulatory content."""

    # Construct request model with validation
    try:
        _request = _models.GetStocksFilings10KVXSectionsRequest(
            query=_models.GetStocksFilings10KVXSectionsRequestQuery(section=section, limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_stock_filings_10_k_sections: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/stocks/filings/10-K/vX/sections"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_stock_filings_10_k_sections")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_stock_filings_10_k_sections", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_stock_filings_10_k_sections",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: reference
@mcp.tool()
async def list_stocks_8k_filings_text(
    form_type_gt: str | None = Field(None, alias="form_type.gt", description="Filter results to filings with form_type values greater than the specified value."),
    form_type_gte: str | None = Field(None, alias="form_type.gte", description="Filter results to filings with form_type values greater than or equal to the specified value."),
    form_type_lt: str | None = Field(None, alias="form_type.lt", description="Filter results to filings with form_type values less than the specified value."),
    form_type_lte: str | None = Field(None, alias="form_type.lte", description="Filter results to filings with form_type values less than or equal to the specified value."),
    limit: int | None = Field(None, description="Maximum number of results to return in the response. Defaults to 10 if not specified, with a maximum allowed value of 99.", ge=1, le=100),
    sort: str | None = Field(None, description="Comma-separated list of columns to sort by, with each column followed by '.asc' or '.desc' to specify sort direction. Defaults to sorting by filing_date in descending order if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve parsed text content from SEC 8-K current report filings, which disclose material corporate events such as earnings announcements, acquisitions, executive changes, and other significant developments."""

    # Construct request model with validation
    try:
        _request = _models.GetStocksFilings8KVXTextRequest(
            query=_models.GetStocksFilings8KVXTextRequestQuery(form_type_gt=form_type_gt, form_type_gte=form_type_gte, form_type_lt=form_type_lt, form_type_lte=form_type_lte, limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_stocks_8k_filings_text: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/stocks/filings/8-K/vX/text"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_stocks_8k_filings_text")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_stocks_8k_filings_text", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_stocks_8k_filings_text",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: reference
@mcp.tool()
async def list_13f_filings(
    filer_cik: str | None = Field(None, description="SEC Central Index Key (CIK) of the filing entity as a 10-digit zero-padded string. Use this to retrieve all 13F filings from a specific institutional investment manager."),
    accession_number: str | None = Field(None, description="Unique SEC accession number for a specific filing (format: NNNNNNNNNN-YY-NNNNNN). Use this to retrieve a particular 13F filing by its unique identifier."),
    limit: int | None = Field(None, description="Maximum number of results to return in the response. Must be between 1 and 1000; defaults to 100 if not specified.", ge=1, le=1001),
    sort: str | None = Field(None, description="Comma-separated list of columns to sort results by, with each column followed by '.asc' or '.desc' to specify ascending or descending order. Defaults to sorting by filing_date in descending order (most recent first) if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve SEC Form 13F quarterly filings data showing institutional investment manager holdings. Filter by filer or accession number to access specific filings from investment managers with at least $100 million in qualifying assets under management."""

    # Construct request model with validation
    try:
        _request = _models.GetStocksFilingsVX13FRequest(
            query=_models.GetStocksFilingsVX13FRequestQuery(filer_cik=filer_cik, accession_number=accession_number, limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_13f_filings: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/stocks/filings/vX/13-F"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_13f_filings")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_13f_filings", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_13f_filings",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: reference
@mcp.tool()
async def list_sec_filings(
    form_type_gt: str | None = Field(None, alias="form_type.gt", description="Filter results to form types greater than the specified value (alphabetically)."),
    form_type_gte: str | None = Field(None, alias="form_type.gte", description="Filter results to form types greater than or equal to the specified value (alphabetically)."),
    form_type_lt: str | None = Field(None, alias="form_type.lt", description="Filter results to form types less than the specified value (alphabetically)."),
    form_type_lte: str | None = Field(None, alias="form_type.lte", description="Filter results to form types less than or equal to the specified value (alphabetically)."),
    limit: int | None = Field(None, description="Maximum number of results to return. Defaults to 1000 if not specified. Maximum allowed value is 50000.", ge=1, le=50001),
    sort: str | None = Field(None, description="Comma-separated list of columns to sort by, with each column suffixed by '.asc' or '.desc' to specify sort direction. Defaults to 'filing_date.desc' if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve SEC EDGAR master index records for all SEC filings, including form types, filing dates, and direct links to source documents. Supports filtering by form type and customizable sorting and pagination."""

    # Construct request model with validation
    try:
        _request = _models.GetStocksFilingsVXIndexRequest(
            query=_models.GetStocksFilingsVXIndexRequestQuery(form_type_gt=form_type_gt, form_type_gte=form_type_gte, form_type_lt=form_type_lt, form_type_lte=form_type_lte, limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_sec_filings: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/stocks/filings/vX/index"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_sec_filings")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_sec_filings", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_sec_filings",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: reference
@mcp.tool()
async def list_risk_factors_from_stock_filings(
    filing_date_any_of: str | None = Field(None, alias="filing_date.any_of", description="Filter results to filings with dates matching any of the specified values. Provide one or more dates as a comma-separated list."),
    limit: int | None = Field(None, description="Maximum number of results to return. Defaults to 100 if not specified. Must be between 1 and 50,000.", ge=1, le=50000),
    sort: str | None = Field(None, description="Comma-separated list of columns to sort by, with each column followed by '.asc' or '.desc' to specify direction. Defaults to sorting by filing_date in descending order."),
) -> dict[str, Any] | ToolResult:
    """Retrieve risk factors disclosed in companies' 10-K SEC filings. Filter by filing date and control result size and ordering."""

    # Construct request model with validation
    try:
        _request = _models.GetStocksFilingsVXRiskFactorsRequest(
            query=_models.GetStocksFilingsVXRiskFactorsRequestQuery(filing_date_any_of=filing_date_any_of, limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_risk_factors_from_stock_filings: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/stocks/filings/vX/risk-factors"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_risk_factors_from_stock_filings")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_risk_factors_from_stock_filings", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_risk_factors_from_stock_filings",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: financials
@mcp.tool()
async def list_balance_sheets(
    limit: int | None = Field(None, description="Maximum number of results to return in the response. Accepts values from 1 to 50,000, with a default of 100 if not specified.", ge=1, le=50001),
    sort: str | None = Field(None, description="Comma-separated list of columns to sort by, with each column followed by '.asc' or '.desc' to specify ascending or descending order. Defaults to sorting by 'period_end' in ascending order if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve quarterly and annual balance sheet data for public companies, showing point-in-time snapshots of assets, liabilities, and shareholders' equity at each period end."""

    # Construct request model with validation
    try:
        _request = _models.GetStocksFinancialsV1BalanceSheetsRequest(
            query=_models.GetStocksFinancialsV1BalanceSheetsRequestQuery(limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_balance_sheets: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/stocks/financials/v1/balance-sheets"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_balance_sheets")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_balance_sheets", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_balance_sheets",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: financials
@mcp.tool()
async def list_cash_flow_statements(
    limit: int | None = Field(None, description="Maximum number of results to return in a single response. Accepts values from 1 to 50,000, with a default of 100 if not specified.", ge=1, le=50001),
    sort: str | None = Field(None, description="Comma-separated list of columns to sort results by, with each column followed by '.asc' or '.desc' to specify ascending or descending order. Defaults to 'period_end.asc' if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve quarterly, annual, and trailing twelve-month cash flow statement data for public companies, including detailed operating, investing, and financing cash flows with validated TTM calculations spanning exactly four quarters."""

    # Construct request model with validation
    try:
        _request = _models.GetStocksFinancialsV1CashFlowStatementsRequest(
            query=_models.GetStocksFinancialsV1CashFlowStatementsRequestQuery(limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_cash_flow_statements: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/stocks/financials/v1/cash-flow-statements"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_cash_flow_statements")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_cash_flow_statements", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_cash_flow_statements",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: financials
@mcp.tool()
async def list_income_statements(
    limit: int | None = Field(None, description="Maximum number of results to return per request, ranging from 1 to 50,000. Defaults to 100 if not specified.", ge=1, le=50001),
    sort: str | None = Field(None, description="Comma-separated list of columns to sort results by, with each column followed by '.asc' or '.desc' to specify ascending or descending order. Defaults to sorting by period_end in ascending order if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve income statement financial data for public companies, including revenue, expenses, and net income across multiple reporting periods. Results can be paginated and sorted by various financial metrics."""

    # Construct request model with validation
    try:
        _request = _models.GetStocksFinancialsV1IncomeStatementsRequest(
            query=_models.GetStocksFinancialsV1IncomeStatementsRequestQuery(limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_income_statements: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/stocks/financials/v1/income-statements"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_income_statements")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_income_statements", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_income_statements",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: financials
@mcp.tool()
async def list_stock_financial_ratios(
    price_gt: float | None = Field(None, alias="price.gt", description="Filter for stock prices strictly greater than the specified value."),
    price_gte: float | None = Field(None, alias="price.gte", description="Filter for stock prices greater than or equal to the specified value."),
    price_lt: float | None = Field(None, alias="price.lt", description="Filter for stock prices strictly less than the specified value."),
    price_lte: float | None = Field(None, alias="price.lte", description="Filter for stock prices less than or equal to the specified value."),
    average_volume_gt: float | None = Field(None, alias="average_volume.gt", description="Filter for average trading volume strictly greater than the specified value."),
    average_volume_gte: float | None = Field(None, alias="average_volume.gte", description="Filter for average trading volume greater than or equal to the specified value."),
    average_volume_lt: float | None = Field(None, alias="average_volume.lt", description="Filter for average trading volume strictly less than the specified value."),
    average_volume_lte: float | None = Field(None, alias="average_volume.lte", description="Filter for average trading volume less than or equal to the specified value."),
    market_cap_gt: float | None = Field(None, alias="market_cap.gt", description="Filter for market capitalization strictly greater than the specified value."),
    market_cap_gte: float | None = Field(None, alias="market_cap.gte", description="Filter for market capitalization greater than or equal to the specified value."),
    market_cap_lt: float | None = Field(None, alias="market_cap.lt", description="Filter for market capitalization strictly less than the specified value."),
    market_cap_lte: float | None = Field(None, alias="market_cap.lte", description="Filter for market capitalization less than or equal to the specified value."),
    earnings_per_share_gt: float | None = Field(None, alias="earnings_per_share.gt", description="Filter for earnings per share strictly greater than the specified value."),
    earnings_per_share_gte: float | None = Field(None, alias="earnings_per_share.gte", description="Filter for earnings per share greater than or equal to the specified value."),
    earnings_per_share_lt: float | None = Field(None, alias="earnings_per_share.lt", description="Filter for earnings per share strictly less than the specified value."),
    earnings_per_share_lte: float | None = Field(None, alias="earnings_per_share.lte", description="Filter for earnings per share less than or equal to the specified value."),
    price_to_earnings_gt: float | None = Field(None, alias="price_to_earnings.gt", description="Filter for price-to-earnings ratio strictly greater than the specified value."),
    price_to_earnings_gte: float | None = Field(None, alias="price_to_earnings.gte", description="Filter for price-to-earnings ratio greater than or equal to the specified value."),
    price_to_earnings_lt: float | None = Field(None, alias="price_to_earnings.lt", description="Filter for price-to-earnings ratio strictly less than the specified value."),
    price_to_earnings_lte: float | None = Field(None, alias="price_to_earnings.lte", description="Filter for price-to-earnings ratio less than or equal to the specified value."),
    price_to_book_gt: float | None = Field(None, alias="price_to_book.gt", description="Filter for price-to-book ratio strictly greater than the specified value."),
    price_to_book_gte: float | None = Field(None, alias="price_to_book.gte", description="Filter for price-to-book ratio greater than or equal to the specified value."),
    price_to_book_lt: float | None = Field(None, alias="price_to_book.lt", description="Filter for price-to-book ratio strictly less than the specified value."),
    price_to_book_lte: float | None = Field(None, alias="price_to_book.lte", description="Filter for price-to-book ratio less than or equal to the specified value."),
    price_to_sales_gt: float | None = Field(None, alias="price_to_sales.gt", description="Filter for price-to-sales ratio strictly greater than the specified value."),
    price_to_sales_gte: float | None = Field(None, alias="price_to_sales.gte", description="Filter for price-to-sales ratio greater than or equal to the specified value."),
    price_to_sales_lt: float | None = Field(None, alias="price_to_sales.lt", description="Filter for price-to-sales ratio strictly less than the specified value."),
    price_to_sales_lte: float | None = Field(None, alias="price_to_sales.lte", description="Filter for price-to-sales ratio less than or equal to the specified value."),
    price_to_cash_flow_gt: float | None = Field(None, alias="price_to_cash_flow.gt", description="Filter for price-to-cash flow ratio strictly greater than the specified value."),
    price_to_cash_flow_gte: float | None = Field(None, alias="price_to_cash_flow.gte", description="Filter for price-to-cash flow ratio greater than or equal to the specified value."),
    price_to_cash_flow_lt: float | None = Field(None, alias="price_to_cash_flow.lt", description="Filter for price-to-cash flow ratio strictly less than the specified value."),
    price_to_cash_flow_lte: float | None = Field(None, alias="price_to_cash_flow.lte", description="Filter for price-to-cash flow ratio less than or equal to the specified value."),
    price_to_free_cash_flow_gt: float | None = Field(None, alias="price_to_free_cash_flow.gt", description="Filter for price-to-free cash flow ratio strictly greater than the specified value."),
    price_to_free_cash_flow_gte: float | None = Field(None, alias="price_to_free_cash_flow.gte", description="Filter for price-to-free cash flow ratio greater than or equal to the specified value."),
    price_to_free_cash_flow_lt: float | None = Field(None, alias="price_to_free_cash_flow.lt", description="Filter for price-to-free cash flow ratio strictly less than the specified value."),
    price_to_free_cash_flow_lte: float | None = Field(None, alias="price_to_free_cash_flow.lte", description="Filter for price-to-free cash flow ratio less than or equal to the specified value."),
    dividend_yield_gt: float | None = Field(None, alias="dividend_yield.gt", description="Filter for dividend yield strictly greater than the specified value."),
    dividend_yield_gte: float | None = Field(None, alias="dividend_yield.gte", description="Filter for dividend yield greater than or equal to the specified value."),
    dividend_yield_lt: float | None = Field(None, alias="dividend_yield.lt", description="Filter for dividend yield strictly less than the specified value."),
    dividend_yield_lte: float | None = Field(None, alias="dividend_yield.lte", description="Filter for dividend yield less than or equal to the specified value."),
    return_on_assets_gt: float | None = Field(None, alias="return_on_assets.gt", description="Filter for return on assets (ROA) strictly greater than the specified value."),
    return_on_assets_gte: float | None = Field(None, alias="return_on_assets.gte", description="Filter for return on assets (ROA) greater than or equal to the specified value."),
    return_on_assets_lt: float | None = Field(None, alias="return_on_assets.lt", description="Filter for return on assets (ROA) strictly less than the specified value."),
    return_on_assets_lte: float | None = Field(None, alias="return_on_assets.lte", description="Filter for return on assets (ROA) less than or equal to the specified value."),
    return_on_equity_gt: float | None = Field(None, alias="return_on_equity.gt", description="Filter for return on equity (ROE) strictly greater than the specified value."),
    return_on_equity_gte: float | None = Field(None, alias="return_on_equity.gte", description="Filter for return on equity (ROE) greater than or equal to the specified value."),
    return_on_equity_lt: float | None = Field(None, alias="return_on_equity.lt", description="Filter for return on equity (ROE) strictly less than the specified value."),
    return_on_equity_lte: float | None = Field(None, alias="return_on_equity.lte", description="Filter for return on equity (ROE) less than or equal to the specified value."),
    debt_to_equity_gt: float | None = Field(None, alias="debt_to_equity.gt", description="Filter for debt-to-equity ratio strictly greater than the specified value."),
    debt_to_equity_gte: float | None = Field(None, alias="debt_to_equity.gte", description="Filter for debt-to-equity ratio greater than or equal to the specified value."),
    debt_to_equity_lt: float | None = Field(None, alias="debt_to_equity.lt", description="Filter for debt-to-equity ratio strictly less than the specified value."),
    debt_to_equity_lte: float | None = Field(None, alias="debt_to_equity.lte", description="Filter for debt-to-equity ratio less than or equal to the specified value."),
    current_gt: float | None = Field(None, alias="current.gt", description="Filter for current ratio strictly greater than the specified value."),
    current_gte: float | None = Field(None, alias="current.gte", description="Filter for current ratio greater than or equal to the specified value."),
    current_lt: float | None = Field(None, alias="current.lt", description="Filter for current ratio strictly less than the specified value."),
    current_lte: float | None = Field(None, alias="current.lte", description="Filter for current ratio less than or equal to the specified value."),
    quick_gt: float | None = Field(None, alias="quick.gt", description="Filter for quick ratio strictly greater than the specified value."),
    quick_gte: float | None = Field(None, alias="quick.gte", description="Filter for quick ratio greater than or equal to the specified value."),
    quick_lt: float | None = Field(None, alias="quick.lt", description="Filter for quick ratio strictly less than the specified value."),
    quick_lte: float | None = Field(None, alias="quick.lte", description="Filter for quick ratio less than or equal to the specified value."),
    cash_gt: float | None = Field(None, alias="cash.gt", description="Filter for cash ratio strictly greater than the specified value."),
    cash_gte: float | None = Field(None, alias="cash.gte", description="Filter for cash ratio greater than or equal to the specified value."),
    cash_lt: float | None = Field(None, alias="cash.lt", description="Filter for cash ratio strictly less than the specified value."),
    cash_lte: float | None = Field(None, alias="cash.lte", description="Filter for cash ratio less than or equal to the specified value."),
    ev_to_sales_gt: float | None = Field(None, alias="ev_to_sales.gt", description="Filter for enterprise value-to-sales ratio strictly greater than the specified value."),
    ev_to_sales_gte: float | None = Field(None, alias="ev_to_sales.gte", description="Filter for enterprise value-to-sales ratio greater than or equal to the specified value."),
    ev_to_sales_lt: float | None = Field(None, alias="ev_to_sales.lt", description="Filter for enterprise value-to-sales ratio strictly less than the specified value."),
    ev_to_sales_lte: float | None = Field(None, alias="ev_to_sales.lte", description="Filter for enterprise value-to-sales ratio less than or equal to the specified value."),
    ev_to_ebitda_gt: float | None = Field(None, alias="ev_to_ebitda.gt", description="Filter for enterprise value-to-EBITDA ratio strictly greater than the specified value."),
    ev_to_ebitda_gte: float | None = Field(None, alias="ev_to_ebitda.gte", description="Filter for enterprise value-to-EBITDA ratio greater than or equal to the specified value."),
    ev_to_ebitda_lt: float | None = Field(None, alias="ev_to_ebitda.lt", description="Filter for enterprise value-to-EBITDA ratio strictly less than the specified value."),
    ev_to_ebitda_lte: float | None = Field(None, alias="ev_to_ebitda.lte", description="Filter for enterprise value-to-EBITDA ratio less than or equal to the specified value."),
    enterprise_value_gt: float | None = Field(None, alias="enterprise_value.gt", description="Filter for enterprise value strictly greater than the specified value."),
    enterprise_value_gte: float | None = Field(None, alias="enterprise_value.gte", description="Filter for enterprise value greater than or equal to the specified value."),
    enterprise_value_lt: float | None = Field(None, alias="enterprise_value.lt", description="Filter for enterprise value strictly less than the specified value."),
    enterprise_value_lte: float | None = Field(None, alias="enterprise_value.lte", description="Filter for enterprise value less than or equal to the specified value."),
    free_cash_flow_gt: float | None = Field(None, alias="free_cash_flow.gt", description="Filter for free cash flow strictly greater than the specified value."),
    free_cash_flow_gte: float | None = Field(None, alias="free_cash_flow.gte", description="Filter for free cash flow greater than or equal to the specified value."),
    free_cash_flow_lt: float | None = Field(None, alias="free_cash_flow.lt", description="Filter for free cash flow strictly less than the specified value."),
    free_cash_flow_lte: float | None = Field(None, alias="free_cash_flow.lte", description="Filter for free cash flow less than or equal to the specified value."),
    limit: int | None = Field(None, description="Maximum number of results to return. Defaults to 100 if not specified; maximum allowed is 50,000.", ge=1, le=50001),
    sort: str | None = Field(None, description="Comma-separated list of columns to sort by, with each column optionally suffixed by '.asc' or '.desc' to specify sort direction. Defaults to 'ticker.asc' if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve comprehensive financial ratios for public companies including valuation, profitability, liquidity, and leverage metrics. Data combines income statements, balance sheets, and cash flow statements with daily stock prices, using trailing twelve months (TTM) data for income/cash flow metrics and quarterly data for balance sheet items."""

    # Construct request model with validation
    try:
        _request = _models.GetStocksFinancialsV1RatiosRequest(
            query=_models.GetStocksFinancialsV1RatiosRequestQuery(price_gt=price_gt, price_gte=price_gte, price_lt=price_lt, price_lte=price_lte, average_volume_gt=average_volume_gt, average_volume_gte=average_volume_gte, average_volume_lt=average_volume_lt, average_volume_lte=average_volume_lte, market_cap_gt=market_cap_gt, market_cap_gte=market_cap_gte, market_cap_lt=market_cap_lt, market_cap_lte=market_cap_lte, earnings_per_share_gt=earnings_per_share_gt, earnings_per_share_gte=earnings_per_share_gte, earnings_per_share_lt=earnings_per_share_lt, earnings_per_share_lte=earnings_per_share_lte, price_to_earnings_gt=price_to_earnings_gt, price_to_earnings_gte=price_to_earnings_gte, price_to_earnings_lt=price_to_earnings_lt, price_to_earnings_lte=price_to_earnings_lte, price_to_book_gt=price_to_book_gt, price_to_book_gte=price_to_book_gte, price_to_book_lt=price_to_book_lt, price_to_book_lte=price_to_book_lte, price_to_sales_gt=price_to_sales_gt, price_to_sales_gte=price_to_sales_gte, price_to_sales_lt=price_to_sales_lt, price_to_sales_lte=price_to_sales_lte, price_to_cash_flow_gt=price_to_cash_flow_gt, price_to_cash_flow_gte=price_to_cash_flow_gte, price_to_cash_flow_lt=price_to_cash_flow_lt, price_to_cash_flow_lte=price_to_cash_flow_lte, price_to_free_cash_flow_gt=price_to_free_cash_flow_gt, price_to_free_cash_flow_gte=price_to_free_cash_flow_gte, price_to_free_cash_flow_lt=price_to_free_cash_flow_lt, price_to_free_cash_flow_lte=price_to_free_cash_flow_lte, dividend_yield_gt=dividend_yield_gt, dividend_yield_gte=dividend_yield_gte, dividend_yield_lt=dividend_yield_lt, dividend_yield_lte=dividend_yield_lte, return_on_assets_gt=return_on_assets_gt, return_on_assets_gte=return_on_assets_gte, return_on_assets_lt=return_on_assets_lt, return_on_assets_lte=return_on_assets_lte, return_on_equity_gt=return_on_equity_gt, return_on_equity_gte=return_on_equity_gte, return_on_equity_lt=return_on_equity_lt, return_on_equity_lte=return_on_equity_lte, debt_to_equity_gt=debt_to_equity_gt, debt_to_equity_gte=debt_to_equity_gte, debt_to_equity_lt=debt_to_equity_lt, debt_to_equity_lte=debt_to_equity_lte, current_gt=current_gt, current_gte=current_gte, current_lt=current_lt, current_lte=current_lte, quick_gt=quick_gt, quick_gte=quick_gte, quick_lt=quick_lt, quick_lte=quick_lte, cash_gt=cash_gt, cash_gte=cash_gte, cash_lt=cash_lt, cash_lte=cash_lte, ev_to_sales_gt=ev_to_sales_gt, ev_to_sales_gte=ev_to_sales_gte, ev_to_sales_lt=ev_to_sales_lt, ev_to_sales_lte=ev_to_sales_lte, ev_to_ebitda_gt=ev_to_ebitda_gt, ev_to_ebitda_gte=ev_to_ebitda_gte, ev_to_ebitda_lt=ev_to_ebitda_lt, ev_to_ebitda_lte=ev_to_ebitda_lte, enterprise_value_gt=enterprise_value_gt, enterprise_value_gte=enterprise_value_gte, enterprise_value_lt=enterprise_value_lt, enterprise_value_lte=enterprise_value_lte, free_cash_flow_gt=free_cash_flow_gt, free_cash_flow_gte=free_cash_flow_gte, free_cash_flow_lt=free_cash_flow_lt, free_cash_flow_lte=free_cash_flow_lte, limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_stock_financial_ratios: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/stocks/financials/v1/ratios"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_stock_financial_ratios")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_stock_financial_ratios", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_stock_financial_ratios",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: reference
@mcp.tool()
async def list_risk_factor_taxonomies(
    taxonomy_gt: float | None = Field(None, alias="taxonomy.gt", description="Filter taxonomies with a value strictly greater than the specified number."),
    taxonomy_gte: float | None = Field(None, alias="taxonomy.gte", description="Filter taxonomies with a value greater than or equal to the specified number."),
    taxonomy_lt: float | None = Field(None, alias="taxonomy.lt", description="Filter taxonomies with a value strictly less than the specified number."),
    taxonomy_lte: float | None = Field(None, alias="taxonomy.lte", description="Filter taxonomies with a value less than or equal to the specified number."),
    primary_category_any_of: str | None = Field(None, alias="primary_category.any_of", description="Filter to include only taxonomies whose primary category matches any of the specified values. Provide multiple values as a comma-separated list."),
    primary_category_gt: str | None = Field(None, alias="primary_category.gt", description="Filter taxonomies by primary category values strictly greater than the specified value (alphabetically for strings)."),
    primary_category_gte: str | None = Field(None, alias="primary_category.gte", description="Filter taxonomies by primary category values greater than or equal to the specified value (alphabetically for strings)."),
    primary_category_lt: str | None = Field(None, alias="primary_category.lt", description="Filter taxonomies by primary category values strictly less than the specified value (alphabetically for strings)."),
    primary_category_lte: str | None = Field(None, alias="primary_category.lte", description="Filter taxonomies by primary category values less than or equal to the specified value (alphabetically for strings)."),
    secondary_category_any_of: str | None = Field(None, alias="secondary_category.any_of", description="Filter to include only taxonomies whose secondary category matches any of the specified values. Provide multiple values as a comma-separated list."),
    secondary_category_gt: str | None = Field(None, alias="secondary_category.gt", description="Filter taxonomies by secondary category values strictly greater than the specified value (alphabetically for strings)."),
    secondary_category_gte: str | None = Field(None, alias="secondary_category.gte", description="Filter taxonomies by secondary category values greater than or equal to the specified value (alphabetically for strings)."),
    secondary_category_lt: str | None = Field(None, alias="secondary_category.lt", description="Filter taxonomies by secondary category values strictly less than the specified value (alphabetically for strings)."),
    secondary_category_lte: str | None = Field(None, alias="secondary_category.lte", description="Filter taxonomies by secondary category values less than or equal to the specified value (alphabetically for strings)."),
    tertiary_category_any_of: str | None = Field(None, alias="tertiary_category.any_of", description="Filter to include only taxonomies whose tertiary category matches any of the specified values. Provide multiple values as a comma-separated list."),
    tertiary_category_gt: str | None = Field(None, alias="tertiary_category.gt", description="Filter taxonomies by tertiary category values strictly greater than the specified value (alphabetically for strings)."),
    tertiary_category_gte: str | None = Field(None, alias="tertiary_category.gte", description="Filter taxonomies by tertiary category values greater than or equal to the specified value (alphabetically for strings)."),
    tertiary_category_lt: str | None = Field(None, alias="tertiary_category.lt", description="Filter taxonomies by tertiary category values strictly less than the specified value (alphabetically for strings)."),
    tertiary_category_lte: str | None = Field(None, alias="tertiary_category.lte", description="Filter taxonomies by tertiary category values less than or equal to the specified value (alphabetically for strings)."),
    limit: int | None = Field(None, description="Maximum number of results to return. Defaults to 200 if not specified; maximum allowed is 999.", ge=1, le=1000),
    sort: str | None = Field(None, description="Sort results by one or more columns in ascending or descending order. Specify columns as a comma-separated list with '.asc' or '.desc' suffix (e.g., 'taxonomy.asc,primary_category.desc'). Defaults to 'taxonomy.desc' if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve the complete taxonomy of risk factor classifications used across the platform. Filter and sort by taxonomy value, primary/secondary/tertiary categories to find specific risk factor definitions."""

    # Construct request model with validation
    try:
        _request = _models.GetStocksTaxonomiesVXRiskFactorsRequest(
            query=_models.GetStocksTaxonomiesVXRiskFactorsRequestQuery(taxonomy_gt=taxonomy_gt, taxonomy_gte=taxonomy_gte, taxonomy_lt=taxonomy_lt, taxonomy_lte=taxonomy_lte, primary_category_any_of=primary_category_any_of, primary_category_gt=primary_category_gt, primary_category_gte=primary_category_gte, primary_category_lt=primary_category_lt, primary_category_lte=primary_category_lte, secondary_category_any_of=secondary_category_any_of, secondary_category_gt=secondary_category_gt, secondary_category_gte=secondary_category_gte, secondary_category_lt=secondary_category_lt, secondary_category_lte=secondary_category_lte, tertiary_category_any_of=tertiary_category_any_of, tertiary_category_gt=tertiary_category_gt, tertiary_category_gte=tertiary_category_gte, tertiary_category_lt=tertiary_category_lt, tertiary_category_lte=tertiary_category_lte, limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_risk_factor_taxonomies: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/stocks/taxonomies/vX/risk-factors"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_risk_factor_taxonomies")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_risk_factor_taxonomies", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_risk_factor_taxonomies",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: us_stocks_reference
@mcp.tool()
async def list_stock_dividends(
    frequency_gt: str | None = Field(None, alias="frequency.gt", description="Filter results to dividends with a frequency value greater than the specified integer."),
    frequency_gte: str | None = Field(None, alias="frequency.gte", description="Filter results to dividends with a frequency value greater than or equal to the specified integer."),
    frequency_lt: str | None = Field(None, alias="frequency.lt", description="Filter results to dividends with a frequency value less than the specified integer."),
    frequency_lte: str | None = Field(None, alias="frequency.lte", description="Filter results to dividends with a frequency value less than or equal to the specified integer."),
    distribution_type_any_of: Literal["recurring", "special", "supplemental", "irregular", "unknown"] | None = Field(None, alias="distribution_type.any_of", description="Filter results to dividends matching any of the specified distribution types. Accepts comma-separated values from: recurring, special, supplemental, irregular, or unknown."),
    limit: int | None = Field(None, description="Maximum number of results to return per request. Defaults to 100 if not specified; maximum allowed is 5000.", ge=1, le=5001),
    sort: str | None = Field(None, description="Comma-separated list of columns to sort by, with sort direction specified per column using '.asc' or '.desc' suffix. Defaults to sorting by ticker in ascending order if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve historical dividend payment records for US stocks, including split-adjusted amounts and historical adjustment factors for price normalization. Filter by dividend frequency and distribution type, with flexible sorting and pagination options."""

    _frequency_gt = _parse_int(frequency_gt)
    _frequency_gte = _parse_int(frequency_gte)
    _frequency_lt = _parse_int(frequency_lt)
    _frequency_lte = _parse_int(frequency_lte)

    # Construct request model with validation
    try:
        _request = _models.GetStocksV1DividendsRequest(
            query=_models.GetStocksV1DividendsRequestQuery(frequency_gt=_frequency_gt, frequency_gte=_frequency_gte, frequency_lt=_frequency_lt, frequency_lte=_frequency_lte, distribution_type_any_of=distribution_type_any_of, limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_stock_dividends: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/stocks/v1/dividends"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_stock_dividends")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_stock_dividends", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_stock_dividends",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: reference
@mcp.tool()
async def list_short_interest(
    days_to_cover: float | None = Field(None, description="Filter results by days-to-cover ratio, calculated as short interest divided by average daily volume. Accepts decimal values to represent the estimated number of trading days needed to cover all short positions at current volume levels."),
    settlement_date: str | None = Field(None, description="Filter results by settlement date in YYYY-MM-DD format, typically aligned with exchange reporting schedules when short interest data becomes official."),
    avg_daily_volume: str | None = Field(None, description="Filter results by average daily trading volume as an integer, used to contextualize short interest levels and calculate days-to-cover metrics."),
    limit: int | None = Field(None, description="Maximum number of results to return in the response. Defaults to 10 if not specified; maximum allowed value is 50,000.", ge=1, le=50001),
    sort: str | None = Field(None, description="Comma-separated list of columns to sort by, with each column followed by .asc or .desc to specify ascending or descending order. Defaults to sorting by ticker in ascending order if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve FINRA short interest data for securities on a specific settlement date, including metrics on short positions, trading volume, and days-to-cover calculations."""

    _avg_daily_volume = _parse_int(avg_daily_volume)

    # Construct request model with validation
    try:
        _request = _models.GetStocksV1ShortInterestRequest(
            query=_models.GetStocksV1ShortInterestRequestQuery(days_to_cover=days_to_cover, settlement_date=settlement_date, avg_daily_volume=_avg_daily_volume, limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_short_interest: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/stocks/v1/short-interest"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_short_interest")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_short_interest", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_short_interest",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: reference
@mcp.tool()
async def list_short_volume_by_ticker(
    short_volume_ratio_any_of: str | None = Field(None, alias="short_volume_ratio.any_of", description="Filter results to include only records where the short volume ratio matches any of the specified values. Provide multiple values as a comma-separated list of floating point numbers."),
    short_volume_ratio_gt: float | None = Field(None, alias="short_volume_ratio.gt", description="Filter results to include only records where the short volume ratio is strictly greater than the specified floating point value."),
    short_volume_ratio_gte: float | None = Field(None, alias="short_volume_ratio.gte", description="Filter results to include only records where the short volume ratio is greater than or equal to the specified floating point value."),
    short_volume_ratio_lt: float | None = Field(None, alias="short_volume_ratio.lt", description="Filter results to include only records where the short volume ratio is strictly less than the specified floating point value."),
    short_volume_ratio_lte: float | None = Field(None, alias="short_volume_ratio.lte", description="Filter results to include only records where the short volume ratio is less than or equal to the specified floating point value."),
    limit: int | None = Field(None, description="Limit the number of results returned. Defaults to 10 if not specified. Maximum allowed value is 50,000.", ge=1, le=50001),
    sort: str | None = Field(None, description="Sort results by one or more columns in ascending or descending order. Specify columns as a comma-separated list with '.asc' or '.desc' appended to each column name (e.g., 'ticker.asc,short_volume_ratio.desc'). Defaults to sorting by ticker in ascending order."),
) -> dict[str, Any] | ToolResult:
    """Retrieve short selling volume data across stock tickers, including total trading volume, short sale metrics, and platform-specific breakdowns. Filter and sort results to analyze short selling activity."""

    # Construct request model with validation
    try:
        _request = _models.GetStocksV1ShortVolumeRequest(
            query=_models.GetStocksV1ShortVolumeRequestQuery(short_volume_ratio_any_of=short_volume_ratio_any_of, short_volume_ratio_gt=short_volume_ratio_gt, short_volume_ratio_gte=short_volume_ratio_gte, short_volume_ratio_lt=short_volume_ratio_lt, short_volume_ratio_lte=short_volume_ratio_lte, limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_short_volume_by_ticker: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/stocks/v1/short-volume"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_short_volume_by_ticker")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_short_volume_by_ticker", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_short_volume_by_ticker",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: us_stocks_reference
@mcp.tool()
async def list_stock_splits_historical(
    execution_date_gt: str | None = Field(None, alias="execution_date.gt", description="Filter results to splits executed after this date (exclusive). Use ISO 8601 format: yyyy-mm-dd."),
    execution_date_gte: str | None = Field(None, alias="execution_date.gte", description="Filter results to splits executed on or after this date (inclusive). Use ISO 8601 format: yyyy-mm-dd."),
    execution_date_lt: str | None = Field(None, alias="execution_date.lt", description="Filter results to splits executed before this date (exclusive). Use ISO 8601 format: yyyy-mm-dd."),
    execution_date_lte: str | None = Field(None, alias="execution_date.lte", description="Filter results to splits executed on or before this date (inclusive). Use ISO 8601 format: yyyy-mm-dd."),
    adjustment_type_any_of: Literal["forward_split", "reverse_split", "stock_dividend"] | None = Field(None, alias="adjustment_type.any_of", description="Filter results by split type. Accepts one or more values (forward_split, reverse_split, or stock_dividend) as a comma-separated list."),
    limit: int | None = Field(None, description="Maximum number of results to return. Defaults to 100 if not specified; maximum allowed is 5000.", ge=1, le=5001),
    sort: str | None = Field(None, description="Sort results by one or more columns in ascending or descending order. Specify as comma-separated list with '.asc' or '.desc' suffix (e.g., 'execution_date.desc'). Defaults to 'execution_date.desc' if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve historical stock split and reverse split events for US equities, including adjustment factors for normalizing historical price data."""

    # Construct request model with validation
    try:
        _request = _models.GetStocksV1SplitsRequest(
            query=_models.GetStocksV1SplitsRequestQuery(execution_date_gt=execution_date_gt, execution_date_gte=execution_date_gte, execution_date_lt=execution_date_lt, execution_date_lte=execution_date_lte, adjustment_type_any_of=adjustment_type_any_of, limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_stock_splits_historical: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/stocks/v1/splits"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_stock_splits_historical")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_stock_splits_historical", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_stock_splits_historical",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: reference
@mcp.tool()
async def list_stocks_by_float(
    free_float_percent_gt: float | None = Field(None, alias="free_float_percent.gt", description="Filter results to securities with free float percentage greater than this value. Accepts decimal numbers."),
    free_float_percent_gte: float | None = Field(None, alias="free_float_percent.gte", description="Filter results to securities with free float percentage greater than or equal to this value. Accepts decimal numbers."),
    free_float_percent_lt: float | None = Field(None, alias="free_float_percent.lt", description="Filter results to securities with free float percentage less than this value. Accepts decimal numbers."),
    free_float_percent_lte: float | None = Field(None, alias="free_float_percent.lte", description="Filter results to securities with free float percentage less than or equal to this value. Accepts decimal numbers."),
    limit: int | None = Field(None, description="Maximum number of results to return. Defaults to 100 if not specified; maximum allowed is 5000.", ge=1, le=5001),
    sort: str | None = Field(None, description="Comma-separated list of columns to sort by, with each column followed by '.asc' or '.desc' to specify direction. Defaults to sorting by ticker in ascending order."),
) -> dict[str, Any] | ToolResult:
    """Retrieve free float data for US-listed securities, including the number of shares available for public trading and the percentage of total shares outstanding. Results can be filtered by free float percentage and sorted by multiple columns."""

    # Construct request model with validation
    try:
        _request = _models.GetStocksVXFloatRequest(
            query=_models.GetStocksVXFloatRequestQuery(free_float_percent_gt=free_float_percent_gt, free_float_percent_gte=free_float_percent_gte, free_float_percent_lt=free_float_percent_lt, free_float_percent_lte=free_float_percent_lte, limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_stocks_by_float: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/stocks/vX/float"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_stocks_by_float")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_stocks_by_float", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_stocks_by_float",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: tmx
@mcp.tool()
async def list_corporate_events(
    status: str | None = Field(None, description="Filter events by their current status. Valid statuses are: approved, canceled, confirmed, historical, pending_approval, postponed, and unconfirmed."),
    tmx_company_id: str | None = Field(None, description="Filter events by the TMX company identifier. Accepts a specific company ID as a 64-bit integer."),
    tmx_company_id_gt: str | None = Field(None, alias="tmx_company_id.gt", description="Filter to companies with TMX ID greater than the specified value (64-bit integer)."),
    tmx_company_id_gte: str | None = Field(None, alias="tmx_company_id.gte", description="Filter to companies with TMX ID greater than or equal to the specified value (64-bit integer)."),
    tmx_company_id_lt: str | None = Field(None, alias="tmx_company_id.lt", description="Filter to companies with TMX ID less than the specified value (64-bit integer)."),
    tmx_company_id_lte: str | None = Field(None, alias="tmx_company_id.lte", description="Filter to companies with TMX ID less than or equal to the specified value (64-bit integer)."),
    tmx_record_id: str | None = Field(None, description="Filter events by the unique TMX event record identifier (alphanumeric string)."),
    limit: int | None = Field(None, description="Maximum number of results to return. Must be between 1 and 50,000; defaults to 100 if not specified.", ge=1, le=50001),
    sort: str | None = Field(None, description="Comma-separated list of columns to sort by, with '.asc' or '.desc' appended to each column to specify direction. Defaults to sorting by date in descending order if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve corporate events and announcements for publicly traded companies, including earnings releases, conferences, dividends, and business updates from TMX. Filter by company, event status, or record ID, and customize result ordering and pagination."""

    _tmx_company_id = _parse_int(tmx_company_id)
    _tmx_company_id_gt = _parse_int(tmx_company_id_gt)
    _tmx_company_id_gte = _parse_int(tmx_company_id_gte)
    _tmx_company_id_lt = _parse_int(tmx_company_id_lt)
    _tmx_company_id_lte = _parse_int(tmx_company_id_lte)

    # Construct request model with validation
    try:
        _request = _models.GetTmxV1CorporateEventsRequest(
            query=_models.GetTmxV1CorporateEventsRequestQuery(status=status, tmx_company_id=_tmx_company_id, tmx_company_id_gt=_tmx_company_id_gt, tmx_company_id_gte=_tmx_company_id_gte, tmx_company_id_lt=_tmx_company_id_lt, tmx_company_id_lte=_tmx_company_id_lte, tmx_record_id=tmx_record_id, limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_corporate_events: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/tmx/v1/corporate-events"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_corporate_events")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_corporate_events", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_corporate_events",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: fx:conversion
@mcp.tool()
async def get_currency_conversion(
    from_: str = Field(..., alias="from", description="The source currency code (e.g., AUD, USD). Use standard ISO 4217 three-letter currency codes."),
    to: str = Field(..., description="The target currency code (e.g., USD, CAD). Use standard ISO 4217 three-letter currency codes."),
    amount: float | None = Field(None, description="The amount to convert as a decimal number. Defaults to 1 if not specified."),
    precision: Literal[0, 1, 2, 3, 4] | None = Field(None, description="The number of decimal places for the conversion result, ranging from 0 to 4. Defaults to 2 decimal places."),
) -> dict[str, Any] | ToolResult:
    """Convert between two currencies using real-time market rates. Supports bidirectional conversion (e.g., USD to CAD or CAD to USD) with customizable amount and decimal precision."""

    # Construct request model with validation
    try:
        _request = _models.RealTimeCurrencyConversionRequest(
            path=_models.RealTimeCurrencyConversionRequestPath(from_=from_, to=to),
            query=_models.RealTimeCurrencyConversionRequestQuery(amount=amount, precision=precision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_currency_conversion: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/conversion/{from}/{to}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/conversion/{from}/{to}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_currency_conversion")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_currency_conversion", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_currency_conversion",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: fx:trades
@mcp.tool()
async def get_historic_forex_ticks(
    from_: str = Field(..., alias="from", description="The source currency code (e.g., USD, AUD, EUR) in the currency pair."),
    to: str = Field(..., description="The target currency code (e.g., JPY, USD, GBP) in the currency pair."),
    date: str = Field(..., description="The date for which to retrieve historic ticks, specified in ISO 8601 date format (YYYY-MM-DD)."),
    offset: int | None = Field(None, description="Pagination offset for retrieving subsequent pages of results. Pass the timestamp value from the last result of the previous page to continue from that point."),
    limit: int | None = Field(None, description="Maximum number of ticks to return in the response. Accepts values up to 10,000."),
) -> dict[str, Any] | ToolResult:
    """Retrieve historic tick data for a forex currency pair on a specific date. Use pagination parameters to navigate through large result sets."""

    # Construct request model with validation
    try:
        _request = _models.DeprecatedGetHistoricForexQuotesRequest(
            path=_models.DeprecatedGetHistoricForexQuotesRequestPath(from_=from_, to=to, date=date),
            query=_models.DeprecatedGetHistoricForexQuotesRequestQuery(offset=offset, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_historic_forex_ticks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/historic/forex/{from}/{to}/{date}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/historic/forex/{from}/{to}/{date}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_historic_forex_ticks")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_historic_forex_ticks", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_historic_forex_ticks",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: crypto:aggregates
@mcp.tool()
async def get_crypto_ema(
    crypto_ticker: str = Field(..., alias="cryptoTicker", description="The cryptocurrency ticker symbol (e.g., X:BTCUSD for Bitcoin in USD)."),
    timespan: Literal["minute", "hour", "day", "week", "month", "quarter", "year"] | None = Field(None, description="The time interval for aggregating price data. Choose from minute, hour, day, week, month, quarter, or year intervals. Defaults to daily aggregates."),
    window: int | None = Field(None, description="The number of periods to include in the EMA calculation. For example, a window of 10 with daily timespan calculates a 10-day moving average. Defaults to 50 periods."),
    series_type: Literal["open", "high", "low", "close"] | None = Field(None, description="The price type used for EMA calculation: open, high, low, or close price. Defaults to close price."),
    order: Literal["asc", "desc"] | None = Field(None, description="Sort order for results by timestamp: ascending (oldest first) or descending (newest first). Defaults to descending."),
    limit: int | None = Field(None, description="Maximum number of results to return. Accepts 1 to 5000 results, defaults to 10.", le=5000),
) -> dict[str, Any] | ToolResult:
    """Retrieve the exponential moving average (EMA) for a cryptocurrency ticker over a specified time range. Use this to analyze price trends and momentum across different timeframes and price types."""

    # Construct request model with validation
    try:
        _request = _models.CryptoEmaRequest(
            path=_models.CryptoEmaRequestPath(crypto_ticker=crypto_ticker),
            query=_models.CryptoEmaRequestQuery(timespan=timespan, window=window, series_type=series_type, order=order, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_crypto_ema: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/indicators/ema/{cryptoTicker}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/indicators/ema/{cryptoTicker}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_crypto_ema")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_crypto_ema", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_crypto_ema",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: fx:aggregates
@mcp.tool()
async def get_forex_ema(
    fx_ticker: str = Field(..., alias="fxTicker", description="The forex ticker symbol to analyze, formatted as a currency pair (e.g., C:EURUSD for EUR/USD)."),
    timespan: Literal["minute", "hour", "day", "week", "month", "quarter", "year"] | None = Field(None, description="The time interval for aggregating price data before EMA calculation. Options include minute, hour, day, week, month, quarter, or year. Defaults to daily aggregates."),
    adjusted: bool | None = Field(None, description="Whether to adjust aggregates for corporate actions like splits. When true (default), results reflect adjusted prices; set to false for unadjusted data."),
    window: int | None = Field(None, description="The number of periods used in the EMA calculation. For example, a window of 10 with daily timespan produces a 10-day moving average. Defaults to 50 periods."),
    series_type: Literal["open", "high", "low", "close"] | None = Field(None, description="The price type used for EMA calculation: open, high, low, or close. Defaults to close price."),
    order: Literal["asc", "desc"] | None = Field(None, description="Sort order for results by timestamp. Use 'asc' for oldest first or 'desc' for newest first. Defaults to descending order."),
    limit: int | None = Field(None, description="Maximum number of results to return. Accepts values from 1 to 5000, with a default of 10 results.", le=5000),
) -> dict[str, Any] | ToolResult:
    """Calculate the exponential moving average (EMA) for a forex currency pair over a specified time range. Returns EMA values based on configurable aggregation periods and price series."""

    # Construct request model with validation
    try:
        _request = _models.ForexEmaRequest(
            path=_models.ForexEmaRequestPath(fx_ticker=fx_ticker),
            query=_models.ForexEmaRequestQuery(timespan=timespan, adjusted=adjusted, window=window, series_type=series_type, order=order, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_forex_ema: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/indicators/ema/{fxTicker}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/indicators/ema/{fxTicker}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_forex_ema")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_forex_ema", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_forex_ema",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: indices:aggregates
@mcp.tool()
async def get_exponential_moving_average(
    indices_ticker: str = Field(..., alias="indicesTicker", description="The ticker symbol for the index (e.g., I:NDX for Nasdaq-100). Required to identify which index to calculate EMA for."),
    timespan: Literal["minute", "hour", "day", "week", "month", "quarter", "year"] | None = Field(None, description="The time interval for aggregating data before calculating EMA. Choose from minute, hour, day, week, month, quarter, or year intervals. Defaults to daily aggregates."),
    adjusted: bool | None = Field(None, description="Whether to adjust aggregates for stock splits and dividends. Set to true (default) for split-adjusted results, or false for unadjusted raw data."),
    window: int | None = Field(None, description="The number of periods to use in the EMA calculation. For example, a window of 10 with daily timespan produces a 10-day moving average. Defaults to 50 periods."),
    series_type: Literal["open", "high", "low", "close"] | None = Field(None, description="Which price value to use for EMA calculation: open, high, low, or close. Defaults to close price."),
    order: Literal["asc", "desc"] | None = Field(None, description="Sort order for results by timestamp. Use 'asc' for oldest first or 'desc' for newest first. Defaults to descending (most recent first)."),
    limit: int | None = Field(None, description="Maximum number of results to return. Accepts 1 to 5000 results. Defaults to 10 results.", le=5000),
) -> dict[str, Any] | ToolResult:
    """Retrieve the exponential moving average (EMA) for an indices ticker over a specified time range. Use this to analyze trend direction and momentum for index symbols like NDX."""

    # Construct request model with validation
    try:
        _request = _models.IndicesEmaRequest(
            path=_models.IndicesEmaRequestPath(indices_ticker=indices_ticker),
            query=_models.IndicesEmaRequestQuery(timespan=timespan, adjusted=adjusted, window=window, series_type=series_type, order=order, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_exponential_moving_average: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/indicators/ema/{indicesTicker}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/indicators/ema/{indicesTicker}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_exponential_moving_average")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_exponential_moving_average", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_exponential_moving_average",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: options:aggregates
@mcp.tool()
async def get_ema_for_options_ticker(
    options_ticker: str = Field(..., alias="optionsTicker", description="The options ticker symbol to analyze, formatted as an options contract identifier (e.g., O:SPY241220P00720000)."),
    timespan: Literal["minute", "hour", "day", "week", "month", "quarter", "year"] | None = Field(None, description="The time interval for aggregating price data before calculating EMA. Choose from minute, hour, day, week, month, quarter, or year intervals. Defaults to daily aggregates."),
    adjusted: bool | None = Field(None, description="Whether to adjust aggregates for stock splits and dividends. Set to true (default) for split-adjusted results, or false for unadjusted raw data."),
    window: int | None = Field(None, description="The number of periods to use in the EMA calculation. For example, a window of 10 with daily timespan produces a 10-day moving average. Defaults to 50 periods."),
    series_type: Literal["open", "high", "low", "close"] | None = Field(None, description="The price type to use for EMA calculation: open, high, low, or close. Defaults to close price."),
    order: Literal["asc", "desc"] | None = Field(None, description="Sort order for results by timestamp. Use 'asc' for oldest first or 'desc' for newest first. Defaults to descending (most recent first)."),
    limit: int | None = Field(None, description="Maximum number of results to return. Accepts values from 1 to 5000, with a default of 10 results.", le=5000),
) -> dict[str, Any] | ToolResult:
    """Calculate and retrieve the exponential moving average (EMA) for an options ticker symbol over a specified time range. Use this to analyze price trends and momentum for options contracts."""

    # Construct request model with validation
    try:
        _request = _models.OptionsEmaRequest(
            path=_models.OptionsEmaRequestPath(options_ticker=options_ticker),
            query=_models.OptionsEmaRequestQuery(timespan=timespan, adjusted=adjusted, window=window, series_type=series_type, order=order, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_ema_for_options_ticker: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/indicators/ema/{optionsTicker}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/indicators/ema/{optionsTicker}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_ema_for_options_ticker")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_ema_for_options_ticker", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_ema_for_options_ticker",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: stocks:aggregates
@mcp.tool()
async def get_exponential_moving_average_stock(
    stock_ticker: str = Field(..., alias="stockTicker", description="The stock ticker symbol to retrieve EMA data for (case-sensitive). For example, AAPL for Apple Inc."),
    timespan: Literal["minute", "hour", "day", "week", "month", "quarter", "year"] | None = Field(None, description="The time interval for aggregating price data before calculating the EMA. Choose from minute, hour, day, week, month, quarter, or year intervals. Defaults to daily aggregates."),
    adjusted: bool | None = Field(None, description="Whether to adjust aggregates for stock splits and dividends. When true (default), results reflect adjusted prices; set to false for unadjusted data."),
    window: int | None = Field(None, description="The number of periods to use in the EMA calculation. For example, a window of 10 with daily aggregates produces a 10-day moving average. Defaults to 50 periods."),
    series_type: Literal["open", "high", "low", "close"] | None = Field(None, description="The price type used to calculate the EMA: open, high, low, or close. Defaults to using closing prices."),
    order: Literal["asc", "desc"] | None = Field(None, description="Sort order for results by timestamp. Use 'asc' for oldest first or 'desc' for newest first. Defaults to descending order."),
    limit: int | None = Field(None, description="Maximum number of results to return. Accepts values from 1 to 5000, with a default of 10 results.", le=5000),
) -> dict[str, Any] | ToolResult:
    """Retrieve the exponential moving average (EMA) for a stock ticker over a specified time range. The EMA is calculated based on aggregated price data at your chosen timespan interval."""

    # Construct request model with validation
    try:
        _request = _models.EmaRequest(
            path=_models.EmaRequestPath(stock_ticker=stock_ticker),
            query=_models.EmaRequestQuery(timespan=timespan, adjusted=adjusted, window=window, series_type=series_type, order=order, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_exponential_moving_average_stock: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/indicators/ema/{stockTicker}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/indicators/ema/{stockTicker}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_exponential_moving_average_stock")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_exponential_moving_average_stock", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_exponential_moving_average_stock",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: crypto:aggregates
@mcp.tool()
async def get_crypto_macd(
    crypto_ticker: str = Field(..., alias="cryptoTicker", description="The cryptocurrency ticker symbol (e.g., X:BTCUSD for Bitcoin in USD)."),
    timespan: Literal["minute", "hour", "day", "week", "month", "quarter", "year"] | None = Field(None, description="The time interval for each data point: minute, hour, day, week, month, quarter, or year. Defaults to daily aggregation."),
    short_window: int | None = Field(None, description="The number of periods for the short-term exponential moving average used in MACD calculation. Defaults to 12."),
    long_window: int | None = Field(None, description="The number of periods for the long-term exponential moving average used in MACD calculation. Defaults to 26."),
    signal_window: int | None = Field(None, description="The number of periods for the signal line (exponential moving average of MACD). Defaults to 9."),
    series_type: Literal["open", "high", "low", "close"] | None = Field(None, description="The price type to use for calculations: open, high, low, or close. Defaults to close price."),
    order: Literal["asc", "desc"] | None = Field(None, description="Sort order for results by timestamp: ascending (oldest first) or descending (newest first). Defaults to descending."),
    limit: int | None = Field(None, description="Maximum number of results to return. Defaults to 10, with a maximum of 5000.", le=5000),
) -> dict[str, Any] | ToolResult:
    """Retrieve Moving Average Convergence/Divergence (MACD) technical indicator data for a cryptocurrency ticker over a specified time range. MACD helps identify trend changes and momentum by comparing exponential moving averages."""

    # Construct request model with validation
    try:
        _request = _models.CryptoMacdRequest(
            path=_models.CryptoMacdRequestPath(crypto_ticker=crypto_ticker),
            query=_models.CryptoMacdRequestQuery(timespan=timespan, short_window=short_window, long_window=long_window, signal_window=signal_window, series_type=series_type, order=order, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_crypto_macd: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/indicators/macd/{cryptoTicker}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/indicators/macd/{cryptoTicker}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_crypto_macd")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_crypto_macd", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_crypto_macd",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: fx:aggregates
@mcp.tool()
async def get_macd_indicator_forex(
    fx_ticker: str = Field(..., alias="fxTicker", description="The forex ticker symbol to analyze (e.g., C:EURUSD for EUR/USD currency pair)."),
    timespan: Literal["minute", "hour", "day", "week", "month", "quarter", "year"] | None = Field(None, description="The time interval for aggregating price data: minute, hour, day, week, month, quarter, or year. Defaults to daily aggregates."),
    adjusted: bool | None = Field(None, description="Whether to adjust aggregates for stock splits and corporate actions. Enabled by default; set to false to use unadjusted prices."),
    short_window: int | None = Field(None, description="The number of periods for the short-term exponential moving average used in MACD calculation. Defaults to 12 periods."),
    long_window: int | None = Field(None, description="The number of periods for the long-term exponential moving average used in MACD calculation. Defaults to 26 periods."),
    signal_window: int | None = Field(None, description="The number of periods for calculating the MACD signal line (exponential moving average of MACD). Defaults to 9 periods."),
    series_type: Literal["open", "high", "low", "close"] | None = Field(None, description="The price type to use for MACD calculation: open, high, low, or close. Defaults to close price."),
    order: Literal["asc", "desc"] | None = Field(None, description="Sort order for results by timestamp: ascending (oldest first) or descending (newest first). Defaults to descending."),
    limit: int | None = Field(None, description="Maximum number of results to return. Defaults to 10; maximum allowed is 5000.", le=5000),
) -> dict[str, Any] | ToolResult:
    """Retrieve Moving Average Convergence/Divergence (MACD) indicator data for a forex ticker symbol. MACD is a momentum oscillator that measures the relationship between two exponential moving averages to identify trend direction and momentum shifts."""

    # Construct request model with validation
    try:
        _request = _models.ForexMacdRequest(
            path=_models.ForexMacdRequestPath(fx_ticker=fx_ticker),
            query=_models.ForexMacdRequestQuery(timespan=timespan, adjusted=adjusted, short_window=short_window, long_window=long_window, signal_window=signal_window, series_type=series_type, order=order, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_macd_indicator_forex: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/indicators/macd/{fxTicker}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/indicators/macd/{fxTicker}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_macd_indicator_forex")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_macd_indicator_forex", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_macd_indicator_forex",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: indices:aggregates
@mcp.tool()
async def get_macd_for_indices(
    indices_ticker: str = Field(..., alias="indicesTicker", description="The ticker symbol for the indices (e.g., I:NDX for Nasdaq-100). Required to identify which index to retrieve MACD data for."),
    timespan: Literal["minute", "hour", "day", "week", "month", "quarter", "year"] | None = Field(None, description="The time interval for aggregating price data before calculating MACD. Choose from minute, hour, day, week, month, quarter, or year intervals. Defaults to daily aggregation."),
    adjusted: bool | None = Field(None, description="Whether to adjust aggregated price data for stock splits and dividends. When true (default), results reflect adjusted prices; set to false for unadjusted data."),
    short_window: int | None = Field(None, description="The number of periods for the short-term exponential moving average used in MACD calculation. Defaults to 12 periods; lower values make the indicator more responsive to recent price changes."),
    long_window: int | None = Field(None, description="The number of periods for the long-term exponential moving average used in MACD calculation. Defaults to 26 periods; higher values smooth out short-term volatility."),
    signal_window: int | None = Field(None, description="The number of periods for calculating the MACD signal line, which is an exponential moving average of the MACD line itself. Defaults to 9 periods."),
    series_type: Literal["open", "high", "low", "close"] | None = Field(None, description="The price series to use for MACD calculation: open, high, low, or close. Defaults to close price, which is the most common choice for technical analysis."),
    order: Literal["asc", "desc"] | None = Field(None, description="Sort order for results by timestamp. Use 'asc' for oldest first or 'desc' for newest first. Defaults to descending order (most recent data first)."),
    limit: int | None = Field(None, description="Maximum number of MACD data points to return. Defaults to 10 results; can be increased up to 5000 for larger datasets.", le=5000),
) -> dict[str, Any] | ToolResult:
    """Retrieve Moving Average Convergence/Divergence (MACD) indicator values for an indices ticker over a specified time range. MACD is a momentum indicator that shows the relationship between two moving averages of price."""

    # Construct request model with validation
    try:
        _request = _models.IndicesMacdRequest(
            path=_models.IndicesMacdRequestPath(indices_ticker=indices_ticker),
            query=_models.IndicesMacdRequestQuery(timespan=timespan, adjusted=adjusted, short_window=short_window, long_window=long_window, signal_window=signal_window, series_type=series_type, order=order, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_macd_for_indices: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/indicators/macd/{indicesTicker}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/indicators/macd/{indicesTicker}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_macd_for_indices")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_macd_for_indices", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_macd_for_indices",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: options:aggregates
@mcp.tool()
async def get_macd_for_options_ticker(
    options_ticker: str = Field(..., alias="optionsTicker", description="The options ticker symbol to analyze, formatted as an options contract identifier (e.g., O:SPY241220P00720000)."),
    timespan: Literal["minute", "hour", "day", "week", "month", "quarter", "year"] | None = Field(None, description="The time interval for aggregating price data before calculating MACD. Choose from minute, hour, day, week, month, quarter, or year intervals. Defaults to daily aggregation."),
    adjusted: bool | None = Field(None, description="Whether to adjust price aggregates for stock splits before calculating MACD. When true (default), results reflect split-adjusted prices; set to false for unadjusted historical prices."),
    short_window: int | None = Field(None, description="The number of periods for the short-term exponential moving average in the MACD calculation. Defaults to 12 periods."),
    long_window: int | None = Field(None, description="The number of periods for the long-term exponential moving average in the MACD calculation. Defaults to 26 periods."),
    signal_window: int | None = Field(None, description="The number of periods for calculating the MACD signal line (exponential moving average of MACD values). Defaults to 9 periods."),
    series_type: Literal["open", "high", "low", "close"] | None = Field(None, description="The price type to use in MACD calculations: open, high, low, or close. Defaults to close price."),
    order: Literal["asc", "desc"] | None = Field(None, description="Sort order for results by timestamp: ascending (oldest first) or descending (newest first). Defaults to descending."),
    limit: int | None = Field(None, description="Maximum number of MACD data points to return. Defaults to 10; maximum allowed is 5000.", le=5000),
) -> dict[str, Any] | ToolResult:
    """Calculate and retrieve Moving Average Convergence/Divergence (MACD) indicator values for an options contract over a specified time range. MACD helps identify trend direction and momentum changes."""

    # Construct request model with validation
    try:
        _request = _models.OptionsMacdRequest(
            path=_models.OptionsMacdRequestPath(options_ticker=options_ticker),
            query=_models.OptionsMacdRequestQuery(timespan=timespan, adjusted=adjusted, short_window=short_window, long_window=long_window, signal_window=signal_window, series_type=series_type, order=order, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_macd_for_options_ticker: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/indicators/macd/{optionsTicker}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/indicators/macd/{optionsTicker}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_macd_for_options_ticker")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_macd_for_options_ticker", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_macd_for_options_ticker",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: stocks:aggregates
@mcp.tool()
async def get_macd_indicator(
    stock_ticker: str = Field(..., alias="stockTicker", description="The stock ticker symbol to retrieve MACD data for (case-sensitive). For example, AAPL for Apple Inc."),
    timespan: Literal["minute", "hour", "day", "week", "month", "quarter", "year"] | None = Field(None, description="The time interval for aggregating price data. Defaults to daily candles. Choose from minute, hour, day, week, month, quarter, or year."),
    adjusted: bool | None = Field(None, description="Whether to adjust aggregates for stock splits and dividends. Defaults to true for adjusted data; set to false for unadjusted prices."),
    short_window: int | None = Field(None, description="The number of periods for the short-term exponential moving average. Defaults to 12 periods."),
    long_window: int | None = Field(None, description="The number of periods for the long-term exponential moving average. Defaults to 26 periods."),
    signal_window: int | None = Field(None, description="The number of periods for calculating the MACD signal line (exponential moving average of MACD). Defaults to 9 periods."),
    series_type: Literal["open", "high", "low", "close"] | None = Field(None, description="The price type to use for MACD calculation: open, high, low, or close. Defaults to close price."),
    order: Literal["asc", "desc"] | None = Field(None, description="Sort order for results by timestamp. Use 'asc' for oldest first or 'desc' for newest first. Defaults to descending."),
    limit: int | None = Field(None, description="Maximum number of results to return. Defaults to 10; maximum allowed is 5000.", le=5000),
) -> dict[str, Any] | ToolResult:
    """Retrieve Moving Average Convergence/Divergence (MACD) technical indicator data for a stock ticker over a specified time range. MACD helps identify trend direction and momentum changes."""

    # Construct request model with validation
    try:
        _request = _models.MacdRequest(
            path=_models.MacdRequestPath(stock_ticker=stock_ticker),
            query=_models.MacdRequestQuery(timespan=timespan, adjusted=adjusted, short_window=short_window, long_window=long_window, signal_window=signal_window, series_type=series_type, order=order, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_macd_indicator: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/indicators/macd/{stockTicker}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/indicators/macd/{stockTicker}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_macd_indicator")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_macd_indicator", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_macd_indicator",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: crypto:aggregates
@mcp.tool()
async def get_crypto_rsi(
    crypto_ticker: str = Field(..., alias="cryptoTicker", description="The cryptocurrency ticker symbol (e.g., X:BTCUSD for Bitcoin/USD pair)."),
    timespan: Literal["minute", "hour", "day", "week", "month", "quarter", "year"] | None = Field(None, description="The time interval for aggregating price data. Defaults to daily aggregates. Choose from minute, hour, day, week, month, quarter, or year intervals."),
    window: int | None = Field(None, description="The number of periods used to calculate RSI. Defaults to 14 periods. A larger window smooths the indicator over a longer timeframe."),
    series_type: Literal["open", "high", "low", "close"] | None = Field(None, description="The price type used in RSI calculation. Defaults to closing price. Options are open, high, low, or close prices."),
    order: Literal["asc", "desc"] | None = Field(None, description="Sort order for results by timestamp. Defaults to descending (most recent first). Choose ascending for oldest-first ordering."),
    limit: int | None = Field(None, description="Maximum number of results to return. Defaults to 10, with a maximum of 5000 results per request.", le=5000),
) -> dict[str, Any] | ToolResult:
    """Retrieve the Relative Strength Index (RSI) indicator for a cryptocurrency ticker over a specified time range. RSI measures momentum on a scale of 0-100 to identify overbought or oversold conditions."""

    # Construct request model with validation
    try:
        _request = _models.CryptoRsiRequest(
            path=_models.CryptoRsiRequestPath(crypto_ticker=crypto_ticker),
            query=_models.CryptoRsiRequestQuery(timespan=timespan, window=window, series_type=series_type, order=order, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_crypto_rsi: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/indicators/rsi/{cryptoTicker}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/indicators/rsi/{cryptoTicker}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_crypto_rsi")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_crypto_rsi", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_crypto_rsi",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: fx:aggregates
@mcp.tool()
async def get_forex_rsi(
    fx_ticker: str = Field(..., alias="fxTicker", description="The forex ticker symbol to analyze, formatted as a currency pair (e.g., C:EURUSD for EUR/USD)."),
    timespan: Literal["minute", "hour", "day", "week", "month", "quarter", "year"] | None = Field(None, description="The time interval for each data point in the RSI calculation. Choose from minute, hour, day, week, month, quarter, or year intervals. Defaults to daily data."),
    adjusted: bool | None = Field(None, description="Whether to adjust price data for corporate actions like splits before calculating RSI. When true (default), uses adjusted prices; set to false for unadjusted prices."),
    window: int | None = Field(None, description="The number of periods used in the RSI calculation window. Defaults to 14 periods, which is the standard RSI lookback period."),
    series_type: Literal["open", "high", "low", "close"] | None = Field(None, description="Which price component to use for RSI calculation: open, high, low, or close. Defaults to close price, which is the most common choice."),
    order: Literal["asc", "desc"] | None = Field(None, description="Sort order for results by timestamp. Use 'asc' for oldest first or 'desc' for newest first. Defaults to descending (most recent first)."),
    limit: int | None = Field(None, description="Maximum number of RSI data points to return. Defaults to 10 results; maximum allowed is 5000.", le=5000),
) -> dict[str, Any] | ToolResult:
    """Calculate the Relative Strength Index (RSI) for a forex currency pair over a specified time range. RSI is a momentum oscillator that measures the magnitude of recent price changes to evaluate overbought or oversold conditions."""

    # Construct request model with validation
    try:
        _request = _models.ForexRsiRequest(
            path=_models.ForexRsiRequestPath(fx_ticker=fx_ticker),
            query=_models.ForexRsiRequestQuery(timespan=timespan, adjusted=adjusted, window=window, series_type=series_type, order=order, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_forex_rsi: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/indicators/rsi/{fxTicker}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/indicators/rsi/{fxTicker}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_forex_rsi")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_forex_rsi", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_forex_rsi",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: indices:aggregates
@mcp.tool()
async def get_rsi_for_indices(
    indices_ticker: str = Field(..., alias="indicesTicker", description="The ticker symbol for the indices (e.g., I:NDX for Nasdaq-100). Required to identify which index to analyze."),
    timespan: Literal["minute", "hour", "day", "week", "month", "quarter", "year"] | None = Field(None, description="The time interval for aggregating price data before calculating RSI. Defaults to daily candles. Choose from minute, hour, day, week, month, quarter, or year."),
    adjusted: bool | None = Field(None, description="Whether to adjust aggregates for stock splits before calculating RSI. Defaults to true (adjusted). Set to false to use unadjusted price data."),
    window: int | None = Field(None, description="The number of periods used in the RSI calculation window. Defaults to 14 periods. Larger values smooth the indicator; smaller values make it more responsive."),
    series_type: Literal["open", "high", "low", "close"] | None = Field(None, description="Which price component to use for RSI calculation: open, high, low, or close. Defaults to close price. Determines which value from each candle feeds into the RSI formula."),
    order: Literal["asc", "desc"] | None = Field(None, description="Sort order for results by timestamp. Use 'asc' for oldest first or 'desc' for newest first. Defaults to descending (most recent first)."),
    limit: int | None = Field(None, description="Maximum number of RSI data points to return. Defaults to 10, with a maximum of 5000 results per request.", le=5000),
) -> dict[str, Any] | ToolResult:
    """Calculate the Relative Strength Index (RSI) for an indices ticker over a specified time range. RSI is a momentum oscillator that measures the magnitude of recent price changes to evaluate overbought or oversold conditions."""

    # Construct request model with validation
    try:
        _request = _models.IndicesRsiRequest(
            path=_models.IndicesRsiRequestPath(indices_ticker=indices_ticker),
            query=_models.IndicesRsiRequestQuery(timespan=timespan, adjusted=adjusted, window=window, series_type=series_type, order=order, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_rsi_for_indices: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/indicators/rsi/{indicesTicker}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/indicators/rsi/{indicesTicker}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_rsi_for_indices")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_rsi_for_indices", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_rsi_for_indices",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: options:aggregates
@mcp.tool()
async def get_options_rsi(
    options_ticker: str = Field(..., alias="optionsTicker", description="The options ticker symbol in the format O:SYMBOL (e.g., O:SPY241220P00720000 for a specific options contract)."),
    timespan: Literal["minute", "hour", "day", "week", "month", "quarter", "year"] | None = Field(None, description="The time interval for aggregating price data before calculating RSI. Choose from minute, hour, day, week, month, quarter, or year intervals. Defaults to daily aggregation."),
    adjusted: bool | None = Field(None, description="Whether to adjust price aggregates for stock splits before calculating RSI. When true (default), results reflect split-adjusted prices; set to false for unadjusted historical prices."),
    window: int | None = Field(None, description="The number of periods used in the RSI calculation window. Defaults to 14 periods; larger values produce smoother, less sensitive indicators while smaller values increase sensitivity to recent price changes."),
    series_type: Literal["open", "high", "low", "close"] | None = Field(None, description="The price series to use for RSI calculation: open, high, low, or close. Defaults to close price, which is the most common choice for technical analysis."),
    order: Literal["asc", "desc"] | None = Field(None, description="Sort order for results by timestamp. Use 'asc' for oldest-first or 'desc' for newest-first (default)."),
    limit: int | None = Field(None, description="Maximum number of RSI data points to return. Defaults to 10; maximum allowed is 5000.", le=5000),
) -> dict[str, Any] | ToolResult:
    """Calculate the Relative Strength Index (RSI) for an options ticker symbol over a specified time range. RSI is a momentum oscillator that measures the magnitude of recent price changes to evaluate overbought or oversold conditions."""

    # Construct request model with validation
    try:
        _request = _models.OptionsRsiRequest(
            path=_models.OptionsRsiRequestPath(options_ticker=options_ticker),
            query=_models.OptionsRsiRequestQuery(timespan=timespan, adjusted=adjusted, window=window, series_type=series_type, order=order, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_options_rsi: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/indicators/rsi/{optionsTicker}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/indicators/rsi/{optionsTicker}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_options_rsi")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_options_rsi", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_options_rsi",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: stocks:aggregates
@mcp.tool()
async def get_rsi_for_stock(
    stock_ticker: str = Field(..., alias="stockTicker", description="The stock ticker symbol in uppercase (e.g., AAPL for Apple Inc.). This is case-sensitive."),
    timespan: Literal["minute", "hour", "day", "week", "month", "quarter", "year"] | None = Field(None, description="The time interval for aggregating price data before calculating RSI. Choose from minute, hour, day, week, month, quarter, or year intervals. Defaults to daily aggregation."),
    adjusted: bool | None = Field(None, description="Whether to adjust price aggregates for stock splits before calculating RSI. Defaults to true (adjusted). Set to false to use unadjusted prices."),
    window: int | None = Field(None, description="The number of periods used in the RSI calculation window. Defaults to 14 periods, which is the standard RSI lookback period."),
    series_type: Literal["open", "high", "low", "close"] | None = Field(None, description="Which price type to use for RSI calculation: open, high, low, or close. Defaults to close price, which is the most common choice."),
    order: Literal["asc", "desc"] | None = Field(None, description="Sort order for results by timestamp. Use 'asc' for oldest first or 'desc' for newest first. Defaults to descending (most recent first)."),
    limit: int | None = Field(None, description="Maximum number of RSI data points to return. Defaults to 10, with a maximum of 5000 results per request.", le=5000),
) -> dict[str, Any] | ToolResult:
    """Calculate the Relative Strength Index (RSI) momentum indicator for a stock ticker over a specified time range. RSI measures the magnitude of recent price changes to evaluate overbought or oversold conditions."""

    # Construct request model with validation
    try:
        _request = _models.RsiRequest(
            path=_models.RsiRequestPath(stock_ticker=stock_ticker),
            query=_models.RsiRequestQuery(timespan=timespan, adjusted=adjusted, window=window, series_type=series_type, order=order, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_rsi_for_stock: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/indicators/rsi/{stockTicker}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/indicators/rsi/{stockTicker}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_rsi_for_stock")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_rsi_for_stock", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_rsi_for_stock",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: crypto:aggregates
@mcp.tool()
async def get_crypto_simple_moving_average(
    crypto_ticker: str = Field(..., alias="cryptoTicker", description="The cryptocurrency ticker symbol to analyze (e.g., X:BTCUSD for Bitcoin in USD)."),
    timespan: Literal["minute", "hour", "day", "week", "month", "quarter", "year"] | None = Field(None, description="The time interval for aggregating price data before calculating the moving average. Choose from minute, hour, day, week, month, quarter, or year intervals. Defaults to daily aggregates."),
    window: int | None = Field(None, description="The number of periods to include in the moving average calculation. For example, a window of 10 with daily aggregates produces a 10-day moving average. Defaults to 50 periods."),
    series_type: Literal["open", "high", "low", "close"] | None = Field(None, description="The price type used in the SMA calculation: open, high, low, or close price. Defaults to using closing prices."),
    order: Literal["asc", "desc"] | None = Field(None, description="Sort order for results by timestamp: ascending (oldest first) or descending (newest first). Defaults to descending order."),
    limit: int | None = Field(None, description="Maximum number of results to return. Accepts values from 1 to 5000, with a default of 10 results.", le=5000),
) -> dict[str, Any] | ToolResult:
    """Calculate the simple moving average (SMA) for a cryptocurrency ticker over a specified time range. Returns SMA values computed from historical price data aggregated at your chosen interval."""

    # Construct request model with validation
    try:
        _request = _models.CryptoSmaRequest(
            path=_models.CryptoSmaRequestPath(crypto_ticker=crypto_ticker),
            query=_models.CryptoSmaRequestQuery(timespan=timespan, window=window, series_type=series_type, order=order, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_crypto_simple_moving_average: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/indicators/sma/{cryptoTicker}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/indicators/sma/{cryptoTicker}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_crypto_simple_moving_average")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_crypto_simple_moving_average", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_crypto_simple_moving_average",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: fx:aggregates
@mcp.tool()
async def get_forex_simple_moving_average(
    fx_ticker: str = Field(..., alias="fxTicker", description="The forex ticker symbol to analyze, formatted as a currency pair (e.g., C:EURUSD for EUR/USD)."),
    timespan: Literal["minute", "hour", "day", "week", "month", "quarter", "year"] | None = Field(None, description="The time interval for aggregating price data before calculating the moving average. Choose from minute, hour, day, week, month, quarter, or year intervals. Defaults to daily aggregates."),
    adjusted: bool | None = Field(None, description="Whether to adjust aggregates for corporate actions like splits. When true (default), results reflect adjusted prices; set to false for unadjusted historical prices."),
    window: int | None = Field(None, description="The number of periods to include in the moving average calculation. For example, a window of 10 with daily timespan produces a 10-day moving average. Defaults to 50 periods."),
    series_type: Literal["open", "high", "low", "close"] | None = Field(None, description="The price type used in the SMA calculation: open, high, low, or close. Defaults to close price."),
    order: Literal["asc", "desc"] | None = Field(None, description="Sort order for results by timestamp. Use 'asc' for oldest first or 'desc' for newest first. Defaults to descending order."),
    limit: int | None = Field(None, description="Maximum number of SMA values to return. Accepts 1 to 5000 results, with a default of 10.", le=5000),
) -> dict[str, Any] | ToolResult:
    """Calculate the simple moving average (SMA) for a forex currency pair over a specified time range. Returns SMA values based on configurable window size, price series, and time aggregation."""

    # Construct request model with validation
    try:
        _request = _models.ForexSmaRequest(
            path=_models.ForexSmaRequestPath(fx_ticker=fx_ticker),
            query=_models.ForexSmaRequestQuery(timespan=timespan, adjusted=adjusted, window=window, series_type=series_type, order=order, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_forex_simple_moving_average: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/indicators/sma/{fxTicker}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/indicators/sma/{fxTicker}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_forex_simple_moving_average")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_forex_simple_moving_average", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_forex_simple_moving_average",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: indices:aggregates
@mcp.tool()
async def get_sma_for_indices(
    indices_ticker: str = Field(..., alias="indicesTicker", description="The ticker symbol for the indices instrument (e.g., I:NDX for Nasdaq-100). Required to identify which index to calculate SMA for."),
    timespan: Literal["minute", "hour", "day", "week", "month", "quarter", "year"] | None = Field(None, description="The time interval for aggregating data before calculating SMA. Choose from minute, hour, day, week, month, quarter, or year. Defaults to daily aggregates."),
    adjusted: bool | None = Field(None, description="Whether to adjust aggregates for stock splits and dividends. Set to true (default) for split-adjusted results, or false for unadjusted data."),
    window: int | None = Field(None, description="The number of periods to include in the moving average calculation. For example, a window of 10 with daily timespan produces a 10-day SMA. Defaults to 50 periods."),
    series_type: Literal["open", "high", "low", "close"] | None = Field(None, description="The price type to use for SMA calculation: open, high, low, or close. Defaults to close price."),
    order: Literal["asc", "desc"] | None = Field(None, description="Sort order for results by timestamp. Use 'asc' for oldest first or 'desc' for newest first. Defaults to descending (most recent first)."),
    limit: int | None = Field(None, description="Maximum number of SMA data points to return. Accepts 1 to 5000 results. Defaults to 10.", le=5000),
) -> dict[str, Any] | ToolResult:
    """Retrieve the simple moving average (SMA) for an indices ticker symbol over a specified time range. Use this to analyze trend direction and momentum for index instruments like the Nasdaq-100."""

    # Construct request model with validation
    try:
        _request = _models.IndicesSmaRequest(
            path=_models.IndicesSmaRequestPath(indices_ticker=indices_ticker),
            query=_models.IndicesSmaRequestQuery(timespan=timespan, adjusted=adjusted, window=window, series_type=series_type, order=order, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_sma_for_indices: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/indicators/sma/{indicesTicker}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/indicators/sma/{indicesTicker}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_sma_for_indices")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_sma_for_indices", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_sma_for_indices",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: options:aggregates
@mcp.tool()
async def get_sma_for_options_ticker(
    options_ticker: str = Field(..., alias="optionsTicker", description="The options ticker symbol to analyze (e.g., O:SPY241220P00720000 for a specific options contract)."),
    timespan: Literal["minute", "hour", "day", "week", "month", "quarter", "year"] | None = Field(None, description="The time interval for aggregating price data before calculating the moving average. Choose from minute, hour, day, week, month, quarter, or year intervals. Defaults to daily aggregates."),
    adjusted: bool | None = Field(None, description="Whether to adjust aggregates for stock splits and dividends. Set to true (default) for split-adjusted results, or false for unadjusted data."),
    window: int | None = Field(None, description="The number of periods to include in the moving average calculation. For example, a window of 10 with daily timespan produces a 10-day moving average. Defaults to 50 periods."),
    series_type: Literal["open", "high", "low", "close"] | None = Field(None, description="The price type used in the SMA calculation: open, high, low, or close price. Defaults to close price."),
    order: Literal["asc", "desc"] | None = Field(None, description="Sort order for results by timestamp: ascending (oldest first) or descending (newest first). Defaults to descending."),
    limit: int | None = Field(None, description="Maximum number of results to return. Accepts values from 1 to 5000, with a default of 10.", le=5000),
) -> dict[str, Any] | ToolResult:
    """Calculate the simple moving average (SMA) for an options ticker symbol over a specified time range. Returns SMA values based on configurable aggregation periods, price series, and window sizes."""

    # Construct request model with validation
    try:
        _request = _models.OptionsSmaRequest(
            path=_models.OptionsSmaRequestPath(options_ticker=options_ticker),
            query=_models.OptionsSmaRequestQuery(timespan=timespan, adjusted=adjusted, window=window, series_type=series_type, order=order, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_sma_for_options_ticker: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/indicators/sma/{optionsTicker}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/indicators/sma/{optionsTicker}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_sma_for_options_ticker")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_sma_for_options_ticker", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_sma_for_options_ticker",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: stocks:aggregates
@mcp.tool()
async def get_simple_moving_average(
    stock_ticker: str = Field(..., alias="stockTicker", description="The stock ticker symbol to retrieve SMA data for (case-sensitive, e.g., AAPL for Apple Inc.)."),
    timespan: Literal["minute", "hour", "day", "week", "month", "quarter", "year"] | None = Field(None, description="The time interval for aggregating price data before calculating the moving average. Options include minute, hour, day, week, month, quarter, or year intervals. Defaults to daily aggregates."),
    adjusted: bool | None = Field(None, description="Whether to adjust aggregate prices for stock splits and dividends. When true (default), prices are adjusted; set to false to use unadjusted prices."),
    window: int | None = Field(None, description="The number of periods to include in the moving average calculation. For example, a window of 10 with daily aggregates produces a 10-day moving average. Defaults to 50 periods."),
    series_type: Literal["open", "high", "low", "close"] | None = Field(None, description="The price type to use for SMA calculation: open, high, low, or close. Defaults to using closing prices."),
    order: Literal["asc", "desc"] | None = Field(None, description="Sort order for results by timestamp: ascending (oldest first) or descending (newest first). Defaults to descending order."),
    limit: int | None = Field(None, description="Maximum number of results to return. Defaults to 10; maximum allowed is 5000.", le=5000),
) -> dict[str, Any] | ToolResult:
    """Calculate the simple moving average (SMA) for a stock ticker over a specified time range and aggregation period. Returns SMA values ordered by timestamp to track price trends."""

    # Construct request model with validation
    try:
        _request = _models.SmaRequest(
            path=_models.SmaRequestPath(stock_ticker=stock_ticker),
            query=_models.SmaRequestQuery(timespan=timespan, adjusted=adjusted, window=window, series_type=series_type, order=order, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_simple_moving_average: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/indicators/sma/{stockTicker}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/indicators/sma/{stockTicker}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_simple_moving_average")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_simple_moving_average", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_simple_moving_average",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: crypto:last:trade
@mcp.tool()
async def get_last_trade_for_crypto_pair(
    from_: str = Field(..., alias="from", description="The source cryptocurrency symbol (e.g., BTC for Bitcoin). Use the standard ticker symbol for the cryptocurrency you want to trade from."),
    to: str = Field(..., description="The target currency or cryptocurrency symbol (e.g., USD for US Dollar). Use the standard ticker symbol for the currency you want to trade to."),
) -> dict[str, Any] | ToolResult:
    """Retrieve the most recent trade tick for a specified cryptocurrency pair. Returns the latest executed trade data including price and timestamp for the given from/to currency combination."""

    # Construct request model with validation
    try:
        _request = _models.LastTradeCryptoRequest(
            path=_models.LastTradeCryptoRequestPath(from_=from_, to=to)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_last_trade_for_crypto_pair: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/last/crypto/{from}/{to}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/last/crypto/{from}/{to}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_last_trade_for_crypto_pair")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_last_trade_for_crypto_pair", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_last_trade_for_crypto_pair",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: fx:last:quote
@mcp.tool()
async def get_last_quote_for_currency_pair(
    from_: str = Field(..., alias="from", description="The source currency symbol (ISO 4217 code) for the currency pair conversion, such as AUD for Australian Dollar."),
    to: str = Field(..., description="The target currency symbol (ISO 4217 code) to convert into, such as USD for US Dollar."),
) -> dict[str, Any] | ToolResult:
    """Retrieve the most recent exchange rate quote for a specified forex currency pair. Returns the latest tick data for converting between two currencies."""

    # Construct request model with validation
    try:
        _request = _models.LastQuoteCurrenciesRequest(
            path=_models.LastQuoteCurrenciesRequestPath(from_=from_, to=to)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_last_quote_for_currency_pair: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/last_quote/currencies/{from}/{to}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/last_quote/currencies/{from}/{to}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_last_quote_for_currency_pair")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_last_quote_for_currency_pair", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_last_quote_for_currency_pair",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: reference:stocks:market
@mcp.tool()
async def get_market_status() -> dict[str, Any] | ToolResult:
    """Retrieve the current trading status of all exchanges and overall financial markets, including whether markets are open, closed, or in pre/post-trading sessions."""

    # Extract parameters for API call
    _http_path = "/v1/marketstatus/now"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_market_status")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_market_status", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_market_status",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: reference:stocks:market
@mcp.tool()
async def list_market_holidays() -> dict[str, Any] | ToolResult:
    """Retrieve a list of upcoming market holidays with their corresponding market open and close times. Use this to identify when markets will be closed or have modified trading hours."""

    # Extract parameters for API call
    _http_path = "/v1/marketstatus/upcoming"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_market_holidays")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_market_holidays", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_market_holidays",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: crypto:open-close
@mcp.tool()
async def get_crypto_daily_open_close(
    from_: str = Field(..., alias="from", description="The base cryptocurrency symbol of the trading pair (e.g., BTC for Bitcoin)."),
    to: str = Field(..., description="The quote currency symbol of the trading pair (e.g., USD for US Dollar)."),
    date: str = Field(..., description="The date for which to retrieve open/close prices, formatted as YYYY-MM-DD."),
    adjusted: bool | None = Field(None, description="Whether to return split-adjusted prices. Defaults to true for adjusted results; set to false to retrieve unadjusted prices."),
) -> dict[str, Any] | ToolResult:
    """Retrieve the opening and closing prices for a cryptocurrency trading pair on a specific date. Prices are adjusted for splits by default."""

    # Construct request model with validation
    try:
        _request = _models.GetCryptoOpenCloseRequest(
            path=_models.GetCryptoOpenCloseRequestPath(from_=from_, to=to, date=date),
            query=_models.GetCryptoOpenCloseRequestQuery(adjusted=adjusted)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_crypto_daily_open_close: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/open-close/crypto/{from}/{to}/{date}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/open-close/crypto/{from}/{to}/{date}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_crypto_daily_open_close")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_crypto_daily_open_close", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_crypto_daily_open_close",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: stocks:open-close
@mcp.tool()
async def get_index_open_close(
    indices_ticker: str = Field(..., alias="indicesTicker", description="The ticker symbol of the index to query, prefixed with 'I:' (e.g., I:NDX for Nasdaq-100)."),
    date: str = Field(..., description="The date for which to retrieve open/close data, formatted as YYYY-MM-DD (e.g., 2023-03-10)."),
) -> dict[str, Any] | ToolResult:
    """Retrieve the opening, closing, and after-hours prices for an index on a specific date. Useful for analyzing daily price movements and market hours performance."""

    # Construct request model with validation
    try:
        _request = _models.GetIndicesOpenCloseRequest(
            path=_models.GetIndicesOpenCloseRequestPath(indices_ticker=indices_ticker, date=date)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_index_open_close: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/open-close/{indicesTicker}/{date}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/open-close/{indicesTicker}/{date}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_index_open_close")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_index_open_close", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_index_open_close",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: options:open-close
@mcp.tool()
async def get_options_daily_open_close(
    options_ticker: str = Field(..., alias="optionsTicker", description="The options contract ticker symbol in the format O:UNDERLYING[EXPIRATION][TYPE][STRIKE] (e.g., O:SPY251219C00650000 for SPY call option expiring December 19, 2025 with $650 strike)."),
    date: str = Field(..., description="The date for which to retrieve open/close data, formatted as YYYY-MM-DD (e.g., 2023-01-09)."),
    adjusted: bool | None = Field(None, description="Whether to adjust results for stock splits. Defaults to true (adjusted); set to false to retrieve unadjusted prices."),
) -> dict[str, Any] | ToolResult:
    """Retrieve the open, close, and after-hours prices for a specific options contract on a given date."""

    # Construct request model with validation
    try:
        _request = _models.GetOptionsOpenCloseRequest(
            path=_models.GetOptionsOpenCloseRequestPath(options_ticker=options_ticker, date=date),
            query=_models.GetOptionsOpenCloseRequestQuery(adjusted=adjusted)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_options_daily_open_close: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/open-close/{optionsTicker}/{date}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/open-close/{optionsTicker}/{date}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_options_daily_open_close")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_options_daily_open_close", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_options_daily_open_close",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: stocks:open-close
@mcp.tool()
async def get_stock_daily_open_close(
    stocks_ticker: str = Field(..., alias="stocksTicker", description="The stock ticker symbol in uppercase (e.g., AAPL for Apple Inc.). Must be case-sensitive and match the official exchange listing."),
    date: str = Field(..., description="The date for which to retrieve pricing data, formatted as YYYY-MM-DD (e.g., 2023-01-09)."),
    adjusted: bool | None = Field(None, description="Whether to adjust prices for stock splits. When true (default), prices reflect split adjustments; set to false to retrieve unadjusted historical prices."),
) -> dict[str, Any] | ToolResult:
    """Retrieve the opening, closing, and after-hours prices for a stock on a specific date. Results are adjusted for stock splits by default."""

    # Construct request model with validation
    try:
        _request = _models.GetStocksOpenCloseRequest(
            path=_models.GetStocksOpenCloseRequestPath(stocks_ticker=stocks_ticker, date=date),
            query=_models.GetStocksOpenCloseRequestQuery(adjusted=adjusted)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_stock_daily_open_close: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/open-close/{stocksTicker}/{date}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/open-close/{stocksTicker}/{date}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_stock_daily_open_close")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_stock_daily_open_close", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_stock_daily_open_close",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: reference:sec:filings
@mcp.tool()
async def list_sec_filings_reference(
    has_xbrl: bool | None = Field(None, description="Filter filings by XBRL instance file availability. When true, returns only filings with XBRL data; when false, returns only filings without XBRL data; when omitted, returns all filings regardless of XBRL status."),
    entities_company_data_cik: str | None = Field(None, alias="entities.company_data.cik", description="Filter filings by the company's Central Index Key (CIK), a unique SEC identifier."),
    entities_company_data_ticker: str | None = Field(None, alias="entities.company_data.ticker", description="Filter filings by the company's stock ticker symbol."),
    entities_company_data_sic: str | None = Field(None, alias="entities.company_data.sic", description="Filter filings by the company's Standard Industrial Classification (SIC) code."),
    period_of_report_date_gte: str | None = Field(None, alias="period_of_report_date.gte", description="Return filings with a period of report date greater than or equal to this date. Use YYYYMMDD format (e.g., 20210101 for January 1, 2021).", pattern="^[0-9]{8}$"),
    period_of_report_date_gt: str | None = Field(None, alias="period_of_report_date.gt", description="Return filings with a period of report date strictly greater than this date. Use YYYYMMDD format (e.g., 20210101 for January 1, 2021).", pattern="^[0-9]{8}$"),
    period_of_report_date_lte: str | None = Field(None, alias="period_of_report_date.lte", description="Return filings with a period of report date less than or equal to this date. Use YYYYMMDD format (e.g., 20210101 for January 1, 2021).", pattern="^[0-9]{8}$"),
    period_of_report_date_lt: str | None = Field(None, alias="period_of_report_date.lt", description="Return filings with a period of report date strictly less than this date. Use YYYYMMDD format (e.g., 20210101 for January 1, 2021).", pattern="^[0-9]{8}$"),
    entities_company_data_name_search: str | None = Field(None, alias="entities.company_data.name.search", description="Search filings by company name using text matching."),
    order: Literal["asc", "desc"] | None = Field(None, description="Sort results in ascending or descending order based on the selected sort field."),
    limit: int | None = Field(None, description="Maximum number of filings to return per request. Defaults to 10; maximum allowed is 1000.", ge=1, le=1000),
    sort: Literal["filing_date", "period_of_report_date"] | None = Field(None, description="Field to sort results by. Choose filing_date for the date the filing was submitted, or period_of_report_date for the reporting period end date. Defaults to filing_date."),
) -> dict[str, Any] | ToolResult:
    """Retrieve SEC filings with flexible filtering by company identifiers, reporting dates, and XBRL availability. Results can be sorted and paginated for efficient data retrieval."""

    # Construct request model with validation
    try:
        _request = _models.ListFilingsRequest(
            query=_models.ListFilingsRequestQuery(has_xbrl=has_xbrl, entities_company_data_cik=entities_company_data_cik, entities_company_data_ticker=entities_company_data_ticker, entities_company_data_sic=entities_company_data_sic, period_of_report_date_gte=period_of_report_date_gte, period_of_report_date_gt=period_of_report_date_gt, period_of_report_date_lte=period_of_report_date_lte, period_of_report_date_lt=period_of_report_date_lt, entities_company_data_name_search=entities_company_data_name_search, order=order, limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_sec_filings_reference: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/reference/sec/filings"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_sec_filings_reference")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_sec_filings_reference", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_sec_filings_reference",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: reference:sec:filing
@mcp.tool()
async def get_filing(filing_id: str = Field(..., description="The unique identifier for the SEC filing to retrieve. This ID corresponds to a specific filing record in the SEC database.")) -> dict[str, Any] | ToolResult:
    """Retrieve a specific SEC filing document by its unique filing identifier. Returns detailed filing information from the Securities and Exchange Commission database."""

    # Construct request model with validation
    try:
        _request = _models.GetFilingRequest(
            path=_models.GetFilingRequestPath(filing_id=filing_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_filing: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/reference/sec/filings/{filing_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/reference/sec/filings/{filing_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_filing")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_filing", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_filing",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: reference:sec:filing:files
@mcp.tool()
async def list_filing_files(
    filing_id: str = Field(..., description="The unique identifier of the SEC filing for which to retrieve associated files."),
    sequence_gte: str | None = Field(None, alias="sequence.gte", description="Filter results to include only files with a sequence number greater than or equal to this value. Sequence numbers range from 1 to 999."),
    sequence_gt: str | None = Field(None, alias="sequence.gt", description="Filter results to include only files with a sequence number strictly greater than this value. Sequence numbers range from 1 to 999."),
    sequence_lte: str | None = Field(None, alias="sequence.lte", description="Filter results to include only files with a sequence number less than or equal to this value. Sequence numbers range from 1 to 999."),
    sequence_lt: str | None = Field(None, alias="sequence.lt", description="Filter results to include only files with a sequence number strictly less than this value. Sequence numbers range from 1 to 999."),
    filename_gte: str | None = Field(None, alias="filename.gte", description="Filter results to include only files with a filename greater than or equal to this value (lexicographic comparison)."),
    filename_gt: str | None = Field(None, alias="filename.gt", description="Filter results to include only files with a filename strictly greater than this value (lexicographic comparison)."),
    filename_lte: str | None = Field(None, alias="filename.lte", description="Filter results to include only files with a filename less than or equal to this value (lexicographic comparison)."),
    filename_lt: str | None = Field(None, alias="filename.lt", description="Filter results to include only files with a filename strictly less than this value (lexicographic comparison)."),
    order: Literal["asc", "desc"] | None = Field(None, description="Sort direction for results: 'asc' for ascending or 'desc' for descending order based on the selected sort field."),
    limit: int | None = Field(None, description="Maximum number of results to return per request. Defaults to 10 if not specified; maximum allowed is 1000.", ge=1, le=1000),
    sort: Literal["sequence", "filename"] | None = Field(None, description="Field to sort results by: 'sequence' (default) sorts by file sequence number, or 'filename' sorts alphabetically by filename."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a list of files associated with a specific SEC filing. Results can be filtered by sequence number or filename, and sorted by either field in ascending or descending order."""

    _sequence_gte = _parse_int(sequence_gte)
    _sequence_gt = _parse_int(sequence_gt)
    _sequence_lte = _parse_int(sequence_lte)
    _sequence_lt = _parse_int(sequence_lt)

    # Construct request model with validation
    try:
        _request = _models.ListFilingFilesRequest(
            path=_models.ListFilingFilesRequestPath(filing_id=filing_id),
            query=_models.ListFilingFilesRequestQuery(sequence_gte=_sequence_gte, sequence_gt=_sequence_gt, sequence_lte=_sequence_lte, sequence_lt=_sequence_lt, filename_gte=filename_gte, filename_gt=filename_gt, filename_lte=filename_lte, filename_lt=filename_lt, order=order, limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_filing_files: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/reference/sec/filings/{filing_id}/files", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/reference/sec/filings/{filing_id}/files"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_filing_files")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_filing_files", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_filing_files",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: reference:sec:filing:file
@mcp.tool()
async def get_sec_filing_file(
    filing_id: str = Field(..., description="The unique identifier of the SEC filing. This ID specifies which filing submission to retrieve the file from."),
    file_id: str = Field(..., description="The unique identifier of the specific file within the filing. This ID pinpoints the exact document or exhibit to retrieve (e.g., '1' for the first file)."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a specific file from an SEC filing by its filing ID and file ID. Use this to access individual documents or exhibits within a complete SEC filing submission."""

    # Construct request model with validation
    try:
        _request = _models.GetFilingFileRequest(
            path=_models.GetFilingFileRequestPath(filing_id=filing_id, file_id=file_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_sec_filing_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/reference/sec/filings/{filing_id}/files/{file_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/reference/sec/filings/{filing_id}/files/{file_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_sec_filing_file")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_sec_filing_file", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_sec_filing_file",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: reference:related:companies
@mcp.tool()
async def list_related_companies(ticker: str = Field(..., description="The stock ticker symbol to find related companies for (e.g., AAPL for Apple Inc.)")) -> dict[str, Any] | ToolResult:
    """Retrieve a list of company tickers related to a given ticker symbol, identified through analysis of news coverage and stock return patterns."""

    # Construct request model with validation
    try:
        _request = _models.GetRelatedCompaniesRequest(
            path=_models.GetRelatedCompaniesRequestPath(ticker=ticker)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_related_companies: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/related-companies/{ticker}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/related-companies/{ticker}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_related_companies")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_related_companies", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_related_companies",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool()
async def get_ticker_summaries() -> dict[str, Any] | ToolResult:
    """Retrieve tick-by-tick movement summaries for all tickers, providing all data needed to visualize price and volume changes."""

    # Extract parameters for API call
    _http_path = "/v1/summaries"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_ticker_summaries")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_ticker_summaries", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_ticker_summaries",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: crypto:aggregates
@mcp.tool()
async def get_grouped_crypto_aggregates(
    date: str = Field(..., description="The date for which to retrieve cryptocurrency market aggregates, formatted as YYYY-MM-DD (e.g., 2025-11-03)."),
    adjusted: bool | None = Field(None, description="Whether to adjust results for splits. Set to true (default) for split-adjusted prices, or false to receive unadjusted data."),
) -> dict[str, Any] | ToolResult:
    """Retrieve daily OHLC (open, high, low, close) price aggregates for the entire cryptocurrency market on a specified date. Results are adjusted for splits by default."""

    # Construct request model with validation
    try:
        _request = _models.GetGroupedCryptoAggregatesRequest(
            path=_models.GetGroupedCryptoAggregatesRequestPath(date=date),
            query=_models.GetGroupedCryptoAggregatesRequestQuery(adjusted=adjusted)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_grouped_crypto_aggregates: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/aggs/grouped/locale/global/market/crypto/{date}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/aggs/grouped/locale/global/market/crypto/{date}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_grouped_crypto_aggregates")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_grouped_crypto_aggregates", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_grouped_crypto_aggregates",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: fx:aggregates
@mcp.tool()
async def get_grouped_forex_aggregates(
    date: str = Field(..., description="The date for which to retrieve forex market aggregates, formatted as YYYY-MM-DD (e.g., 2025-11-03)."),
    adjusted: bool | None = Field(None, description="Whether to return split-adjusted results. Defaults to true for adjusted data; set to false to retrieve unadjusted values."),
) -> dict[str, Any] | ToolResult:
    """Retrieve daily OHLC (open, high, low, close) aggregated data for all forex currency pairs on a specified date. Results are adjusted for splits by default."""

    # Construct request model with validation
    try:
        _request = _models.GetGroupedForexAggregatesRequest(
            path=_models.GetGroupedForexAggregatesRequestPath(date=date),
            query=_models.GetGroupedForexAggregatesRequestQuery(adjusted=adjusted)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_grouped_forex_aggregates: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/aggs/grouped/locale/global/market/fx/{date}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/aggs/grouped/locale/global/market/fx/{date}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_grouped_forex_aggregates")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_grouped_forex_aggregates", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_grouped_forex_aggregates",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: stocks:aggregates
@mcp.tool()
async def get_grouped_stocks_aggregates(
    date: str = Field(..., description="The date for which to retrieve market aggregates, formatted as YYYY-MM-DD (e.g., 2025-11-03)."),
    adjusted: bool | None = Field(None, description="Whether to return split-adjusted prices. Defaults to true; set to false to retrieve unadjusted data."),
    include_otc: bool | None = Field(None, description="Whether to include over-the-counter (OTC) securities in the results. Defaults to false."),
) -> dict[str, Any] | ToolResult:
    """Retrieve daily OHLC (open, high, low, close) aggregate data for the entire US equities market on a specified date. Results are adjusted for splits by default."""

    # Construct request model with validation
    try:
        _request = _models.GetGroupedStocksAggregatesRequest(
            path=_models.GetGroupedStocksAggregatesRequestPath(date=date),
            query=_models.GetGroupedStocksAggregatesRequestQuery(adjusted=adjusted, include_otc=include_otc)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_grouped_stocks_aggregates: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/aggs/grouped/locale/us/market/stocks/{date}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/aggs/grouped/locale/us/market/stocks/{date}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_grouped_stocks_aggregates")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_grouped_stocks_aggregates", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_grouped_stocks_aggregates",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: crypto:aggregates
@mcp.tool()
async def get_previous_crypto_aggregates(
    crypto_ticker: str = Field(..., alias="cryptoTicker", description="The ticker symbol representing the cryptocurrency pair (e.g., X:BTCUSD for Bitcoin to US Dollar)."),
    adjusted: bool | None = Field(None, description="Whether to return split-adjusted results. Defaults to true for adjusted data; set to false to retrieve unadjusted historical prices."),
) -> dict[str, Any] | ToolResult:
    """Retrieve the previous trading day's OHLC (open, high, low, close) data for a specified cryptocurrency pair. Use this to analyze the prior day's price movement and market range."""

    # Construct request model with validation
    try:
        _request = _models.GetPreviousCryptoAggregatesRequest(
            path=_models.GetPreviousCryptoAggregatesRequestPath(crypto_ticker=crypto_ticker),
            query=_models.GetPreviousCryptoAggregatesRequestQuery(adjusted=adjusted)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_previous_crypto_aggregates: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/aggs/ticker/{cryptoTicker}/prev", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/aggs/ticker/{cryptoTicker}/prev"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_previous_crypto_aggregates")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_previous_crypto_aggregates", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_previous_crypto_aggregates",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: crypto:aggregates
@mcp.tool()
async def get_crypto_aggregates(
    crypto_ticker: str = Field(..., alias="cryptoTicker", description="The cryptocurrency pair ticker symbol (e.g., X:BTCUSD for Bitcoin/USD)."),
    multiplier: int = Field(..., description="The multiplier for the timespan unit. Must be a positive integer that scales the timespan (e.g., multiplier=5 with timespan='minute' produces 5-minute bars)."),
    timespan: Literal["second", "minute", "hour", "day", "week", "month", "quarter", "year"] = Field(..., description="The unit of time for each aggregate bar. Choose from: second, minute, hour, day, week, month, quarter, or year."),
    from_: str = Field(..., alias="from", description="The start of the time window for aggregates. Provide either a date in YYYY-MM-DD format or a millisecond Unix timestamp."),
    to: str = Field(..., description="The end of the time window for aggregates. Provide either a date in YYYY-MM-DD format or a millisecond Unix timestamp."),
    adjusted: bool | None = Field(None, description="Whether to adjust results for stock splits. Defaults to true (adjusted). Set to false to retrieve unadjusted data."),
    sort: Literal["asc", "desc"] | None = Field(None, description="Sort order for results by timestamp. Use 'asc' for oldest-first or 'desc' for newest-first ordering."),
    limit: int | None = Field(None, description="Maximum number of base aggregates to query for creating results. Accepts values up to 50,000; defaults to 5,000 if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve aggregate bars (OHLCV data) for a cryptocurrency pair over a specified date range with customizable time window sizes. For example, use multiplier=5 with timespan='minute' to get 5-minute bars."""

    # Construct request model with validation
    try:
        _request = _models.GetCryptoAggregatesRequest(
            path=_models.GetCryptoAggregatesRequestPath(crypto_ticker=crypto_ticker, multiplier=multiplier, timespan=timespan, from_=from_, to=to),
            query=_models.GetCryptoAggregatesRequestQuery(adjusted=adjusted, sort=sort, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_crypto_aggregates: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/aggs/ticker/{cryptoTicker}/range/{multiplier}/{timespan}/{from}/{to}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/aggs/ticker/{cryptoTicker}/range/{multiplier}/{timespan}/{from}/{to}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_crypto_aggregates")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_crypto_aggregates", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_crypto_aggregates",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: fx:aggregates
@mcp.tool()
async def get_previous_forex_close(
    forex_ticker: str = Field(..., alias="forexTicker", description="The forex ticker symbol representing a currency pair (e.g., C:EURUSD for Euro/US Dollar)."),
    adjusted: bool | None = Field(None, description="Whether to return split-adjusted results. Defaults to true for adjusted data; set to false to retrieve unadjusted historical prices."),
) -> dict[str, Any] | ToolResult:
    """Retrieve the previous trading day's OHLC (open, high, low, close) data for a specified forex currency pair. Useful for analyzing recent price action and market trends."""

    # Construct request model with validation
    try:
        _request = _models.GetPreviousForexAggregatesRequest(
            path=_models.GetPreviousForexAggregatesRequestPath(forex_ticker=forex_ticker),
            query=_models.GetPreviousForexAggregatesRequestQuery(adjusted=adjusted)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_previous_forex_close: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/aggs/ticker/{forexTicker}/prev", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/aggs/ticker/{forexTicker}/prev"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_previous_forex_close")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_previous_forex_close", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_previous_forex_close",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: fx:aggregates
@mcp.tool()
async def get_forex_aggregates(
    forex_ticker: str = Field(..., alias="forexTicker", description="The forex ticker symbol for the currency pair (e.g., C:EURUSD for EUR/USD)."),
    multiplier: int = Field(..., description="The multiplier for the timespan unit. Must be a positive integer that scales the timespan (e.g., multiplier=5 with timespan='minute' returns 5-minute bars)."),
    timespan: Literal["second", "minute", "hour", "day", "week", "month", "quarter", "year"] = Field(..., description="The unit of time for each aggregate bar. Choose from: second, minute, hour, day, week, month, quarter, or year."),
    from_: str = Field(..., alias="from", description="The start of the time window for aggregates. Provide either a date in YYYY-MM-DD format or a millisecond Unix timestamp."),
    to: str = Field(..., description="The end of the time window for aggregates. Provide either a date in YYYY-MM-DD format or a millisecond Unix timestamp."),
    adjusted: bool | None = Field(None, description="Whether to adjust results for stock splits. Defaults to true (adjusted). Set to false to retrieve unadjusted data."),
    sort: Literal["asc", "desc"] | None = Field(None, description="Sort order for results by timestamp. Use 'asc' for oldest-first or 'desc' for newest-first ordering."),
    limit: int | None = Field(None, description="Maximum number of base aggregates to query for creating results. Accepts values up to 50,000; defaults to 5,000 if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve aggregate (OHLCV) bars for a forex currency pair over a specified date range with customizable time window sizes. For example, use multiplier=5 with timespan='minute' to get 5-minute bars."""

    # Construct request model with validation
    try:
        _request = _models.GetForexAggregatesRequest(
            path=_models.GetForexAggregatesRequestPath(forex_ticker=forex_ticker, multiplier=multiplier, timespan=timespan, from_=from_, to=to),
            query=_models.GetForexAggregatesRequestQuery(adjusted=adjusted, sort=sort, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_forex_aggregates: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/aggs/ticker/{forexTicker}/range/{multiplier}/{timespan}/{from}/{to}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/aggs/ticker/{forexTicker}/range/{multiplier}/{timespan}/{from}/{to}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_forex_aggregates")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_forex_aggregates", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_forex_aggregates",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: indices:aggregates
@mcp.tool()
async def get_previous_index_aggregates(indices_ticker: str = Field(..., alias="indicesTicker", description="The ticker symbol of the index (e.g., I:NDX for Nasdaq-100). Use the index ticker in the format specified by your data provider.")) -> dict[str, Any] | ToolResult:
    """Retrieve the previous trading day's OHLC (open, high, low, close) aggregate data for a specified index. Useful for comparing current performance against the prior day's closing values."""

    # Construct request model with validation
    try:
        _request = _models.GetPreviousIndicesAggregatesRequest(
            path=_models.GetPreviousIndicesAggregatesRequestPath(indices_ticker=indices_ticker)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_previous_index_aggregates: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/aggs/ticker/{indicesTicker}/prev", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/aggs/ticker/{indicesTicker}/prev"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_previous_index_aggregates")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_previous_index_aggregates", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_previous_index_aggregates",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: indices:aggregates
@mcp.tool()
async def get_indices_aggregates(
    indices_ticker: str = Field(..., alias="indicesTicker", description="The ticker symbol of the index (e.g., I:NDX for Nasdaq-100)."),
    multiplier: int = Field(..., description="The multiplier for the timespan unit. Combined with timespan to define the aggregate window size (e.g., multiplier=5 with timespan='minute' creates 5-minute bars)."),
    timespan: Literal["second", "minute", "hour", "day", "week", "month", "quarter", "year"] = Field(..., description="The unit of time for the aggregate window. Choose from: second, minute, hour, day, week, month, quarter, or year."),
    from_: str = Field(..., alias="from", description="The start of the aggregate time window. Provide either a date in YYYY-MM-DD format or a millisecond Unix timestamp."),
    to: str = Field(..., description="The end of the aggregate time window. Provide either a date in YYYY-MM-DD format or a millisecond Unix timestamp."),
    sort: Literal["asc", "desc"] | None = Field(None, description="Sort results by timestamp in ascending order (oldest first) or descending order (newest first). Defaults to ascending if not specified."),
    limit: int | None = Field(None, description="Maximum number of base aggregates to query for creating results. Accepts values up to 50,000; defaults to 5,000 if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve aggregate (OHLCV) bars for an index over a specified date range with customizable time window sizes. For example, use multiplier=5 with timespan='minute' to get 5-minute bars."""

    # Construct request model with validation
    try:
        _request = _models.GetIndicesAggregatesRequest(
            path=_models.GetIndicesAggregatesRequestPath(indices_ticker=indices_ticker, multiplier=multiplier, timespan=timespan, from_=from_, to=to),
            query=_models.GetIndicesAggregatesRequestQuery(sort=sort, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_indices_aggregates: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/aggs/ticker/{indicesTicker}/range/{multiplier}/{timespan}/{from}/{to}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/aggs/ticker/{indicesTicker}/range/{multiplier}/{timespan}/{from}/{to}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_indices_aggregates")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_indices_aggregates", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_indices_aggregates",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: options:aggregates
@mcp.tool()
async def get_previous_close_for_options_contract(
    options_ticker: str = Field(..., alias="optionsTicker", description="The options contract ticker symbol in the format O:{underlying}{expiration}{type}{strike} (e.g., O:SPY251219C00650000 for SPY call option expiring December 19, 2025 at $650 strike)."),
    adjusted: bool | None = Field(None, description="Whether to return split-adjusted results. Defaults to true for adjusted data; set to false to retrieve unadjusted historical prices."),
) -> dict[str, Any] | ToolResult:
    """Retrieve the previous trading day's OHLC (open, high, low, close) data for a specified options contract. Results are adjusted for splits by default."""

    # Construct request model with validation
    try:
        _request = _models.GetPreviousOptionsAggregatesRequest(
            path=_models.GetPreviousOptionsAggregatesRequestPath(options_ticker=options_ticker),
            query=_models.GetPreviousOptionsAggregatesRequestQuery(adjusted=adjusted)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_previous_close_for_options_contract: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/aggs/ticker/{optionsTicker}/prev", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/aggs/ticker/{optionsTicker}/prev"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_previous_close_for_options_contract")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_previous_close_for_options_contract", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_previous_close_for_options_contract",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: options:aggregates
@mcp.tool()
async def get_options_aggregates(
    options_ticker: str = Field(..., alias="optionsTicker", description="The options contract ticker symbol in the format O:UNDERLYING[EXPIRATION][TYPE][STRIKE] (e.g., O:SPY251219C00650000 for a SPY call option expiring December 19, 2025 with a $650 strike)."),
    multiplier: int = Field(..., description="The multiplier for the timespan unit. Combined with timespan, this defines the bar size (e.g., multiplier=5 with timespan='minute' produces 5-minute bars). Must be a positive integer."),
    timespan: Literal["second", "minute", "hour", "day", "week", "month", "quarter", "year"] = Field(..., description="The unit of time for each aggregate bar. Choose from: second, minute, hour, day, week, month, quarter, or year."),
    from_: str = Field(..., alias="from", description="The start of the time window for aggregates. Provide either a date in YYYY-MM-DD format or a millisecond Unix timestamp."),
    to: str = Field(..., description="The end of the time window for aggregates. Provide either a date in YYYY-MM-DD format or a millisecond Unix timestamp. Must be after the 'from' date."),
    adjusted: bool | None = Field(None, description="Whether to adjust results for corporate actions like splits. Defaults to true (adjusted). Set to false to retrieve unadjusted data."),
    sort: Literal["asc", "desc"] | None = Field(None, description="Sort order for results by timestamp. Use 'asc' for oldest-first or 'desc' for newest-first ordering."),
    limit: int | None = Field(None, description="Maximum number of base aggregates to query when constructing the result set. Accepts values up to 50,000; defaults to 5,000. Higher limits may improve accuracy for custom timespan aggregations."),
) -> dict[str, Any] | ToolResult:
    """Retrieve aggregate bars for an options contract over a specified date range in custom time window sizes. For example, with a 5-minute timespan, the API returns 5-minute OHLCV bars."""

    # Construct request model with validation
    try:
        _request = _models.GetOptionsAggregatesRequest(
            path=_models.GetOptionsAggregatesRequestPath(options_ticker=options_ticker, multiplier=multiplier, timespan=timespan, from_=from_, to=to),
            query=_models.GetOptionsAggregatesRequestQuery(adjusted=adjusted, sort=sort, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_options_aggregates: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/aggs/ticker/{optionsTicker}/range/{multiplier}/{timespan}/{from}/{to}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/aggs/ticker/{optionsTicker}/range/{multiplier}/{timespan}/{from}/{to}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_options_aggregates")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_options_aggregates", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_options_aggregates",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: stocks:aggregates
@mcp.tool()
async def get_previous_day_stock_ohlc(
    stocks_ticker: str = Field(..., alias="stocksTicker", description="The stock ticker symbol in uppercase (e.g., AAPL for Apple Inc.). Must be an exact, case-sensitive match."),
    adjusted: bool | None = Field(None, description="Whether to adjust results for stock splits. Defaults to true; set to false to retrieve unadjusted prices."),
) -> dict[str, Any] | ToolResult:
    """Retrieve the previous trading day's open, high, low, and close (OHLC) prices for a specified stock ticker. Results are adjusted for stock splits by default."""

    # Construct request model with validation
    try:
        _request = _models.GetPreviousStocksAggregatesRequest(
            path=_models.GetPreviousStocksAggregatesRequestPath(stocks_ticker=stocks_ticker),
            query=_models.GetPreviousStocksAggregatesRequestQuery(adjusted=adjusted)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_previous_day_stock_ohlc: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/aggs/ticker/{stocksTicker}/prev", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/aggs/ticker/{stocksTicker}/prev"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_previous_day_stock_ohlc")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_previous_day_stock_ohlc", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_previous_day_stock_ohlc",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: stocks:aggregates
@mcp.tool()
async def get_stock_aggregates_by_range(
    stocks_ticker: str = Field(..., alias="stocksTicker", description="The stock ticker symbol in uppercase (e.g., AAPL for Apple Inc.). Must be an exact, case-sensitive match."),
    multiplier: int = Field(..., description="The multiplier for the timespan unit. Combined with timespan to define the bar size (e.g., multiplier=5 with timespan='minute' produces 5-minute bars). Must be a positive integer."),
    timespan: Literal["second", "minute", "hour", "day", "week", "month", "quarter", "year"] = Field(..., description="The unit of time for each aggregate bar. Valid options are: second, minute, hour, day, week, month, quarter, or year."),
    from_: str = Field(..., alias="from", description="The start of the time window for aggregates. Accepts either a date in YYYY-MM-DD format or a millisecond Unix timestamp."),
    to: str = Field(..., description="The end of the time window for aggregates. Accepts either a date in YYYY-MM-DD format or a millisecond Unix timestamp. Must be on or after the 'from' date."),
    adjusted: bool | None = Field(None, description="Whether to adjust results for stock splits. Defaults to true (adjusted). Set to false to retrieve unadjusted data."),
    sort: Literal["asc", "desc"] | None = Field(None, description="Sort order for results by timestamp. Use 'asc' for ascending order (oldest first) or 'desc' for descending order (newest first)."),
    limit: int | None = Field(None, description="Maximum number of base aggregates to query when building results. Accepts values from 1 to 50,000; defaults to 5,000 if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve aggregate (OHLCV) bars for a stock over a specified date range with customizable time window sizes. For example, use multiplier=5 with timespan='minute' to get 5-minute bars."""

    # Construct request model with validation
    try:
        _request = _models.GetStocksAggregatesRequest(
            path=_models.GetStocksAggregatesRequestPath(stocks_ticker=stocks_ticker, multiplier=multiplier, timespan=timespan, from_=from_, to=to),
            query=_models.GetStocksAggregatesRequestQuery(adjusted=adjusted, sort=sort, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_stock_aggregates_by_range: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/aggs/ticker/{stocksTicker}/range/{multiplier}/{timespan}/{from}/{to}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/aggs/ticker/{stocksTicker}/range/{multiplier}/{timespan}/{from}/{to}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_stock_aggregates_by_range")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_stock_aggregates_by_range", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_stock_aggregates_by_range",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: stocks:last:quote
@mcp.tool()
async def get_last_quote(stocks_ticker: str = Field(..., alias="stocksTicker", description="The stock ticker symbol in case-sensitive format (e.g., AAPL for Apple Inc.).")) -> dict[str, Any] | ToolResult:
    """Retrieve the most recent NBBO (National Best Bid and Offer) quote for a specified stock ticker symbol."""

    # Construct request model with validation
    try:
        _request = _models.LastQuoteRequest(
            path=_models.LastQuoteRequestPath(stocks_ticker=stocks_ticker)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_last_quote: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/last/nbbo/{stocksTicker}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/last/nbbo/{stocksTicker}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_last_quote")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_last_quote", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_last_quote",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: options:last:trade
@mcp.tool()
async def get_last_trade_for_options_contract(options_ticker: str = Field(..., alias="optionsTicker", description="The options contract ticker symbol in the format O:{underlying_symbol}{expiration_date}{contract_type}{strike_price} (e.g., O:TSLA210903C00700000 for a Tesla call option expiring September 3, 2021 with a $700 strike).")) -> dict[str, Any] | ToolResult:
    """Retrieve the most recent trade execution for a specified options contract. Returns trade details including price, size, and timestamp for the latest transaction."""

    # Construct request model with validation
    try:
        _request = _models.LastTradeOptionsRequest(
            path=_models.LastTradeOptionsRequestPath(options_ticker=options_ticker)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_last_trade_for_options_contract: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/last/trade/{optionsTicker}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/last/trade/{optionsTicker}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_last_trade_for_options_contract")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_last_trade_for_options_contract", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_last_trade_for_options_contract",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: stocks:last:trade
@mcp.tool()
async def get_last_trade(stocks_ticker: str = Field(..., alias="stocksTicker", description="The stock ticker symbol in uppercase (e.g., AAPL for Apple Inc.). Must be a valid, case-sensitive ticker symbol.")) -> dict[str, Any] | ToolResult:
    """Retrieve the most recent trade execution for a specified stock ticker symbol. Returns the latest trade data including price, size, and timestamp."""

    # Construct request model with validation
    try:
        _request = _models.LastTradeRequest(
            path=_models.LastTradeRequestPath(stocks_ticker=stocks_ticker)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_last_trade: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/last/trade/{stocksTicker}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/last/trade/{stocksTicker}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_last_trade")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_last_trade", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_last_trade",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: reference:news
@mcp.tool()
async def list_news_for_ticker(
    published_utc: str | None = Field(None, description="Filter results to articles published on, before, or after a specific date. Use ISO 8601 format for the date specification."),
    order: Literal["asc", "desc"] | None = Field(None, description="Sort direction for results: ascending (oldest first) or descending (newest first). Defaults to descending when used with the sort field."),
    limit: int | None = Field(None, description="Maximum number of results to return. Must be between 1 and 1000 articles; defaults to 10 if not specified.", ge=1, le=1000),
    sort: Literal["published_utc"] | None = Field(None, description="Field to sort results by. Currently supports sorting by publication date (published_utc), which is the default ordering."),
) -> dict[str, Any] | ToolResult:
    """Retrieve the most recent news articles for a stock ticker symbol, including article summaries and links to original sources. Results can be filtered by publication date and sorted by recency."""

    # Construct request model with validation
    try:
        _request = _models.ListNewsRequest(
            query=_models.ListNewsRequestQuery(published_utc=published_utc, order=order, limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_news_for_ticker: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v2/reference/news"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_news_for_ticker")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_news_for_ticker", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_news_for_ticker",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: crypto:snapshot
@mcp.tool()
async def list_crypto_tickers_snapshot() -> dict[str, Any] | ToolResult:
    """Retrieve current market snapshot data for all traded cryptocurrency symbols, including minute and day aggregates, previous day comparison, and latest trade/quote information. Data is refreshed from exchanges starting around 4am EST daily, with snapshots cleared at 12am EST."""

    # Extract parameters for API call
    _http_path = "/v2/snapshot/locale/global/markets/crypto/tickers"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_crypto_tickers_snapshot")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_crypto_tickers_snapshot", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_crypto_tickers_snapshot",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: crypto:snapshot
@mcp.tool()
async def get_crypto_ticker_snapshot(ticker: str = Field(..., description="The cryptocurrency ticker symbol to retrieve snapshot data for, formatted as an exchange prefix and currency pair (e.g., X:BTCUSD for Bitcoin in USD).")) -> dict[str, Any] | ToolResult:
    """Retrieve real-time and aggregate market data for a cryptocurrency ticker, including current minute and day aggregates, previous day comparison, and the latest trade and quote information. Data is refreshed as exchange data arrives and resets daily at 12am EST."""

    # Construct request model with validation
    try:
        _request = _models.GetCryptoSnapshotTickerRequest(
            path=_models.GetCryptoSnapshotTickerRequestPath(ticker=ticker)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_crypto_ticker_snapshot: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/snapshot/locale/global/markets/crypto/tickers/{ticker}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/snapshot/locale/global/markets/crypto/tickers/{ticker}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_crypto_ticker_snapshot")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_crypto_ticker_snapshot", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_crypto_ticker_snapshot",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: crypto:snapshot
@mcp.tool()
async def list_crypto_gainers_or_losers(direction: Literal["gainers", "losers"] = Field(..., description="Specify whether to return top gainers or top losers. Use 'gainers' for tickers with the highest positive percentage change, or 'losers' for tickers with the highest negative percentage change since the previous day's close.")) -> dict[str, Any] | ToolResult:
    """Retrieve the top 20 cryptocurrency gainers or losers by percentage change since the previous day's close. Snapshot data resets daily at 12am EST and populates as exchange data arrives."""

    # Construct request model with validation
    try:
        _request = _models.GetCryptoSnapshotDirectionRequest(
            path=_models.GetCryptoSnapshotDirectionRequestPath(direction=direction)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_crypto_gainers_or_losers: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/snapshot/locale/global/markets/crypto/{direction}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/snapshot/locale/global/markets/crypto/{direction}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_crypto_gainers_or_losers")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_crypto_gainers_or_losers", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_crypto_gainers_or_losers",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: fx:snapshot
@mcp.tool()
async def get_forex_snapshot_tickers() -> dict[str, Any] | ToolResult:
    """Retrieve real-time snapshot data for all traded forex symbols, including current minute and day aggregates, previous day aggregates, and the latest trade and quote information. Note: Snapshot data resets daily at 12am EST and begins populating as early as 4am EST when exchange data arrives."""

    # Extract parameters for API call
    _http_path = "/v2/snapshot/locale/global/markets/forex/tickers"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_forex_snapshot_tickers")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_forex_snapshot_tickers", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_forex_snapshot_tickers",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: fx:snapshot
@mcp.tool()
async def get_forex_ticker_snapshot(ticker: str = Field(..., description="The forex currency pair ticker symbol (e.g., C:EURUSD for Euro/US Dollar). Use the format C: prefix followed by the three-letter currency codes.")) -> dict[str, Any] | ToolResult:
    """Retrieve real-time forex market data for a currency pair, including current minute and day aggregates, previous day comparison, and the latest trade and quote information. Data is refreshed as exchange data arrives and resets daily at 12am EST."""

    # Construct request model with validation
    try:
        _request = _models.GetForexSnapshotTickerRequest(
            path=_models.GetForexSnapshotTickerRequestPath(ticker=ticker)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_forex_ticker_snapshot: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/snapshot/locale/global/markets/forex/tickers/{ticker}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/snapshot/locale/global/markets/forex/tickers/{ticker}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_forex_ticker_snapshot")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_forex_ticker_snapshot", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_forex_ticker_snapshot",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: fx:snapshot
@mcp.tool()
async def list_forex_gainers_or_losers(direction: Literal["gainers", "losers"] = Field(..., description="Specify whether to return the top gainers or top losers. Use 'gainers' for pairs with the highest positive percentage change, or 'losers' for pairs with the highest negative percentage change since the previous day's close.")) -> dict[str, Any] | ToolResult:
    """Retrieve the top 20 forex currency pairs ranked by daily percentage change. Returns either the biggest gainers or losers since the previous day's close, with snapshot data refreshed daily at 12am EST."""

    # Construct request model with validation
    try:
        _request = _models.GetForexSnapshotDirectionRequest(
            path=_models.GetForexSnapshotDirectionRequestPath(direction=direction)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_forex_gainers_or_losers: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/snapshot/locale/global/markets/forex/{direction}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/snapshot/locale/global/markets/forex/{direction}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_forex_gainers_or_losers")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_forex_gainers_or_losers", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_forex_gainers_or_losers",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: stocks:snapshot
@mcp.tool()
async def list_stock_tickers_snapshot(include_otc: bool | None = Field(None, description="Set to true to include over-the-counter (OTC) securities in the results; defaults to false to return only exchange-listed stocks.")) -> dict[str, Any] | ToolResult:
    """Retrieve real-time market data snapshot for all traded stock symbols. Data is refreshed continuously from exchanges starting around 4am EST daily, with the previous day's data cleared at 3:30am EST."""

    # Construct request model with validation
    try:
        _request = _models.GetStocksSnapshotTickersRequest(
            query=_models.GetStocksSnapshotTickersRequestQuery(include_otc=include_otc)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_stock_tickers_snapshot: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v2/snapshot/locale/us/markets/stocks/tickers"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_stock_tickers_snapshot")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_stock_tickers_snapshot", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_stock_tickers_snapshot",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: stocks:snapshot
@mcp.tool()
async def get_stock_snapshot_by_ticker(stocks_ticker: str = Field(..., alias="stocksTicker", description="The stock ticker symbol in uppercase (e.g., AAPL for Apple Inc.). Must match the exact case-sensitive symbol used by the exchange.")) -> dict[str, Any] | ToolResult:
    """Retrieve real-time market data snapshot for a specific stock ticker symbol. Data is refreshed as exchange data arrives, typically starting at 4am EST after the 3:30am EST daily reset."""

    # Construct request model with validation
    try:
        _request = _models.GetStocksSnapshotTickerRequest(
            path=_models.GetStocksSnapshotTickerRequestPath(stocks_ticker=stocks_ticker)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_stock_snapshot_by_ticker: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/snapshot/locale/us/markets/stocks/tickers/{stocksTicker}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/snapshot/locale/us/markets/stocks/tickers/{stocksTicker}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_stock_snapshot_by_ticker")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_stock_snapshot_by_ticker", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_stock_snapshot_by_ticker",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: stocks:snapshot
@mcp.tool()
async def list_stocks_by_direction(
    direction: Literal["gainers", "losers"] = Field(..., description="Specify whether to return top gainers or top losers ranked by percentage price change since the previous close."),
    include_otc: bool | None = Field(None, description="Set to true to include over-the-counter (OTC) securities in the results; defaults to false to exclude OTC securities."),
) -> dict[str, Any] | ToolResult:
    """Retrieve the top 20 stocks with the highest percentage gains or losses since the previous day's close. Results include only tickers with trading volume of 10,000 or more and are updated throughout the trading day."""

    # Construct request model with validation
    try:
        _request = _models.GetStocksSnapshotDirectionRequest(
            path=_models.GetStocksSnapshotDirectionRequestPath(direction=direction),
            query=_models.GetStocksSnapshotDirectionRequestQuery(include_otc=include_otc)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_stocks_by_direction: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/snapshot/locale/us/markets/stocks/{direction}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/snapshot/locale/us/markets/stocks/{direction}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_stocks_by_direction")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_stocks_by_direction", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_stocks_by_direction",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: stocks:quotes
@mcp.tool()
async def get_nbbo_quotes_for_date(
    ticker: str = Field(..., description="The stock ticker symbol (e.g., AAPL) for which to retrieve quotes."),
    date: str = Field(..., description="The date for which to retrieve quotes, specified in YYYY-MM-DD format (e.g., 2020-10-14)."),
    timestamp_limit: int | None = Field(None, alias="timestampLimit", description="Optional maximum timestamp threshold; only quotes at or before this timestamp will be included in results."),
    reverse: bool | None = Field(None, description="Optional flag to reverse the sort order of results; when true, results are returned in descending order."),
    limit: int | None = Field(None, description="Optional limit on the number of quotes returned in the response, with a maximum of 50,000 and default of 5,000."),
) -> dict[str, Any] | ToolResult:
    """Retrieve National Best Bid and Offer (NBBO) quotes for a specific stock ticker on a given date. Returns intraday quote data with optional filtering and ordering."""

    # Construct request model with validation
    try:
        _request = _models.DeprecatedGetHistoricStocksQuotesRequest(
            path=_models.DeprecatedGetHistoricStocksQuotesRequestPath(ticker=ticker, date=date),
            query=_models.DeprecatedGetHistoricStocksQuotesRequestQuery(timestamp_limit=timestamp_limit, reverse=reverse, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_nbbo_quotes_for_date: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/ticks/stocks/nbbo/{ticker}/{date}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/ticks/stocks/nbbo/{ticker}/{date}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_nbbo_quotes_for_date")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_nbbo_quotes_for_date", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_nbbo_quotes_for_date",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: fx:quotes
@mcp.tool()
async def get_fx_quotes(
    fx_ticker: str = Field(..., alias="fxTicker", description="The FX ticker symbol to retrieve quotes for, formatted as a currency pair (e.g., C:EUR-USD)."),
    order: Literal["asc", "desc"] | None = Field(None, description="Sort order for results: ascending or descending. Defaults to descending order."),
    limit: int | None = Field(None, description="Maximum number of results to return. Must be between 1 and 50,000; defaults to 1,000.", ge=1, le=50000),
    sort: Literal["timestamp"] | None = Field(None, description="Field to sort results by. Currently supports sorting by timestamp only."),
) -> dict[str, Any] | ToolResult:
    """Retrieve best bid-offer (BBO) quotes for a foreign exchange ticker symbol. Returns quote data sorted by timestamp in descending order by default, with configurable pagination and ordering."""

    # Construct request model with validation
    try:
        _request = _models.QuotesFxRequest(
            path=_models.QuotesFxRequestPath(fx_ticker=fx_ticker),
            query=_models.QuotesFxRequestQuery(order=order, limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_fx_quotes: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v3/quotes/{fxTicker}", _request.path.model_dump(by_alias=True)) if _request.path else "/v3/quotes/{fxTicker}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_fx_quotes")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_fx_quotes", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_fx_quotes",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: options:quotes
@mcp.tool()
async def list_options_quotes(
    options_ticker: str = Field(..., alias="optionsTicker", description="The options ticker symbol to retrieve quotes for, formatted as an OCC options symbol (e.g., O:SPY241220P00720000 for a SPY put option)."),
    order: Literal["asc", "desc"] | None = Field(None, description="Sort order for results based on the sort field. Defaults to descending order (newest first)."),
    limit: int | None = Field(None, description="Maximum number of quote records to return in the response. Accepts values from 1 to 50,000, with a default of 1,000.", ge=1, le=50000),
    sort: Literal["timestamp"] | None = Field(None, description="Field to sort results by. Currently supports sorting by timestamp only."),
) -> dict[str, Any] | ToolResult:
    """Retrieve historical quote data for an options contract ticker symbol, with configurable sorting and pagination to handle large result sets."""

    # Construct request model with validation
    try:
        _request = _models.QuotesOptionsRequest(
            path=_models.QuotesOptionsRequestPath(options_ticker=options_ticker),
            query=_models.QuotesOptionsRequestQuery(order=order, limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_options_quotes: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v3/quotes/{optionsTicker}", _request.path.model_dump(by_alias=True)) if _request.path else "/v3/quotes/{optionsTicker}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_options_quotes")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_options_quotes", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_options_quotes",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: stocks:quotes
@mcp.tool()
async def get_stock_quotes(
    stock_ticker: str = Field(..., alias="stockTicker", description="The stock ticker symbol to retrieve quotes for (case-sensitive). For example, AAPL for Apple Inc."),
    order: Literal["asc", "desc"] | None = Field(None, description="Sort order for results based on the sort field. Defaults to descending order."),
    limit: int | None = Field(None, description="Maximum number of quote records to return. Accepts values from 1 to 50,000, with a default of 1,000.", ge=1, le=50000),
    sort: Literal["timestamp"] | None = Field(None, description="Field to sort results by. Currently supports sorting by timestamp."),
) -> dict[str, Any] | ToolResult:
    """Retrieve National Best Bid and Offer (NBBO) quotes for a stock ticker symbol. Returns quote data sorted and limited according to specified parameters."""

    # Construct request model with validation
    try:
        _request = _models.QuotesRequest(
            path=_models.QuotesRequestPath(stock_ticker=stock_ticker),
            query=_models.QuotesRequestQuery(order=order, limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_stock_quotes: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v3/quotes/{stockTicker}", _request.path.model_dump(by_alias=True)) if _request.path else "/v3/quotes/{stockTicker}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_stock_quotes")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_stock_quotes", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_stock_quotes",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: reference:conditions
@mcp.tool()
async def list_conditions(
    data_type: Literal["trade", "bbo", "nbbo"] | None = Field(None, description="Filter results to conditions associated with a specific data type: trade data, best bid-offer quotes, or national best bid-offer quotes."),
    id_: int | None = Field(None, alias="id", description="Filter results to a specific condition by its numeric identifier."),
    sip: Literal["CTA", "UTP", "OPRA"] | None = Field(None, description="Filter results to conditions that have a mapping for a specific SIP (Consolidated Tape Association, Unlisted Trading Privileges, or Options Price Reporting Authority)."),
    order: Literal["asc", "desc"] | None = Field(None, description="Sort results in ascending or descending order based on the selected sort field."),
    limit: int | None = Field(None, description="Limit the number of results returned; defaults to 10 with a maximum of 1000 results per request.", ge=1, le=1000),
    sort: Literal["asset_class", "id", "type", "name", "data_types", "legacy"] | None = Field(None, description="Select the field to sort by: asset class, condition ID, type, name, supported data types, or legacy status. Defaults to asset class."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all market conditions used by Massive, with optional filtering by data type, SIP, or condition ID. Results can be sorted and paginated for efficient data retrieval."""

    # Construct request model with validation
    try:
        _request = _models.ListConditionsRequest(
            query=_models.ListConditionsRequestQuery(data_type=data_type, id_=id_, sip=sip, order=order, limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_conditions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/reference/conditions"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_conditions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_conditions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_conditions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: reference:dividends
@mcp.tool()
async def list_dividends(
    record_date: str | None = Field(None, description="Filter dividends by the record date (the date on which shareholders must be registered to receive the dividend). Use YYYY-MM-DD format."),
    declaration_date: str | None = Field(None, description="Filter dividends by the declaration date (when the dividend was officially announced). Use YYYY-MM-DD format."),
    pay_date: str | None = Field(None, description="Filter dividends by the payment date (when the dividend was or will be paid to shareholders). Use YYYY-MM-DD format."),
    cash_amount: float | None = Field(None, description="Filter dividends by the cash amount paid per share. Accepts numeric values."),
    dividend_type: Literal["CD", "SC", "LT", "ST"] | None = Field(None, description="Filter dividends by type: CD for regular/consistent dividends, SC for special/infrequent cash dividends, LT for long-term capital gains, or ST for short-term capital gains."),
    order: Literal["asc", "desc"] | None = Field(None, description="Sort results in ascending or descending order based on the selected sort field."),
    limit: int | None = Field(None, description="Limit the number of results returned. Must be between 1 and 1000, with a default of 10 results.", ge=1, le=1000),
    sort: Literal["ex_dividend_date", "pay_date", "declaration_date", "record_date", "cash_amount", "ticker"] | None = Field(None, description="Choose which field to sort by: ex_dividend_date (default), pay_date, declaration_date, record_date, cash_amount, or ticker symbol."),
) -> dict[str, Any] | ToolResult:
    """Retrieve historical dividend payments with filtering and sorting capabilities. Query by date, amount, or dividend type to find specific dividend records across securities."""

    # Construct request model with validation
    try:
        _request = _models.ListDividendsRequest(
            query=_models.ListDividendsRequestQuery(record_date=record_date, declaration_date=declaration_date, pay_date=pay_date, cash_amount=cash_amount, dividend_type=dividend_type, order=order, limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_dividends: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/reference/dividends"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_dividends")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_dividends", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_dividends",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: reference:exchanges
@mcp.tool()
async def list_exchanges(locale: Literal["us", "global"] | None = Field(None, description="Filter results by geographic region: use 'us' for United States exchanges or 'global' for worldwide exchanges.")) -> dict[str, Any] | ToolResult:
    """Retrieve a list of all exchanges that Massive has data for, optionally filtered by geographic locale."""

    # Construct request model with validation
    try:
        _request = _models.ListExchangesRequest(
            query=_models.ListExchangesRequestQuery(locale=locale)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_exchanges: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/reference/exchanges"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_exchanges")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_exchanges", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_exchanges",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: reference:options:contracts:list
@mcp.tool()
async def list_options_contracts(
    underlying_ticker: str | None = Field(None, description="Filter results to contracts for a specific underlying stock ticker symbol (e.g., AAPL, TSLA)."),
    contract_type: Literal["call", "put"] | None = Field(None, description="Filter by contract type: either call options or put options."),
    as_of: str | None = Field(None, description="Query contracts as they existed on a specific date using YYYY-MM-DD format. Defaults to today's date if not specified."),
    expired: bool | None = Field(None, description="Include expired contracts in results. By default, only active contracts are returned."),
    order: Literal["asc", "desc"] | None = Field(None, description="Sort results in ascending or descending order based on the selected sort field."),
    limit: int | None = Field(None, description="Maximum number of results to return, between 1 and 1000. Defaults to 10 results per request.", ge=1, le=1000),
    sort: Literal["ticker", "underlying_ticker", "expiration_date", "strike_price"] | None = Field(None, description="Field to sort results by: ticker symbol, underlying ticker, expiration date, or strike price. Defaults to sorting by ticker."),
) -> dict[str, Any] | ToolResult:
    """Retrieve historical options contracts for a given underlying asset, including both active and expired contracts. Filter by contract type, expiration date, and other criteria to find specific options trading opportunities."""

    # Construct request model with validation
    try:
        _request = _models.ListOptionsContractsRequest(
            query=_models.ListOptionsContractsRequestQuery(underlying_ticker=underlying_ticker, contract_type=contract_type, as_of=as_of, expired=expired, order=order, limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_options_contracts: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/reference/options/contracts"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_options_contracts")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_options_contracts", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_options_contracts",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: reference:options:contract
@mcp.tool()
async def get_options_contract(
    options_ticker: str = Field(..., description="The options ticker symbol identifying the contract (e.g., O:SPY251219C00650000). This follows the standard options ticker format which encodes the underlying symbol, expiration date, option type, and strike price."),
    as_of: str | None = Field(None, description="Historical reference date for the contract data in YYYY-MM-DD format. If not provided, defaults to today's date."),
) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific options contract using its ticker symbol. Optionally specify a historical date to view the contract as it existed on that date."""

    # Construct request model with validation
    try:
        _request = _models.GetOptionsContractRequest(
            path=_models.GetOptionsContractRequestPath(options_ticker=options_ticker),
            query=_models.GetOptionsContractRequestQuery(as_of=as_of)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_options_contract: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v3/reference/options/contracts/{options_ticker}", _request.path.model_dump(by_alias=True)) if _request.path else "/v3/reference/options/contracts/{options_ticker}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_options_contract")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_options_contract", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_options_contract",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: reference:stocks
@mcp.tool()
async def list_stock_splits(
    reverse_split: bool | None = Field(None, description="Filter results to show only reverse stock splits, where the split ratio decreases the number of shares (split_from > split_to). Omit to include all splits."),
    execution_date_gte: str | None = Field(None, alias="execution_date.gte", description="Filter splits executed on or after this date (inclusive). Use ISO 8601 date format (YYYY-MM-DD)."),
    execution_date_gt: str | None = Field(None, alias="execution_date.gt", description="Filter splits executed after this date (exclusive). Use ISO 8601 date format (YYYY-MM-DD)."),
    execution_date_lte: str | None = Field(None, alias="execution_date.lte", description="Filter splits executed on or before this date (inclusive). Use ISO 8601 date format (YYYY-MM-DD)."),
    execution_date_lt: str | None = Field(None, alias="execution_date.lt", description="Filter splits executed before this date (exclusive). Use ISO 8601 date format (YYYY-MM-DD)."),
    order: Literal["asc", "desc"] | None = Field(None, description="Sort results in ascending or descending order based on the sort field. Defaults to ascending."),
    limit: int | None = Field(None, description="Maximum number of results to return per request. Must be between 1 and 1000, defaults to 10.", ge=1, le=1000),
    sort: Literal["execution_date", "ticker"] | None = Field(None, description="Field to sort results by: execution_date or ticker. Defaults to execution_date."),
) -> dict[str, Any] | ToolResult:
    """Retrieve historical stock splits with details including ticker symbol, execution date, and split ratio factors. Filter by reverse splits, date range, and customize sorting and pagination."""

    # Construct request model with validation
    try:
        _request = _models.ListStockSplitsRequest(
            query=_models.ListStockSplitsRequestQuery(reverse_split=reverse_split, execution_date_gte=execution_date_gte, execution_date_gt=execution_date_gt, execution_date_lte=execution_date_lte, execution_date_lt=execution_date_lt, order=order, limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_stock_splits: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/reference/splits"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_stock_splits")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_stock_splits", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_stock_splits",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: reference:tickers:list
@mcp.tool()
async def list_tickers(
    market: Literal["stocks", "crypto", "fx", "otc", "indices"] | None = Field(None, description="Filter results to a specific market type: stocks, crypto, forex, otc, or indices. Omit to include all markets."),
    exchange: str | None = Field(None, description="Filter by the asset's primary exchange using its ISO 10383 Market Identifier Code (MIC). Leave empty to query all exchanges."),
    cusip: str | None = Field(None, description="Filter by CUSIP code to find a specific asset. Note: CUSIP codes are accepted for filtering but are not returned in the response for legal reasons."),
    search: str | None = Field(None, description="Search for matching terms within ticker symbols and company names."),
    active: bool | None = Field(None, description="Return only actively traded tickers on the queried date. Defaults to true."),
    order: Literal["asc", "desc"] | None = Field(None, description="Sort results in ascending or descending order based on the sort field."),
    limit: int | None = Field(None, description="Limit the number of results returned. Must be between 1 and 1000, defaults to 100.", ge=1, le=1000),
    sort: Literal["ticker", "name", "market", "locale", "primary_exchange", "type", "currency_symbol", "currency_name", "base_currency_symbol", "base_currency_name", "cik", "composite_figi", "share_class_figi", "last_updated_utc", "delisted_utc"] | None = Field(None, description="Sort results by a specific field: ticker, name, market, locale, primary_exchange, type, currency details, identifiers (CIK, FIGI), or last_updated_utc. Defaults to ticker."),
) -> dict[str, Any] | ToolResult:
    """Query all supported ticker symbols across stocks, indices, forex, and crypto markets. Filter by market type, exchange, CUSIP, or search terms to find specific assets."""

    # Construct request model with validation
    try:
        _request = _models.ListTickersRequest(
            query=_models.ListTickersRequestQuery(market=market, exchange=exchange, cusip=cusip, search=search, active=active, order=order, limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_tickers: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/reference/tickers"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_tickers")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_tickers", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_tickers",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: reference:tickers:types
@mcp.tool()
async def list_ticker_types(locale: Literal["us", "global"] | None = Field(None, description="Filter ticker types by geographic market: use 'us' for United States market or 'global' for worldwide tickers. If omitted, returns all ticker types.")) -> dict[str, Any] | ToolResult:
    """Retrieve all ticker types available in the Massive database. Optionally filter results by geographic locale to see ticker types relevant to a specific market."""

    # Construct request model with validation
    try:
        _request = _models.ListTickerTypesRequest(
            query=_models.ListTickerTypesRequestQuery(locale=locale)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_ticker_types: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/reference/tickers/types"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_ticker_types")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_ticker_types", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_ticker_types",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: reference:tickers:get
@mcp.tool()
async def get_ticker_details(ticker: str = Field(..., description="The ticker symbol to look up, case-sensitive (e.g., AAPL for Apple Inc.). Must be a valid ticker symbol supported by the service.")) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific ticker symbol, including company data and market details supported by Massive."""

    # Construct request model with validation
    try:
        _request = _models.GetTickerRequest(
            path=_models.GetTickerRequestPath(ticker=ticker)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_ticker_details: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v3/reference/tickers/{ticker}", _request.path.model_dump(by_alias=True)) if _request.path else "/v3/reference/tickers/{ticker}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_ticker_details")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_ticker_details", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_ticker_details",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool()
async def list_snapshots(
    order: Literal["asc", "desc"] | None = Field(None, description="Sort order direction for results: ascending or descending based on the sort field."),
    limit: int | None = Field(None, description="Maximum number of results to return per request, between 1 and 250 (defaults to 10).", ge=1, le=250),
    sort: Literal["ticker"] | None = Field(None, description="Field to sort results by; currently supports sorting by ticker symbol."),
) -> dict[str, Any] | ToolResult:
    """Retrieve current snapshots for assets across all asset types, with optional sorting and pagination controls."""

    # Construct request model with validation
    try:
        _request = _models.SnapshotsRequest(
            query=_models.SnapshotsRequestQuery(order=order, limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_snapshots: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/snapshot"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_snapshots")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_snapshots", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_snapshots",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: indices:snapshot
@mcp.tool()
async def list_indices_snapshot(
    order: Literal["asc", "desc"] | None = Field(None, description="Sort direction for results: ascending or descending order based on the sort field."),
    limit: int | None = Field(None, description="Maximum number of results to return in the response, ranging from 1 to 250 (defaults to 10 if not specified).", ge=1, le=250),
    sort: Literal["ticker"] | None = Field(None, description="Field to use for ordering results; currently supports sorting by ticker symbol."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a snapshot of current indices data for specified tickers, with optional sorting and pagination controls."""

    # Construct request model with validation
    try:
        _request = _models.IndicesSnapshotRequest(
            query=_models.IndicesSnapshotRequestQuery(order=order, limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_indices_snapshot: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/snapshot/indices"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_indices_snapshot")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_indices_snapshot", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_indices_snapshot",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: options:snapshot
@mcp.tool()
async def list_options_chain(
    underlying_asset: str = Field(..., alias="underlyingAsset", description="The ticker symbol of the underlying asset (e.g., EVRI). This is the security for which you want to retrieve options contracts."),
    contract_type: Literal["call", "put"] | None = Field(None, description="Filter results to only calls or puts. If omitted, both contract types are returned."),
    order: Literal["asc", "desc"] | None = Field(None, description="Sort results in ascending or descending order based on the sort field. Defaults to ascending if not specified."),
    limit: int | None = Field(None, description="Maximum number of results to return, between 1 and 250. Defaults to 10 if not specified.", ge=1, le=250),
    sort: Literal["ticker", "expiration_date", "strike_price"] | None = Field(None, description="Field to sort by: ticker symbol, expiration date, or strike price. Defaults to ticker if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all options contracts for a given underlying asset, with optional filtering by contract type and customizable sorting and pagination."""

    # Construct request model with validation
    try:
        _request = _models.OptionsChainRequest(
            path=_models.OptionsChainRequestPath(underlying_asset=underlying_asset),
            query=_models.OptionsChainRequestQuery(contract_type=contract_type, order=order, limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_options_chain: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v3/snapshot/options/{underlyingAsset}", _request.path.model_dump(by_alias=True)) if _request.path else "/v3/snapshot/options/{underlyingAsset}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_options_chain")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_options_chain", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_options_chain",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: options:snapshot
@mcp.tool()
async def get_option_contract_snapshot(
    underlying_asset: str = Field(..., alias="underlyingAsset", description="The ticker symbol of the underlying stock (e.g., EVRI). This identifies which equity the option contract is based on."),
    option_contract: str = Field(..., alias="optionContract", description="The unique identifier for the specific option contract (e.g., O:EVRI260116C00015000). This format typically encodes the underlying asset, expiration date, contract type (call/put), and strike price."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a real-time snapshot of an option contract for a given underlying stock, including current pricing and contract details."""

    # Construct request model with validation
    try:
        _request = _models.OptionContractRequest(
            path=_models.OptionContractRequestPath(underlying_asset=underlying_asset, option_contract=option_contract)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_option_contract_snapshot: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v3/snapshot/options/{underlyingAsset}/{optionContract}", _request.path.model_dump(by_alias=True)) if _request.path else "/v3/snapshot/options/{underlyingAsset}/{optionContract}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_option_contract_snapshot")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_option_contract_snapshot", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_option_contract_snapshot",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: crypto:trades
@mcp.tool()
async def list_crypto_trades(
    crypto_ticker: str = Field(..., alias="cryptoTicker", description="The cryptocurrency ticker symbol to retrieve trades for, formatted as an exchange prefix and currency pair (e.g., X:BTC-USD for Bitcoin in US dollars)."),
    order: Literal["asc", "desc"] | None = Field(None, description="Sort order for results: ascending (oldest first) or descending (newest first). Defaults to descending order."),
    limit: int | None = Field(None, description="Maximum number of trade records to return. Must be between 1 and 50,000; defaults to 1,000 if not specified.", ge=1, le=50000),
    sort: Literal["timestamp"] | None = Field(None, description="Field to sort results by. Currently supports sorting by timestamp only."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a list of trades for a specified cryptocurrency ticker symbol, with options to sort, order, and limit results. Useful for analyzing recent trading activity and market movements."""

    # Construct request model with validation
    try:
        _request = _models.TradesCryptoRequest(
            path=_models.TradesCryptoRequestPath(crypto_ticker=crypto_ticker),
            query=_models.TradesCryptoRequestQuery(order=order, limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_crypto_trades: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v3/trades/{cryptoTicker}", _request.path.model_dump(by_alias=True)) if _request.path else "/v3/trades/{cryptoTicker}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_crypto_trades")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_crypto_trades", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_crypto_trades",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: options:trades
@mcp.tool()
async def list_options_trades(
    options_ticker: str = Field(..., alias="optionsTicker", description="The options ticker symbol identifying the specific contract to retrieve trades for (e.g., O:TSLA210903C00700000)."),
    order: Literal["asc", "desc"] | None = Field(None, description="Sort direction for results based on the sort field; defaults to descending order (newest first)."),
    limit: int | None = Field(None, description="Maximum number of trade records to return, between 1 and 50,000; defaults to 1,000 if not specified.", ge=1, le=50000),
    sort: Literal["timestamp"] | None = Field(None, description="Field to sort results by; currently supports sorting by timestamp only."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a list of trades executed for a specific options contract within an optional time range, with configurable sorting and pagination."""

    # Construct request model with validation
    try:
        _request = _models.TradesOptionsRequest(
            path=_models.TradesOptionsRequestPath(options_ticker=options_ticker),
            query=_models.TradesOptionsRequestQuery(order=order, limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_options_trades: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v3/trades/{optionsTicker}", _request.path.model_dump(by_alias=True)) if _request.path else "/v3/trades/{optionsTicker}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_options_trades")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_options_trades", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_options_trades",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: stocks:trades
@mcp.tool()
async def list_trades(
    stock_ticker: str = Field(..., alias="stockTicker", description="The stock ticker symbol to retrieve trades for (case-sensitive). For example, AAPL for Apple Inc."),
    order: Literal["asc", "desc"] | None = Field(None, description="Sort order for results based on the sort field. Choose ascending or descending order; defaults to descending."),
    limit: int | None = Field(None, description="Maximum number of trade records to return. Accepts values from 1 to 50,000; defaults to 1,000 if not specified.", ge=1, le=50000),
    sort: Literal["timestamp"] | None = Field(None, description="Field to sort results by. Currently supports sorting by timestamp."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a list of trades for a specified stock ticker within an optional time range, with configurable sorting and pagination."""

    # Construct request model with validation
    try:
        _request = _models.TradesRequest(
            path=_models.TradesRequestPath(stock_ticker=stock_ticker),
            query=_models.TradesRequestQuery(order=order, limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_trades: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v3/trades/{stockTicker}", _request.path.model_dump(by_alias=True)) if _request.path else "/v3/trades/{stockTicker}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_trades")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_trades", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_trades",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: reference:stocks
@mcp.tool()
async def list_financials(
    sic: str | None = Field(None, description="Filter results by Standard Industrial Classification (SIC) code to narrow results to a specific industry sector."),
    company_name_search: str | None = Field(None, alias="company_name.search", description="Search for companies by name using partial text matching."),
    period_of_report_date_gte: str | None = Field(None, alias="period_of_report_date.gte", description="Filter to include only financial records with a period-of-report date on or after this date (inclusive). Use ISO 8601 date format."),
    period_of_report_date_gt: str | None = Field(None, alias="period_of_report_date.gt", description="Filter to include only financial records with a period-of-report date strictly after this date (exclusive). Use ISO 8601 date format."),
    period_of_report_date_lte: str | None = Field(None, alias="period_of_report_date.lte", description="Filter to include only financial records with a period-of-report date on or before this date (inclusive). Use ISO 8601 date format."),
    period_of_report_date_lt: str | None = Field(None, alias="period_of_report_date.lt", description="Filter to include only financial records with a period-of-report date strictly before this date (exclusive). Use ISO 8601 date format."),
    order: Literal["asc", "desc"] | None = Field(None, description="Sort results in ascending or descending order based on the field specified in the sort parameter."),
    limit: int | None = Field(None, description="Maximum number of results to return per request. Defaults to 10 and cannot exceed 100.", ge=1, le=100),
    sort: Literal["filing_date", "period_of_report_date"] | None = Field(None, description="Field to sort results by. Choose between filing date or period-of-report date. Defaults to period-of-report date."),
) -> dict[str, Any] | ToolResult:
    """Retrieve historical financial data for stocks extracted from SEC XBRL filings. Filter by company, industry classification, reporting period, and customize result ordering and pagination."""

    # Construct request model with validation
    try:
        _request = _models.ListFinancialsRequest(
            query=_models.ListFinancialsRequestQuery(sic=sic, company_name_search=company_name_search, period_of_report_date_gte=period_of_report_date_gte, period_of_report_date_gt=period_of_report_date_gt, period_of_report_date_lte=period_of_report_date_lte, period_of_report_date_lt=period_of_report_date_lt, order=order, limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_financials: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/vX/reference/financials"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_financials")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_financials", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_financials",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: reference:stocks:ipos
@mcp.tool()
async def list_ipos_detailed(
    listing_date: str | None = Field(None, description="Filter results to a specific listing date (the first trading date for the newly listed entity). Use ISO 8601 date format."),
    ipo_status: Literal["direct_listing_process", "history", "new", "pending", "postponed", "rumor", "withdrawn"] | None = Field(None, description="Filter results by IPO status: new, pending, rumor, postponed, withdrawn, direct listing process, or historical."),
    order: Literal["asc", "desc"] | None = Field(None, description="Sort results in ascending or descending order. Defaults to descending."),
    limit: int | None = Field(None, description="Maximum number of results to return. Must be between 1 and 1000, defaults to 10.", ge=1, le=1000),
    sort: Literal["listing_date", "ticker", "last_updated", "security_type", "issuer_name", "currency_code", "isin", "us_code", "final_issue_price", "min_shares_offered", "max_shares_offered", "lowest_offer_price", "highest_offer_price", "total_offer_size", "shares_outstanding", "primary_exchange", "lot_size", "security_description", "ipo_status", "announced_date"] | None = Field(None, description="Field to sort by, such as listing date, ticker symbol, issuer name, offering price, or IPO status. Defaults to listing date."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a list of Initial Public Offerings with detailed information including issuer names, ticker symbols, pricing, and offering details. Filter by status (new, pending, historical, etc.) and customize sorting and pagination."""

    # Construct request model with validation
    try:
        _request = _models.ListIpOsRequest(
            query=_models.ListIpOsRequestQuery(listing_date=listing_date, ipo_status=ipo_status, order=order, limit=limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_ipos_detailed: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/vX/reference/ipos"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_ipos_detailed")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_ipos_detailed", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_ipos_detailed",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: reference:tickers:get
@mcp.tool()
async def list_ticker_events(
    id_: str = Field(..., alias="id", description="The security identifier as a ticker symbol (case-sensitive, e.g., AAPL), CUSIP, or Composite FIGI. When using a ticker, events are returned for the entity currently represented by that ticker; use the Ticker Details endpoint to find identifiers for entities previously associated with a ticker."),
    types: str | None = Field(None, description="Filter results by event type using a comma-separated list. Currently supports ticker_change. Omit to return all available event types."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a chronological timeline of corporate events for a security identified by ticker symbol, CUSIP, or Composite FIGI. Returns events for the entity currently associated with the identifier."""

    # Construct request model with validation
    try:
        _request = _models.GetEventsRequest(
            path=_models.GetEventsRequestPath(id_=id_),
            query=_models.GetEventsRequestQuery(types=types)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_ticker_events: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/vX/reference/tickers/{id}/events", _request.path.model_dump(by_alias=True)) if _request.path else "/vX/reference/tickers/{id}/events"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_ticker_events")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_ticker_events", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_ticker_events",
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
        print("  python polygon_api_server.py", file=sys.stderr)
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

    parser = argparse.ArgumentParser(description="Polygon API MCP Server")

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
    logger.info("Starting Polygon API MCP Server")
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

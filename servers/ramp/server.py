#!/usr/bin/env python3
"""
Ramp Developer API MCP Server
Generated: 2026-05-05 16:05:49 UTC
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
from typing import Any, Literal, cast

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

BASE_URL = os.getenv("BASE_URL", "https://api.ramp.com")
SERVER_NAME = "Ramp Developer API"
SERVER_VERSION = "1.0.1"

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


def _resolve_request_url(base_url: str, path: str) -> str:
    """Resolve request URL without duplicating absolute API prefixes.

    Some specs provide a base URL with a path prefix (for example
    ``https://host/admin/api/2024-01``) while operation paths are already
    absolute from the API root (for example ``/admin/api/2020-01/shop.json``).
    Passing that path directly to an httpx client with ``base_url`` would
    incorrectly produce ``.../admin/api/2024-01/admin/api/2020-01/...``.

    When the request path already starts with the same absolute API root (or
    the base URL path itself), send it against the origin instead.
    """
    if not path or "://" in path or not path.startswith("/"):
        return path

    try:
        base = httpx.URL(base_url)
    except Exception:
        return path

    if not base.host:
        return path

    if base.port is not None:
        origin = f"{base.scheme}://{base.host}:{base.port}"
    else:
        origin = f"{base.scheme}://{base.host}"

    base_path = (base.path or "").rstrip("/")
    if not base_path:
        return path

    base_parent = base_path.rsplit("/", 1)[0] if "/" in base_path else ""
    if path == base_path or path.startswith(base_path + "/"):
        return f"{origin}{path}"
    if base_parent and base_parent != "/" and (path == base_parent or path.startswith(base_parent + "/")):
        return f"{origin}{path}"
    return path


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
    _request_url = _resolve_request_url(BASE_URL, path)

    last_error: httpx.HTTPStatusError | Exception | None = None
    _auth_retried = False  # Guard: only attempt one auth refresh per request
    for attempt in range(max_attempts):
        try:
            # Dispatch body to correct httpx kwarg based on content type
            _json = body if body_content_type is None or body_content_type == "application/json" else None
            _form_content: bytes | str | None = None
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
            _content: bytes | str | None = None
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
                url=_request_url,
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
    'oauth2',
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

mcp = FastMCP("Ramp Developer API", middleware=[_JsonCoercionMiddleware()])

# Tags: Accounting
@mcp.tool()
async def list_gl_accounts(
    remote_id: str | None = Field(None, description="Filter results to accounts matching this external or remote system identifier."),
    is_active: bool | None = Field(None, description="Filter by account active status: true returns only active accounts, false returns only inactive accounts, omitting this parameter returns all accounts regardless of status."),
    code: str | None = Field(None, description="Filter results to accounts matching this account code."),
    page_size: int | None = Field(None, description="Number of results per page, between 2 and 100 inclusive. Defaults to 20 if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of general ledger accounts with optional filtering by remote ID, active status, or account code."""

    # Construct request model with validation
    try:
        _request = _models.GetGlAccountListResourceRequest(
            query=_models.GetGlAccountListResourceRequestQuery(remote_id=remote_id, is_active=is_active, code=code, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_gl_accounts: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/accounting/accounts"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_gl_accounts")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_gl_accounts", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_gl_accounts",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Accounting
@mcp.tool()
async def create_gl_accounts(gl_accounts: list[_models.GlAccount] = Field(..., description="A list of general ledger accounts to upload for transaction classification. Accepts between 1 and 500 accounts per request. All accounts in the batch must be valid; a single malformed account will cause the entire batch to be rejected.", min_length=1, max_length=500)) -> dict[str, Any] | ToolResult:
    """Batch upload general ledger accounts to classify Ramp transactions. Uploads are all-or-nothing: if any account in the batch is malformed or violates constraints, the entire batch is rejected. Ensure accounts don't already exist on Ramp; use the PATCH endpoint to update existing accounts instead."""

    # Construct request model with validation
    try:
        _request = _models.PostGlAccountListResourceRequest(
            body=_models.PostGlAccountListResourceRequestBody(gl_accounts=gl_accounts)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_gl_accounts: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/accounting/accounts"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_gl_accounts")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_gl_accounts", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_gl_accounts",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Accounting
@mcp.tool()
async def get_gl_account(gl_account_id: str = Field(..., description="The unique identifier (UUID) of the general ledger account to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve a specific general ledger account by its unique identifier. Returns the account details for accounting and financial reporting purposes."""

    # Construct request model with validation
    try:
        _request = _models.GetGlAccountResourceRequest(
            path=_models.GetGlAccountResourceRequestPath(gl_account_id=gl_account_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_gl_account: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/accounting/accounts/{gl_account_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/accounting/accounts/{gl_account_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_gl_account")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_gl_account", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_gl_account",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Accounting
@mcp.tool()
async def update_gl_account(
    gl_account_id: str = Field(..., description="The unique identifier (UUID) of the general ledger account to update."),
    code: str | None = Field(None, description="The new code for the general ledger account. Provide an empty string to clear the existing code."),
    name: str | None = Field(None, description="The new name for the general ledger account."),
    reactivate: Literal[True] | None = Field(None, description="Set to true to reactivate a deleted general ledger account."),
) -> dict[str, Any] | ToolResult:
    """Update a general ledger account's name or code, or reactivate a previously deleted account."""

    # Construct request model with validation
    try:
        _request = _models.PatchGlAccountResourceRequest(
            path=_models.PatchGlAccountResourceRequestPath(gl_account_id=gl_account_id),
            body=_models.PatchGlAccountResourceRequestBody(code=code, name=name, reactivate=reactivate)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_gl_account: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/accounting/accounts/{gl_account_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/accounting/accounts/{gl_account_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_gl_account")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_gl_account", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_gl_account",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Accounting
@mcp.tool()
async def delete_gl_account(gl_account_id: str = Field(..., description="The unique identifier of the general ledger account to delete, provided as a UUID.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a general ledger account from the accounting system. This operation removes the account and cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteGlAccountResourceRequest(
            path=_models.DeleteGlAccountResourceRequestPath(gl_account_id=gl_account_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_gl_account: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/accounting/accounts/{gl_account_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/accounting/accounts/{gl_account_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_gl_account")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_gl_account", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_gl_account",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Accounting
@mcp.tool()
async def list_accounting_connections() -> dict[str, Any] | ToolResult:
    """Retrieve all accounting connections configured for the current business. This returns a complete list of integrated accounting systems and their connection details."""

    # Extract parameters for API call
    _http_path = "/developer/v1/accounting/all-connections"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_accounting_connections")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_accounting_connections", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_accounting_connections",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Accounting
@mcp.tool()
async def create_accounting_connection(
    remote_provider_name: str = Field(..., description="The name of the accounting provider (e.g., QuickBooks, Xero, NetSuite). This identifies which accounting system to connect."),
    settings: _models.PostAccountingConnectionResourceBodySettings | None = Field(None, description="Optional configuration settings specific to the accounting provider's API connection. Settings vary by provider and are only applicable to API-based connections."),
) -> dict[str, Any] | ToolResult:
    """Register a new API-based accounting connection to enable accounting API functionality. If a Universal CSV connection already exists for the provider, it will be automatically upgraded to an API-based connection."""

    # Construct request model with validation
    try:
        _request = _models.PostAccountingConnectionResourceRequest(
            body=_models.PostAccountingConnectionResourceRequestBody(remote_provider_name=remote_provider_name, settings=settings)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_accounting_connection: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/accounting/connection"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_accounting_connection")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_accounting_connection", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_accounting_connection",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Accounting
@mcp.tool()
async def disconnect_accounting_connection() -> dict[str, Any] | ToolResult:
    """Disconnect an active accounting connection. This operation only supports API-based connections and will remove the integration link between your application and the accounting system."""

    # Extract parameters for API call
    _http_path = "/developer/v1/accounting/connection"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("disconnect_accounting_connection")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("disconnect_accounting_connection", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="disconnect_accounting_connection",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Accounting
@mcp.tool()
async def get_accounting_connection(connection_id: str = Field(..., description="The unique identifier of the accounting connection to retrieve. This ID is used to look up the specific connection record in the system.")) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific accounting connection by its unique identifier. Use this to fetch connection settings, status, and configuration details."""

    # Construct request model with validation
    try:
        _request = _models.GetAccountingConnectionDetailResourceRequest(
            path=_models.GetAccountingConnectionDetailResourceRequestPath(connection_id=connection_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_accounting_connection: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/accounting/connection/{connection_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/accounting/connection/{connection_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_accounting_connection")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_accounting_connection", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_accounting_connection",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Accounting
@mcp.tool()
async def update_accounting_connection(
    connection_id: str = Field(..., description="The unique identifier of the accounting connection to update."),
    settings: _models.PatchAccountingConnectionDetailResourceBodySettings | None = Field(None, description="Configuration settings for the accounting connection. Only applicable to API-based connections; settings vary depending on the connection type and provider requirements."),
) -> dict[str, Any] | ToolResult:
    """Update the configuration settings for an accounting connection. This operation is restricted to API-based accounting connections and allows you to modify connection-specific settings."""

    # Construct request model with validation
    try:
        _request = _models.PatchAccountingConnectionDetailResourceRequest(
            path=_models.PatchAccountingConnectionDetailResourceRequestPath(connection_id=connection_id),
            body=_models.PatchAccountingConnectionDetailResourceRequestBody(settings=settings)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_accounting_connection: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/accounting/connection/{connection_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/accounting/connection/{connection_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_accounting_connection")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_accounting_connection", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_accounting_connection",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Accounting
@mcp.tool()
async def reactivate_accounting_connection(connection_id: str = Field(..., description="The unique identifier (UUID) of the accounting connection to reactivate.")) -> dict[str, Any] | ToolResult:
    """Reactivate a previously disconnected accounting connection, restoring it to active status while preserving all previous field configurations and settings. The business must not have any other active accounting connections at the time of reactivation."""

    # Construct request model with validation
    try:
        _request = _models.PostReactivateConnectionResourceRequest(
            path=_models.PostReactivateConnectionResourceRequestPath(connection_id=connection_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for reactivate_accounting_connection: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/accounting/connection/{connection_id}/reactivate", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/accounting/connection/{connection_id}/reactivate"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("reactivate_accounting_connection")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("reactivate_accounting_connection", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="reactivate_accounting_connection",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Accounting
@mcp.tool()
async def list_custom_field_options(
    field_id: str = Field(..., description="The unique identifier (ramp_id) of the custom accounting field whose options you want to retrieve. This is a UUID that must be obtained from custom field endpoints."),
    remote_id: str | None = Field(None, description="Filter results by the external ID of custom accounting field options as they appear in the ERP system."),
    is_active: bool | None = Field(None, description="Filter by active status: true returns only active options, false returns only inactive options, and omitting this parameter returns all options regardless of status."),
    code: str | None = Field(None, description="Filter results by the code identifier of custom accounting field options."),
    visibility: Literal["HIDDEN", "VISIBLE"] | None = Field(None, description="Filter by visibility setting: either HIDDEN or VISIBLE. Omitting this parameter returns options with any visibility level."),
    page_size: int | None = Field(None, description="The number of results to return per page, between 2 and 100 inclusive. Defaults to 20 if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of options available for a specific custom accounting field, with optional filtering by remote ID, active status, code, or visibility."""

    # Construct request model with validation
    try:
        _request = _models.GetCustomFieldOptionListResourceRequest(
            query=_models.GetCustomFieldOptionListResourceRequestQuery(remote_id=remote_id, is_active=is_active, code=code, visibility=visibility, field_id=field_id, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_custom_field_options: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/accounting/field-options"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_custom_field_options")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_custom_field_options", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_custom_field_options",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Accounting
@mcp.tool()
async def create_custom_field_options(
    field_id: str = Field(..., description="The UUID of the custom accounting field to which these options belong. This is the ramp_id returned from custom field endpoints."),
    options: list[_models.FieldOption] = Field(..., description="A list of field options to upload for the specified custom accounting field. Must contain between 1 and 500 options. All options in the batch are processed together; if any option is invalid, the entire batch is rejected.", min_length=1, max_length=500),
) -> dict[str, Any] | ToolResult:
    """Batch upload new options for a custom accounting field. Up to 500 options can be uploaded at once in an all-or-nothing transaction—if any option is malformed or violates constraints, the entire batch is rejected. Ensure options don't already exist on Ramp; use the PATCH endpoint to update existing options instead."""

    # Construct request model with validation
    try:
        _request = _models.PostCustomFieldOptionListResourceRequest(
            body=_models.PostCustomFieldOptionListResourceRequestBody(field_id=field_id, options=options)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_custom_field_options: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/accounting/field-options"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_custom_field_options")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_custom_field_options", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_custom_field_options",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Accounting
@mcp.tool()
async def get_custom_field_option(field_option_id: str = Field(..., description="The unique identifier (UUID) of the custom field option to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve a specific custom accounting field option by its unique identifier. Use this to fetch details about a predefined option value for a custom accounting field."""

    # Construct request model with validation
    try:
        _request = _models.GetCustomFieldOptionResourceRequest(
            path=_models.GetCustomFieldOptionResourceRequestPath(field_option_id=field_option_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_custom_field_option: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/accounting/field-options/{field_option_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/accounting/field-options/{field_option_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_custom_field_option")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_custom_field_option", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_custom_field_option",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Accounting
@mcp.tool()
async def update_custom_field_option(
    field_option_id: str = Field(..., description="The unique identifier (UUID format) of the custom field option to update."),
    code: str | None = Field(None, description="The code identifier for this custom field option. You can provide an empty string to clear the code. Only available for non-ERP integrated systems."),
    reactivate: Literal[True] | None = Field(None, description="Set to true to reactivate a previously deleted custom field option. Only available for non-ERP integrated systems."),
    value: str | None = Field(None, description="The display name of the custom field option. Only available for non-ERP integrated systems."),
    visibility: Literal["HIDDEN", "VISIBLE"] | None = Field(None, description="Controls whether this option is visible or hidden in the UI. Must be either VISIBLE or HIDDEN."),
) -> dict[str, Any] | ToolResult:
    """Update a custom accounting field option by modifying its code, name, visibility, or reactivation status. Only available for non-ERP integrated systems."""

    # Construct request model with validation
    try:
        _request = _models.PutCustomFieldOptionResourceRequest(
            path=_models.PutCustomFieldOptionResourceRequestPath(field_option_id=field_option_id),
            body=_models.PutCustomFieldOptionResourceRequestBody(code=code, reactivate=reactivate, value=value, visibility=visibility)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_custom_field_option: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/accounting/field-options/{field_option_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/accounting/field-options/{field_option_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_custom_field_option")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_custom_field_option", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_custom_field_option",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Accounting
@mcp.tool()
async def update_custom_field_option_partial(
    field_option_id: str = Field(..., description="The unique identifier (UUID format) of the custom field option to update."),
    code: str | None = Field(None, description="The code identifier for this custom field option. You can provide an empty string to clear the code. Only available for non-ERP integrated systems."),
    reactivate: Literal[True] | None = Field(None, description="Set to true to reactivate a previously deleted custom field option. Only available for non-ERP integrated systems."),
    value: str | None = Field(None, description="The display name of the custom field option. Only available for non-ERP integrated systems."),
    visibility: Literal["HIDDEN", "VISIBLE"] | None = Field(None, description="Controls whether this option is visible or hidden in the UI. Must be either VISIBLE or HIDDEN."),
) -> dict[str, Any] | ToolResult:
    """Update a custom accounting field option by modifying its code, value, visibility, or reactivation status. Only available for non-ERP integrated systems."""

    # Construct request model with validation
    try:
        _request = _models.PatchCustomFieldOptionResourceRequest(
            path=_models.PatchCustomFieldOptionResourceRequestPath(field_option_id=field_option_id),
            body=_models.PatchCustomFieldOptionResourceRequestBody(code=code, reactivate=reactivate, value=value, visibility=visibility)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_custom_field_option_partial: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/accounting/field-options/{field_option_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/accounting/field-options/{field_option_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_custom_field_option_partial")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_custom_field_option_partial", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_custom_field_option_partial",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Accounting
@mcp.tool()
async def delete_custom_field_option(field_option_id: str = Field(..., description="The unique identifier (UUID) of the custom field option to delete.")) -> dict[str, Any] | ToolResult:
    """Delete a custom accounting field option by its unique identifier. This operation permanently removes the field option from the accounting system."""

    # Construct request model with validation
    try:
        _request = _models.DeleteCustomFieldOptionResourceRequest(
            path=_models.DeleteCustomFieldOptionResourceRequestPath(field_option_id=field_option_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_custom_field_option: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/accounting/field-options/{field_option_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/accounting/field-options/{field_option_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_custom_field_option")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_custom_field_option", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_custom_field_option",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Accounting
@mcp.tool()
async def list_custom_accounting_fields(
    remote_id: str | None = Field(None, description="Filter results to custom accounting fields matching a specific remote or external ID in your ERP system."),
    is_active: bool | None = Field(None, description="Filter by field status: omit to return all fields, true for active fields only, or false for inactive fields only."),
    page_size: int | None = Field(None, description="Number of results per page, between 2 and 100 (defaults to 20 if not specified)."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of custom accounting fields from your ERP system, with optional filtering by remote ID and active status."""

    # Construct request model with validation
    try:
        _request = _models.GetCustomFieldListResourceRequest(
            query=_models.GetCustomFieldListResourceRequestQuery(remote_id=remote_id, is_active=is_active, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_custom_accounting_fields: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/accounting/fields"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_custom_accounting_fields")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_custom_accounting_fields", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_custom_accounting_fields",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Accounting
@mcp.tool()
async def create_accounting_custom_field(
    id_: str = Field(..., alias="id", description="The unique identifier for this custom field in your ERP system. This ID is used to match and prevent duplicate fields."),
    input_type: Literal["BOOLEAN", "FREE_FORM_TEXT", "SINGLE_CHOICE"] = Field(..., description="The data type for user input: BOOLEAN for true/false values, FREE_FORM_TEXT for open-ended text, or SINGLE_CHOICE for predefined options."),
    name: str = Field(..., description="The display name for this custom accounting field as it will appear in the UI."),
    is_required_for: list[Literal["BILL", "BILL_PAYMENT", "INVOICE", "PURCHASE_ORDER", "REIMBURSEMENT", "TRANSACTION", "VENDOR_CREDIT"]] | None = Field(None, description="An optional list of object types that must have this field populated before they can be marked as ready to sync (e.g., expenses, invoices)."),
    is_splittable: bool | None = Field(None, description="Optional flag to allow this field to annotate individual split line items within a transaction. Defaults to false if not specified."),
) -> dict[str, Any] | ToolResult:
    """Create a new custom accounting field for your ERP system integration. If a field with the same ID already exists, the existing field will be returned; inactive fields will be reactivated. To modify an existing field, use the update endpoint instead."""

    # Construct request model with validation
    try:
        _request = _models.PostCustomFieldListResourceRequest(
            body=_models.PostCustomFieldListResourceRequestBody(id_=id_, input_type=input_type, is_required_for=is_required_for, is_splittable=is_splittable, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_accounting_custom_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/accounting/fields"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_accounting_custom_field")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_accounting_custom_field", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_accounting_custom_field",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Accounting
@mcp.tool()
async def get_custom_field(field_id: str = Field(..., description="The unique identifier (UUID) of the custom accounting field to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve a custom accounting field by its unique identifier. Use this to fetch detailed information about a specific custom field configured in your accounting system."""

    # Construct request model with validation
    try:
        _request = _models.GetCustomFieldResourceRequest(
            path=_models.GetCustomFieldResourceRequestPath(field_id=field_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_custom_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/accounting/fields/{field_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/accounting/fields/{field_id}"
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

# Tags: Accounting
@mcp.tool()
async def update_custom_accounting_field(
    field_id: str = Field(..., description="The unique identifier (UUID) of the custom accounting field to update."),
    is_splittable: bool | None = Field(None, description="Whether this custom field can be split across multiple line items or cost centers."),
    name: str | None = Field(None, description="The display name for the custom accounting field."),
) -> dict[str, Any] | ToolResult:
    """Update properties of a custom accounting field in Ramp, such as its name or splittability configuration. Specify the field by its UUID and provide the properties you want to modify."""

    # Construct request model with validation
    try:
        _request = _models.PatchCustomFieldResourceRequest(
            path=_models.PatchCustomFieldResourceRequestPath(field_id=field_id),
            body=_models.PatchCustomFieldResourceRequestBody(is_splittable=is_splittable, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_custom_accounting_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/accounting/fields/{field_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/accounting/fields/{field_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_custom_accounting_field")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_custom_accounting_field", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_custom_accounting_field",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Accounting
@mcp.tool()
async def delete_custom_field(field_id: str = Field(..., description="The unique identifier (UUID) of the custom accounting field to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a custom accounting field by its unique identifier. This operation removes the field and its associated data from the accounting system."""

    # Construct request model with validation
    try:
        _request = _models.DeleteCustomFieldResourceRequest(
            path=_models.DeleteCustomFieldResourceRequestPath(field_id=field_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_custom_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/accounting/fields/{field_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/accounting/fields/{field_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_custom_field")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_custom_field", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_custom_field",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Accounting
@mcp.tool()
async def list_inventory_item_accounting_fields() -> dict[str, Any] | ToolResult:
    """Retrieve the list of available accounting fields for inventory items in the current accounting connection. Use this to understand which fields can be queried or managed for inventory item operations."""

    # Extract parameters for API call
    _http_path = "/developer/v1/accounting/inventory-item"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_inventory_item_accounting_fields")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_inventory_item_accounting_fields", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_inventory_item_accounting_fields",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Accounting
@mcp.tool()
async def create_inventory_item_accounting_field(name: str = Field(..., description="The name of the inventory item tracking category. This identifies the type of inventory metric or attribute being tracked (e.g., 'Warehouse Location', 'Serial Number', 'Batch ID').")) -> dict[str, Any] | ToolResult:
    """Create a new inventory item accounting field to track a specific category for inventory items within an accounting connection. Only one active field can exist per accounting connection."""

    # Construct request model with validation
    try:
        _request = _models.PostInventoryItemFieldListResourceRequest(
            body=_models.PostInventoryItemFieldListResourceRequestBody(name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_inventory_item_accounting_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/accounting/inventory-item"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_inventory_item_accounting_field")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_inventory_item_accounting_field", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_inventory_item_accounting_field",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Accounting
@mcp.tool()
async def update_inventory_item_field(name: str | None = Field(None, description="The name of the inventory item field to update. Specify which accounting field should be modified.")) -> dict[str, Any] | ToolResult:
    """Update a specific accounting field for an inventory item. Use this to modify individual field values within an inventory item's accounting configuration."""

    # Construct request model with validation
    try:
        _request = _models.PatchInventoryItemFieldListResourceRequest(
            body=_models.PatchInventoryItemFieldListResourceRequestBody(name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_inventory_item_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/accounting/inventory-item"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_inventory_item_field")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_inventory_item_field", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_inventory_item_field",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Accounting
@mcp.tool()
async def delete_inventory_item_accounting_field() -> dict[str, Any] | ToolResult:
    """Remove a custom accounting field from inventory items. This operation deletes the field definition and its associated data across all inventory items."""

    # Extract parameters for API call
    _http_path = "/developer/v1/accounting/inventory-item"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_inventory_item_accounting_field")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_inventory_item_accounting_field", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_inventory_item_accounting_field",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Accounting
@mcp.tool()
async def list_inventory_item_options(
    remote_id: str | None = Field(None, description="Filter results to inventory items matching this external or remote system identifier."),
    is_active: bool | None = Field(None, description="Filter by active status: true returns only active items, false returns only inactive items, and omitting this parameter returns all items regardless of status."),
    code: str | None = Field(None, description="Filter results to inventory items matching this code value."),
    page_size: int | None = Field(None, description="Number of results per page, between 2 and 100 inclusive. Defaults to 20 if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of inventory item field options with optional filtering by remote ID, active status, or code."""

    # Construct request model with validation
    try:
        _request = _models.GetInventoryItemFieldOptionsListResourceRequest(
            query=_models.GetInventoryItemFieldOptionsListResourceRequestQuery(remote_id=remote_id, is_active=is_active, code=code, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_inventory_item_options: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/accounting/inventory-item/options"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_inventory_item_options")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_inventory_item_options", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_inventory_item_options",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Accounting
@mcp.tool()
async def add_inventory_item_options(options: list[_models.InventoryItemOption] = Field(..., description="A list of inventory item options to upload. Must contain between 1 and 500 options. Order is preserved as submitted.", min_length=1, max_length=500)) -> dict[str, Any] | ToolResult:
    """Upload a batch of inventory item options to an active accounting field. Requires an active inventory item accounting field configured for the accounting connection."""

    # Construct request model with validation
    try:
        _request = _models.PostInventoryItemFieldOptionsListResourceRequest(
            body=_models.PostInventoryItemFieldOptionsListResourceRequestBody(options=options)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_inventory_item_options: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/accounting/inventory-item/options"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_inventory_item_options")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_inventory_item_options", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_inventory_item_options",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Accounting
@mcp.tool()
async def update_inventory_item_option(
    option_id: str = Field(..., description="The unique identifier of the inventory item option to update."),
    name: str | None = Field(None, description="The new name for the inventory item option."),
    reactivate: Literal[True] | None = Field(None, description="Reactivate a deleted inventory item option. When provided, this parameter must be set to true; false is not a valid value."),
) -> dict[str, Any] | ToolResult:
    """Update an inventory item option by modifying its name or reactivating a previously deleted option."""

    # Construct request model with validation
    try:
        _request = _models.PatchInventoryItemFieldOptionResourceRequest(
            path=_models.PatchInventoryItemFieldOptionResourceRequestPath(option_id=option_id),
            body=_models.PatchInventoryItemFieldOptionResourceRequestBody(name=name, reactivate=reactivate)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_inventory_item_option: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/accounting/inventory-item/options/{option_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/accounting/inventory-item/options/{option_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_inventory_item_option")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_inventory_item_option", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_inventory_item_option",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Accounting
@mcp.tool()
async def delete_inventory_item_option(option_id: str = Field(..., description="The unique identifier of the inventory item option to delete.")) -> dict[str, Any] | ToolResult:
    """Delete a specific inventory item option by its ID. This operation removes the option from the system permanently."""

    # Construct request model with validation
    try:
        _request = _models.DeleteInventoryItemFieldOptionResourceRequest(
            path=_models.DeleteInventoryItemFieldOptionResourceRequestPath(option_id=option_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_inventory_item_option: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/accounting/inventory-item/options/{option_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/accounting/inventory-item/options/{option_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_inventory_item_option")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_inventory_item_option", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_inventory_item_option",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Accounting
@mcp.tool()
async def mark_transactions_ready_to_sync(
    object_ids: list[str] = Field(..., description="A list of transaction IDs to mark as ready for sync. Provide between 1 and 500 object IDs per request.", min_length=1, max_length=500),
    object_type: Literal["TRANSACTION"] = Field(..., description="The type of object being marked for sync. Currently supports TRANSACTION objects only."),
) -> dict[str, Any] | ToolResult:
    """Mark one or more accounting transactions as ready to sync. This notifies the system that the specified transactions are prepared for synchronization."""

    # Construct request model with validation
    try:
        _request = _models.PostReadyToSyncResourceRequest(
            body=_models.PostReadyToSyncResourceRequestBody(object_ids=object_ids, object_type=object_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for mark_transactions_ready_to_sync: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/accounting/ready-to-sync"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("mark_transactions_ready_to_sync")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("mark_transactions_ready_to_sync", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="mark_transactions_ready_to_sync",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Accounting
@mcp.tool()
async def report_sync_results(
    idempotency_key: str = Field(..., description="A unique identifier for this request, typically a randomly generated UUID. The server uses this to recognize and deduplicate retries of the same request."),
    sync_type: Literal["BILL_PAYMENT_SYNC", "BILL_SYNC", "BROKERAGE_ORDER_SYNC", "REIMBURSEMENT_SYNC", "STATEMENT_CREDIT_SYNC", "TRANSACTION_SYNC", "TRANSFER_SYNC", "WALLET_TRANSFER_SYNC"] = Field(..., description="The category of objects being synced. Must be one of: BILL_PAYMENT_SYNC, BILL_SYNC, BROKERAGE_ORDER_SYNC, REIMBURSEMENT_SYNC, STATEMENT_CREDIT_SYNC, TRANSACTION_SYNC, TRANSFER_SYNC, or WALLET_TRANSFER_SYNC."),
    failed_syncs: list[_models.ApiAccountingFailedSyncRequestBody] | None = Field(None, description="A list of objects that failed to sync, containing between 1 and 5000 items. Include this when reporting sync failures.", min_length=1, max_length=5000),
    successful_syncs: list[_models.ApiAccountingSuccessfulSyncRequestBody] | None = Field(None, description="A list of objects that were successfully synced, containing between 1 and 5000 items. Include this when reporting sync successes.", min_length=1, max_length=5000),
) -> dict[str, Any] | ToolResult:
    """Report the results of a batch sync operation to Ramp, specifying which objects succeeded and which failed. An idempotency key ensures safe retry handling."""

    # Construct request model with validation
    try:
        _request = _models.PostSyncListResourceRequest(
            body=_models.PostSyncListResourceRequestBody(failed_syncs=failed_syncs, idempotency_key=idempotency_key, successful_syncs=successful_syncs, sync_type=sync_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for report_sync_results: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/accounting/syncs"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("report_sync_results")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("report_sync_results", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="report_sync_results",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Accounting
@mcp.tool()
async def get_tax_code_field() -> dict[str, Any] | ToolResult:
    """Retrieve the tax code accounting field configured for the current accounting connection. This field is used to classify transactions for tax reporting purposes."""

    # Extract parameters for API call
    _http_path = "/developer/v1/accounting/tax/code"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_tax_code_field")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_tax_code_field", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_tax_code_field",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Accounting
@mcp.tool()
async def create_tax_code_field(name: str = Field(..., description="The display name for the tax code accounting field. This name identifies the field within the accounting system.")) -> dict[str, Any] | ToolResult:
    """Create a new tax code accounting field for an accounting connection. Only one active tax code field can exist per connection, so creating a new one will replace any existing field."""

    # Construct request model with validation
    try:
        _request = _models.PostTaxCodeFieldResourceRequest(
            body=_models.PostTaxCodeFieldResourceRequestBody(name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_tax_code_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/accounting/tax/code"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_tax_code_field")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_tax_code_field", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_tax_code_field",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Accounting
@mcp.tool()
async def update_tax_code_field(name: str | None = Field(None, description="The new name for the tax code field. This identifier is used to reference the tax code in accounting operations.")) -> dict[str, Any] | ToolResult:
    """Update the name or other properties of a tax code accounting field. Use this operation to modify an existing tax code field's configuration."""

    # Construct request model with validation
    try:
        _request = _models.PatchTaxCodeFieldResourceRequest(
            body=_models.PatchTaxCodeFieldResourceRequestBody(name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_tax_code_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/accounting/tax/code"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_tax_code_field")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_tax_code_field", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_tax_code_field",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Accounting
@mcp.tool()
async def delete_tax_code() -> dict[str, Any] | ToolResult:
    """Remove a tax code from the accounting system. This operation deletes the tax code field resource and its associated configuration."""

    # Extract parameters for API call
    _http_path = "/developer/v1/accounting/tax/code"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_tax_code")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_tax_code", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_tax_code",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Accounting
@mcp.tool()
async def list_tax_code_options(
    remote_id: str | None = Field(None, description="Filter results to tax codes matching this remote or external identifier from your source system."),
    is_active: bool | None = Field(None, description="Filter by active status: omit to return all tax codes, true for active only, or false for inactive only."),
    code: str | None = Field(None, description="Filter results to tax codes matching this code value exactly."),
    page_size: int | None = Field(None, description="Number of results per page, between 2 and 100 (defaults to 20 if not specified)."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of available tax code options, with optional filtering by remote ID, active status, or code value. Use this to populate dropdowns or validate tax code selections in accounting workflows."""

    # Construct request model with validation
    try:
        _request = _models.GetTaxCodeFieldOptionsListResourceRequest(
            query=_models.GetTaxCodeFieldOptionsListResourceRequestQuery(remote_id=remote_id, is_active=is_active, code=code, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_tax_code_options: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/accounting/tax/code/options"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_tax_code_options")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_tax_code_options", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_tax_code_options",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Accounting
@mcp.tool()
async def add_tax_code_options(options: list[_models.TaxCodeOption] = Field(..., description="A list of tax code options to upload. Must contain between 1 and 500 options.", min_length=1, max_length=500)) -> dict[str, Any] | ToolResult:
    """Upload tax code options to an active tax code accounting field. Requires an active tax code accounting field to be configured for the accounting connection."""

    # Construct request model with validation
    try:
        _request = _models.PostTaxCodeFieldOptionsListResourceRequest(
            body=_models.PostTaxCodeFieldOptionsListResourceRequestBody(options=options)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_tax_code_options: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/accounting/tax/code/options"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_tax_code_options")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_tax_code_options", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_tax_code_options",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Accounting
@mcp.tool()
async def update_tax_code_option(
    option_id: str = Field(..., description="The unique identifier of the tax code option to update."),
    name: str | None = Field(None, description="The display name for this tax code option."),
    tax_rate_ids: list[str] | None = Field(None, description="A list of external tax rate IDs (remote_id values) to associate with this tax code option. Providing this value will replace all existing tax rate associations. Order is not significant."),
) -> dict[str, Any] | ToolResult:
    """Update the name and associated tax rates for a specific tax code option. Changes to tax rate associations will replace all existing associations for this option."""

    # Construct request model with validation
    try:
        _request = _models.PatchTaxCodeFieldOptionResourceRequest(
            path=_models.PatchTaxCodeFieldOptionResourceRequestPath(option_id=option_id),
            body=_models.PatchTaxCodeFieldOptionResourceRequestBody(name=name, tax_rate_ids=tax_rate_ids)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_tax_code_option: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/accounting/tax/code/options/{option_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/accounting/tax/code/options/{option_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_tax_code_option")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_tax_code_option", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_tax_code_option",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Accounting
@mcp.tool()
async def delete_tax_code_option(option_id: str = Field(..., description="The unique identifier of the tax code option to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a tax code option from the accounting system. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteTaxCodeFieldOptionResourceRequest(
            path=_models.DeleteTaxCodeFieldOptionResourceRequestPath(option_id=option_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_tax_code_option: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/accounting/tax/code/options/{option_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/accounting/tax/code/options/{option_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_tax_code_option")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_tax_code_option", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_tax_code_option",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Accounting
@mcp.tool()
async def list_tax_rates(page_size: int | None = Field(None, description="Number of tax rates to return per page. Must be between 2 and 100 results; defaults to 20 if not specified.")) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of tax rates configured in the accounting system. Use the page_size parameter to control how many results are returned per page."""

    # Construct request model with validation
    try:
        _request = _models.GetTaxCodeRatesListResourceRequest(
            query=_models.GetTaxCodeRatesListResourceRequestQuery(page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_tax_rates: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/accounting/tax/rates"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_tax_rates")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_tax_rates", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_tax_rates",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Accounting
@mcp.tool()
async def upload_tax_rates(tax_rates: list[_models.TaxRate] = Field(..., description="A list of tax rates to upload, containing between 1 and 500 rates. Each rate must be properly formatted and not already exist in your Ramp account.", min_length=1, max_length=500)) -> dict[str, Any] | ToolResult:
    """Upload a batch of tax rates to your Ramp account. All rates in the batch are processed together—if any rate is malformed or violates constraints, the entire upload is rejected. Ensure rates are properly formatted and don't already exist in your system."""

    # Construct request model with validation
    try:
        _request = _models.PostTaxCodeRatesListResourceRequest(
            body=_models.PostTaxCodeRatesListResourceRequestBody(tax_rates=tax_rates)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for upload_tax_rates: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/accounting/tax/rates"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("upload_tax_rates")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("upload_tax_rates", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="upload_tax_rates",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Accounting
@mcp.tool()
async def update_tax_rate(
    tax_rate_id: str = Field(..., description="The unique identifier of the tax rate to update."),
    accounting_gl_account_id: str | None = Field(None, description="The Ramp ID of the GL account to associate with this tax rate. Must be a valid UUID format."),
    name: str | None = Field(None, description="The display name for the tax rate."),
    rate: str | None = Field(None, description="The tax rate percentage expressed as a decimal value (e.g., 0.10 for 10%)."),
) -> dict[str, Any] | ToolResult:
    """Update an existing tax rate's configuration, including its name, rate percentage, and associated GL account."""

    # Construct request model with validation
    try:
        _request = _models.PatchTaxRateDetailResourceRequest(
            path=_models.PatchTaxRateDetailResourceRequestPath(tax_rate_id=tax_rate_id),
            body=_models.PatchTaxRateDetailResourceRequestBody(accounting_gl_account_id=accounting_gl_account_id, name=name, rate=rate)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_tax_rate: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/accounting/tax/rates/{tax_rate_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/accounting/tax/rates/{tax_rate_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_tax_rate")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_tax_rate", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_tax_rate",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Accounting
@mcp.tool()
async def delete_tax_rate(tax_rate_id: str = Field(..., description="The unique identifier of the tax rate to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a tax rate from the accounting system. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteTaxRateDetailResourceRequest(
            path=_models.DeleteTaxRateDetailResourceRequestPath(tax_rate_id=tax_rate_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_tax_rate: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/accounting/tax/rates/{tax_rate_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/accounting/tax/rates/{tax_rate_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_tax_rate")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_tax_rate", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_tax_rate",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Accounting
@mcp.tool()
async def list_vendors_accounting(
    remote_id: str | None = Field(None, description="Filter results to vendors matching this remote or external identifier."),
    is_active: bool | None = Field(None, description="Filter by vendor active status: true returns only active vendors, false returns only inactive vendors, and omitting this parameter returns all vendors regardless of status."),
    code: str | None = Field(None, description="Filter results to vendors matching this code."),
    page_size: int | None = Field(None, description="Number of results per page, between 2 and 100 inclusive. Defaults to 20 if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of accounting vendors with optional filtering by remote ID, active status, or vendor code."""

    # Construct request model with validation
    try:
        _request = _models.GetAccountingVendorListResourceRequest(
            query=_models.GetAccountingVendorListResourceRequestQuery(remote_id=remote_id, is_active=is_active, code=code, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_vendors_accounting: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/accounting/vendors"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_vendors_accounting")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_vendors_accounting", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_vendors_accounting",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Accounting
@mcp.tool()
async def create_vendors(vendors: list[_models.AccountingVendor] = Field(..., description="A list of vendor objects to upload for transaction classification. Between 1 and 500 vendors can be submitted per request. Each vendor must be properly formatted and not already exist in Ramp.", min_length=1, max_length=500)) -> dict[str, Any] | ToolResult:
    """Batch upload vendors to classify Ramp transactions. Uploads are all-or-nothing: if any vendor in the batch is malformed or violates constraints, the entire batch is rejected. Ensure vendors are sanitized and don't already exist in Ramp; use the update endpoint instead for modifying existing vendors."""

    # Construct request model with validation
    try:
        _request = _models.PostAccountingVendorListResourceRequest(
            body=_models.PostAccountingVendorListResourceRequestBody(vendors=vendors)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_vendors: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/accounting/vendors"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_vendors")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_vendors", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_vendors",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Accounting
@mcp.tool()
async def get_vendor_accounting(vendor_id: str = Field(..., description="The unique identifier (UUID) of the vendor to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific accounting vendor by its unique identifier."""

    # Construct request model with validation
    try:
        _request = _models.GetAccountingVendorResourceRequest(
            path=_models.GetAccountingVendorResourceRequestPath(vendor_id=vendor_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_vendor_accounting: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/accounting/vendors/{vendor_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/accounting/vendors/{vendor_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_vendor_accounting")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_vendor_accounting", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_vendor_accounting",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Accounting
@mcp.tool()
async def update_vendor_accounting(
    vendor_id: str = Field(..., description="The unique identifier of the vendor to update, formatted as a UUID."),
    code: str | None = Field(None, description="The vendor's code identifier. Provide an empty string to clear the existing code."),
    name: str | None = Field(None, description="The display name of the vendor."),
    reactivate: Literal[True] | None = Field(None, description="Set to true to restore a vendor that was previously deleted."),
) -> dict[str, Any] | ToolResult:
    """Update vendor details including name and code, or reactivate a previously deleted vendor. Provide only the fields you want to modify."""

    # Construct request model with validation
    try:
        _request = _models.PatchAccountingVendorResourceRequest(
            path=_models.PatchAccountingVendorResourceRequestPath(vendor_id=vendor_id),
            body=_models.PatchAccountingVendorResourceRequestBody(code=code, name=name, reactivate=reactivate)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_vendor_accounting: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/accounting/vendors/{vendor_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/accounting/vendors/{vendor_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_vendor_accounting")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_vendor_accounting", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_vendor_accounting",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Accounting
@mcp.tool()
async def delete_vendor_accounting(vendor_id: str = Field(..., description="The unique identifier (UUID) of the vendor to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete an accounting vendor by its unique identifier. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteAccountingVendorResourceRequest(
            path=_models.DeleteAccountingVendorResourceRequestPath(vendor_id=vendor_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_vendor_accounting: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/accounting/vendors/{vendor_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/accounting/vendors/{vendor_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_vendor_accounting")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_vendor_accounting", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_vendor_accounting",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Application
@mcp.tool()
async def get_application_resource() -> dict[str, Any] | ToolResult:
    """Retrieve the active financing application for the business. Each business can have only one active application at a time, so this endpoint returns a single application resource."""

    # Extract parameters for API call
    _http_path = "/developer/v1/applications"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_application_resource")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_application_resource", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_application_resource",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Application
@mcp.tool()
async def create_financing_application(
    applicant: _models.PostApplicationResourceBodyApplicant = Field(..., description="Required information about the applicant, including their contact details and identification."),
    beneficial_owners: list[_models.ApiApplicationPersonParamsRequestBody] | None = Field(None, description="Optional list of individuals who have beneficial ownership in the business. Order may indicate ownership hierarchy or priority."),
    business: _models.PostApplicationResourceBodyBusiness | None = Field(None, description="Optional business details such as legal name, industry, and operational information."),
    controlling_officer: _models.PostApplicationResourceBodyControllingOfficer | None = Field(None, description="Optional information about the individual with primary control over the business operations and decision-making."),
    financial_details: _models.PostApplicationResourceBodyFinancialDetails | None = Field(None, description="Optional financial information required for underwriting assessment, such as revenue, expenses, and credit metrics."),
    oauth_authorize_params: _models.PostApplicationResourceBodyOauthAuthorizeParams | None = Field(None, description="Optional OAuth parameters that, when provided, will redirect the applicant to an OAuth consent screen after they accept the invitation email."),
) -> dict[str, Any] | ToolResult:
    """Create a new financing application for a business applicant. The applicant will receive an email with instructions to complete their signup and application. If the applicant email already exists, an invitation will be resent for applications in progress, or the operation will have no effect if the business is already approved."""

    # Construct request model with validation
    try:
        _request = _models.PostApplicationResourceRequest(
            body=_models.PostApplicationResourceRequestBody(applicant=applicant, beneficial_owners=beneficial_owners, business=business, controlling_officer=controlling_officer, financial_details=financial_details, oauth_authorize_params=oauth_authorize_params)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_financing_application: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/applications"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_financing_application")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_financing_application", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_financing_application",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Audit Log
@mcp.tool()
async def list_audit_log_events(
    user_ids: list[str] | None = Field(None, description="Filter results to only include events attributed to specific users. Provide an array of user IDs to narrow the results."),
    event_actor_types: list[Literal["policy_agent", "ramp", "user"]] | None = Field(None, description="Filter results to only include events from specific actor types (e.g., user, system, service). Provide an array of actor type values."),
    event_types: list[Literal["ABK agent blocked on user", "ABK agent review requested", "ABK agent started", "AI custom field config executed", "Accounting ai auto mark ready", "Activated card", "Added bill field", "Added card acceptance policy", "Added procurement field", "Added user to funds", "Added vendor field", "Admin changed email", "Admin changed phone", "Agent access request resolved", "Agent access requested", "Agent created", "Agent current version changed", "Agent permissions updated", "Agent version created", "Agent version published", "Approval chain updated", "Approval step added", "Approval step approved", "Approval step rejected", "Approval step skipped", "Approval step terminated", "Approved by manager", "Approved card edit request with modifications", "Approved card edit request", "Approved funds edit request with modifications", "Approved funds edit request", "Approved new card request with modifications", "Approved new card request", "Approved procurement change request", "Approved request for new funds with modifications", "Approved request for new funds", "Attendee split", "Bank account updated", "Bill linked to PO", "Bill linked", "Bill pay accepted sync for bank account from vendor network", "Bill pay accepted sync for vendor card acceptance policy from vendor network", "Bill pay accepted sync for vendor check mailing address from vendor network", "Bill pay accepted sync for vendor information from vendor network", "Bill pay accepted sync for vendor tax info from vendor network", "Bill pay accounting manual user action", "Bill pay accounting sync triggered", "Bill pay approval policy updated", "Bill pay automatic card payment no longer eligible", "Bill pay automatic card payment", "Bill pay bank account updated", "Bill pay batch payment initiated", "Bill pay business vendor unlinked from vendor network", "Bill pay card delivery", "Bill pay check address update", "Bill pay check tracking update", "Bill pay deleted bill", "Bill pay delivered payment", "Bill pay dismissed fraud alert", "Bill pay edited payee address", "Bill pay edited payment method", "Bill pay initiated payment refund", "Bill pay mailed check payment", "Bill pay marked as paid", "Bill pay matched transaction to bill", "Bill pay payment failed", "Bill pay payment posted", "Bill pay recurrence info changed for recurring series", "Bill pay rejected sync for bank account from vendor network", "Bill pay rejected sync for vendor card acceptance policy from vendor network", "Bill pay rejected sync for vendor check mailing address from vendor network", "Bill pay rejected sync for vendor information from vendor network", "Bill pay rejected sync for vendor tax info from vendor network", "Bill pay retried payment", "Bill pay returned funds", "Bill unlinked from PO", "Bill unlinked", "Billing config updated", "Blank canvas workflow execution updated", "Blank canvas workflow pause status updated", "Booking request approval policy updated", "Brokerage order updated", "Cancel revision request", "Cancelled by customer", "Cancelled by ramp", "Card delivered", "Card payment initiated", "Cash agent recommendation updated", "Changed bank account on bill", "Changed card holder", "Changed funds user", "Combined contracts with this contract", "Communication sent", "Complete revision", "Created accounting split line item", "Created card", "Created fund from purchase order", "Created merchant error", "Created unrecognized charge", "Created", "Deleted bill field", "Deleted card acceptance policy", "Deleted procurement field", "Deleted vendor field", "Deleted", "Demoted co-owner to member", "Detached funds from spend program", "Document labeled", "Document updated", "Docusign envelope updated", "Draft vendor created", "Draft vendor deleted", "Draft vendor published", "Edited bill field", "Edited card acceptance policy", "Edited contract tracking setting", "Edited procurement field", "Edited spend intent", "Edited tin", "Edited vendor field", "Edited wallet automation", "Email updated", "Emailed purchase order", "Exception given from dispute resolution", "Exception given from repayment", "Exception request approved", "Exception request cancelled", "Exception request denied", "Exception requested", "External ticket created asana", "External ticket created jira", "External ticket created linear", "External ticket created zendesk", "Funds activated from reissued virtual card", "Generated renewal brief for contract", "Ironclad workflow updated", "Issued funds", "Linked funds to spend program", "Locked access to funds", "Locked card", "Managed portfolio transfer updated", "Manager updated", "Mark as accidental", "Matched purchase order to transaction", "Matched transaction to purchase order", "Memo updated", "Merged vendors", "Name updated hris", "Name updated", "New virtual card issued for currency migration", "Notification sent due to purchase order request modification", "Password reset required", "Password reset user", "Password updated user", "Payback cancelled", "Payback payment failed", "Payback payment manually paid", "Payback payment retried", "Payback payment succeeded", "Payback request approved by user", "Payback request cancelled by manager", "Payback request rejected by user", "Payback requested by manager", "Payback triggered by user", "Payee linked to accounting", "Payment run updated", "Payment updated", "Phone updated", "Policy agent suggestion feedback submitted", "Post spend approval policy updated", "Procurement  unmatched purchase order from transaction", "Procurement  unmatched transaction from purchase order", "Procurement agent run completed", "Procurement change request approval policy updated", "Procurement send global form", "Procurement submit global form response", "Procurement vendor onboarding submitted", "Procurement vendor onboarding triggered", "Promoted member to co-owner", "Purchase order accounting sync created vendor", "Purchase order accounting sync failed", "Purchase order accounting sync success", "RFX clarification answered", "RFX clarification question submitted", "RFX closed", "RFX created", "RFX graded", "RFX published", "RFX response redacted", "RFX response submitted", "RFX vendor accepted", "RFX vendor added", "RFX vendor declined", "RFX vendor removed", "Receipt created", "Receipt deleted", "Receipt matched", "Refund cleared", "Refund paid", "Reimbursement bank account updated", "Reimbursement from user", "Reimbursement policy agent suggestion feedback submitted", "Reimbursement submitted", "Reimbursement to user", "Reimbursements disabled", "Reimbursements enabled", "Reissued card", "Rejected card edit request", "Rejected funds edit request", "Rejected new card request", "Rejected procurement change request", "Rejected request for new funds", "Reminded to approve items", "Reminded to upload missing items", "Removed user from funds", "Request revision", "Requested an edit to these funds", "Requested new card", "Requested new funds", "Resolved by ramp", "Review needed", "Reviewed by ramp", "Role updated", "SFTP Authentication Failed", "SFTP Authentication IP and Username Matched", "SFTP Configuration Changed", "Separation of duties disabled", "Separation of duties enabled", "Set member limit on shared fund", "Sourcing event created", "Sourcing event status changed", "Spend allocation change request approval policy updated", "Spend approved", "Spend rejected", "Spend request approval policy updated", "Status updated", "Submitted procurement change request", "Temporarily unlocked access to funds", "Terminated card", "Terminated funds", "Test", "Third party risk management vendor review updated", "This contract was combined with another contract", "Ticket assignee updated", "Ticket status updated", "Totp authenticator created", "Totp authenticator deleted", "Totp authenticator updated", "Transaction approval policy updated", "Transaction cleared", "Transaction entity changed", "Transaction missing item reminder event", "Transaction paid", "Transaction receipt updated", "Transaction submission policy exemption event", "Transferred ownership of funds", "Travel policy selection updated", "Undid marking transaction as accidental", "Unlocked access to funds", "Unlocked card temporarily", "Unlocked card", "Unmark as accidental", "Updated card program", "Updated card", "Updated funds", "Updated spend program", "User accepted invite", "User assigned by external firm", "User assigned through external firm merge", "User created", "User deactivated", "User deleted", "User invited", "User locked", "User login", "User previewed", "User reactivated", "User undeleted", "User unlocked", "Vendor Network updates enabled", "Vendor awarded", "Vendor credit action", "Vendor imported from erp", "Vendor management  vendor added to managed list", "Vendor management  vendor removed from managed list", "Vendor management agreement deleted document", "Vendor management agreement deleted", "Vendor management agreement linked document", "Vendor management agreement linked purchase order", "Vendor management agreement notification type switched", "Vendor management agreement status changed", "Vendor management agreement unlinked document", "Vendor management agreement unlinked purchase order", "Vendor management agreement uploaded document", "Vendor management edited agreement field", "Vendor management expansion request status changed", "Vendor payment approval policy updated", "Vendor profile access created", "Vendor profile access denied", "Vendor profile access edited", "Vendor profile access email sent", "Vendor profile access requested", "Vendor profile access revoked", "Vendor profile all documents downloaded", "Vendor profile document downloaded", "Vendor sync failure", "Viewed sensitive card details", "Violation from manager", "Violation from rule", "Violation from user", "Virtual card reissued", "Workflow restarted due to purchase order request modification"]] | None = Field(None, description="Filter results to only include specific event types (e.g., login, create, delete, update). Provide an array of event type values."),
    page_size: int | None = Field(None, description="Number of results to return per page. Must be between 2 and 100 results; defaults to 20 if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of audit log events with optional filtering by user, actor type, and event type. Use this to track system activities and changes across your organization."""

    # Construct request model with validation
    try:
        _request = _models.GetAuditLogEventsListResourceRequest(
            query=_models.GetAuditLogEventsListResourceRequestQuery(user_ids=user_ids, event_actor_types=event_actor_types, event_types=event_types, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_audit_log_events: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/audit-logs/events"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_query = _serialize_query(_http_query, {
        "user_ids": ("form", False),
        "event_actor_types": ("form", False),
        "event_types": ("form", False),
    })
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_audit_log_events")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_audit_log_events", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_audit_log_events",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Bank Accounts
@mcp.tool()
async def list_bank_accounts(page_size: int | None = Field(None, description="Number of bank accounts to return per page. Must be between 2 and 100 results; defaults to 20 if not specified.")) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of bank accounts associated with the authenticated user or organization. Results are returned in pages with configurable size."""

    # Construct request model with validation
    try:
        _request = _models.GetBankAccountListWithPaginationRequest(
            query=_models.GetBankAccountListWithPaginationRequestQuery(page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_bank_accounts: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/bank-accounts"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_bank_accounts")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_bank_accounts", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_bank_accounts",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Bank Accounts
@mcp.tool()
async def get_bank_account(bank_account_id: str = Field(..., description="The unique identifier (UUID) of the bank account to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information for a specific bank account by its unique identifier. Returns the complete bank account resource including account details and metadata."""

    # Construct request model with validation
    try:
        _request = _models.GetBankAccountResourceRequest(
            path=_models.GetBankAccountResourceRequestPath(bank_account_id=bank_account_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_bank_account: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/bank-accounts/{bank_account_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/bank-accounts/{bank_account_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_bank_account")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_bank_account", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_bank_account",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Bill
@mcp.tool()
async def list_bills_with_pagination(
    entity_id: str | None = Field(None, description="Filter results to bills associated with a specific entity (UUID format)."),
    customer_friendly_payment_id: str | None = Field(None, description="Filter by exact customer-friendly payment ID to retrieve all bills in the same payment or batch payment group."),
    draft_bill_id: str | None = Field(None, description="Filter by exact draft bill ID (UUID format)."),
    invoice_number: str | None = Field(None, description="Filter by exact invoice number."),
    remote_id: str | None = Field(None, description="Filter by exact remote ID from an external system."),
    accounting_field_selection_id: str | None = Field(None, description="Filter to bills coded with a specific accounting field selection (UUID format)."),
    status_summaries: list[Literal["APPROVAL_PENDING", "APPROVAL_REJECTED", "ARCHIVED", "AWAITING_RELEASE", "BLOCKED", "HELD_BY_PROVIDER", "ON_HOLD", "PAYMENT_COMPLETED", "PAYMENT_DETAILS_MISSING", "PAYMENT_ERROR", "PAYMENT_NOT_INSTRUCTED", "PAYMENT_PROCESSING", "PAYMENT_READY", "PAYMENT_SCHEDULED", "PENDING_VENDOR_APPROVAL", "WAITING_FOR_TRANSACTION_MATCH", "WAITING_FOR_VENDOR"]] | None = Field(None, description="Filter by one or more bill status summaries. Provide as a comma-separated list of status values."),
    payment_id: str | None = Field(None, description="Filter by payment ID (UUID format) to retrieve all bills belonging to the same payment."),
    vendor_id: str | None = Field(None, description="Filter results to bills from a specific vendor (UUID format)."),
    is_accounting_sync_enabled: bool | None = Field(None, description="Filter by ERP sync configuration: true returns only bills configured to sync to the ERP, false returns only bills excluded from sync."),
    approval_status: Literal["APPROVED", "INITIALIZED", "PENDING", "REJECTED", "TERMINATED"] | None = Field(None, description="Filter by bill approval status. Valid values are: APPROVED, INITIALIZED, PENDING, REJECTED, or TERMINATED. This is distinct from payment release approval status."),
    payment_status: Literal["OPEN", "PAID"] | None = Field(None, description="Filter by payment status. Valid values are: OPEN (unpaid) or PAID."),
    sync_status: Literal["BILL_AND_PAYMENT_SYNCED", "BILL_SYNCED", "NOT_SYNCED"] | None = Field(None, description="Filter by ERP sync status. Valid values are: BILL_AND_PAYMENT_SYNCED, BILL_SYNCED, or NOT_SYNCED."),
    is_archived: bool | None = Field(None, description="Include archived (deleted) bills in results instead of active bills. Defaults to false."),
    from_due_date: str | None = Field(None, description="Return only bills with a due date on or after this date. Provide as an ISO 8601 datetime string."),
    to_due_date: str | None = Field(None, description="Return only bills with a due date on or before this date. Provide as an ISO 8601 datetime string."),
    from_issued_date: str | None = Field(None, description="Return only bills with an issue date on or after this date. Provide as an ISO 8601 datetime string."),
    to_issued_date: str | None = Field(None, description="Return only bills with an issue date on or before this date. Provide as an ISO 8601 datetime string."),
    from_paid_at: str | None = Field(None, description="Return only bills with a payment date on or after this date. Provide as an ISO 8601 datetime string."),
    to_paid_at: str | None = Field(None, description="Return only bills with a payment date on or before this date. Provide as an ISO 8601 datetime string."),
    min_amount: str | None = Field(None, description="Return only bills with an amount greater than or equal to this value. Accepts numeric values."),
    max_amount: str | None = Field(None, description="Return only bills with an amount less than or equal to this value. Accepts numeric values."),
    page_size: int | None = Field(None, description="Number of results per page. Must be between 2 and 100. Defaults to 20 if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of bills with flexible filtering by entity, vendor, payment status, approval status, dates, amounts, and accounting sync configuration. Supports searching by identifiers and status summaries."""

    # Construct request model with validation
    try:
        _request = _models.GetBillListWithPaginationRequest(
            query=_models.GetBillListWithPaginationRequestQuery(entity_id=entity_id, customer_friendly_payment_id=customer_friendly_payment_id, draft_bill_id=draft_bill_id, invoice_number=invoice_number, remote_id=remote_id, accounting_field_selection_id=accounting_field_selection_id, status_summaries=status_summaries, payment_id=payment_id, vendor_id=vendor_id, is_accounting_sync_enabled=is_accounting_sync_enabled, approval_status=approval_status, payment_status=payment_status, sync_status=sync_status, is_archived=is_archived, from_due_date=from_due_date, to_due_date=to_due_date, from_issued_date=from_issued_date, to_issued_date=to_issued_date, from_paid_at=from_paid_at, to_paid_at=to_paid_at, min_amount=min_amount, max_amount=max_amount, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_bills_with_pagination: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/bills"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_query = _serialize_query(_http_query, {
        "status_summaries": ("form", False),
    })
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_bills_with_pagination")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_bills_with_pagination", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_bills_with_pagination",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Bill
@mcp.tool()
async def create_bill(
    due_at: str = Field(..., description="Due date for payment of the bill in ISO 8601 date format (YYYY-MM-DD)."),
    entity_id: str = Field(..., description="UUID of the business entity associated with this bill."),
    invoice_currency: Literal["AED", "AFN", "ALL", "AMD", "ANG", "AOA", "ARS", "AUD", "AWG", "AZN", "BAM", "BBD", "BDT", "BGN", "BHD", "BIF", "BMD", "BND", "BOB", "BOV", "BRL", "BSD", "BTN", "BWP", "BYN", "BZD", "CAD", "CDF", "CHE", "CHF", "CHW", "CLF", "CLP", "CNH", "CNY", "COP", "COU", "CRC", "CUC", "CUP", "CVE", "CZK", "DJF", "DKK", "DOP", "DZD", "EGP", "ERN", "ETB", "EUR", "EURC", "FJD", "FKP", "GBP", "GEL", "GHS", "GIP", "GMD", "GNF", "GTQ", "GYD", "HKD", "HNL", "HRK", "HTG", "HUF", "IDR", "ILS", "INR", "IQD", "IRR", "ISK", "JMD", "JOD", "JPY", "KES", "KGS", "KHR", "KMF", "KPW", "KRW", "KWD", "KYD", "KZT", "LAK", "LBP", "LKR", "LRD", "LSL", "LYD", "MAD", "MDL", "MGA", "MKD", "MMK", "MNT", "MOP", "MRU", "MUR", "MVR", "MWK", "MXN", "MXV", "MYR", "MZN", "NAD", "NGN", "NIO", "NOK", "NPR", "NZD", "OMR", "PAB", "PEN", "PGK", "PHP", "PKR", "PLN", "PYG", "QAR", "RON", "RSD", "RUB", "RWF", "SAR", "SBD", "SCR", "SDG", "SEK", "SGD", "SHP", "SLE", "SLL", "SOS", "SRD", "SSP", "STN", "SVC", "SYP", "SZL", "THB", "TJS", "TMT", "TND", "TOP", "TRY", "TTD", "TWD", "TZS", "UAH", "UGX", "USD", "USDB", "USDC", "USN", "UYI", "UYU", "UYW", "UZS", "VED", "VES", "VND", "VUV", "WST", "XAD", "XAF", "XAG", "XAU", "XBA", "XBB", "XBC", "XBD", "XCD", "XCG", "XDR", "XOF", "XPD", "XPF", "XPT", "XSU", "XTS", "XUA", "XXX", "YER", "ZAR", "ZMW", "ZWG", "ZWL"] = Field(..., description="Three-letter ISO 4217 currency code for the bill amount (e.g., USD, EUR, GBP). Must be a valid currency code."),
    invoice_number: str = Field(..., description="The invoice number displayed on the bill. Maximum 20 characters; must be unique or match your vendor's numbering system.", max_length=20),
    issued_at: str = Field(..., description="Date the bill was issued by the vendor in ISO 8601 date format (YYYY-MM-DD)."),
    vendor_id: str = Field(..., description="UUID of the vendor issuing this bill."),
    accounting_field_selections: list[_models.ApiCreateAccountingFieldParamsRequestBody] | None = Field(None, description="List of accounting field selections to code the bill for ERP synchronization. Specify which accounting fields and their selected values should be applied."),
    attachment_id: str | None = Field(None, description="UUID of a previously uploaded file to attach to this bill for reference or documentation purposes."),
    enable_accounting_sync: bool | None = Field(None, description="Set to false to prevent this bill from syncing to your ERP system. Must remain true if a remote_id is provided."),
    inventory_line_items: list[_models.ApiCreateBillInventoryLineItemParamsRequestBody] | None = Field(None, description="List of inventory line items to include on the bill. Each item should specify quantity, unit cost, and inventory details."),
    line_items: list[_models.ApiCreateBillLineItemParamsRequestBody] | None = Field(None, description="List of line items detailing charges on the bill. Each item should include description, quantity, unit price, and optional account coding."),
    memo: str | None = Field(None, description="Internal memo or notes about the bill. Maximum 1000 characters.", max_length=1000),
    payment_details: _models.ApiCreateBankAccountPaymentParamsRequestBody | _models.ApiCreateBillVendorPaymentParamsRequestBody | _models.ApiCreateCardBillPaymentParamsRequestBody | _models.ApiCreateManualBillPaymentParamsRequestBody | None = Field(None, description="Payment method details for the bill. Schema varies based on the payment method selected (e.g., bank transfer, check, credit card)."),
    posting_date: str | None = Field(None, description="Date the bill is posted to the accounting system in ISO 8601 date format (YYYY-MM-DD). If not provided, defaults to the issued date."),
    purchase_order_ids: list[str] | None = Field(None, description="List of purchase order UUIDs to match and reconcile against this bill for three-way matching."),
    remote_id: str | None = Field(None, description="External identifier for this bill from your system or ERP. When provided, enable_accounting_sync must be set to true."),
    vendor_contact_id: str | None = Field(None, description="UUID of the vendor contact to receive this bill. Must be associated with the specified vendor unless use_default_vendor_contact is enabled."),
    vendor_memo: str | None = Field(None, description="Message or memo to include for the vendor. Maximum 400 characters.", max_length=400),
) -> dict[str, Any] | ToolResult:
    """Create a new bill for a vendor. Batch payments cannot be created through this API; use this operation for individual bill creation with line items, attachments, and accounting synchronization options."""

    # Construct request model with validation
    try:
        _request = _models.PostBillListWithPaginationRequest(
            body=_models.PostBillListWithPaginationRequestBody(accounting_field_selections=accounting_field_selections, attachment_id=attachment_id, due_at=due_at, enable_accounting_sync=enable_accounting_sync, entity_id=entity_id, inventory_line_items=inventory_line_items, invoice_currency=invoice_currency, invoice_number=invoice_number, issued_at=issued_at, line_items=line_items, memo=memo, payment_details=payment_details, posting_date=posting_date, purchase_order_ids=purchase_order_ids, remote_id=remote_id, vendor_contact_id=vendor_contact_id, vendor_id=vendor_id, vendor_memo=vendor_memo)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_bill: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/bills"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_bill")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_bill", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_bill",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Bill
@mcp.tool()
async def list_draft_bills(
    entity_id: str | None = Field(None, description="Filter results to draft bills associated with a specific entity, specified as a UUID."),
    invoice_number: str | None = Field(None, description="Filter results to draft bills matching an exact invoice number."),
    remote_id: str | None = Field(None, description="Filter results to draft bills matching an exact remote ID."),
    vendor_id: str | None = Field(None, description="Filter results to draft bills from a specific vendor, specified as a UUID."),
    from_due_date: str | None = Field(None, description="Show only draft bills with a due date on or after this date. Provide as an ISO 8601 datetime string."),
    to_due_date: str | None = Field(None, description="Show only draft bills with a due date on or before this date. Provide as an ISO 8601 datetime string."),
    from_issued_date: str | None = Field(None, description="Show only draft bills with an issued date on or after this date. Provide as an ISO 8601 datetime string."),
    to_issued_date: str | None = Field(None, description="Show only draft bills with an issued date on or before this date. Provide as an ISO 8601 datetime string."),
    page_size: int | None = Field(None, description="Number of results per page. Must be between 2 and 100; defaults to 20 if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of draft bills with optional filtering by entity, vendor, invoice details, and date ranges. Useful for finding bills in draft status that match specific criteria."""

    # Construct request model with validation
    try:
        _request = _models.GetDraftBillListWithPaginationRequest(
            query=_models.GetDraftBillListWithPaginationRequestQuery(entity_id=entity_id, invoice_number=invoice_number, remote_id=remote_id, vendor_id=vendor_id, from_due_date=from_due_date, to_due_date=to_due_date, from_issued_date=from_issued_date, to_issued_date=to_issued_date, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_draft_bills: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/bills/drafts"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_draft_bills")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_draft_bills", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_draft_bills",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Bill
@mcp.tool()
async def create_draft_bill(
    vendor_id: str = Field(..., description="UUID of the vendor who issued this bill. Required to create the draft."),
    accounting_field_selections: list[_models.ApiCreateAccountingFieldParamsRequestBody] | None = Field(None, description="List of accounting field selections to code the bill for accounting purposes."),
    due_at: str | None = Field(None, description="Due date for payment of the bill in ISO 8601 date format (YYYY-MM-DD)."),
    enable_accounting_sync: bool | None = Field(None, description="Set to false to prevent this bill from syncing to your connected ERP system; defaults to true for automatic sync."),
    entity_id: str | None = Field(None, description="UUID of the business entity associated with this bill."),
    inventory_line_items: list[_models.ApiCreateBillInventoryLineItemParamsRequestBody] | None = Field(None, description="List of inventory line items to attach to the bill. Providing this replaces all existing inventory line items."),
    invoice_currency: Literal["AED", "AFN", "ALL", "AMD", "ANG", "AOA", "ARS", "AUD", "AWG", "AZN", "BAM", "BBD", "BDT", "BGN", "BHD", "BIF", "BMD", "BND", "BOB", "BOV", "BRL", "BSD", "BTN", "BWP", "BYN", "BZD", "CAD", "CDF", "CHE", "CHF", "CHW", "CLF", "CLP", "CNH", "CNY", "COP", "COU", "CRC", "CUC", "CUP", "CVE", "CZK", "DJF", "DKK", "DOP", "DZD", "EGP", "ERN", "ETB", "EUR", "EURC", "FJD", "FKP", "GBP", "GEL", "GHS", "GIP", "GMD", "GNF", "GTQ", "GYD", "HKD", "HNL", "HRK", "HTG", "HUF", "IDR", "ILS", "INR", "IQD", "IRR", "ISK", "JMD", "JOD", "JPY", "KES", "KGS", "KHR", "KMF", "KPW", "KRW", "KWD", "KYD", "KZT", "LAK", "LBP", "LKR", "LRD", "LSL", "LYD", "MAD", "MDL", "MGA", "MKD", "MMK", "MNT", "MOP", "MRU", "MUR", "MVR", "MWK", "MXN", "MXV", "MYR", "MZN", "NAD", "NGN", "NIO", "NOK", "NPR", "NZD", "OMR", "PAB", "PEN", "PGK", "PHP", "PKR", "PLN", "PYG", "QAR", "RON", "RSD", "RUB", "RWF", "SAR", "SBD", "SCR", "SDG", "SEK", "SGD", "SHP", "SLE", "SLL", "SOS", "SRD", "SSP", "STN", "SVC", "SYP", "SZL", "THB", "TJS", "TMT", "TND", "TOP", "TRY", "TTD", "TWD", "TZS", "UAH", "UGX", "USD", "USDB", "USDC", "USN", "UYI", "UYU", "UYW", "UZS", "VED", "VES", "VND", "VUV", "WST", "XAD", "XAF", "XAG", "XAU", "XBA", "XBB", "XBC", "XBD", "XCD", "XCG", "XDR", "XOF", "XPD", "XPF", "XPT", "XSU", "XTS", "XUA", "XXX", "YER", "ZAR", "ZMW", "ZWG", "ZWL"] | None = Field(None, description="Three-letter ISO 4217 currency code for the invoice (e.g., USD, EUR, GBP). Supports major world currencies and crypto assets."),
    invoice_number: str | None = Field(None, description="The invoice number or reference from the vendor, up to 20 characters.", max_length=20),
    issued_at: str | None = Field(None, description="Date the bill was issued by the vendor in ISO 8601 date format (YYYY-MM-DD)."),
    line_items: list[_models.ApiCreateBillLineItemParamsRequestBody] | None = Field(None, description="List of line items detailing charges on the bill. Providing this replaces all existing line items."),
    memo: str | None = Field(None, description="Internal notes or memo about the bill, up to 1000 characters.", max_length=1000),
    posting_date: str | None = Field(None, description="Date the bill is posted to the accounting system in ISO 8601 date format (YYYY-MM-DD)."),
    purchase_order_ids: list[str] | None = Field(None, description="List of purchase order UUIDs to match and link to this bill. Providing this replaces all existing linked purchase orders."),
    remote_id: str | None = Field(None, description="External identifier for this bill from your system, useful for tracking and reconciliation."),
    vendor_contact_id: str | None = Field(None, description="UUID of the vendor contact person associated with this bill; the contact must belong to the specified vendor."),
) -> dict[str, Any] | ToolResult:
    """Create a draft bill for a vendor with optional line items, accounting details, and purchase order matching. Draft bills can be configured for ERP synchronization and support multiple currencies."""

    # Construct request model with validation
    try:
        _request = _models.PostDraftBillListWithPaginationRequest(
            body=_models.PostDraftBillListWithPaginationRequestBody(accounting_field_selections=accounting_field_selections, due_at=due_at, enable_accounting_sync=enable_accounting_sync, entity_id=entity_id, inventory_line_items=inventory_line_items, invoice_currency=invoice_currency, invoice_number=invoice_number, issued_at=issued_at, line_items=line_items, memo=memo, posting_date=posting_date, purchase_order_ids=purchase_order_ids, remote_id=remote_id, vendor_contact_id=vendor_contact_id, vendor_id=vendor_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_draft_bill: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/bills/drafts"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_draft_bill")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_draft_bill", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_draft_bill",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Bill
@mcp.tool()
async def get_draft_bill(draft_bill_id: str = Field(..., description="The unique identifier of the draft bill to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve a specific draft bill by its unique identifier. Use this to view the current state and details of a bill in draft status."""

    # Construct request model with validation
    try:
        _request = _models.GetDraftBillResourceRequest(
            path=_models.GetDraftBillResourceRequestPath(draft_bill_id=draft_bill_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_draft_bill: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/bills/drafts/{draft_bill_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/bills/drafts/{draft_bill_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_draft_bill")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_draft_bill", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_draft_bill",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Bill
@mcp.tool()
async def update_draft_bill(
    draft_bill_id: str = Field(..., description="The unique identifier of the draft bill to update."),
    accounting_field_selections: list[_models.ApiCreateAccountingFieldParamsRequestBody] | None = Field(None, description="List of accounting field options selected to categorize and code the bill for accounting purposes."),
    due_at: str | None = Field(None, description="The due date for payment of the bill, specified as a calendar date."),
    enable_accounting_sync: bool | None = Field(None, description="Set to false to prevent this bill from automatically syncing to your connected ERP system; defaults to true."),
    entity_id: str | None = Field(None, description="The UUID of the business entity associated with this bill."),
    inventory_line_items: list[_models.ApiCreateBillInventoryLineItemParamsRequestBody] | None = Field(None, description="List of inventory line items to attach to the bill. Providing this list replaces all previously existing inventory line items."),
    invoice_currency: Literal["AED", "AFN", "ALL", "AMD", "ANG", "AOA", "ARS", "AUD", "AWG", "AZN", "BAM", "BBD", "BDT", "BGN", "BHD", "BIF", "BMD", "BND", "BOB", "BOV", "BRL", "BSD", "BTN", "BWP", "BYN", "BZD", "CAD", "CDF", "CHE", "CHF", "CHW", "CLF", "CLP", "CNH", "CNY", "COP", "COU", "CRC", "CUC", "CUP", "CVE", "CZK", "DJF", "DKK", "DOP", "DZD", "EGP", "ERN", "ETB", "EUR", "EURC", "FJD", "FKP", "GBP", "GEL", "GHS", "GIP", "GMD", "GNF", "GTQ", "GYD", "HKD", "HNL", "HRK", "HTG", "HUF", "IDR", "ILS", "INR", "IQD", "IRR", "ISK", "JMD", "JOD", "JPY", "KES", "KGS", "KHR", "KMF", "KPW", "KRW", "KWD", "KYD", "KZT", "LAK", "LBP", "LKR", "LRD", "LSL", "LYD", "MAD", "MDL", "MGA", "MKD", "MMK", "MNT", "MOP", "MRU", "MUR", "MVR", "MWK", "MXN", "MXV", "MYR", "MZN", "NAD", "NGN", "NIO", "NOK", "NPR", "NZD", "OMR", "PAB", "PEN", "PGK", "PHP", "PKR", "PLN", "PYG", "QAR", "RON", "RSD", "RUB", "RWF", "SAR", "SBD", "SCR", "SDG", "SEK", "SGD", "SHP", "SLE", "SLL", "SOS", "SRD", "SSP", "STN", "SVC", "SYP", "SZL", "THB", "TJS", "TMT", "TND", "TOP", "TRY", "TTD", "TWD", "TZS", "UAH", "UGX", "USD", "USDB", "USDC", "USN", "UYI", "UYU", "UYW", "UZS", "VED", "VES", "VND", "VUV", "WST", "XAD", "XAF", "XAG", "XAU", "XBA", "XBB", "XBC", "XBD", "XCD", "XCG", "XDR", "XOF", "XPD", "XPF", "XPT", "XSU", "XTS", "XUA", "XXX", "YER", "ZAR", "ZMW", "ZWG", "ZWL"] | None = Field(None, description="The currency code for the invoice amount, selected from the ISO 4217 standard currency list."),
    invoice_number: str | None = Field(None, description="The vendor's invoice number or reference identifier, up to 20 characters.", max_length=20),
    issued_at: str | None = Field(None, description="The date the bill was issued by the vendor, specified as a calendar date."),
    line_items: list[_models.ApiCreateBillLineItemParamsRequestBody] | None = Field(None, description="List of line items detailing charges, quantities, and amounts on the bill. Providing this list replaces all previously existing line items."),
    memo: str | None = Field(None, description="Internal notes or comments about the bill, up to 1000 characters.", max_length=1000),
    posting_date: str | None = Field(None, description="The date the bill is posted or recorded in the accounting system, specified as a calendar date."),
    purchase_order_ids: list[str] | None = Field(None, description="List of purchase order identifiers to match and link with this bill. Providing this list replaces all previously linked purchase orders."),
    remote_id: str | None = Field(None, description="An external identifier or reference number for this bill from your internal system or vendor portal."),
    vendor_contact_id: str | None = Field(None, description="The UUID of the vendor contact person associated with this bill; the contact must belong to the specified vendor."),
    vendor_id: str | None = Field(None, description="The UUID of the vendor issuing this bill."),
) -> dict[str, Any] | ToolResult:
    """Update an existing draft bill with new details such as vendor information, line items, dates, and accounting settings. Changes are applied to the draft without posting to the accounting system."""

    # Construct request model with validation
    try:
        _request = _models.PatchDraftBillResourceRequest(
            path=_models.PatchDraftBillResourceRequestPath(draft_bill_id=draft_bill_id),
            body=_models.PatchDraftBillResourceRequestBody(accounting_field_selections=accounting_field_selections, due_at=due_at, enable_accounting_sync=enable_accounting_sync, entity_id=entity_id, inventory_line_items=inventory_line_items, invoice_currency=invoice_currency, invoice_number=invoice_number, issued_at=issued_at, line_items=line_items, memo=memo, posting_date=posting_date, purchase_order_ids=purchase_order_ids, remote_id=remote_id, vendor_contact_id=vendor_contact_id, vendor_id=vendor_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_draft_bill: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/bills/drafts/{draft_bill_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/bills/drafts/{draft_bill_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_draft_bill")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_draft_bill", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_draft_bill",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Bill
@mcp.tool()
async def add_draft_bill_attachment(
    draft_bill_id: str = Field(..., description="The unique identifier of the draft bill to which the attachment will be uploaded."),
    attachment_type: Literal["EMAIL", "FILE", "INVOICE", "VENDOR_CREDIT"] = Field(..., description="The classification of the attachment. Use 'INVOICE' to designate the actual invoice document for the bill; only one INVOICE attachment is permitted per draft bill."),
    file_: str = Field(..., alias="file", description="The file to upload as a binary attachment. The file should be included in the multipart/form-data request with the part name 'file' and Content-Disposition header set to 'attachment'."),
) -> dict[str, Any] | ToolResult:
    """Upload a file attachment to a draft bill. Only one INVOICE type attachment is allowed per draft bill."""

    # Construct request model with validation
    try:
        _request = _models.PostDraftBillAttachmentUploadResourceRequest(
            path=_models.PostDraftBillAttachmentUploadResourceRequestPath(draft_bill_id=draft_bill_id),
            body=_models.PostDraftBillAttachmentUploadResourceRequestBody(attachment_type=attachment_type, file_=file_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_draft_bill_attachment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/bills/drafts/{draft_bill_id}/attachments", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/bills/drafts/{draft_bill_id}/attachments"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_draft_bill_attachment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_draft_bill_attachment", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_draft_bill_attachment",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["file"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Bill
@mcp.tool()
async def get_bill(bill_id: str = Field(..., description="The unique identifier of the bill to retrieve. This is a required string value that identifies which bill to fetch.")) -> dict[str, Any] | ToolResult:
    """Retrieve a specific bill by its unique identifier. Returns the complete bill details including charges, dates, and payment information."""

    # Construct request model with validation
    try:
        _request = _models.GetBillResourceRequest(
            path=_models.GetBillResourceRequestPath(bill_id=bill_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_bill: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/bills/{bill_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/bills/{bill_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_bill")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_bill", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_bill",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Bill
@mcp.tool()
async def update_bill(
    bill_id: str = Field(..., description="The unique identifier of the bill to update."),
    accounting_field_selections: list[_models.ApiCreateAccountingFieldParamsRequestBody] | None = Field(None, description="List of accounting field selections used to code the bill for accounting purposes."),
    due_at: str | None = Field(None, description="The due date for payment, specified as a date in ISO 8601 format (YYYY-MM-DD)."),
    entity_id: str | None = Field(None, description="The UUID of the business entity associated with this bill."),
    inventory_line_items: list[_models.ApiCreateBillInventoryLineItemParamsRequestBody] | None = Field(None, description="List of inventory line items to attach to the bill. Providing this replaces all existing inventory line items."),
    invoice_number: str | None = Field(None, description="The vendor's invoice number, up to 20 characters.", max_length=20),
    issued_at: str | None = Field(None, description="The date the bill was issued, specified as a date in ISO 8601 format (YYYY-MM-DD)."),
    line_items: list[_models.ApiCreateBillLineItemParamsRequestBody] | None = Field(None, description="List of line items detailing charges on the bill. Providing this replaces all existing line items."),
    memo: str | None = Field(None, description="Internal memo or notes about the bill, up to 1000 characters.", max_length=1000),
    posting_date: str | None = Field(None, description="The date the bill is posted to the accounting system, specified as a date in ISO 8601 format (YYYY-MM-DD)."),
    purchase_order_ids: list[str] | None = Field(None, description="List of purchase order identifiers to match against this bill. Providing this replaces all existing linked purchase orders."),
    remote_id: str | None = Field(None, description="An external identifier that uniquely identifies this bill in the client's system."),
    vendor_contact_id: str | None = Field(None, description="The UUID of the vendor contact associated with this bill. The contact must belong to the specified vendor."),
    vendor_id: str | None = Field(None, description="The UUID of the vendor who issued this bill."),
    vendor_memo: str | None = Field(None, description="Memo or message to include for the vendor, up to 400 characters.", max_length=400),
) -> dict[str, Any] | ToolResult:
    """Update an approved bill with new financial details, line items, dates, or vendor information. Only bills with approved status can be modified."""

    # Construct request model with validation
    try:
        _request = _models.PatchBillResourceRequest(
            path=_models.PatchBillResourceRequestPath(bill_id=bill_id),
            body=_models.PatchBillResourceRequestBody(accounting_field_selections=accounting_field_selections, due_at=due_at, entity_id=entity_id, inventory_line_items=inventory_line_items, invoice_number=invoice_number, issued_at=issued_at, line_items=line_items, memo=memo, posting_date=posting_date, purchase_order_ids=purchase_order_ids, remote_id=remote_id, vendor_contact_id=vendor_contact_id, vendor_id=vendor_id, vendor_memo=vendor_memo)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_bill: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/bills/{bill_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/bills/{bill_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_bill")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_bill", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_bill",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Bill
@mcp.tool()
async def archive_bill(bill_id: str = Field(..., description="The unique identifier of the bill to archive. Paid bills and bills belonging to a batch payment cannot be deleted.")) -> dict[str, Any] | ToolResult:
    """Archive a bill and cancel associated inflight payments or terminate attached one-time cards. This is a destructive action that cannot be reversed for paid bills or bills in batch payments."""

    # Construct request model with validation
    try:
        _request = _models.DeleteBillResourceRequest(
            path=_models.DeleteBillResourceRequestPath(bill_id=bill_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for archive_bill: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/bills/{bill_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/bills/{bill_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("archive_bill")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("archive_bill", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="archive_bill",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Bill
@mcp.tool()
async def add_bill_attachment(
    bill_id: str = Field(..., description="The unique identifier of the bill to attach the file to, formatted as a UUID."),
    attachment_type: Literal["EMAIL", "FILE", "INVOICE", "VENDOR_CREDIT"] = Field(..., description="The classification of the attachment. Use 'INVOICE' to designate the actual invoice document for the bill; only one INVOICE attachment is permitted per bill."),
    file_: str = Field(..., alias="file", description="The binary file content to upload as the attachment."),
) -> dict[str, Any] | ToolResult:
    """Upload a file attachment to an existing bill. Note that only one INVOICE type attachment is allowed per bill."""

    # Construct request model with validation
    try:
        _request = _models.PostBillAttachmentUploadResourceRequest(
            path=_models.PostBillAttachmentUploadResourceRequestPath(bill_id=bill_id),
            body=_models.PostBillAttachmentUploadResourceRequestBody(attachment_type=attachment_type, file_=file_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_bill_attachment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/bills/{bill_id}/attachments", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/bills/{bill_id}/attachments"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_bill_attachment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_bill_attachment", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_bill_attachment",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["file"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Business
@mcp.tool()
async def get_business() -> dict[str, Any] | ToolResult:
    """Retrieve the authenticated company's business profile and organizational information."""

    # Extract parameters for API call
    _http_path = "/developer/v1/business"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_business")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_business", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_business",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Business
@mcp.tool()
async def get_business_balance() -> dict[str, Any] | ToolResult:
    """Retrieve the current balance information for your business account, including available funds and account status."""

    # Extract parameters for API call
    _http_path = "/developer/v1/business/balance"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_business_balance")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_business_balance", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_business_balance",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Card
@mcp.tool()
async def list_cards(
    entity_id: str | None = Field(None, description="Filter results to cards belonging to a specific business entity, specified as a UUID."),
    user_id: str | None = Field(None, description="Filter results to cards owned by a specific user, specified as a UUID."),
    is_activated: bool | None = Field(None, description="Filter to show only activated cards. Defaults to true if not specified."),
    is_terminated: bool | None = Field(None, description="Filter to show only terminated cards. Defaults to false if not specified."),
    page_size: int | None = Field(None, description="Number of results per page, between 2 and 100 inclusive. Defaults to 20 if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of cards with optional filtering by entity, user, activation status, and termination status."""

    # Construct request model with validation
    try:
        _request = _models.GetCardListWithPaginationRequest(
            query=_models.GetCardListWithPaginationRequestQuery(entity_id=entity_id, user_id=user_id, is_activated=is_activated, is_terminated=is_terminated, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_cards: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/cards"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_cards")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_cards", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_cards",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Card
@mcp.tool()
async def create_physical_card(
    idempotency_key: str = Field(..., description="A unique identifier (typically a UUID) generated by the client to ensure idempotent requests. The server uses this to recognize and deduplicate retries of the same request."),
    user_id: str = Field(..., description="UUID of the user who will own and use the card."),
    entity_id: str | None = Field(None, description="UUID of the business entity to associate with the card. If omitted, the card will be linked to the entity associated with the user's location."),
    fulfillment: _models.PostPhysicalCardBodyFulfillment | None = Field(None, description="Fulfillment configuration for the physical card, including delivery address and shipping preferences."),
    is_temporary: bool | None = Field(None, description="Set to true to create a temporary card with limited validity. Defaults to false for standard permanent cards."),
    spending_restrictions: _models.PostPhysicalCardBodySpendingRestrictions | None = Field(None, description="Spending limits and restrictions to apply to the card. Either this or card_program_id must be provided to define card behavior."),
) -> dict[str, Any] | ToolResult:
    """Initiates an asynchronous request to create a new physical Ramp card for a specified user. The operation returns immediately with a task ID for tracking the card creation process."""

    # Construct request model with validation
    try:
        _request = _models.PostPhysicalCardRequest(
            body=_models.PostPhysicalCardRequestBody(entity_id=entity_id, fulfillment=fulfillment, idempotency_key=idempotency_key, is_temporary=is_temporary, spending_restrictions=spending_restrictions, user_id=user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_physical_card: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/cards/deferred/physical"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_physical_card")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_physical_card", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_physical_card",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Card
@mcp.tool()
async def get_card_deferred_task_status(task_id: str = Field(..., description="The unique identifier of the deferred task, provided as a UUID.")) -> dict[str, Any] | ToolResult:
    """Retrieve the current status of a deferred card processing task. Use this to poll for completion of asynchronous card operations."""

    # Construct request model with validation
    try:
        _request = _models.GetCardDeferredTaskResourceRequest(
            path=_models.GetCardDeferredTaskResourceRequestPath(task_id=task_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_card_deferred_task_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/cards/deferred/status/{task_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/cards/deferred/status/{task_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_card_deferred_task_status")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_card_deferred_task_status", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_card_deferred_task_status",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Card
@mcp.tool()
async def create_virtual_card(
    idempotency_key: str = Field(..., description="A unique identifier (typically a UUID) generated by the client to prevent duplicate card creation if the request is retried. The server uses this to recognize and deduplicate subsequent attempts of the same request."),
    user_id: str = Field(..., description="UUID of the user who will own and use the card. This is required to identify the cardholder."),
    entity_id: str | None = Field(None, description="UUID of the business entity to associate with the card. If omitted, the card will be linked to the entity associated with the user's location."),
    is_temporary: bool | None = Field(None, description="Set to true to create a temporary card with limited validity; defaults to false for standard permanent cards."),
    spending_restrictions: _models.PostVirtualCardBodySpendingRestrictions | None = Field(None, description="Defines spending limits and restrictions for the card. Either this parameter or card_program_id must be provided to configure card behavior."),
) -> dict[str, Any] | ToolResult:
    """Initiates an asynchronous request to create a new virtual card for a specified user. Returns a task identifier that can be used to track the card creation status."""

    # Construct request model with validation
    try:
        _request = _models.PostVirtualCardRequest(
            body=_models.PostVirtualCardRequestBody(entity_id=entity_id, idempotency_key=idempotency_key, is_temporary=is_temporary, spending_restrictions=spending_restrictions, user_id=user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_virtual_card: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/cards/deferred/virtual"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_virtual_card")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_virtual_card", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_virtual_card",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Card
@mcp.tool()
async def get_card(card_id: str = Field(..., description="The unique identifier of the card to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific card by its unique identifier."""

    # Construct request model with validation
    try:
        _request = _models.GetCardResourceRequest(
            path=_models.GetCardResourceRequestPath(card_id=card_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_card: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/cards/{card_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/cards/{card_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_card")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_card", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_card",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Card
@mcp.tool()
async def update_card(
    card_id: str = Field(..., description="The unique identifier of the card to update."),
    entity_id: str | None = Field(None, description="The UUID of the business entity to associate with this card. Use this to reassign the card to a different entity."),
    has_notifications_enabled: bool | None = Field(None, description="Enable or disable notifications for this card."),
    new_user_id: str | None = Field(None, description="The UUID of the user who will become the new owner of this card."),
    spending_restrictions: _models.PatchCardResourceBodySpendingRestrictions | None = Field(None, description="Spending restrictions to apply to the card. Only include fields that need to be modified; unchanged restrictions do not need to be specified."),
) -> dict[str, Any] | ToolResult:
    """Update card properties including owner, display name, and spending restrictions. Allows modification of the associated business entity and notification settings."""

    # Construct request model with validation
    try:
        _request = _models.PatchCardResourceRequest(
            path=_models.PatchCardResourceRequestPath(card_id=card_id),
            body=_models.PatchCardResourceRequestBody(entity_id=entity_id, has_notifications_enabled=has_notifications_enabled, new_user_id=new_user_id, spending_restrictions=spending_restrictions)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_card: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/cards/{card_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/cards/{card_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_card")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_card", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_card",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Card
@mcp.tool()
async def suspend_card(
    card_id: str = Field(..., description="The unique identifier of the card to suspend."),
    idempotency_key: str = Field(..., description="A unique identifier generated by the client (typically a UUID) to ensure idempotent behavior. The server uses this to recognize and deduplicate retried requests, preventing duplicate suspensions if the request is sent multiple times."),
) -> dict[str, Any] | ToolResult:
    """Suspend a card to lock it from use. This creates an asynchronous task that prevents further transactions on the card; the suspension can be reverted later."""

    # Construct request model with validation
    try:
        _request = _models.PostCardSuspensionResourceRequest(
            path=_models.PostCardSuspensionResourceRequestPath(card_id=card_id),
            body=_models.PostCardSuspensionResourceRequestBody(idempotency_key=idempotency_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for suspend_card: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/cards/{card_id}/deferred/suspension", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/cards/{card_id}/deferred/suspension"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("suspend_card")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("suspend_card", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="suspend_card",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Card
@mcp.tool()
async def delete_card(
    card_id: str = Field(..., description="The unique identifier of the card to terminate."),
    idempotency_key: str = Field(..., description="A unique value generated by the client (typically a UUID) to ensure idempotent behavior. The server uses this key to recognize and deduplicate retried requests, preventing duplicate terminations if the request is sent multiple times."),
) -> dict[str, Any] | ToolResult:
    """Permanently terminate a card by creating an asynchronous task. This action is irreversible and cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.PostCardTerminationResourceRequest(
            path=_models.PostCardTerminationResourceRequestPath(card_id=card_id),
            body=_models.PostCardTerminationResourceRequestBody(idempotency_key=idempotency_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_card: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/cards/{card_id}/deferred/termination", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/cards/{card_id}/deferred/termination"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_card")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_card", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_card",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Card
@mcp.tool()
async def unsuspend_card(
    card_id: str = Field(..., description="The unique identifier of the card to unsuspend."),
    idempotency_key: str = Field(..., description="A unique identifier (typically a UUID) generated by the client to ensure idempotent request handling. The server uses this to recognize and deduplicate retries of the same request."),
) -> dict[str, Any] | ToolResult:
    """Initiates an asynchronous task to remove a card's suspension status, allowing it to be used for transactions again."""

    # Construct request model with validation
    try:
        _request = _models.PostCardUnsuspensionResourceRequest(
            path=_models.PostCardUnsuspensionResourceRequestPath(card_id=card_id),
            body=_models.PostCardUnsuspensionResourceRequestBody(idempotency_key=idempotency_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for unsuspend_card: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/cards/{card_id}/deferred/unsuspension", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/cards/{card_id}/deferred/unsuspension"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("unsuspend_card")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("unsuspend_card", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="unsuspend_card",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Cashback
@mcp.tool()
async def list_cashbacks(
    sync_status: Literal["NOT_SYNC_READY", "SYNCED", "SYNC_READY"] | None = Field(None, description="Filter results by synchronization status. Use NOT_SYNC_READY for cashbacks pending sync, SYNC_READY for those ready to sync, or SYNCED for already synchronized cashbacks. When provided, this filter takes precedence over other sync-related filters."),
    entity_id: str | None = Field(None, description="Filter cashbacks to those associated with a specific business entity, specified as a UUID."),
    statement_id: str | None = Field(None, description="Filter cashbacks to only those included in a specific statement, specified as a UUID."),
    page_size: int | None = Field(None, description="Number of results per page, between 2 and 100 inclusive. Defaults to 20 if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of cashback payments with optional filtering by sync status, business entity, or statement inclusion."""

    # Construct request model with validation
    try:
        _request = _models.GetCashbackListWithPaginationRequest(
            query=_models.GetCashbackListWithPaginationRequestQuery(sync_status=sync_status, entity_id=entity_id, statement_id=statement_id, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_cashbacks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/cashbacks"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_cashbacks")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_cashbacks", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_cashbacks",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Cashback
@mcp.tool()
async def get_cashback(cashback_id: str = Field(..., description="The unique identifier of the cashback payment to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve details for a specific cashback payment by its unique identifier."""

    # Construct request model with validation
    try:
        _request = _models.GetCashbackResourceRequest(
            path=_models.GetCashbackResourceRequestPath(cashback_id=cashback_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_cashback: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/cashbacks/{cashback_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/cashbacks/{cashback_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_cashback")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_cashback", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_cashback",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Records
@mcp.tool()
async def list_custom_tables() -> dict[str, Any] | ToolResult:
    """Retrieve a list of all custom tables available in the developer environment. This operation returns metadata for custom table definitions that can be used to store and manage custom records."""

    # Extract parameters for API call
    _http_path = "/developer/v1/custom-records/custom-tables"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_custom_tables")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_custom_tables", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_custom_tables",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Records
@mcp.tool()
async def list_custom_table_columns(custom_table_name: str = Field(..., description="The name of the custom table for which to list columns. This is the identifier of the custom table resource.")) -> dict[str, Any] | ToolResult:
    """Retrieve all columns defined for a specific custom table. Returns the column metadata including names, types, and configurations for the specified custom table."""

    # Construct request model with validation
    try:
        _request = _models.GetDevApiCustomTableColumnRequest(
            path=_models.GetDevApiCustomTableColumnRequestPath(custom_table_name=custom_table_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_custom_table_columns: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/custom-records/custom-tables/{custom_table_name}/columns", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/custom-records/custom-tables/{custom_table_name}/columns"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_custom_table_columns")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_custom_table_columns", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_custom_table_columns",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Records
@mcp.tool()
async def list_custom_table_rows(
    custom_table_name: str = Field(..., description="The name of the custom table to query for rows."),
    external_key: list[str] | None = Field(None, description="Filter results by the external key of custom rows. Accepts one or more external key values to match against."),
    include_all_referenced_rows: bool | None = Field(None, description="When enabled, includes all referenced rows in each cell instead of a limited subset. Defaults to false for performance."),
    page_size: int | None = Field(None, description="Number of rows to return per request, up to a maximum of 100. Defaults to 50 rows."),
) -> dict[str, Any] | ToolResult:
    """Retrieve rows from a custom table, with optional filtering by external key and control over referenced row inclusion and pagination."""

    # Construct request model with validation
    try:
        _request = _models.GetDevApiCustomRowRequest(
            path=_models.GetDevApiCustomRowRequestPath(custom_table_name=custom_table_name),
            query=_models.GetDevApiCustomRowRequestQuery(external_key=external_key, include_all_referenced_rows=include_all_referenced_rows, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_custom_table_rows: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/custom-records/custom-tables/{custom_table_name}/rows", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/custom-records/custom-tables/{custom_table_name}/rows"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_custom_table_rows")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_custom_table_rows", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_custom_table_rows",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Records
@mcp.tool()
async def update_custom_table_rows(
    custom_table_name: str = Field(..., description="The name of the custom table where rows will be inserted or updated."),
    data: list[_models.CustomRowColumnContentsByColumnNameRequestBody] = Field(..., description="An array of row objects to insert or update. All objects must have identical column names; use null to omit setting a value for a specific column in a row."),
) -> dict[str, Any] | ToolResult:
    """Insert or update multiple rows in a custom table. Rows are identified by their existing keys, and all entries must contain the same set of column names with null values for columns that should not be modified."""

    # Construct request model with validation
    try:
        _request = _models.PutDevApiCustomRowRequest(
            path=_models.PutDevApiCustomRowRequestPath(custom_table_name=custom_table_name),
            body=_models.PutDevApiCustomRowRequestBody(data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_custom_table_rows: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/custom-records/custom-tables/{custom_table_name}/rows", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/custom-records/custom-tables/{custom_table_name}/rows"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_custom_table_rows")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_custom_table_rows", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_custom_table_rows",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Records
@mcp.tool()
async def delete_custom_table_rows(
    custom_table_name: str = Field(..., description="The name of the custom table from which rows will be deleted."),
    data: list[_models.CustomRowExternalKeyRequestBody] = Field(..., description="An array of external keys identifying the rows to delete. Each key must correspond to an existing row in the specified custom table."),
) -> dict[str, Any] | ToolResult:
    """Delete one or more rows from a custom table by their external keys. Specify the custom table and provide a list of row identifiers to remove."""

    # Construct request model with validation
    try:
        _request = _models.DeleteDevApiCustomRowRequest(
            path=_models.DeleteDevApiCustomRowRequestPath(custom_table_name=custom_table_name),
            body=_models.DeleteDevApiCustomRowRequestBody(data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_custom_table_rows: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/custom-records/custom-tables/{custom_table_name}/rows", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/custom-records/custom-tables/{custom_table_name}/rows"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_custom_table_rows")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_custom_table_rows", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_custom_table_rows",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Records
@mcp.tool()
async def update_custom_table_row_external_key(
    custom_table_name: str = Field(..., description="The name of the custom table containing the row to be updated."),
    row_id: str = Field(..., description="The unique identifier of the row whose external key should be changed."),
    new_external_key: str = Field(..., description="The new external key value to assign to the row. This becomes the new external identifier for the row."),
) -> dict[str, Any] | ToolResult:
    """Updates the external key identifier for a specific row in a custom table. This operation allows you to change how the row is referenced externally."""

    # Construct request model with validation
    try:
        _request = _models.PatchDevApiChangeCustomRowExternalKeyRequest(
            path=_models.PatchDevApiChangeCustomRowExternalKeyRequestPath(custom_table_name=custom_table_name, row_id=row_id),
            body=_models.PatchDevApiChangeCustomRowExternalKeyRequestBody(new_external_key=new_external_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_custom_table_row_external_key: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/custom-records/custom-tables/{custom_table_name}/rows/{row_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/custom-records/custom-tables/{custom_table_name}/rows/{row_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_custom_table_row_external_key")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_custom_table_row_external_key", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_custom_table_row_external_key",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Records
@mcp.tool()
async def append_custom_table_rows(
    table_name: str = Field(..., description="The name of the custom table where rows will be appended or updated."),
    data: list[_models.CustomRowColumnContentsByColumnNameRequestBody] = Field(..., description="An array of row objects to insert or update. All objects in the array must have identical column names; use null for any columns where a value should not be set."),
) -> dict[str, Any] | ToolResult:
    """Append or update multiple rows in a custom table by providing cell data. Each row entry must contain the same set of column names, with null values used to indicate cells that should not be modified."""

    # Construct request model with validation
    try:
        _request = _models.PostDevApiAppendCustomRowCellsRequest(
            path=_models.PostDevApiAppendCustomRowCellsRequestPath(table_name=table_name),
            body=_models.PostDevApiAppendCustomRowCellsRequestBody(data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for append_custom_table_rows: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/custom-records/custom-tables/{table_name}/rows/-/append", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/custom-records/custom-tables/{table_name}/rows/-/append"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("append_custom_table_rows")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("append_custom_table_rows", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="append_custom_table_rows",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Records
@mcp.tool()
async def remove_custom_table_row_cells(
    table_name: str = Field(..., description="The name of the custom table from which cells will be removed. This identifies the target table for the operation."),
    data: list[_models.CustomRowColumnContentsByColumnNameRequestBody] = Field(..., description="An array of row specifications indicating which cells to remove. Each row entry must specify the row identifier and list the column names whose cells should be cleared. All entries must use consistent column naming."),
) -> dict[str, Any] | ToolResult:
    """Remove specific cells from rows in a custom table. Specify which cells to clear by providing row identifiers and column names."""

    # Construct request model with validation
    try:
        _request = _models.PostDevApiRemoveCustomRowCellsRequest(
            path=_models.PostDevApiRemoveCustomRowCellsRequestPath(table_name=table_name),
            body=_models.PostDevApiRemoveCustomRowCellsRequestBody(data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_custom_table_row_cells: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/custom-records/custom-tables/{table_name}/rows/-/remove", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/custom-records/custom-tables/{table_name}/rows/-/remove"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_custom_table_row_cells")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_custom_table_row_cells", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_custom_table_row_cells",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Records
@mcp.tool()
async def list_matrix_tables() -> dict[str, Any] | ToolResult:
    """Retrieve all Matrix tables configured for your business. Matrix tables are custom data structures used to organize and manage complex, multi-dimensional business data."""

    # Extract parameters for API call
    _http_path = "/developer/v1/custom-records/matrix-tables"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_matrix_tables")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_matrix_tables", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_matrix_tables",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Records
@mcp.tool()
async def create_matrix_table(
    input_columns: list[_models.DeveloperApiMatrixInputColumnDefRequestBody] = Field(..., description="Array of input columns that define the matrix dimensions. Each column can reference existing fields or accept numeric values. The order of columns defines the lookup hierarchy."),
    label: str = Field(..., description="Human-readable display name for the matrix table, shown in the user interface."),
    result_columns: list[_models.DeveloperApiMatrixResultColumnDefRequestBody] = Field(..., description="Array of result columns that store the output values computed from the input column combinations. The order corresponds to the sequence of results returned."),
    name: str | None = Field(None, description="API identifier for the matrix table used in programmatic references. If not provided, a default name will be generated automatically."),
) -> dict[str, Any] | ToolResult:
    """Create a matrix table that maps unique combinations of input values to result values, enabling efficient lookup operations across multiple dimensions."""

    # Construct request model with validation
    try:
        _request = _models.PostDevApiMatrixTablesRequest(
            body=_models.PostDevApiMatrixTablesRequestBody(input_columns=input_columns, label=label, name=name, result_columns=result_columns)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_matrix_table: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/custom-records/matrix-tables"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_matrix_table")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_matrix_table", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_matrix_table",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Records
@mcp.tool()
async def add_result_column_to_matrix_table(
    table_name: str = Field(..., description="The name of the matrix table to which the result column will be added."),
    cardinality: Literal["many_to_many", "many_to_one"] = Field(..., description="The relationship cardinality for the result column: either many_to_one or many_to_many, defining how the result data relates to the matrix rows."),
    label: str = Field(..., description="The display name for the result column as it will appear in the user interface."),
    native_table: _models.PostDevApiAddMatrixResultColumnBodyNativeTable = Field(..., description="The native table that the result column references. Only users and accounting_field_options are supported as valid native tables."),
    name: str | None = Field(None, description="The API name for the result column used in programmatic access. If not provided, a default name will be generated."),
) -> dict[str, Any] | ToolResult:
    """Add a result column to an existing matrix table, enabling aggregation of user or accounting field data without modifying the table's input columns. Result columns can only reference users or accounting_field_options native tables."""

    # Construct request model with validation
    try:
        _request = _models.PostDevApiAddMatrixResultColumnRequest(
            path=_models.PostDevApiAddMatrixResultColumnRequestPath(table_name=table_name),
            body=_models.PostDevApiAddMatrixResultColumnRequestBody(cardinality=cardinality, label=label, name=name, native_table=native_table)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_result_column_to_matrix_table: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/custom-records/matrix-tables/{table_name}/columns", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/custom-records/matrix-tables/{table_name}/columns"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_result_column_to_matrix_table")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_result_column_to_matrix_table", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_result_column_to_matrix_table",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Records
@mcp.tool()
async def rename_matrix_column(
    column_name: str = Field(..., description="The current API name of the column to rename within the matrix table."),
    table_name: str = Field(..., description="The name of the matrix table containing the column to rename."),
    new_name: str = Field(..., description="The new API name to assign to the column. This becomes the identifier used in API requests and responses."),
) -> dict[str, Any] | ToolResult:
    """Rename the API identifier for a matrix table column while keeping its human-readable label unchanged. This operation works for both input and result columns in custom matrix records."""

    # Construct request model with validation
    try:
        _request = _models.PatchDevApiRenameMatrixColumnRequest(
            path=_models.PatchDevApiRenameMatrixColumnRequestPath(column_name=column_name, table_name=table_name),
            body=_models.PatchDevApiRenameMatrixColumnRequestBody(new_name=new_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for rename_matrix_column: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/custom-records/matrix-tables/{table_name}/columns/{column_name}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/custom-records/matrix-tables/{table_name}/columns/{column_name}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("rename_matrix_column")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("rename_matrix_column", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="rename_matrix_column",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Records
@mcp.tool()
async def list_matrix_table_rows(
    table_name: str = Field(..., description="The name of the matrix table to query."),
    external_keys: list[str] | None = Field(None, description="Optional list of external keys to filter results to specific rows. Only rows matching one of the provided keys are returned."),
    filters: list[_models.DeveloperApiMatrixColumnFilterRequestBody] | None = Field(None, description="Optional list of filters to apply against input column values. Only rows matching ALL specified filters are included in results."),
    page_size: int | None = Field(None, description="Maximum number of rows to return per page. Defaults to 100 rows."),
) -> dict[str, Any] | ToolResult:
    """Retrieve rows from a matrix table with inputs and results separated. Input columns are always complete, while result columns contain only values that have been explicitly set."""

    # Construct request model with validation
    try:
        _request = _models.PostDevApiMatrixListRowsRequest(
            path=_models.PostDevApiMatrixListRowsRequestPath(table_name=table_name),
            body=_models.PostDevApiMatrixListRowsRequestBody(external_keys=external_keys, filters=filters, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_matrix_table_rows: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/custom-records/matrix-tables/{table_name}/list-rows", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/custom-records/matrix-tables/{table_name}/list-rows"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_matrix_table_rows")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_matrix_table_rows", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_matrix_table_rows",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Records
@mcp.tool()
async def rename_matrix_table(
    table_name: str = Field(..., description="The current API name of the Matrix table to be renamed. This is the identifier used to reference the table in API operations."),
    new_name: str = Field(..., description="The new API name for the Matrix table. This will become the identifier used to reference the table in subsequent API operations."),
) -> dict[str, Any] | ToolResult:
    """Updates the API name of an existing Matrix table. This operation allows you to change how the table is referenced in API calls without affecting its underlying data or structure."""

    # Construct request model with validation
    try:
        _request = _models.PostDevApiRenameMatrixTableRequest(
            path=_models.PostDevApiRenameMatrixTableRequestPath(table_name=table_name),
            body=_models.PostDevApiRenameMatrixTableRequestBody(new_name=new_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for rename_matrix_table: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/custom-records/matrix-tables/{table_name}/rename", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/custom-records/matrix-tables/{table_name}/rename"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("rename_matrix_table")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("rename_matrix_table", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="rename_matrix_table",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Records
@mcp.tool()
async def upsert_matrix_table_rows(
    table_name: str = Field(..., description="The name of the matrix table to upsert rows into."),
    data: list[_models.MatrixRowInputByNameRequestBody] = Field(..., description="Array of row objects to create or update. Each row must include an external_key field to identify whether it should be created or updated. Order is not significant."),
) -> dict[str, Any] | ToolResult:
    """Creates new rows or updates existing rows in a matrix table. Rows are identified by their external_key; matching keys update existing rows while new keys create new rows. Result values can be partially updated."""

    # Construct request model with validation
    try:
        _request = _models.PutDevApiMatrixPutRowsRequest(
            path=_models.PutDevApiMatrixPutRowsRequestPath(table_name=table_name),
            body=_models.PutDevApiMatrixPutRowsRequestBody(data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for upsert_matrix_table_rows: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/custom-records/matrix-tables/{table_name}/rows", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/custom-records/matrix-tables/{table_name}/rows"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("upsert_matrix_table_rows")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("upsert_matrix_table_rows", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="upsert_matrix_table_rows",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Records
@mcp.tool()
async def append_matrix_table_cells(
    table_name: str = Field(..., description="The name of the matrix table where cells will be appended. This identifies which custom record table to update."),
    data: list[_models.MatrixRowInputByNameRequestBody] = Field(..., description="An array of row objects, each containing cells to append to many-to-many result columns. Order is preserved as provided. Each row should specify the target row and the cell values to add."),
) -> dict[str, Any] | ToolResult:
    """Append values to many-to-many result columns in a matrix table without replacing existing data. This operation only works with many-to-many relationship columns."""

    # Construct request model with validation
    try:
        _request = _models.PostDevApiMatrixAppendCellsRequest(
            path=_models.PostDevApiMatrixAppendCellsRequestPath(table_name=table_name),
            body=_models.PostDevApiMatrixAppendCellsRequestBody(data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for append_matrix_table_cells: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/custom-records/matrix-tables/{table_name}/rows/-/append", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/custom-records/matrix-tables/{table_name}/rows/-/append"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("append_matrix_table_cells")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("append_matrix_table_cells", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="append_matrix_table_cells",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Records
@mcp.tool()
async def remove_matrix_table_cells(
    table_name: str = Field(..., description="The name of the matrix table from which cells will be removed."),
    data: list[_models.MatrixRowInputByNameRequestBody] = Field(..., description="An array of row objects specifying which cells to remove from many-to-many result columns. Each row entry identifies the target row and the specific cell values to delete."),
) -> dict[str, Any] | ToolResult:
    """Remove specific cell values from many-to-many result columns in a matrix table without affecting other data in those rows."""

    # Construct request model with validation
    try:
        _request = _models.PostDevApiMatrixRemoveCellsRequest(
            path=_models.PostDevApiMatrixRemoveCellsRequestPath(table_name=table_name),
            body=_models.PostDevApiMatrixRemoveCellsRequestBody(data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_matrix_table_cells: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/custom-records/matrix-tables/{table_name}/rows/-/remove", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/custom-records/matrix-tables/{table_name}/rows/-/remove"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_matrix_table_cells")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_matrix_table_cells", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_matrix_table_cells",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Records
@mcp.tool()
async def delete_matrix_row(
    row_id: str = Field(..., description="The unique identifier of the matrix table row to delete."),
    table_name: str = Field(..., description="The name of the matrix table containing the row to delete."),
) -> dict[str, Any] | ToolResult:
    """Permanently removes a single row from a matrix table by its ID. This operation deletes the specified row and cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteDevApiDeleteMatrixRowRequest(
            path=_models.DeleteDevApiDeleteMatrixRowRequestPath(row_id=row_id, table_name=table_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_matrix_row: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/custom-records/matrix-tables/{table_name}/rows/{row_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/custom-records/matrix-tables/{table_name}/rows/{row_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_matrix_row")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_matrix_row", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_matrix_row",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Records
@mcp.tool()
async def list_native_tables() -> dict[str, Any] | ToolResult:
    """Retrieve a list of all native Ramp tables available in the developer environment. Use this to discover and reference custom record tables for integration purposes."""

    # Extract parameters for API call
    _http_path = "/developer/v1/custom-records/native-tables"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_native_tables")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_native_tables", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_native_tables",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Records
@mcp.tool()
async def list_native_table_columns(native_table_name: str = Field(..., description="The name of the native Ramp table for which to retrieve custom columns. This identifies the specific table whose column definitions should be listed.")) -> dict[str, Any] | ToolResult:
    """Retrieve all custom columns defined for a specified native Ramp table. This operation returns the column metadata and configuration for the given native table."""

    # Construct request model with validation
    try:
        _request = _models.GetDevApiNativeTableColumnRequest(
            path=_models.GetDevApiNativeTableColumnRequestPath(native_table_name=native_table_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_native_table_columns: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/custom-records/native-tables/{native_table_name}/columns", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/custom-records/native-tables/{native_table_name}/columns"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_native_table_columns")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_native_table_columns", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_native_table_columns",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Records
@mcp.tool()
async def list_native_table_rows(
    native_table_name: str = Field(..., description="The name of the Native Ramp table to query for rows."),
    include_all_referenced_rows: bool | None = Field(None, description="When enabled, includes all referenced rows within each cell instead of a limited subset. Defaults to false."),
    page_size: int | None = Field(None, description="Number of rows to return per request, up to a maximum of 100. Defaults to 50."),
    ramp_id: list[str] | None = Field(None, description="Filter results to include only rows associated with the specified Ramp object IDs. Provide as an array of IDs."),
) -> dict[str, Any] | ToolResult:
    """Retrieve rows and their custom column values from a Native Ramp table, with optional filtering by Ramp object IDs and configurable pagination."""

    # Construct request model with validation
    try:
        _request = _models.GetDevApiNativeRowRequest(
            path=_models.GetDevApiNativeRowRequestPath(native_table_name=native_table_name),
            query=_models.GetDevApiNativeRowRequestQuery(include_all_referenced_rows=include_all_referenced_rows, page_size=page_size, ramp_id=ramp_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_native_table_rows: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/custom-records/native-tables/{native_table_name}/rows", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/custom-records/native-tables/{native_table_name}/rows"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_native_table_rows")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_native_table_rows", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_native_table_rows",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Records
@mcp.tool()
async def update_native_table_rows(
    native_table_name: str = Field(..., description="The name of the Native Ramp table where rows will be inserted or updated."),
    data: list[_models.NativeRowColumnContentsByColumnNameRequestBody] = Field(..., description="An array of row objects to insert or update. All objects must contain the same set of column names; use `null` values for columns that should not be set on specific rows."),
) -> dict[str, Any] | ToolResult:
    """Insert or update rows in a Native Ramp table. Specify the table by name and provide row data with consistent column sets across all entries."""

    # Construct request model with validation
    try:
        _request = _models.PutDevApiNativeRowRequest(
            path=_models.PutDevApiNativeRowRequestPath(native_table_name=native_table_name),
            body=_models.PutDevApiNativeRowRequestBody(data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_native_table_rows: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/custom-records/native-tables/{native_table_name}/rows", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/custom-records/native-tables/{native_table_name}/rows"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_native_table_rows")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_native_table_rows", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_native_table_rows",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Records
@mcp.tool()
async def append_native_table_rows(
    native_table_name: str = Field(..., description="The name of the Native Ramp table where rows will be appended or updated."),
    data: list[_models.NativeRowColumnContentsByColumnNameRequestBody] = Field(..., description="An array of row objects to insert or update. Each row must contain the same set of column names. Use null for any column value that should not be set, allowing partial row updates."),
) -> dict[str, Any] | ToolResult:
    """Append or update rows in a Native Ramp table by providing cell data. Use null values to indicate cells that should not be modified."""

    # Construct request model with validation
    try:
        _request = _models.PostDevApiAppendNativeRowCellsRequest(
            path=_models.PostDevApiAppendNativeRowCellsRequestPath(native_table_name=native_table_name),
            body=_models.PostDevApiAppendNativeRowCellsRequestBody(data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for append_native_table_rows: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/custom-records/native-tables/{native_table_name}/rows/-/append", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/custom-records/native-tables/{native_table_name}/rows/-/append"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("append_native_table_rows")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("append_native_table_rows", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="append_native_table_rows",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Records
@mcp.tool()
async def remove_native_table_row_cells(
    native_table_name: str = Field(..., description="The name of the native table from which cells will be removed. This identifies the specific Native Ramp table to modify."),
    data: list[_models.NativeRowColumnContentsByColumnNameRequestBody] = Field(..., description="Array of row specifications indicating which cells to remove. Each row entry must specify the row identifier and the column names whose cells should be cleared. All entries must use consistent column naming."),
) -> dict[str, Any] | ToolResult:
    """Remove specific cells from rows in a Native Ramp table. Specify which cells to clear by providing row identifiers and column names."""

    # Construct request model with validation
    try:
        _request = _models.PostDevApiRemoveNativeRowCellsRequest(
            path=_models.PostDevApiRemoveNativeRowCellsRequestPath(native_table_name=native_table_name),
            body=_models.PostDevApiRemoveNativeRowCellsRequestBody(data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_native_table_row_cells: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/custom-records/native-tables/{native_table_name}/rows/-/remove", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/custom-records/native-tables/{native_table_name}/rows/-/remove"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_native_table_row_cells")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_native_table_row_cells", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_native_table_row_cells",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Department
@mcp.tool()
async def list_departments(page_size: int | None = Field(None, description="Number of departments to return per page. Must be between 2 and 100 items; defaults to 20 if not specified.")) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of all departments. Results are returned in pages with a configurable size to support efficient browsing of large department collections."""

    # Construct request model with validation
    try:
        _request = _models.GetDepartmentListWithPaginationRequest(
            query=_models.GetDepartmentListWithPaginationRequestQuery(page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_departments: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/departments"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_departments")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_departments", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_departments",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Department
@mcp.tool()
async def create_department(name: str = Field(..., description="The display name for the department. This identifier is used to reference the department throughout the system.")) -> dict[str, Any] | ToolResult:
    """Create a new department with the specified name. The department will be added to the organization and made available for use in resource allocation and team management."""

    # Construct request model with validation
    try:
        _request = _models.PostDepartmentListWithPaginationRequest(
            body=_models.PostDepartmentListWithPaginationRequestBody(name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_department: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/departments"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_department")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_department", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_department",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Department
@mcp.tool()
async def get_department(department_id: str = Field(..., description="The unique identifier of the department to retrieve, formatted as a UUID.")) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific department by its unique identifier."""

    # Construct request model with validation
    try:
        _request = _models.GetDepartmentResourceRequest(
            path=_models.GetDepartmentResourceRequestPath(department_id=department_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_department: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/departments/{department_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/departments/{department_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_department")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_department", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_department",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Department
@mcp.tool()
async def update_department(
    department_id: str = Field(..., description="The unique identifier of the department to update, formatted as a UUID."),
    name: str = Field(..., description="The new name for the department."),
) -> dict[str, Any] | ToolResult:
    """Update an existing department's information by its unique identifier. Allows modification of department details such as name."""

    # Construct request model with validation
    try:
        _request = _models.PatchDepartmentResourceRequest(
            path=_models.PatchDepartmentResourceRequestPath(department_id=department_id),
            body=_models.PatchDepartmentResourceRequestBody(name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_department: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/departments/{department_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/departments/{department_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_department")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_department", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_department",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Embedded Cards
@mcp.tool()
async def create_card_embed_token(
    card_id: str = Field(..., description="The unique identifier of the card for which to create an embed token."),
    parent_origin: str = Field(..., description="The origin URL where the card will be embedded, specified as a valid HTTP or HTTPS URL with hostname (e.g., https://app.example.com/). Localhost origins are not permitted in production environments."),
) -> dict[str, Any] | ToolResult:
    """Generate an embed initialization token for an activated card, enabling secure embedded card functionality on a specified origin. The card must be in an active state to create the token."""

    # Construct request model with validation
    try:
        _request = _models.PostRampEmbeddedCardResourceRequest(
            path=_models.PostRampEmbeddedCardResourceRequestPath(card_id=card_id),
            body=_models.PostRampEmbeddedCardResourceRequestBody(parent_origin=parent_origin)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_card_embed_token: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/embedded/cards/{card_id}/embed", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/embedded/cards/{card_id}/embed"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_card_embed_token")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_card_embed_token", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_card_embed_token",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Business Entities
@mcp.tool()
async def list_entities_with_pagination(
    currency: Literal["AED", "AFN", "ALL", "AMD", "ANG", "AOA", "ARS", "AUD", "AWG", "AZN", "BAM", "BBD", "BDT", "BGN", "BHD", "BIF", "BMD", "BND", "BOB", "BOV", "BRL", "BSD", "BTN", "BWP", "BYN", "BZD", "CAD", "CDF", "CHE", "CHF", "CHW", "CLF", "CLP", "CNH", "CNY", "COP", "COU", "CRC", "CUC", "CUP", "CVE", "CZK", "DJF", "DKK", "DOP", "DZD", "EGP", "ERN", "ETB", "EUR", "EURC", "FJD", "FKP", "GBP", "GEL", "GHS", "GIP", "GMD", "GNF", "GTQ", "GYD", "HKD", "HNL", "HRK", "HTG", "HUF", "IDR", "ILS", "INR", "IQD", "IRR", "ISK", "JMD", "JOD", "JPY", "KES", "KGS", "KHR", "KMF", "KPW", "KRW", "KWD", "KYD", "KZT", "LAK", "LBP", "LKR", "LRD", "LSL", "LYD", "MAD", "MDL", "MGA", "MKD", "MMK", "MNT", "MOP", "MRU", "MUR", "MVR", "MWK", "MXN", "MXV", "MYR", "MZN", "NAD", "NGN", "NIO", "NOK", "NPR", "NZD", "OMR", "PAB", "PEN", "PGK", "PHP", "PKR", "PLN", "PYG", "QAR", "RON", "RSD", "RUB", "RWF", "SAR", "SBD", "SCR", "SDG", "SEK", "SGD", "SHP", "SLE", "SLL", "SOS", "SRD", "SSP", "STN", "SVC", "SYP", "SZL", "THB", "TJS", "TMT", "TND", "TOP", "TRY", "TTD", "TWD", "TZS", "UAH", "UGX", "USD", "USDB", "USDC", "USN", "UYI", "UYU", "UYW", "UZS", "VED", "VES", "VND", "VUV", "WST", "XAD", "XAF", "XAG", "XAU", "XBA", "XBB", "XBC", "XBD", "XCD", "XCG", "XDR", "XOF", "XPD", "XPF", "XPT", "XSU", "XTS", "XUA", "XXX", "YER", "ZAR", "ZMW", "ZWG", "ZWL"] | None = Field(None, description="Filter results to entities using a specific currency code (e.g., USD, EUR, GBP). Accepts ISO 4217 currency codes and cryptocurrency variants."),
    entity_name: str | None = Field(None, description="Filter results to entities matching a specific name or partial name."),
    is_primary: bool | None = Field(None, description="Filter to return only primary entities (true) or only non-primary entities (false)."),
    hide_inactive: bool | None = Field(None, description="Exclude inactive entities from results. Defaults to false, which includes both active and inactive entities."),
    page_size: int | None = Field(None, description="Number of results per page. Must be between 2 and 100 inclusive. Defaults to 20 if not specified."),
    include_deleted_accounts: Any | None = Field(None, description="Include deleted accounts in the results."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of business entities with optional filtering by currency, name, primary status, and active state."""

    # Construct request model with validation
    try:
        _request = _models.GetEntityListWithPaginationRequest(
            query=_models.GetEntityListWithPaginationRequestQuery(currency=currency, entity_name=entity_name, is_primary=is_primary, hide_inactive=hide_inactive, page_size=page_size, include_deleted_accounts=include_deleted_accounts)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_entities_with_pagination: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/entities"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_entities_with_pagination")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_entities_with_pagination", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_entities_with_pagination",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Business Entities
@mcp.tool()
async def get_entity(
    entity_id: str = Field(..., description="The unique identifier of the business entity to retrieve, formatted as a UUID."),
    hide_inactive: bool | None = Field(None, description="When enabled, excludes inactive entities from the results. Defaults to false, returning all entities regardless of active status."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a specific business entity by its unique identifier. Optionally filter out inactive entities from the response."""

    # Construct request model with validation
    try:
        _request = _models.GetEntityResourceRequest(
            path=_models.GetEntityResourceRequestPath(entity_id=entity_id),
            query=_models.GetEntityResourceRequestQuery(hide_inactive=hide_inactive)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_entity: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/entities/{entity_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/entities/{entity_id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_entity")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_entity", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_entity",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Item Receipts
@mcp.tool()
async def list_item_receipts(
    page_size: int | None = Field(None, description="Number of results per page, between 2 and 100. Defaults to 20 if not specified."),
    entity_id: str | None = Field(None, description="Filter results to a specific business entity using its unique identifier (UUID format)."),
    purchase_order_line_item_id: str | None = Field(None, description="Filter results to a specific purchase order line item using its unique identifier (UUID format)."),
    purchase_order_id: str | None = Field(None, description="Filter results to a specific purchase order using its unique identifier (UUID format)."),
    include_archived: bool | None = Field(None, description="Include archived item receipts in the results. By default, only active receipts are returned."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of item receipts, optionally filtered by entity, purchase order, or line item. Archived receipts are excluded by default."""

    # Construct request model with validation
    try:
        _request = _models.GetItemReceiptsResourceRequest(
            query=_models.GetItemReceiptsResourceRequestQuery(page_size=page_size, entity_id=entity_id, purchase_order_line_item_id=purchase_order_line_item_id, purchase_order_id=purchase_order_id, include_archived=include_archived)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_item_receipts: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/item-receipts"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_item_receipts")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_item_receipts", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_item_receipts",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Item Receipts
@mcp.tool()
async def create_item_receipt(
    item_receipt_line_items: list[_models.ApiItemReceiptLineItemCreateParamsRequestBody] = Field(..., description="Array of line items included in this receipt, each specifying the items received. Order of items in the array is preserved as submitted."),
    item_receipt_number: str = Field(..., description="Unique identifier for this item receipt, used to reference and track the receipt in your system."),
    purchase_order_id: str = Field(..., description="The unique identifier (UUID format) of the purchase order this receipt is associated with. The receipt must be linked to an existing purchase order."),
    received_at: str = Field(..., description="The date when the vendor delivered or will deliver the goods or services, specified in ISO 8601 date format (YYYY-MM-DD)."),
    memo: str | None = Field(None, description="Optional internal note or comment associated with this item receipt for reference purposes."),
) -> dict[str, Any] | ToolResult:
    """Create a new item receipt to record goods or services received from a vendor against a purchase order. This documents the receipt of items and their delivery date."""

    # Construct request model with validation
    try:
        _request = _models.PostItemReceiptsResourceRequest(
            body=_models.PostItemReceiptsResourceRequestBody(item_receipt_line_items=item_receipt_line_items, item_receipt_number=item_receipt_number, memo=memo, purchase_order_id=purchase_order_id, received_at=received_at)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_item_receipt: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/item-receipts"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_item_receipt")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_item_receipt", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_item_receipt",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Item Receipts
@mcp.tool()
async def get_item_receipt(item_receipt_id: str = Field(..., description="The unique identifier of the item receipt to retrieve, formatted as a UUID.")) -> dict[str, Any] | ToolResult:
    """Retrieve a single item receipt by its unique identifier. Returns the complete receipt details for the specified item receipt."""

    # Construct request model with validation
    try:
        _request = _models.GetItemReceiptSingleResourceRequest(
            path=_models.GetItemReceiptSingleResourceRequestPath(item_receipt_id=item_receipt_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_item_receipt: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/item-receipts/{item_receipt_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/item-receipts/{item_receipt_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_item_receipt")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_item_receipt", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_item_receipt",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Item Receipts
@mcp.tool()
async def delete_item_receipt(item_receipt_id: str = Field(..., description="The unique identifier (UUID) of the item receipt to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a specific item receipt by its unique identifier. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteItemReceiptSingleResourceRequest(
            path=_models.DeleteItemReceiptSingleResourceRequestPath(item_receipt_id=item_receipt_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_item_receipt: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/item-receipts/{item_receipt_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/item-receipts/{item_receipt_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_item_receipt")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_item_receipt", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_item_receipt",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Limit
@mcp.tool()
async def list_spend_limits(
    entity_id: str | None = Field(None, description="Filter results to limits associated with a specific business entity, specified as a UUID."),
    spend_program_id: str | None = Field(None, description="Filter results to limits linked to a specific spend program, specified as a UUID."),
    card_id: str | None = Field(None, description="Filter results to limits associated with a specific card, specified as a UUID."),
    user_id: str | None = Field(None, description="Filter results to limits owned by a specific user, specified as a UUID."),
    is_terminated: bool | None = Field(None, description="When true, return only terminated spend limits; when false or omitted, return active limits."),
    user_access_roles: list[Literal["COORDINATOR", "COOWNER", "MEMBER", "OWNER"]] | None = Field(None, description="Filter by user access roles. Accepts one or more values from: OWNER, COOWNER, MEMBER. Can be provided as repeated parameters or comma-separated values. Only limits with matching access types are returned."),
    page_size: int | None = Field(None, description="Number of results per page, between 2 and 100 inclusive. Defaults to 20 if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of spend limits with optional filtering by entity, program, card, user, termination status, and access roles."""

    # Construct request model with validation
    try:
        _request = _models.GetSpendLimitListWithPaginationRequest(
            query=_models.GetSpendLimitListWithPaginationRequestQuery(entity_id=entity_id, spend_program_id=spend_program_id, card_id=card_id, user_id=user_id, is_terminated=is_terminated, user_access_roles=user_access_roles, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_spend_limits: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/limits"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_query = _serialize_query(_http_query, {
        "user_access_roles": ("form", False),
    })
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_spend_limits")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_spend_limits", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_spend_limits",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Limit
@mcp.tool()
async def create_spend_limit(
    idempotency_key: str = Field(..., description="A unique identifier (UUID) generated by the client to prevent duplicate limit creation if the request is retried. The server uses this to recognize and deduplicate subsequent attempts of the same request."),
    user_id: str = Field(..., description="UUID of the user who owns and is the primary user of this spend limit."),
    accounting_rules: list[_models.SpendLimitAccountingRulesDataRequestBody] | None = Field(None, description="Array of accounting rules to apply to this spend limit. Rules define how spending is categorized and tracked for accounting purposes."),
    is_shareable: bool | None = Field(None, description="Boolean flag indicating whether this spend limit can be shared and used by multiple users, or is restricted to the owner only."),
    permitted_spend_types: _models.PostSpendLimitCreationBodyPermittedSpendTypes | None = Field(None, description="Specifies which types of spending are allowed under this limit. Required when creating a limit without a spend program; ignored if spend_program_id is provided."),
    spend_program_id: str | None = Field(None, description="UUID of an existing spend program to associate with this limit. When provided, the limit inherits the program's spending restrictions and cannot override permitted spend types."),
    spending_restrictions: _models.PostSpendLimitCreationBodySpendingRestrictions | None = Field(None, description="Custom spending restrictions that define limits, categories, and rules for this limit. Ignored if spend_program_id is provided, as the limit will inherit the program's restrictions instead."),
) -> dict[str, Any] | ToolResult:
    """Create a new spend limit for a user. The limit can be associated with an existing spend program (inheriting its restrictions) or created independently with custom spending restrictions and permitted spend types."""

    # Construct request model with validation
    try:
        _request = _models.PostSpendLimitCreationRequest(
            body=_models.PostSpendLimitCreationRequestBody(accounting_rules=accounting_rules, idempotency_key=idempotency_key, is_shareable=is_shareable, permitted_spend_types=permitted_spend_types, spend_program_id=spend_program_id, spending_restrictions=spending_restrictions, user_id=user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_spend_limit: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/limits/deferred"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_spend_limit")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_spend_limit", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_spend_limit",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Limit
@mcp.tool()
async def get_spend_limit_deferred_task_status(task_id: str = Field(..., description="The unique identifier of the deferred task, provided as a UUID.")) -> dict[str, Any] | ToolResult:
    """Retrieve the current status of a deferred spend limit task. Use this to check the progress and outcome of asynchronous spend limit operations."""

    # Construct request model with validation
    try:
        _request = _models.GetSpendLimitDeferredTaskStatusRequest(
            path=_models.GetSpendLimitDeferredTaskStatusRequestPath(task_id=task_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_spend_limit_deferred_task_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/limits/deferred/status/{task_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/limits/deferred/status/{task_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_spend_limit_deferred_task_status")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_spend_limit_deferred_task_status", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_spend_limit_deferred_task_status",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Limit
@mcp.tool()
async def get_spend_limit(spend_limit_id: str = Field(..., description="The unique identifier of the spending limit to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve details for a specific spending limit by its ID. Use this to fetch current limit configuration and status."""

    # Construct request model with validation
    try:
        _request = _models.GetSpendLimitResourceRequest(
            path=_models.GetSpendLimitResourceRequestPath(spend_limit_id=spend_limit_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_spend_limit: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/limits/{spend_limit_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/limits/{spend_limit_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_spend_limit")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_spend_limit", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_spend_limit",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Limit
@mcp.tool()
async def update_spend_limit(
    spend_limit_id: str = Field(..., description="The unique identifier of the spend limit to update."),
    accounting_rules: list[_models.SpendLimitAccountingRulesDataRequestBody] | None = Field(None, description="Set or modify accounting rules that apply to all card transactions and reimbursements under this spend limit."),
    existing_expense_policy_agent_exemption_application_rules: Literal["APPLY_TO_ALL", "APPLY_TO_NONE"] | None = Field(None, description="Controls how policy agent exemptions apply to existing transactions when is_exempt_from_policy_agent is enabled. Use APPLY_TO_ALL to retroactively exempt all existing transactions, or APPLY_TO_NONE to exempt only future transactions."),
    is_exempt_from_policy_agent: bool | None = Field(None, description="When enabled, exempts this spend limit from policy agent review, preventing the policy agent from evaluating transactions against this limit."),
    is_shareable: bool | None = Field(None, description="When enabled, allows this spend limit to be shared among multiple users."),
    new_user_id: str | None = Field(None, description="Transfer ownership of this spend limit to a different user by providing their user ID."),
    permitted_spend_types: _models.PutSpendLimitResourceBodyPermittedSpendTypes | None = Field(None, description="Modify the types of spending permitted under this limit. When provided, all fields of permitted_spend_types must be included; partial updates are not supported."),
    spend_program_id: str | None = Field(None, description="Link this spend limit to a spend program, which will override the limit's spending restrictions and permitted spend types with those defined in the program. Pass null to detach the current spend program. This field cannot be combined with other update fields."),
    spending_restrictions: _models.PutSpendLimitResourceBodySpendingRestrictions | None = Field(None, description="Modify spending restrictions for this limit. When provided, the entire set of new restrictions must be specified, as they will completely replace all existing restrictions."),
) -> dict[str, Any] | ToolResult:
    """Update an existing spend limit's configuration, including accounting rules, policy agent exemptions, sharing settings, spending restrictions, and program associations."""

    # Construct request model with validation
    try:
        _request = _models.PutSpendLimitResourceRequest(
            path=_models.PutSpendLimitResourceRequestPath(spend_limit_id=spend_limit_id),
            body=_models.PutSpendLimitResourceRequestBody(accounting_rules=accounting_rules, existing_expense_policy_agent_exemption_application_rules=existing_expense_policy_agent_exemption_application_rules, is_exempt_from_policy_agent=is_exempt_from_policy_agent, is_shareable=is_shareable, new_user_id=new_user_id, permitted_spend_types=permitted_spend_types, spend_program_id=spend_program_id, spending_restrictions=spending_restrictions)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_spend_limit: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/limits/{spend_limit_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/limits/{spend_limit_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_spend_limit")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_spend_limit", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_spend_limit",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Limit
@mcp.tool()
async def update_spend_limit_partial(
    spend_limit_id: str = Field(..., description="The unique identifier of the spend limit to update."),
    accounting_rules: list[_models.SpendLimitAccountingRulesDataRequestBody] | None = Field(None, description="Set or modify accounting rules that apply to all card transactions and reimbursements under this spend limit."),
    existing_expense_policy_agent_exemption_application_rules: Literal["APPLY_TO_ALL", "APPLY_TO_NONE"] | None = Field(None, description="Controls how policy agent exemptions apply to existing transactions when is_exempt_from_policy_agent is enabled. Use APPLY_TO_ALL to retroactively exempt all existing transactions, or APPLY_TO_NONE to exempt only future transactions."),
    is_exempt_from_policy_agent: bool | None = Field(None, description="When enabled, exempts this spend limit from policy agent review, preventing the policy agent from evaluating transactions against this limit."),
    is_shareable: bool | None = Field(None, description="When enabled, allows this spend limit to be shared among multiple users."),
    new_user_id: str | None = Field(None, description="Transfer ownership of this spend limit to a different user by providing their user ID."),
    permitted_spend_types: _models.PatchSpendLimitResourceBodyPermittedSpendTypes | None = Field(None, description="Modify the types of spending permitted under this limit. When provided, all fields of permitted_spend_types must be included; partial updates are not supported."),
    spend_program_id: str | None = Field(None, description="Link this spend limit to a spend program, which will override the limit's spending restrictions and permitted spend types with those defined in the program. Pass null to detach the current spend program. This field cannot be combined with other update fields."),
    spending_restrictions: _models.PatchSpendLimitResourceBodySpendingRestrictions | None = Field(None, description="Replace all spending restrictions for this limit with a new set. When provided, the entire set of restrictions must be specified; existing restrictions will be completely overridden."),
) -> dict[str, Any] | ToolResult:
    """Update configuration for a spend limit, including accounting rules, policy agent exemptions, sharing settings, spending restrictions, and program associations."""

    # Construct request model with validation
    try:
        _request = _models.PatchSpendLimitResourceRequest(
            path=_models.PatchSpendLimitResourceRequestPath(spend_limit_id=spend_limit_id),
            body=_models.PatchSpendLimitResourceRequestBody(accounting_rules=accounting_rules, existing_expense_policy_agent_exemption_application_rules=existing_expense_policy_agent_exemption_application_rules, is_exempt_from_policy_agent=is_exempt_from_policy_agent, is_shareable=is_shareable, new_user_id=new_user_id, permitted_spend_types=permitted_spend_types, spend_program_id=spend_program_id, spending_restrictions=spending_restrictions)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_spend_limit_partial: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/limits/{spend_limit_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/limits/{spend_limit_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_spend_limit_partial")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_spend_limit_partial", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_spend_limit_partial",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Limit
@mcp.tool()
async def add_users_to_spend_limit(
    spend_limit_id: str = Field(..., description="The unique identifier (UUID) of the spend limit to which users will be added."),
    user_ids: list[str] | None = Field(None, description="Array of user identifiers to add to the shared spend limit. Each entry should be a valid user ID in the system."),
) -> dict[str, Any] | ToolResult:
    """Add one or more users to a shared spend limit, allowing them to access and manage the allocation together."""

    # Construct request model with validation
    try:
        _request = _models.PutSpendAllocationAddUsersRequest(
            path=_models.PutSpendAllocationAddUsersRequestPath(spend_limit_id=spend_limit_id),
            body=_models.PutSpendAllocationAddUsersRequestBody(user_ids=user_ids)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_users_to_spend_limit: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/limits/{spend_limit_id}/add-users", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/limits/{spend_limit_id}/add-users"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_users_to_spend_limit")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_users_to_spend_limit", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_users_to_spend_limit",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Limit
@mcp.tool()
async def terminate_spend_limit(
    spend_limit_id: str = Field(..., description="The unique identifier of the spend limit to terminate."),
    idempotency_key: str = Field(..., description="A unique value (typically a UUID) generated by the client to ensure idempotent request handling. The server uses this to recognize and deduplicate retries of the same request."),
) -> dict[str, Any] | ToolResult:
    """Permanently terminate a spend limit by creating an asynchronous task. The operation is idempotent and can be safely retried."""

    # Construct request model with validation
    try:
        _request = _models.PostSpendLimitTerminationResourceRequest(
            path=_models.PostSpendLimitTerminationResourceRequestPath(spend_limit_id=spend_limit_id),
            body=_models.PostSpendLimitTerminationResourceRequestBody(idempotency_key=idempotency_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for terminate_spend_limit: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/limits/{spend_limit_id}/deferred/termination", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/limits/{spend_limit_id}/deferred/termination"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("terminate_spend_limit")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("terminate_spend_limit", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="terminate_spend_limit",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Limit
@mcp.tool()
async def remove_users_from_spend_limit(
    spend_limit_id: str = Field(..., description="The unique identifier (UUID) of the spend limit from which users will be removed."),
    user_ids: list[str] | None = Field(None, description="Array of user identifiers to remove from the spend limit. If omitted, no users are removed."),
) -> dict[str, Any] | ToolResult:
    """Remove one or more users from a shared spend limit, revoking their access to that limit's budget allocation."""

    # Construct request model with validation
    try:
        _request = _models.DeleteSpendAllocationDeleteUsersRequest(
            path=_models.DeleteSpendAllocationDeleteUsersRequestPath(spend_limit_id=spend_limit_id),
            body=_models.DeleteSpendAllocationDeleteUsersRequestBody(user_ids=user_ids)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_users_from_spend_limit: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/limits/{spend_limit_id}/delete-users", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/limits/{spend_limit_id}/delete-users"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_users_from_spend_limit")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_users_from_spend_limit", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_users_from_spend_limit",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Limit
@mcp.tool()
async def suspend_spend_limit(spend_limit_id: str = Field(..., description="The unique identifier of the spend limit to suspend.")) -> dict[str, Any] | ToolResult:
    """Suspend an active spend limit to temporarily halt enforcement of spending restrictions without deleting the limit configuration."""

    # Construct request model with validation
    try:
        _request = _models.PostSpendLimitSuspensionResourceRequest(
            path=_models.PostSpendLimitSuspensionResourceRequestPath(spend_limit_id=spend_limit_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for suspend_spend_limit: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/limits/{spend_limit_id}/suspension", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/limits/{spend_limit_id}/suspension"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("suspend_spend_limit")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("suspend_spend_limit", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="suspend_spend_limit",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Limit
@mcp.tool()
async def unsuspend_spend_limit(spend_limit_id: str = Field(..., description="The unique identifier of the spend limit to unsuspend.")) -> dict[str, Any] | ToolResult:
    """Reactivate a suspended spending limit, allowing it to enforce restrictions again."""

    # Construct request model with validation
    try:
        _request = _models.PostSpendLimitUnsuspensionResourceRequest(
            path=_models.PostSpendLimitUnsuspensionResourceRequestPath(spend_limit_id=spend_limit_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for unsuspend_spend_limit: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/limits/{spend_limit_id}/unsuspension", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/limits/{spend_limit_id}/unsuspension"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("unsuspend_spend_limit")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("unsuspend_spend_limit", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="unsuspend_spend_limit",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Location
@mcp.tool()
async def list_locations(
    entity_id: str | None = Field(None, description="Filter results to locations associated with a specific business entity, specified as a UUID."),
    page_size: int | None = Field(None, description="Number of results per page, between 2 and 100 inclusive. Defaults to 20 if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of business locations, optionally filtered by a specific business entity."""

    # Construct request model with validation
    try:
        _request = _models.GetLocationListResourceRequest(
            query=_models.GetLocationListResourceRequestQuery(entity_id=entity_id, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_locations: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/locations"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_locations")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_locations", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_locations",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Location
@mcp.tool()
async def create_location(
    name: str = Field(..., description="The display name for the location. This is a required field that uniquely identifies the location within its entity."),
    entity_id: str | None = Field(None, description="UUID identifier of the business entity this location belongs to. If not provided, the location may be created under a default or current entity context."),
) -> dict[str, Any] | ToolResult:
    """Create a new location for a business entity. The location will be associated with the specified entity and identified by the provided name."""

    # Construct request model with validation
    try:
        _request = _models.PostLocationListResourceRequest(
            body=_models.PostLocationListResourceRequestBody(entity_id=entity_id, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_location: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/locations"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_location")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_location", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_location",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Location
@mcp.tool()
async def get_location(location_id: str = Field(..., description="The unique identifier of the location to retrieve, formatted as a UUID.")) -> dict[str, Any] | ToolResult:
    """Retrieve a specific location by its unique identifier. Returns detailed information about the requested location."""

    # Construct request model with validation
    try:
        _request = _models.GetLocationSingleResourceRequest(
            path=_models.GetLocationSingleResourceRequestPath(location_id=location_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_location: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/locations/{location_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/locations/{location_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_location")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_location", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_location",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Location
@mcp.tool()
async def update_location(
    location_id: str = Field(..., description="The unique identifier of the location to update, formatted as a UUID."),
    name: str = Field(..., description="The updated name for the location."),
    entity_id: str | None = Field(None, description="The UUID of the business entity this location belongs to. Provide this to reassign the location to a different entity."),
) -> dict[str, Any] | ToolResult:
    """Update an existing location's details, including its name and associated business entity. Provide the location ID and the fields you want to update."""

    # Construct request model with validation
    try:
        _request = _models.PatchLocationSingleResourceRequest(
            path=_models.PatchLocationSingleResourceRequestPath(location_id=location_id),
            body=_models.PatchLocationSingleResourceRequestBody(entity_id=entity_id, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_location: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/locations/{location_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/locations/{location_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_location")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_location", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_location",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Memo
@mcp.tool()
async def list_memos(
    card_id: str | None = Field(None, description="Filter results to memos associated with a specific card. Provide the card's UUID."),
    department_id: str | None = Field(None, description="Filter results to memos associated with a specific department. Provide the department's UUID."),
    location_id: str | None = Field(None, description="Filter results to memos associated with a specific location. Provide the location's UUID."),
    merchant_id: str | None = Field(None, description="Filter results to memos associated with a specific merchant. Provide the merchant's UUID."),
    user_id: str | None = Field(None, description="Filter results to memos associated with a specific user. Provide the user's UUID."),
    page_size: int | None = Field(None, description="Number of memos to return per page. Must be between 2 and 100 inclusive. Defaults to 20 if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of memos with optional filtering by card, department, location, merchant, or user. Results are returned in pages with configurable size."""

    # Construct request model with validation
    try:
        _request = _models.GetMemoListWithPaginationRequest(
            query=_models.GetMemoListWithPaginationRequestQuery(card_id=card_id, department_id=department_id, location_id=location_id, merchant_id=merchant_id, user_id=user_id, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_memos: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/memos"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_memos")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_memos", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_memos",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Memo
@mcp.tool()
async def get_memo(transaction_id: str = Field(..., description="The unique identifier of the transaction in UUID format.")) -> dict[str, Any] | ToolResult:
    """Retrieve a transaction memo by its unique identifier. Returns the memo details associated with the specified transaction."""

    # Construct request model with validation
    try:
        _request = _models.GetMemoSingleResourceRequest(
            path=_models.GetMemoSingleResourceRequestPath(transaction_id=transaction_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_memo: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/memos/{transaction_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/memos/{transaction_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_memo")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_memo", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_memo",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Memo
@mcp.tool()
async def create_memo_for_transaction(
    transaction_id: str = Field(..., description="The unique identifier of the transaction to which the memo will be attached. Must be a valid UUID format."),
    memo: str = Field(..., description="The text content of the memo. Limited to a maximum of 255 characters.", max_length=255),
) -> dict[str, Any] | ToolResult:
    """Create and attach a new memo to a specific transaction. The memo text is limited to 255 characters and serves as a note or annotation for the transaction record."""

    # Construct request model with validation
    try:
        _request = _models.PostMemoCreateSingleResourceRequest(
            path=_models.PostMemoCreateSingleResourceRequestPath(transaction_id=transaction_id),
            body=_models.PostMemoCreateSingleResourceRequestBody(memo=memo)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_memo_for_transaction: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/memos/{transaction_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/memos/{transaction_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_memo_for_transaction")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_memo_for_transaction", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_memo_for_transaction",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Merchant
@mcp.tool()
async def list_merchants(
    transaction_from_date: str | None = Field(None, description="Filter results to include only merchants with transactions on or after this date. Specify as an ISO 8601 datetime string."),
    transaction_to_date: str | None = Field(None, description="Filter results to include only merchants with transactions on or before this date. Specify as an ISO 8601 datetime string."),
    page_size: int | None = Field(None, description="Number of merchants to return per page. Must be between 2 and 100 inclusive; defaults to 20 if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of merchants, optionally filtered by transaction date range. Use pagination parameters to control result set size."""

    # Construct request model with validation
    try:
        _request = _models.GetMerchantListWithPaginationRequest(
            query=_models.GetMerchantListWithPaginationRequestQuery(transaction_from_date=transaction_from_date, transaction_to_date=transaction_to_date, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_merchants: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/merchants"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_merchants")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_merchants", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_merchants",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Purchase Order
@mcp.tool()
async def list_purchase_orders(
    creation_source: Literal["ACCOUNTING_PROVIDER", "DEVELOPER_API", "RAMP"] | None = Field(None, description="Filter purchase orders by their creation source: ACCOUNTING_PROVIDER (imported from accounting software), DEVELOPER_API (created via API), or RAMP (created through Ramp platform)."),
    receipt_status: Literal["FULLY_RECEIVED", "NOT_RECEIVED", "OVER_RECEIVED", "PARTIALLY_RECEIVED"] | None = Field(None, description="Filter purchase orders by receipt status: NOT_RECEIVED (no items received), PARTIALLY_RECEIVED (some items received), FULLY_RECEIVED (all items received), or OVER_RECEIVED (more items received than ordered)."),
    page_size: int | None = Field(None, description="Number of results per page, between 2 and 100. Defaults to 20 if not specified."),
    entity_id: str | None = Field(None, description="Filter results to purchase orders associated with a specific business entity using its unique identifier."),
    spend_request_id: str | None = Field(None, description="Filter results to purchase orders linked to a specific spend request using its unique identifier."),
    three_way_match_enabled: bool | None = Field(None, description="Filter to include only purchase orders where three-way match (PO, receipt, and invoice reconciliation) is enabled. Defaults to false."),
    include_archived: bool | None = Field(None, description="Include archived purchase orders in results. By default, only active purchase orders are returned."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of purchase orders with optional filtering by creation source, receipt status, entity, spend request, and three-way match configuration. Supports inclusion of archived purchase orders."""

    # Construct request model with validation
    try:
        _request = _models.GetPurchaseOrdersResourceRequest(
            query=_models.GetPurchaseOrdersResourceRequestQuery(creation_source=creation_source, receipt_status=receipt_status, page_size=page_size, entity_id=entity_id, spend_request_id=spend_request_id, three_way_match_enabled=three_way_match_enabled, include_archived=include_archived)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_purchase_orders: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/purchase-orders"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_purchase_orders")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_purchase_orders", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_purchase_orders",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Purchase Order
@mcp.tool()
async def create_purchase_order(
    currency: Literal["AED", "AFN", "ALL", "AMD", "ANG", "AOA", "ARS", "AUD", "AWG", "AZN", "BAM", "BBD", "BDT", "BGN", "BHD", "BIF", "BMD", "BND", "BOB", "BOV", "BRL", "BSD", "BTN", "BWP", "BYN", "BZD", "CAD", "CDF", "CHE", "CHF", "CHW", "CLF", "CLP", "CNH", "CNY", "COP", "COU", "CRC", "CUC", "CUP", "CVE", "CZK", "DJF", "DKK", "DOP", "DZD", "EGP", "ERN", "ETB", "EUR", "EURC", "FJD", "FKP", "GBP", "GEL", "GHS", "GIP", "GMD", "GNF", "GTQ", "GYD", "HKD", "HNL", "HRK", "HTG", "HUF", "IDR", "ILS", "INR", "IQD", "IRR", "ISK", "JMD", "JOD", "JPY", "KES", "KGS", "KHR", "KMF", "KPW", "KRW", "KWD", "KYD", "KZT", "LAK", "LBP", "LKR", "LRD", "LSL", "LYD", "MAD", "MDL", "MGA", "MKD", "MMK", "MNT", "MOP", "MRU", "MUR", "MVR", "MWK", "MXN", "MXV", "MYR", "MZN", "NAD", "NGN", "NIO", "NOK", "NPR", "NZD", "OMR", "PAB", "PEN", "PGK", "PHP", "PKR", "PLN", "PYG", "QAR", "RON", "RSD", "RUB", "RWF", "SAR", "SBD", "SCR", "SDG", "SEK", "SGD", "SHP", "SLE", "SLL", "SOS", "SRD", "SSP", "STN", "SVC", "SYP", "SZL", "THB", "TJS", "TMT", "TND", "TOP", "TRY", "TTD", "TWD", "TZS", "UAH", "UGX", "USD", "USDB", "USDC", "USN", "UYI", "UYU", "UYW", "UZS", "VED", "VES", "VND", "VUV", "WST", "XAD", "XAF", "XAG", "XAU", "XBA", "XBB", "XBC", "XBD", "XCD", "XCG", "XDR", "XOF", "XPD", "XPF", "XPT", "XSU", "XTS", "XUA", "XXX", "YER", "ZAR", "ZMW", "ZWG", "ZWL"] = Field(..., description="The currency code for the purchase order amount. Must be a valid ISO 4217 currency code (e.g., USD, EUR, GBP)."),
    entity_id: str = Field(..., description="The UUID of the business entity associated with this purchase order."),
    line_items: list[_models.ApiPurchaseOrderLineItemCreateParamsRequestBody] = Field(..., description="Array of line items detailing the goods or services being purchased. Each item should include quantity, description, and unit price information."),
    three_way_match_enabled: bool = Field(..., description="Whether three-way matching is required for this purchase order. When enabled, an item receipt must be attached to confirm goods were received before payment."),
    accounting_field_selections: list[_models.ApiCreateAccountingFieldParamsRequestBody] | None = Field(None, description="List of accounting field selections to code the purchase order for financial tracking. Typically only one vendor accounting field is applied per purchase order."),
    memo: str | None = Field(None, description="Optional internal memo or notes for the purchase order."),
    net_payment_terms: int | None = Field(None, description="Number of days after invoice receipt within which payment must be made to the vendor."),
    promise_date: str | None = Field(None, description="The expected delivery date for goods or services from the vendor, specified in ISO 8601 date format (YYYY-MM-DD)."),
    purchase_order_number: str | None = Field(None, description="Unique purchase order identifier with format prefix-number. Prefixes may contain only numbers, uppercase letters, and dashes; invalid characters are automatically removed. If omitted, a number is auto-generated using the procurement settings prefix."),
    spend_end_date: str | None = Field(None, description="The end date for authorized spending under this purchase order, specified in ISO 8601 date format (YYYY-MM-DD)."),
    spend_start_date: str | None = Field(None, description="The start date for authorized spending under this purchase order, specified in ISO 8601 date format (YYYY-MM-DD)."),
    vendor_id: str | None = Field(None, description="The UUID of the vendor supplying the goods or services for this purchase order."),
) -> dict[str, Any] | ToolResult:
    """Create a new purchase order for a business entity with specified line items, vendor, and payment terms. Supports optional three-way matching for receipt verification and accounting field coding."""

    # Construct request model with validation
    try:
        _request = _models.PostPurchaseOrdersResourceRequest(
            body=_models.PostPurchaseOrdersResourceRequestBody(accounting_field_selections=accounting_field_selections, currency=currency, entity_id=entity_id, line_items=line_items, memo=memo, net_payment_terms=net_payment_terms, promise_date=promise_date, purchase_order_number=purchase_order_number, spend_end_date=spend_end_date, spend_start_date=spend_start_date, three_way_match_enabled=three_way_match_enabled, vendor_id=vendor_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_purchase_order: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/purchase-orders"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_purchase_order")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_purchase_order", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_purchase_order",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Purchase Order
@mcp.tool()
async def get_purchase_order(purchase_order_id: str = Field(..., description="The unique identifier of the purchase order to retrieve, formatted as a UUID.")) -> dict[str, Any] | ToolResult:
    """Retrieve a single purchase order by its unique identifier. Returns the complete purchase order details including line items, pricing, and status information."""

    # Construct request model with validation
    try:
        _request = _models.GetPurchaseOrderSingleResourceRequest(
            path=_models.GetPurchaseOrderSingleResourceRequestPath(purchase_order_id=purchase_order_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_purchase_order: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/purchase-orders/{purchase_order_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/purchase-orders/{purchase_order_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_purchase_order")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_purchase_order", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_purchase_order",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Purchase Order
@mcp.tool()
async def update_purchase_order(
    purchase_order_id: str = Field(..., description="The unique identifier of the purchase order to update, formatted as a UUID."),
    accounting_field_selections: list[_models.ApiCreateAccountingFieldParamsRequestBody] | None = Field(None, description="List of accounting field options to assign for coding the purchase order at the body level. Updates are applied in an all-or-nothing manner; typically only a single vendor accounting field is supported per purchase order."),
    spend_end_date: str | None = Field(None, description="The end date for spending on this purchase order, specified in ISO 8601 date format (YYYY-MM-DD)."),
    spend_start_date: str | None = Field(None, description="The start date for spending on this purchase order, specified in ISO 8601 date format (YYYY-MM-DD)."),
) -> dict[str, Any] | ToolResult:
    """Update an approved purchase order's spending dates and accounting field selections. Changes to accounting fields are applied atomically—all selections must be valid or the entire update will be rejected."""

    # Construct request model with validation
    try:
        _request = _models.PatchPurchaseOrderSingleResourceRequest(
            path=_models.PatchPurchaseOrderSingleResourceRequestPath(purchase_order_id=purchase_order_id),
            body=_models.PatchPurchaseOrderSingleResourceRequestBody(accounting_field_selections=accounting_field_selections, spend_end_date=spend_end_date, spend_start_date=spend_start_date)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_purchase_order: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/purchase-orders/{purchase_order_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/purchase-orders/{purchase_order_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_purchase_order")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_purchase_order", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_purchase_order",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Purchase Order
@mcp.tool()
async def archive_purchase_order(
    purchase_order_id: str = Field(..., description="The unique identifier (UUID) of the purchase order to archive."),
    archived_reason: str | None = Field(None, description="Optional reason documenting why the purchase order is being archived."),
) -> dict[str, Any] | ToolResult:
    """Archive a purchase order by its ID, optionally recording the reason for archival. Archived purchase orders are removed from active workflows but retained for historical records."""

    # Construct request model with validation
    try:
        _request = _models.PostPurchaseOrderArchiveResourceRequest(
            path=_models.PostPurchaseOrderArchiveResourceRequestPath(purchase_order_id=purchase_order_id),
            body=_models.PostPurchaseOrderArchiveResourceRequestBody(archived_reason=archived_reason)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for archive_purchase_order: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/purchase-orders/{purchase_order_id}/archive", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/purchase-orders/{purchase_order_id}/archive"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("archive_purchase_order")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("archive_purchase_order", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="archive_purchase_order",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Purchase Order
@mcp.tool()
async def add_line_items_to_purchase_order(
    purchase_order_id: str = Field(..., description="The unique identifier of the purchase order to which line items will be added."),
    line_items: list[_models.ApiPurchaseOrderLineItemCreateParamsRequestBody] = Field(..., description="An array of line item objects to add to the purchase order. Each item represents a product or service to be included in the order. The order of items in the array is preserved."),
) -> dict[str, Any] | ToolResult:
    """Add one or more line items to an existing purchase order. Existing line items remain unchanged; only new items are appended."""

    # Construct request model with validation
    try:
        _request = _models.PostPurchaseOrderLineItemsResourceRequest(
            path=_models.PostPurchaseOrderLineItemsResourceRequestPath(purchase_order_id=purchase_order_id),
            body=_models.PostPurchaseOrderLineItemsResourceRequestBody(line_items=line_items)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_line_items_to_purchase_order: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/purchase-orders/{purchase_order_id}/line-items", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/purchase-orders/{purchase_order_id}/line-items"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_line_items_to_purchase_order")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_line_items_to_purchase_order", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_line_items_to_purchase_order",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Purchase Order
@mcp.tool()
async def update_purchase_order_line_item(
    line_item_id: str = Field(..., description="The unique identifier of the line item to update."),
    purchase_order_id: str = Field(..., description="The unique identifier of the purchase order containing the line item."),
    accounting_field_selections: list[_models.ApiCreateAccountingFieldParamsRequestBody] | None = Field(None, description="List of accounting field options to assign to this line item for coding purposes. Updates are applied atomically—all selections must be valid or the entire operation fails."),
    description: str | None = Field(None, description="Text description of the line item contents or purpose."),
    unit_price: str | None = Field(None, description="Unit price for the line item. Accepts numeric values or numeric strings."),
    unit_quantity: int | None = Field(None, description="Quantity of units for the line item. Must be a positive integer."),
) -> dict[str, Any] | ToolResult:
    """Update a single line item on an approved purchase order. Modify pricing, quantity, description, or accounting field assignments for the line item."""

    # Construct request model with validation
    try:
        _request = _models.PatchPurchaseOrderLineItemSingleResourceRequest(
            path=_models.PatchPurchaseOrderLineItemSingleResourceRequestPath(line_item_id=line_item_id, purchase_order_id=purchase_order_id),
            body=_models.PatchPurchaseOrderLineItemSingleResourceRequestBody(accounting_field_selections=accounting_field_selections, description=description, unit_price=unit_price, unit_quantity=unit_quantity)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_purchase_order_line_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/purchase-orders/{purchase_order_id}/line-items/{line_item_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/purchase-orders/{purchase_order_id}/line-items/{line_item_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_purchase_order_line_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_purchase_order_line_item", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_purchase_order_line_item",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Purchase Order
@mcp.tool()
async def delete_purchase_order_line_item(
    line_item_id: str = Field(..., description="The unique identifier of the line item to be deleted from the purchase order."),
    purchase_order_id: str = Field(..., description="The unique identifier of the purchase order containing the line item to be deleted."),
) -> dict[str, Any] | ToolResult:
    """Remove a single line item from an approved purchase order. The purchase order must be in an approved state before line items can be deleted."""

    # Construct request model with validation
    try:
        _request = _models.DeletePurchaseOrderLineItemSingleResourceRequest(
            path=_models.DeletePurchaseOrderLineItemSingleResourceRequestPath(line_item_id=line_item_id, purchase_order_id=purchase_order_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_purchase_order_line_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/purchase-orders/{purchase_order_id}/line-items/{line_item_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/purchase-orders/{purchase_order_id}/line-items/{line_item_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_purchase_order_line_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_purchase_order_line_item", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_purchase_order_line_item",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Receipt Integrations
@mcp.tool()
async def list_receipt_integration_opted_out_emails(
    email: str | None = Field(None, description="Filter results to a specific email address. Must be a valid email format."),
    id_: str | None = Field(None, alias="id", description="Filter results to a specific receipt integration by its unique identifier (UUID format)."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a list of email addresses that have opted out of receipt integrations. Optionally filter results by a specific email address or integration ID."""

    # Construct request model with validation
    try:
        _request = _models.GetReceiptIntegrationOptedOutEmailsListResourceRequest(
            body=_models.GetReceiptIntegrationOptedOutEmailsListResourceRequestBody(email=email, id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_receipt_integration_opted_out_emails: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/receipt-integrations/opt-out"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_receipt_integration_opted_out_emails")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_receipt_integration_opted_out_emails", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_receipt_integration_opted_out_emails",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Receipt Integrations
@mcp.tool()
async def remove_opted_out_email_from_receipt_integration(mailbox_opted_out_email_uuid: str = Field(..., description="The unique identifier (UUID) of the opted-out email record to remove from the opt-out list.")) -> dict[str, Any] | ToolResult:
    """Remove an email address from the receipt integration opt-out list, allowing it to receive receipt integrations again."""

    # Construct request model with validation
    try:
        _request = _models.DeleteReceiptIntegrationOptedOutEmailsDeleteResourceRequest(
            path=_models.DeleteReceiptIntegrationOptedOutEmailsDeleteResourceRequestPath(mailbox_opted_out_email_uuid=mailbox_opted_out_email_uuid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_opted_out_email_from_receipt_integration: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/receipt-integrations/opt-out/{mailbox_opted_out_email_uuid}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/receipt-integrations/opt-out/{mailbox_opted_out_email_uuid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_opted_out_email_from_receipt_integration")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_opted_out_email_from_receipt_integration", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_opted_out_email_from_receipt_integration",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Receipt
@mcp.tool()
async def list_receipts(
    reimbursement_id: str | None = Field(None, description="Filter results to receipts associated with a specific reimbursement using its unique identifier."),
    transaction_id: str | None = Field(None, description="Filter results to receipts associated with a specific transaction using its unique identifier."),
    page_size: int | None = Field(None, description="Number of receipts to return per page. Must be between 2 and 100 results; defaults to 20 if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of receipts, optionally filtered by reimbursement or transaction. Use pagination to control result set size."""

    # Construct request model with validation
    try:
        _request = _models.GetReceiptListRequest(
            query=_models.GetReceiptListRequestQuery(reimbursement_id=reimbursement_id, transaction_id=transaction_id, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_receipts: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/receipts"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_receipts")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_receipts", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_receipts",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Receipt
@mcp.tool()
async def upload_receipt(
    idempotency_key: str = Field(..., description="A unique identifier (UUID) that prevents duplicate uploads. Use a UUID to ensure idempotency across retries."),
    user_id: str = Field(..., description="UUID of the user associated with this receipt. This affects the priority and accuracy of automatic transaction matching."),
    transaction_id: str | None = Field(None, description="Optional UUID of the transaction to attach this receipt to. If omitted, Ramp will attempt to automatically match the receipt to the most relevant transaction."),
) -> dict[str, Any] | ToolResult:
    """Upload a receipt image and optionally link it to a transaction. If a transaction ID is provided, the receipt attaches directly to that transaction; otherwise, Ramp automatically matches the receipt to the most relevant transaction based on context."""

    # Construct request model with validation
    try:
        _request = _models.PostReceiptUploadRequest(
            body=_models.PostReceiptUploadRequestBody(idempotency_key=idempotency_key, transaction_id=transaction_id, user_id=user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for upload_receipt: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/receipts"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("upload_receipt")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("upload_receipt", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="upload_receipt",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Receipt
@mcp.tool()
async def get_receipt(receipt_id: str = Field(..., description="The unique identifier of the receipt to retrieve, formatted as a UUID.")) -> dict[str, Any] | ToolResult:
    """Retrieve a single receipt by its unique identifier. Returns the complete receipt details for the specified receipt ID."""

    # Construct request model with validation
    try:
        _request = _models.GetReceiptSingleResourceRequest(
            path=_models.GetReceiptSingleResourceRequestPath(receipt_id=receipt_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_receipt: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/receipts/{receipt_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/receipts/{receipt_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_receipt")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_receipt", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_receipt",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Reimbursement
@mcp.tool()
async def list_reimbursements(
    direction: Literal["BUSINESS_TO_USER", "USER_TO_BUSINESS"] | None = Field(None, description="Filter reimbursements by direction: BUSINESS_TO_USER for standard reimbursements (default) or USER_TO_BUSINESS for repayments from users back to the business."),
    sync_status: Literal["NOT_SYNC_READY", "SYNCED", "SYNC_READY"] | None = Field(None, description="Filter by synchronization status: NOT_SYNC_READY (not ready for sync), SYNC_READY (ready to sync), or SYNCED (already synchronized)."),
    from_transaction_date: str | None = Field(None, description="Filter reimbursements by the underlying transaction date, returning only those on or after this date (ISO 8601 format)."),
    to_transaction_date: str | None = Field(None, description="Filter reimbursements by the underlying transaction date, returning only those on or before this date (ISO 8601 format)."),
    awaiting_approval_by_user_id: str | None = Field(None, description="Filter for reimbursements awaiting approval from a specific user, identified by their UUID."),
    has_been_approved: bool | None = Field(None, description="Filter reimbursements by approval status: true for approved reimbursements, false for unapproved. Omit to return all reimbursements regardless of approval status."),
    trip_id: str | None = Field(None, description="Filter reimbursements associated with a specific trip, identified by its UUID."),
    accounting_field_selection_id: str | None = Field(None, description="Filter reimbursements by accounting field selection, identified by its UUID. This uniquely identifies an accounting field selection configuration on Ramp."),
    entity_id: str | None = Field(None, description="Filter reimbursements by business entity, identified by its UUID."),
    from_submitted_at: str | None = Field(None, description="Filter reimbursements by submission date, returning only those submitted on or after this date (ISO 8601 format)."),
    to_submitted_at: str | None = Field(None, description="Filter reimbursements by submission date, returning only those submitted on or before this date (ISO 8601 format)."),
    synced_after: str | None = Field(None, description="Filter reimbursements by sync date, returning only those synchronized on or after this date (ISO 8601 format)."),
    updated_after: str | None = Field(None, description="Filter reimbursements by last update date, returning only those updated on or after this date (ISO 8601 format)."),
    page_size: int | None = Field(None, description="Number of results per page; must be between 2 and 100. Defaults to 20 if not specified."),
    user_id: str | None = Field(None, description="Filter reimbursements by user, identified by their UUID."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of reimbursements with flexible filtering by direction, approval status, dates, and associated entities. Supports filtering by transaction dates, submission dates, sync status, and approval workflows."""

    # Construct request model with validation
    try:
        _request = _models.GetReimbursementListWithPaginationRequest(
            query=_models.GetReimbursementListWithPaginationRequestQuery(direction=direction, sync_status=sync_status, from_transaction_date=from_transaction_date, to_transaction_date=to_transaction_date, awaiting_approval_by_user_id=awaiting_approval_by_user_id, has_been_approved=has_been_approved, trip_id=trip_id, accounting_field_selection_id=accounting_field_selection_id, entity_id=entity_id, from_submitted_at=from_submitted_at, to_submitted_at=to_submitted_at, synced_after=synced_after, updated_after=updated_after, page_size=page_size, user_id=user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_reimbursements: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/reimbursements"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_reimbursements")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_reimbursements", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_reimbursements",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Reimbursement
@mcp.tool()
async def create_mileage_reimbursement(
    distance: str = Field(..., description="The distance traveled, provided as a numeric value or string. Use distance_units to specify whether this is in kilometers or miles."),
    reimbursee_id: str = Field(..., description="The unique identifier (UUID) of the employee requesting reimbursement."),
    trip_date: str = Field(..., description="The date the trip occurred, formatted as a calendar date (ISO 8601 format)."),
    distance_units: Literal["KILOMETERS", "MILES"] | None = Field(None, description="The unit of measurement for the distance: either kilometers or miles. Defaults to miles if not specified."),
    end_location: str | None = Field(None, description="The destination location or address where the trip ended."),
    memo: str | None = Field(None, description="An optional note or description for the reimbursement request."),
    start_location: str | None = Field(None, description="The starting location or address where the trip began."),
    waypoints: list[str] | None = Field(None, description="An optional array of intermediate locations visited during the trip, in order of travel."),
) -> dict[str, Any] | ToolResult:
    """Create a mileage reimbursement request for an employee. Specify the distance traveled, trip date, and reimbursee to generate a reimbursement record."""

    # Construct request model with validation
    try:
        _request = _models.PostMileageReimbursementResourceRequest(
            body=_models.PostMileageReimbursementResourceRequestBody(distance=distance, distance_units=distance_units, end_location=end_location, memo=memo, reimbursee_id=reimbursee_id, start_location=start_location, trip_date=trip_date, waypoints=waypoints)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_mileage_reimbursement: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/reimbursements/mileage"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_mileage_reimbursement")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_mileage_reimbursement", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_mileage_reimbursement",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Reimbursement
@mcp.tool()
async def upload_receipt_for_reimbursement(
    idempotency_key: str = Field(..., description="A unique identifier (UUID) that prevents duplicate receipt uploads. Generate a new UUID for each upload request to ensure idempotency."),
    reimbursee_id: str = Field(..., description="The UUID of the employee or user who will be reimbursed for this receipt."),
    reimbursement_id: str | None = Field(None, description="The UUID of an existing reimbursement to attach this receipt to. If omitted, Ramp will automatically create a new draft reimbursement by extracting receipt data via OCR."),
) -> dict[str, Any] | ToolResult:
    """Upload a receipt image for reimbursement processing. The receipt can be linked to an existing reimbursement or used to automatically create a new draft reimbursement via OCR analysis."""

    # Construct request model with validation
    try:
        _request = _models.PostReimbursementReceiptUploadRequest(
            body=_models.PostReimbursementReceiptUploadRequestBody(idempotency_key=idempotency_key, reimbursee_id=reimbursee_id, reimbursement_id=reimbursement_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for upload_receipt_for_reimbursement: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/reimbursements/submit-receipt"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("upload_receipt_for_reimbursement")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("upload_receipt_for_reimbursement", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="upload_receipt_for_reimbursement",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Reimbursement
@mcp.tool()
async def get_reimbursement(reimbursement_id: str = Field(..., description="The unique identifier of the reimbursement to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific reimbursement by its unique identifier."""

    # Construct request model with validation
    try:
        _request = _models.GetReimbursementResourceRequest(
            path=_models.GetReimbursementResourceRequestPath(reimbursement_id=reimbursement_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_reimbursement: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/reimbursements/{reimbursement_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/reimbursements/{reimbursement_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_reimbursement")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_reimbursement", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_reimbursement",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Spend Program
@mcp.tool()
async def list_spend_programs(page_size: int | None = Field(None, description="Number of spend programs to return per page. Must be between 2 and 100 results; defaults to 20 if not specified.")) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of spend programs. Use the page_size parameter to control how many results are returned per page."""

    # Construct request model with validation
    try:
        _request = _models.GetSpendProgramResourceRequest(
            query=_models.GetSpendProgramResourceRequestQuery(page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_spend_programs: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/spend-programs"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_spend_programs")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_spend_programs", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_spend_programs",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Spend Program
@mcp.tool()
async def create_spend_program(
    description: str = Field(..., description="A brief explanation of the spend program's purpose and use case."),
    display_name: str = Field(..., description="The user-facing name of the spend program that will be displayed in interfaces."),
    icon: Literal["AccountingServicesIcon", "AdvertisingIcon", "CONTRACTORS_AND_PROFESSIONAL_SERVICES", "CUSTOM", "CardIcon", "EducationStipendIcon", "EmployeeRewardsIcon", "GroundTransportationIcon", "LegalFeesIcon", "LodgingIcon", "LunchOrderingIcon", "OnboardingIcon", "PerDiemCardIcon", "SOFTWARE", "SaasSubscriptionIcon", "SoftwareTrialIcon", "SuppliesIcon", "TeamSocialIcon", "TravelExpensesIcon", "VirtualEventIcon", "WellnessIcon", "WorkFromHomeIcon", "advertising", "airlines", "bills", "business", "car_services", "contractor", "education", "entertainment", "event_balloons", "event_virtual", "food", "fuel_and_gas", "general_expense", "general_merchandise", "gift", "government_services", "internet_and_phone", "legal", "lodging", "lodging_room", "newspaper", "office", "physical_card", "procurement_checklist", "procurement_intake", "professional_services", "restaurants", "reward", "saas_software", "shipping", "travel_misc", "wellness"] = Field(..., description="A visual icon identifier for the spend program. Choose from predefined category icons (e.g., 'SaasSubscriptionIcon', 'TravelExpensesIcon', 'WellnessIcon') or use 'CUSTOM' for a custom icon. Icons help users quickly identify the program's purpose."),
    permitted_spend_types: _models.PostSpendProgramResourceBodyPermittedSpendTypes = Field(..., description="The types of spending allowed under this program (e.g., software subscriptions, travel, meals). This defines what purchases users can make with funds from this program."),
    spending_restrictions: _models.PostSpendProgramResourceBodySpendingRestrictions = Field(..., description="Spending limits and restrictions applied to this program, such as daily/monthly caps, merchant category restrictions, or geographic limitations."),
    is_shareable: bool | None = Field(None, description="Whether the spend program can be shared and accessed by multiple users. Defaults to false (single-user only)."),
    issuance_rules: _models.PostSpendProgramResourceBodyIssuanceRules | None = Field(None, description="Optional rules that control how limits are issued from this program. Define which users or user groups (by department, location, or custom attributes) can request limits or receive them automatically. Set `applies_to_all` to true to grant permissions to all employees, or leave unset if no custom issuance logic is needed."),
    issue_physical_card_if_needed: bool | None = Field(None, description="Whether to automatically issue a physical card to users who don't already have one when they join this spend program. Defaults to false."),
) -> dict[str, Any] | ToolResult:
    """Create a new spend program that defines spending policies, restrictions, and issuance rules for a group of users. Spend programs control how funds are allocated, what types of spending are permitted, and whether physical cards should be issued."""

    # Construct request model with validation
    try:
        _request = _models.PostSpendProgramResourceRequest(
            body=_models.PostSpendProgramResourceRequestBody(description=description, display_name=display_name, icon=icon, is_shareable=is_shareable, issuance_rules=issuance_rules, issue_physical_card_if_needed=issue_physical_card_if_needed, permitted_spend_types=permitted_spend_types, spending_restrictions=spending_restrictions)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_spend_program: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/spend-programs"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_spend_program")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_spend_program", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_spend_program",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Spend Program
@mcp.tool()
async def get_spend_program(spend_program_id: str = Field(..., description="The unique identifier of the spend program to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific spend program by its unique identifier."""

    # Construct request model with validation
    try:
        _request = _models.GetSpendProgramSingleResourceRequest(
            path=_models.GetSpendProgramSingleResourceRequestPath(spend_program_id=spend_program_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_spend_program: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/spend-programs/{spend_program_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/spend-programs/{spend_program_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_spend_program")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_spend_program", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_spend_program",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Statement
@mcp.tool()
async def list_statements(page_size: int | None = Field(None, description="Number of statements to return per page. Must be between 2 and 100 results; defaults to 20 if not specified.")) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of statements. Use the page_size parameter to control how many results are returned per page."""

    # Construct request model with validation
    try:
        _request = _models.GetStatementListWithPaginationRequest(
            query=_models.GetStatementListWithPaginationRequestQuery(page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_statements: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/statements"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_statements")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_statements", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_statements",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Statement
@mcp.tool()
async def get_statement(statement_id: str = Field(..., description="The unique identifier of the statement to retrieve. This ID is typically provided when a statement is created or can be obtained from a list of statements.")) -> dict[str, Any] | ToolResult:
    """Retrieve a specific statement by its unique identifier. Use this to fetch detailed information about a previously created or stored statement."""

    # Construct request model with validation
    try:
        _request = _models.GetStatementResourceRequest(
            path=_models.GetStatementResourceRequestPath(statement_id=statement_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_statement: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/statements/{statement_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/statements/{statement_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_statement")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_statement", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_statement",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Transaction
@mcp.tool()
async def list_transactions(
    sk_category_id: Literal[1, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 2, 20, 21, 23, 24, 25, 26, 27, 28, 29, 3, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 4, 40, 41, 42, 43, 44, 5, 6, 7, 8, 9] | None = Field(None, description="Filter transactions by Ramp expense category code. Valid codes range from 1 to 44."),
    department_id: str | None = Field(None, description="Filter transactions by department using its unique identifier."),
    limit_id: str | None = Field(None, description="Filter transactions by spending limit using its unique identifier."),
    location_id: str | None = Field(None, description="Filter transactions by merchant location using its unique identifier."),
    merchant_id: str | None = Field(None, description="Filter transactions by merchant using its unique identifier."),
    card_id: str | None = Field(None, description="Filter transactions by physical card using its unique identifier."),
    spend_program_id: str | None = Field(None, description="Filter transactions by spend program using its unique identifier."),
    statement_id: str | None = Field(None, description="Filter transactions by statement using its unique identifier."),
    approval_status: Literal["AWAITING_EMPLOYEE", "AWAITING_EMPLOYEE_CHANGES_REQUESTED", "AWAITING_EMPLOYEE_MISSING_ITEMS", "AWAITING_EMPLOYEE_REPAYMENT_FAILED", "AWAITING_EMPLOYEE_REPAYMENT_REQUESTED", "AWAITING_REVIEWER", "FULLY_APPROVED"] | None = Field(None, description="Filter transactions by approval status. Valid statuses include awaiting employee action, awaiting reviewer, or fully approved."),
    user_id: str | None = Field(None, description="Filter transactions by cardholder user using their unique identifier."),
    awaiting_approval_by_user_id: str | None = Field(None, description="Filter transactions awaiting approval from a specific user using their unique identifier."),
    sync_status: Literal["NOT_SYNC_READY", "SYNCED", "SYNC_READY"] | None = Field(None, description="Filter transactions by synchronization status: not ready to sync, already synced, or ready to sync. When set, this supersedes other sync-related filters."),
    has_been_approved: bool | None = Field(None, description="Filter to include only transactions that have been approved, or only those that have not been approved. If not specified, returns all transactions regardless of approval status."),
    all_requirements_met_and_approved: bool | None = Field(None, description="Filter to include only transactions that are fully approved with all cardholder requirements met (receipts, memos, tracking categories). If not specified, returns all transactions."),
    has_statement: bool | None = Field(None, description="Filter to include only transactions with a statement, or only those without a statement. If not specified, returns all transactions."),
    synced_after: str | None = Field(None, description="Filter for transactions synced after a specific date and time in ISO 8601 format."),
    min_amount: str | None = Field(None, description="Filter for transactions with an amount greater than or equal to the specified USD dollar amount. Accepts numeric values."),
    max_amount: str | None = Field(None, description="Filter for transactions with an amount less than or equal to the specified USD dollar amount. Accepts numeric values."),
    trip_id: str | None = Field(None, description="Filter transactions by trip using its unique identifier."),
    accounting_field_selection_id: str | None = Field(None, description="Filter transactions by accounting field selection using its unique identifier."),
    entity_id: str | None = Field(None, description="Filter transactions by business entity using its unique identifier."),
    requires_memo: bool | None = Field(None, description="When set to true, returns only transactions that require a memo but do not have one. Cannot be set to false."),
    include_merchant_data: bool | None = Field(None, description="When set to true, includes all purchase data provided by the merchant in the response."),
    order_by_date_desc: bool | None = Field(None, description="When set to true, sorts transactions by user transaction date in descending order (newest first). Note that multiple ordering parameters cannot be used together."),
    order_by_amount_desc: bool | None = Field(None, description="When set to true, sorts transactions by amount in descending order (highest first). Note that multiple ordering parameters cannot be used together."),
    page_size: int | None = Field(None, description="Number of results to return per page. Must be between 2 and 100; defaults to 20 if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of transactions with support for filtering by various attributes (category, department, user, approval status, etc.) and ordering by date or amount. By default, all transactions except declined ones are returned."""

    # Construct request model with validation
    try:
        _request = _models.GetTransactionsCanonicalListWithPaginationRequest(
            query=_models.GetTransactionsCanonicalListWithPaginationRequestQuery(sk_category_id=sk_category_id, department_id=department_id, limit_id=limit_id, location_id=location_id, merchant_id=merchant_id, card_id=card_id, spend_program_id=spend_program_id, statement_id=statement_id, approval_status=approval_status, user_id=user_id, awaiting_approval_by_user_id=awaiting_approval_by_user_id, sync_status=sync_status, has_been_approved=has_been_approved, all_requirements_met_and_approved=all_requirements_met_and_approved, has_statement=has_statement, synced_after=synced_after, min_amount=min_amount, max_amount=max_amount, trip_id=trip_id, accounting_field_selection_id=accounting_field_selection_id, entity_id=entity_id, requires_memo=requires_memo, include_merchant_data=include_merchant_data, order_by_date_desc=order_by_date_desc, order_by_amount_desc=order_by_amount_desc, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_transactions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/transactions"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_transactions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_transactions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_transactions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Transaction
@mcp.tool()
async def get_transaction(
    transaction_id: str = Field(..., description="The unique identifier of the transaction to retrieve."),
    include_merchant_data: bool | None = Field(None, description="When enabled, includes all purchase data provided by the merchant, such as item details, categories, and merchant-specific metadata."),
) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific transaction by its ID. Optionally include merchant-provided purchase data for comprehensive transaction context."""

    # Construct request model with validation
    try:
        _request = _models.GetTransactionCanonicalResourceRequest(
            path=_models.GetTransactionCanonicalResourceRequestPath(transaction_id=transaction_id),
            query=_models.GetTransactionCanonicalResourceRequestQuery(include_merchant_data=include_merchant_data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_transaction: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/transactions/{transaction_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/transactions/{transaction_id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_transaction")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_transaction", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_transaction",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Transfer Payment
@mcp.tool()
async def list_transfers_with_pagination(
    sync_status: Literal["NOT_SYNC_READY", "SYNCED", "SYNC_READY"] | None = Field(None, description="Filter transfers by their synchronization readiness state. Use NOT_SYNC_READY for transfers not yet ready to sync, SYNC_READY for transfers prepared for synchronization, or SYNCED for transfers already synchronized. This parameter takes precedence over has_no_sync_commits if both are provided."),
    status: Literal["ACH_CONFIRMED", "CANCELED", "COMPLETED", "ERROR", "INITIATED", "NOT_ACKED", "NOT_ENOUGH_FUNDS", "PROCESSING_BY_ODFI", "REJECTED_BY_ODFI", "RETURNED_BY_RDFI", "SUBMITTED_TO_FED", "SUBMITTED_TO_RDFI", "UNNECESSARY", "UPLOADED"] | None = Field(None, description="Filter transfers by their current processing status in the ACH workflow. Refer to the Transfers Guide for detailed definitions of each status value, which range from initial states like INITIATED through final states like COMPLETED or REJECTED_BY_ODFI."),
    entity_id: str | None = Field(None, description="Filter transfers to only those associated with a specific business entity, identified by its UUID."),
    statement_id: str | None = Field(None, description="Filter transfers to only those included in a specific statement, identified by its UUID."),
    page_size: int | None = Field(None, description="Set the number of transfer records returned per page. Must be between 2 and 100 results per page. Defaults to 20 if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of transfer payments with optional filtering by sync status, transfer status, business entity, or statement. Use this to view transfer history and monitor payment processing status."""

    # Construct request model with validation
    try:
        _request = _models.GetTransferListWithPaginationRequest(
            query=_models.GetTransferListWithPaginationRequestQuery(sync_status=sync_status, status=status, entity_id=entity_id, statement_id=statement_id, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_transfers_with_pagination: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/transfers"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_transfers_with_pagination")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_transfers_with_pagination", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_transfers_with_pagination",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Transfer Payment
@mcp.tool()
async def get_transfer(transfer_id: str = Field(..., description="The unique identifier of the transfer payment to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve details of a specific transfer payment by its unique identifier. Use this to check the status, amount, and other metadata of a completed or pending transfer."""

    # Construct request model with validation
    try:
        _request = _models.GetTransferResourceRequest(
            path=_models.GetTransferResourceRequestPath(transfer_id=transfer_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_transfer: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/transfers/{transfer_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/transfers/{transfer_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_transfer")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_transfer", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_transfer",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Trips
@mcp.tool()
async def list_trips(
    user_ids: list[str] | None = Field(None, description="Filter results to include only trips assigned to specific users. Provide an array of user IDs."),
    status: Literal["cancelled", "completed", "ongoing", "upcoming"] | None = Field(None, description="Filter trips by their current status: cancelled, completed, ongoing, or upcoming."),
    min_amount: str | None = Field(None, description="Show only trips with a total amount greater than or equal to this value. Accepts numeric values."),
    max_amount: str | None = Field(None, description="Show only trips with a total amount less than or equal to this value. Accepts numeric values."),
    trip_name: str | None = Field(None, description="Filter trips by exact name match."),
    page_size: int | None = Field(None, description="Number of results to return per page. Must be between 2 and 100; defaults to 20 if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all trips for the business with optional filtering by user, status, amount range, and name. Results are paginated with a configurable page size."""

    # Construct request model with validation
    try:
        _request = _models.GetTripListResourceRequest(
            query=_models.GetTripListResourceRequestQuery(user_ids=user_ids, status=status, min_amount=min_amount, max_amount=max_amount, trip_name=trip_name, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_trips: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/trips"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_query = _serialize_query(_http_query, {
        "user_ids": ("form", False),
    })
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_trips")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_trips", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_trips",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Trips
@mcp.tool()
async def get_trip(trip_id: str = Field(..., description="The unique identifier of the trip to retrieve, formatted as a UUID.")) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific trip using its unique identifier."""

    # Construct request model with validation
    try:
        _request = _models.GetTripSingleResourceRequest(
            path=_models.GetTripSingleResourceRequestPath(trip_id=trip_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_trip: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/trips/{trip_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/trips/{trip_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_trip")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_trip", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_trip",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: User
@mcp.tool()
async def list_users(
    employee_id: str | None = Field(None, description="Filter results to users with a specific employee ID."),
    role: Literal["AUDITOR", "BUSINESS_ADMIN", "BUSINESS_BOOKKEEPER", "BUSINESS_OWNER", "BUSINESS_USER", "GUEST_USER", "IT_ADMIN"] | None = Field(None, description="Filter results to users with a specific role: AUDITOR, BUSINESS_ADMIN, BUSINESS_BOOKKEEPER, BUSINESS_OWNER, BUSINESS_USER, GUEST_USER, or IT_ADMIN."),
    status: Literal["USER_ACTIVE", "USER_INACTIVE", "USER_SUSPENDED"] | None = Field(None, description="Filter results by user status: USER_ACTIVE, USER_INACTIVE, or USER_SUSPENDED. If not specified, returns all active and inactive users but excludes suspended users."),
    page_size: int | None = Field(None, description="Number of results per page, between 2 and 100. Defaults to 20 if not specified."),
    entity_id: str | None = Field(None, description="Filter results to users belonging to a specific business entity, specified as a UUID."),
    department_id: str | None = Field(None, description="Filter results to users in a specific department, specified as a UUID."),
    email: str | None = Field(None, description="Filter results to users with a specific email address."),
    location_id: str | None = Field(None, description="Filter results to users at a specific location, specified as a UUID."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of users with optional filtering by employee ID, role, status, entity, department, email, or location. Defaults to returning all active and inactive users, excluding suspended users."""

    # Construct request model with validation
    try:
        _request = _models.GetUserListWithPaginationRequest(
            query=_models.GetUserListWithPaginationRequestQuery(employee_id=employee_id, role=role, status=status, page_size=page_size, entity_id=entity_id, department_id=department_id, email=email, location_id=location_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_users: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/users"
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

# Tags: User
@mcp.tool()
async def send_user_invite(
    email: str = Field(..., description="The employee's email address used for sending the invite and account access."),
    first_name: str = Field(..., description="The employee's first name; limited to 255 characters.", max_length=255),
    idempotency_key: str = Field(..., description="A unique identifier generated by the client (preferably a UUID) to ensure idempotent request handling. The server uses this to recognize and deduplicate retries of the same request."),
    last_name: str = Field(..., description="The employee's last name; limited to 255 characters.", max_length=255),
    role: Literal["AUDITOR", "BUSINESS_ADMIN", "BUSINESS_BOOKKEEPER", "BUSINESS_OWNER", "BUSINESS_USER", "GUEST_USER", "IT_ADMIN"] = Field(..., description="The employee's role within the system. Valid roles are: AUDITOR, BUSINESS_ADMIN, BUSINESS_BOOKKEEPER, BUSINESS_OWNER, BUSINESS_USER, GUEST_USER, or IT_ADMIN. Note that BUSINESS_OWNER cannot be assigned via invite."),
    department_id: str | None = Field(None, description="UUID of the department to which the employee belongs."),
    direct_manager_id: str | None = Field(None, description="UUID of the employee's direct manager."),
    is_manager: bool | None = Field(None, description="Whether the employee has managerial responsibilities and permissions."),
    location_id: str | None = Field(None, description="UUID of the location to which the employee is assigned. Locations are mapped to entities in a many-to-one relationship."),
    scheduled_deactivation_date: str | None = Field(None, description="The date (in ISO 8601 format) when the user account will be automatically deactivated. For guest users, this defaults to 6 months from invite creation unless explicitly set to null. Cannot be set for admins or owners."),
) -> dict[str, Any] | ToolResult:
    """Trigger an asynchronous task to send a user invite via email. The invited user must accept the invite to complete onboarding and gain access to the system."""

    # Construct request model with validation
    try:
        _request = _models.PostUserCreationDeferredTaskRequest(
            body=_models.PostUserCreationDeferredTaskRequestBody(department_id=department_id, direct_manager_id=direct_manager_id, email=email, first_name=first_name, idempotency_key=idempotency_key, is_manager=is_manager, last_name=last_name, location_id=location_id, role=role, scheduled_deactivation_date=scheduled_deactivation_date)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for send_user_invite: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/users/deferred"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("send_user_invite")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("send_user_invite", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="send_user_invite",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: User
@mcp.tool()
async def get_deferred_task_status(task_id: str = Field(..., description="The unique identifier (UUID) of the deferred task whose status you want to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve the current status of a deferred task by its unique identifier. Use this to poll for completion or check the progress of asynchronous operations."""

    # Construct request model with validation
    try:
        _request = _models.GetUserDeferredTaskResourceRequest(
            path=_models.GetUserDeferredTaskResourceRequestPath(task_id=task_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_deferred_task_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/users/deferred/status/{task_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/users/deferred/status/{task_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_deferred_task_status")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_deferred_task_status", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_deferred_task_status",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: User
@mcp.tool()
async def get_user(user_id: str = Field(..., description="The unique identifier of the user to retrieve, formatted as a UUID.")) -> dict[str, Any] | ToolResult:
    """Retrieve a specific user's profile and details by their unique identifier."""

    # Construct request model with validation
    try:
        _request = _models.GetUserResourceRequest(
            path=_models.GetUserResourceRequestPath(user_id=user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/users/{user_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/users/{user_id}"
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

# Tags: User
@mcp.tool()
async def update_user(
    user_id: str = Field(..., description="The unique identifier of the user to update, formatted as a UUID."),
    auto_promote: bool | None = Field(None, description="Automatically promote the user's manager to a manager role if they are not already one."),
    department_id: str | None = Field(None, description="The unique identifier (UUID) of the department the employee belongs to."),
    direct_manager_id: str | None = Field(None, description="The unique identifier (UUID) of the employee's direct manager."),
    first_name: str | None = Field(None, description="The employee's first name. Must be at least 1 character long.", min_length=1),
    is_manager: bool | None = Field(None, description="Whether the employee has manager-level permissions and responsibilities."),
    last_name: str | None = Field(None, description="The employee's last name. Must be at least 1 character long.", min_length=1),
    location_id: str | None = Field(None, description="The unique identifier (UUID) of the physical location where the employee is based."),
    role: Literal["AUDITOR", "BUSINESS_ADMIN", "BUSINESS_BOOKKEEPER", "BUSINESS_OWNER", "BUSINESS_USER", "GUEST_USER", "IT_ADMIN"] | None = Field(None, description="The employee's role within the organization. Valid roles include: AUDITOR, BUSINESS_ADMIN, BUSINESS_BOOKKEEPER, BUSINESS_OWNER, BUSINESS_USER, GUEST_USER, or IT_ADMIN."),
    scheduled_deactivation_date: str | None = Field(None, description="The date (in ISO 8601 format) when the user account will be automatically deactivated. Set to null to remove a scheduled deactivation. Cannot be set for admin or owner roles."),
) -> dict[str, Any] | ToolResult:
    """Update user profile information including name, organizational hierarchy, role, and deactivation schedule. Supports partial updates of employee details."""

    # Construct request model with validation
    try:
        _request = _models.PatchUserResourceRequest(
            path=_models.PatchUserResourceRequestPath(user_id=user_id),
            body=_models.PatchUserResourceRequestBody(auto_promote=auto_promote, department_id=department_id, direct_manager_id=direct_manager_id, first_name=first_name, is_manager=is_manager, last_name=last_name, location_id=location_id, role=role, scheduled_deactivation_date=scheduled_deactivation_date)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/users/{user_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/users/{user_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_user", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_user",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: User
@mcp.tool()
async def deactivate_user(user_id: str = Field(..., description="The unique identifier of the user to deactivate, formatted as a UUID.")) -> dict[str, Any] | ToolResult:
    """Deactivate a user account, preventing them from logging in, making card purchases, or receiving notifications from Ramp."""

    # Construct request model with validation
    try:
        _request = _models.PatchUserDeactivationResourceRequest(
            path=_models.PatchUserDeactivationResourceRequestPath(user_id=user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for deactivate_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/users/{user_id}/deactivate", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/users/{user_id}/deactivate"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("deactivate_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("deactivate_user", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="deactivate_user",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: User
@mcp.tool()
async def reactivate_user(user_id: str = Field(..., description="The unique identifier of the user to reactivate, formatted as a UUID.")) -> dict[str, Any] | ToolResult:
    """Reactivate a deactivated user account, restoring their ability to log in, use their issued cards, and receive Ramp notifications."""

    # Construct request model with validation
    try:
        _request = _models.PatchUserReactivationResourceRequest(
            path=_models.PatchUserReactivationResourceRequestPath(user_id=user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for reactivate_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/users/{user_id}/reactivate", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/users/{user_id}/reactivate"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("reactivate_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("reactivate_user", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="reactivate_user",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Card Vault
@mcp.tool()
async def create_card_vault(
    user_id: str = Field(..., description="UUID of the user who will own and use this card. Required to identify the cardholder."),
    accounting_rules: list[_models.SpendLimitAccountingRulesDataRequestBody] | None = Field(None, description="Array of accounting rules to apply to this card and its spend limit. Rules are applied in the order specified."),
    allowed_overage_percent_override: str | None = Field(None, description="Optional override for the maximum overage percentage allowed on this card's spend limit. Must be a decimal value between 0 and 100 (e.g., 10 for 10%). If not provided, the card inherits the overage setting from its spend program or business default."),
    spend_program_id: str | None = Field(None, description="UUID of the spend program to associate with this card. When provided, the card automatically inherits the spending restrictions and limits from the program, and any spending_restrictions parameter is ignored."),
    spending_restrictions: _models.PostCardVaultCreationBodySpendingRestrictions | None = Field(None, description="Spending restrictions that define where and how this card can be used. Ignored if spend_program_id is provided, as restrictions are inherited from the spend program instead."),
) -> dict[str, Any] | ToolResult:
    """Create a virtual card with optional spend limits and accounting rules. Requires Vault API access and returns sensitive card details for the specified user."""

    # Construct request model with validation
    try:
        _request = _models.PostCardVaultCreationRequest(
            body=_models.PostCardVaultCreationRequestBody(accounting_rules=accounting_rules, allowed_overage_percent_override=allowed_overage_percent_override, spend_program_id=spend_program_id, spending_restrictions=spending_restrictions, user_id=user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_card_vault: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/vault/cards"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_card_vault")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_card_vault", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_card_vault",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Card Vault
@mcp.tool()
async def get_card_vault_details(card_id: str = Field(..., description="The unique identifier of the card whose sensitive details should be retrieved from the vault.")) -> dict[str, Any] | ToolResult:
    """Retrieve sensitive details for a stored card from the vault. Requires Vault API access permissions to execute."""

    # Construct request model with validation
    try:
        _request = _models.GetCardVaultResourceRequest(
            path=_models.GetCardVaultResourceRequestPath(card_id=card_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_card_vault_details: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/vault/cards/{card_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/vault/cards/{card_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_card_vault_details")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_card_vault_details", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_card_vault_details",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Vendor
@mcp.tool()
async def list_vendors(
    external_vendor_id: str | None = Field(None, description="Filter results to vendors matching this customer-defined external vendor identifier, independent of any accounting system remote IDs."),
    merchant_id: str | None = Field(None, description="Filter results to vendors associated with this specific card merchant, identified by UUID."),
    accounting_vendor_remote_ids: list[str] | None = Field(None, description="Filter results to vendors whose accounting system remote IDs match any in this comma-separated list of strings."),
    vendor_tracking_category_option_ids: list[str] | None = Field(None, description="Filter results to vendors whose accounting field selection IDs match any in this comma-separated list of UUIDs."),
    sk_category_ids: list[Literal[1, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 2, 20, 21, 23, 24, 25, 26, 27, 28, 29, 3, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 4, 40, 41, 42, 43, 44, 5, 6, 7, 8, 9]] | None = Field(None, description="Filter results to vendors whose Ramp category codes match any in this comma-separated list of integers."),
    page_size: int | None = Field(None, description="Number of vendors to return per page; must be between 2 and 100. Defaults to 20 if not specified."),
    vendor_owner_id: str | None = Field(None, description="Filter results to vendors owned by this specific user, identified by UUID."),
    include_subsidiary: bool | None = Field(None, description="When enabled, include ERP subsidiary identifiers associated with each vendor in the response, if available. Defaults to false."),
    is_active: bool | None = Field(None, description="Filter results to vendors with this active status (true for active vendors, false for inactive)."),
    name: str | None = Field(None, description="Filter results to vendors whose name matches or contains this value."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of vendors with optional filtering by external ID, merchant, accounting system mappings, categories, and ownership. Use filters to narrow results to specific vendors matching your business criteria."""

    # Construct request model with validation
    try:
        _request = _models.GetVendorListResourceRequest(
            query=_models.GetVendorListResourceRequestQuery(external_vendor_id=external_vendor_id, merchant_id=merchant_id, accounting_vendor_remote_ids=accounting_vendor_remote_ids, vendor_tracking_category_option_ids=vendor_tracking_category_option_ids, sk_category_ids=sk_category_ids, page_size=page_size, vendor_owner_id=vendor_owner_id, include_subsidiary=include_subsidiary, is_active=is_active, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_vendors: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/vendors"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_query = _serialize_query(_http_query, {
        "accounting_vendor_remote_ids": ("form", False),
        "vendor_tracking_category_option_ids": ("form", False),
        "sk_category_ids": ("form", False),
    })
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_vendors")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_vendors", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_vendors",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Vendor
@mcp.tool()
async def create_vendor(
    business_vendor_contacts: _models.PostVendorListResourceBodyBusinessVendorContacts = Field(..., description="Contact information for the vendor, including name, email, phone, and other relevant details. This is required to create the vendor."),
    country: str = Field(..., description="The country where the vendor is located. Required field that determines tax and regulatory context."),
    accounting_vendor_remote_id: str | None = Field(None, description="The accounting system remote ID for the vendor. Provide either this or vendor_tracking_category_option_id, but not both."),
    address: _models.PostVendorListResourceBodyAddress | None = Field(None, description="The vendor's physical address, including street, city, state, postal code, and country details."),
    external_vendor_id: str | None = Field(None, description="A customer-defined external identifier for the vendor, independent of any accounting system IDs. Useful for tracking vendors across multiple systems."),
    name: str | None = Field(None, description="The vendor's business name. Must be at least 1 character long.", min_length=1),
    request_payment_details: bool | None = Field(None, description="Whether to request payment details (ACH bank account, international wire transfer, check mailing address) from the vendor. Requires a valid contact email address."),
    request_tax_details: bool | None = Field(None, description="Whether to request tax information (Tax Identification Number, federal tax classification, tax address) from the vendor. Requires a valid contact email address."),
    vendor_owner_id: str | None = Field(None, description="The UUID of the user who will own and manage this vendor. If not provided, the vendor will be created without an assigned owner."),
    vendor_tracking_category_option_id: str | None = Field(None, description="The Ramp unique identifier of an existing accounting vendor to link with this vendor. Provide either this or accounting_vendor_remote_id, but not both."),
) -> dict[str, Any] | ToolResult:
    """Create a new vendor that is automatically approved and not subject to existing approval policies. Optionally request payment or tax details from the vendor contact."""

    # Construct request model with validation
    try:
        _request = _models.PostVendorListResourceRequest(
            body=_models.PostVendorListResourceRequestBody(accounting_vendor_remote_id=accounting_vendor_remote_id, address=address, business_vendor_contacts=business_vendor_contacts, country=country, external_vendor_id=external_vendor_id, name=name, request_payment_details=request_payment_details, request_tax_details=request_tax_details, vendor_owner_id=vendor_owner_id, vendor_tracking_category_option_id=vendor_tracking_category_option_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_vendor: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/vendors"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_vendor")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_vendor", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_vendor",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Vendor
@mcp.tool()
async def list_vendor_agreements(
    agreement_custom_records: _models.PostVendorAgreementListResourceBodyAgreementCustomRecords | None = Field(None, description="JSON object containing custom record field filters to match against agreement custom records."),
    auto_renews: bool | None = Field(None, description="Filter to include only agreements that automatically renew, or exclude them if false."),
    contract_owner_ids: list[str] | None = Field(None, description="Filter by one or more contract owner IDs to return only agreements owned by specified users."),
    department_ids: list[str] | None = Field(None, description="Filter by one or more department IDs to return only agreements associated with specified departments."),
    end_date_range: _models.PostVendorAgreementListResourceBodyEndDateRange | None = Field(None, description="JSON object specifying a relative date range filter for agreement end dates (e.g., within next 30 days)."),
    exclude_snoozed: bool | None = Field(None, description="When true, exclude agreements that have been snoozed from the results."),
    has_end_date: bool | None = Field(None, description="Filter to include only agreements with a defined end date, or exclude them if false."),
    has_pending_expansion_requests: bool | None = Field(None, description="Filter to include only agreements with pending expansion requests, or exclude them if false."),
    has_reminders: bool | None = Field(None, description="Filter to include only agreements with configured reminders, or exclude them if false."),
    include_archived: bool | None = Field(None, description="When true, include archived agreements in results; defaults to false to show only active agreements."),
    is_active: bool | None = Field(None, description="Filter to include only currently active agreements, or exclude them if false."),
    is_up_for_renewal: bool | None = Field(None, description="Filter to include only agreements that are up for renewal, or exclude them if false."),
    last_date_to_terminate_range: _models.PostVendorAgreementListResourceBodyLastDateToTerminateRange | None = Field(None, description="JSON object specifying a relative date range filter for the last date to terminate an agreement (e.g., within next 60 days)."),
    max_days_remaining: int | None = Field(None, description="Filter to include only agreements with days remaining less than or equal to this value."),
    max_total_value: str | None = Field(None, description="Filter to include only agreements with total contract value less than or equal to this amount. Accepts numeric string or number format."),
    min_days_remaining: int | None = Field(None, description="Filter to include only agreements with days remaining greater than or equal to this value."),
    min_total_value: str | None = Field(None, description="Filter to include only agreements with total contract value greater than or equal to this amount. Accepts numeric string or number format."),
    page_size: int | None = Field(None, description="Number of results per page; must be between 2 and 100, defaults to 20 if not specified."),
    payee_agreement_ids: list[str] | None = Field(None, description="Filter by one or more agreement IDs to return only specified agreements."),
    payee_ids: list[str] | None = Field(None, description="Filter by one or more vendor (payee) IDs to return only agreements with specified vendors."),
    payee_owner_ids: list[str] | None = Field(None, description="Filter by one or more vendor owner IDs to return only agreements owned by specified vendor contacts."),
    renewal_status: list[Literal["CANCELLED", "EXPIRED", "INITIATED", "NOT_STARTED", "REJECTED", "RENEWED"]] | None = Field(None, description="Filter by one or more renewal status values to include only agreements with matching renewal statuses."),
    renewal_status_exclude: list[Literal["CANCELLED", "EXPIRED", "INITIATED", "NOT_STARTED", "REJECTED", "RENEWED"]] | None = Field(None, description="Exclude agreements with any of the specified renewal statuses from results."),
    start_date_range: _models.PostVendorAgreementListResourceBodyStartDateRange | None = Field(None, description="JSON object specifying a relative date range filter for agreement start dates (e.g., within last 90 days)."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of vendor agreements with flexible filtering by dates, financial values, renewal status, ownership, and custom metadata. Supports inclusion of archived agreements and exclusion of snoozed items."""

    # Construct request model with validation
    try:
        _request = _models.PostVendorAgreementListResourceRequest(
            body=_models.PostVendorAgreementListResourceRequestBody(agreement_custom_records=agreement_custom_records, auto_renews=auto_renews, contract_owner_ids=contract_owner_ids, department_ids=department_ids, end_date_range=end_date_range, exclude_snoozed=exclude_snoozed, has_end_date=has_end_date, has_pending_expansion_requests=has_pending_expansion_requests, has_reminders=has_reminders, include_archived=include_archived, is_active=is_active, is_up_for_renewal=is_up_for_renewal, last_date_to_terminate_range=last_date_to_terminate_range, max_days_remaining=max_days_remaining, max_total_value=max_total_value, min_days_remaining=min_days_remaining, min_total_value=min_total_value, page_size=page_size, payee_agreement_ids=payee_agreement_ids, payee_ids=payee_ids, payee_owner_ids=payee_owner_ids, renewal_status=renewal_status, renewal_status_exclude=renewal_status_exclude, start_date_range=start_date_range)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_vendor_agreements: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/vendors/agreements"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_vendor_agreements")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_vendor_agreements", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_vendor_agreements",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Vendor
@mcp.tool()
async def list_vendor_credits(
    from_accounting_date: str | None = Field(None, description="Filter results to include only vendor credits with an accounting date on or after this date (inclusive). Use ISO 8601 date format."),
    to_accounting_date: str | None = Field(None, description="Filter results to include only vendor credits with an accounting date on or before this date (inclusive). Use ISO 8601 date format."),
    include_fully_used: bool | None = Field(None, description="When false (default), excludes vendor credits marked as fully used from results. Set to true to include them."),
    page_size: int | None = Field(None, description="Number of results per page, between 2 and 100. Defaults to 20 if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all vendor credits across all vendors for a business, with optional filtering by accounting date range and credit status."""

    # Construct request model with validation
    try:
        _request = _models.GetAllVendorCreditsListRequest(
            query=_models.GetAllVendorCreditsListRequestQuery(from_accounting_date=from_accounting_date, to_accounting_date=to_accounting_date, include_fully_used=include_fully_used, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_vendor_credits: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/developer/v1/vendors/credits"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_vendor_credits")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_vendor_credits", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_vendor_credits",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Vendor
@mcp.tool()
async def get_vendor_credit(vendor_credit_id: str = Field(..., description="The unique identifier (UUID) of the vendor credit to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific vendor credit by its unique identifier."""

    # Construct request model with validation
    try:
        _request = _models.GetVendorCreditDetailRequest(
            path=_models.GetVendorCreditDetailRequestPath(vendor_credit_id=vendor_credit_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_vendor_credit: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/vendors/credits/{vendor_credit_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/vendors/credits/{vendor_credit_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_vendor_credit")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_vendor_credit", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_vendor_credit",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Vendor
@mcp.tool()
async def get_vendor(vendor_id: str = Field(..., description="The unique identifier of the vendor, formatted as a UUID.")) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific vendor by its unique identifier."""

    # Construct request model with validation
    try:
        _request = _models.GetVendorResourceRequest(
            path=_models.GetVendorResourceRequestPath(vendor_id=vendor_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_vendor: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/vendors/{vendor_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/vendors/{vendor_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_vendor")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_vendor", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_vendor",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Vendor
@mcp.tool()
async def update_vendor(
    vendor_id: str = Field(..., description="The unique identifier of the vendor to update, formatted as a UUID."),
    accounting_vendor_remote_id: str | None = Field(None, description="The remote identifier for this vendor in your accounting system. Provide either this or vendor_tracking_category_option_id, but not both."),
    address: _models.PatchVendorResourceBodyAddress | None = Field(None, description="The vendor's physical address details."),
    country: str | None = Field(None, description="The country where the vendor is located."),
    description: str | None = Field(None, description="A descriptive name or label for the vendor."),
    external_vendor_id: str | None = Field(None, description="A custom external identifier for the vendor that you define, independent of any accounting system identifiers."),
    is_active: bool | None = Field(None, description="Set to true to mark the vendor as active, or false to deactivate it."),
    vendor_tracking_category_option_id: str | None = Field(None, description="The unique identifier of the vendor tracking category option, formatted as a UUID. Provide either this or accounting_vendor_remote_id, but not both."),
) -> dict[str, Any] | ToolResult:
    """Update vendor details including contact information, identifiers, and active status. Use this to modify an existing vendor's attributes in the system."""

    # Construct request model with validation
    try:
        _request = _models.PatchVendorResourceRequest(
            path=_models.PatchVendorResourceRequestPath(vendor_id=vendor_id),
            body=_models.PatchVendorResourceRequestBody(accounting_vendor_remote_id=accounting_vendor_remote_id, address=address, country=country, description=description, external_vendor_id=external_vendor_id, is_active=is_active, vendor_tracking_category_option_id=vendor_tracking_category_option_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_vendor: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/vendors/{vendor_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/vendors/{vendor_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_vendor")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_vendor", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_vendor",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Vendor
@mcp.tool()
async def delete_vendor(vendor_id: str = Field(..., description="The unique identifier of the vendor to delete, formatted as a UUID.")) -> dict[str, Any] | ToolResult:
    """Delete a vendor from the system. The vendor must have no associated transactions, bills, contracts, or spend requests to be successfully deleted."""

    # Construct request model with validation
    try:
        _request = _models.DeleteVendorResourceRequest(
            path=_models.DeleteVendorResourceRequestPath(vendor_id=vendor_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_vendor: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/vendors/{vendor_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/vendors/{vendor_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_vendor")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_vendor", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_vendor",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Vendor
@mcp.tool()
async def list_vendor_bank_accounts(
    vendor_id: str = Field(..., description="The unique identifier (UUID) of the vendor whose bank accounts you want to retrieve."),
    page_size: int | None = Field(None, description="The number of bank accounts to return per page. Must be between 2 and 100 results; defaults to 20 if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of bank accounts associated with a specific vendor. Use pagination parameters to control result set size."""

    # Construct request model with validation
    try:
        _request = _models.GetVendorBankAccountListResourceRequest(
            path=_models.GetVendorBankAccountListResourceRequestPath(vendor_id=vendor_id),
            query=_models.GetVendorBankAccountListResourceRequestQuery(page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_vendor_bank_accounts: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/vendors/{vendor_id}/accounts", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/vendors/{vendor_id}/accounts"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_vendor_bank_accounts")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_vendor_bank_accounts", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_vendor_bank_accounts",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Vendor
@mcp.tool()
async def get_vendor_bank_account(
    bank_account_id: str = Field(..., description="The unique identifier (UUID) of the vendor whose bank account you want to retrieve."),
    vendor_id: str = Field(..., description="The unique identifier (UUID) of the specific bank account to fetch."),
) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific bank account associated with a vendor. Use this to access bank account details for payment processing or vendor management purposes."""

    # Construct request model with validation
    try:
        _request = _models.GetVendorBankAccountResourceRequest(
            path=_models.GetVendorBankAccountResourceRequestPath(bank_account_id=bank_account_id, vendor_id=vendor_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_vendor_bank_account: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/vendors/{vendor_id}/accounts/{bank_account_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/vendors/{vendor_id}/accounts/{bank_account_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_vendor_bank_account")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_vendor_bank_account", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_vendor_bank_account",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Vendor
@mcp.tool()
async def archive_vendor_bank_account(
    bank_account_id: str = Field(..., description="The unique identifier (UUID) of the bank account to archive."),
    vendor_id: str = Field(..., description="The unique identifier (UUID) of the vendor that owns the bank account."),
    replacement_bank_account_id: str | None = Field(None, description="The unique identifier (UUID) of the replacement bank account to transfer any associated bills, drafts, or recurring templates to. Required if the account being archived has existing associations."),
) -> dict[str, Any] | ToolResult:
    """Archive a vendor's bank account. If the account has associated bills, drafts, or recurring templates, you must specify a replacement bank account to transfer them to."""

    # Construct request model with validation
    try:
        _request = _models.PostVendorBankAccountArchiveResourceRequest(
            path=_models.PostVendorBankAccountArchiveResourceRequestPath(bank_account_id=bank_account_id, vendor_id=vendor_id),
            body=_models.PostVendorBankAccountArchiveResourceRequestBody(replacement_bank_account_id=replacement_bank_account_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for archive_vendor_bank_account: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/vendors/{vendor_id}/accounts/{bank_account_id}/archive", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/vendors/{vendor_id}/accounts/{bank_account_id}/archive"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("archive_vendor_bank_account")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("archive_vendor_bank_account", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="archive_vendor_bank_account",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Vendor
@mcp.tool()
async def list_vendor_contacts(
    vendor_id: str = Field(..., description="The unique identifier (UUID) of the vendor whose contacts you want to retrieve."),
    page_size: int | None = Field(None, description="The number of contacts to return per page, between 2 and 100. Defaults to 20 if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of contacts associated with a specific vendor. Use pagination to control the number of results returned per page."""

    # Construct request model with validation
    try:
        _request = _models.GetVendorContactListResourceRequest(
            path=_models.GetVendorContactListResourceRequestPath(vendor_id=vendor_id),
            query=_models.GetVendorContactListResourceRequestQuery(page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_vendor_contacts: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/vendors/{vendor_id}/contacts", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/vendors/{vendor_id}/contacts"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_vendor_contacts")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_vendor_contacts", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_vendor_contacts",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Vendor
@mcp.tool()
async def get_vendor_contact(
    vendor_contact_id: str = Field(..., description="The unique identifier of the vendor contact to retrieve, formatted as a UUID."),
    vendor_id: str = Field(..., description="The unique identifier of the vendor that owns the contact, formatted as a UUID."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a specific contact person associated with a vendor. Requires both the vendor ID and the contact ID to identify the exact contact record."""

    # Construct request model with validation
    try:
        _request = _models.GetVendorContactResourceRequest(
            path=_models.GetVendorContactResourceRequestPath(vendor_contact_id=vendor_contact_id, vendor_id=vendor_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_vendor_contact: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/vendors/{vendor_id}/contacts/{vendor_contact_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/vendors/{vendor_id}/contacts/{vendor_contact_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_vendor_contact")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_vendor_contact", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_vendor_contact",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Vendor
@mcp.tool()
async def list_vendor_credits_by_vendor(
    vendor_id: str = Field(..., description="The unique identifier (UUID) of the vendor whose credits should be retrieved."),
    from_accounting_date: str | None = Field(None, description="Filter results to include only vendor credits with an accounting date on or after this date (ISO 8601 format). Optional."),
    to_accounting_date: str | None = Field(None, description="Filter results to include only vendor credits with an accounting date on or before this date (ISO 8601 format). Optional."),
    include_fully_used: bool | None = Field(None, description="When true, includes vendor credits marked as fully used in the results. Defaults to false, excluding fully used credits."),
    page_size: int | None = Field(None, description="Number of results per page, between 2 and 100. Defaults to 20 if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of vendor credits for a specific vendor, with optional filtering by accounting date range and inclusion of fully used credits."""

    # Construct request model with validation
    try:
        _request = _models.GetVendorCreditsListRequest(
            path=_models.GetVendorCreditsListRequestPath(vendor_id=vendor_id),
            query=_models.GetVendorCreditsListRequestQuery(from_accounting_date=from_accounting_date, to_accounting_date=to_accounting_date, include_fully_used=include_fully_used, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_vendor_credits_by_vendor: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/vendors/{vendor_id}/credits", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/vendors/{vendor_id}/credits"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_vendor_credits_by_vendor")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_vendor_credits_by_vendor", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_vendor_credits_by_vendor",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Vendor
@mcp.tool()
async def add_vendor_bank_account(
    vendor_id: str = Field(..., description="The unique identifier of the vendor to add the bank account for. Must be a valid UUID."),
    account_nickname: str | None = Field(None, description="An optional human-readable label for this bank account to help identify it among multiple payment methods."),
    ach_details: _models.PostVendorBankAccountUpdateResourceBodyAchDetails | None = Field(None, description="ACH payment details for US bank transfers, including routing and account numbers. Provide this for ACH transfers or wire_details for wire transfers."),
    is_default: bool | None = Field(None, description="Set to true to make this the vendor's default payment method. Defaults to false if not specified."),
    wire_details: _models.PostVendorBankAccountUpdateResourceBodyWireDetails | None = Field(None, description="Wire transfer payment details for US wire transfers, including routing and account numbers. Provide this for wire transfers or ach_details for ACH transfers."),
) -> dict[str, Any] | ToolResult:
    """Add or update a bank account for a vendor's payment processing. The account addition may require approval based on your business's configured approval policies."""

    # Construct request model with validation
    try:
        _request = _models.PostVendorBankAccountUpdateResourceRequest(
            path=_models.PostVendorBankAccountUpdateResourceRequestPath(vendor_id=vendor_id),
            body=_models.PostVendorBankAccountUpdateResourceRequestBody(account_nickname=account_nickname, ach_details=ach_details, is_default=is_default, wire_details=wire_details)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_vendor_bank_account: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/vendors/{vendor_id}/update-bank-accounts", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/vendors/{vendor_id}/update-bank-accounts"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_vendor_bank_account")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_vendor_bank_account", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_vendor_bank_account",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Webhooks
@mcp.tool()
async def get_webhook_subscription(webhook_id: str = Field(..., description="The unique identifier (UUID) of the webhook subscription to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve a specific outbound webhook subscription by its unique identifier. Use this to inspect the configuration and status of a webhook."""

    # Construct request model with validation
    try:
        _request = _models.GetOutboundWebhookSubscriptionDetailResourceRequest(
            path=_models.GetOutboundWebhookSubscriptionDetailResourceRequestPath(webhook_id=webhook_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_webhook_subscription: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/webhooks/{webhook_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/webhooks/{webhook_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_webhook_subscription")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_webhook_subscription", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_webhook_subscription",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Webhooks
@mcp.tool()
async def delete_webhook(webhook_id: str = Field(..., description="The unique identifier of the webhook subscription to delete, formatted as a UUID.")) -> dict[str, Any] | ToolResult:
    """Delete a webhook subscription by its unique identifier. This permanently removes the webhook and stops it from receiving events."""

    # Construct request model with validation
    try:
        _request = _models.DeleteOutboundWebhookSubscriptionDetailResourceRequest(
            path=_models.DeleteOutboundWebhookSubscriptionDetailResourceRequestPath(webhook_id=webhook_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_webhook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/developer/v1/webhooks/{webhook_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/developer/v1/webhooks/{webhook_id}"
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
        print("  python ramp_developer_api_server.py", file=sys.stderr)
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

    parser = argparse.ArgumentParser(description="Ramp Developer API MCP Server")

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
    logger.info("Starting Ramp Developer API MCP Server")
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

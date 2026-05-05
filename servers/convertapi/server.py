#!/usr/bin/env python3
"""
ConvertAPI MCP Server

API Info:
- API License: Apache 2.0 (http://www.apache.org/licenses/LICENSE-2.0.html)
- Terms of Service: https://www.convertapi.com/terms

Generated: 2026-05-05 14:45:22 UTC
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

BASE_URL = os.getenv("BASE_URL", "https://v2.convertapi.com")
SERVER_NAME = "ConvertAPI"
SERVER_VERSION = "1.0.3"

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

def build_transparent_color(red: int | None = None, green: int | None = None, blue: int | None = None, alpha: int | None = None) -> str | None:
    """Helper function for parameter transformation"""
    if red is None and green is None and blue is None and alpha is None:
        return None

    try:
        r = red if red is not None else 0
        g = green if green is not None else 0
        b = blue if blue is not None else 0
        a = alpha if alpha is not None else 255
        
        if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255 and 0 <= a <= 255):
            raise ValueError(f"Color channel values must be in range 0-255, got R={r}, G={g}, B={b}, A={a}")
        
        return f"{r},{g},{b},{a}"
    except (TypeError, ValueError) as e:
        raise ValueError(f"Failed to build transparent color: {e}") from e

def parse_margin(value: str | None = None) -> dict | None:
    """Helper function for parameter transformation"""
    if value is None:
        return None
    try:
        parts = value.split(',')
        if len(parts) != 2:
            raise ValueError('Margin must contain exactly 2 values')
        return {'MarginHorizontal': int(parts[0].strip()), 'MarginVertical': int(parts[1].strip())}
    except ValueError as e:
        raise ValueError(f'Invalid margin format: {value}') from e

def parse_margins(value: str | None = None) -> dict | None:
    """Helper function for parameter transformation"""
    if value is None:
        return None
    parts = value.strip().split()
    if len(parts) == 1:
        m = int(parts[0])
        return {'MarginTop': m, 'MarginRight': m, 'MarginBottom': m, 'MarginLeft': m}
    elif len(parts) == 2:
        v, h = int(parts[0]), int(parts[1])
        return {'MarginTop': v, 'MarginRight': h, 'MarginBottom': v, 'MarginLeft': h}
    elif len(parts) == 4:
        return {'MarginTop': int(parts[0]), 'MarginRight': int(parts[1]), 'MarginBottom': int(parts[2]), 'MarginLeft': int(parts[3])}
    else:
        raise ValueError('Margins must be 1, 2, or 4 space-separated integers') from None

def parse_offset(value: str | None = None) -> dict | None:
    """Helper function for parameter transformation"""
    if value is None:
        return None
    try:
        parts = value.split(',')
        if len(parts) != 2:
            raise ValueError('Offset must contain exactly two comma-separated values')
        return {'OffsetX': float(parts[0].strip()), 'OffsetY': float(parts[1].strip())}
    except ValueError as e:
        raise ValueError(f'Invalid offset format: {value}. Expected format: x,y') from e

def build_redaction_data(redaction_text_values: list[str] | None = None, redaction_regex_patterns: list[str] | None = None, redaction_detect_descriptions: list[str] | None = None) -> list[dict] | None:
    """Helper function for parameter transformation"""
    if not any([redaction_text_values, redaction_regex_patterns, redaction_detect_descriptions]):
        return None

    try:
        redaction_array = []
        
        if redaction_text_values:
            for text in redaction_text_values:
                redaction_array.append({"Text": text})
        
        if redaction_regex_patterns:
            for pattern in redaction_regex_patterns:
                escaped_pattern = json.dumps(pattern)[1:-1]
                redaction_array.append({"Regex": escaped_pattern})
        
        if redaction_detect_descriptions:
            for description in redaction_detect_descriptions:
                redaction_array.append({"Detect": description})
        
        return redaction_array if redaction_array else None
    except Exception as e:
        raise ValueError(f"Failed to build redaction data: {e}") from e

def build_footer_html(footer_content: str | None = None, footer_css: str | None = None, footer_include_page_number: bool | None = None, footer_include_total_pages: bool | None = None, footer_include_title: bool | None = None, footer_include_date: bool | None = None) -> str | None:
    """Helper function for parameter transformation"""
    if footer_content is None:
        return None
    try:
        html_parts = []
        if footer_css:
            html_parts.append(f"<style>{footer_css}</style>")
        html_parts.append(footer_content)
        if footer_include_page_number:
            html_parts.append("<span class='pageNumber'></span>")
        if footer_include_total_pages:
            html_parts.append("<span class='totalPages'></span>")
        if footer_include_title:
            html_parts.append("<span class='title'></span>")
        if footer_include_date:
            html_parts.append("<span class='date'></span>")
        return "".join(html_parts)
    except Exception as e:
        raise ValueError(f"Failed to build footer HTML: {e}") from e

def build_header_html(header_content: str | None = None, header_css: str | None = None, header_include_page_number: bool | None = None, header_include_total_pages: bool | None = None, header_include_title: bool | None = None, header_include_date: bool | None = None) -> str | None:
    """Helper function for parameter transformation"""
    if header_content is None:
        return None
    try:
        html_parts = []
        if header_css:
            html_parts.append(f"<style>{header_css}</style>")
        html_parts.append(header_content)
        if header_include_page_number:
            html_parts.append("<span class='pageNumber'></span>")
        if header_include_total_pages:
            html_parts.append("<span class='totalPages'></span>")
        if header_include_title:
            html_parts.append("<span class='title'></span>")
        if header_include_date:
            html_parts.append("<span class='date'></span>")
        return "".join(html_parts)
    except Exception as e:
        raise ValueError(f"Failed to build header HTML: {e}") from e


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
    'secret',
    'token',
]

# Initialize authentication handlers at server startup
_auth_handlers: dict[str, Any] = {}
try:
    _auth_handlers["secret"] = _auth.BearerTokenAuth(env_var="SECRET_BEARER_TOKEN", token_format="Bearer")
    logging.info("Authentication configured: secret")
except ValueError as e:
    # Extract credential names from error message (first sentence before "Leave empty")
    error_msg = str(e).split("Leave empty")[0].strip()
    logging.warning(f"Credentials for secret not configured: {error_msg}")
    _auth_handlers["secret"] = None
try:
    _auth_handlers["token"] = _auth.BearerTokenAuth(env_var="TOKEN_BEARER_TOKEN", token_format="Bearer")
    logging.info("Authentication configured: token")
except ValueError as e:
    # Extract credential names from error message (first sentence before "Leave empty")
    error_msg = str(e).split("Leave empty")[0].strip()
    logging.warning(f"Credentials for token not configured: {error_msg}")
    _auth_handlers["token"] = None

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

mcp = FastMCP("ConvertAPI", middleware=[_JsonCoercionMiddleware()])

# Tags: File Server
@mcp.tool()
async def upload_file(
    filename: str | None = Field(None, description="The name of the file being uploaded. Required unless the content-disposition header is provided."),
    url: str | None = Field(None, description="A remote URL pointing to the file to upload. If provided, the file will be downloaded and stored directly from this location instead of uploading file contents."),
    file_: str | None = Field(None, alias="file", description="The binary file content to upload. Provide the raw file data directly."),
) -> dict[str, Any] | ToolResult:
    """Upload a file to ConvertAPI servers for temporary storage and reuse across multiple conversion operations. The file is securely stored for up to 3 hours and assigned a unique File ID for referencing in subsequent conversion requests."""

    # Construct request model with validation
    try:
        _request = _models.PostUploadRequest(
            query=_models.PostUploadRequestQuery(filename=filename, url=url),
            body=_models.PostUploadRequestBody(file_=file_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for upload_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/upload"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("upload_file")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("upload_file", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="upload_file",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["file"],
        headers=_http_headers,
    )

    return _response_data

# Tags: File Server
@mcp.tool()
async def download_file(
    file_id: str = Field(..., alias="fileId", description="The unique identifier of the file to download. Must be exactly 32 characters long.", min_length=32, max_length=32),
    download: Literal["attachment", "inline"] | None = Field(None, description="Specifies how the file should be delivered: as an attachment for download or inline for viewing in a web browser."),
) -> dict[str, Any] | ToolResult:
    """Download or view a file by its ID. Specify whether to download as an attachment or view inline in a web browser."""

    # Construct request model with validation
    try:
        _request = _models.GetDRequest(
            path=_models.GetDRequestPath(file_id=file_id),
            query=_models.GetDRequestQuery(download=download)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for download_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/d/{fileId}", _request.path.model_dump(by_alias=True)) if _request.path else "/d/{fileId}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("download_file")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("download_file", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="download_file",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: File Server
@mcp.tool()
async def delete_file(file_id: str = Field(..., alias="fileId", description="The unique identifier of the file to delete. Must be exactly 32 characters.", min_length=32, max_length=32)) -> dict[str, Any] | ToolResult:
    """Permanently delete a file from storage. Files are automatically deleted after 3 hours if not manually removed."""

    # Construct request model with validation
    try:
        _request = _models.DeleteDRequest(
            path=_models.DeleteDRequestPath(file_id=file_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/d/{fileId}", _request.path.model_dump(by_alias=True)) if _request.path else "/d/{fileId}"
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

# Tags: File Server
@mcp.tool()
async def get_file_metadata(file_id: str = Field(..., alias="fileId", description="The unique identifier of the file. This is a 32-character alphanumeric string that uniquely identifies the file in the system.", min_length=32, max_length=32)) -> dict[str, Any] | ToolResult:
    """Retrieve metadata and information about a file without downloading its contents. Use this to check file existence, properties, and availability."""

    # Construct request model with validation
    try:
        _request = _models.HeadDRequest(
            path=_models.HeadDRequestPath(file_id=file_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_file_metadata: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/d/{fileId}", _request.path.model_dump(by_alias=True)) if _request.path else "/d/{fileId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_file_metadata")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_file_metadata", "HEAD", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_file_metadata",
        method="HEAD",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: User
@mcp.tool()
async def get_account() -> dict[str, Any] | ToolResult:
    """Retrieve account information including balance status and other account details. Requires authentication with a secret key."""

    # Extract parameters for API call
    _http_path = "/user"
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

# Tags: User
@mcp.tool()
async def get_usage_statistics(
    start_date: str = Field(..., alias="startDate", description="The start date for the statistics query period in YYYY-MM-DD format (inclusive)."),
    end_date: str = Field(..., alias="endDate", description="The end date for the statistics query period in YYYY-MM-DD format (inclusive)."),
) -> dict[str, Any] | ToolResult:
    """Retrieve usage statistics for a specified date range. Returns aggregated data about your account activity and consumption metrics within the provided time period."""

    # Construct request model with validation
    try:
        _request = _models.GetUserStatisticRequest(
            query=_models.GetUserStatisticRequestQuery(start_date=start_date, end_date=end_date)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_usage_statistics: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/user/statistic"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_usage_statistics")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_usage_statistics", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_usage_statistics",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_image_to_jpg(
    file_: str | None = Field(None, alias="File", description="The image file to convert, provided as either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Custom name for the output JPG file. The system automatically sanitizes the filename, appends the .jpg extension, and adds numeric indexing (e.g., image_0.jpg, image_1.jpg) if multiple files are generated."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the target output dimensions."),
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(None, alias="ColorSpace", description="Specify the color space for the output JPG image."),
) -> dict[str, Any] | ToolResult:
    """Convert an AI image file to JPG format with optional scaling and color space adjustments. Supports URL or file content input with customizable output naming and image properties."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertAiToJpgRequest(
            body=_models.PostConvertAiToJpgRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, color_space=color_space)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_image_to_jpg: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/ai/to/jpg"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_image_to_jpg")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_image_to_jpg", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_image_to_jpg",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_ai_to_png(
    file_: str | None = Field(None, alias="File", description="The file to convert, provided either as a URL or raw file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output PNG file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.png, output_1.png) for multiple files."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Whether to maintain the original aspect ratio when scaling the output image."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Whether to apply scaling only when the input image dimensions exceed the target output dimensions."),
    red: int | None = Field(None, description="Red channel value (0-255)"),
    green: int | None = Field(None, description="Green channel value (0-255)"),
    blue: int | None = Field(None, description="Blue channel value (0-255)"),
    alpha: int | None = Field(None, description="Alpha channel value (0-255), where 0 is fully transparent and 255 is fully opaque. Optional; if not provided, defaults to 255 (fully opaque)."),
) -> dict[str, Any] | ToolResult:
    """Converts Adobe Illustrator (AI) files to PNG format with optional scaling and proportional constraints. Supports both file uploads and URL-based file sources."""

    # Call helper functions
    transparent_color = build_transparent_color(red, green, blue, alpha)

    # Construct request model with validation
    try:
        _request = _models.PostConvertAiToPngRequest(
            body=_models.PostConvertAiToPngRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, transparent_color=transparent_color)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_ai_to_png: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/ai/to/png"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_ai_to_png")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_ai_to_png", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_ai_to_png",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_image_to_pnm(
    file_: str | None = Field(None, alias="File", description="The image file to convert, provided as a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.pnm, output_1.pnm) for multiple files."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Apply scaling only when the input image dimensions exceed the target output dimensions."),
    red: int | None = Field(None, description="Red channel value (0-255)"),
    green: int | None = Field(None, description="Green channel value (0-255)"),
    blue: int | None = Field(None, description="Blue channel value (0-255)"),
    alpha: int | None = Field(None, description="Alpha channel value (0-255), where 0 is fully transparent and 255 is fully opaque. Optional; if not provided, defaults to 255 (fully opaque)."),
) -> dict[str, Any] | ToolResult:
    """Convert an Adobe Illustrator (AI) image file to Portable Anymap (PNM) format. Supports URL or file content input with optional scaling and proportional constraint controls."""

    # Call helper functions
    transparent_color = build_transparent_color(red, green, blue, alpha)

    # Construct request model with validation
    try:
        _request = _models.PostConvertAiToPnmRequest(
            body=_models.PostConvertAiToPnmRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, transparent_color=transparent_color)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_image_to_pnm: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/ai/to/pnm"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_image_to_pnm")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_image_to_pnm", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_image_to_pnm",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_ai_to_svg(
    file_: str | None = Field(None, alias="File", description="The file to convert, provided as either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output SVG file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.svg, output_1.svg) for multiple files."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Apply scaling only when the input image dimensions exceed the output dimensions."),
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(None, alias="ColorSpace", description="Define the color space for the output image."),
) -> dict[str, Any] | ToolResult:
    """Convert Adobe Illustrator (AI) files to Scalable Vector Graphics (SVG) format with optional scaling and color space adjustments. Supports both file uploads and URL-based inputs."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertAiToSvgRequest(
            body=_models.PostConvertAiToSvgRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, color_space=color_space)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_ai_to_svg: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/ai/to/svg"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_ai_to_svg")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_ai_to_svg", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_ai_to_svg",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_ai_to_tiff(
    file_: str | None = Field(None, alias="File", description="The file to convert, provided as either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output TIFF file(s). The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.tiff, output_1.tiff) for multi-page conversions."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the target output dimensions."),
    multi_page: bool | None = Field(None, alias="MultiPage", description="Generate a single multi-page TIFF file instead of separate single-page files."),
) -> dict[str, Any] | ToolResult:
    """Convert Adobe Illustrator (AI) files to TIFF format with optional scaling and multi-page support. Supports both URL-based and direct file uploads."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertAiToTiffRequest(
            body=_models.PostConvertAiToTiffRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, multi_page=multi_page)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_ai_to_tiff: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/ai/to/tiff"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_ai_to_tiff")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_ai_to_tiff", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_ai_to_tiff",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_image_to_webp(
    file_: str | None = Field(None, alias="File", description="The image file to convert. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output file. The API automatically sanitizes the filename, appends the correct .webp extension, and adds indexing (e.g., image_0.webp, image_1.webp) for multiple outputs."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the output dimensions."),
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(None, alias="ColorSpace", description="Set the color space for the output image."),
) -> dict[str, Any] | ToolResult:
    """Convert an AI image file to WebP format with optional scaling and color space adjustments. Supports URL or file content input with configurable output naming and image properties."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertAiToWebpRequest(
            body=_models.PostConvertAiToWebpRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, color_space=color_space)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_image_to_webp: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/ai/to/webp"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_image_to_webp")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_image_to_webp", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_image_to_webp",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_image_bmp_to_jpg(
    file_: str | None = Field(None, alias="File", description="The image file to convert. Can be provided as a URL or raw file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing for multiple output files to ensure unique identification."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the output dimensions."),
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(None, alias="ColorSpace", description="Define the color space for the output image."),
) -> dict[str, Any] | ToolResult:
    """Convert a BMP image file to JPG format with optional scaling and color space adjustments. Supports both URL and direct file content input."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertBmpToJpgRequest(
            body=_models.PostConvertBmpToJpgRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, color_space=color_space)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_image_bmp_to_jpg: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/bmp/to/jpg"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_image_bmp_to_jpg")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_image_bmp_to_jpg", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_image_bmp_to_jpg",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_image_to_pdf(
    file_: str | None = Field(None, alias="File", description="The image file to convert. Accepts either a URL reference or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.pdf, filename_1.pdf) for multiple output files."),
    rotate: int | None = Field(None, alias="Rotate", description="Rotation angle in degrees to apply to the image. Leave empty to use automatic rotation based on EXIF data in TIFF and JPEG images.", ge=-360, le=360),
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(None, alias="ColorSpace", description="Color space for the output PDF. Defines how colors are represented in the converted document."),
    color_profile: Literal["default", "isocoatedv2"] | None = Field(None, alias="ColorProfile", description="Color profile to apply to the output PDF. Some profiles override the ColorSpace setting."),
    pdfa: bool | None = Field(None, alias="Pdfa", description="Enable PDF/A-1b compliance for long-term archival and preservation of the output document."),
    margin: str | None = Field(None, alias="Margin", description="Page margins in millimeters as 'horizontal,vertical' (e.g., '10,15')"),
) -> dict[str, Any] | ToolResult:
    """Convert BMP images to PDF format with support for rotation, color space configuration, and PDF/A compliance. Accepts file input as URL or binary content and generates a named output PDF file."""

    # Call helper functions
    margin_parsed = parse_margin(margin)

    # Construct request model with validation
    try:
        _request = _models.PostConvertBmpToPdfRequest(
            body=_models.PostConvertBmpToPdfRequestBody(file_=file_, file_name=file_name, rotate=rotate, color_space=color_space, color_profile=color_profile, pdfa=pdfa, margin_horizontal=margin_parsed.get('MarginHorizontal') if margin_parsed else None, margin_vertical=margin_parsed.get('MarginVertical') if margin_parsed else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_image_to_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/bmp/to/pdf"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_image_to_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_image_to_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_image_to_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_image_bmp_to_png(
    file_: str | None = Field(None, alias="File", description="The image file to convert. Accepts either a URL pointing to a BMP file or the raw binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output PNG file. The system automatically sanitizes the filename, appends the correct .png extension, and adds numeric indexing (e.g., image_0.png, image_1.png) if multiple files are generated."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image to the target dimensions."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Apply scaling only when the input image dimensions exceed the target output dimensions, leaving smaller images unchanged."),
    red: int | None = Field(None, description="Red channel value (0-255)"),
    green: int | None = Field(None, description="Green channel value (0-255)"),
    blue: int | None = Field(None, description="Blue channel value (0-255)"),
    alpha: int | None = Field(None, description="Alpha channel value (0-255), where 0 is fully transparent and 255 is fully opaque. Optional; if not provided, defaults to 255 (fully opaque)."),
) -> dict[str, Any] | ToolResult:
    """Convert a BMP image file to PNG format with optional scaling and proportional constraint controls. Supports both URL-based and direct file content input."""

    # Call helper functions
    transparent_color = build_transparent_color(red, green, blue, alpha)

    # Construct request model with validation
    try:
        _request = _models.PostConvertBmpToPngRequest(
            body=_models.PostConvertBmpToPngRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, transparent_color=transparent_color)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_image_bmp_to_png: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/bmp/to/png"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_image_bmp_to_png")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_image_bmp_to_png", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_image_bmp_to_png",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_image_bmp_to_pnm(
    file_: str | None = Field(None, alias="File", description="The image file to convert, provided either as a URL or raw file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output file. The system automatically sanitizes the filename, appends the correct extension for PNM format, and adds indexing (e.g., output_0.pnm, output_1.pnm) when multiple files are generated."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image to the target dimensions."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Apply scaling only when the input image dimensions exceed the target output dimensions, leaving smaller images unchanged."),
    red: int | None = Field(None, description="Red channel value (0-255)"),
    green: int | None = Field(None, description="Green channel value (0-255)"),
    blue: int | None = Field(None, description="Blue channel value (0-255)"),
    alpha: int | None = Field(None, description="Alpha channel value (0-255), where 0 is fully transparent and 255 is fully opaque. Optional; if not provided, defaults to 255 (fully opaque)."),
) -> dict[str, Any] | ToolResult:
    """Convert a BMP image file to PNM (Portable Anymap) format with optional scaling and proportion constraints. Supports both URL-based and direct file content input."""

    # Call helper functions
    transparent_color = build_transparent_color(red, green, blue, alpha)

    # Construct request model with validation
    try:
        _request = _models.PostConvertBmpToPnmRequest(
            body=_models.PostConvertBmpToPnmRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, transparent_color=transparent_color)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_image_bmp_to_pnm: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/bmp/to/pnm"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_image_bmp_to_pnm")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_image_bmp_to_pnm", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_image_bmp_to_pnm",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_image_to_svg_bmp(
    file_: str | None = Field(None, alias="File", description="The image file to convert. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output SVG file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing for multiple output files to ensure unique, safe file naming."),
    preset: Literal["none", "detailed", "crisp", "graphic", "illustration", "noisyScan"] | None = Field(None, alias="Preset", description="A vectorization preset that applies pre-configured tracing settings optimized for different image types. When selected, presets override individual converter options except ColorMode, providing consistent and balanced SVG results."),
    color_mode: Literal["color", "bw"] | None = Field(None, alias="ColorMode", description="Controls whether the image is traced in full color or converted to black-and-white during vectorization."),
    layering: Literal["cutout", "stacked"] | None = Field(None, alias="Layering", description="Determines how color regions are arranged in the output SVG: cutout mode isolates regions as separate layers, while stacked mode overlays regions on top of each other."),
    curve_mode: Literal["pixel", "polygon", "spline"] | None = Field(None, alias="CurveMode", description="Defines how shapes are approximated during tracing. Pixel mode follows exact pixel boundaries with minimal smoothing, Polygon mode creates straight-edged paths with sharp corners, and Spline mode generates smooth continuous curves for more natural shapes."),
) -> dict[str, Any] | ToolResult:
    """Converts a BMP image to SVG vector format with configurable tracing presets and vectorization options. Supports color or black-and-white output with customizable curve approximation and layer arrangement."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertBmpToSvgRequest(
            body=_models.PostConvertBmpToSvgRequestBody(file_=file_, file_name=file_name, preset=preset, color_mode=color_mode, layering=layering, curve_mode=curve_mode)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_image_to_svg_bmp: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/bmp/to/svg"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_image_to_svg_bmp")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_image_to_svg_bmp", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_image_to_svg_bmp",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_image_bmp_to_tiff(
    file_: str | None = Field(None, alias="File", description="The BMP image file to convert. Accepts either a URL reference or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output TIFF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.tiff, output_1.tiff) for multiple files."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Apply scaling only when the input image dimensions exceed the target output dimensions."),
    multi_page: bool | None = Field(None, alias="MultiPage", description="Generate a multi-page TIFF file combining all converted pages into a single output file."),
) -> dict[str, Any] | ToolResult:
    """Convert a BMP image to TIFF format with optional scaling and multi-page output support. Supports both URL and direct file content input."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertBmpToTiffRequest(
            body=_models.PostConvertBmpToTiffRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, multi_page=multi_page)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_image_bmp_to_tiff: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/bmp/to/tiff"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_image_bmp_to_tiff")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_image_bmp_to_tiff", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_image_bmp_to_tiff",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_image_bmp_to_webp(
    file_: str | None = Field(None, alias="File", description="The image file to convert. Accepts either a URL pointing to a BMP file or the raw binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Custom name for the output WebP file. The system automatically sanitizes the name, appends the correct file extension, and adds indexing for multiple output files to ensure unique, safe filenames."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image to a different size."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions are larger than the target output dimensions."),
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(None, alias="ColorSpace", description="Define the color space for the output image. Choose from standard color profiles to optimize the image for different use cases."),
) -> dict[str, Any] | ToolResult:
    """Convert a BMP image file to WebP format with optional scaling and color space adjustments. Supports both URL-based and direct file uploads."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertBmpToWebpRequest(
            body=_models.PostConvertBmpToWebpRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, color_space=color_space)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_image_bmp_to_webp: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/bmp/to/webp"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_image_bmp_to_webp")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_image_bmp_to_webp", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_image_bmp_to_webp",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_csv_to_pdf(
    file_: str | None = Field(None, alias="File", description="The CSV file to convert. Accepts either a URL or raw file content in binary format."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., report_0.pdf, report_1.pdf) for multiple output files."),
    password: str | None = Field(None, alias="Password", description="Password required to open the input CSV file if it is password-protected."),
    convert_metadata: bool | None = Field(None, alias="ConvertMetadata", description="Preserve document metadata such as title, author, and keywords in the output PDF."),
    auto_column_fit: bool | None = Field(None, alias="AutoColumnFit", description="Automatically adjust column widths to minimize empty space and optimize table layout in the PDF."),
    header_on_each_page: bool | None = Field(None, alias="HeaderOnEachPage", description="Repeat the header row on every page when table content spans multiple pages in the PDF output."),
    thousands_separator: str | None = Field(None, alias="ThousandsSeparator", description="Character used to separate thousands in numeric values (e.g., comma for 1,000 or period for 1.000)."),
    decimal_separator: str | None = Field(None, alias="DecimalSeparator", description="Character used to separate decimal places in numeric values (e.g., period for 1.5 or comma for 1,5)."),
    date_format: Literal["us", "iso", "eu", "german", "japanese"] | None = Field(None, alias="DateFormat", description="Date format standard to apply in the output PDF, overriding regional Excel settings to ensure consistency."),
    pdfa: bool | None = Field(None, alias="Pdfa", description="Generate a PDF/A-1b compliant document for long-term archival and preservation purposes."),
) -> dict[str, Any] | ToolResult:
    """Converts CSV spreadsheet files to PDF format with support for formatting options, metadata preservation, and PDF/A compliance. Handles column fitting, header repetition across pages, and customizable number/date formatting."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertCsvToPdfRequest(
            body=_models.PostConvertCsvToPdfRequestBody(file_=file_, file_name=file_name, password=password, convert_metadata=convert_metadata, auto_column_fit=auto_column_fit, header_on_each_page=header_on_each_page, thousands_separator=thousands_separator, decimal_separator=decimal_separator, date_format=date_format, pdfa=pdfa)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_csv_to_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/csv/to/pdf"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_csv_to_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_csv_to_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_csv_to_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_csv_to_xlsx(
    file_: str | None = Field(None, alias="File", description="The CSV file to convert. Can be provided as a file upload or as a URL pointing to the CSV file."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the generated Excel output file. The system automatically sanitizes the filename, appends the .xlsx extension, and adds numeric suffixes (e.g., _0, _1) if multiple files are generated."),
    delimiter: str | None = Field(None, alias="Delimiter", description="The character used to separate fields in the CSV file. Specify the delimiter that matches your CSV format."),
    cell_type: Literal["general", "text"] | None = Field(None, alias="CellType", description="Determines how cell values are formatted in the output Excel file. Use 'text' to preserve CSV formatting for dates and numbers, or 'general' for automatic Excel formatting."),
) -> dict[str, Any] | ToolResult:
    """Converts a CSV file to Excel (XLSX) format with configurable field delimiters and cell type formatting. Supports both file uploads and URL-based file sources."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertCsvToXlsxRequest(
            body=_models.PostConvertCsvToXlsxRequestBody(file_=file_, file_name=file_name, delimiter=delimiter, cell_type=cell_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_csv_to_xlsx: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/csv/to/xlsx"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_csv_to_xlsx")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_csv_to_xlsx", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_csv_to_xlsx",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_djvu_to_jpg(
    file_: str | None = Field(None, alias="File", description="The DJVU file to convert. Can be provided as a URL or raw file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output file(s). The system sanitizes the filename, appends the correct extension, and adds indexing for multiple outputs (e.g., report_0.jpg, report_1.jpg)."),
    jpg_type: Literal["jpeg", "jpegcmyk", "jpeggray"] | None = Field(None, alias="JpgType", description="JPG encoding type for the output image. Choose between standard JPEG, CMYK color space, or grayscale."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain aspect ratio when scaling the output image to the target dimensions."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the target output size."),
) -> dict[str, Any] | ToolResult:
    """Converts a DJVU document to JPG image format with configurable output type and scaling options. Supports URL or file content input and generates uniquely named output files."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertDjvuToJpgRequest(
            body=_models.PostConvertDjvuToJpgRequestBody(file_=file_, file_name=file_name, jpg_type=jpg_type, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_djvu_to_jpg: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/djvu/to/jpg"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_djvu_to_jpg")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_djvu_to_jpg", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_djvu_to_jpg",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_djvu_to_pdf(
    file_: str | None = Field(None, alias="File", description="The DJVU file to convert. Can be provided as a URL or raw file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing for multiple output files to ensure unique, safe file naming."),
    base_font_size: float | None = Field(None, alias="BaseFontSize", description="Base font size in points (pt) for the converted PDF. All text scaling is relative to this value.", ge=1, le=50),
    margin_left: float | None = Field(None, alias="MarginLeft", description="Left margin in points (pt) for text content on the PDF page.", ge=0, le=200),
    margin_right: float | None = Field(None, alias="MarginRight", description="Right margin in points (pt) for text content on the PDF page.", ge=0, le=200),
    margin_top: float | None = Field(None, alias="MarginTop", description="Top margin in points (pt) for text content on the PDF page.", ge=0, le=200),
    margin_bottom: float | None = Field(None, alias="MarginBottom", description="Bottom margin in points (pt) for text content on the PDF page.", ge=0, le=200),
) -> dict[str, Any] | ToolResult:
    """Converts a DJVU document to PDF format with customizable layout and typography settings. Supports file input via URL or direct file content with configurable margins and base font sizing."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertDjvuToPdfRequest(
            body=_models.PostConvertDjvuToPdfRequestBody(file_=file_, file_name=file_name, base_font_size=base_font_size, margin_left=margin_left, margin_right=margin_right, margin_top=margin_top, margin_bottom=margin_bottom)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_djvu_to_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/djvu/to/pdf"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_djvu_to_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_djvu_to_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_djvu_to_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_djvu_to_png(
    file_: str | None = Field(None, alias="File", description="The DJVU file to convert. Accepts either a URL pointing to the file or the raw file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output PNG file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.png, output_1.png) for multiple files from a single input."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image to fit the target dimensions."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Apply scaling only when the input image dimensions exceed the target output dimensions, leaving smaller images unchanged."),
) -> dict[str, Any] | ToolResult:
    """Convert a DJVU document or image file to PNG format. Supports URL-based or direct file input with optional scaling and proportional resizing controls."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertDjvuToPngRequest(
            body=_models.PostConvertDjvuToPngRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_djvu_to_png: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/djvu/to/png"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_djvu_to_png")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_djvu_to_png", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_djvu_to_png",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_djvu_to_tiff(
    file_: str | None = Field(None, alias="File", description="The DJVU file to convert. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output TIFF file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.tiff, output_1.tiff) for multi-page conversions."),
    tiff_type: Literal["color24nc", "color32nc", "color24lzw", "color32lzw", "color24zip", "color32zip", "grayscale", "grayscalelzw", "grayscalezip", "monochromeg3", "monochromeg32d", "monochromeg4", "monochromelzw", "monochromepackbits"] | None = Field(None, alias="TiffType", description="TIFF compression and color format. Choose from color variants (24-bit or 32-bit with no compression, LZW, or ZIP), grayscale options, or monochrome formats with various compression methods."),
    multi_page: bool | None = Field(None, alias="MultiPage", description="Generate a single multi-page TIFF file containing all pages, or separate TIFF files for each page."),
    fill_order: Literal["0", "1"] | None = Field(None, alias="FillOrder", description="Bit order within each byte: 0 for most significant bit first (standard), 1 for least significant bit first."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image to a different size."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Apply scaling only when the input image dimensions exceed the target output dimensions, preserving quality for smaller images."),
) -> dict[str, Any] | ToolResult:
    """Convert DJVU documents to TIFF image format with configurable output settings including compression type, multi-page support, and scaling options."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertDjvuToTiffRequest(
            body=_models.PostConvertDjvuToTiffRequestBody(file_=file_, file_name=file_name, tiff_type=tiff_type, multi_page=multi_page, fill_order=fill_order, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_djvu_to_tiff: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/djvu/to/tiff"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_djvu_to_tiff")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_djvu_to_tiff", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_djvu_to_tiff",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_djvu_to_webp(
    file_: str | None = Field(None, alias="File", description="The file to convert, provided as either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output file. The API automatically sanitizes the filename, appends the correct .webp extension, and adds numeric indexing (e.g., output_0.webp, output_1.webp) when multiple files are generated."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the output dimensions."),
) -> dict[str, Any] | ToolResult:
    """Convert a DJVU document or image to WebP format. Supports URL or file content input with optional scaling and proportional constraint controls."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertDjvuToWebpRequest(
            body=_models.PostConvertDjvuToWebpRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_djvu_to_webp: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/djvu/to/webp"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_djvu_to_webp")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_djvu_to_webp", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_djvu_to_webp",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_document_to_docx(
    file_: str | None = Field(None, alias="File", description="The document file to convert. Accepts either a URL pointing to the file or the raw file content as binary data."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output file. The API automatically sanitizes the filename, appends the correct .docx extension, and adds numeric indexing (e.g., document_0.docx, document_1.docx) if multiple files are generated from a single input."),
    password: str | None = Field(None, alias="Password", description="Password required to open the input document if it is password-protected."),
    update_toc: bool | None = Field(None, alias="UpdateToc", description="When enabled, automatically updates all tables of content in the converted document to reflect current document structure."),
    update_references: bool | None = Field(None, alias="UpdateReferences", description="When enabled, automatically updates all reference fields (cross-references, citations, etc.) in the converted document."),
) -> dict[str, Any] | ToolResult:
    """Converts a document file to Microsoft Word (.docx) format. Supports password-protected documents and can optionally update tables of content and reference fields in the output."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertDocToDocxRequest(
            body=_models.PostConvertDocToDocxRequestBody(file_=file_, file_name=file_name, password=password, update_toc=update_toc, update_references=update_references)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_document_to_docx: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/doc/to/docx"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_document_to_docx")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_document_to_docx", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_document_to_docx",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def compare_docx_documents(
    file_: str | None = Field(None, alias="File", description="The primary Word document to be compared. Accepts either a file URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output comparison file. The system automatically sanitizes the filename, appends the appropriate extension, and adds indexing for multiple output files to ensure unique, safe file naming."),
    password: str | None = Field(None, alias="Password", description="Password required to open the primary document if it is password-protected."),
    compare_file: str | None = Field(None, alias="CompareFile", description="The Word document to compare against the primary document. Accepts either a file URL or binary file content."),
    compare_level: Literal["Word", "Character"] | None = Field(None, alias="CompareLevel", description="Specifies the granularity level for identifying differences between documents. Word-level comparison detects changes at word boundaries, while character-level comparison identifies changes at individual character positions."),
    compare_formatting: bool | None = Field(None, alias="CompareFormatting", description="Include formatting variations such as font, size, color, and style differences in the comparison results."),
    compare_case_changes: bool | None = Field(None, alias="CompareCaseChanges", description="Include capitalization and case differences in the comparison results."),
    compare_whitespace: bool | None = Field(None, alias="CompareWhitespace", description="Include whitespace differences such as spaces, tabs, and paragraph breaks in the comparison results."),
    compare_tables: bool | None = Field(None, alias="CompareTables", description="Include differences in table content and structure in the comparison results."),
    compare_headers: bool | None = Field(None, alias="CompareHeaders", description="Include differences in document headers and footers in the comparison results."),
    compare_footnotes: bool | None = Field(None, alias="CompareFootnotes", description="Include differences in footnotes and endnotes in the comparison results."),
    compare_textboxes: bool | None = Field(None, alias="CompareTextboxes", description="Include differences in text box content in the comparison results."),
    compare_fields: bool | None = Field(None, alias="CompareFields", description="Include differences in document fields in the comparison results."),
    compare_comments: bool | None = Field(None, alias="CompareComments", description="Include differences in comments and annotations in the comparison results."),
    compare_moves: bool | None = Field(None, alias="CompareMoves", description="Track and report content that has been moved between locations within the documents."),
    accept_revisions: bool | None = Field(None, alias="AcceptRevisions", description="Automatically accept all tracked revisions in the primary document before performing the comparison."),
    revision_author: str | None = Field(None, alias="RevisionAuthor", description="Author name to attribute to the comparison operation in the revision history."),
) -> dict[str, Any] | ToolResult:
    """Compare two Word documents and generate a detailed comparison report highlighting differences in content, formatting, and structure. Supports granular comparison options for specific document elements like tables, headers, comments, and more."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertDocxToCompareRequest(
            body=_models.PostConvertDocxToCompareRequestBody(file_=file_, file_name=file_name, password=password, compare_file=compare_file, compare_level=compare_level, compare_formatting=compare_formatting, compare_case_changes=compare_case_changes, compare_whitespace=compare_whitespace, compare_tables=compare_tables, compare_headers=compare_headers, compare_footnotes=compare_footnotes, compare_textboxes=compare_textboxes, compare_fields=compare_fields, compare_comments=compare_comments, compare_moves=compare_moves, accept_revisions=accept_revisions, revision_author=revision_author)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for compare_docx_documents: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/docx/to/compare"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("compare_docx_documents")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("compare_docx_documents", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="compare_docx_documents",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File", "CompareFile"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_document_to_html(
    file_: str | None = Field(None, alias="File", description="The document file to convert. Accepts either a file upload (binary content) or a URL pointing to a DOCX file."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the generated HTML output file. The API automatically sanitizes the filename, appends the correct extension, and adds numeric indexing (e.g., document_0.html, document_1.html) if multiple files are generated."),
    inline_images: bool | None = Field(None, alias="InlineImages", description="Whether to embed images from the document directly into the HTML output as inline content, or reference them externally."),
) -> dict[str, Any] | ToolResult:
    """Converts a DOCX document to HTML format with optional inline image embedding. Supports both file uploads and URL-based document sources."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertDocxToHtmlRequest(
            body=_models.PostConvertDocxToHtmlRequestBody(file_=file_, file_name=file_name, inline_images=inline_images)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_document_to_html: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/docx/to/html"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_document_to_html")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_document_to_html", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_document_to_html",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_document_to_image(
    file_: str | None = Field(None, alias="File", description="The document file to convert. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output file(s). The API automatically sanitizes the filename, appends the correct JPG extension, and adds numeric indexing (e.g., report_0.jpg, report_1.jpg) when multiple files are generated from a single input."),
    password: str | None = Field(None, alias="Password", description="Password for opening password-protected DOCX documents."),
    page_range: str | None = Field(None, alias="PageRange", description="Specifies which pages to convert using a range format (e.g., 1-10 converts pages 1 through 10 inclusive)."),
) -> dict[str, Any] | ToolResult:
    """Converts DOCX documents to JPG image format. Supports password-protected documents and selective page range conversion."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertDocxToJpgRequest(
            body=_models.PostConvertDocxToJpgRequestBody(file_=file_, file_name=file_name, password=password, page_range=page_range)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_document_to_image: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/docx/to/jpg"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_document_to_image")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_document_to_image", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_document_to_image",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_document_to_markdown(
    file_: str | None = Field(None, alias="File", description="The DOCX file to convert. Can be provided as a URL reference or as binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output Markdown file. The API automatically sanitizes the filename, appends the .md extension, and adds numeric suffixes (e.g., document_0.md, document_1.md) when generating multiple output files."),
) -> dict[str, Any] | ToolResult:
    """Converts a DOCX document to Markdown format. Accepts a DOCX file via URL or direct file content and returns the converted Markdown output with a customizable filename."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertDocxToMdRequest(
            body=_models.PostConvertDocxToMdRequestBody(file_=file_, file_name=file_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_document_to_markdown: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/docx/to/md"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_document_to_markdown")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_document_to_markdown", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_document_to_markdown",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_document_docx_to_odt(
    file_: str | None = Field(None, alias="File", description="The document file to convert. Accepts either a URL pointing to the file or the raw file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output file. The API automatically sanitizes the filename, appends the correct .odt extension, and adds numeric indexing (e.g., document_0.odt, document_1.odt) if multiple files are generated."),
    password: str | None = Field(None, alias="Password", description="Password required to open the input document if it is password-protected."),
    update_toc: bool | None = Field(None, alias="UpdateToc", description="When enabled, automatically updates all tables of content in the document during conversion."),
    update_references: bool | None = Field(None, alias="UpdateReferences", description="When enabled, automatically updates all reference fields in the document during conversion."),
) -> dict[str, Any] | ToolResult:
    """Converts a DOCX document to ODT (OpenDocument Text) format. Supports password-protected documents and can optionally update tables of content and reference fields during conversion."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertDocxToOdtRequest(
            body=_models.PostConvertDocxToOdtRequestBody(file_=file_, file_name=file_name, password=password, update_toc=update_toc, update_references=update_references)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_document_docx_to_odt: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/docx/to/odt"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_document_docx_to_odt")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_document_docx_to_odt", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_document_docx_to_odt",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_document_to_pdf(
    file_: str | None = Field(None, alias="File", description="The document file to convert. Accepts either a file URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the generated PDF output file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., report_0.pdf, report_1.pdf) for multiple output files."),
    password: str | None = Field(None, alias="Password", description="Password required to open password-protected DOCX documents."),
    page_range: str | None = Field(None, alias="PageRange", description="Specifies which pages to include in the output PDF using a range format (e.g., 1-10 for pages 1 through 10)."),
    convert_markups: bool | None = Field(None, alias="ConvertMarkups", description="When enabled, includes document markups such as revisions and comments in the converted PDF."),
    convert_tags: bool | None = Field(None, alias="ConvertTags", description="When enabled, converts document structure tags to improve PDF accessibility for screen readers and assistive technologies."),
    convert_metadata: bool | None = Field(None, alias="ConvertMetadata", description="When enabled, preserves document metadata (Title, Author, Keywords) as PDF metadata properties."),
    bookmark_mode: Literal["none", "headings", "bookmarks"] | None = Field(None, alias="BookmarkMode", description="Controls how bookmarks are generated in the PDF: 'none' disables bookmarks, 'headings' creates bookmarks from document headings, and 'bookmarks' uses existing bookmarks from the source document."),
    update_toc: bool | None = Field(None, alias="UpdateToc", description="When enabled, automatically updates all tables of content in the document before conversion."),
    pdfa: bool | None = Field(None, alias="Pdfa", description="When enabled, creates a PDF/A-3a compliant document for long-term archival and preservation."),
) -> dict[str, Any] | ToolResult:
    """Converts DOCX documents to PDF format with support for advanced formatting options, metadata preservation, and accessibility features. Handles password-protected documents and allows customization of bookmarks, page ranges, and PDF/A compliance."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertDocxToPdfRequest(
            body=_models.PostConvertDocxToPdfRequestBody(file_=file_, file_name=file_name, password=password, page_range=page_range, convert_markups=convert_markups, convert_tags=convert_tags, convert_metadata=convert_metadata, bookmark_mode=bookmark_mode, update_toc=update_toc, pdfa=pdfa)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_document_to_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/docx/to/pdf"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_document_to_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_document_to_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_document_to_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_document_to_image_png(
    file_: str | None = Field(None, alias="File", description="The document file to convert. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output file(s). The API sanitizes the filename, appends the correct extension, and adds indexing for multiple outputs (e.g., report_0.png, report_1.png)."),
    password: str | None = Field(None, alias="Password", description="Password required to open protected or encrypted documents."),
    page_range: str | None = Field(None, alias="PageRange", description="Specifies which pages to convert using range notation (e.g., 1-10 converts pages 1 through 10)."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintains aspect ratio when scaling the output image to prevent distortion."),
    rotate: int | None = Field(None, alias="Rotate", description="Rotates the output image by the specified angle in degrees.", ge=-360, le=360),
    red: int | None = Field(None, description="Red channel value (0-255)"),
    green: int | None = Field(None, description="Green channel value (0-255)"),
    blue: int | None = Field(None, description="Blue channel value (0-255)"),
    alpha: int | None = Field(None, description="Alpha channel value (0-255), where 0 is fully transparent and 255 is fully opaque. Optional; if not provided, defaults to 255 (fully opaque)."),
) -> dict[str, Any] | ToolResult:
    """Converts DOCX documents to PNG images with support for page range selection, scaling, and rotation. Handles password-protected documents and generates uniquely named output files."""

    # Call helper functions
    transparent_color = build_transparent_color(red, green, blue, alpha)

    # Construct request model with validation
    try:
        _request = _models.PostConvertDocxToPngRequest(
            body=_models.PostConvertDocxToPngRequestBody(file_=file_, file_name=file_name, password=password, page_range=page_range, scale_proportions=scale_proportions, rotate=rotate, transparent_color=transparent_color)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_document_to_image_png: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/docx/to/png"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_document_to_image_png")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_document_to_image_png", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_document_to_image_png",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_document_to_protected_word(
    file_: str | None = Field(None, alias="File", description="The document file to convert. Accepts either a URL reference or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the generated output file. The system automatically sanitizes the filename, appends the correct file extension, and adds indexing (e.g., filename_0, filename_1) when multiple files are produced from a single input."),
    encrypt_password: str | None = Field(None, alias="EncryptPassword", description="Password to encrypt the output Word document. When set, the password will be required to open and view the document content."),
) -> dict[str, Any] | ToolResult:
    """Converts a document file to a password-protected Word format. The output file can be encrypted with a password to restrict access and viewing of the document content."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertDocxToProtectRequest(
            body=_models.PostConvertDocxToProtectRequestBody(file_=file_, file_name=file_name, encrypt_password=encrypt_password)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_document_to_protected_word: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/docx/to/protect"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_document_to_protected_word")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_document_to_protected_word", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_document_to_protected_word",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_document_docx_to_rtf(
    file_: str | None = Field(None, alias="File", description="The document file to convert, provided as a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output RTF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.rtf, filename_1.rtf) for multiple output files."),
    password: str | None = Field(None, alias="Password", description="Password required to open password-protected DOCX documents."),
    update_toc: bool | None = Field(None, alias="UpdateToc", description="Automatically update all tables of content in the document during conversion."),
    update_references: bool | None = Field(None, alias="UpdateReferences", description="Automatically update all reference fields in the document during conversion."),
) -> dict[str, Any] | ToolResult:
    """Converts a DOCX document to RTF format with optional support for password-protected files and automatic updates to tables of content and reference fields."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertDocxToRtfRequest(
            body=_models.PostConvertDocxToRtfRequestBody(file_=file_, file_name=file_name, password=password, update_toc=update_toc, update_references=update_references)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_document_docx_to_rtf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/docx/to/rtf"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_document_docx_to_rtf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_document_docx_to_rtf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_document_docx_to_rtf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_document_to_tiff(
    file_: str | None = Field(None, alias="File", description="The document file to convert. Accepts either a URL reference or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output TIFF file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.tiff, filename_1.tiff) for multi-file outputs."),
    password: str | None = Field(None, alias="Password", description="Password required to open password-protected DOCX documents."),
    page_range: str | None = Field(None, alias="PageRange", description="Specifies which pages to convert using a range format (e.g., 1-10 converts pages 1 through 10)."),
    tiff_type: Literal["color24nc", "color32nc", "color24lzw", "color32lzw", "color24zip", "color32zip", "grayscale", "grayscalelzw", "grayscalezip", "monochromeg3", "monochromeg32d", "monochromeg4", "monochromelzw", "monochromepackbits"] | None = Field(None, alias="TiffType", description="Defines the TIFF compression type and color depth. Options range from color formats (24/32-bit with various compression) to grayscale and monochrome variants."),
    multi_page: bool | None = Field(None, alias="MultiPage", description="When enabled, combines all converted pages into a single multi-page TIFF file. When disabled, generates separate TIFF files for each page."),
    fill_order: Literal["0", "1"] | None = Field(None, alias="FillOrder", description="Specifies the logical bit order within each byte of the TIFF data. Value 0 represents MSB-first (most significant bit first), while 1 represents LSB-first (least significant bit first)."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="When enabled, maintains the original aspect ratio when scaling the output image to fit specified dimensions."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="When enabled, applies scaling only if the input image dimensions exceed the target output dimensions. Prevents upscaling of smaller images."),
) -> dict[str, Any] | ToolResult:
    """Converts DOCX documents to TIFF image format with configurable compression, color depth, and page range options. Supports password-protected documents and multi-page TIFF generation."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertDocxToTiffRequest(
            body=_models.PostConvertDocxToTiffRequestBody(file_=file_, file_name=file_name, password=password, page_range=page_range, tiff_type=tiff_type, multi_page=multi_page, fill_order=fill_order, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_document_to_tiff: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/docx/to/tiff"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_document_to_tiff")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_document_to_tiff", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_document_to_tiff",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_document_to_text(
    file_: str | None = Field(None, alias="File", description="The document file to convert. Accepts either a file URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output text file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.txt, output_1.txt) for multiple files."),
    password: str | None = Field(None, alias="Password", description="Password required to open the input document if it is password-protected."),
    substitutions: bool | None = Field(None, alias="Substitutions", description="When enabled, replaces special symbols with their text equivalents (e.g., © becomes (c))."),
    end_line_char: Literal["crlf", "cr", "lfcr", "lf"] | None = Field(None, alias="EndLineChar", description="Specifies the line ending character to use in the output text file."),
) -> dict[str, Any] | ToolResult:
    """Converts a DOCX document to plain text format with optional character substitutions and configurable line ending styles. Supports password-protected documents and customizable output file naming."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertDocxToTxtRequest(
            body=_models.PostConvertDocxToTxtRequestBody(file_=file_, file_name=file_name, password=password, substitutions=substitutions, end_line_char=end_line_char)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_document_to_text: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/docx/to/txt"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_document_to_text")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_document_to_text", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_document_to_text",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_document_to_webp(
    file_: str | None = Field(None, alias="File", description="The document file to convert. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output file(s). The system sanitizes the filename, appends the correct extension automatically, and adds indexing (e.g., filename_0.webp, filename_1.webp) for multiple output files."),
    password: str | None = Field(None, alias="Password", description="Password required to open password-protected DOCX documents."),
    page_range: str | None = Field(None, alias="PageRange", description="Specifies which pages to convert using a range format (e.g., 1-10 converts pages 1 through 10)."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="When enabled, maintains the original aspect ratio when scaling the output image to prevent distortion."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="When enabled, scaling is applied only if the input image dimensions exceed the output dimensions, preventing unnecessary upscaling."),
) -> dict[str, Any] | ToolResult:
    """Converts DOCX documents to WebP image format with configurable page range, scaling, and output naming. Supports password-protected documents and flexible scaling options."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertDocxToWebpRequest(
            body=_models.PostConvertDocxToWebpRequestBody(file_=file_, file_name=file_name, password=password, page_range=page_range, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_document_to_webp: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/docx/to/webp"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_document_to_webp")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_document_to_webp", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_document_to_webp",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_docx_to_xml(
    file_: str | None = Field(None, alias="File", description="The Word document to convert. Accepts either a file URL or raw file content in binary format."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output XML file(s). The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., report_0.xml, report_1.xml) for multiple output files."),
    password: str | None = Field(None, alias="Password", description="Password required to open the input document if it is password-protected."),
    update_toc: bool | None = Field(None, alias="UpdateToc", description="Whether to automatically update all tables of content in the document during conversion."),
    update_references: bool | None = Field(None, alias="UpdateReferences", description="Whether to automatically update all reference fields in the document during conversion."),
    xml_type: Literal["word2003", "flatWordXml", "strictOpenXml"] | None = Field(None, alias="XmlType", description="The XML schema type to use when saving the Word document. Word2003 uses legacy XML format, flatWordXml uses a single flat structure, and strictOpenXml uses the modern Office Open XML standard."),
) -> dict[str, Any] | ToolResult:
    """Converts a Word document (.docx) to XML format with support for multiple XML schema types. Optionally updates tables of content and reference fields, and supports password-protected documents."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertDocxToXmlRequest(
            body=_models.PostConvertDocxToXmlRequestBody(file_=file_, file_name=file_name, password=password, update_toc=update_toc, update_references=update_references, xml_type=xml_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_docx_to_xml: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/docx/to/xml"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_docx_to_xml")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_docx_to_xml", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_docx_to_xml",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_document_to_jpg(
    file_: str | None = Field(None, alias="File", description="The document file to convert. Accepts either a URL reference or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output file(s). The API automatically sanitizes the filename, appends the correct JPG extension, and adds numeric indexing (e.g., document_0.jpg, document_1.jpg) when multiple output files are generated."),
    password: str | None = Field(None, alias="Password", description="Password required to open password-protected documents."),
    page_range: str | None = Field(None, alias="PageRange", description="Specifies which pages to convert using a range format. Only the specified pages will be included in the output."),
) -> dict[str, Any] | ToolResult:
    """Converts a DOTX (Word template) document to JPG image format. Supports password-protected documents and selective page range conversion."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertDotxToJpgRequest(
            body=_models.PostConvertDotxToJpgRequestBody(file_=file_, file_name=file_name, password=password, page_range=page_range)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_document_to_jpg: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/dotx/to/jpg"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_document_to_jpg")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_document_to_jpg", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_document_to_jpg",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_dotx_to_pdf(
    file_: str | None = Field(None, alias="File", description="The Word document file to convert. Accepts either a file URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the generated PDF output file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., report_0.pdf, report_1.pdf) for multiple outputs."),
    password: str | None = Field(None, alias="Password", description="Password required to open password-protected Word documents."),
    page_range: str | None = Field(None, alias="PageRange", description="Specifies which pages to convert using a range format (e.g., 1-10 converts pages 1 through 10)."),
    convert_markups: bool | None = Field(None, alias="ConvertMarkups", description="When enabled, includes document markups such as revisions and comments in the PDF output."),
    convert_tags: bool | None = Field(None, alias="ConvertTags", description="When enabled, converts document structure tags to improve PDF accessibility for screen readers and assistive technologies."),
    convert_metadata: bool | None = Field(None, alias="ConvertMetadata", description="When enabled, preserves document metadata (Title, Author, Keywords) as PDF metadata properties."),
    bookmark_mode: Literal["none", "headings", "bookmarks"] | None = Field(None, alias="BookmarkMode", description="Controls bookmark generation in the PDF: 'none' disables bookmarks, 'headings' creates bookmarks from document headings, and 'bookmarks' uses existing bookmarks from the source document."),
    update_toc: bool | None = Field(None, alias="UpdateToc", description="When enabled, automatically updates all tables of content in the document before conversion."),
    pdfa: bool | None = Field(None, alias="Pdfa", description="When enabled, generates a PDF/A-3a compliant document for long-term archival and preservation."),
) -> dict[str, Any] | ToolResult:
    """Converts a Word document (.dotx) to PDF format with support for advanced options including markup conversion, accessibility tags, metadata preservation, and PDF/A compliance."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertDotxToPdfRequest(
            body=_models.PostConvertDotxToPdfRequestBody(file_=file_, file_name=file_name, password=password, page_range=page_range, convert_markups=convert_markups, convert_tags=convert_tags, convert_metadata=convert_metadata, bookmark_mode=bookmark_mode, update_toc=update_toc, pdfa=pdfa)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_dotx_to_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/dotx/to/pdf"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_dotx_to_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_dotx_to_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_dotx_to_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_dwf_to_jpg(
    file_: str | None = Field(None, alias="File", description="The file to convert, provided as either a URL reference or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.jpg, filename_1.jpg) for multiple output files."),
    export_layers: bool | None = Field(None, alias="ExportLayers", description="Whether to export AutoCAD layers as separate elements in the output image."),
    color_space: Literal["truecolors", "grayscale", "monochrome"] | None = Field(None, alias="ColorSpace", description="The color space for the output image, affecting color representation and file size."),
) -> dict[str, Any] | ToolResult:
    """Converts AutoCAD DWF files to JPG image format with support for layer export and color space customization. Accepts file input as URL or binary content and generates optimized image output."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertDwfToJpgRequest(
            body=_models.PostConvertDwfToJpgRequestBody(file_=file_, file_name=file_name, export_layers=export_layers, color_space=color_space)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_dwf_to_jpg: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/dwf/to/jpg"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_dwf_to_jpg")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_dwf_to_jpg", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_dwf_to_jpg",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_dwf_to_pdf(
    file_: str | None = Field(None, alias="File", description="The DWF file to convert. Accepts either a URL reference or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the generated PDF output file. The system automatically sanitizes the filename, appends the correct .pdf extension, and adds numeric indexing (e.g., output_0.pdf, output_1.pdf) when multiple files are produced from a single input."),
    export_layers: bool | None = Field(None, alias="ExportLayers", description="Whether to preserve and export AutoCAD layers in the PDF output, maintaining the layer structure from the original DWF file."),
    auto_fit: bool | None = Field(None, alias="AutoFit", description="Automatically detects the drawing dimensions and adjusts the output to fit the page size, optionally rotating the page orientation to accommodate the drawing without clipping."),
    color_space: Literal["truecolors", "grayscale", "monochrome"] | None = Field(None, alias="ColorSpace", description="Specifies the color space for the PDF output. Choose truecolors for full color reproduction, grayscale for reduced file size with gray tones, or monochrome for black and white only."),
) -> dict[str, Any] | ToolResult:
    """Converts AutoCAD DWF (Design Web Format) files to PDF format with support for layer export and automatic page fitting. The conversion intelligently handles drawing dimensions and color space preferences to produce optimized PDF output."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertDwfToPdfRequest(
            body=_models.PostConvertDwfToPdfRequestBody(file_=file_, file_name=file_name, export_layers=export_layers, auto_fit=auto_fit, color_space=color_space)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_dwf_to_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/dwf/to/pdf"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_dwf_to_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_dwf_to_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_dwf_to_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_dwf_to_png(
    file_: str | None = Field(None, alias="File", description="The DWF file to convert. Can be provided as a URL or raw binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output PNG file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.png, output_1.png) for multiple files to ensure unique identification."),
    export_layers: bool | None = Field(None, alias="ExportLayers", description="Whether to export AutoCAD layers as separate elements in the output image."),
    color_space: Literal["truecolors", "grayscale", "monochrome"] | None = Field(None, alias="ColorSpace", description="Color space for the output PNG image. Truecolors preserves full color information, grayscale converts to 256 shades of gray, and monochrome converts to pure black and white."),
    red: int | None = Field(None, description="Red channel value (0-255)"),
    green: int | None = Field(None, description="Green channel value (0-255)"),
    blue: int | None = Field(None, description="Blue channel value (0-255)"),
    alpha: int | None = Field(None, description="Alpha channel value (0-255), where 0 is fully transparent and 255 is fully opaque. Optional; if not provided, defaults to 255 (fully opaque)."),
) -> dict[str, Any] | ToolResult:
    """Converts AutoCAD DWF files to PNG image format with support for layer export and color space customization. Accepts file input as URL or binary content and generates uniquely named output files."""

    # Call helper functions
    transparent_color = build_transparent_color(red, green, blue, alpha)

    # Construct request model with validation
    try:
        _request = _models.PostConvertDwfToPngRequest(
            body=_models.PostConvertDwfToPngRequestBody(file_=file_, file_name=file_name, export_layers=export_layers, color_space=color_space, transparent_color=transparent_color)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_dwf_to_png: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/dwf/to/png"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_dwf_to_png")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_dwf_to_png", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_dwf_to_png",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_dwf_to_svg(
    file_: str | None = Field(None, alias="File", description="The DWF file to convert. Provide either a publicly accessible URL or the binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output SVG file(s). The API automatically sanitizes the filename, appends the correct extension, and adds numeric indices for multiple output files to ensure unique, safe naming."),
    export_layers: bool | None = Field(None, alias="ExportLayers", description="Whether to export AutoCAD layers as separate elements in the SVG output."),
    color_space: Literal["truecolors", "grayscale", "monochrome"] | None = Field(None, alias="ColorSpace", description="Color space for the output SVG. Choose between full color, grayscale, or monochrome rendering."),
) -> dict[str, Any] | ToolResult:
    """Converts AutoCAD DWF files to SVG format with support for layer export and color space customization. Accepts file input as URL or binary content and generates properly named output files."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertDwfToSvgRequest(
            body=_models.PostConvertDwfToSvgRequestBody(file_=file_, file_name=file_name, export_layers=export_layers, color_space=color_space)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_dwf_to_svg: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/dwf/to/svg"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_dwf_to_svg")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_dwf_to_svg", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_dwf_to_svg",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_dwf_to_tiff(
    file_: str | None = Field(None, alias="File", description="The DWF file to convert. Provide either a publicly accessible URL or the binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output TIFF file(s). The system automatically sanitizes the filename, appends the correct extension, and adds numeric suffixes (e.g., filename_0.tiff, filename_1.tiff) when multiple files are generated."),
    export_layers: bool | None = Field(None, alias="ExportLayers", description="Whether to export AutoCAD layers as separate elements in the output TIFF."),
    color_space: Literal["truecolors", "grayscale", "monochrome"] | None = Field(None, alias="ColorSpace", description="Color space for the output TIFF image. Choose truecolors for full color output, grayscale for reduced color depth, or monochrome for black and white only."),
    multi_page: bool | None = Field(None, alias="MultiPage", description="Whether to combine all pages into a single multi-page TIFF file or generate separate TIFF files for each page."),
) -> dict[str, Any] | ToolResult:
    """Converts AutoCAD DWF files to TIFF format with support for layer export, color space configuration, and multi-page output. Accepts file input as URL or binary content and generates sanitized output files with automatic extension handling."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertDwfToTiffRequest(
            body=_models.PostConvertDwfToTiffRequestBody(file_=file_, file_name=file_name, export_layers=export_layers, color_space=color_space, multi_page=multi_page)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_dwf_to_tiff: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/dwf/to/tiff"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_dwf_to_tiff")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_dwf_to_tiff", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_dwf_to_tiff",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_dwf_to_webp(
    file_: str | None = Field(None, alias="File", description="The file to convert, provided as either a URL reference or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output file(s). The system automatically sanitizes the filename, appends the correct WebP extension, and adds numeric indexing (e.g., output_0.webp, output_1.webp) when multiple files are generated from a single input."),
    export_layers: bool | None = Field(None, alias="ExportLayers", description="Whether to export AutoCAD layers as separate elements in the output."),
    color_space: Literal["truecolors", "grayscale", "monochrome"] | None = Field(None, alias="ColorSpace", description="The color space for the output image."),
    red: int | None = Field(None, description="Red channel value (0-255)"),
    green: int | None = Field(None, description="Green channel value (0-255)"),
    blue: int | None = Field(None, description="Blue channel value (0-255)"),
    alpha: int | None = Field(None, description="Alpha channel value (0-255), where 0 is fully transparent and 255 is fully opaque. Optional; if not provided, defaults to 255 (fully opaque)."),
) -> dict[str, Any] | ToolResult:
    """Converts AutoCAD DWF files to WebP format with support for layer export and color space customization. Accepts file input as URL or binary content and generates optimized WebP output."""

    # Call helper functions
    transparent_color = build_transparent_color(red, green, blue, alpha)

    # Construct request model with validation
    try:
        _request = _models.PostConvertDwfToWebpRequest(
            body=_models.PostConvertDwfToWebpRequestBody(file_=file_, file_name=file_name, export_layers=export_layers, color_space=color_space, transparent_color=transparent_color)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_dwf_to_webp: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/dwf/to/webp"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_dwf_to_webp")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_dwf_to_webp", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_dwf_to_webp",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_dwg_to_jpg(
    file_: str | None = Field(None, alias="File", description="The DWG file to convert. Provide either a URL pointing to the file or the raw file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output JPG file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.jpg, filename_1.jpg) for multiple output files."),
    export_layers: bool | None = Field(None, alias="ExportLayers", description="Whether to export AutoCAD layers as separate elements in the output image."),
    color_space: Literal["truecolors", "grayscale", "monochrome"] | None = Field(None, alias="ColorSpace", description="Color space for the output JPG image. Choose between full color, grayscale, or monochrome rendering."),
) -> dict[str, Any] | ToolResult:
    """Converts AutoCAD DWG files to JPG image format with support for layer export and color space customization. Accepts file input via URL or direct file content."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertDwgToJpgRequest(
            body=_models.PostConvertDwgToJpgRequestBody(file_=file_, file_name=file_name, export_layers=export_layers, color_space=color_space)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_dwg_to_jpg: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/dwg/to/jpg"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_dwg_to_jpg")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_dwg_to_jpg", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_dwg_to_jpg",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_dwg_to_pdf(
    file_: str | None = Field(None, alias="File", description="The DWG file to convert. Can be provided as a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.pdf, filename_1.pdf) for multiple output files."),
    export_layers: bool | None = Field(None, alias="ExportLayers", description="Whether to export AutoCAD layers as separate elements in the PDF output."),
    auto_fit: bool | None = Field(None, alias="AutoFit", description="Automatically detects and adjusts the drawing to fit the current page size, including automatic page orientation adjustment if needed."),
    color_space: Literal["truecolors", "grayscale", "monochrome"] | None = Field(None, alias="ColorSpace", description="Specifies the color space for the output PDF. Choose from true color, grayscale, or monochrome rendering."),
) -> dict[str, Any] | ToolResult:
    """Converts AutoCAD DWG files to PDF format with support for layer export, automatic page fitting, and color space configuration. Accepts file input as URL or binary content."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertDwgToPdfRequest(
            body=_models.PostConvertDwgToPdfRequestBody(file_=file_, file_name=file_name, export_layers=export_layers, auto_fit=auto_fit, color_space=color_space)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_dwg_to_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/dwg/to/pdf"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_dwg_to_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_dwg_to_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_dwg_to_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_dwg_to_png(
    file_: str | None = Field(None, alias="File", description="The DWG file to convert. Provide either a URL pointing to the file or the raw file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output PNG file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.png, filename_1.png) for multiple output files."),
    export_layers: bool | None = Field(None, alias="ExportLayers", description="Whether to export AutoCAD layers as separate elements in the output image."),
    color_space: Literal["truecolors", "grayscale", "monochrome"] | None = Field(None, alias="ColorSpace", description="Color space for the output PNG image. Choose between full color, grayscale, or monochrome rendering."),
    red: int | None = Field(None, description="Red channel value (0-255)"),
    green: int | None = Field(None, description="Green channel value (0-255)"),
    blue: int | None = Field(None, description="Blue channel value (0-255)"),
    alpha: int | None = Field(None, description="Alpha channel value (0-255), where 0 is fully transparent and 255 is fully opaque. Optional; if not provided, defaults to 255 (fully opaque)."),
) -> dict[str, Any] | ToolResult:
    """Converts AutoCAD DWG files to PNG image format with support for layer export and color space customization. Accepts file input via URL or direct file content."""

    # Call helper functions
    transparent_color = build_transparent_color(red, green, blue, alpha)

    # Construct request model with validation
    try:
        _request = _models.PostConvertDwgToPngRequest(
            body=_models.PostConvertDwgToPngRequestBody(file_=file_, file_name=file_name, export_layers=export_layers, color_space=color_space, transparent_color=transparent_color)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_dwg_to_png: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/dwg/to/png"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_dwg_to_png")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_dwg_to_png", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_dwg_to_png",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_dwg_to_svg(
    file_: str | None = Field(None, alias="File", description="The DWG file to convert, provided as either a URL reference or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output SVG file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.svg, output_1.svg) for multiple generated files."),
    export_layers: bool | None = Field(None, alias="ExportLayers", description="Whether to export AutoCAD layers as separate SVG elements in the output."),
    color_space: Literal["truecolors", "grayscale", "monochrome"] | None = Field(None, alias="ColorSpace", description="The color space for the output SVG, affecting how colors are rendered."),
) -> dict[str, Any] | ToolResult:
    """Converts AutoCAD DWG files to SVG format with support for layer export and color space configuration. Accepts file input via URL or direct file content."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertDwgToSvgRequest(
            body=_models.PostConvertDwgToSvgRequestBody(file_=file_, file_name=file_name, export_layers=export_layers, color_space=color_space)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_dwg_to_svg: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/dwg/to/svg"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_dwg_to_svg")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_dwg_to_svg", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_dwg_to_svg",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_dwg_to_tiff(
    file_: str | None = Field(None, alias="File", description="The DWG file to convert. Provide either a URL pointing to the file or the raw file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output TIFF file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.tiff, filename_1.tiff) for multiple output files."),
    export_layers: bool | None = Field(None, alias="ExportLayers", description="Whether to export AutoCAD layers as separate elements in the output."),
    color_space: Literal["truecolors", "grayscale", "monochrome"] | None = Field(None, alias="ColorSpace", description="Color space for the output TIFF image."),
    multi_page: bool | None = Field(None, alias="MultiPage", description="Whether to create a multi-page TIFF file combining all content, or separate single-page files."),
) -> dict[str, Any] | ToolResult:
    """Converts AutoCAD DWG files to TIFF format with support for layer export, color space configuration, and multi-page output. Accepts file input via URL or direct file content."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertDwgToTiffRequest(
            body=_models.PostConvertDwgToTiffRequestBody(file_=file_, file_name=file_name, export_layers=export_layers, color_space=color_space, multi_page=multi_page)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_dwg_to_tiff: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/dwg/to/tiff"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_dwg_to_tiff")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_dwg_to_tiff", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_dwg_to_tiff",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_dwg_to_webp(
    file_: str | None = Field(None, alias="File", description="The DWG file to convert. Provide either a URL pointing to the file or the raw file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output WebP file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.webp, filename_1.webp) for multiple output files."),
    export_layers: bool | None = Field(None, alias="ExportLayers", description="Whether to export AutoCAD layers as separate elements in the output."),
    color_space: Literal["truecolors", "grayscale", "monochrome"] | None = Field(None, alias="ColorSpace", description="Color space for the output WebP image. Choose between full color, grayscale, or monochrome rendering."),
    red: int | None = Field(None, description="Red channel value (0-255)"),
    green: int | None = Field(None, description="Green channel value (0-255)"),
    blue: int | None = Field(None, description="Blue channel value (0-255)"),
    alpha: int | None = Field(None, description="Alpha channel value (0-255), where 0 is fully transparent and 255 is fully opaque. Optional; if not provided, defaults to 255 (fully opaque)."),
) -> dict[str, Any] | ToolResult:
    """Converts AutoCAD DWG files to WebP format with support for layer export and color space customization. Accepts file input via URL or direct file content."""

    # Call helper functions
    transparent_color = build_transparent_color(red, green, blue, alpha)

    # Construct request model with validation
    try:
        _request = _models.PostConvertDwgToWebpRequest(
            body=_models.PostConvertDwgToWebpRequestBody(file_=file_, file_name=file_name, export_layers=export_layers, color_space=color_space, transparent_color=transparent_color)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_dwg_to_webp: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/dwg/to/webp"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_dwg_to_webp")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_dwg_to_webp", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_dwg_to_webp",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_dxf_to_jpg(
    file_: str | None = Field(None, alias="File", description="The DXF file to convert. Provide either a publicly accessible URL or the binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Custom name for the output JPG file. The system automatically sanitizes the name, appends the correct file extension, and adds indexing (e.g., filename_0.jpg, filename_1.jpg) for multiple output files."),
    export_layers: bool | None = Field(None, alias="ExportLayers", description="Whether to export AutoCAD layers as separate elements in the output image."),
    color_space: Literal["truecolors", "grayscale", "monochrome"] | None = Field(None, alias="ColorSpace", description="The color space for the output JPG image. Choose between full color, grayscale, or monochrome rendering."),
) -> dict[str, Any] | ToolResult:
    """Converts AutoCAD DXF files to JPG image format with support for layer export and color space customization. Accepts file input as URL or binary content and generates optimized image output."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertDxfToJpgRequest(
            body=_models.PostConvertDxfToJpgRequestBody(file_=file_, file_name=file_name, export_layers=export_layers, color_space=color_space)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_dxf_to_jpg: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/dxf/to/jpg"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_dxf_to_jpg")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_dxf_to_jpg", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_dxf_to_jpg",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_dxf_to_pdf(
    file_: str | None = Field(None, alias="File", description="The DXF file to convert. Accepts either a URL reference or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output PDF file(s). The system automatically sanitizes the filename, appends the correct extension, and adds numeric indices for multiple output files to ensure unique, safe naming."),
    export_layers: bool | None = Field(None, alias="ExportLayers", description="Whether to preserve and export AutoCAD layers in the output PDF."),
    auto_fit: bool | None = Field(None, alias="AutoFit", description="Automatically detects the drawing dimensions and adjusts the page size and orientation to fit the content without clipping."),
    color_space: Literal["truecolors", "grayscale", "monochrome"] | None = Field(None, alias="ColorSpace", description="Specifies the color space for the output PDF. Choose truecolors for full color output, grayscale for reduced file size, or monochrome for black and white only."),
) -> dict[str, Any] | ToolResult:
    """Converts AutoCAD DXF drawings to PDF format with support for layer export, automatic page fitting, and color space configuration. The conversion intelligently handles multi-page outputs and ensures proper file naming."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertDxfToPdfRequest(
            body=_models.PostConvertDxfToPdfRequestBody(file_=file_, file_name=file_name, export_layers=export_layers, auto_fit=auto_fit, color_space=color_space)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_dxf_to_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/dxf/to/pdf"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_dxf_to_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_dxf_to_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_dxf_to_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_dxf_to_png(
    file_: str | None = Field(None, alias="File", description="The DXF file to convert, provided either as a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output PNG file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.png, filename_1.png) for multiple output files."),
    export_layers: bool | None = Field(None, alias="ExportLayers", description="Whether to export AutoCAD layers as separate elements in the output image."),
    color_space: Literal["truecolors", "grayscale", "monochrome"] | None = Field(None, alias="ColorSpace", description="The color space for the output PNG image. Choose truecolors for full RGB output, grayscale for 8-bit grayscale, or monochrome for black and white."),
    red: int | None = Field(None, description="Red channel value (0-255)"),
    green: int | None = Field(None, description="Green channel value (0-255)"),
    blue: int | None = Field(None, description="Blue channel value (0-255)"),
    alpha: int | None = Field(None, description="Alpha channel value (0-255), where 0 is fully transparent and 255 is fully opaque. Optional; if not provided, defaults to 255 (fully opaque)."),
) -> dict[str, Any] | ToolResult:
    """Converts AutoCAD DXF files to PNG image format with support for layer export and color space customization. Accepts file input as URL or binary content and generates optimized raster images."""

    # Call helper functions
    transparent_color = build_transparent_color(red, green, blue, alpha)

    # Construct request model with validation
    try:
        _request = _models.PostConvertDxfToPngRequest(
            body=_models.PostConvertDxfToPngRequestBody(file_=file_, file_name=file_name, export_layers=export_layers, color_space=color_space, transparent_color=transparent_color)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_dxf_to_png: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/dxf/to/png"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_dxf_to_png")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_dxf_to_png", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_dxf_to_png",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_dxf_to_svg(
    file_: str | None = Field(None, alias="File", description="The DXF file to convert. Provide either a publicly accessible URL or the binary file content directly."),
    file_name: str | None = Field(None, alias="FileName", description="Custom name for the output SVG file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.svg, filename_1.svg) for multiple output files."),
    export_layers: bool | None = Field(None, alias="ExportLayers", description="Whether to preserve and export AutoCAD layer information in the output SVG file."),
    color_space: Literal["truecolors", "grayscale", "monochrome"] | None = Field(None, alias="ColorSpace", description="Color space for the output SVG. Choose between full color, grayscale, or monochrome rendering."),
) -> dict[str, Any] | ToolResult:
    """Converts AutoCAD DXF files to SVG format with support for layer export and color space configuration. Accepts file input as URL or binary content and generates optimized vector graphics output."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertDxfToSvgRequest(
            body=_models.PostConvertDxfToSvgRequestBody(file_=file_, file_name=file_name, export_layers=export_layers, color_space=color_space)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_dxf_to_svg: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/dxf/to/svg"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_dxf_to_svg")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_dxf_to_svg", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_dxf_to_svg",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_dxf_to_tiff(
    file_: str | None = Field(None, alias="File", description="The DXF file to convert. Accepts either a URL reference or raw file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output TIFF file(s). The system automatically sanitizes the filename, appends the correct extension, and adds numeric suffixes (e.g., `filename_0.tiff`, `filename_1.tiff`) when generating multiple files."),
    export_layers: bool | None = Field(None, alias="ExportLayers", description="Whether to export AutoCAD layers as separate elements in the output TIFF."),
    color_space: Literal["truecolors", "grayscale", "monochrome"] | None = Field(None, alias="ColorSpace", description="Color space for the output image. Choose between full color, grayscale, or black-and-white rendering."),
    multi_page: bool | None = Field(None, alias="MultiPage", description="Whether to combine all output into a single multi-page TIFF file or create separate TIFF files for each page."),
) -> dict[str, Any] | ToolResult:
    """Converts DXF (AutoCAD drawing) files to TIFF image format with support for layer export and multi-page output. Useful for archiving technical drawings or sharing CAD designs as raster images."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertDxfToTiffRequest(
            body=_models.PostConvertDxfToTiffRequestBody(file_=file_, file_name=file_name, export_layers=export_layers, color_space=color_space, multi_page=multi_page)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_dxf_to_tiff: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/dxf/to/tiff"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_dxf_to_tiff")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_dxf_to_tiff", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_dxf_to_tiff",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_dxf_to_webp(
    file_: str | None = Field(None, alias="File", description="The DXF file to convert. Can be provided as a URL or raw binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Custom name for the output WebP file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing for multiple output files to ensure unique, safe file naming."),
    export_layers: bool | None = Field(None, alias="ExportLayers", description="Whether to export AutoCAD layers as separate elements in the output."),
    color_space: Literal["truecolors", "grayscale", "monochrome"] | None = Field(None, alias="ColorSpace", description="Color space for the output WebP image. Choose between full color, grayscale, or monochrome rendering."),
    red: int | None = Field(None, description="Red channel value (0-255)"),
    green: int | None = Field(None, description="Green channel value (0-255)"),
    blue: int | None = Field(None, description="Blue channel value (0-255)"),
    alpha: int | None = Field(None, description="Alpha channel value (0-255), where 0 is fully transparent and 255 is fully opaque. Optional; if not provided, defaults to 255 (fully opaque)."),
) -> dict[str, Any] | ToolResult:
    """Converts AutoCAD DXF files to WebP image format with support for layer export and color space customization. Accepts file input as URL or binary content and generates optimized WebP output."""

    # Call helper functions
    transparent_color = build_transparent_color(red, green, blue, alpha)

    # Construct request model with validation
    try:
        _request = _models.PostConvertDxfToWebpRequest(
            body=_models.PostConvertDxfToWebpRequestBody(file_=file_, file_name=file_name, export_layers=export_layers, color_space=color_space, transparent_color=transparent_color)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_dxf_to_webp: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/dxf/to/webp"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_dxf_to_webp")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_dxf_to_webp", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_dxf_to_webp",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def extract_email_attachments(
    file_: str | None = Field(None, alias="File", description="The email file to process. Accepts either a URL pointing to the file or the raw file content as binary data."),
    file_name: str | None = Field(None, alias="FileName", description="Custom name for the output file(s). The system automatically sanitizes the name, appends the appropriate file extension, and adds numeric suffixes (e.g., _0, _1) when multiple files are generated from a single input."),
    use_cid_as_file_name: bool | None = Field(None, alias="UseCIDAsFileName", description="When enabled, uses the Content ID (CID) of attachments as the filename instead of the original filename."),
    ignore_inline_attachments: bool | None = Field(None, alias="IgnoreInlineAttachments", description="When enabled, skips inline attachments such as embedded images and logos, processing only standalone attachments."),
) -> dict[str, Any] | ToolResult:
    """Extracts attachments and metadata from email files (EML, MSG, etc.) into structured data. Supports filtering of inline attachments and customizable output file naming."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertEmailToExtractRequest(
            body=_models.PostConvertEmailToExtractRequestBody(file_=file_, file_name=file_name, use_cid_as_file_name=use_cid_as_file_name, ignore_inline_attachments=ignore_inline_attachments)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for extract_email_attachments: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/email/to/extract"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("extract_email_attachments")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("extract_email_attachments", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="extract_email_attachments",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def extract_email_metadata(
    file_: str | None = Field(None, alias="File", description="The email file to process. Accepts either a file URL or raw file content in binary format."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output metadata file. The system automatically sanitizes the filename, appends the appropriate extension, and adds numeric indexing (e.g., metadata_0, metadata_1) when multiple output files are generated from a single input."),
    ignore_inline_attachments: bool | None = Field(None, alias="IgnoreInlineAttachments", description="When enabled, skips inline attachments such as embedded images and logos during processing, extracting only non-inline attachments."),
) -> dict[str, Any] | ToolResult:
    """Extracts structured metadata from email files, converting email content into organized metadata format. Supports both file uploads and direct content input, with optional filtering of inline attachments."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertEmailToMetadataRequest(
            body=_models.PostConvertEmailToMetadataRequestBody(file_=file_, file_name=file_name, ignore_inline_attachments=ignore_inline_attachments)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for extract_email_metadata: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/email/to/metadata"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("extract_email_metadata")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("extract_email_metadata", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="extract_email_metadata",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_email_to_image(
    file_: str | None = Field(None, alias="File", description="The email file to convert. Accepts either a URL reference or raw file content in binary format."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the generated output file(s). The system automatically sanitizes the filename, appends the correct extension, and adds numeric indices (e.g., output_0.jpg, output_1.jpg) when multiple files are produced."),
    ignore_attachment_errors: bool | None = Field(None, alias="IgnoreAttachmentErrors", description="When enabled, attachment conversion errors are suppressed and the email is still converted to the target format. Only applies when attachments are being processed."),
    merge: bool | None = Field(None, alias="Merge", description="When enabled, merges the email body content with converted attachments into a single output. Only applies when attachments are being processed."),
) -> dict[str, Any] | ToolResult:
    """Convert an email message (EML format) to JPG image format. Optionally process attachments and merge them with the email body in the output."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertEmlToJpgRequest(
            body=_models.PostConvertEmlToJpgRequestBody(file_=file_, file_name=file_name, ignore_attachment_errors=ignore_attachment_errors, merge=merge)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_email_to_image: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/eml/to/jpg"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_email_to_image")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_email_to_image", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_email_to_image",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_eml_to_pdf(
    file_: str | None = Field(None, alias="File", description="The EML file to convert. Accepts either a URL reference or raw file content in binary format."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the generated PDF output file. The system automatically sanitizes the filename, appends the correct extension, and adds numeric indexing (e.g., report_0.pdf, report_1.pdf) when multiple files are produced."),
    ignore_attachment_errors: bool | None = Field(None, alias="IgnoreAttachmentErrors", description="When enabled, attachment conversion errors are ignored and the email body is still converted to PDF. Only applies when attachments are being converted."),
    merge: bool | None = Field(None, alias="Merge", description="When enabled, merges the email body with converted attachments into a single PDF document. Only applies when attachments are being converted."),
    pdfa: bool | None = Field(None, alias="Pdfa", description="When enabled, creates a PDF/A-1b compliant document, which is an ISO-standardized archival format suitable for long-term preservation."),
    margins: str | None = Field(None, alias="Margins", description="Page margins in millimeters as space-separated values in CSS order: top right bottom left (e.g., '10 10 10 10')"),
) -> dict[str, Any] | ToolResult:
    """Converts an EML (email) file to PDF format, with optional support for embedding attachments and creating PDF/A-1b compliant documents."""

    # Call helper functions
    margins_parsed = parse_margins(margins)

    # Construct request model with validation
    try:
        _request = _models.PostConvertEmlToPdfRequest(
            body=_models.PostConvertEmlToPdfRequestBody(file_=file_, file_name=file_name, ignore_attachment_errors=ignore_attachment_errors, merge=merge, pdfa=pdfa, margin_top=margins_parsed.get('MarginTop') if margins_parsed else None, margin_right=margins_parsed.get('MarginRight') if margins_parsed else None, margin_bottom=margins_parsed.get('MarginBottom') if margins_parsed else None, margin_left=margins_parsed.get('MarginLeft') if margins_parsed else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_eml_to_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/eml/to/pdf"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_eml_to_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_eml_to_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_eml_to_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_email_to_png(
    file_: str | None = Field(None, alias="File", description="The email file to convert. Accepts either a URL reference or raw file content in binary format."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output file(s). The system automatically sanitizes the filename, appends the correct extension, and adds numeric indices (e.g., output_0.png, output_1.png) when multiple files are generated."),
    ignore_attachment_errors: bool | None = Field(None, alias="IgnoreAttachmentErrors", description="When enabled, attachment conversion errors are ignored and the email is still converted to PNG. Only applies when attachments are being converted."),
    merge: bool | None = Field(None, alias="Merge", description="When enabled, merges the email body with converted attachments into the final PNG output. Only applies when attachments are being converted."),
) -> dict[str, Any] | ToolResult:
    """Converts an email message (EML format) to PNG image format, with optional support for converting and merging attachments into the output."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertEmlToPngRequest(
            body=_models.PostConvertEmlToPngRequestBody(file_=file_, file_name=file_name, ignore_attachment_errors=ignore_attachment_errors, merge=merge)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_email_to_png: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/eml/to/png"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_email_to_png")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_email_to_png", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_email_to_png",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_eml_to_tiff(
    file_: str | None = Field(None, alias="File", description="The email file to convert. Accepts either a URL reference or raw file content in binary format."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output TIFF file(s). The system automatically sanitizes the filename, appends the correct extension, and adds numeric indexing (e.g., `document_0.tiff`, `document_1.tiff`) when multiple files are generated."),
    ignore_attachment_errors: bool | None = Field(None, alias="IgnoreAttachmentErrors", description="When enabled, attachment conversion errors are ignored and the email body is still converted to TIFF. Only applies when attachments are being converted."),
    merge: bool | None = Field(None, alias="Merge", description="When enabled, merges the email body with converted attachments into the output TIFF file(s). Only applies when attachments are being converted."),
    multi_page: bool | None = Field(None, alias="MultiPage", description="When enabled, creates a single multi-page TIFF file containing all content. When disabled, generates separate TIFF files for each page."),
) -> dict[str, Any] | ToolResult:
    """Converts email messages (EML format) to TIFF image files, with optional support for merging email body with attachments into a single or multi-page document."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertEmlToTiffRequest(
            body=_models.PostConvertEmlToTiffRequestBody(file_=file_, file_name=file_name, ignore_attachment_errors=ignore_attachment_errors, merge=merge, multi_page=multi_page)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_eml_to_tiff: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/eml/to/tiff"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_eml_to_tiff")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_eml_to_tiff", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_eml_to_tiff",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_eml_to_webp(
    file_: str | None = Field(None, alias="File", description="The EML file to convert, provided as either a URL or raw file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output WebP file(s). The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.webp, output_1.webp) for multiple files."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Whether to maintain the original aspect ratio when scaling the output image."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Whether to apply scaling only when the input image dimensions exceed the output dimensions."),
) -> dict[str, Any] | ToolResult:
    """Converts an EML (email) file to WebP image format. Supports URL or file content input with optional scaling and proportional constraint controls."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertEmlToWebpRequest(
            body=_models.PostConvertEmlToWebpRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_eml_to_webp: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/eml/to/webp"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_eml_to_webp")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_eml_to_webp", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_eml_to_webp",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_eps_to_jpg(
    file_: str | None = Field(None, alias="File", description="The EPS file to convert, provided either as a URL or raw binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output JPG file. The API automatically sanitizes the filename, appends the correct .jpg extension, and adds numeric indexing (e.g., output_0.jpg, output_1.jpg) when multiple files are generated from a single input."),
) -> dict[str, Any] | ToolResult:
    """Converts an EPS (Encapsulated PostScript) file to JPG format. Accepts file input as a URL or binary content and generates a converted JPG output file with automatic naming."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertEpsToJpgRequest(
            body=_models.PostConvertEpsToJpgRequestBody(file_=file_, file_name=file_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_eps_to_jpg: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/eps/to/jpg"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_eps_to_jpg")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_eps_to_jpg", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_eps_to_jpg",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_eps_to_pdf(
    file_: str | None = Field(None, alias="File", description="The EPS file to convert. Provide either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output PDF file. The system sanitizes the filename, appends the correct extension, and adds indexing for multiple output files (e.g., report_0.pdf, report_1.pdf)."),
    pdf_version: Literal["1.2", "1.3", "1.4", "1.5", "1.6", "1.7", "1.8", "2.0"] | None = Field(None, alias="PdfVersion", description="PDF specification version to use for the output document."),
    pdf_resolution: int | None = Field(None, alias="PdfResolution", description="Output resolution in dots per inch (DPI). Higher values produce better quality but larger file sizes.", ge=10, le=2400),
    pdf_title: str | None = Field(None, alias="PdfTitle", description="Custom title for the PDF document metadata. Use a single quote and space (' ') to remove the title entirely."),
    pdf_subject: str | None = Field(None, alias="PdfSubject", description="Custom subject for the PDF document metadata. Use a single quote and space (' ') to remove the subject entirely."),
    pdf_author: str | None = Field(None, alias="PdfAuthor", description="Custom author name for the PDF document metadata. Use a single quote and space (' ') to remove the author entirely."),
    pdf_keywords: str | None = Field(None, alias="PdfKeywords", description="Custom keywords for the PDF document metadata, typically used for searchability. Use a single quote and space (' ') to remove keywords entirely."),
    open_page: int | None = Field(None, alias="OpenPage", description="Page number where the PDF should open when first displayed in a viewer.", ge=1, le=3000),
    open_zoom: Literal["Default", "ActualSize", "FitPage", "FitWidth", "FitHeight", "FitVisible", "25", "50", "75", "100", "125", "150", "200", "400", "800", "1600", "2400", "3200", "6400"] | None = Field(None, alias="OpenZoom", description="Default zoom level when opening the PDF in a viewer. Choose from preset percentages or fit-to-page options."),
    color_space: Literal["Default", "RGB", "CMYK", "Gray"] | None = Field(None, alias="ColorSpace", description="Color space for the PDF output. RGB is suitable for screen viewing, CMYK for professional printing, and Gray for grayscale documents."),
) -> dict[str, Any] | ToolResult:
    """Convert EPS (Encapsulated PostScript) files to PDF format with customizable output properties including resolution, metadata, and viewer settings."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertEpsToPdfRequest(
            body=_models.PostConvertEpsToPdfRequestBody(file_=file_, file_name=file_name, pdf_version=pdf_version, pdf_resolution=pdf_resolution, pdf_title=pdf_title, pdf_subject=pdf_subject, pdf_author=pdf_author, pdf_keywords=pdf_keywords, open_page=open_page, open_zoom=open_zoom, color_space=color_space)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_eps_to_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/eps/to/pdf"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_eps_to_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_eps_to_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_eps_to_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_eps_to_png(
    file_: str | None = Field(None, alias="File", description="The EPS file to convert, provided either as a URL or as binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Custom name for the output PNG file. The API automatically sanitizes the filename, appends the correct .png extension, and adds numeric indexing (e.g., output_0.png, output_1.png) when multiple files are generated from a single input."),
) -> dict[str, Any] | ToolResult:
    """Converts an EPS (Encapsulated PostScript) file to PNG format. Accepts file input as a URL or binary file content and generates a PNG output file with optional custom naming."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertEpsToPngRequest(
            body=_models.PostConvertEpsToPngRequestBody(file_=file_, file_name=file_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_eps_to_png: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/eps/to/png"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_eps_to_png")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_eps_to_png", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_eps_to_png",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_eps_to_tiff(
    file_: str | None = Field(None, alias="File", description="The EPS file to convert, provided either as a URL reference or raw binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output TIFF file. The system automatically sanitizes the filename, appends the correct .tiff extension, and adds numeric indexing (e.g., output_0.tiff, output_1.tiff) when multiple files are generated from a single input."),
) -> dict[str, Any] | ToolResult:
    """Converts an EPS (Encapsulated PostScript) file to TIFF (Tagged Image File Format) image format. Accepts file input as a URL or binary content and generates a properly named output file."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertEpsToTiffRequest(
            body=_models.PostConvertEpsToTiffRequestBody(file_=file_, file_name=file_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_eps_to_tiff: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/eps/to/tiff"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_eps_to_tiff")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_eps_to_tiff", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_eps_to_tiff",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_epub_to_jpg(
    file_: str | None = Field(None, alias="File", description="The EPUB file to convert. Accepts either a URL or raw file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output file(s). The system automatically sanitizes the filename, appends the correct extension, and adds numeric indices for multiple outputs (e.g., report_0.jpg, report_1.jpg)."),
    jpg_type: Literal["jpeg", "jpegcmyk", "jpeggray"] | None = Field(None, alias="JpgType", description="Color mode for the output JPG image. Choose between standard RGB (jpeg), CMYK for print (jpegcmyk), or grayscale (jpeggray)."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain aspect ratio when scaling the output image to specified dimensions."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Apply scaling only when the input image dimensions exceed the target output size, preventing upscaling of smaller images."),
) -> dict[str, Any] | ToolResult:
    """Convert EPUB documents to JPG image format with configurable output settings. Supports multiple JPG color modes and optional image scaling to optimize file size and dimensions."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertEpubToJpgRequest(
            body=_models.PostConvertEpubToJpgRequestBody(file_=file_, file_name=file_name, jpg_type=jpg_type, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_epub_to_jpg: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/epub/to/jpg"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_epub_to_jpg")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_epub_to_jpg", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_epub_to_jpg",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_epub_to_pdf(
    file_: str | None = Field(None, alias="File", description="The EPUB file to convert. Accepts either a direct file upload or a URL pointing to the EPUB file."),
    file_name: str | None = Field(None, alias="FileName", description="Custom name for the output PDF file. The system automatically sanitizes the filename, appends the .pdf extension, and adds numeric suffixes if multiple files are generated."),
    base_font_size: float | None = Field(None, alias="BaseFontSize", description="Base font size in points (pt) for the PDF. All text scales relative to this value.", ge=1, le=50),
    margin_left: float | None = Field(None, alias="MarginLeft", description="Left margin width in points (pt) for the PDF page content.", ge=0, le=200),
    margin_right: float | None = Field(None, alias="MarginRight", description="Right margin width in points (pt) for the PDF page content.", ge=0, le=200),
    margin_top: float | None = Field(None, alias="MarginTop", description="Top margin width in points (pt) for the PDF page content.", ge=0, le=200),
    margin_bottom: float | None = Field(None, alias="MarginBottom", description="Bottom margin width in points (pt) for the PDF page content.", ge=0, le=200),
) -> dict[str, Any] | ToolResult:
    """Converts an EPUB file to PDF format with customizable typography and page layout settings. Supports both file uploads and URL-based sources with options to control font sizing and margins."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertEpubToPdfRequest(
            body=_models.PostConvertEpubToPdfRequestBody(file_=file_, file_name=file_name, base_font_size=base_font_size, margin_left=margin_left, margin_right=margin_right, margin_top=margin_top, margin_bottom=margin_bottom)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_epub_to_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/epub/to/pdf"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_epub_to_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_epub_to_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_epub_to_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_epub_to_png(
    file_: str | None = Field(None, alias="File", description="The EPUB file to convert. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output PNG file(s). The system automatically sanitizes the filename, appends the correct extension, and adds numeric indexing (e.g., output_0.png, output_1.png) when multiple files are generated from a single input."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain aspect ratio when scaling the output image to the target dimensions."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the target output dimensions."),
) -> dict[str, Any] | ToolResult:
    """Convert EPUB documents to PNG image format. Supports URL or file content input with optional scaling and proportional constraint controls."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertEpubToPngRequest(
            body=_models.PostConvertEpubToPngRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_epub_to_png: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/epub/to/png"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_epub_to_png")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_epub_to_png", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_epub_to_png",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_epub_to_tiff(
    file_: str | None = Field(None, alias="File", description="The EPUB file to convert. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output TIFF file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.tiff, output_1.tiff) for multi-page conversions."),
    tiff_type: Literal["color24nc", "color32nc", "color24lzw", "color32lzw", "color24zip", "color32zip", "grayscale", "grayscalelzw", "grayscalezip", "monochromeg3", "monochromeg32d", "monochromeg4", "monochromelzw", "monochromepackbits"] | None = Field(None, alias="TiffType", description="TIFF compression and color format. Choose between color variants (24-bit or 32-bit with no compression, LZW, or ZIP), grayscale options, or monochrome formats with various compression methods."),
    multi_page: bool | None = Field(None, alias="MultiPage", description="Generate a single multi-page TIFF file containing all pages, or separate TIFF files for each page."),
    fill_order: Literal["0", "1"] | None = Field(None, alias="FillOrder", description="Bit order within each byte: 0 for most significant bit first (MSB), 1 for least significant bit first (LSB)."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain aspect ratio when scaling the output image to fit specified dimensions."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Apply scaling only when the input image dimensions exceed the target output dimensions, leaving smaller images unchanged."),
) -> dict[str, Any] | ToolResult:
    """Convert EPUB documents to TIFF image format with configurable output settings including multi-page support, compression type, and scaling options."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertEpubToTiffRequest(
            body=_models.PostConvertEpubToTiffRequestBody(file_=file_, file_name=file_name, tiff_type=tiff_type, multi_page=multi_page, fill_order=fill_order, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_epub_to_tiff: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/epub/to/tiff"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_epub_to_tiff")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_epub_to_tiff", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_epub_to_tiff",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_epub_to_webp(
    file_: str | None = Field(None, alias="File", description="The EPUB file to convert. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output file(s). The API sanitizes the filename, appends the correct extension automatically, and adds indexing (e.g., output_0.webp, output_1.webp) for multiple files from a single input."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain aspect ratio when scaling the output image to the target dimensions."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the target output dimensions."),
) -> dict[str, Any] | ToolResult:
    """Convert EPUB documents to WebP image format. Supports URL or file content input with optional scaling and proportional constraint controls."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertEpubToWebpRequest(
            body=_models.PostConvertEpubToWebpRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_epub_to_webp: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/epub/to/webp"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_epub_to_webp")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_epub_to_webp", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_epub_to_webp",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_file_to_pdf(
    file_: str | None = Field(None, alias="File", description="The file to convert, provided either as a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output PDF file. The API automatically sanitizes the filename, appends the .pdf extension, and adds numeric indexing (e.g., filename_0.pdf, filename_1.pdf) when multiple output files are generated from a single input."),
) -> dict[str, Any] | ToolResult:
    """Converts a file to PDF format from a provided file or URL. Supports various input formats and generates uniquely named output files with automatic extension handling."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertFileToPdfRequest(
            body=_models.PostConvertFileToPdfRequestBody(file_=file_, file_name=file_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_file_to_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/file/to/pdf"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_file_to_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_file_to_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_file_to_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def compress_files_to_archive(
    files: list[str] | None = Field(None, alias="Files", description="Files to compress into the archive. Each file can be provided as a URL or raw file content. When using query or multipart parameters, append an index suffix to each file parameter (e.g., Files[0], Files[1])."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output ZIP archive file. The system automatically sanitizes the filename to remove unsafe characters and appends the .zip extension. For multiple input files, output files are automatically indexed (e.g., archive_0.zip, archive_1.zip)."),
    compression_level: Literal["Optimal", "Medium", "Fastest", "NoCompression"] | None = Field(None, alias="CompressionLevel", description="Compression algorithm intensity for the archive. Controls the trade-off between file size and compression speed."),
    password: str | None = Field(None, alias="Password", description="Optional password to encrypt and protect the ZIP archive. When set, the archive requires this password to extract."),
) -> dict[str, Any] | ToolResult:
    """Converts and compresses multiple files into a single ZIP archive with optional password protection. Supports files provided as URLs or direct content."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertFileToZipRequest(
            body=_models.PostConvertFileToZipRequestBody(files=files, file_name=file_name, compression_level=compression_level, password=password)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for compress_files_to_archive: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/file/to/zip"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("compress_files_to_archive")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("compress_files_to_archive", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="compress_files_to_archive",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["Files"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_gif_animation(
    files: list[str] | None = Field(None, alias="Files", description="GIF files to convert. Accepts URLs or file content. When using query or multipart parameters, append an index suffix (e.g., Files[0], Files[1]) to distinguish multiple files."),
    file_name: str | None = Field(None, alias="FileName", description="Custom name for the output file(s). The API sanitizes the filename, appends the appropriate extension, and automatically indexes multiple outputs (e.g., output_0.gif, output_1.gif) to ensure unique identifiers."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain aspect ratio when scaling the output image."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the target output dimensions."),
    animation_delay: int | None = Field(None, alias="AnimationDelay", description="Time interval between animation frames, specified in hundredths of a second. Controls playback speed of the GIF animation.", ge=0, le=20000),
    animation_iterations: int | None = Field(None, alias="AnimationIterations", description="Number of times the animation loops. Set to zero for infinite looping.", ge=0, le=1000),
) -> dict[str, Any] | ToolResult:
    """Convert GIF files with customizable animation settings including frame delay and loop iterations. Supports URL or file content input with optional output filename specification."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertGifToGifRequest(
            body=_models.PostConvertGifToGifRequestBody(files=files, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, animation_delay=animation_delay, animation_iterations=animation_iterations)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_gif_animation: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/gif/to/gif"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_gif_animation")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_gif_animation", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_gif_animation",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["Files"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_gif_to_jpg(
    file_: str | None = Field(None, alias="File", description="The GIF image file to convert. Accepts either a file upload or a URL pointing to the source image."),
    file_name: str | None = Field(None, alias="FileName", description="Custom name for the output JPG file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing for multiple outputs to ensure unique, safe file naming."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain the original aspect ratio when resizing the output image."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Only resize the image if the input dimensions exceed the target output dimensions."),
    alpha_color: str | None = Field(None, alias="AlphaColor", description="Replace transparent areas with a solid color. Accepts RGBA or CMYK hex color codes, or standard color names."),
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(None, alias="ColorSpace", description="Define the color space for the output image."),
) -> dict[str, Any] | ToolResult:
    """Convert GIF images to JPG format with optional scaling, color space adjustment, and transparency handling. Supports both file uploads and URL-based inputs."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertGifToJpgRequest(
            body=_models.PostConvertGifToJpgRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, alpha_color=alpha_color, color_space=color_space)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_gif_to_jpg: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/gif/to/jpg"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_gif_to_jpg")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_gif_to_jpg", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_gif_to_jpg",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_gif_to_pdf(
    file_: str | None = Field(None, alias="File", description="The GIF image file to convert. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.pdf, output_1.pdf) for multiple files."),
    rotate: int | None = Field(None, alias="Rotate", description="Rotation angle in degrees for the output image. Use a value between -360 and 360, or leave empty to apply automatic rotation based on EXIF data if available.", ge=-360, le=360),
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(None, alias="ColorSpace", description="Color space for the output PDF. Defines how colors are represented in the converted document."),
    color_profile: Literal["default", "isocoatedv2"] | None = Field(None, alias="ColorProfile", description="Color profile for the output PDF. Some profiles override the ColorSpace setting. Use 'isocoatedv2' for ISO Coated v2 profile compliance."),
    pdfa: bool | None = Field(None, alias="Pdfa", description="Enable PDF/A-1b compliance for long-term archival and preservation of the output PDF document."),
    margin: str | None = Field(None, alias="Margin", description="Page margins in millimeters as 'horizontal,vertical' (e.g., '10,15')"),
) -> dict[str, Any] | ToolResult:
    """Convert GIF images to PDF format with support for rotation, color space configuration, and PDF/A compliance. Handles single or multiple image conversions with automatic file naming."""

    # Call helper functions
    margin_parsed = parse_margin(margin)

    # Construct request model with validation
    try:
        _request = _models.PostConvertGifToPdfRequest(
            body=_models.PostConvertGifToPdfRequestBody(file_=file_, file_name=file_name, rotate=rotate, color_space=color_space, color_profile=color_profile, pdfa=pdfa, margin_horizontal=margin_parsed.get('MarginHorizontal') if margin_parsed else None, margin_vertical=margin_parsed.get('MarginVertical') if margin_parsed else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_gif_to_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/gif/to/pdf"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_gif_to_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_gif_to_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_gif_to_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_gif_to_png(
    file_: str | None = Field(None, alias="File", description="The GIF image file to convert. Accepts either a URL pointing to the file or the raw file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output PNG file. The system automatically sanitizes the filename, appends the correct .png extension, and adds numeric indexing (e.g., output_0.png, output_1.png) when generating multiple files from a single input."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image to a different size."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Apply scaling only when the input image dimensions exceed the target output dimensions, leaving smaller images unchanged."),
    red: int | None = Field(None, description="Red channel value (0-255)"),
    green: int | None = Field(None, description="Green channel value (0-255)"),
    blue: int | None = Field(None, description="Blue channel value (0-255)"),
    alpha: int | None = Field(None, description="Alpha channel value (0-255), where 0 is fully transparent and 255 is fully opaque. Optional; if not provided, defaults to 255 (fully opaque)."),
) -> dict[str, Any] | ToolResult:
    """Convert a GIF image to PNG format with optional scaling and proportional constraint controls. Supports both URL-based and direct file content input."""

    # Call helper functions
    transparent_color = build_transparent_color(red, green, blue, alpha)

    # Construct request model with validation
    try:
        _request = _models.PostConvertGifToPngRequest(
            body=_models.PostConvertGifToPngRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, transparent_color=transparent_color)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_gif_to_png: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/gif/to/png"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_gif_to_png")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_gif_to_png", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_gif_to_png",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_gif_to_pnm(
    file_: str | None = Field(None, alias="File", description="The GIF image file to convert. Accepts either a URL reference or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output PNM file. The system automatically sanitizes the filename, appends the correct .pnm extension, and adds numeric indexing (e.g., output_0.pnm, output_1.pnm) if multiple files are generated."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image to the target dimensions."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Apply scaling only when the input image dimensions exceed the target output size, leaving smaller images unchanged."),
    red: int | None = Field(None, description="Red channel value (0-255)"),
    green: int | None = Field(None, description="Green channel value (0-255)"),
    blue: int | None = Field(None, description="Blue channel value (0-255)"),
    alpha: int | None = Field(None, description="Alpha channel value (0-255), where 0 is fully transparent and 255 is fully opaque. Optional; if not provided, defaults to 255 (fully opaque)."),
) -> dict[str, Any] | ToolResult:
    """Convert a GIF image file to PNM (Portable Anymap) format with optional scaling and proportion constraints. Supports both URL-based and direct file content input."""

    # Call helper functions
    transparent_color = build_transparent_color(red, green, blue, alpha)

    # Construct request model with validation
    try:
        _request = _models.PostConvertGifToPnmRequest(
            body=_models.PostConvertGifToPnmRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, transparent_color=transparent_color)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_gif_to_pnm: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/gif/to/pnm"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_gif_to_pnm")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_gif_to_pnm", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_gif_to_pnm",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_gif_to_svg(
    file_: str | None = Field(None, alias="File", description="The GIF file to convert. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the generated SVG output file. The system automatically sanitizes the filename, appends the correct .svg extension, and adds numeric indexing if multiple files are produced."),
    preset: Literal["none", "detailed", "crisp", "graphic", "illustration", "noisyScan"] | None = Field(None, alias="Preset", description="Vectorization preset that applies pre-configured tracing settings optimized for different image types. When selected, presets override all other converter options except ColorMode."),
    color_mode: Literal["color", "bw"] | None = Field(None, alias="ColorMode", description="Output color mode for the traced SVG. Choose between full color or black-and-white vectorization."),
    layering: Literal["cutout", "stacked"] | None = Field(None, alias="Layering", description="Arrangement method for color regions in the output SVG. Cutout mode creates isolated layers, while stacked mode overlays regions on top of each other."),
    curve_mode: Literal["pixel", "polygon", "spline"] | None = Field(None, alias="CurveMode", description="Shape approximation method during vectorization. Pixel mode traces exact pixel boundaries with minimal smoothing, Polygon creates straight-edged paths with sharp corners, and Spline generates smooth continuous curves."),
) -> dict[str, Any] | ToolResult:
    """Converts GIF images to scalable vector graphics (SVG) format using configurable vectorization presets and tracing options. Supports both color and black-and-white output with customizable layering and curve approximation modes."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertGifToSvgRequest(
            body=_models.PostConvertGifToSvgRequestBody(file_=file_, file_name=file_name, preset=preset, color_mode=color_mode, layering=layering, curve_mode=curve_mode)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_gif_to_svg: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/gif/to/svg"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_gif_to_svg")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_gif_to_svg", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_gif_to_svg",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_gif_to_tiff(
    file_: str | None = Field(None, alias="File", description="The GIF file to convert. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output TIFF file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.tiff, output_1.tiff) for multiple files."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain aspect ratio when scaling the output image."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the output dimensions."),
    multi_page: bool | None = Field(None, alias="MultiPage", description="Generate a single multi-page TIFF file instead of separate files for each frame."),
) -> dict[str, Any] | ToolResult:
    """Convert GIF images to TIFF format with optional scaling and multi-page support. Supports both URL-based and direct file uploads."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertGifToTiffRequest(
            body=_models.PostConvertGifToTiffRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, multi_page=multi_page)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_gif_to_tiff: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/gif/to/tiff"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_gif_to_tiff")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_gif_to_tiff", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_gif_to_tiff",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_gif_to_webp(
    file_: str | None = Field(None, alias="File", description="The GIF image file to convert. Accepts either a file upload or a URL pointing to the source image."),
    file_name: str | None = Field(None, alias="FileName", description="Custom name for the output WebP file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing for multiple outputs to ensure unique, safe file naming."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the target output size."),
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(None, alias="ColorSpace", description="Define the color space for the output image. Use 'default' to preserve the source color space, or specify a target color space for conversion."),
) -> dict[str, Any] | ToolResult:
    """Convert GIF images to WebP format with optional scaling and color space adjustments. Supports both file uploads and URL-based inputs."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertGifToWebpRequest(
            body=_models.PostConvertGifToWebpRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, color_space=color_space)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_gif_to_webp: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/gif/to/webp"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_gif_to_webp")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_gif_to_webp", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_gif_to_webp",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_heic_to_jpg(
    file_: str | None = Field(None, alias="File", description="The image file to convert. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output JPG file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.jpg, filename_1.jpg) for multiple outputs."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain aspect ratio when scaling the output image."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the output dimensions."),
    alpha_color: str | None = Field(None, alias="AlphaColor", description="Color to apply to transparent areas. Accepts RGBA or CMYK hex strings, or standard color names."),
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(None, alias="ColorSpace", description="Color space for the output image."),
) -> dict[str, Any] | ToolResult:
    """Convert HEIC image files to JPG format with optional scaling and color space adjustments. Supports both URL-based and direct file uploads with customizable output naming and image properties."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertHeicToJpgRequest(
            body=_models.PostConvertHeicToJpgRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, alpha_color=alpha_color, color_space=color_space)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_heic_to_jpg: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/heic/to/jpg"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_heic_to_jpg")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_heic_to_jpg", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_heic_to_jpg",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_image_heic_to_jxl(
    file_: str | None = Field(None, alias="File", description="The image file to convert. Accepts either a file upload or a URL pointing to the source image."),
    file_name: str | None = Field(None, alias="FileName", description="Custom name for the output file. The API automatically sanitizes the name, appends the correct file extension, and adds indexing for multiple output files to ensure unique, safe filenames."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Apply scaling only when the input image dimensions exceed the target output dimensions."),
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(None, alias="ColorSpace", description="Define the color space for the output image. Choose from standard color profiles or use the default setting."),
) -> dict[str, Any] | ToolResult:
    """Convert HEIC image files to JXL (JPEG XL) format with optional scaling and color space adjustments. Supports both file uploads and URL-based inputs."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertHeicToJxlRequest(
            body=_models.PostConvertHeicToJxlRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, color_space=color_space)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_image_heic_to_jxl: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/heic/to/jxl"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_image_heic_to_jxl")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_image_heic_to_jxl", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_image_heic_to_jxl",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_heic_to_pdf(
    file_: str | None = Field(None, alias="File", description="The HEIC image file to convert. Provide either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing for multiple output files to ensure unique, safe file naming."),
    rotate: int | None = Field(None, alias="Rotate", description="Rotate the output image by the specified degrees. Leave empty to use automatic rotation based on EXIF data if available.", ge=-360, le=360),
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(None, alias="ColorSpace", description="Set the color space for the output PDF. Choose from standard color space options or use default for automatic selection."),
    color_profile: Literal["default", "isocoatedv2"] | None = Field(None, alias="ColorProfile", description="Apply a specific color profile to the output PDF. Some profiles may override the ColorSpace setting."),
    pdfa: bool | None = Field(None, alias="Pdfa", description="Generate a PDF/A-1b compliant document for long-term archival and preservation."),
    margin: str | None = Field(None, alias="Margin", description="Page margins in millimeters as 'horizontal,vertical' (e.g., '10,20')"),
) -> dict[str, Any] | ToolResult:
    """Convert HEIC image files to PDF format with support for rotation, color space configuration, and PDF/A compliance. Accepts file input via URL or direct file content."""

    # Call helper functions
    margin_parsed = parse_margin(margin)

    # Construct request model with validation
    try:
        _request = _models.PostConvertHeicToPdfRequest(
            body=_models.PostConvertHeicToPdfRequestBody(file_=file_, file_name=file_name, rotate=rotate, color_space=color_space, color_profile=color_profile, pdfa=pdfa, margin_horizontal=margin_parsed.get('MarginHorizontal') if margin_parsed else None, margin_vertical=margin_parsed.get('MarginVertical') if margin_parsed else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_heic_to_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/heic/to/pdf"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_heic_to_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_heic_to_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_heic_to_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_heic_to_png(
    file_: str | None = Field(None, alias="File", description="The image file to convert, provided either as a URL or raw file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output PNG file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., image_0.png, image_1.png) for multiple outputs from a single input."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Whether to maintain the original aspect ratio when scaling the output image."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Whether to apply scaling only when the input image dimensions exceed the target output dimensions."),
    red: int | None = Field(None, description="Red channel value (0-255)"),
    green: int | None = Field(None, description="Green channel value (0-255)"),
    blue: int | None = Field(None, description="Blue channel value (0-255)"),
    alpha: int | None = Field(None, description="Alpha channel value (0-255), where 0 is fully transparent and 255 is fully opaque. Optional; if not provided, defaults to 255 (fully opaque)."),
) -> dict[str, Any] | ToolResult:
    """Convert HEIC image files to PNG format with optional scaling and proportional constraints. Supports both URL-based and direct file content input."""

    # Call helper functions
    transparent_color = build_transparent_color(red, green, blue, alpha)

    # Construct request model with validation
    try:
        _request = _models.PostConvertHeicToPngRequest(
            body=_models.PostConvertHeicToPngRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, transparent_color=transparent_color)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_heic_to_png: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/heic/to/png"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_heic_to_png")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_heic_to_png", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_heic_to_png",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_image_heic_to_pnm(
    file_: str | None = Field(None, alias="File", description="The image file to convert. Accepts either a URL reference or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output file. The API automatically sanitizes the filename, appends the correct .pnm extension, and adds numeric indexing (e.g., output_0.pnm, output_1.pnm) when multiple files are generated."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image to the target dimensions."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Apply scaling only when the input image dimensions exceed the target output dimensions, leaving smaller images unchanged."),
    red: int | None = Field(None, description="Red channel value (0-255)"),
    green: int | None = Field(None, description="Green channel value (0-255)"),
    blue: int | None = Field(None, description="Blue channel value (0-255)"),
    alpha: int | None = Field(None, description="Alpha channel value (0-255), where 0 is fully transparent and 255 is fully opaque. Optional; if not provided, defaults to 255 (fully opaque)."),
) -> dict[str, Any] | ToolResult:
    """Convert HEIC image files to PNM (Portable Anymap) format with optional scaling and proportional constraint controls."""

    # Call helper functions
    transparent_color = build_transparent_color(red, green, blue, alpha)

    # Construct request model with validation
    try:
        _request = _models.PostConvertHeicToPnmRequest(
            body=_models.PostConvertHeicToPnmRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, transparent_color=transparent_color)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_image_heic_to_pnm: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/heic/to/pnm"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_image_heic_to_pnm")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_image_heic_to_pnm", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_image_heic_to_pnm",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_heic_to_svg(
    file_: str | None = Field(None, alias="File", description="The HEIC image file to convert. Accepts either a URL pointing to the image or the raw file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output SVG file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., image_0.svg, image_1.svg) for multiple outputs."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain aspect ratio when scaling the output image to fit specified dimensions."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the target output dimensions."),
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(None, alias="ColorSpace", description="Define the color space for the output SVG image."),
) -> dict[str, Any] | ToolResult:
    """Convert HEIC image files to SVG vector format. Supports URL or direct file content input with optional scaling and color space configuration."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertHeicToSvgRequest(
            body=_models.PostConvertHeicToSvgRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, color_space=color_space)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_heic_to_svg: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/heic/to/svg"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_heic_to_svg")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_heic_to_svg", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_heic_to_svg",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_heic_to_tiff(
    file_: str | None = Field(None, alias="File", description="The image file to convert. Accepts either a URL pointing to the file or the raw file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output TIFF file(s). The system automatically sanitizes the name, appends the correct extension, and adds indexing (e.g., filename_0.tiff, filename_1.tiff) for multiple output files."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the target output dimensions."),
    multi_page: bool | None = Field(None, alias="MultiPage", description="Generate a multi-page TIFF file when converting. If disabled, creates a single-page TIFF."),
) -> dict[str, Any] | ToolResult:
    """Convert HEIC image files to TIFF format with optional scaling and multi-page support. Supports both URL-based and direct file uploads."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertHeicToTiffRequest(
            body=_models.PostConvertHeicToTiffRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, multi_page=multi_page)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_heic_to_tiff: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/heic/to/tiff"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_heic_to_tiff")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_heic_to_tiff", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_heic_to_tiff",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_image_heic_to_webp(
    file_: str | None = Field(None, alias="File", description="The image file to convert. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing for multiple outputs (e.g., image_0.webp, image_1.webp)."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain aspect ratio when scaling the output image."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the output dimensions."),
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(None, alias="ColorSpace", description="Define the color space for the output image."),
) -> dict[str, Any] | ToolResult:
    """Convert HEIC image files to WebP format with optional scaling and color space adjustments. Supports both file uploads and URL-based inputs."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertHeicToWebpRequest(
            body=_models.PostConvertHeicToWebpRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, color_space=color_space)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_image_heic_to_webp: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/heic/to/webp"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_image_heic_to_webp")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_image_heic_to_webp", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_image_heic_to_webp",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_heif_to_jpg(
    file_: str | None = Field(None, alias="File", description="The image file to convert. Accepts either a URL reference or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output JPG file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., image_0.jpg, image_1.jpg) for multiple outputs from a single input."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the target output size."),
    alpha_color: str | None = Field(None, alias="AlphaColor", description="Specify a color to replace transparent areas in the image. Accepts RGBA or CMYK hex color codes, or standard color names."),
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(None, alias="ColorSpace", description="Define the color space for the output image."),
) -> dict[str, Any] | ToolResult:
    """Convert HEIF image files to JPG format with optional scaling and color space adjustments. Supports both URL and direct file content input."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertHeifToJpgRequest(
            body=_models.PostConvertHeifToJpgRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, alpha_color=alpha_color, color_space=color_space)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_heif_to_jpg: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/heif/to/jpg"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_heif_to_jpg")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_heif_to_jpg", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_heif_to_jpg",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_heif_to_pdf(
    file_: str | None = Field(None, alias="File", description="The HEIF image file to convert. Provide either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output PDF file. The system automatically sanitizes the filename, appends the .pdf extension, and adds numeric indexing (e.g., output_0.pdf, output_1.pdf) when multiple files are generated."),
    rotate: int | None = Field(None, alias="Rotate", description="Rotation angle in degrees for the output image. Specify a value between -360 and 360, or leave empty to automatically rotate based on EXIF data in TIFF and JPEG images.", ge=-360, le=360),
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(None, alias="ColorSpace", description="Color space for the output PDF. Choose from standard color spaces or use the default setting."),
    color_profile: Literal["default", "isocoatedv2"] | None = Field(None, alias="ColorProfile", description="Color profile to apply to the output PDF. Some profiles may override the ColorSpace setting."),
    pdfa: bool | None = Field(None, alias="Pdfa", description="Enable PDF/A-1b compliance for the output document, ensuring long-term archival compatibility."),
    margin: str | None = Field(None, alias="Margin", description="Page margins in millimeters as 'horizontal,vertical' (e.g., '10,20')"),
) -> dict[str, Any] | ToolResult:
    """Convert HEIF image files to PDF format with support for rotation, color space configuration, and PDF/A compliance. Accepts file input as URL or binary content and generates a properly named output PDF file."""

    # Call helper functions
    margin_parsed = parse_margin(margin)

    # Construct request model with validation
    try:
        _request = _models.PostConvertHeifToPdfRequest(
            body=_models.PostConvertHeifToPdfRequestBody(file_=file_, file_name=file_name, rotate=rotate, color_space=color_space, color_profile=color_profile, pdfa=pdfa, margin_horizontal=margin_parsed.get('MarginHorizontal') if margin_parsed else None, margin_vertical=margin_parsed.get('MarginVertical') if margin_parsed else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_heif_to_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/heif/to/pdf"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_heif_to_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_heif_to_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_heif_to_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_html_to_docx(
    file_: str | None = Field(None, alias="File", description="The HTML content to convert, provided either as a publicly accessible URL or as raw file content in binary format."),
    file_name: str | None = Field(None, alias="FileName", description="The desired name for the output DOCX file. The API automatically sanitizes the filename, appends the correct .docx extension, and adds numeric suffixes (e.g., _0, _1) if multiple files are generated from a single input."),
    margins: str | None = Field(None, alias="Margins", description="Page margins in inches as 'horizontal,vertical' (e.g., '0.5,0.75')"),
) -> dict[str, Any] | ToolResult:
    """Converts HTML content to DOCX format. Accepts HTML as a URL or raw file content and generates a properly formatted Word document with the specified output filename."""

    # Call helper functions
    margins_parsed = parse_margins(margins)

    # Construct request model with validation
    try:
        _request = _models.PostConvertHtmlToDocxRequest(
            body=_models.PostConvertHtmlToDocxRequestBody(file_=file_, file_name=file_name, margin_horizontal=margins_parsed.get('MarginHorizontal') if margins_parsed else None, margin_vertical=margins_parsed.get('MarginVertical') if margins_parsed else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_html_to_docx: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/html/to/docx"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_html_to_docx")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_html_to_docx", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_html_to_docx",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_html_to_jpg(
    file_name: str | None = Field(None, alias="FileName", description="Name for the output JPG file(s). The system sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.jpg, output_1.jpg) for multiple files to ensure unique identification."),
    ad_block: bool | None = Field(None, alias="AdBlock", description="Block advertisements from appearing in the converted page."),
    cookie_consent_block: bool | None = Field(None, alias="CookieConsentBlock", description="Automatically remove EU cookie consent warnings and related cookie banners from web pages before conversion."),
    cookies: str | None = Field(None, alias="Cookies", description="Set additional cookies to include in the page request. Separate multiple cookies with semicolons."),
    java_script: bool | None = Field(None, alias="JavaScript", description="Enable JavaScript execution during page rendering. When enabled, scripts will run before conversion begins."),
    wait_element: str | None = Field(None, alias="WaitElement", description="CSS selector for a DOM element. The converter will wait for this element to appear in the DOM before starting the conversion process."),
    user_css: str | None = Field(None, alias="UserCss", description="Custom CSS rules to apply to the page before conversion. These styles are injected into the page rendering context."),
    css_media_type: str | None = Field(None, alias="CssMediaType", description="CSS media type to use during conversion. Supports standard types (screen, print) and custom media types."),
    headers: str | None = Field(None, alias="Headers", description="Custom HTTP headers to include in the page request. Separate multiple headers with pipe characters (|) and use colon (:) to separate header names from values."),
    zoom: float | None = Field(None, alias="Zoom", description="Set the default zoom level for webpage rendering. Values between 0.1 and 10 are supported.", ge=0.1, le=10),
    file_: str | None = Field(None, alias="File", description="The HTML content or URL to convert. Accepts either a web URL or raw HTML file content."),
) -> dict[str, Any] | ToolResult:
    """Convert HTML content or web pages to JPG image format. Supports URL-based or direct HTML content conversion with advanced rendering options including JavaScript execution, CSS customization, and DOM element waiting."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertHtmlToJpgRequest(
            body=_models.PostConvertHtmlToJpgRequestBody(file_name=file_name, ad_block=ad_block, cookie_consent_block=cookie_consent_block, cookies=cookies, java_script=java_script, wait_element=wait_element, user_css=user_css, css_media_type=css_media_type, headers=headers, zoom=zoom, file_=file_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_html_to_jpg: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/html/to/jpg"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_html_to_jpg")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_html_to_jpg", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_html_to_jpg",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_html_to_markdown(
    file_: str | None = Field(None, alias="File", description="The HTML content to convert. Provide either a URL pointing to an HTML file or the raw HTML content as a string."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the generated Markdown output file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing for multiple outputs to ensure unique, safe file naming."),
    github_flavored: bool | None = Field(None, alias="GithubFlavored", description="Enable GitHub-flavored Markdown (GFM) syntax in the output for enhanced compatibility with GitHub platforms."),
    remove_comments: bool | None = Field(None, alias="RemoveComments", description="Remove HTML comment tags from the output Markdown document."),
    unsupported_tags: Literal["PassThrough", "Drop", "Bypass", "Fail"] | None = Field(None, alias="UnsupportedTags", description="Define how to handle HTML tags that are not supported in Markdown conversion. Choose to pass through as-is, drop entirely, bypass processing, or fail on unsupported tags."),
    pass_through_tags: str | None = Field(None, alias="PassThroughTags", description="Specify HTML tags to pass through unchanged to the Markdown output. Provide tag names as a comma-separated list. Only applies when UnsupportedTags is set to PassThrough."),
    list_bullet_char: str | None = Field(None, alias="ListBulletChar", description="Set the character used for bullet points in unordered lists within the Markdown output."),
) -> dict[str, Any] | ToolResult:
    """Convert HTML content or files to Markdown format with customizable formatting options including GitHub-flavored markdown support and tag handling rules."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertHtmlToMdRequest(
            body=_models.PostConvertHtmlToMdRequestBody(file_=file_, file_name=file_name, github_flavored=github_flavored, remove_comments=remove_comments, unsupported_tags=unsupported_tags, pass_through_tags=pass_through_tags, list_bullet_char=list_bullet_char)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_html_to_markdown: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/html/to/md"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_html_to_markdown")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_html_to_markdown", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_html_to_markdown",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_html_to_pdf(
    file_name: str | None = Field(None, alias="FileName", description="Name for the generated PDF output file. The system sanitizes the filename, appends the .pdf extension automatically, and adds numeric suffixes (e.g., report_0.pdf, report_1.pdf) when multiple files are generated."),
    ad_block: bool | None = Field(None, alias="AdBlock", description="Block advertisements from appearing in the converted PDF."),
    cookie_consent_block: bool | None = Field(None, alias="CookieConsentBlock", description="Automatically remove EU cookie consent banners and related warnings from the page before conversion."),
    cookies: str | None = Field(None, alias="Cookies", description="Set additional cookies to include in the page request. Separate multiple cookies with semicolons."),
    java_script: bool | None = Field(None, alias="JavaScript", description="Enable JavaScript execution during page rendering. Disable if the page contains problematic scripts."),
    wait_element: str | None = Field(None, alias="WaitElement", description="CSS selector for a DOM element that must appear before conversion begins. Useful for waiting on dynamically loaded content."),
    user_css: str | None = Field(None, alias="UserCss", description="Custom CSS rules to apply to the page before conversion. Useful for hiding elements or adjusting layout."),
    css_media_type: str | None = Field(None, alias="CssMediaType", description="CSS media type to use during conversion. Controls how stylesheets are applied (e.g., screen, print, or custom types)."),
    headers: str | None = Field(None, alias="Headers", description="Custom HTTP headers to include in the page request. Separate multiple headers with pipe characters and use colon to separate header names from values."),
    load_lazy_content: bool | None = Field(None, alias="LoadLazyContent", description="Load images that are only visible when scrolled into view (lazy-loaded images)."),
    viewport_width: int | None = Field(None, alias="ViewportWidth", description="Browser viewport width in pixels. Affects how the page is rendered and reflowed.", ge=200, le=4000),
    viewport_height: int | None = Field(None, alias="ViewportHeight", description="Browser viewport height in pixels. Affects how the page is rendered and reflowed.", ge=200, le=4000),
    respect_viewport: bool | None = Field(None, alias="RespectViewport", description="If true, the PDF renders as it appears in the browser. If false, uses Chrome's print-to-PDF behavior which may adjust layout."),
    page_range: str | None = Field(None, alias="PageRange", description="Specify which pages to convert using ranges (e.g., 1-10) or individual page numbers (e.g., 1,2,5)."),
    background: bool | None = Field(None, alias="Background", description="Include background colors and images from the page in the PDF output."),
    fixed_elements: Literal["fixed", "absolute", "relative", "hide"] | None = Field(None, alias="FixedElements", description="Change how fixed-position elements are handled during conversion. Use 'hide' to remove them, or change their CSS position property."),
    header: str | None = Field(None, alias="Header", description="HTML content to insert as a header on each page. Use CSS classes pageNumber, totalPages, title, and date for dynamic content injection. Supports inline CSS styling."),
    footer: str | None = Field(None, alias="Footer", description="HTML content to insert as a footer on each page. Use CSS classes pageNumber, totalPages, title, and date for dynamic content injection. Supports inline CSS styling."),
    show_elements: str | None = Field(None, alias="ShowElements", description="CSS selector for DOM elements that should remain visible. All other elements will be hidden during conversion."),
    avoid_break_elements: str | None = Field(None, alias="AvoidBreakElements", description="CSS selector for elements where page breaks should be avoided. Prevents breaking content within these elements."),
    break_before_elements: str | None = Field(None, alias="BreakBeforeElements", description="CSS selector for elements that should trigger a page break before them."),
    break_after_elements: str | None = Field(None, alias="BreakAfterElements", description="CSS selector for elements that should trigger a page break after them."),
    file_: str | None = Field(None, alias="File", description="The HTML content or URL to convert to PDF. Can be a full URL (http/https) or raw HTML file content."),
    margins: str | None = Field(None, alias="Margins", description="Page margins in millimeters as a space-separated string in CSS order: top right bottom left (e.g., '10 5 10 5')"),
) -> dict[str, Any] | ToolResult:
    """Converts HTML content from a URL or file to PDF format with advanced rendering options, including JavaScript execution, custom styling, headers/footers, and page layout control."""

    # Call helper functions
    margins_parsed = parse_margins(margins)

    # Construct request model with validation
    try:
        _request = _models.PostConvertHtmlToPdfRequest(
            body=_models.PostConvertHtmlToPdfRequestBody(file_name=file_name, ad_block=ad_block, cookie_consent_block=cookie_consent_block, cookies=cookies, java_script=java_script, wait_element=wait_element, user_css=user_css, css_media_type=css_media_type, headers=headers, load_lazy_content=load_lazy_content, viewport_width=viewport_width, viewport_height=viewport_height, respect_viewport=respect_viewport, page_range=page_range, background=background, fixed_elements=fixed_elements, header=header, footer=footer, show_elements=show_elements, avoid_break_elements=avoid_break_elements, break_before_elements=break_before_elements, break_after_elements=break_after_elements, file_=file_, margin_top=margins_parsed.get('MarginTop') if margins_parsed else None, margin_right=margins_parsed.get('MarginRight') if margins_parsed else None, margin_bottom=margins_parsed.get('MarginBottom') if margins_parsed else None, margin_left=margins_parsed.get('MarginLeft') if margins_parsed else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_html_to_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/html/to/pdf"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_html_to_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_html_to_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_html_to_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_html_to_png(
    file_name: str | None = Field(None, alias="FileName", description="Name for the output PNG file. The system sanitizes the filename, appends the .png extension automatically, and adds numeric suffixes (e.g., _0, _1) when generating multiple files from a single input."),
    ad_block: bool | None = Field(None, alias="AdBlock", description="Block advertisements from appearing in the converted page."),
    cookie_consent_block: bool | None = Field(None, alias="CookieConsentBlock", description="Automatically remove EU cookie consent banners and related warnings from the page before conversion."),
    cookies: str | None = Field(None, alias="Cookies", description="Set additional cookies to include in the page request. Provide multiple cookies as name-value pairs separated by semicolons."),
    java_script: bool | None = Field(None, alias="JavaScript", description="Enable JavaScript execution on the page during conversion, allowing dynamic content to render."),
    wait_element: str | None = Field(None, alias="WaitElement", description="CSS selector for a DOM element. The converter will wait for this element to appear before starting the conversion, useful for pages with delayed content loading."),
    user_css: str | None = Field(None, alias="UserCss", description="Custom CSS rules to apply to the page before conversion begins."),
    css_media_type: str | None = Field(None, alias="CssMediaType", description="CSS media type to use during conversion. Common values include 'screen' and 'print', but custom media types are also supported."),
    headers: str | None = Field(None, alias="Headers", description="Custom HTTP headers to include in the page request. Provide headers as name-value pairs separated by pipes, with each pair separated by a colon."),
    zoom: float | None = Field(None, alias="Zoom", description="Zoom level for rendering the webpage. Values below 1 zoom out, values above 1 zoom in.", ge=0.1, le=10),
    transparent_background: bool | None = Field(None, alias="TransparentBackground", description="Use a transparent background instead of the default white background. The source HTML body background color must also be set to 'none' for transparency to work."),
    file_: str | None = Field(None, alias="File", description="The HTML content or URL to convert. Provide either a web URL or raw HTML content."),
) -> dict[str, Any] | ToolResult:
    """Converts HTML content or web pages to PNG image format. Supports JavaScript execution, custom styling, cookie handling, and DOM element waiting for dynamic content rendering."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertHtmlToPngRequest(
            body=_models.PostConvertHtmlToPngRequestBody(file_name=file_name, ad_block=ad_block, cookie_consent_block=cookie_consent_block, cookies=cookies, java_script=java_script, wait_element=wait_element, user_css=user_css, css_media_type=css_media_type, headers=headers, zoom=zoom, transparent_background=transparent_background, file_=file_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_html_to_png: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/html/to/png"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_html_to_png")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_html_to_png", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_html_to_png",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_html_to_text(
    file_name: str | None = Field(None, alias="FileName", description="Name for the output text file. The API sanitizes the filename, appends the correct extension, and uses indexing (e.g., output_0.txt, output_1.txt) for multiple files."),
    ad_block: bool | None = Field(None, alias="AdBlock", description="Remove advertisements from the HTML content during conversion."),
    cookie_consent_block: bool | None = Field(None, alias="CookieConsentBlock", description="Automatically remove EU cookie consent banners and related warnings from the page."),
    cookies: str | None = Field(None, alias="Cookies", description="Include additional cookies in the page request. Separate multiple cookies with semicolons."),
    java_script: bool | None = Field(None, alias="JavaScript", description="Enable JavaScript execution on the page during conversion."),
    wait_element: str | None = Field(None, alias="WaitElement", description="CSS selector for a DOM element. The converter will wait for this element to appear before starting the conversion."),
    user_css: str | None = Field(None, alias="UserCss", description="Custom CSS rules to apply to the page before conversion begins."),
    css_media_type: str | None = Field(None, alias="CssMediaType", description="CSS media type to use during conversion (e.g., screen, print, or custom types)."),
    headers: str | None = Field(None, alias="Headers", description="Custom HTTP headers to include in the request. Separate multiple headers with pipes and use colons to delimit header names from values."),
    file_: str | None = Field(None, alias="File", description="HTML content to convert. Provide either a URL or raw HTML file content."),
    extract_elements: str | None = Field(None, alias="ExtractElements", description="CSS selector to extract specific DOM elements instead of converting the entire page. Use class selectors (.classname), ID selectors (#id), or tag names."),
) -> dict[str, Any] | ToolResult:
    """Converts HTML content from a URL or file to plain text format. Supports advanced options like JavaScript execution, element extraction, custom styling, and cookie/ad handling for flexible web content processing."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertHtmlToTxtRequest(
            body=_models.PostConvertHtmlToTxtRequestBody(file_name=file_name, ad_block=ad_block, cookie_consent_block=cookie_consent_block, cookies=cookies, java_script=java_script, wait_element=wait_element, user_css=user_css, css_media_type=css_media_type, headers=headers, file_=file_, extract_elements=extract_elements)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_html_to_text: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/html/to/txt"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_html_to_text")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_html_to_text", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_html_to_text",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_html_to_spreadsheet(
    file_: str | None = Field(None, alias="File", description="The HTML content to convert, provided either as a publicly accessible URL or as raw file content in binary format."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the generated output spreadsheet file. The system automatically sanitizes the filename, appends the correct .xls extension, and adds numeric indexing (e.g., report_0.xls, report_1.xls) if multiple files are generated from a single input."),
) -> dict[str, Any] | ToolResult:
    """Converts HTML content or files to Excel spreadsheet format. Accepts HTML input as a URL or raw file content and generates a formatted XLS output file."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertHtmlToXlsRequest(
            body=_models.PostConvertHtmlToXlsRequestBody(file_=file_, file_name=file_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_html_to_spreadsheet: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/html/to/xls"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_html_to_spreadsheet")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_html_to_spreadsheet", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_html_to_spreadsheet",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_html_to_xlsx(
    file_: str | None = Field(None, alias="File", description="The HTML content to convert, provided either as a publicly accessible URL or as raw file content in binary format."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the generated output Excel file. The system automatically sanitizes the filename, appends the .xlsx extension, and adds numeric suffixes (e.g., _0, _1) if multiple files are generated from a single input."),
) -> dict[str, Any] | ToolResult:
    """Converts HTML content or files to Excel spreadsheet format. Accepts HTML input as a URL or raw file content and generates a formatted XLSX output file."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertHtmlToXlsxRequest(
            body=_models.PostConvertHtmlToXlsxRequestBody(file_=file_, file_name=file_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_html_to_xlsx: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/html/to/xlsx"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_html_to_xlsx")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_html_to_xlsx", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_html_to_xlsx",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_image_ico_to_jpg(
    file_: str | None = Field(None, alias="File", description="The image file to convert. Accepts a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.jpg, output_1.jpg) for multiple files."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain aspect ratio when scaling the output image."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Only scale the image if the input is larger than the desired output dimensions."),
    alpha_color: str | None = Field(None, alias="AlphaColor", description="Replace transparent areas with a specific color. Accepts RGBA or CMYK hex strings, or standard color names."),
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(None, alias="ColorSpace", description="Set the color space for the output image."),
) -> dict[str, Any] | ToolResult:
    """Convert ICO (icon) image files to JPG format with optional scaling, color space adjustment, and alpha channel handling."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertIcoToJpgRequest(
            body=_models.PostConvertIcoToJpgRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, alpha_color=alpha_color, color_space=color_space)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_image_ico_to_jpg: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/ico/to/jpg"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_image_ico_to_jpg")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_image_ico_to_jpg", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_image_ico_to_jpg",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_ico_to_pdf(
    file_: str | None = Field(None, alias="File", description="The ICO image file to convert. Provide either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.pdf, filename_1.pdf) for multiple output files."),
    rotate: int | None = Field(None, alias="Rotate", description="Rotation angle in degrees to apply to the image. For automatic rotation based on EXIF metadata in TIFF and JPEG images, leave empty.", ge=-360, le=360),
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(None, alias="ColorSpace", description="Color space for the output PDF. Defines how colors are represented in the converted document."),
    color_profile: Literal["default", "isocoatedv2"] | None = Field(None, alias="ColorProfile", description="Color profile to apply to the output PDF. Some profiles override the ColorSpace setting."),
    pdfa: bool | None = Field(None, alias="Pdfa", description="Enable PDF/A-1b compliance for the output document, ensuring long-term archival compatibility."),
    margin: str | None = Field(None, alias="Margin", description="Page margins in millimeters as 'horizontal,vertical' (e.g., '10,15')"),
) -> dict[str, Any] | ToolResult:
    """Convert ICO (icon) image files to PDF format with support for rotation, color space configuration, and PDF/A compliance. Accepts file input as URL or binary content and generates a properly named output PDF file."""

    # Call helper functions
    margin_parsed = parse_margin(margin)

    # Construct request model with validation
    try:
        _request = _models.PostConvertIcoToPdfRequest(
            body=_models.PostConvertIcoToPdfRequestBody(file_=file_, file_name=file_name, rotate=rotate, color_space=color_space, color_profile=color_profile, pdfa=pdfa, margin_horizontal=margin_parsed.get('MarginHorizontal') if margin_parsed else None, margin_vertical=margin_parsed.get('MarginVertical') if margin_parsed else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_ico_to_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/ico/to/pdf"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_ico_to_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_ico_to_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_ico_to_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_image_ico_to_png(
    file_: str | None = Field(None, alias="File", description="The image file to convert, provided as either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output PNG file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.png, output_1.png) for multiple files."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Whether to maintain the original aspect ratio when scaling the output image."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Whether to apply scaling only when the input image dimensions exceed the output dimensions."),
    red: int | None = Field(None, description="Red channel value (0-255)"),
    green: int | None = Field(None, description="Green channel value (0-255)"),
    blue: int | None = Field(None, description="Blue channel value (0-255)"),
    alpha: int | None = Field(None, description="Alpha channel value (0-255), where 0 is fully transparent and 255 is fully opaque. Optional; if not provided, defaults to 255 (fully opaque)."),
) -> dict[str, Any] | ToolResult:
    """Convert an ICO (icon) image file to PNG format. Supports URL or file content input with optional scaling and proportional resizing."""

    # Call helper functions
    transparent_color = build_transparent_color(red, green, blue, alpha)

    # Construct request model with validation
    try:
        _request = _models.PostConvertIcoToPngRequest(
            body=_models.PostConvertIcoToPngRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, transparent_color=transparent_color)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_image_ico_to_png: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/ico/to/png"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_image_ico_to_png")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_image_ico_to_png", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_image_ico_to_png",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_icon_to_svg(
    file_: str | None = Field(None, alias="File", description="The ICO file to convert. Accepts either a URL or raw file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output SVG file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing for multiple output files to ensure unique, safe file naming."),
    preset: Literal["none", "detailed", "crisp", "graphic", "illustration", "noisyScan"] | None = Field(None, alias="Preset", description="Vectorization preset that applies pre-configured tracing settings optimized for specific image types. When selected, presets override individual converter options except ColorMode. Use 'none' for custom configuration."),
    color_mode: Literal["color", "bw"] | None = Field(None, alias="ColorMode", description="Color processing mode for tracing. Choose 'color' for full-color output or 'bw' for black-and-white conversion."),
    layering: Literal["cutout", "stacked"] | None = Field(None, alias="Layering", description="Arrangement method for color regions in the output SVG. 'cutout' creates isolated layers, while 'stacked' overlays regions on top of each other."),
    curve_mode: Literal["pixel", "polygon", "spline"] | None = Field(None, alias="CurveMode", description="Shape approximation method during tracing. 'pixel' follows exact pixel boundaries with minimal smoothing, 'polygon' creates straight-edged paths with sharp corners, and 'spline' generates smooth continuous curves."),
) -> dict[str, Any] | ToolResult:
    """Converts ICO (icon) files to SVG (Scalable Vector Graphics) format with customizable vectorization settings. Supports preset configurations for different image types and offers fine-grained control over color mode, layering, and curve approximation."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertIcoToSvgRequest(
            body=_models.PostConvertIcoToSvgRequestBody(file_=file_, file_name=file_name, preset=preset, color_mode=color_mode, layering=layering, curve_mode=curve_mode)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_icon_to_svg: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/ico/to/svg"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_icon_to_svg")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_icon_to_svg", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_icon_to_svg",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_image_ico_to_webp(
    file_: str | None = Field(None, alias="File", description="The image file to convert. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing for multiple outputs (e.g., image_0.webp, image_1.webp)."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain aspect ratio when scaling the output image."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the output dimensions."),
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(None, alias="ColorSpace", description="Color space for the output image. Choose from standard color profiles or use default for automatic detection."),
) -> dict[str, Any] | ToolResult:
    """Convert ICO image files to WebP format with optional scaling and color space adjustments. Supports both file uploads and URL-based sources."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertIcoToWebpRequest(
            body=_models.PostConvertIcoToWebpRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, color_space=color_space)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_image_ico_to_webp: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/ico/to/webp"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_image_ico_to_webp")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_image_ico_to_webp", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_image_ico_to_webp",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def join_images(
    files: list[str] | None = Field(None, alias="Files", description="Images to combine into a single composite image. Each item can be provided as a URL or file content. When using query or multipart parameters, append an index suffix (e.g., Files[0], Files[1])."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output composite image file. The system automatically sanitizes the filename, appends the appropriate extension based on the target format, and adds indexing for multiple outputs to ensure unique, safe filenames."),
    join_direction: Literal["vertical", "horizontal"] | None = Field(None, alias="JoinDirection", description="Direction in which images are arranged in the composite. Choose vertical to stack images top-to-bottom or horizontal to arrange them left-to-right."),
    image_spacing: int | None = Field(None, alias="ImageSpacing", description="Space in pixels between individual images in the composite. Specify a value between 0 and 200 pixels.", ge=0, le=200),
    spacing_color: str | None = Field(None, alias="SpacingColor", description="Color of the spacing area between images. Works in conjunction with ImageSpacing to customize the visual appearance of gaps in the composite image."),
    image_output_format: Literal["auto", "jpg", "png", "tiff"] | None = Field(None, alias="ImageOutputFormat", description="Output format for the final composite image. Select a specific format (jpg, png, tiff) or use auto-detection to match the format of the input images."),
) -> dict[str, Any] | ToolResult:
    """Combines multiple images into a single composite image with configurable layout direction, spacing, and output format. Supports vertical or horizontal arrangement with customizable spacing color and format conversion."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertImagesToJoinRequest(
            body=_models.PostConvertImagesToJoinRequestBody(files=files, file_name=file_name, join_direction=join_direction, image_spacing=image_spacing, spacing_color=spacing_color, image_output_format=image_output_format)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for join_images: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/images/to/join"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("join_images")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("join_images", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="join_images",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["Files"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_images_to_pdf(
    files: list[str] | None = Field(None, alias="Files", description="Images to convert to PDF. Each item can be provided as a URL or file content. When using query or multipart parameters, append an index to each parameter name (e.g., Files[0], Files[1])."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds an index suffix for multiple output files to ensure unique, safe naming."),
    rotate: int | None = Field(None, alias="Rotate", description="Rotate images by the specified number of degrees. Leave empty to automatically rotate based on EXIF orientation data in TIFF and JPEG images.", ge=-360, le=360),
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(None, alias="ColorSpace", description="Set the color space for the output PDF. Use 'default' to preserve original image colors, or specify a standard color space for consistent output."),
    pdfa: bool | None = Field(None, alias="Pdfa", description="Generate a PDF/A-1b compliant document suitable for long-term archival and preservation."),
    margin: str | None = Field(None, alias="Margin", description="Page margins in millimeters as 'horizontal,vertical' (e.g., '10,15')"),
) -> dict[str, Any] | ToolResult:
    """Convert one or more images to a PDF document with optional image processing capabilities including rotation and color space adjustment. Supports PDF/A-1b compliance for archival purposes."""

    # Call helper functions
    margin_parsed = parse_margin(margin)

    # Construct request model with validation
    try:
        _request = _models.PostConvertImagesToPdfRequest(
            body=_models.PostConvertImagesToPdfRequestBody(files=files, file_name=file_name, rotate=rotate, color_space=color_space, pdfa=pdfa, margin_horizontal=margin_parsed.get('MarginHorizontal') if margin_parsed else None, margin_vertical=margin_parsed.get('MarginVertical') if margin_parsed else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_images_to_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/images/to/pdf"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_images_to_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_images_to_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_images_to_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["Files"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_jfif_to_pdf(
    file_: str | None = Field(None, alias="File", description="The image file to convert. Provide either a URL reference or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.pdf, filename_1.pdf) for multiple outputs to ensure unique, safe file naming."),
    rotate: int | None = Field(None, alias="Rotate", description="Rotation angle in degrees for the output image. Specify a value between -360 and 360, or leave empty to automatically rotate based on EXIF data in TIFF and JPEG images.", ge=-360, le=360),
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(None, alias="ColorSpace", description="Color space for the output PDF. Select from standard color space options to control how colors are represented in the final document."),
    color_profile: Literal["default", "isocoatedv2"] | None = Field(None, alias="ColorProfile", description="Color profile to apply to the output PDF. Some profiles override the ColorSpace setting. Use 'isocoatedv2' for ISO Coated v2 standard compliance."),
    pdfa: bool | None = Field(None, alias="Pdfa", description="Enable PDF/A-1b compliance for the output document. When true, creates an archival-grade PDF suitable for long-term preservation."),
    margin: str | None = Field(None, alias="Margin", description="Page margins in millimeters as 'horizontal,vertical' (e.g., '10,15')"),
) -> dict[str, Any] | ToolResult:
    """Convert JFIF image files to PDF format with support for rotation, color space configuration, and PDF/A compliance. Accepts file input as URL or binary content and generates a properly named output PDF file."""

    # Call helper functions
    margin_parsed = parse_margin(margin)

    # Construct request model with validation
    try:
        _request = _models.PostConvertJfifToPdfRequest(
            body=_models.PostConvertJfifToPdfRequestBody(file_=file_, file_name=file_name, rotate=rotate, color_space=color_space, color_profile=color_profile, pdfa=pdfa, margin_horizontal=margin_parsed.get('MarginHorizontal') if margin_parsed else None, margin_vertical=margin_parsed.get('MarginVertical') if margin_parsed else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_jfif_to_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/jfif/to/pdf"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_jfif_to_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_jfif_to_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_jfif_to_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def compress_jpg_image(
    file_: str | None = Field(None, alias="File", description="The JPG image file to compress. Can be provided as a URL or as binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output compressed image file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing for multiple outputs to ensure unique and safe file naming."),
    compression_level: Literal["Lossless", "Good", "Extreme"] | None = Field(None, alias="CompressionLevel", description="The compression quality level to apply to the image. Lossless preserves all image data, Good provides balanced compression, and Extreme maximizes file size reduction."),
) -> dict[str, Any] | ToolResult:
    """Compress a JPG image file with configurable compression levels. Accepts image files via URL or direct upload and generates an optimized output file with the specified compression quality."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertJpgToCompressRequest(
            body=_models.PostConvertJpgToCompressRequestBody(file_=file_, file_name=file_name, compression_level=compression_level)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for compress_jpg_image: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/jpg/to/compress"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("compress_jpg_image")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("compress_jpg_image", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="compress_jpg_image",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_image_to_gif(
    files: list[str] | None = Field(None, alias="Files", description="Image files to convert, provided as URLs or file content. When using query or multipart parameters, append an index to each file parameter (e.g., Files[0], Files[1])."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output GIF file(s). The API sanitizes the filename, appends the correct extension, and automatically indexes multiple output files to ensure unique naming."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Only scale the output if the input image dimensions exceed the target size."),
    animation_delay: int | None = Field(None, alias="AnimationDelay", description="Delay between animation frames, specified in hundredths of a second (e.g., 100 = 1 second).", ge=0, le=20000),
    animation_iterations: int | None = Field(None, alias="AnimationIterations", description="Number of times the animation loops. Set to 0 for infinite looping.", ge=0, le=1000),
) -> dict[str, Any] | ToolResult:
    """Convert one or more JPG images to animated GIF format with customizable animation timing and looping behavior."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertJpgToGifRequest(
            body=_models.PostConvertJpgToGifRequestBody(files=files, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, animation_delay=animation_delay, animation_iterations=animation_iterations)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_image_to_gif: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/jpg/to/gif"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_image_to_gif")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_image_to_gif", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_image_to_gif",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["Files"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_image_format(
    file_: str | None = Field(None, alias="File", description="The image file to convert. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.jpg, filename_1.jpg) for multiple outputs to ensure unique, safe file naming."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions are larger than the target output dimensions."),
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(None, alias="ColorSpace", description="Set the color space profile for the output image."),
) -> dict[str, Any] | ToolResult:
    """Convert a JPG image to JPG format with optional scaling and color space adjustments. Useful for optimizing image properties such as dimensions and color profile while maintaining the same format."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertJpgToJpgRequest(
            body=_models.PostConvertJpgToJpgRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, color_space=color_space)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_image_format: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/jpg/to/jpg"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_image_format")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_image_format", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_image_format",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_image_jpg_to_jxl(
    file_: str | None = Field(None, alias="File", description="The image file to convert. Accepts either a URL pointing to the image or the raw file content."),
    file_name: str | None = Field(None, alias="FileName", description="Custom name for the output file. The system automatically sanitizes the name, appends the correct file extension, and adds indexing for multiple outputs to ensure unique, safe filenames."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Apply scaling only when the input image dimensions exceed the target output dimensions."),
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(None, alias="ColorSpace", description="Define the color space for the output image. Use 'default' for automatic detection, or specify a particular color space."),
) -> dict[str, Any] | ToolResult:
    """Convert a JPG image to JXL (JPEG XL) format with optional scaling and color space adjustments. Supports both URL-based and direct file uploads."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertJpgToJxlRequest(
            body=_models.PostConvertJpgToJxlRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, color_space=color_space)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_image_jpg_to_jxl: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/jpg/to/jxl"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_image_jpg_to_jxl")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_image_jpg_to_jxl", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_image_jpg_to_jxl",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_image_to_pdf_jpeg(
    file_: str | None = Field(None, alias="File", description="The image file to convert. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.pdf, filename_1.pdf) when multiple files are generated."),
    rotate: int | None = Field(None, alias="Rotate", description="Rotation angle in degrees to apply to the image. Leave empty to automatically detect and apply rotation from EXIF metadata in JPEG and TIFF images.", ge=-360, le=360),
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(None, alias="ColorSpace", description="The color space to apply to the output PDF. Determines how colors are represented in the final document."),
    color_profile: Literal["default", "isocoatedv2"] | None = Field(None, alias="ColorProfile", description="The color profile to embed in the output PDF. Some profiles may override the ColorSpace setting."),
    pdfa: bool | None = Field(None, alias="Pdfa", description="Enable PDF/A-1b compliance for long-term archival and preservation of the document."),
    margin: str | None = Field(None, alias="Margin", description="Page margins in millimeters as 'horizontal,vertical' (e.g., '10,20')"),
) -> dict[str, Any] | ToolResult:
    """Convert JPG images to PDF format with optional image processing capabilities including rotation, color space adjustment, and PDF/A compliance."""

    # Call helper functions
    margin_parsed = parse_margin(margin)

    # Construct request model with validation
    try:
        _request = _models.PostConvertJpgToPdfRequest(
            body=_models.PostConvertJpgToPdfRequestBody(file_=file_, file_name=file_name, rotate=rotate, color_space=color_space, color_profile=color_profile, pdfa=pdfa, margin_horizontal=margin_parsed.get('MarginHorizontal') if margin_parsed else None, margin_vertical=margin_parsed.get('MarginVertical') if margin_parsed else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_image_to_pdf_jpeg: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/jpg/to/pdf"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_image_to_pdf_jpeg")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_image_to_pdf_jpeg", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_image_to_pdf_jpeg",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_image_jpg_to_png(
    file_: str | None = Field(None, alias="File", description="The image file to convert, provided either as a URL or raw file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output PNG file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., image_0.png, image_1.png) for multiple outputs from a single input."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Whether to maintain the original aspect ratio when scaling the output image."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Whether to apply scaling only when the input image dimensions exceed the target output dimensions."),
    red: int | None = Field(None, description="Red channel value (0-255)"),
    green: int | None = Field(None, description="Green channel value (0-255)"),
    blue: int | None = Field(None, description="Blue channel value (0-255)"),
    alpha: int | None = Field(None, description="Alpha channel value (0-255), where 0 is fully transparent and 255 is fully opaque. Optional; if not provided, defaults to 255 (fully opaque)."),
) -> dict[str, Any] | ToolResult:
    """Convert a JPG image to PNG format with optional scaling and proportional constraints. Supports both URL-based and direct file content input."""

    # Call helper functions
    transparent_color = build_transparent_color(red, green, blue, alpha)

    # Construct request model with validation
    try:
        _request = _models.PostConvertJpgToPngRequest(
            body=_models.PostConvertJpgToPngRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, transparent_color=transparent_color)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_image_jpg_to_png: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/jpg/to/png"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_image_jpg_to_png")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_image_jpg_to_png", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_image_jpg_to_png",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_image_jpg_to_pnm(
    file_: str | None = Field(None, alias="File", description="The image file to convert. Accepts either a URL pointing to the JPG file or the raw binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output PNM file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., image_0.pnm, image_1.pnm) for multiple outputs from a single input."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image to the target dimensions."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Apply scaling only when the input image dimensions exceed the target output size, leaving smaller images unchanged."),
    red: int | None = Field(None, description="Red channel value (0-255)"),
    green: int | None = Field(None, description="Green channel value (0-255)"),
    blue: int | None = Field(None, description="Blue channel value (0-255)"),
    alpha: int | None = Field(None, description="Alpha channel value (0-255), where 0 is fully transparent and 255 is fully opaque. Optional; if not provided, defaults to 255 (fully opaque)."),
) -> dict[str, Any] | ToolResult:
    """Convert a JPG image to PNM (Portable Anymap) format with optional scaling and proportional constraints. Supports both URL-based and direct file uploads."""

    # Call helper functions
    transparent_color = build_transparent_color(red, green, blue, alpha)

    # Construct request model with validation
    try:
        _request = _models.PostConvertJpgToPnmRequest(
            body=_models.PostConvertJpgToPnmRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, transparent_color=transparent_color)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_image_jpg_to_pnm: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/jpg/to/pnm"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_image_jpg_to_pnm")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_image_jpg_to_pnm", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_image_jpg_to_pnm",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_image_to_svg_jpg(
    file_: str | None = Field(None, alias="File", description="The image file to convert. Accepts either a URL reference or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the generated output SVG file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.svg, filename_1.svg) for multiple output files."),
    preset: Literal["none", "detailed", "crisp", "graphic", "illustration", "noisyScan"] | None = Field(None, alias="Preset", description="A vectorization preset that applies pre-configured tracing settings optimized for specific image types. When selected, presets override individual converter options except ColorMode, ensuring consistent and balanced SVG output."),
    color_mode: Literal["color", "bw"] | None = Field(None, alias="ColorMode", description="Determines whether the image is traced in full color or converted to black-and-white during vectorization."),
    layering: Literal["cutout", "stacked"] | None = Field(None, alias="Layering", description="Controls how color regions are arranged in the output SVG: cutout mode isolates regions as separate layers, while stacked mode overlays regions for blending effects."),
    curve_mode: Literal["pixel", "polygon", "spline"] | None = Field(None, alias="CurveMode", description="Defines the shape approximation method during tracing. Pixel mode follows exact pixel boundaries with minimal smoothing, Polygon creates straight-edged paths with sharp corners, and Spline generates smooth continuous curves for natural-looking shapes."),
) -> dict[str, Any] | ToolResult:
    """Converts a JPG image to scalable vector graphics (SVG) format using configurable tracing and vectorization settings. Supports preset configurations for different image types and offers fine-grained control over color handling, layering, and curve approximation."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertJpgToSvgRequest(
            body=_models.PostConvertJpgToSvgRequestBody(file_=file_, file_name=file_name, preset=preset, color_mode=color_mode, layering=layering, curve_mode=curve_mode)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_image_to_svg_jpg: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/jpg/to/svg"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_image_to_svg_jpg")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_image_to_svg_jpg", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_image_to_svg_jpg",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_image_to_tiff(
    file_: str | None = Field(None, alias="File", description="The image file to convert. Accepts either a URL pointing to the JPG file or the raw file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output TIFF file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.tiff, filename_1.tiff) for multi-file outputs."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the target output dimensions."),
    multi_page: bool | None = Field(None, alias="MultiPage", description="Generate a multi-page TIFF file when processing multiple images or pages."),
) -> dict[str, Any] | ToolResult:
    """Convert a JPG image to TIFF format with optional scaling and multi-page support. Supports both URL-based and direct file uploads."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertJpgToTiffRequest(
            body=_models.PostConvertJpgToTiffRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, multi_page=multi_page)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_image_to_tiff: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/jpg/to/tiff"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_image_to_tiff")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_image_to_tiff", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_image_to_tiff",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def extract_text_from_image(
    file_: str | None = Field(None, alias="File", description="The image file to convert. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output text file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.txt, output_1.txt) for multiple files."),
    preprocessing: bool | None = Field(None, alias="Preprocessing", description="Enable advanced image preprocessing techniques such as deskew, thresholding, resizing, and sharpening to improve text extraction accuracy. Increases processing time when enabled."),
    ocr_language: Literal["ar", "ca", "zh-cn", "zh-tw", "da", "nl", "en", "fi", "fa", "de", "el", "he", "it", "ja", "ko", "lt", "no", "pl", "pt", "ro", "ru", "sl", "es", "sv", "tr", "ua", "th"] | None = Field(None, alias="OcrLanguage", description="The language to use for OCR text recognition. Supports multiple languages; contact support to request additional language support."),
) -> dict[str, Any] | ToolResult:
    """Converts a JPG image to text by performing optical character recognition (OCR). Supports optional image preprocessing to enhance text clarity and multiple language recognition."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertJpgToTxtRequest(
            body=_models.PostConvertJpgToTxtRequestBody(file_=file_, file_name=file_name, preprocessing=preprocessing, ocr_language=ocr_language)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for extract_text_from_image: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/jpg/to/txt"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("extract_text_from_image")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("extract_text_from_image", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="extract_text_from_image",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_image_jpg_to_webp(
    file_: str | None = Field(None, alias="File", description="The image file to convert. Accepts either a file upload or a URL pointing to the source image."),
    file_name: str | None = Field(None, alias="FileName", description="Custom name for the output file. The API automatically sanitizes the filename, appends the correct .webp extension, and adds numeric indexing for multiple output files to ensure unique, safe filenames."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Apply scaling only when the input image dimensions exceed the target output dimensions."),
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(None, alias="ColorSpace", description="Define the color space for the output image."),
) -> dict[str, Any] | ToolResult:
    """Convert JPG images to WebP format with optional scaling and color space adjustments. Supports both file uploads and URL-based inputs."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertJpgToWebpRequest(
            body=_models.PostConvertJpgToWebpRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, color_space=color_space)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_image_jpg_to_webp: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/jpg/to/webp"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_image_jpg_to_webp")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_image_jpg_to_webp", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_image_jpg_to_webp",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_presentation_to_pptx(
    file_: str | None = Field(None, alias="File", description="The Keynote presentation file to convert. Can be provided as a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the generated output file. The system automatically sanitizes the filename, appends the correct .pptx extension, and adds numeric indexing (e.g., output_0.pptx, output_1.pptx) if multiple files are generated."),
) -> dict[str, Any] | ToolResult:
    """Converts a Keynote presentation file to PowerPoint format (PPTX). Accepts file input as a URL or binary content and generates a properly named output file."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertKeyToPptxRequest(
            body=_models.PostConvertKeyToPptxRequestBody(file_=file_, file_name=file_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_presentation_to_pptx: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/key/to/pptx"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_presentation_to_pptx")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_presentation_to_pptx", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_presentation_to_pptx",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_log_to_docx(
    file_: str | None = Field(None, alias="File", description="The log file to convert. Provide either a URL pointing to the file or the raw file content as binary data."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the generated output file. The API automatically sanitizes the filename, appends the .docx extension, and adds numeric indexing (e.g., report_0.docx, report_1.docx) if multiple files are generated."),
) -> dict[str, Any] | ToolResult:
    """Converts a log file to Microsoft Word (.docx) format. Accepts log file content or URL and generates a formatted Word document with the specified output filename."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertLogToDocxRequest(
            body=_models.PostConvertLogToDocxRequestBody(file_=file_, file_name=file_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_log_to_docx: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/log/to/docx"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_log_to_docx")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_log_to_docx", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_log_to_docx",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_log_to_pdf(
    file_: str | None = Field(None, alias="File", description="The log file to convert. Accepts either a file URL or raw file content in binary format."),
    file_name: str | None = Field(None, alias="FileName", description="Custom name for the generated output PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., `report_0.pdf`, `report_1.pdf`) for multiple output files."),
    page_range: str | None = Field(None, alias="PageRange", description="Specifies which pages to include in the output PDF using a range format (e.g., 1-10 for pages 1 through 10). Defaults to the first 6000 pages."),
    pdfa_version: Literal["none", "pdfA1b", "pdfA2b", "pdfA3b"] | None = Field(None, alias="PdfaVersion", description="Sets the PDF/A compliance version for archival-grade PDF output. Use 'none' for standard PDF without compliance requirements."),
) -> dict[str, Any] | ToolResult:
    """Converts log files to PDF format with optional page range selection and PDF/A compliance. Supports both file uploads and URL-based file sources."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertLogToPdfRequest(
            body=_models.PostConvertLogToPdfRequestBody(file_=file_, file_name=file_name, page_range=page_range, pdfa_version=pdfa_version)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_log_to_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/log/to/pdf"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_log_to_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_log_to_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_log_to_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_log_to_text(
    file_: str | None = Field(None, alias="File", description="The log file to convert. Accepts either a URL reference or raw file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the generated output file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., file_0.txt, file_1.txt) for multiple outputs to ensure unique, safe file identification."),
    password: str | None = Field(None, alias="Password", description="Password required to open password-protected log files."),
    substitutions: bool | None = Field(None, alias="Substitutions", description="Enable replacement of special symbols with their text equivalents (e.g., © becomes (c)) in the output text."),
    end_line_char: Literal["crlf", "cr", "lfcr", "lf"] | None = Field(None, alias="EndLineChar", description="Specifies the line ending character(s) to use when breaking lines in the output text file."),
) -> dict[str, Any] | ToolResult:
    """Converts log files to plain text format with optional symbol substitution and configurable line ending characters. Supports protected documents via password and customizable output file naming."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertLogToTxtRequest(
            body=_models.PostConvertLogToTxtRequestBody(file_=file_, file_name=file_name, password=password, substitutions=substitutions, end_line_char=end_line_char)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_log_to_text: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/log/to/txt"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_log_to_text")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_log_to_text", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_log_to_text",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_markdown_to_html(
    file_: str | None = Field(None, alias="File", description="The Markdown content to convert, provided either as a URL or raw file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the generated HTML output file. The system automatically sanitizes the filename, appends the .html extension, and adds numeric suffixes (e.g., output_0.html, output_1.html) when generating multiple files from a single input."),
) -> dict[str, Any] | ToolResult:
    """Converts Markdown content to HTML format. Accepts Markdown input as file content or URL and generates corresponding HTML output."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertMdToHtmlRequest(
            body=_models.PostConvertMdToHtmlRequestBody(file_=file_, file_name=file_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_markdown_to_html: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/md/to/html"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_markdown_to_html")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_markdown_to_html", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_markdown_to_html",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_markdown_to_pdf(
    file_: str | None = Field(None, alias="File", description="The Markdown file to convert. Provide either a URL pointing to the file or the raw file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the generated PDF output file. The system automatically sanitizes the filename, appends the .pdf extension, and adds numeric suffixes (e.g., _0, _1) if multiple files are generated."),
    margin_top: int | None = Field(None, alias="MarginTop", description="Top margin of the PDF page in millimeters. Valid range is 0-500 mm.", ge=0, le=500),
    margin_right: int | None = Field(None, alias="MarginRight", description="Right margin of the PDF page in millimeters. Valid range is 0-500 mm.", ge=0, le=500),
    margin_bottom: int | None = Field(None, alias="MarginBottom", description="Bottom margin of the PDF page in millimeters. Valid range is 0-500 mm.", ge=0, le=500),
    margin_left: int | None = Field(None, alias="MarginLeft", description="Left margin of the PDF page in millimeters. Valid range is 0-500 mm.", ge=0, le=500),
) -> dict[str, Any] | ToolResult:
    """Converts Markdown documents to PDF format with customizable page margins. Accepts Markdown content via URL or file upload and generates a formatted PDF output."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertMdToPdfRequest(
            body=_models.PostConvertMdToPdfRequestBody(file_=file_, file_name=file_name, margin_top=margin_top, margin_right=margin_right, margin_bottom=margin_bottom, margin_left=margin_left)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_markdown_to_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/md/to/pdf"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_markdown_to_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_markdown_to_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_markdown_to_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_mhtml_to_docx(
    file_: str | None = Field(None, alias="File", description="The MHTML file to convert, provided either as a URL or as binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output DOCX file. The API automatically sanitizes the filename, appends the correct extension, and adds numeric indexing (e.g., document_0.docx, document_1.docx) when multiple files are generated from a single input."),
    margins: str | None = Field(None, alias="Margins", description="Page margins in inches as 'horizontal,vertical' (e.g., '1.0,0.5')"),
) -> dict[str, Any] | ToolResult:
    """Converts an MHTML (MIME HTML) file to DOCX format. Accepts file input as a URL or binary content and generates a properly named output document."""

    # Call helper functions
    margins_parsed = parse_margins(margins)

    # Construct request model with validation
    try:
        _request = _models.PostConvertMhtmlToDocxRequest(
            body=_models.PostConvertMhtmlToDocxRequestBody(file_=file_, file_name=file_name, margin_horizontal=margins_parsed.get('MarginHorizontal') if margins_parsed else None, margin_vertical=margins_parsed.get('MarginVertical') if margins_parsed else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_mhtml_to_docx: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/mhtml/to/docx"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_mhtml_to_docx")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_mhtml_to_docx", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_mhtml_to_docx",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_mobi_to_jpg(
    file_: str | None = Field(None, alias="File", description="The MOBI file to convert. Accepts either a URL or raw file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output file(s). The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.jpg, filename_1.jpg) for multiple output files."),
    jpg_type: Literal["jpeg", "jpegcmyk", "jpeggray"] | None = Field(None, alias="JpgType", description="JPG color mode for the output image. Choose between standard JPEG, CMYK for print-ready output, or grayscale for reduced file size."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain aspect ratio when resizing the output image to prevent distortion."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the target output dimensions, preserving quality for smaller images."),
) -> dict[str, Any] | ToolResult:
    """Converts MOBI eBook files to JPG image format with configurable output quality and scaling options. Supports multiple JPG color modes and intelligent scaling to optimize output file size."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertMobiToJpgRequest(
            body=_models.PostConvertMobiToJpgRequestBody(file_=file_, file_name=file_name, jpg_type=jpg_type, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_mobi_to_jpg: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/mobi/to/jpg"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_mobi_to_jpg")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_mobi_to_jpg", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_mobi_to_jpg",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_mobi_to_pdf(
    file_: str | None = Field(None, alias="File", description="The MOBI file to convert, provided either as a URL or as binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the generated PDF output file. The system automatically sanitizes the filename, appends the correct .pdf extension, and adds numeric indexing (e.g., output_0.pdf, output_1.pdf) when multiple files are generated from a single input."),
    base_font_size: float | None = Field(None, alias="BaseFontSize", description="The base font size in points (pt) for the converted PDF. All text scaling is relative to this value.", ge=1, le=50),
    margins: str | None = Field(None, alias="Margins", description="Page margins in points (pt) in CSS shorthand format: 'top right bottom left' (e.g., '72 36 72 36')"),
) -> dict[str, Any] | ToolResult:
    """Converts MOBI eBook files to PDF format with customizable font sizing. Accepts file input as URL or binary content and generates a properly named output PDF file."""

    # Call helper functions
    margins_parsed = parse_margins(margins)

    # Construct request model with validation
    try:
        _request = _models.PostConvertMobiToPdfRequest(
            body=_models.PostConvertMobiToPdfRequestBody(file_=file_, file_name=file_name, base_font_size=base_font_size, margin_top=margins_parsed.get('MarginTop') if margins_parsed else None, margin_right=margins_parsed.get('MarginRight') if margins_parsed else None, margin_bottom=margins_parsed.get('MarginBottom') if margins_parsed else None, margin_left=margins_parsed.get('MarginLeft') if margins_parsed else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_mobi_to_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/mobi/to/pdf"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_mobi_to_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_mobi_to_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_mobi_to_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_mobi_to_png(
    file_: str | None = Field(None, alias="File", description="The MOBI file to convert. Accepts either a URL pointing to the file or the raw file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output PNG file(s). The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.png, output_1.png) for multiple files."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain aspect ratio when resizing the output image."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the target output size."),
) -> dict[str, Any] | ToolResult:
    """Convert MOBI eBook files to PNG image format. Supports URL or file content input with optional scaling and proportional resizing controls."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertMobiToPngRequest(
            body=_models.PostConvertMobiToPngRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_mobi_to_png: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/mobi/to/png"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_mobi_to_png")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_mobi_to_png", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_mobi_to_png",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_mobi_to_tiff(
    file_: str | None = Field(None, alias="File", description="The MOBI file to convert. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output TIFF file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.tiff, output_1.tiff) for multi-page conversions."),
    tiff_type: Literal["color24nc", "color32nc", "color24lzw", "color32lzw", "color24zip", "color32zip", "grayscale", "grayscalelzw", "grayscalezip", "monochromeg3", "monochromeg32d", "monochromeg4", "monochromelzw", "monochromepackbits"] | None = Field(None, alias="TiffType", description="Specifies the TIFF color type and compression method. Choose from color variants (24/32-bit with no compression, LZW, or ZIP), grayscale options, or monochrome formats."),
    multi_page: bool | None = Field(None, alias="MultiPage", description="When enabled, combines all pages into a single multi-page TIFF file. When disabled, generates separate TIFF files for each page."),
    fill_order: Literal["0", "1"] | None = Field(None, alias="FillOrder", description="Defines the bit order within each byte of the TIFF data. Use 0 for most standard applications or 1 for specific compatibility requirements."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="When enabled, maintains the original aspect ratio when resizing the output image to fit specified dimensions."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="When enabled, only applies scaling if the input image dimensions exceed the target output dimensions. Prevents upscaling of smaller images."),
) -> dict[str, Any] | ToolResult:
    """Converts MOBI eBook files to TIFF image format with configurable output options including color depth, compression, and multi-page support."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertMobiToTiffRequest(
            body=_models.PostConvertMobiToTiffRequestBody(file_=file_, file_name=file_name, tiff_type=tiff_type, multi_page=multi_page, fill_order=fill_order, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_mobi_to_tiff: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/mobi/to/tiff"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_mobi_to_tiff")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_mobi_to_tiff", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_mobi_to_tiff",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_email_to_jpg(
    file_: str | None = Field(None, alias="File", description="The email message file to convert. Accepts either a URL reference or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output JPG file(s). The system automatically sanitizes the filename, appends the correct extension, and adds numeric indexing (e.g., output_0.jpg, output_1.jpg) when multiple files are generated."),
    ignore_attachment_errors: bool | None = Field(None, alias="IgnoreAttachmentErrors", description="When enabled, attachment conversion errors will not prevent the email body from being converted to JPG. Only applies when attachments are being processed."),
    merge: bool | None = Field(None, alias="Merge", description="When enabled, merges the email body content with extracted attachments during conversion. Only applies when attachments are being processed."),
) -> dict[str, Any] | ToolResult:
    """Converts an email message file (MSG format) to JPG image format, with optional support for extracting and merging attachments into the output."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertMsgToJpgRequest(
            body=_models.PostConvertMsgToJpgRequestBody(file_=file_, file_name=file_name, ignore_attachment_errors=ignore_attachment_errors, merge=merge)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_email_to_jpg: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/msg/to/jpg"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_email_to_jpg")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_email_to_jpg", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_email_to_jpg",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_msg_to_pdf(
    file_: str | None = Field(None, alias="File", description="The MSG file to convert. Accepts either a URL reference or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the generated PDF output file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., report_0.pdf, report_1.pdf) when multiple files are produced."),
    ignore_attachment_errors: bool | None = Field(None, alias="IgnoreAttachmentErrors", description="When enabled, attachment conversion errors are ignored and the email body is still converted to PDF. Only applies when attachments are being converted."),
    merge: bool | None = Field(None, alias="Merge", description="When enabled, merges the email body with converted attachments into a single PDF document. Only applies when attachments are being converted."),
    pdfa: bool | None = Field(None, alias="Pdfa", description="When enabled, creates a PDF/A-1b compliant document for long-term archival and preservation."),
    margins: str | None = Field(None, alias="Margins", description="Page margins in millimeters as space-separated values: 'top right bottom left' (e.g., '10 10 10 10')"),
) -> dict[str, Any] | ToolResult:
    """Converts MSG (Outlook email) files to PDF format with optional attachment handling and PDF/A compliance. Supports file input via URL or binary content."""

    # Call helper functions
    margins_parsed = parse_margins(margins)

    # Construct request model with validation
    try:
        _request = _models.PostConvertMsgToPdfRequest(
            body=_models.PostConvertMsgToPdfRequestBody(file_=file_, file_name=file_name, ignore_attachment_errors=ignore_attachment_errors, merge=merge, pdfa=pdfa, margin_top=margins_parsed.get('MarginTop') if margins_parsed else None, margin_right=margins_parsed.get('MarginRight') if margins_parsed else None, margin_bottom=margins_parsed.get('MarginBottom') if margins_parsed else None, margin_left=margins_parsed.get('MarginLeft') if margins_parsed else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_msg_to_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/msg/to/pdf"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_msg_to_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_msg_to_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_msg_to_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_email_to_png_outlook(
    file_: str | None = Field(None, alias="File", description="The email message file to convert. Accepts either a URL pointing to the file or the raw file content as binary data."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output PNG file(s). The system automatically sanitizes the filename, appends the correct extension, and adds numeric indices (e.g., email_0.png, email_1.png) when multiple files are generated."),
    ignore_attachment_errors: bool | None = Field(None, alias="IgnoreAttachmentErrors", description="When enabled, the conversion process will continue even if errors occur while processing email attachments. Only applies when attachments are being converted."),
    merge: bool | None = Field(None, alias="Merge", description="When enabled, email body content and attachments are combined into a single output during conversion. Only applies when attachments are being converted."),
) -> dict[str, Any] | ToolResult:
    """Converts an email message file (MSG format) to PNG image format, with optional support for embedding attachments into the output. Useful for archiving, sharing, or preserving email content as images."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertMsgToPngRequest(
            body=_models.PostConvertMsgToPngRequestBody(file_=file_, file_name=file_name, ignore_attachment_errors=ignore_attachment_errors, merge=merge)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_email_to_png_outlook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/msg/to/png"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_email_to_png_outlook")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_email_to_png_outlook", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_email_to_png_outlook",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_msg_to_tiff(
    file_: str | None = Field(None, alias="File", description="The MSG file to convert. Accepts either a URL pointing to the file or the raw file content as binary data."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output TIFF file(s). The API automatically sanitizes the name, appends the correct extension, and adds numeric suffixes (e.g., _0, _1) when multiple files are generated."),
    ignore_attachment_errors: bool | None = Field(None, alias="IgnoreAttachmentErrors", description="If enabled, attachment conversion errors will not prevent the email body from being converted. Only applies when attachments are being converted."),
    merge: bool | None = Field(None, alias="Merge", description="If enabled, merges the email body with converted attachments into the output. Only applies when attachments are being converted."),
    multi_page: bool | None = Field(None, alias="MultiPage", description="If enabled, creates a single multi-page TIFF file containing all content. If disabled, generates separate TIFF files for each page."),
) -> dict[str, Any] | ToolResult:
    """Converts MSG email files to TIFF image format, with support for embedding attachments and creating multi-page documents. Useful for archiving emails as image files or integrating with document management systems."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertMsgToTiffRequest(
            body=_models.PostConvertMsgToTiffRequestBody(file_=file_, file_name=file_name, ignore_attachment_errors=ignore_attachment_errors, merge=merge, multi_page=multi_page)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_msg_to_tiff: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/msg/to/tiff"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_msg_to_tiff")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_msg_to_tiff", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_msg_to_tiff",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_message_to_webp(
    file_: str | None = Field(None, alias="File", description="The message file to convert. Accepts either a URL reference or raw file content in binary format."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output WebP file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.webp, output_1.webp) for multiple files to ensure unique, safe filenames."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain aspect ratio when scaling the output image to the target dimensions."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the target output size."),
) -> dict[str, Any] | ToolResult:
    """Convert a message file to WebP image format with optional scaling and proportional constraints. Supports both URL and file content input."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertMsgToWebpRequest(
            body=_models.PostConvertMsgToWebpRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_message_to_webp: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/msg/to/webp"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_message_to_webp")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_message_to_webp", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_message_to_webp",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_numbers_to_csv(
    file_: str | None = Field(None, alias="File", description="The file to convert, provided either as a URL or raw file content in binary format."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the generated CSV output file. The system automatically sanitizes the filename, appends the .csv extension, and adds numeric indexing (e.g., output_0.csv, output_1.csv) if multiple files are generated."),
) -> dict[str, Any] | ToolResult:
    """Converts a numbers file to CSV format. Accepts file input as a URL or file content and generates a properly named CSV output file."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertNumbersToCsvRequest(
            body=_models.PostConvertNumbersToCsvRequestBody(file_=file_, file_name=file_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_numbers_to_csv: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/numbers/to/csv"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_numbers_to_csv")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_numbers_to_csv", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_numbers_to_csv",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_numbers_to_xlsx(
    file_: str | None = Field(None, alias="File", description="The Numbers file to convert, provided either as a URL or as binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the generated output file. The system automatically sanitizes the filename, appends the correct .xlsx extension, and adds numeric indexing (e.g., report_0.xlsx, report_1.xlsx) if multiple files are generated."),
) -> dict[str, Any] | ToolResult:
    """Converts a Numbers spreadsheet file to Excel (XLSX) format. Accepts file input as a URL or binary content and generates a properly named output file."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertNumbersToXlsxRequest(
            body=_models.PostConvertNumbersToXlsxRequestBody(file_=file_, file_name=file_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_numbers_to_xlsx: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/numbers/to/xlsx"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_numbers_to_xlsx")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_numbers_to_xlsx", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_numbers_to_xlsx",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_document_to_jpg_spreadsheet(
    file_: str | None = Field(None, alias="File", description="The file to convert, provided either as a URL reference or raw binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Custom name for the output JPG file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.jpg, output_1.jpg) for multiple generated files."),
) -> dict[str, Any] | ToolResult:
    """Converts an ODC (OpenDocument Chart) file to JPG image format. Accepts file input as a URL or binary content and generates a JPG output file with optional custom naming."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertOdcToJpgRequest(
            body=_models.PostConvertOdcToJpgRequestBody(file_=file_, file_name=file_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_document_to_jpg_spreadsheet: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/odc/to/jpg"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_document_to_jpg_spreadsheet")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_document_to_jpg_spreadsheet", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_document_to_jpg_spreadsheet",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_odc_to_pdf(
    file_: str | None = Field(None, alias="File", description="The ODC file to convert. Accepts either a file upload or a URL pointing to the source file."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., `report_0.pdf`, `report_1.pdf`) for multiple output files."),
    pdfa_version: Literal["none", "pdfA1b", "pdfA2b", "pdfA3b"] | None = Field(None, alias="PdfaVersion", description="Specifies the PDF/A compliance version for the output file. Use 'none' for standard PDF, or select a PDF/A version for archival compliance."),
) -> dict[str, Any] | ToolResult:
    """Converts an ODC (OpenDocument Chart) file to PDF format with optional PDF/A compliance. Supports both file uploads and URL-based sources."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertOdcToPdfRequest(
            body=_models.PostConvertOdcToPdfRequestBody(file_=file_, file_name=file_name, pdfa_version=pdfa_version)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_odc_to_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/odc/to/pdf"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_odc_to_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_odc_to_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_odc_to_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_odc_to_png(
    file_: str | None = Field(None, alias="File", description="The ODC file to convert, provided as either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output PNG file(s). The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., `output_0.png`, `output_1.png`) for multiple files to ensure unique, safe naming."),
    background_color: str | None = Field(None, alias="BackgroundColor", description="Background color applied to transparent areas in the converted image. Accepts color names (e.g., `white`, `black`), RGB format (e.g., `255,0,0`), HEX format (e.g., `#FF0000`), or `transparent` to preserve transparency."),
) -> dict[str, Any] | ToolResult:
    """Converts ODC (OpenDocument Chart) files to PNG image format. Supports URL or file content input with optional background color customization for transparent areas."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertOdcToPngRequest(
            body=_models.PostConvertOdcToPngRequestBody(file_=file_, file_name=file_name, background_color=background_color)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_odc_to_png: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/odc/to/png"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_odc_to_png")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_odc_to_png", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_odc_to_png",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_document_to_jpg_formula(
    file_: str | None = Field(None, alias="File", description="The document file to convert, provided either as a URL or as binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output JPG file(s). The API automatically sanitizes the filename, appends the correct extension, and adds numeric indexing (e.g., document_0.jpg, document_1.jpg) when multiple output files are generated from a single input."),
) -> dict[str, Any] | ToolResult:
    """Converts ODF (OpenDocument Format) documents to JPG image format. Supports both file uploads and URL-based file sources."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertOdfToJpgRequest(
            body=_models.PostConvertOdfToJpgRequestBody(file_=file_, file_name=file_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_document_to_jpg_formula: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/odf/to/jpg"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_document_to_jpg_formula")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_document_to_jpg_formula", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_document_to_jpg_formula",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_document_to_pdf_odf(
    file_: str | None = Field(None, alias="File", description="The document file to convert. Can be provided as a file upload (binary content) or as a URL pointing to the source file."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the generated output PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds numeric indexing (e.g., `report_0.pdf`, `report_1.pdf`) when multiple files are generated from a single input."),
    pdfa_version: Literal["none", "pdfA1b", "pdfA2b", "pdfA3b"] | None = Field(None, alias="PdfaVersion", description="Specifies the PDF/A compliance version for the output file. PDF/A formats ensure long-term archival compatibility. Use 'none' for standard PDF output without archival compliance."),
) -> dict[str, Any] | ToolResult:
    """Converts ODF (Open Document Format) files to PDF format with optional PDF/A compliance. Supports both file uploads and URL-based file sources."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertOdfToPdfRequest(
            body=_models.PostConvertOdfToPdfRequestBody(file_=file_, file_name=file_name, pdfa_version=pdfa_version)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_document_to_pdf_odf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/odf/to/pdf"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_document_to_pdf_odf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_document_to_pdf_odf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_document_to_pdf_odf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_document_to_png(
    file_: str | None = Field(None, alias="File", description="The document file to convert. Accepts either a URL reference or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the generated output file(s). The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., `_0`, `_1`) when multiple files are generated from a single input."),
    background_color: str | None = Field(None, alias="BackgroundColor", description="The background color applied to transparent areas in the converted images. Accepts color names, RGB values (comma-separated), HEX codes, or the value `transparent` to preserve transparency."),
) -> dict[str, Any] | ToolResult:
    """Converts ODF (OpenDocument Format) documents to PNG images. Supports customization of output filename and background color for transparent areas."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertOdfToPngRequest(
            body=_models.PostConvertOdfToPngRequestBody(file_=file_, file_name=file_name, background_color=background_color)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_document_to_png: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/odf/to/png"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_document_to_png")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_document_to_png", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_document_to_png",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_odg_to_pdf(
    file_: str | None = Field(None, alias="File", description="The ODG file to convert. Can be provided as a file upload (binary content) or as a URL pointing to the source file."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., `document_0.pdf`, `document_1.pdf`) when multiple files are generated."),
    pdfa_version: Literal["none", "pdfA1b", "pdfA2b", "pdfA3b"] | None = Field(None, alias="PdfaVersion", description="Specifies the PDF/A compliance version for the output file. Use 'none' for standard PDF, or select a PDF/A version for archival compliance."),
) -> dict[str, Any] | ToolResult:
    """Converts an ODG (OpenDocument Graphics) file to PDF format with optional PDF/A compliance. Supports both file uploads and URL-based file sources."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertOdgToPdfRequest(
            body=_models.PostConvertOdgToPdfRequestBody(file_=file_, file_name=file_name, pdfa_version=pdfa_version)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_odg_to_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/odg/to/pdf"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_odg_to_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_odg_to_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_odg_to_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_presentation_to_jpg(
    file_: str | None = Field(None, alias="File", description="The presentation file to convert. Accepts either a file upload (binary content) or a URL pointing to the ODP file."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output JPG file(s). The API automatically sanitizes the filename, appends the correct extension, and adds numeric indexing (e.g., presentation_0.jpg, presentation_1.jpg) when multiple images are generated from slides."),
) -> dict[str, Any] | ToolResult:
    """Converts an ODP (OpenDocument Presentation) file to JPG image format. Supports both file uploads and URL-based sources, generating one or more JPG images from the presentation slides."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertOdpToJpgRequest(
            body=_models.PostConvertOdpToJpgRequestBody(file_=file_, file_name=file_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_presentation_to_jpg: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/odp/to/jpg"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_presentation_to_jpg")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_presentation_to_jpg", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_presentation_to_jpg",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_odp_to_pdf(
    file_: str | None = Field(None, alias="File", description="The ODP file to convert. Accepts either a URL pointing to the file or the raw file content as binary data."),
    file_name: str | None = Field(None, alias="FileName", description="Custom name for the output PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., `_0`, `_1`) if multiple files are generated from a single input."),
    pdfa_version: Literal["none", "pdfA1b", "pdfA2b", "pdfA3b"] | None = Field(None, alias="PdfaVersion", description="Specifies the PDF/A compliance version for the output file. Use 'none' for standard PDF, or select a PDF/A version for archival compliance."),
) -> dict[str, Any] | ToolResult:
    """Converts an ODP (OpenDocument Presentation) file to PDF format with optional PDF/A compliance. Supports file input via URL or direct file content and allows customization of output filename and PDF/A version."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertOdpToPdfRequest(
            body=_models.PostConvertOdpToPdfRequestBody(file_=file_, file_name=file_name, pdfa_version=pdfa_version)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_odp_to_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/odp/to/pdf"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_odp_to_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_odp_to_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_odp_to_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_presentation_to_png(
    file_: str | None = Field(None, alias="File", description="The ODP file to convert. Accepts either a URL pointing to the file or the raw file content as binary data."),
    file_name: str | None = Field(None, alias="FileName", description="Custom name for the output PNG file(s). The system automatically sanitizes the name, appends the correct file extension, and adds numeric indexing (e.g., `presentation_0.png`, `presentation_1.png`) when multiple files are generated from a single input."),
    background_color: str | None = Field(None, alias="BackgroundColor", description="Background color applied to transparent areas in the generated PNG images. Accepts color names (e.g., `white`, `black`), RGB format (comma-separated values 0-255), HEX format (with # prefix), or `transparent` to preserve transparency."),
) -> dict[str, Any] | ToolResult:
    """Converts ODP (OpenDocument Presentation) files to PNG image format. Supports file input via URL or direct file content, with optional background color customization for transparent areas."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertOdpToPngRequest(
            body=_models.PostConvertOdpToPngRequestBody(file_=file_, file_name=file_name, background_color=background_color)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_presentation_to_png: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/odp/to/png"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_presentation_to_png")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_presentation_to_png", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_presentation_to_png",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_spreadsheet_to_image(
    file_: str | None = Field(None, alias="File", description="The spreadsheet file to convert, provided either as a URL or raw binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the generated output image file. The system automatically sanitizes the filename, appends the correct JPG extension, and adds numeric indexing (e.g., output_0.jpg, output_1.jpg) if multiple images are generated from a single input."),
) -> dict[str, Any] | ToolResult:
    """Converts an ODS (OpenDocument Spreadsheet) file to JPG image format. Accepts file input as a URL or binary content and generates a named output image file."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertOdsToJpgRequest(
            body=_models.PostConvertOdsToJpgRequestBody(file_=file_, file_name=file_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_spreadsheet_to_image: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/ods/to/jpg"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_spreadsheet_to_image")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_spreadsheet_to_image", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_spreadsheet_to_image",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_ods_to_pdf(
    file_: str | None = Field(None, alias="File", description="The ODS file to convert. Can be provided as a file upload or as a URL pointing to the source file."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the generated PDF output file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., `report_0.pdf`, `report_1.pdf`) when multiple files are generated from a single input."),
    pdfa_version: Literal["none", "pdfA1b", "pdfA2b", "pdfA3b"] | None = Field(None, alias="PdfaVersion", description="Specifies the PDF/A compliance version for the output file. PDF/A versions provide long-term archival compatibility. Use 'none' for standard PDF output without PDF/A compliance."),
) -> dict[str, Any] | ToolResult:
    """Converts an ODS (OpenDocument Spreadsheet) file to PDF format with optional PDF/A compliance. Supports both file uploads and URL-based file sources."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertOdsToPdfRequest(
            body=_models.PostConvertOdsToPdfRequestBody(file_=file_, file_name=file_name, pdfa_version=pdfa_version)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_ods_to_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/ods/to/pdf"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_ods_to_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_ods_to_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_ods_to_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_ods_to_png(
    file_: str | None = Field(None, alias="File", description="The ODS file to convert. Accepts either a URL pointing to the file or the raw file content as binary data."),
    file_name: str | None = Field(None, alias="FileName", description="Custom name for the output PNG file(s). The system automatically sanitizes the name, appends the correct file extension, and adds numeric indexing (e.g., `report_0.png`, `report_1.png`) when multiple files are generated from a single input."),
    background_color: str | None = Field(None, alias="BackgroundColor", description="Background color for the generated PNG image. Specify a color name (e.g., `white`, `black`), RGB format (e.g., `255,0,0`), or HEX format (e.g., `#FF0000`). Use `transparent` to preserve transparency."),
) -> dict[str, Any] | ToolResult:
    """Converts an ODS (OpenDocument Spreadsheet) file to PNG image format. Supports file input via URL or direct content, with customizable output naming and background color options."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertOdsToPngRequest(
            body=_models.PostConvertOdsToPngRequestBody(file_=file_, file_name=file_name, background_color=background_color)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_ods_to_png: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/ods/to/png"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_ods_to_png")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_ods_to_png", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_ods_to_png",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_document_odt_to_docx(
    file_: str | None = Field(None, alias="File", description="The document file to convert. Accepts either a URL pointing to the file or the raw file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output DOCX file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.docx, filename_1.docx) for multiple output files."),
    password: str | None = Field(None, alias="Password", description="Password required to open the input document if it is password-protected."),
    update_toc: bool | None = Field(None, alias="UpdateToc", description="Whether to automatically update all tables of content in the converted document."),
    update_references: bool | None = Field(None, alias="UpdateReferences", description="Whether to automatically update all reference fields in the converted document."),
) -> dict[str, Any] | ToolResult:
    """Converts an ODT (OpenDocument Text) document to DOCX (Microsoft Word) format. Supports password-protected documents and optional updates to tables of content and reference fields."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertOdtToDocxRequest(
            body=_models.PostConvertOdtToDocxRequestBody(file_=file_, file_name=file_name, password=password, update_toc=update_toc, update_references=update_references)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_document_odt_to_docx: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/odt/to/docx"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_document_odt_to_docx")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_document_odt_to_docx", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_document_odt_to_docx",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_document_to_jpg_text(
    file_: str | None = Field(None, alias="File", description="The document file to convert. Can be provided as a URL reference or raw file content in binary format."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output JPG file(s). The API automatically sanitizes the filename, appends the correct extension, and adds numeric indexing (e.g., document_0.jpg, document_1.jpg) when multiple output files are generated from a single input."),
) -> dict[str, Any] | ToolResult:
    """Converts an ODT (OpenDocument Text) document to JPG image format. Supports both file uploads and URL-based file sources."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertOdtToJpgRequest(
            body=_models.PostConvertOdtToJpgRequestBody(file_=file_, file_name=file_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_document_to_jpg_text: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/odt/to/jpg"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_document_to_jpg_text")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_document_to_jpg_text", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_document_to_jpg_text",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_document_to_pdf_odt(
    file_: str | None = Field(None, alias="File", description="The document file to convert. Can be provided as a file upload (binary content) or as a URL pointing to the source document."),
    file_name: str | None = Field(None, alias="FileName", description="Custom name for the generated output PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds numeric indexing (e.g., filename_0.pdf, filename_1.pdf) when multiple files are generated from a single input."),
    pdfa_version: Literal["none", "pdfA1b", "pdfA2b", "pdfA3b"] | None = Field(None, alias="PdfaVersion", description="PDF/A compliance version for the output file. Select 'none' for standard PDF, or choose a PDF/A version (1b, 2b, or 3b) for long-term archival compliance."),
) -> dict[str, Any] | ToolResult:
    """Converts an ODT (OpenDocument Text) document to PDF format with optional PDF/A compliance. Supports both file uploads and URL-based sources, with customizable output naming and PDF/A version selection."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertOdtToPdfRequest(
            body=_models.PostConvertOdtToPdfRequestBody(file_=file_, file_name=file_name, pdfa_version=pdfa_version)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_document_to_pdf_odt: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/odt/to/pdf"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_document_to_pdf_odt")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_document_to_pdf_odt", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_document_to_pdf_odt",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_document_to_png_text(
    file_: str | None = Field(None, alias="File", description="The ODT file to convert. Accepts either a file URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Custom name for the output PNG file(s). The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., `output_0.png`, `output_1.png`) for multiple files to ensure unique, safe naming."),
    background_color: str | None = Field(None, alias="BackgroundColor", description="Background color for transparent areas in the converted images. Accepts color names (e.g., `white`, `black`), RGB format (e.g., `255,0,0`), HEX format (e.g., `#FF0000`), or `transparent` to preserve transparency."),
) -> dict[str, Any] | ToolResult:
    """Converts ODT (OpenDocument Text) files to PNG images. Supports file input via URL or direct content, with optional background color customization for transparent areas."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertOdtToPngRequest(
            body=_models.PostConvertOdtToPngRequestBody(file_=file_, file_name=file_name, background_color=background_color)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_document_to_png_text: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/odt/to/png"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_document_to_png_text")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_document_to_png_text", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_document_to_png_text",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_document_odt_to_txt(
    file_: str | None = Field(None, alias="File", description="The ODT document to convert. Accepts either a file URL or raw file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output text file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.txt, output_1.txt) for multiple files."),
    password: str | None = Field(None, alias="Password", description="Password required to open password-protected ODT documents."),
    substitutions: bool | None = Field(None, alias="Substitutions", description="When enabled, replaces special symbols with their text equivalents (e.g., © becomes (c))."),
    end_line_char: Literal["crlf", "cr", "lfcr", "lf"] | None = Field(None, alias="EndLineChar", description="Specifies the line ending character to use in the output text file."),
) -> dict[str, Any] | ToolResult:
    """Converts ODT (OpenDocument Text) documents to plain text format. Supports password-protected documents, symbol substitution, and configurable line ending characters."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertOdtToTxtRequest(
            body=_models.PostConvertOdtToTxtRequestBody(file_=file_, file_name=file_name, password=password, substitutions=substitutions, end_line_char=end_line_char)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_document_odt_to_txt: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/odt/to/txt"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_document_odt_to_txt")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_document_odt_to_txt", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_document_odt_to_txt",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_document_to_xml(
    file_: str | None = Field(None, alias="File", description="The document file to convert. Accepts either a file URL or raw file content in binary format."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output XML file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., document_0.xml, document_1.xml) when multiple files are generated."),
    password: str | None = Field(None, alias="Password", description="Password required to open the input document if it is password-protected."),
    update_toc: bool | None = Field(None, alias="UpdateToc", description="When enabled, automatically updates all tables of content in the document during conversion."),
    update_references: bool | None = Field(None, alias="UpdateReferences", description="When enabled, automatically updates all reference fields in the document during conversion."),
    xml_type: Literal["word2003", "flatWordXml", "strictOpenXml"] | None = Field(None, alias="XmlType", description="Specifies the XML schema format to use for the output. Word2003 uses legacy XML, flatWordXml uses a flat structure, and strictOpenXml uses the modern Office Open XML standard."),
) -> dict[str, Any] | ToolResult:
    """Converts an ODT (OpenDocument Text) document to XML format with optional support for updating tables of content and reference fields. Supports password-protected documents and multiple XML output formats."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertOdtToXmlRequest(
            body=_models.PostConvertOdtToXmlRequestBody(file_=file_, file_name=file_name, password=password, update_toc=update_toc, update_references=update_references, xml_type=xml_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_document_to_xml: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/odt/to/xml"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_document_to_xml")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_document_to_xml", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_document_to_xml",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_office_document_to_pdf(
    file_: str | None = Field(None, alias="File", description="The document file to convert. Can be provided as a file upload (binary content) or as a URL pointing to the document."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the generated PDF output file. The system automatically sanitizes the filename, appends the correct extension, and adds numeric suffixes (e.g., _0, _1) when multiple files are generated from a single input."),
    password: str | None = Field(None, alias="Password", description="Password required to open password-protected documents. Only needed if the input document is encrypted."),
    pdfa: bool | None = Field(None, alias="Pdfa", description="When enabled, generates a PDF/A-1b compliant document suitable for long-term archival and preservation."),
) -> dict[str, Any] | ToolResult:
    """Converts office documents (Word, Excel, PowerPoint, etc.) to PDF format with optional password protection and PDF/A compliance. Supports both file uploads and URL-based document sources."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertOfficeToPdfRequest(
            body=_models.PostConvertOfficeToPdfRequestBody(file_=file_, file_name=file_name, password=password, pdfa=pdfa)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_office_document_to_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/office/to/pdf"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_office_document_to_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_office_document_to_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_office_document_to_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_pages_to_docx(
    file_: str | None = Field(None, alias="File", description="The Pages document to convert, provided as either a URL reference or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the generated DOCX output file. The API automatically sanitizes the filename, appends the correct extension, and adds numeric indexing (e.g., document_0.docx, document_1.docx) when multiple files are produced from a single input."),
) -> dict[str, Any] | ToolResult:
    """Converts a Pages document to DOCX format. Accepts file input as a URL or binary content and generates a properly named output file."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPagesToDocxRequest(
            body=_models.PostConvertPagesToDocxRequestBody(file_=file_, file_name=file_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_pages_to_docx: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/pages/to/docx"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_pages_to_docx")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_pages_to_docx", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_pages_to_docx",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_pages_to_text(
    file_: str | None = Field(None, alias="File", description="The document file to convert. Can be provided as a URL or raw file content in binary format."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the generated output file(s). The system automatically sanitizes the filename, appends the correct extension for the target format, and adds numeric indexing (e.g., `output_0.txt`, `output_1.txt`) when multiple files are generated from a single input."),
) -> dict[str, Any] | ToolResult:
    """Converts document pages to plain text format. Supports file uploads via URL or direct file content and generates appropriately named output files."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPagesToTxtRequest(
            body=_models.PostConvertPagesToTxtRequestBody(file_=file_, file_name=file_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_pages_to_text: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/pages/to/txt"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_pages_to_text")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_pages_to_text", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_pages_to_text",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def compress_pdf(
    file_: str | None = Field(None, alias="File", description="The PDF file to compress. Accepts either a file URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output compressed PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.pdf, filename_1.pdf) for multiple output files."),
    password: str | None = Field(None, alias="Password", description="Password required to open the PDF if it is password-protected."),
    preset: Literal["none", "lossless", "text", "archive", "web", "ebook", "printer"] | None = Field(None, alias="Preset", description="Predefined compression profile optimized for specific use cases. When selected, all other compression options are ignored. Choose 'none' for no compression or select a preset tailored to your needs (lossless preserves quality, text optimizes for documents, web reduces file size for online sharing, etc.)."),
    unembed_base_fonts: bool | None = Field(None, alias="UnembedBaseFonts", description="Remove standard base fonts from the PDF to reduce file size. Embedded fonts will be substituted with system fonts on viewing."),
    subset_embedded_fonts: bool | None = Field(None, alias="SubsetEmbeddedFonts", description="Subset embedded fonts to include only characters actually used in the document, removing unused glyphs to reduce file size."),
    remove_forms: bool | None = Field(None, alias="RemoveForms", description="Remove all interactive form fields from the PDF document."),
    remove_duplicates: bool | None = Field(None, alias="RemoveDuplicates", description="Remove duplicate font definitions and color profiles to eliminate redundant data."),
    optimize: bool | None = Field(None, alias="Optimize", description="Optimize page content streams to reduce file size and improve rendering efficiency."),
    remove_piece_information: bool | None = Field(None, alias="RemovePieceInformation", description="Remove private metadata dictionaries from design applications (Adobe Illustrator, Photoshop, etc.) that are not essential for document display."),
    remove_embedded_files: bool | None = Field(None, alias="RemoveEmbeddedFiles", description="Remove embedded files and attachments from the PDF document."),
    remove_structure_information: bool | None = Field(None, alias="RemoveStructureInformation", description="Remove all structural information and tagging used for accessibility and document organization."),
    remove_metadata: bool | None = Field(None, alias="RemoveMetadata", description="Remove XMP metadata and document properties embedded in the PDF catalog and marked content."),
    remove_unused_resources: bool | None = Field(None, alias="RemoveUnusedResources", description="Remove unused resource references such as fonts, images, and patterns that are defined but not displayed in the document."),
    linearize: bool | None = Field(None, alias="Linearize", description="Linearize the PDF structure and optimize for fast web viewing, enabling progressive rendering as the file downloads."),
    preserve_pdfa: bool | None = Field(None, alias="PreservePdfa", description="Maintain PDF/A compliance standards during compression to ensure long-term archival compatibility."),
) -> dict[str, Any] | ToolResult:
    """Compress a PDF file using configurable optimization techniques to reduce file size while preserving document quality. Supports preset compression profiles or granular control over specific compression options."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPdfToCompressRequest(
            body=_models.PostConvertPdfToCompressRequestBody(file_=file_, file_name=file_name, password=password, preset=preset, unembed_base_fonts=unembed_base_fonts, subset_embedded_fonts=subset_embedded_fonts, remove_forms=remove_forms, remove_duplicates=remove_duplicates, optimize=optimize, remove_piece_information=remove_piece_information, remove_embedded_files=remove_embedded_files, remove_structure_information=remove_structure_information, remove_metadata=remove_metadata, remove_unused_resources=remove_unused_resources, linearize=linearize, preserve_pdfa=preserve_pdfa)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for compress_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/pdf/to/compress"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("compress_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("compress_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="compress_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def crop_pdf(
    file_: str | None = Field(None, alias="File", description="The PDF file to crop. Accepts a file URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output file(s). The API sanitizes the filename, appends the correct extension, and adds indexing for multiple outputs (e.g., report_0.pdf, report_1.pdf)."),
    password: str | None = Field(None, alias="Password", description="Password to unlock a protected PDF file."),
    page_range: str | None = Field(None, alias="PageRange", description="Specifies which pages to crop using page numbers, ranges, or keywords. Supports comma-separated values and ranges (e.g., 1,2,5-last)."),
    crop_mode: Literal["auto", "size", "margins"] | None = Field(None, alias="CropMode", description="Cropping strategy: automatic content detection, fixed margins, or exact dimensions."),
    measurement_unit: Literal["pt", "in", "mm", "cm"] | None = Field(None, alias="MeasurementUnit", description="Unit of measurement for width, height, and margin values."),
    auto_strategy: Literal["perPage", "uniform"] | None = Field(None, alias="AutoStrategy", description="Determines whether automatic cropping is applied individually per page or uniformly across all pages. Only applies when CropMode is set to auto."),
    auto_padding: float | None = Field(None, alias="AutoPadding", description="Padding distance to add around automatically detected content, using the selected measurement unit. Only applies when CropMode is set to auto.", ge=0, le=30000),
    anchor: Literal["center", "topleft", "top", "topright", "left", "right", "bottom", "bottomright"] | None = Field(None, alias="Anchor", description="Reference point for positioning the crop rectangle when using fixed width and height dimensions."),
    vertical_margin: float | None = Field(None, alias="VerticalMargin", description="Top and bottom margin distances to apply when cropping with margins, using the selected measurement unit. Only applies when CropMode is set to margins.", ge=0, le=30000),
    horizontal_margin: float | None = Field(None, alias="HorizontalMargin", description="Left and right margin distances to apply when cropping with margins, using the selected measurement unit. Only applies when CropMode is set to margins.", ge=0, le=30000),
) -> dict[str, Any] | ToolResult:
    """Crop PDF pages by automatically detecting content, applying margins, or resizing to specific dimensions. Supports selective page ranges and multiple cropping strategies."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPdfToCropRequest(
            body=_models.PostConvertPdfToCropRequestBody(file_=file_, file_name=file_name, password=password, page_range=page_range, crop_mode=crop_mode, measurement_unit=measurement_unit, auto_strategy=auto_strategy, auto_padding=auto_padding, anchor=anchor, vertical_margin=vertical_margin, horizontal_margin=horizontal_margin)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for crop_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/pdf/to/crop"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("crop_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("crop_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="crop_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_pdf_to_csv(
    file_: str | None = Field(None, alias="File", description="The PDF file to convert. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output CSV file. The system sanitizes the filename, appends the correct extension, and adds indexing (e.g., report_0.csv, report_1.csv) for multiple output files."),
    password: str | None = Field(None, alias="Password", description="Password required to open password-protected PDF documents."),
    page_range: str | None = Field(None, alias="PageRange", description="Specifies which pages to convert using a range (e.g., 1-10) or comma-separated list (e.g., 1,2,5)."),
    enable_ocr: Literal["Scanned", "All", "None"] | None = Field(None, alias="EnableOcr", description="Controls optical character recognition behavior. Use 'Scanned' for OCR on scanned pages only, 'All' for all pages, or 'None' to disable OCR."),
    ocr_language: Literal["ar", "ca", "zh-cn", "zh-tw", "da", "nl", "en", "fi", "fa", "de", "el", "he", "it", "ja", "ko", "lt", "no", "pl", "pt", "ro", "ru", "sl", "es", "sv", "tr", "ua", "th"] | None = Field(None, alias="OcrLanguage", description="Language for OCR processing. Supports multiple languages including English, Spanish, Chinese, Arabic, and others. Contact support to request additional languages."),
    delimiter: str | None = Field(None, alias="Delimiter", description="Character used to separate fields in the output CSV file."),
) -> dict[str, Any] | ToolResult:
    """Converts a PDF document to CSV format with support for password-protected files, selective page ranges, and optical character recognition. Automatically handles file naming and delimiter configuration for structured data extraction."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPdfToCsvRequest(
            body=_models.PostConvertPdfToCsvRequestBody(file_=file_, file_name=file_name, password=password, page_range=page_range, enable_ocr=enable_ocr, ocr_language=ocr_language, delimiter=delimiter)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_pdf_to_csv: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/pdf/to/csv"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_pdf_to_csv")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_pdf_to_csv", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_pdf_to_csv",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def delete_pdf_pages(
    file_: str | None = Field(None, alias="File", description="The PDF file to process. Accepts a file URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., document_0.pdf, document_1.pdf) for multiple output files."),
    password: str | None = Field(None, alias="Password", description="Password required to open password-protected PDF documents."),
    page_range: str | None = Field(None, alias="PageRange", description="Pages to delete specified as a range (e.g., 1-10) or comma-separated individual page numbers (e.g., 1,2,5)."),
    delete_blank_pages: bool | None = Field(None, alias="DeleteBlankPages", description="Automatically detect and remove blank pages from the PDF."),
) -> dict[str, Any] | ToolResult:
    """Remove specified pages from a PDF document. Supports deletion by page range, individual pages, or automatic blank page detection."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPdfToDeletePagesRequest(
            body=_models.PostConvertPdfToDeletePagesRequestBody(file_=file_, file_name=file_name, password=password, page_range=page_range, delete_blank_pages=delete_blank_pages)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_pdf_pages: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/pdf/to/delete-pages"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_pdf_pages")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_pdf_pages", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_pdf_pages",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_pdf_to_docx(
    file_: str | None = Field(None, alias="File", description="The PDF file to convert. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output DOCX file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.docx, filename_1.docx) for multiple output files."),
    password: str | None = Field(None, alias="Password", description="Password required to open password-protected PDF documents."),
    page_range: str | None = Field(None, alias="PageRange", description="Specifies which pages to convert using a range (e.g., 1-10) or comma-separated list (e.g., 1,2,5). Defaults to the first 2000 pages."),
    wysiwyg: bool | None = Field(None, alias="Wysiwyg", description="When enabled, preserves exact PDF formatting by converting layout elements to editable text boxes in the DOCX output."),
    ocr_mode: Literal["auto", "force", "never"] | None = Field(None, alias="OcrMode", description="Controls OCR application during conversion. Use 'auto' to apply OCR only when needed, 'force' to OCR all pages, or 'never' to disable OCR entirely."),
    ocr_language: Literal["auto", "ar", "ca", "zh", "da", "nl", "en", "fi", "fr", "de", "el", "ko", "it", "ja", "no", "pl", "pt", "ro", "ru", "sl", "es", "sv", "tr", "ua", "th"] | None = Field(None, alias="OcrLanguage", description="Specifies the language for OCR text recognition. Use 'auto' for automatic detection, or manually select a language code if auto-detection fails."),
    annotations_: Literal["textBox", "comment", "none"] | None = Field(None, alias="Annotations", description="Determines how PDF annotations are handled in the output. Use 'textBox' to convert annotations to editable text boxes, 'comment' to convert them to Word comments, or 'none' to exclude annotations."),
) -> dict[str, Any] | ToolResult:
    """Converts a PDF document to DOCX format with support for password-protected files, selective page ranges, OCR processing, and annotation handling. Preserves formatting through text box conversion and supports multiple OCR languages for accurate text recognition."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPdfToDocxRequest(
            body=_models.PostConvertPdfToDocxRequestBody(file_=file_, file_name=file_name, password=password, page_range=page_range, wysiwyg=wysiwyg, ocr_mode=ocr_mode, ocr_language=ocr_language, annotations_=annotations_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_pdf_to_docx: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/pdf/to/docx"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_pdf_to_docx")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_pdf_to_docx", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_pdf_to_docx",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def extract_data_from_pdf(
    file_: str | None = Field(None, alias="File", description="The PDF file to process. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output file(s). The system sanitizes the filename, appends the appropriate extension, and adds indexing (e.g., report_0.pdf, report_1.pdf) for multiple outputs to ensure unique, safe file naming."),
    password: str | None = Field(None, alias="Password", description="Password required to open password-protected PDF documents."),
    document_type: Literal["auto", "invoice", "receipt", "contract", "identification", "financial", "form", "manual"] | None = Field(None, alias="DocumentType", description="Document category to apply optimized extraction rules. Use 'Auto' for automatic detection, select a specific type (Invoice, Receipt, Contract, etc.) for improved accuracy, or choose 'Manual' to use only custom extraction fields."),
    custom_extraction_data: str | None = Field(None, alias="CustomExtractionData", description="JSON array of custom field definitions for extraction. Each object specifies a FieldName (output key) and Extract (description of what to extract). Used when DocumentType is 'Manual' or to supplement predefined extraction."),
    minimum_confidence: float | None = Field(None, alias="MinimumConfidence", description="Minimum confidence score (0.01 to 0.99) for AI-based sensitive data detection. Higher values reduce false positives but may miss subtle matches.", ge=0.01, le=0.99),
) -> dict[str, Any] | ToolResult:
    """Extract structured data from PDF documents using AI-powered recognition. Supports predefined document types (invoices, receipts, contracts, etc.) or custom field extraction with configurable confidence thresholds."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPdfToExtractRequest(
            body=_models.PostConvertPdfToExtractRequestBody(file_=file_, file_name=file_name, password=password, document_type=document_type, custom_extraction_data=custom_extraction_data, minimum_confidence=minimum_confidence)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for extract_data_from_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/pdf/to/extract"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("extract_data_from_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("extract_data_from_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="extract_data_from_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def extract_images_from_pdf(
    file_: str | None = Field(None, alias="File", description="The PDF file to process. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output file(s). The API sanitizes the filename, appends the appropriate extension, and adds indexing (e.g., filename_0, filename_1) for multiple outputs."),
    password: str | None = Field(None, alias="Password", description="Password for opening password-protected PDF documents."),
    page_range: str | None = Field(None, alias="PageRange", description="Specifies which pages to process. Use ranges (e.g., 1-10) or comma-separated individual pages (e.g., 1,2,5)."),
    image_output_format: Literal["default", "jpg", "png", "tiff"] | None = Field(None, alias="ImageOutputFormat", description="Output format for extracted images. Use 'default' to automatically select the most suitable format and extract all images including hidden ones; other formats apply the MinimumImageWidth and MinimumImageHeight filters."),
    minimum_image_width: int | None = Field(None, alias="MinimumImageWidth", description="Minimum width in pixels for extracted images. Images narrower than this threshold are excluded.", ge=0, le=1000),
    minimum_image_height: int | None = Field(None, alias="MinimumImageHeight", description="Minimum height in pixels for extracted images. Images shorter than this threshold are excluded.", ge=0, le=1000),
) -> dict[str, Any] | ToolResult:
    """Extract images from PDF documents with configurable filtering by size and page range. Supports password-protected PDFs and multiple output formats."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPdfToExtractImagesRequest(
            body=_models.PostConvertPdfToExtractImagesRequestBody(file_=file_, file_name=file_name, password=password, page_range=page_range, image_output_format=image_output_format, minimum_image_width=minimum_image_width, minimum_image_height=minimum_image_height)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for extract_images_from_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/pdf/to/extract-images"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("extract_images_from_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("extract_images_from_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="extract_images_from_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def extract_pdf_form_fields(
    file_: str | None = Field(None, alias="File", description="The PDF file to convert. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output FDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.fdf, output_1.fdf) for multiple files to ensure unique, safe naming."),
    password: str | None = Field(None, alias="Password", description="Password required to open password-protected PDF documents."),
    include_alternate_names: bool | None = Field(None, alias="IncludeAlternateNames", description="When enabled, includes alternate field names (tooltip text) from the PDF in the FDF output for better field identification."),
) -> dict[str, Any] | ToolResult:
    """Converts a PDF document to FDF (Forms Data Format) while extracting form field data. Optionally includes alternate field names as tooltips in the output."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPdfToFdfExtractRequest(
            body=_models.PostConvertPdfToFdfExtractRequestBody(file_=file_, file_name=file_name, password=password, include_alternate_names=include_alternate_names)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for extract_pdf_form_fields: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/pdf/to/fdf-extract"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("extract_pdf_form_fields")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("extract_pdf_form_fields", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="extract_pdf_form_fields",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def import_pdf_with_fdf_form_data(
    file_: str | None = Field(None, alias="File", description="The PDF file to be converted. Accepts either a URL reference or binary file content."),
    fdf_file: str | None = Field(None, alias="FdfFile", description="The FDF (Forms Data Format) file containing structured form field data to be imported into the PDF. Accepts either a URL reference or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output file(s) generated by the conversion. The system automatically sanitizes the filename, appends the appropriate file extension, and adds numeric indexing (e.g., `_0`, `_1`) when multiple output files are generated from a single input."),
    password: str | None = Field(None, alias="Password", description="Password required to open password-protected PDF documents. Only needed if the input PDF is encrypted."),
) -> dict[str, Any] | ToolResult:
    """Convert a PDF document by importing and merging structured form data from an FDF file. This operation combines a PDF with FDF form data to populate form fields and generate the merged output."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPdfToFdfImportRequest(
            body=_models.PostConvertPdfToFdfImportRequestBody(file_=file_, fdf_file=fdf_file, file_name=file_name, password=password)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for import_pdf_with_fdf_form_data: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/pdf/to/fdf-import"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("import_pdf_with_fdf_form_data")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("import_pdf_with_fdf_form_data", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="import_pdf_with_fdf_form_data",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File", "FdfFile"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def flatten_pdf(
    file_: str | None = Field(None, alias="File", description="The PDF file to be flattened. Accepts either a URL reference or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.pdf, filename_1.pdf) for multiple output files to ensure unique and safe file naming."),
    password: str | None = Field(None, alias="Password", description="Password required to open a protected or encrypted PDF document."),
    flatten_controls: bool | None = Field(None, alias="FlattenControls", description="Convert form controls (text fields, checkboxes, dropdowns) into static content, preventing editing while maintaining their original visual appearance."),
    flatten_widgets: bool | None = Field(None, alias="FlattenWidgets", description="Convert widget annotations (buttons, list boxes, signature fields) into static content, removing interactivity while preserving their original visual appearance."),
    flatten_text: bool | None = Field(None, alias="FlattenText", description="Convert text into vectorial paths to prevent text selection, copying, and extraction, making the PDF read-only while maintaining original vector quality."),
) -> dict[str, Any] | ToolResult:
    """Convert a PDF document into a flattened format by removing interactivity from form controls, widgets, and text elements. This operation transforms editable and interactive PDF components into static page content while preserving visual appearance."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPdfToFlattenRequest(
            body=_models.PostConvertPdfToFlattenRequestBody(file_=file_, file_name=file_name, password=password, flatten_controls=flatten_controls, flatten_widgets=flatten_widgets, flatten_text=flatten_text)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for flatten_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/pdf/to/flatten"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("flatten_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("flatten_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="flatten_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_pdf_to_html(
    file_: str | None = Field(None, alias="File", description="The PDF file to convert. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output HTML file(s). The system sanitizes the filename, appends the correct extension, and adds indexing (e.g., report_0.html, report_1.html) for multiple output files."),
    password: str | None = Field(None, alias="Password", description="Password required to open password-protected PDF documents."),
    page_range: str | None = Field(None, alias="PageRange", description="Specifies which pages to convert using a range (e.g., 1-10) or comma-separated list (e.g., 1,2,5). Defaults to the first 2000 pages."),
    wysiwyg: bool | None = Field(None, alias="Wysiwyg", description="When enabled, preserves exact PDF formatting by converting text to HTML text boxes. Maintains visual layout fidelity during conversion."),
    ocr_mode: Literal["auto", "force", "never"] | None = Field(None, alias="OcrMode", description="Controls OCR application during conversion. Auto applies OCR only when needed, Force applies OCR to all pages, and Never disables OCR entirely."),
    ocr_language: Literal["auto", "ar", "ca", "zh", "da", "nl", "en", "fi", "fr", "de", "el", "ko", "it", "ja", "no", "pl", "pt", "ro", "ru", "sl", "es", "sv", "tr", "ua", "th"] | None = Field(None, alias="OcrLanguage", description="Specifies the language for OCR text recognition. Use auto-detection by default, or manually select a language if auto-detection fails."),
) -> dict[str, Any] | ToolResult:
    """Converts PDF documents to HTML format with support for password-protected files, selective page ranges, and optical character recognition. Preserves formatting using text boxes and offers flexible OCR configuration for accurate text extraction."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPdfToHtmlRequest(
            body=_models.PostConvertPdfToHtmlRequestBody(file_=file_, file_name=file_name, password=password, page_range=page_range, wysiwyg=wysiwyg, ocr_mode=ocr_mode, ocr_language=ocr_language)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_pdf_to_html: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/pdf/to/html"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_pdf_to_html")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_pdf_to_html", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_pdf_to_html",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def add_watermark_to_pdf(
    file_: str | None = Field(None, alias="File", description="The PDF file to convert. Accepts a file URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output image file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing for multiple outputs to ensure unique, safe file naming."),
    password: str | None = Field(None, alias="Password", description="Password required to open password-protected PDF documents."),
    image_file: str | None = Field(None, alias="ImageFile", description="Image file to use as the watermark. Accepts a file URL or binary image content."),
    page_range: str | None = Field(None, alias="PageRange", description="Specifies which pages to process. Use ranges (e.g., 1-10) or comma-separated page numbers (e.g., 1,2,5)."),
    opacity: int | None = Field(None, alias="Opacity", description="Controls the transparency of the watermark, where 0 is fully transparent and 100 is fully opaque.", ge=0, le=100),
    style: Literal["stamp", "watermark"] | None = Field(None, alias="Style", description="Determines watermark placement: 'stamp' overlays the watermark on top of page content, while 'watermark' places it behind the content."),
    go_to_link: str | None = Field(None, alias="GoToLink", description="Web address to navigate to when the watermark is clicked."),
    go_to_page: str | None = Field(None, alias="GoToPage", description="Page number to navigate to when the watermark is clicked."),
    page_rotation: bool | None = Field(None, alias="PageRotation", description="When enabled, the watermark rotates with the PDF page. When disabled, the watermark maintains its original orientation regardless of page rotation."),
    page_box: Literal["mediabox", "trimbox", "bleedbox", "cropbox"] | None = Field(None, alias="PageBox", description="Defines the PDF page area used as the reference for watermark placement (mediabox is the full page, trimbox excludes margins, bleedbox is for printing, cropbox is the visible area)."),
    horizontal_alignment: Literal["left", "center", "right"] | None = Field(None, alias="HorizontalAlignment", description="Horizontal alignment of the watermark on the page."),
    vertical_alignment: Literal["top", "center", "bottom"] | None = Field(None, alias="VerticalAlignment", description="Vertical alignment of the watermark on the page."),
    measurement_unit: Literal["pt", "in", "mm", "cm"] | None = Field(None, alias="MeasurementUnit", description="Unit of measurement used for watermark position and size parameters."),
    offset: str | None = Field(None, alias="Offset", description="Watermark offset as a coordinate pair in the format 'x,y' using the selected MeasurementUnit. Positive X moves right, negative left. Positive Y moves down, negative up."),
) -> dict[str, Any] | ToolResult:
    """Convert a PDF document to images with an optional watermark overlay or stamp. Supports customizable watermark positioning, styling, opacity, and interactive click-through functionality."""

    # Call helper functions
    offset_parsed = parse_offset(offset)

    # Construct request model with validation
    try:
        _request = _models.PostConvertPdfToImageWatermarkRequest(
            body=_models.PostConvertPdfToImageWatermarkRequestBody(file_=file_, file_name=file_name, password=password, image_file=image_file, page_range=page_range, opacity=opacity, style=style, go_to_link=go_to_link, go_to_page=go_to_page, page_rotation=page_rotation, page_box=page_box, horizontal_alignment=horizontal_alignment, vertical_alignment=vertical_alignment, measurement_unit=measurement_unit, offset_x=offset_parsed.get('OffsetX') if offset_parsed else None, offset_y=offset_parsed.get('OffsetY') if offset_parsed else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_watermark_to_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/pdf/to/image-watermark"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_watermark_to_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_watermark_to_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_watermark_to_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File", "ImageFile"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_pdf_to_jpg(
    file_: str | None = Field(None, alias="File", description="The PDF file to convert. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output JPG file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.jpg, filename_1.jpg) for multi-page conversions."),
    password: str | None = Field(None, alias="Password", description="Password required to open a password-protected PDF document."),
    page_range: str | None = Field(None, alias="PageRange", description="Specifies which pages to convert using a range (e.g., 1-10) or comma-separated list (e.g., 1,2,5). Defaults to first 2000 pages."),
    rotate: Literal["default", "none", "rotate90", "rotate180", "rotate270"] | None = Field(None, alias="Rotate", description="Applies rotation to PDF pages before conversion. Select 'default' to use the PDF's embedded rotation settings, or specify a fixed rotation angle."),
    crop_to: Literal["BoundingBox", "TrimBox", "MediaBox", "ArtBox", "BleedBox"] | None = Field(None, alias="CropTo", description="Defines which page boundary to use for cropping during conversion. Different box types represent different content areas within the PDF page."),
    color_space: Literal["rgb", "cmyk", "gray"] | None = Field(None, alias="ColorSpace", description="Sets the color space for the output JPG image. Choose RGB for standard color, CMYK for print-ready output, or grayscale for black and white."),
) -> dict[str, Any] | ToolResult:
    """Convert PDF documents to JPG image format with support for page selection, rotation, cropping, and color space customization. Handles password-protected PDFs and generates multiple images for multi-page documents."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPdfToJpgRequest(
            body=_models.PostConvertPdfToJpgRequestBody(file_=file_, file_name=file_name, password=password, page_range=page_range, rotate=rotate, crop_to=crop_to, color_space=color_space)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_pdf_to_jpg: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/pdf/to/jpg"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_pdf_to_jpg")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_pdf_to_jpg", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_pdf_to_jpg",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def merge_pdfs(
    files: list[str] | None = Field(None, alias="Files", description="Array of PDF files to merge. Each file can be provided as a URL or file content. Files are merged in the order provided."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output merged PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing if multiple output files are generated."),
    password: str | None = Field(None, alias="Password", description="Password required to open the source PDF files if they are password-protected."),
    remove_duplicate_fonts: bool | None = Field(None, alias="RemoveDuplicateFonts", description="When enabled, prevents duplicate fonts from being included in the merged PDF, reducing file size."),
    bookmarks_toc: Literal["disabled", "filename", "title"] | None = Field(None, alias="BookmarksToc", description="Adds a top-level bookmark for each merged file using either the filename or the PDF title from metadata."),
    open_page: int | None = Field(None, alias="OpenPage", description="Specifies the page number where the merged PDF document should open when first displayed.", ge=1, le=3000),
) -> dict[str, Any] | ToolResult:
    """Merge multiple PDF files into a single document with optional font deduplication, table of contents bookmarks, and password protection support."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPdfToMergeRequest(
            body=_models.PostConvertPdfToMergeRequestBody(files=files, file_name=file_name, password=password, remove_duplicate_fonts=remove_duplicate_fonts, bookmarks_toc=bookmarks_toc, open_page=open_page)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for merge_pdfs: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/pdf/to/merge"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("merge_pdfs")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("merge_pdfs", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="merge_pdfs",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["Files"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_pdf_to_metadata(
    file_: str | None = Field(None, alias="File", description="The PDF file to convert. Accepts either a URL pointing to the file or the raw file content as binary data."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output file(s). The system automatically sanitizes the filename, appends the correct extension, and adds numeric suffixes (e.g., _0, _1) when multiple files are generated to ensure unique, safe file naming."),
    password: str | None = Field(None, alias="Password", description="The password required to open the PDF if it is password-protected. Only needed for encrypted documents."),
) -> dict[str, Any] | ToolResult:
    """Converts a PDF document to metadata format, extracting structured information from the file. Supports password-protected documents and customizable output file naming."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPdfToMetaRequest(
            body=_models.PostConvertPdfToMetaRequestBody(file_=file_, file_name=file_name, password=password)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_pdf_to_metadata: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/pdf/to/meta"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_pdf_to_metadata")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_pdf_to_metadata", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_pdf_to_metadata",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def extract_text_from_pdf(
    file_: str | None = Field(None, alias="File", description="The PDF file to process. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Custom name for the output file(s). The system automatically sanitizes the name, appends the appropriate file extension based on output format, and adds numeric suffixes for multiple files to ensure unique, safe filenames."),
    password: str | None = Field(None, alias="Password", description="Password required to open password-protected PDF documents."),
    page_range: str | None = Field(None, alias="PageRange", description="Specifies which pages to process. Use ranges (e.g., 1-10) or comma-separated individual pages (e.g., 1,2,5)."),
    ocr_mode: Literal["auto", "always", "reprocess"] | None = Field(None, alias="OcrMode", description="Controls how OCR is applied to pages. Auto skips pages with existing text, Always adds OCR while preserving existing text, and Reprocess regenerates the text layer for all pages."),
    ocr_language: Literal["ar", "ca", "zh-cn", "zh-tw", "da", "nl", "en", "fi", "fa", "de", "el", "he", "it", "ja", "ko", "lt", "no", "pl", "pt", "ro", "ru", "sl", "es", "sv", "tr", "ua", "th"] | None = Field(None, alias="OcrLanguage", description="Language for text recognition. Supports multiple languages including English, Spanish, Chinese, Arabic, and others. Contact support to request additional languages."),
    output_type: Literal["pdf", "txt"] | None = Field(None, alias="OutputType", description="Format for the extracted text. PDF embeds the OCR text layer into the document for searchability, while TXT returns plain text content only."),
    page_segmentation_mode: Literal["sparseText", "sparseTextOsd", "auto", "autoOsd", "singleLine", "singleColumn", "singleWord"] | None = Field(None, alias="PageSegmentationMode", description="Determines how the OCR engine analyzes document layout and detects text. SparseText finds scattered text without ordering, SparseTextOsd adds orientation detection, Auto selects the best mode automatically, AutoOsd combines auto-detection with orientation handling, SingleColumn assumes single-column layouts, SingleLine treats content as one line, and SingleWord recognizes isolated words."),
) -> dict[str, Any] | ToolResult:
    """Converts a PDF document to searchable text using OCR (Optical Character Recognition). Supports multiple languages, flexible page ranges, and configurable text extraction modes to handle various document layouts and existing text layers."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPdfToOcrRequest(
            body=_models.PostConvertPdfToOcrRequestBody(file_=file_, file_name=file_name, password=password, page_range=page_range, ocr_mode=ocr_mode, ocr_language=ocr_language, output_type=output_type, page_segmentation_mode=page_segmentation_mode)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for extract_text_from_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/pdf/to/ocr"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("extract_text_from_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("extract_text_from_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="extract_text_from_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_pdf_to_pcl(
    file_: str | None = Field(None, alias="File", description="The PDF file to convert. Accepts either a URL reference or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output PCL file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.pcl, output_1.pcl) for multiple output files."),
    color_mode: Literal["color", "monochrome"] | None = Field(None, alias="ColorMode", description="The color mode for the output document. Choose between full color or monochrome rendering."),
    resolution: int | None = Field(None, alias="Resolution", description="The output resolution in dots per inch (DPI). Higher values improve image quality but increase file size. Valid range is 10 to 1000 DPI.", ge=10, le=1000),
) -> dict[str, Any] | ToolResult:
    """Converts a PDF document to PCL (Printer Command Language) format with customizable output settings. Supports color mode selection and resolution adjustment for optimal print quality and file size balance."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPdfToPclRequest(
            body=_models.PostConvertPdfToPclRequestBody(file_=file_, file_name=file_name, color_mode=color_mode, resolution=resolution)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_pdf_to_pcl: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/pdf/to/pcl"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_pdf_to_pcl")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_pdf_to_pcl", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_pdf_to_pcl",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_pdf_to_pdf(
    file_: str | None = Field(None, alias="File", description="The PDF file to convert. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Custom name for the output PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., `report_0.pdf`, `report_1.pdf`) for multiple output files."),
    pdf_version: Literal["1.2", "1.3", "1.4", "1.5", "1.6", "1.7", "1.8", "2.0"] | None = Field(None, alias="PdfVersion", description="The PDF specification version to use for the output document."),
    pdf_title: str | None = Field(None, alias="PdfTitle", description="Custom title for the PDF document metadata. Use a single quote and space (' ') to remove the title entirely."),
    pdf_subject: str | None = Field(None, alias="PdfSubject", description="Custom subject for the PDF document metadata. Use a single quote and space (' ') to remove the subject entirely."),
    pdf_author: str | None = Field(None, alias="PdfAuthor", description="Custom author name for the PDF document metadata. Use a single quote and space (' ') to remove the author entirely."),
    pdf_creator: str | None = Field(None, alias="PdfCreator", description="Custom creator application name for the PDF document metadata. Use a single quote and space (' ') to remove the creator entirely."),
    pdf_keywords: str | None = Field(None, alias="PdfKeywords", description="Custom keywords for the PDF document metadata, typically used for searchability. Use a single quote and space (' ') to remove the keywords entirely."),
    open_page: int | None = Field(None, alias="OpenPage", description="The page number where the PDF should open when first displayed. Must be between 1 and 3000.", ge=1, le=3000),
    open_zoom: Literal["Default", "ActualSize", "FitPage", "FitWidth", "FitHeight", "FitVisible", "25", "50", "75", "100", "125", "150", "200", "400", "800", "1600", "2400", "3200", "6400"] | None = Field(None, alias="OpenZoom", description="The default zoom level applied when opening the PDF. Choose from preset percentages or fit-to-page options."),
    color_space: Literal["Default", "RGB", "CMYK", "Gray"] | None = Field(None, alias="ColorSpace", description="The color space model for the output PDF. RGB is suitable for screen display, CMYK for professional printing, and Gray for grayscale documents."),
) -> dict[str, Any] | ToolResult:
    """Convert a PDF document while optionally customizing metadata, viewer settings, and color space properties. Useful for updating PDF versions, embedding document information, or adjusting display preferences."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPdfToPdfRequest(
            body=_models.PostConvertPdfToPdfRequestBody(file_=file_, file_name=file_name, pdf_version=pdf_version, pdf_title=pdf_title, pdf_subject=pdf_subject, pdf_author=pdf_author, pdf_creator=pdf_creator, pdf_keywords=pdf_keywords, open_page=open_page, open_zoom=open_zoom, color_space=color_space)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_pdf_to_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/pdf/to/pdf"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_pdf_to_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_pdf_to_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_pdf_to_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def add_watermark_to_pdf_document(
    file_: str | None = Field(None, alias="File", description="The PDF file to be watermarked. Can be provided as a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output watermarked PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing for multiple output files to ensure unique identification."),
    password: str | None = Field(None, alias="Password", description="Password required to open the input PDF if it is password-protected."),
    overlay_file: str | None = Field(None, alias="OverlayFile", description="PDF file to use as the watermark overlay. Can be provided as a URL or binary file content."),
    overlay_page: int | None = Field(None, alias="OverlayPage", description="Page number from the overlay file to use as the watermark. Must be a valid page within the overlay document.", ge=1, le=2000),
    page_range: str | None = Field(None, alias="PageRange", description="Pages to apply the watermark to, specified as a range (e.g., 1-10) or comma-separated list (e.g., 1,2,5). Defaults to all pages."),
    opacity: int | None = Field(None, alias="Opacity", description="Watermark transparency level as a percentage. Lower values make the watermark more transparent.", ge=0, le=100),
    style: Literal["stamp", "watermark"] | None = Field(None, alias="Style", description="Watermark placement style. Stamp places the watermark over page content, while watermark places it beneath page content."),
    go_to_link: str | None = Field(None, alias="GoToLink", description="Web address to navigate to when the watermark is clicked. Creates an interactive link on the watermark."),
    go_to_page: str | None = Field(None, alias="GoToPage", description="Page number to navigate to when the watermark is clicked. Creates an internal document link on the watermark."),
    page_rotation: bool | None = Field(None, alias="PageRotation", description="Whether the watermark should rotate together with the PDF page. When enabled, watermark orientation matches page rotation; when disabled, watermark maintains fixed orientation."),
    page_box: Literal["mediabox", "trimbox", "bleedbox", "cropbox"] | None = Field(None, alias="PageBox", description="PDF page box used as the reference area for watermark positioning. Different boxes define different page boundaries (media, trim, bleed, or crop)."),
    measurement_unit: Literal["pt", "in", "mm", "cm"] | None = Field(None, alias="MeasurementUnit", description="Unit of measurement for watermark position and size parameters."),
    horizontal_alignment: Literal["left", "center", "right"] | None = Field(None, alias="HorizontalAlignment", description="Horizontal alignment of the watermark relative to the page."),
    vertical_alignment: Literal["top", "center", "bottom"] | None = Field(None, alias="VerticalAlignment", description="Vertical alignment of the watermark relative to the page."),
    offset: str | None = Field(None, alias="Offset", description="Watermark offset as a coordinate in the format 'x,y' using the selected MeasurementUnit. Positive X moves right, negative left. Positive Y moves down, negative up."),
) -> dict[str, Any] | ToolResult:
    """Add a watermark or stamp overlay to a PDF document with customizable positioning, opacity, and interactive elements. Supports applying watermarks across specified page ranges with flexible alignment and styling options."""

    # Call helper functions
    offset_parsed = parse_offset(offset)

    # Construct request model with validation
    try:
        _request = _models.PostConvertPdfToPdfWatermarkRequest(
            body=_models.PostConvertPdfToPdfWatermarkRequestBody(file_=file_, file_name=file_name, password=password, overlay_file=overlay_file, overlay_page=overlay_page, page_range=page_range, opacity=opacity, style=style, go_to_link=go_to_link, go_to_page=go_to_page, page_rotation=page_rotation, page_box=page_box, measurement_unit=measurement_unit, horizontal_alignment=horizontal_alignment, vertical_alignment=vertical_alignment, offset_x=offset_parsed.get('OffsetX') if offset_parsed else None, offset_y=offset_parsed.get('OffsetY') if offset_parsed else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_watermark_to_pdf_document: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/pdf/to/pdf-watermark"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_watermark_to_pdf_document")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_watermark_to_pdf_document", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_watermark_to_pdf_document",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File", "OverlayFile"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_pdf_to_pdfa(
    file_: str | None = Field(None, alias="File", description="The PDF file to convert. Accepts either a URL reference or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output PDF/A file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., report_0.pdf, report_1.pdf) for multiple output files."),
    password: str | None = Field(None, alias="Password", description="Password required to open a password-protected PDF document."),
    pdfa_version: Literal["pdfA1a", "pdfA1b", "pdfA2a", "pdfA2b", "pdfA2u", "pdfA3a", "pdfA3b", "pdfA3u", "pdfA4", "pdfA4e", "pdfA4f"] | None = Field(None, alias="PdfaVersion", description="The PDF/A compliance version to target for the output document."),
    invoice_format: Literal["none", "facturX", "zugferd1", "zugferd2"] | None = Field(None, alias="InvoiceFormat", description="E-invoice format to embed in the PDF. When specified, overrides the PdfaVersion setting and outputs PDF/A-3 format. Requires a valid structured invoice XML file."),
    invoice_file: str | None = Field(None, alias="InvoiceFile", description="Structured invoice XML file (ZUGFeRD or Factur-X format) to embed for hybrid-invoice compatibility. Required when InvoiceFormat is set to a value other than 'none'."),
    linearize: bool | None = Field(None, alias="Linearize", description="Linearize the PDF structure and optimize for fast web viewing and streaming."),
) -> dict[str, Any] | ToolResult:
    """Converts a PDF document to PDF/A format for long-term archival compliance. Supports optional password-protected PDFs, e-invoice embedding (ZUGFeRD/Factur-X), and web optimization."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPdfToPdfaRequest(
            body=_models.PostConvertPdfToPdfaRequestBody(file_=file_, file_name=file_name, password=password, pdfa_version=pdfa_version, invoice_format=invoice_format, invoice_file=invoice_file, linearize=linearize)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_pdf_to_pdfa: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/pdf/to/pdfa"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_pdf_to_pdfa")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_pdf_to_pdfa", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_pdf_to_pdfa",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File", "InvoiceFile"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_pdf_to_pdfua(
    file_: str | None = Field(None, alias="File", description="The PDF file to convert. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.pdf, filename_1.pdf) for multiple output files."),
    password: str | None = Field(None, alias="Password", description="Password required to open the input PDF if it is password-protected."),
    linearize: bool | None = Field(None, alias="Linearize", description="Enables linearization of the PDF file to optimize for fast web viewing and streaming."),
) -> dict[str, Any] | ToolResult:
    """Converts a standard PDF file to PDF/UA (Universal Accessibility) format, ensuring compliance with accessibility standards. Optionally linearizes the output for optimized web viewing performance."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPdfToPdfuaRequest(
            body=_models.PostConvertPdfToPdfuaRequestBody(file_=file_, file_name=file_name, password=password, linearize=linearize)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_pdf_to_pdfua: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/pdf/to/pdfua"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_pdf_to_pdfua")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_pdf_to_pdfua", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_pdf_to_pdfua",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_pdf_to_png(
    file_: str | None = Field(None, alias="File", description="The PDF file to convert. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the generated output PNG file(s). The system automatically sanitizes the filename, appends the correct extension, and adds an index suffix for multiple output files to ensure unique identification."),
    password: str | None = Field(None, alias="Password", description="Password required to open a protected or encrypted PDF document."),
    page_range: str | None = Field(None, alias="PageRange", description="Specifies which pages to convert using a range or comma-separated list format. Allows selective conversion of specific pages from the PDF."),
    rotate: Literal["default", "none", "rotate90", "rotate180", "rotate270"] | None = Field(None, alias="Rotate", description="Applies rotation to PDF pages before conversion to PNG. Select from predefined rotation angles or use the default orientation."),
    crop_to: Literal["BoundingBox", "TrimBox", "MediaBox", "ArtBox", "BleedBox"] | None = Field(None, alias="CropTo", description="Defines which PDF box boundary to use for cropping the page during conversion. Different box types capture different content areas of the PDF page."),
    background_color: str | None = Field(None, alias="BackgroundColor", description="Sets the background color for transparent areas in the PDF. Accepts color names, RGB values, or hexadecimal color codes. Use 'transparent' to preserve transparency in the output PNG."),
) -> dict[str, Any] | ToolResult:
    """Converts PDF documents to PNG image format with support for page selection, rotation, cropping, and background color customization. Handles password-protected PDFs and generates multiple output images for multi-page documents."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPdfToPngRequest(
            body=_models.PostConvertPdfToPngRequestBody(file_=file_, file_name=file_name, password=password, page_range=page_range, rotate=rotate, crop_to=crop_to, background_color=background_color)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_pdf_to_png: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/pdf/to/png"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_pdf_to_png")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_pdf_to_png", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_pdf_to_png",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_pdf_to_pptx(
    file_: str | None = Field(None, alias="File", description="The PDF file to convert. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output PowerPoint file. The system automatically sanitizes the filename, appends the correct extension, and adds numeric suffixes (e.g., report_0.pptx, report_1.pptx) when generating multiple files."),
    password: str | None = Field(None, alias="Password", description="Password required to open password-protected PDF documents."),
    page_range: str | None = Field(None, alias="PageRange", description="Specifies which pages to convert using a range (e.g., 1-10) or comma-separated list (e.g., 1,2,5)."),
    ocr_mode: Literal["auto", "force", "never"] | None = Field(None, alias="OcrMode", description="Controls when optical character recognition is applied during conversion. Auto applies OCR only when needed, Force applies it to all pages, and Never disables it entirely."),
    ocr_language: Literal["auto", "ar", "ca", "zh", "da", "nl", "en", "fi", "fr", "de", "el", "ko", "it", "ja", "no", "pl", "pt", "ro", "ru", "sl", "es", "sv", "tr", "ua", "th"] | None = Field(None, alias="OcrLanguage", description="Specifies the language for OCR text recognition. Use auto-detection by default, or manually select a language if auto-detection fails."),
    text_recovery_mode: Literal["auto", "always", "never"] | None = Field(None, alias="TextRecoveryMode", description="Determines how text is recovered from PDFs with non-standard encodings. Auto detects and recovers text only when needed, Always forces recovery for all text, and Never disables recovery."),
) -> dict[str, Any] | ToolResult:
    """Converts a PDF document to PowerPoint (PPTX) format with support for password-protected files, selective page ranges, and optical character recognition (OCR) for text extraction."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPdfToPptxRequest(
            body=_models.PostConvertPdfToPptxRequestBody(file_=file_, file_name=file_name, password=password, page_range=page_range, ocr_mode=ocr_mode, ocr_language=ocr_language, text_recovery_mode=text_recovery_mode)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_pdf_to_pptx: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/pdf/to/pptx"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_pdf_to_pptx")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_pdf_to_pptx", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_pdf_to_pptx",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_pdf_to_print(
    file_: str | None = Field(None, alias="File", description="The PDF file to convert. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output file(s). The system sanitizes the filename, appends the appropriate extension, and adds indexing (e.g., filename_0.pdf, filename_1.pdf) for multiple output files."),
    password: str | None = Field(None, alias="Password", description="Password required to open a protected or encrypted PDF document."),
    trim_size: Literal["default", "a2", "a3", "a4", "a5", "a6", "letter", "legal", "custom"] | None = Field(None, alias="TrimSize", description="Page size to apply to every page in the output. Select 'default' to preserve each page's current size, or 'custom' to specify exact dimensions via TrimWidth and TrimHeight."),
    trim_width: int | None = Field(None, alias="TrimWidth", description="Width of the trim box in millimeters when TrimSize is set to 'custom'. Must be between 10 and 1000 mm.", ge=10, le=1000),
    bleed_mode: Literal["none", "mirror", "stretch"] | None = Field(None, alias="BleedMode", description="Controls how bleed content is generated. 'Mirror' reflects page content outward for full-bleed preview, 'Stretch' extends edge pixels into the bleed area, or 'None' disables bleed fabrication."),
    trim_marks: bool | None = Field(None, alias="TrimMarks", description="When enabled, adds crop marks positioned outside the bleed box to indicate trim boundaries."),
    registration_marks: bool | None = Field(None, alias="RegistrationMarks", description="When enabled, adds registration targets (crosshairs) centered at least 3mm outside the bleed box on each edge for color registration alignment."),
    slug: str | None = Field(None, alias="Slug", description="Text to display at the bottom of the media box, typically used for printed file names, order numbers, or customer information."),
    tint_bars: bool | None = Field(None, alias="TintBars", description="When enabled, adds grayscale and color control bars at the top of the page, positioned outside the trim box for quality verification."),
    color_space: Literal["default", "rgb", "cmyk", "gray"] | None = Field(None, alias="ColorSpace", description="Defines the color space for the output PDF. 'Default' preserves the original color space, or specify RGB, CMYK, or grayscale conversion."),
    output_intent: Literal["none", "fogra39", "fogra51", "gracol2013", "swop2013", "japancolor2011", "custom"] | None = Field(None, alias="OutputIntent", description="Embeds an ICC color profile as the PDF's output intent for color management. Select 'custom' to provide a custom ICC profile file via OutputIntentIccFile."),
    output_intent_icc_file: str | None = Field(None, alias="OutputIntentIccFile", description="Custom ICC profile file to embed as the PDF output intent. Required when OutputIntent is set to 'custom'."),
    downsample_images: bool | None = Field(None, alias="DownsampleImages", description="When enabled, reduces resolution of images exceeding the target resolution to minimize file size while maintaining quality."),
    resolution: int | None = Field(None, alias="Resolution", description="Target resolution in pixels per inch (PPI) used for rasterization tasks such as bleed fabrication and image downsampling. Valid range is 10 to 800 PPI.", ge=10, le=800),
    page_range: str | None = Field(None, alias="PageRange", description="Specifies which pages to convert using a comma-separated range (e.g., 1,2,5-last). Supports keywords 'even', 'odd', and 'last'. Maximum of 100 pages will be processed per conversion."),
) -> dict[str, Any] | ToolResult:
    """Converts a PDF document to print-ready format with support for professional print specifications including trim sizes, bleed modes, color spaces, and registration marks. Supports page range selection and ICC profile embedding for color-managed workflows."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPdfToPrintRequest(
            body=_models.PostConvertPdfToPrintRequestBody(file_=file_, file_name=file_name, password=password, trim_size=trim_size, trim_width=trim_width, bleed_mode=bleed_mode, trim_marks=trim_marks, registration_marks=registration_marks, slug=slug, tint_bars=tint_bars, color_space=color_space, output_intent=output_intent, output_intent_icc_file=output_intent_icc_file, downsample_images=downsample_images, resolution=resolution, page_range=page_range)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_pdf_to_print: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/pdf/to/print"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_pdf_to_print")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_pdf_to_print", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_pdf_to_print",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File", "OutputIntentIccFile"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def protect_pdf(
    file_: str | None = Field(None, alias="File", description="The PDF file to protect. Accepts either a file URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output protected PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., document_0.pdf, document_1.pdf) for multiple output files."),
    password: str | None = Field(None, alias="Password", description="Password required to open the protected PDF document. Used when the document has existing protection that needs to be processed."),
    encryption_algorithm: Literal["Standard40Bit", "Standard128Bit", "Aes128Bit", "Aes256Bit"] | None = Field(None, alias="EncryptionAlgorithm", description="Algorithm used to encrypt the PDF document. Determines the strength and type of encryption applied."),
    encrypt_meta: bool | None = Field(None, alias="EncryptMeta", description="Whether to encrypt the PDF metadata (document properties, author, title, etc.) in addition to the content."),
    user_password: str | None = Field(None, alias="UserPassword", description="User password (document open password) that recipients must enter to view the PDF in Acrobat Reader. Distinct from owner password."),
    owner_password: str | None = Field(None, alias="OwnerPassword", description="Owner password (permissions password) that controls restrictions on printing, editing, and copying. Recipients can open the document without this password but cannot modify restrictions."),
    respect_owner_password: bool | None = Field(None, alias="RespectOwnerPassword", description="Whether to preserve the original document's owner password and permissions. When enabled, requires the correct owner password in the Password field. When disabled, existing restrictions are removed."),
    assemble_document: bool | None = Field(None, alias="AssembleDocument", description="Whether to allow assembly operations such as inserting, rotating, or deleting pages, and creating bookmarks or thumbnail images."),
    modify_contents: bool | None = Field(None, alias="ModifyContents", description="Whether to allow modifications to the document content."),
    extract_contents: bool | None = Field(None, alias="ExtractContents", description="Whether to allow extraction of text and graphics from the document."),
    modify_annotations: bool | None = Field(None, alias="ModifyAnnotations", description="Whether to allow adding or modifying text annotations and filling interactive form fields."),
    fill_form_fields: bool | None = Field(None, alias="FillFormFields", description="Whether to allow filling in existing interactive form fields, including signature fields."),
    print_document: bool | None = Field(None, alias="PrintDocument", description="Whether to allow printing the document."),
    print_faithful_copy: bool | None = Field(None, alias="PrintFaithfulCopy", description="Whether to allow printing the document to a representation from which a faithful digital copy of the PDF content could be generated."),
) -> dict[str, Any] | ToolResult:
    """Convert and protect a PDF document by applying encryption, setting access passwords, and configuring user permissions. Supports multiple encryption algorithms and granular control over document operations like printing, editing, and content extraction."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPdfToProtectRequest(
            body=_models.PostConvertPdfToProtectRequestBody(file_=file_, file_name=file_name, password=password, encryption_algorithm=encryption_algorithm, encrypt_meta=encrypt_meta, user_password=user_password, owner_password=owner_password, respect_owner_password=respect_owner_password, assemble_document=assemble_document, modify_contents=modify_contents, extract_contents=extract_contents, modify_annotations=modify_annotations, fill_form_fields=fill_form_fields, print_document=print_document, print_faithful_copy=print_faithful_copy)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for protect_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/pdf/to/protect"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("protect_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("protect_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="protect_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_pdf_to_rasterized_image(
    file_: str | None = Field(None, alias="File", description="The PDF file to convert. Accepts either a URL reference or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output file(s). The system automatically sanitizes the filename, appends the appropriate image extension, and adds numeric indexing (e.g., filename_0.png, filename_1.png) when multiple output files are generated from a single input."),
    password: str | None = Field(None, alias="Password", description="Password required to open password-protected PDF documents."),
    resolution: int | None = Field(None, alias="Resolution", description="Resolution for rasterized output measured in dots per inch (DPI). Higher values produce sharper images but increase file size. Valid range is 10 to 800 DPI.", ge=10, le=800),
) -> dict[str, Any] | ToolResult:
    """Convert PDF documents to rasterized image files at a specified resolution. Supports password-protected PDFs and allows customization of output image quality through DPI settings."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPdfToRasterizeRequest(
            body=_models.PostConvertPdfToRasterizeRequestBody(file_=file_, file_name=file_name, password=password, resolution=resolution)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_pdf_to_rasterized_image: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/pdf/to/rasterize"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_pdf_to_rasterized_image")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_pdf_to_rasterized_image", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_pdf_to_rasterized_image",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def redact_pdf(
    file_: str | None = Field(None, alias="File", description="The PDF file to redact. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output file(s). The API sanitizes the filename, appends the correct extension, and adds indexing for multiple output files (e.g., report_0.pdf, report_1.pdf)."),
    password: str | None = Field(None, alias="Password", description="Password to open a protected PDF document."),
    preset: Literal["auto", "gdpr", "hipaa", "ferpa", "foia", "glba", "ccpa", "manual"] | None = Field(None, alias="Preset", description="Compliance preset that determines which categories of sensitive data the AI detects and redacts. Use 'manual' to rely exclusively on custom redaction parameters (PII, PHI, Financial)."),
    context_size: Literal["balanced", "page"] | None = Field(None, alias="ContextSize", description="Defines how the AI processes document context. 'Page' processes each page independently for structured data and high-volume detections. 'Balanced' maintains cross-page context for large documents while optimizing performance."),
    redaction_color: str | None = Field(None, alias="RedactionColor", description="Color used to mask redacted text. Accepts hexadecimal (e.g., #FFFFFF), RGB with optional alpha channel (e.g., 255,255,255), or named colors (e.g., white, red, blue)."),
    redaction_thickness: float | None = Field(None, alias="RedactionThickness", description="Height of the redaction stroke relative to the original line height. A value of 1 matches the original height; values below 1 reduce height, values above 1 increase it.", ge=0.5, le=2),
    pii: bool | None = Field(None, alias="PII", description="Enable detection and redaction of Personally Identifiable Information (PII) such as names, email addresses, phone numbers, birthdates, and home addresses."),
    phi: bool | None = Field(None, alias="PHI", description="Enable detection and redaction of Patient Health Information (PHI) such as patient names, medical records, insurance details, and prescription data."),
    financial: bool | None = Field(None, alias="Financial", description="Enable detection and redaction of financial data including credit card numbers, bank account numbers, and financial transaction details."),
    minimum_confidence: float | None = Field(None, alias="MinimumConfidence", description="Minimum confidence threshold for AI-based detection of sensitive data. Higher values reduce false positives but may miss subtle matches.", ge=0.01, le=0.99),
    page_range: str | None = Field(None, alias="PageRange", description="Pages to redact, specified as a range (e.g., 1-10) or comma-separated list (e.g., 1,2,5)."),
    redaction_text_values: list[str] | None = Field(None, description="List of exact text strings to be redacted"),
    redaction_regex_patterns: list[str] | None = Field(None, description="List of regular expression patterns (unescaped) for flexible text matching. Patterns will be automatically escaped during construction."),
    redaction_detect_descriptions: list[str] | None = Field(None, description="List of AI-based detection descriptions (e.g., 'Bank account number', 'Social security number')"),
) -> dict[str, Any] | ToolResult:
    """Convert and redact sensitive data from a PDF document based on compliance presets or custom detection rules. Supports automatic AI-based detection of PII, financial, and health information, or manual redaction configuration."""

    # Call helper functions
    redaction_data = build_redaction_data(redaction_text_values, redaction_regex_patterns, redaction_detect_descriptions)

    # Construct request model with validation
    try:
        _request = _models.PostConvertPdfToRedactRequest(
            body=_models.PostConvertPdfToRedactRequestBody(file_=file_, file_name=file_name, password=password, preset=preset, context_size=context_size, redaction_color=redaction_color, redaction_thickness=redaction_thickness, pii=pii, phi=phi, financial=financial, minimum_confidence=minimum_confidence, page_range=page_range, redaction_data=redaction_data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for redact_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/pdf/to/redact"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("redact_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("redact_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="redact_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def resize_pdf_pages(
    file_: str | None = Field(None, alias="File", description="The PDF file to resize. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.pdf, output_1.pdf) for multiple files to ensure unique identification."),
    password: str | None = Field(None, alias="Password", description="Password required to open a protected or encrypted PDF file."),
    page_range: str | None = Field(None, alias="PageRange", description="Specifies which pages to convert using page numbers and keywords. Supports comma-separated values, ranges with hyphens, and keywords like 'even', 'odd', and 'last' to select specific pages."),
    measurement_unit: Literal["pt", "in", "mm", "cm"] | None = Field(None, alias="MeasurementUnit", description="The unit of measurement for page dimensions (height and width)."),
) -> dict[str, Any] | ToolResult:
    """Resize PDF pages to specified dimensions. Supports selective page conversion with customizable measurement units and password-protected PDF handling."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPdfToResizeRequest(
            body=_models.PostConvertPdfToResizeRequestBody(file_=file_, file_name=file_name, password=password, page_range=page_range, measurement_unit=measurement_unit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for resize_pdf_pages: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/pdf/to/resize"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("resize_pdf_pages")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("resize_pdf_pages", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="resize_pdf_pages",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def rotate_pdf_pages(
    file_: str | None = Field(None, alias="File", description="The PDF file to rotate. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., document_0.pdf, document_1.pdf) for multiple output files."),
    password: str | None = Field(None, alias="Password", description="Password required to open a protected or encrypted PDF document."),
    auto_rotate: bool | None = Field(None, alias="AutoRotate", description="Enable automatic detection and correction of page orientation to the optimal reading angle."),
    angle: Literal["0", "90", "180", "270"] | None = Field(None, alias="Angle", description="Rotation angle in degrees to apply to selected pages."),
    page_range: str | None = Field(None, alias="PageRange", description="Specify which pages to rotate using page numbers, ranges, or keywords. Use comma-separated values for multiple selections and hyphens for ranges (e.g., 1,2,5-last or even, odd)."),
) -> dict[str, Any] | ToolResult:
    """Rotate pages in a PDF document by a specified angle or automatically detect optimal orientation. Supports selective page ranges and password-protected PDFs."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPdfToRotateRequest(
            body=_models.PostConvertPdfToRotateRequestBody(file_=file_, file_name=file_name, password=password, auto_rotate=auto_rotate, angle=angle, page_range=page_range)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for rotate_pdf_pages: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/pdf/to/rotate"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("rotate_pdf_pages")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("rotate_pdf_pages", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="rotate_pdf_pages",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_pdf_to_rtf(
    file_: str | None = Field(None, alias="File", description="The PDF file to convert. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output RTF file. The system sanitizes the filename, appends the correct extension, and adds indexing (e.g., document_0.rtf, document_1.rtf) for multiple output files."),
    password: str | None = Field(None, alias="Password", description="Password required to open password-protected PDF documents."),
    page_range: str | None = Field(None, alias="PageRange", description="Specifies which pages to convert using a range (e.g., 1-10) or comma-separated list (e.g., 1,2,5). Defaults to pages 1-2000."),
    wysiwyg: bool | None = Field(None, alias="Wysiwyg", description="When enabled, preserves exact formatting from the source PDF by using text boxes in the output RTF."),
    ocr_mode: Literal["auto", "force", "never"] | None = Field(None, alias="OcrMode", description="Controls OCR (Optical Character Recognition) behavior during conversion. Auto applies OCR only when needed, Force applies to all pages, and Never disables OCR entirely."),
    ocr_language: Literal["auto", "ar", "ca", "zh", "da", "nl", "en", "fi", "fr", "de", "el", "ko", "it", "ja", "no", "pl", "pt", "ro", "ru", "sl", "es", "sv", "tr", "ua", "th"] | None = Field(None, alias="OcrLanguage", description="Specifies the language for OCR text recognition. Use auto-detection by default, or manually select a language if auto-detection fails."),
) -> dict[str, Any] | ToolResult:
    """Converts PDF documents to RTF (Rich Text Format) with support for password-protected files, selective page ranges, and OCR capabilities. Preserves formatting and enables text recognition for scanned documents."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPdfToRtfRequest(
            body=_models.PostConvertPdfToRtfRequestBody(file_=file_, file_name=file_name, password=password, page_range=page_range, wysiwyg=wysiwyg, ocr_mode=ocr_mode, ocr_language=ocr_language)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_pdf_to_rtf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/pdf/to/rtf"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_pdf_to_rtf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_pdf_to_rtf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_pdf_to_rtf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def split_pdf(
    file_: str | None = Field(None, alias="File", description="The PDF file to be split. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output file(s). The API sanitizes the filename, appends the appropriate extension, and adds numeric indices (e.g., `report_0.pdf`, `report_1.pdf`) when multiple files are generated."),
    password: str | None = Field(None, alias="Password", description="Password required to open password-protected PDF documents."),
    split_by_pattern: str | None = Field(None, alias="SplitByPattern", description="A comma-separated sequence of positive integers that defines the page count for each split segment. The pattern repeats cyclically until all pages are consumed. For example, a pattern of `3,2` creates segments of 3 pages, then 2 pages, repeating as needed."),
    split_by_text_pattern: str | None = Field(None, alias="SplitByTextPattern", description="A regular expression pattern that triggers a new document split whenever matching text is found on a page. For example, `Chapter\\s+\\d+` splits at pages containing \"Chapter 1\", \"Chapter 2\", etc. Pages before the first match are grouped together, and any remaining pages after the last match form a final segment."),
    split_by_bookmark: bool | None = Field(None, alias="SplitByBookmark", description="When enabled, automatically splits the PDF at each bookmarked page. For nested bookmarks, splitting occurs at the deepest level, and output filenames reflect the full bookmark hierarchy (e.g., `ParentBookmark-ChildBookmark.pdf`). PDFs without bookmarks are returned unchanged."),
    merge_output: bool | None = Field(None, alias="MergeOutput", description="When enabled, merges all split segments back into a single PDF file instead of returning separate files for each segment."),
) -> dict[str, Any] | ToolResult:
    """Splits a PDF document into multiple files based on page ranges, text patterns, or bookmarks. Optionally merges the split segments back into a single file."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPdfToSplitRequest(
            body=_models.PostConvertPdfToSplitRequestBody(file_=file_, file_name=file_name, password=password, split_by_pattern=split_by_pattern, split_by_text_pattern=split_by_text_pattern, split_by_bookmark=split_by_bookmark, merge_output=merge_output)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for split_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/pdf/to/split"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("split_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("split_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="split_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_pdf_to_svg(
    file_: str | None = Field(None, alias="File", description="The PDF file to convert. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output SVG file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.svg, output_1.svg) for multiple files."),
    password: str | None = Field(None, alias="Password", description="Password required to open password-protected PDF documents."),
    page_range: str | None = Field(None, alias="PageRange", description="Specifies which pages to convert. Use ranges (e.g., 1-10) or comma-separated individual pages (e.g., 1,2,5)."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="When enabled, maintains the aspect ratio of the output image during scaling operations."),
    rotate: int | None = Field(None, alias="Rotate", description="Rotates the output image by the specified angle in degrees.", ge=-360, le=360),
    red: int | None = Field(None, description="Red channel value (0-255)"),
    green: int | None = Field(None, description="Green channel value (0-255)"),
    blue: int | None = Field(None, description="Blue channel value (0-255)"),
    alpha: int | None = Field(None, description="Alpha channel value (0-255), where 0 is fully transparent and 255 is fully opaque. Optional; if not provided, defaults to 255 (fully opaque)."),
) -> dict[str, Any] | ToolResult:
    """Converts PDF documents to SVG (Scalable Vector Graphics) format, with support for page range selection, rotation, and password-protected documents. Useful for extracting vector-based graphics from PDFs while maintaining scalability."""

    # Call helper functions
    transparent_color = build_transparent_color(red, green, blue, alpha)

    # Construct request model with validation
    try:
        _request = _models.PostConvertPdfToSvgRequest(
            body=_models.PostConvertPdfToSvgRequestBody(file_=file_, file_name=file_name, password=password, page_range=page_range, scale_proportions=scale_proportions, rotate=rotate, transparent_color=transparent_color)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_pdf_to_svg: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/pdf/to/svg"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_pdf_to_svg")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_pdf_to_svg", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_pdf_to_svg",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_pdf_to_text_with_watermark(
    file_: str | None = Field(None, alias="File", description="The PDF file to convert. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., report_0.txt, report_1.txt) for multiple outputs."),
    password: str | None = Field(None, alias="Password", description="Password required to open password-protected PDF documents."),
    text: str | None = Field(None, alias="Text", description="Text content for the watermark. Supports dynamic variables like %PAGE%, %FILENAME%, %DATE%, %TIME%, %DATETIME%, document metadata (%AUTHOR%, %TITLE%, %SUBJECT%, %KEYWORDS%), and %N% for line breaks."),
    style: Literal["stamp", "watermark"] | None = Field(None, alias="Style", description="Watermark display style. Stamp places the watermark over page content; watermark places it beneath."),
    font_size: int | None = Field(None, alias="FontSize", description="Font size for the watermark text in points.", ge=1, le=200),
    text_rendering_mode: Literal["filltext", "stroketext", "fillstroke", "invisible"] | None = Field(None, alias="TextRenderingMode", description="Text rendering mode controlling how the watermark text is drawn (filled, stroked, both, or invisible)."),
    font_color: str | None = Field(None, alias="FontColor", description="Color of the watermark text. Specify as a color value (e.g., hex code or color name)."),
    stroke_color: str | None = Field(None, alias="StrokeColor", description="Color of the text stroke/outline."),
    stroke_width: int | None = Field(None, alias="StrokeWidth", description="Width of the text stroke in points.", ge=0, le=200),
    font_name: Literal["arial", "bahnschrift", "calibri", "cambria", "consolas", "constantia", "courierNew", "georgia", "tahoma", "timesNewRoman", "verdana"] | None = Field(None, alias="FontName", description="Font family for the watermark text. Contact support for additional font availability."),
    rotate: int | None = Field(None, alias="Rotate", description="Rotation angle of the watermark in degrees (0-360).", ge=0, le=360),
    opacity: int | None = Field(None, alias="Opacity", description="Transparency level of the watermark as a percentage (0=fully transparent, 100=fully opaque).", ge=0, le=100),
    go_to_link: str | None = Field(None, alias="GoToLink", description="Web URL to navigate to when the watermark is clicked."),
    go_to_page: str | None = Field(None, alias="GoToPage", description="Page number to navigate to when the watermark is clicked."),
    page_box: Literal["mediabox", "trimbox", "bleedbox", "cropbox"] | None = Field(None, alias="PageBox", description="PDF page box type used as the reference area for watermark positioning (mediabox is the full page, others define trimmed/bleed/crop areas)."),
    horizontal_alignment: Literal["left", "center", "right"] | None = Field(None, alias="HorizontalAlignment", description="Horizontal alignment of the watermark within its container."),
    vertical_alignment: Literal["top", "center", "bottom"] | None = Field(None, alias="VerticalAlignment", description="Vertical alignment of the watermark within its container."),
    measurement_unit: Literal["pt", "in", "mm", "cm"] | None = Field(None, alias="MeasurementUnit", description="Unit of measurement for width, height, and position parameters."),
    width: float | None = Field(None, alias="Width", description="Width of the watermark text box in the specified measurement unit. A value of 0 means the width is automatically determined.", ge=0, le=10000),
    height: float | None = Field(None, alias="Height", description="Height of the watermark text box in the specified measurement unit. A value of 0 means the height is automatically determined.", ge=0, le=10000),
    line_spacing: int | None = Field(None, alias="LineSpacing", description="Line spacing adjustment for multi-line watermark text in points.", ge=-30, le=30),
    page_range: str | None = Field(None, alias="PageRange", description="Pages to apply the watermark to. Specify as a range (e.g., 1-10) or comma-separated list (e.g., 1,2,5)."),
    font_embed: bool | None = Field(None, alias="FontEmbed", description="Whether to embed fonts in the output document for consistent rendering across systems."),
    font_subset: bool | None = Field(None, alias="FontSubset", description="Whether to subset fonts (include only used characters) to reduce file size."),
    offset: str | None = Field(None, alias="Offset", description="Watermark offset as 'x,y' coordinates. Positive X moves right, negative left. Positive Y moves down, negative up. Uses the selected MeasurementUnit."),
) -> dict[str, Any] | ToolResult:
    """Converts a PDF document to text format while applying customizable watermark or stamp overlays. Supports dynamic watermark text with variables, advanced styling options, and precise positioning control."""

    # Call helper functions
    offset_parsed = parse_offset(offset)

    # Construct request model with validation
    try:
        _request = _models.PostConvertPdfToTextWatermarkRequest(
            body=_models.PostConvertPdfToTextWatermarkRequestBody(file_=file_, file_name=file_name, password=password, text=text, style=style, font_size=font_size, text_rendering_mode=text_rendering_mode, font_color=font_color, stroke_color=stroke_color, stroke_width=stroke_width, font_name=font_name, rotate=rotate, opacity=opacity, go_to_link=go_to_link, go_to_page=go_to_page, page_box=page_box, horizontal_alignment=horizontal_alignment, vertical_alignment=vertical_alignment, measurement_unit=measurement_unit, width=width, height=height, line_spacing=line_spacing, page_range=page_range, font_embed=font_embed, font_subset=font_subset, offset_x=offset_parsed.get('OffsetX') if offset_parsed else None, offset_y=offset_parsed.get('OffsetY') if offset_parsed else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_pdf_to_text_with_watermark: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/pdf/to/text-watermark"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_pdf_to_text_with_watermark")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_pdf_to_text_with_watermark", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_pdf_to_text_with_watermark",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_pdf_to_tiff(
    file_: str | None = Field(None, alias="File", description="The PDF file to convert. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output TIFF file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.tiff, filename_1.tiff) for multiple output files."),
    password: str | None = Field(None, alias="Password", description="Password required to open a password-protected PDF document."),
    page_range: str | None = Field(None, alias="PageRange", description="Specifies which pages to convert using a range (e.g., 1-10) or comma-separated list (e.g., 1,2,5)."),
    rotate: Literal["default", "none", "rotate90", "rotate180", "rotate270"] | None = Field(None, alias="Rotate", description="Applies rotation to PDF pages before conversion."),
    crop_to: Literal["BoundingBox", "TrimBox", "MediaBox", "ArtBox", "BleedBox"] | None = Field(None, alias="CropTo", description="Defines which PDF box area to use when cropping pages during conversion."),
    background_color: str | None = Field(None, alias="BackgroundColor", description="Sets the background color for transparent areas in the PDF. Accepts color names (white, black), RGB format (255,0,0), HEX format (#FF0000), or 'transparent' to preserve transparency."),
    multi_page: bool | None = Field(None, alias="MultiPage", description="When enabled, creates a single multi-page TIFF file containing all converted pages. When disabled, generates separate TIFF files for each page."),
    color_mode: Literal["default", "cmyk", "grayscale", "bitonal"] | None = Field(None, alias="ColorMode", description="Specifies the color mode for the output TIFF image."),
) -> dict[str, Any] | ToolResult:
    """Converts PDF documents to TIFF image format with support for page selection, rotation, cropping, and color mode customization. Handles password-protected PDFs and can generate single or multi-page TIFF files."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPdfToTiffRequest(
            body=_models.PostConvertPdfToTiffRequestBody(file_=file_, file_name=file_name, password=password, page_range=page_range, rotate=rotate, crop_to=crop_to, background_color=background_color, multi_page=multi_page, color_mode=color_mode)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_pdf_to_tiff: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/pdf/to/tiff"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_pdf_to_tiff")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_pdf_to_tiff", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_pdf_to_tiff",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_pdf_to_tiff_fax(
    file_: str | None = Field(None, alias="File", description="The PDF file to convert. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output file(s). The API automatically sanitizes the filename, appends the correct extension, and adds indexing for multiple output files to ensure unique identification."),
    password: str | None = Field(None, alias="Password", description="Password required to open password-protected PDF documents."),
    tiff_type: Literal["monochromeg3", "monochromeg32d", "monochromeg4", "monochromelzw", "monochromepackbits"] | None = Field(None, alias="TiffType", description="Compression type for the TIFF FAX output. Determines the encoding method used in the resulting file."),
    multi_page: bool | None = Field(None, alias="MultiPage", description="When enabled, combines all converted pages into a single multi-page TIFF file. When disabled, generates separate TIFF files for each page."),
    page_range: str | None = Field(None, alias="PageRange", description="Specifies which pages to convert from the PDF. Use hyphen for ranges (e.g., 1-10) or comma-separated values for individual pages (e.g., 1,2,5)."),
    crop_to: Literal["BoundingBox", "TrimBox", "MediaBox", "ArtBox", "BleedBox"] | None = Field(None, alias="CropTo", description="Defines which page boundary box to use for cropping during conversion. Different box types capture different content areas of the PDF page."),
) -> dict[str, Any] | ToolResult:
    """Converts PDF documents to TIFF FAX format with support for multi-page output, custom compression types, and selective page range processing. Ideal for fax transmission and archival purposes."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPdfToTiffFaxRequest(
            body=_models.PostConvertPdfToTiffFaxRequestBody(file_=file_, file_name=file_name, password=password, tiff_type=tiff_type, multi_page=multi_page, page_range=page_range, crop_to=crop_to)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_pdf_to_tiff_fax: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/pdf/to/tiff-fax"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_pdf_to_tiff_fax")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_pdf_to_tiff_fax", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_pdf_to_tiff_fax",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_pdf_to_text(
    file_: str | None = Field(None, alias="File", description="The PDF file to convert. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output text file(s). The system sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.txt, output_1.txt) when multiple files are generated."),
    password: str | None = Field(None, alias="Password", description="Password required to open password-protected PDF documents."),
    page_range: str | None = Field(None, alias="PageRange", description="Specify which pages to convert using a range (e.g., 1-10) or comma-separated list (e.g., 1,2,5)."),
    ocr_mode: Literal["auto", "force", "never"] | None = Field(None, alias="OcrMode", description="Controls OCR application during conversion. Auto applies OCR only when needed, Force applies OCR to all pages, and Never disables OCR entirely."),
    ocr_language: Literal["auto", "ar", "ca", "zh", "da", "nl", "en", "fi", "fr", "de", "el", "ko", "it", "ja", "no", "pl", "pt", "ro", "ru", "sl", "es", "sv", "tr", "ua", "th"] | None = Field(None, alias="OcrLanguage", description="Specifies the language for OCR text recognition. Use auto-detection by default, or manually select a language if auto-detection fails."),
    include_formatting: bool | None = Field(None, alias="IncludeFormatting", description="Preserve text formatting (fonts, spacing, alignment) during extraction. Only effective when headers/footers and footnotes removal are disabled."),
    split_pages: bool | None = Field(None, alias="SplitPages", description="Generate a separate output file for each page instead of combining all pages into a single file."),
    remove_headers_footers: bool | None = Field(None, alias="RemoveHeadersFooters", description="Exclude headers and footers from the extracted text output."),
    remove_footnotes: bool | None = Field(None, alias="RemoveFootnotes", description="Exclude footnotes from the extracted text output."),
    remove_tables: bool | None = Field(None, alias="RemoveTables", description="Exclude tables from the extracted text output."),
) -> dict[str, Any] | ToolResult:
    """Convert PDF documents to plain text format with optional OCR, formatting preservation, and content filtering. Supports password-protected files, page range selection, and multi-language text recognition."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPdfToTxtRequest(
            body=_models.PostConvertPdfToTxtRequestBody(file_=file_, file_name=file_name, password=password, page_range=page_range, ocr_mode=ocr_mode, ocr_language=ocr_language, include_formatting=include_formatting, split_pages=split_pages, remove_headers_footers=remove_headers_footers, remove_footnotes=remove_footnotes, remove_tables=remove_tables)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_pdf_to_text: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/pdf/to/txt"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_pdf_to_text")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_pdf_to_text", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_pdf_to_text",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def unprotect_pdf(
    file_: str | None = Field(None, alias="File", description="The PDF file to unprotect. Provide either a publicly accessible URL or the raw file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds numeric suffixes (e.g., `document_0.pdf`, `document_1.pdf`) if multiple files are generated."),
    password: str | None = Field(None, alias="Password", description="The password protecting the PDF. Provide the user password to remove user-level protection, or leave empty to remove owner-level protection."),
) -> dict[str, Any] | ToolResult:
    """Remove password protection from a PDF file. Specify a user password to remove user-level protection, or leave the password empty to remove owner-level protection."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPdfToUnprotectRequest(
            body=_models.PostConvertPdfToUnprotectRequestBody(file_=file_, file_name=file_name, password=password)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for unprotect_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/pdf/to/unprotect"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("unprotect_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("unprotect_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="unprotect_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_pdf_to_webp(
    file_: str | None = Field(None, alias="File", description="The PDF file to convert. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output file(s). The system sanitizes the filename, appends the correct extension automatically, and adds indexing (e.g., filename_0.webp, filename_1.webp) for multiple outputs."),
    password: str | None = Field(None, alias="Password", description="Password required to open password-protected PDF documents."),
    page_range: str | None = Field(None, alias="PageRange", description="Specify which pages to convert using a range (e.g., 1-10) or comma-separated list (e.g., 1,2,5)."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain aspect ratio when scaling the output image to prevent distortion."),
    rotate: int | None = Field(None, alias="Rotate", description="Rotate the output image by the specified angle in degrees.", ge=-360, le=360),
    red: int | None = Field(None, description="Red channel value (0-255)"),
    green: int | None = Field(None, description="Green channel value (0-255)"),
    blue: int | None = Field(None, description="Blue channel value (0-255)"),
    alpha: int | None = Field(None, description="Alpha channel value (0-255), where 0 is fully transparent and 255 is fully opaque. Optional; if not provided, defaults to 255 (fully opaque)."),
) -> dict[str, Any] | ToolResult:
    """Convert PDF documents to WebP image format with support for page selection, rotation, and scaling options. Handles password-protected PDFs and generates uniquely named output files."""

    # Call helper functions
    transparent_color = build_transparent_color(red, green, blue, alpha)

    # Construct request model with validation
    try:
        _request = _models.PostConvertPdfToWebpRequest(
            body=_models.PostConvertPdfToWebpRequestBody(file_=file_, file_name=file_name, password=password, page_range=page_range, scale_proportions=scale_proportions, rotate=rotate, transparent_color=transparent_color)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_pdf_to_webp: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/pdf/to/webp"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_pdf_to_webp")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_pdf_to_webp", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_pdf_to_webp",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_pdf_to_xlsx(
    file_: str | None = Field(None, alias="File", description="The PDF file to convert. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the generated Excel output file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., report_0.xlsx, report_1.xlsx) for multiple output files."),
    password: str | None = Field(None, alias="Password", description="Password required to open password-protected PDF documents."),
    page_range: str | None = Field(None, alias="PageRange", description="Specifies which pages to extract from the PDF. Use ranges (e.g., 1-10) or comma-separated page numbers (e.g., 1,2,5)."),
    ocr_mode: Literal["auto", "force", "never"] | None = Field(None, alias="OcrMode", description="Controls when Optical Character Recognition is applied. Auto applies OCR only when needed, Force applies it to all pages, and Never disables OCR entirely."),
    ocr_language: Literal["auto", "ar", "ca", "zh", "da", "nl", "en", "fi", "fr", "de", "el", "ko", "it", "ja", "no", "pl", "pt", "ro", "ru", "sl", "es", "sv", "tr", "ua", "th"] | None = Field(None, alias="OcrLanguage", description="Specifies the language for OCR text recognition. Use auto-detection by default, or manually select a language if auto-detection fails."),
    include_formatting: bool | None = Field(None, alias="IncludeFormatting", description="When enabled, includes non-table content such as images and paragraphs in the Excel output alongside extracted tables."),
    single_sheet: bool | None = Field(None, alias="SingleSheet", description="When enabled, combines all extracted tables into a single worksheet instead of creating separate sheets."),
    decimal_separator: Literal["auto", "period", "comma"] | None = Field(None, alias="DecimalSeparator", description="Specifies the character used as a decimal separator in numeric values. Auto-detection uses the formatting from the document, or you can force a specific separator."),
    thousands_separator: Literal["auto", "period", "comma", "space"] | None = Field(None, alias="ThousandsSeparator", description="Specifies the character used as a thousands separator in numeric values. Auto-detection uses the formatting from the document, or you can force a specific separator."),
) -> dict[str, Any] | ToolResult:
    """Converts PDF documents to Excel spreadsheet format, with support for OCR text recognition, table extraction, and numeric formatting customization."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPdfToXlsxRequest(
            body=_models.PostConvertPdfToXlsxRequestBody(file_=file_, file_name=file_name, password=password, page_range=page_range, ocr_mode=ocr_mode, ocr_language=ocr_language, include_formatting=include_formatting, single_sheet=single_sheet, decimal_separator=decimal_separator, thousands_separator=thousands_separator)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_pdf_to_xlsx: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/pdf/to/xlsx"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_pdf_to_xlsx")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_pdf_to_xlsx", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_pdf_to_xlsx",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def validate_pdfa_conformance(
    file_: str | None = Field(None, alias="File", description="The PDF file to validate. Can be provided as a URL or raw file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output validation report file. The system sanitizes the filename, appends the appropriate extension, and adds indexing for multiple output files to ensure unique and safe file naming."),
    password: str | None = Field(None, alias="Password", description="Password required to open the PDF if it is password-protected."),
    expected_conformance: Literal["auto", "pdfA1a", "pdfA1b", "pdfA2a", "pdfA2b", "pdfA2u", "pdfA3a", "pdfA3b", "pdfA3u", "pdfA4", "pdfA4e", "pdfA4f"] | None = Field(None, alias="ExpectedConformance", description="The PDF/A conformance level to validate against. Use 'auto' to automatically detect the document's claimed conformance level, or specify a particular PDF/A version."),
) -> dict[str, Any] | ToolResult:
    """Validates a PDF file against PDF/A conformance standards. Analyzes the document to ensure it meets the specified PDF/A version requirements, with support for password-protected files and automatic conformance level detection."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPdfaToValidateRequest(
            body=_models.PostConvertPdfaToValidateRequestBody(file_=file_, file_name=file_name, password=password, expected_conformance=expected_conformance)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for validate_pdfa_conformance: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/pdfa/to/validate"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("validate_pdfa_conformance")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("validate_pdfa_conformance", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="validate_pdfa_conformance",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_png_to_gif(
    files: list[str] | None = Field(None, alias="Files", description="PNG image files to convert to GIF format. Accepts file URLs or direct file content. When using query or multipart parameters, each file must be indexed (Files[0], Files[1], etc.)."),
    file_name: str | None = Field(None, alias="FileName", description="Custom name for the output GIF file(s). The system automatically sanitizes the filename, appends the .gif extension, and adds numeric suffixes for multiple outputs (e.g., animation_0.gif, animation_1.gif) to ensure unique, safe filenames."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image to a different size."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions are larger than the target output dimensions."),
    animation_delay: int | None = Field(None, alias="AnimationDelay", description="Time interval between animation frames, specified in hundredths of a second. Controls the playback speed of the animated GIF.", ge=0, le=20000),
    animation_iterations: int | None = Field(None, alias="AnimationIterations", description="Number of times the animation loops. Set to 0 for infinite looping.", ge=0, le=1000),
) -> dict[str, Any] | ToolResult:
    """Convert PNG image files to animated GIF format with customizable animation settings. Supports single or batch file conversion with optional scaling and frame delay control."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPngToGifRequest(
            body=_models.PostConvertPngToGifRequestBody(files=files, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, animation_delay=animation_delay, animation_iterations=animation_iterations)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_png_to_gif: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/png/to/gif"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_png_to_gif")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_png_to_gif", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_png_to_gif",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["Files"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_image_png_to_jpg(
    file_: str | None = Field(None, alias="File", description="The image file to convert. Can be provided as a URL or raw file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.jpg, filename_1.jpg) for multiple outputs."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the target output size."),
    alpha_color: str | None = Field(None, alias="AlphaColor", description="Replace transparent areas with a specific color. Accepts RGBA or CMYK hex strings, or standard color names."),
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(None, alias="ColorSpace", description="Define the color space for the output image."),
) -> dict[str, Any] | ToolResult:
    """Convert a PNG image to JPG format with optional scaling, color space adjustment, and alpha channel handling. Supports both URL and file content input."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPngToJpgRequest(
            body=_models.PostConvertPngToJpgRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, alpha_color=alpha_color, color_space=color_space)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_image_png_to_jpg: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/png/to/jpg"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_image_png_to_jpg")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_image_png_to_jpg", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_image_png_to_jpg",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_image_to_pdf_png(
    file_: str | None = Field(None, alias="File", description="The image file to convert. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.pdf, output_1.pdf) for multiple files."),
    rotate: int | None = Field(None, alias="Rotate", description="Rotation angle in degrees for the image. Leave empty to automatically detect and apply rotation from EXIF metadata in TIFF and JPEG images.", ge=-360, le=360),
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(None, alias="ColorSpace", description="Color space for the output PDF. Defines how colors are represented in the document."),
    color_profile: Literal["default", "isocoatedv2"] | None = Field(None, alias="ColorProfile", description="Color profile for the output PDF. Some profiles override the ColorSpace setting."),
    pdfa: bool | None = Field(None, alias="Pdfa", description="Enable PDF/A-1b compliance for long-term archival and preservation of the document."),
    margin: str | None = Field(None, alias="Margin", description="Page margins in millimeters as 'horizontal,vertical' (e.g., '10,15')"),
) -> dict[str, Any] | ToolResult:
    """Convert PNG images to PDF format with optional image processing capabilities including rotation, color space adjustment, and PDF/A compliance."""

    # Call helper functions
    margin_parsed = parse_margin(margin)

    # Construct request model with validation
    try:
        _request = _models.PostConvertPngToPdfRequest(
            body=_models.PostConvertPngToPdfRequestBody(file_=file_, file_name=file_name, rotate=rotate, color_space=color_space, color_profile=color_profile, pdfa=pdfa, margin_horizontal=margin_parsed.get('MarginHorizontal') if margin_parsed else None, margin_vertical=margin_parsed.get('MarginVertical') if margin_parsed else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_image_to_pdf_png: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/png/to/pdf"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_image_to_pdf_png")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_image_to_pdf_png", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_image_to_pdf_png",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_image_png_to_pnm(
    file_: str | None = Field(None, alias="File", description="The image file to convert. Accepts either a URL reference or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output file. The system automatically sanitizes the filename, appends the correct .pnm extension, and adds numeric indexing (e.g., image_0.pnm, image_1.pnm) when multiple files are generated."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image to the target dimensions."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Apply scaling only when the input image dimensions exceed the target output size, leaving smaller images unchanged."),
    red: int | None = Field(None, description="Red channel value (0-255)"),
    green: int | None = Field(None, description="Green channel value (0-255)"),
    blue: int | None = Field(None, description="Blue channel value (0-255)"),
    alpha: int | None = Field(None, description="Alpha channel value (0-255), where 0 is fully transparent and 255 is fully opaque. Optional; if not provided, defaults to 255 (fully opaque)."),
) -> dict[str, Any] | ToolResult:
    """Convert a PNG image to PNM (Portable Anymap) format with optional scaling and proportional constraint controls. Supports both URL-based and direct file content input."""

    # Call helper functions
    transparent_color = build_transparent_color(red, green, blue, alpha)

    # Construct request model with validation
    try:
        _request = _models.PostConvertPngToPnmRequest(
            body=_models.PostConvertPngToPnmRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, transparent_color=transparent_color)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_image_png_to_pnm: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/png/to/pnm"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_image_png_to_pnm")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_image_png_to_pnm", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_image_png_to_pnm",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_image_to_svg(
    file_: str | None = Field(None, alias="File", description="The image file to convert. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output SVG file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.svg, filename_1.svg) for multiple output files."),
    preset: Literal["none", "detailed", "crisp", "graphic", "illustration", "noisyScan"] | None = Field(None, alias="Preset", description="A vectorization preset that applies pre-configured tracing settings optimized for specific image types. When selected, presets override all other converter options except ColorMode, ensuring consistent and balanced SVG output."),
    color_mode: Literal["color", "bw"] | None = Field(None, alias="ColorMode", description="Determines whether the image is traced in black-and-white or full color mode."),
    layering: Literal["cutout", "stacked"] | None = Field(None, alias="Layering", description="Specifies how color regions are arranged in the output SVG: cutout layers isolate each color region separately, while stacked overlays layer regions on top of each other."),
    curve_mode: Literal["pixel", "polygon", "spline"] | None = Field(None, alias="CurveMode", description="Defines the shape approximation method during tracing. Pixel mode follows exact pixel boundaries with minimal smoothing, Polygon creates straight-edged paths with sharp corners, and Spline generates smooth continuous curves for more natural shapes."),
) -> dict[str, Any] | ToolResult:
    """Converts a PNG image to scalable vector graphics (SVG) format using configurable tracing and vectorization settings. Supports preset configurations for different image types and offers fine-grained control over color handling, layering, and curve approximation."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPngToSvgRequest(
            body=_models.PostConvertPngToSvgRequestBody(file_=file_, file_name=file_name, preset=preset, color_mode=color_mode, layering=layering, curve_mode=curve_mode)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_image_to_svg: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/png/to/svg"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_image_to_svg")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_image_to_svg", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_image_to_svg",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_png_to_tiff(
    file_: str | None = Field(None, alias="File", description="The PNG image file to convert. Accepts either a URL reference or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output TIFF file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.tiff, output_1.tiff) for multiple files."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the target output size."),
    multi_page: bool | None = Field(None, alias="MultiPage", description="Generate a multi-page TIFF file when converting multiple images or pages."),
) -> dict[str, Any] | ToolResult:
    """Convert PNG images to TIFF format with optional scaling and multi-page support. Supports both URL-based and direct file uploads."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPngToTiffRequest(
            body=_models.PostConvertPngToTiffRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, multi_page=multi_page)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_png_to_tiff: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/png/to/tiff"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_png_to_tiff")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_png_to_tiff", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_png_to_tiff",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_image_png_to_webp(
    file_: str | None = Field(None, alias="File", description="The image file to convert. Accepts either a file upload or a URL pointing to the PNG image."),
    file_name: str | None = Field(None, alias="FileName", description="Custom name for the output WebP file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing for multiple output files to ensure unique, safe file naming."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the target output dimensions."),
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(None, alias="ColorSpace", description="Define the color space for the output image. Choose from standard color profiles or use the default setting."),
) -> dict[str, Any] | ToolResult:
    """Convert PNG images to WebP format with optional scaling and color space adjustments. Supports both file uploads and URL-based inputs."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPngToWebpRequest(
            body=_models.PostConvertPngToWebpRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, color_space=color_space)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_image_png_to_webp: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/png/to/webp"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_image_png_to_webp")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_image_png_to_webp", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_image_png_to_webp",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def translate_po_file(
    file_: str | None = Field(None, alias="File", description="The PO file to be converted and translated. Accepts either a file URL or raw file content in binary format."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output file(s). The API sanitizes the filename, appends the appropriate extension, and adds indexing (e.g., output_0.po, output_1.po) for multiple files to ensure unique, safe naming."),
    overwrite_translations: bool | None = Field(None, alias="OverwriteTranslations", description="When enabled, re-translates strings that already have existing translations in the PO file. Useful for updating outdated or low-quality translations."),
    translation_context: str | None = Field(None, alias="TranslationContext", description="Optional context to guide the translation engine. Provide a brief description of the product, audience, or domain to improve tone, terminology, and translation accuracy."),
    source_language: Literal["auto", "ar", "ca", "zh-cn", "zh-tw", "da", "nl", "en", "fi", "fr", "de", "el", "he", "hi", "id", "ko", "it", "ja", "no", "pl", "pt", "ro", "ru", "sl", "es", "sv", "tr", "uk", "vi", "th"] | None = Field(None, alias="SourceLanguage", description="The source language for translation. Use 'auto' to automatically detect the language from the PO file content, or specify a concrete language code."),
    target_language: Literal["auto", "ar", "ca", "zh-cn", "zh-tw", "da", "nl", "en", "fi", "fr", "de", "el", "he", "hi", "id", "ko", "it", "ja", "no", "pl", "pt", "ro", "ru", "sl", "es", "sv", "tr", "uk", "vi", "th"] | None = Field(None, alias="TargetLanguage", description="The target language for translation. Use 'auto' to preserve the language already defined in the PO file, or specify a concrete language code to override it."),
) -> dict[str, Any] | ToolResult:
    """Converts a PO (Portable Object) localization file and translates its strings to a target language. Supports automatic language detection, selective translation of untranslated strings, and optional context guidance for improved translation accuracy."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPoToTranslateRequest(
            body=_models.PostConvertPoToTranslateRequestBody(file_=file_, file_name=file_name, overwrite_translations=overwrite_translations, translation_context=translation_context, source_language=source_language, target_language=target_language)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for translate_po_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/po/to/translate"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("translate_po_file")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("translate_po_file", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="translate_po_file",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_presentation_to_jpg_template(
    file_: str | None = Field(None, alias="File", description="The presentation file to convert. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output file(s). The API automatically sanitizes the filename, appends the correct extension, and adds indexing for multiple outputs (e.g., presentation_0.jpg, presentation_1.jpg)."),
    password: str | None = Field(None, alias="Password", description="Password required to open password-protected presentations."),
    page_range: str | None = Field(None, alias="PageRange", description="Specifies which pages to convert using a range (e.g., 1-10) or comma-separated list (e.g., 1,2,5). Defaults to pages 1-2000."),
    convert_hidden_slides: bool | None = Field(None, alias="ConvertHiddenSlides", description="When enabled, includes hidden slides in the conversion output. Defaults to false."),
) -> dict[str, Any] | ToolResult:
    """Converts PowerPoint presentations (POTX format) to JPG images. Supports password-protected files, selective page ranges, and optional inclusion of hidden slides."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPotxToJpgRequest(
            body=_models.PostConvertPotxToJpgRequestBody(file_=file_, file_name=file_name, password=password, page_range=page_range, convert_hidden_slides=convert_hidden_slides)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_presentation_to_jpg_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/potx/to/jpg"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_presentation_to_jpg_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_presentation_to_jpg_template", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_presentation_to_jpg_template",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_presentation_template_to_pdf(
    file_: str | None = Field(None, alias="File", description="The presentation file to convert. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., report_0.pdf, report_1.pdf) for multiple output files."),
    password: str | None = Field(None, alias="Password", description="Password required to open password-protected presentations."),
    page_range: str | None = Field(None, alias="PageRange", description="Specifies which pages to convert using a range (e.g., 1-10) or comma-separated list (e.g., 1,2,5). Defaults to converting the first 2000 pages."),
    convert_hidden_slides: bool | None = Field(None, alias="ConvertHiddenSlides", description="When enabled, includes hidden slides in the PDF output. Defaults to false."),
    convert_metadata: bool | None = Field(None, alias="ConvertMetadata", description="When enabled, preserves document metadata such as title, author, and keywords in the PDF output. Defaults to true."),
    convert_speaker_notes: Literal["Disabled", "SeparatePage", "PageComments"] | None = Field(None, alias="ConvertSpeakerNotes", description="Determines how speaker notes are handled during conversion. Choose Disabled to exclude notes, SeparatePage to add notes on separate pages, or PageComments to embed notes as PDF comments."),
    pdfa: bool | None = Field(None, alias="Pdfa", description="When enabled, creates a PDF/A-3a compliant document for long-term archival. Defaults to false."),
) -> dict[str, Any] | ToolResult:
    """Converts PowerPoint presentations (POTX format) to PDF documents with support for selective page ranges, speaker notes handling, and PDF/A compliance options."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPotxToPdfRequest(
            body=_models.PostConvertPotxToPdfRequestBody(file_=file_, file_name=file_name, password=password, page_range=page_range, convert_hidden_slides=convert_hidden_slides, convert_metadata=convert_metadata, convert_speaker_notes=convert_speaker_notes, pdfa=pdfa)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_presentation_template_to_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/potx/to/pdf"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_presentation_template_to_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_presentation_template_to_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_presentation_template_to_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_presentation_to_png_template(
    file_: str | None = Field(None, alias="File", description="The presentation file to convert. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output PNG file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing for multiple output files to ensure unique identification."),
    password: str | None = Field(None, alias="Password", description="Password required to open password-protected presentations."),
    page_range: str | None = Field(None, alias="PageRange", description="Specifies which slides to convert using page numbers. Use ranges (e.g., 1-10) or comma-separated individual pages (e.g., 1,2,5)."),
    convert_hidden_slides: bool | None = Field(None, alias="ConvertHiddenSlides", description="When enabled, includes hidden slides in the conversion output."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="When enabled, maintains the original aspect ratio when scaling the output images."),
    rotate: int | None = Field(None, alias="Rotate", description="Rotates the output images by the specified angle in degrees.", ge=-360, le=360),
    red: int | None = Field(None, description="Red channel value (0-255)"),
    green: int | None = Field(None, description="Green channel value (0-255)"),
    blue: int | None = Field(None, description="Blue channel value (0-255)"),
    alpha: int | None = Field(None, description="Alpha channel value (0-255), where 0 is fully transparent and 255 is fully opaque. Optional; if not provided, defaults to 255 (fully opaque)."),
) -> dict[str, Any] | ToolResult:
    """Converts PowerPoint presentations (POTX format) to PNG images. Supports page range selection, hidden slide inclusion, image scaling, and rotation adjustments."""

    # Call helper functions
    transparent_color = build_transparent_color(red, green, blue, alpha)

    # Construct request model with validation
    try:
        _request = _models.PostConvertPotxToPngRequest(
            body=_models.PostConvertPotxToPngRequestBody(file_=file_, file_name=file_name, password=password, page_range=page_range, convert_hidden_slides=convert_hidden_slides, scale_proportions=scale_proportions, rotate=rotate, transparent_color=transparent_color)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_presentation_to_png_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/potx/to/png"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_presentation_to_png_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_presentation_to_png_template", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_presentation_to_png_template",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_potx_to_pptx(
    file_: str | None = Field(None, alias="File", description="The file to convert, provided either as a URL or as binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output file. The system automatically sanitizes the filename, appends the correct extension for the target format, and adds indexing (e.g., _0, _1) when multiple output files are generated from a single input."),
    password: str | None = Field(None, alias="Password", description="The password required to open the input file if it is password-protected."),
) -> dict[str, Any] | ToolResult:
    """Converts a PowerPoint template file (POTX format) to a standard PowerPoint presentation (PPTX format). Supports both file uploads and URL-based file sources, with optional password protection for encrypted documents."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPotxToPptxRequest(
            body=_models.PostConvertPotxToPptxRequestBody(file_=file_, file_name=file_name, password=password)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_potx_to_pptx: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/potx/to/pptx"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_potx_to_pptx")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_potx_to_pptx", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_potx_to_pptx",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_presentation_template_to_tiff(
    file_: str | None = Field(None, alias="File", description="The presentation file to convert. Accepts either a file URL or raw file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output TIFF file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing for multiple output files to ensure unique identification."),
    password: str | None = Field(None, alias="Password", description="Password required to open password-protected presentations."),
    page_range: str | None = Field(None, alias="PageRange", description="Specifies which pages to convert using a range or comma-separated list format."),
    convert_hidden_slides: bool | None = Field(None, alias="ConvertHiddenSlides", description="Whether to include hidden slides in the conversion output."),
    tiff_type: Literal["color24nc", "color32nc", "color24lzw", "color32lzw", "color24zip", "color32zip", "grayscale", "grayscalelzw", "grayscalezip", "monochromeg3", "monochromeg32d", "monochromeg4", "monochromelzw", "monochromepackbits"] | None = Field(None, alias="TiffType", description="Specifies the TIFF compression type and color depth for the output image."),
    multi_page: bool | None = Field(None, alias="MultiPage", description="Whether to combine all converted pages into a single multi-page TIFF file or create separate files per page."),
    fill_order: Literal["0", "1"] | None = Field(None, alias="FillOrder", description="Defines the bit order within each byte in the TIFF output."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Whether to maintain the original aspect ratio when scaling the output image."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Whether to apply scaling only when the input image dimensions exceed the target output dimensions."),
) -> dict[str, Any] | ToolResult:
    """Converts PowerPoint presentations (POTX format) to TIFF image files with support for selective page ranges, hidden slides, and customizable image compression and scaling options."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPotxToTiffRequest(
            body=_models.PostConvertPotxToTiffRequestBody(file_=file_, file_name=file_name, password=password, page_range=page_range, convert_hidden_slides=convert_hidden_slides, tiff_type=tiff_type, multi_page=multi_page, fill_order=fill_order, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_presentation_template_to_tiff: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/potx/to/tiff"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_presentation_template_to_tiff")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_presentation_template_to_tiff", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_presentation_template_to_tiff",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_presentation_to_webp_template(
    file_: str | None = Field(None, alias="File", description="The presentation file to convert. Accepts either a file URL or raw file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing for multiple outputs to ensure unique, safe file naming."),
    password: str | None = Field(None, alias="Password", description="Password required to open password-protected presentations."),
    page_range: str | None = Field(None, alias="PageRange", description="Specifies which slides to convert using a range (e.g., 1-10) or comma-separated list (e.g., 1,2,5)."),
    convert_hidden_slides: bool | None = Field(None, alias="ConvertHiddenSlides", description="When enabled, includes hidden slides in the conversion output."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="When enabled, maintains the original aspect ratio when scaling the output image."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="When enabled, applies scaling only if the input image dimensions exceed the output dimensions."),
) -> dict[str, Any] | ToolResult:
    """Converts PowerPoint presentations (POTX format) to WebP images. Supports page range selection, hidden slide inclusion, and image scaling options for flexible output control."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPotxToWebpRequest(
            body=_models.PostConvertPotxToWebpRequestBody(file_=file_, file_name=file_name, password=password, page_range=page_range, convert_hidden_slides=convert_hidden_slides, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_presentation_to_webp_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/potx/to/webp"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_presentation_to_webp_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_presentation_to_webp_template", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_presentation_to_webp_template",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_presentation_to_jpg_slideshow(
    file_: str | None = Field(None, alias="File", description="The presentation file to convert. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing for multiple output files to ensure unique identification."),
    password: str | None = Field(None, alias="Password", description="Password required to open password-protected presentation documents."),
    page_range: str | None = Field(None, alias="PageRange", description="Specifies which pages to convert using a range (e.g., 1-10) or comma-separated list (e.g., 1,2,5). Defaults to pages 1-2000."),
    convert_hidden_slides: bool | None = Field(None, alias="ConvertHiddenSlides", description="When enabled, includes hidden slides in the conversion output. Defaults to false."),
) -> dict[str, Any] | ToolResult:
    """Converts PPSX presentation files to JPG image format. Supports password-protected documents, selective page ranges, and optional inclusion of hidden slides."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPpsxToJpgRequest(
            body=_models.PostConvertPpsxToJpgRequestBody(file_=file_, file_name=file_name, password=password, page_range=page_range, convert_hidden_slides=convert_hidden_slides)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_presentation_to_jpg_slideshow: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/ppsx/to/jpg"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_presentation_to_jpg_slideshow")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_presentation_to_jpg_slideshow", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_presentation_to_jpg_slideshow",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_presentation_slideshow_to_pdf(
    file_: str | None = Field(None, alias="File", description="The presentation file to convert. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., report_0.pdf, report_1.pdf) for multiple output files."),
    password: str | None = Field(None, alias="Password", description="Password required to open password-protected presentations."),
    page_range: str | None = Field(None, alias="PageRange", description="Specifies which pages to convert using a range (e.g., 1-10) or comma-separated list (e.g., 1,2,5). Defaults to converting the first 2000 pages."),
    convert_hidden_slides: bool | None = Field(None, alias="ConvertHiddenSlides", description="When enabled, includes hidden slides in the PDF output."),
    convert_metadata: bool | None = Field(None, alias="ConvertMetadata", description="When enabled, preserves document metadata such as title, author, and keywords in the PDF output."),
    convert_speaker_notes: Literal["Disabled", "SeparatePage", "PageComments"] | None = Field(None, alias="ConvertSpeakerNotes", description="Determines how speaker notes are handled during conversion: Disabled (omitted), SeparatePage (on separate pages), or PageComments (as PDF comments)."),
    pdfa: bool | None = Field(None, alias="Pdfa", description="When enabled, creates a PDF/A-3a compliant document for long-term archival purposes."),
) -> dict[str, Any] | ToolResult:
    """Converts PowerPoint presentations (PPSX format) to PDF documents with support for selective page ranges, speaker notes handling, and PDF/A compliance options."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPpsxToPdfRequest(
            body=_models.PostConvertPpsxToPdfRequestBody(file_=file_, file_name=file_name, password=password, page_range=page_range, convert_hidden_slides=convert_hidden_slides, convert_metadata=convert_metadata, convert_speaker_notes=convert_speaker_notes, pdfa=pdfa)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_presentation_slideshow_to_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/ppsx/to/pdf"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_presentation_slideshow_to_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_presentation_slideshow_to_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_presentation_slideshow_to_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_presentation_to_png_slideshow(
    file_: str | None = Field(None, alias="File", description="The presentation file to convert. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.png, output_1.png) for multiple files."),
    password: str | None = Field(None, alias="Password", description="Password required to open protected presentations."),
    page_range: str | None = Field(None, alias="PageRange", description="Specifies which slides to convert using a range or comma-separated list (e.g., 1-10 or 1,2,5)."),
    convert_hidden_slides: bool | None = Field(None, alias="ConvertHiddenSlides", description="When enabled, includes hidden slides in the conversion output."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="When enabled, maintains the original aspect ratio when scaling the output image."),
    rotate: int | None = Field(None, alias="Rotate", description="Rotates the output image by the specified angle in degrees.", ge=-360, le=360),
    red: int | None = Field(None, description="Red channel value (0-255)"),
    green: int | None = Field(None, description="Green channel value (0-255)"),
    blue: int | None = Field(None, description="Blue channel value (0-255)"),
    alpha: int | None = Field(None, description="Alpha channel value (0-255), where 0 is fully transparent and 255 is fully opaque. Optional; if not provided, defaults to 255 (fully opaque)."),
) -> dict[str, Any] | ToolResult:
    """Converts PPSX presentation files to PNG image format, with support for selective slide conversion, hidden slide inclusion, and image transformation options."""

    # Call helper functions
    transparent_color = build_transparent_color(red, green, blue, alpha)

    # Construct request model with validation
    try:
        _request = _models.PostConvertPpsxToPngRequest(
            body=_models.PostConvertPpsxToPngRequestBody(file_=file_, file_name=file_name, password=password, page_range=page_range, convert_hidden_slides=convert_hidden_slides, scale_proportions=scale_proportions, rotate=rotate, transparent_color=transparent_color)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_presentation_to_png_slideshow: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/ppsx/to/png"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_presentation_to_png_slideshow")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_presentation_to_png_slideshow", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_presentation_to_png_slideshow",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_presentation_ppsx_to_pptx(
    file_: str | None = Field(None, alias="File", description="The presentation file to convert, provided either as a URL reference or as direct binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the converted output file. The system automatically sanitizes the filename, appends the correct PPTX extension, and adds numeric indexing (e.g., filename_0.pptx, filename_1.pptx) when multiple output files are generated from a single input."),
) -> dict[str, Any] | ToolResult:
    """Converts a PowerPoint Show file (PPSX) to PowerPoint Presentation format (PPTX). Accepts file input via URL or direct file content and generates a properly named output file."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPpsxToPptxRequest(
            body=_models.PostConvertPpsxToPptxRequestBody(file_=file_, file_name=file_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_presentation_ppsx_to_pptx: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/ppsx/to/pptx"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_presentation_ppsx_to_pptx")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_presentation_ppsx_to_pptx", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_presentation_ppsx_to_pptx",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_presentation_slideshow_to_tiff(
    file_: str | None = Field(None, alias="File", description="The presentation file to convert. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing for multiple output files to ensure unique identification."),
    password: str | None = Field(None, alias="Password", description="Password required to open password-protected presentations."),
    page_range: str | None = Field(None, alias="PageRange", description="Specifies which slides to convert using a range (e.g., 1-10) or comma-separated list (e.g., 1,2,5)."),
    convert_hidden_slides: bool | None = Field(None, alias="ConvertHiddenSlides", description="When enabled, includes hidden slides in the conversion output."),
    tiff_type: Literal["color24nc", "color32nc", "color24lzw", "color32lzw", "color24zip", "color32zip", "grayscale", "grayscalelzw", "grayscalezip", "monochromeg3", "monochromeg32d", "monochromeg4", "monochromelzw", "monochromepackbits"] | None = Field(None, alias="TiffType", description="Specifies the TIFF compression type and color depth. Options range from color formats with various compression algorithms to grayscale and monochrome variants."),
    multi_page: bool | None = Field(None, alias="MultiPage", description="When enabled, combines all slides into a single multi-page TIFF file. When disabled, generates separate TIFF files for each slide."),
    fill_order: Literal["0", "1"] | None = Field(None, alias="FillOrder", description="Defines the bit order within each byte in the TIFF file. Use 0 for least-significant-bit-first or 1 for most-significant-bit-first."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="When enabled, maintains the original aspect ratio when scaling the output image dimensions."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="When enabled, applies scaling only if the input image dimensions exceed the target output dimensions."),
) -> dict[str, Any] | ToolResult:
    """Converts PPSX presentation files to TIFF image format with support for selective slide ranges, hidden slides, and customizable TIFF compression and color settings."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPpsxToTiffRequest(
            body=_models.PostConvertPpsxToTiffRequestBody(file_=file_, file_name=file_name, password=password, page_range=page_range, convert_hidden_slides=convert_hidden_slides, tiff_type=tiff_type, multi_page=multi_page, fill_order=fill_order, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_presentation_slideshow_to_tiff: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/ppsx/to/tiff"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_presentation_slideshow_to_tiff")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_presentation_slideshow_to_tiff", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_presentation_slideshow_to_tiff",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_presentation_to_webp_slideshow(
    file_: str | None = Field(None, alias="File", description="The presentation file to convert. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output file(s). The API automatically sanitizes the filename, appends the correct extension, and adds indexing for multiple outputs (e.g., presentation_0.webp, presentation_1.webp)."),
    password: str | None = Field(None, alias="Password", description="Password required to open password-protected presentations."),
    page_range: str | None = Field(None, alias="PageRange", description="Specifies which slides to convert using page numbers or ranges. Separate multiple selections with commas."),
    convert_hidden_slides: bool | None = Field(None, alias="ConvertHiddenSlides", description="When enabled, includes hidden slides in the conversion output."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="When enabled, maintains the aspect ratio when scaling the output image."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="When enabled, scales the image only if the input is larger than the target output size."),
) -> dict[str, Any] | ToolResult:
    """Converts PowerPoint presentations (PPSX format) to WebP image format. Supports selective page conversion, hidden slide inclusion, and image scaling options."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPpsxToWebpRequest(
            body=_models.PostConvertPpsxToWebpRequestBody(file_=file_, file_name=file_name, password=password, page_range=page_range, convert_hidden_slides=convert_hidden_slides, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_presentation_to_webp_slideshow: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/ppsx/to/webp"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_presentation_to_webp_slideshow")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_presentation_to_webp_slideshow", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_presentation_to_webp_slideshow",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_presentation_ppt_to_pptx(
    file_: str | None = Field(None, alias="File", description="The presentation file to convert, provided either as a URL or as binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output PPTX file. The system automatically sanitizes the filename, appends the correct extension, and adds numeric indexing (e.g., presentation_0.pptx, presentation_1.pptx) if multiple files are generated."),
    password: str | None = Field(None, alias="Password", description="Password required to open the input presentation if it is password-protected."),
) -> dict[str, Any] | ToolResult:
    """Converts a PowerPoint presentation from legacy PPT format to modern PPTX format. Supports password-protected documents and accepts file input via URL or direct file content."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPptToPptxRequest(
            body=_models.PostConvertPptToPptxRequestBody(file_=file_, file_name=file_name, password=password)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_presentation_ppt_to_pptx: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/ppt/to/pptx"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_presentation_ppt_to_pptx")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_presentation_ppt_to_pptx", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_presentation_ppt_to_pptx",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_presentation_to_images(
    file_: str | None = Field(None, alias="File", description="The PowerPoint file to convert. Accepts either a file URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Custom name for the output file(s). The system automatically sanitizes the filename, appends the correct extension, and adds numeric indices for multiple output files to ensure unique identification."),
    password: str | None = Field(None, alias="Password", description="Password required to open password-protected PowerPoint documents."),
    page_range: str | None = Field(None, alias="PageRange", description="Specify which slides to convert using a range (e.g., 1-10) or comma-separated list (e.g., 1,2,5). Defaults to the first 2000 slides."),
    convert_hidden_slides: bool | None = Field(None, alias="ConvertHiddenSlides", description="When enabled, includes hidden slides in the conversion output. Defaults to false."),
) -> dict[str, Any] | ToolResult:
    """Convert PowerPoint presentations to individual JPG image files. Supports password-protected documents, selective page ranges, and optional inclusion of hidden slides."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPptxToJpgRequest(
            body=_models.PostConvertPptxToJpgRequestBody(file_=file_, file_name=file_name, password=password, page_range=page_range, convert_hidden_slides=convert_hidden_slides)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_presentation_to_images: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/pptx/to/jpg"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_presentation_to_images")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_presentation_to_images", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_presentation_to_images",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_presentation_to_pdf(
    file_: str | None = Field(None, alias="File", description="The presentation file to convert. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., report_0.pdf, report_1.pdf) for multiple output files."),
    password: str | None = Field(None, alias="Password", description="Password required to open password-protected presentations."),
    page_range: str | None = Field(None, alias="PageRange", description="Specifies which pages to convert using a range (e.g., 1-10) or comma-separated list (e.g., 1,2,5). Defaults to converting the first 2000 pages."),
    convert_hidden_slides: bool | None = Field(None, alias="ConvertHiddenSlides", description="When enabled, includes hidden slides in the PDF output. Defaults to false."),
    convert_metadata: bool | None = Field(None, alias="ConvertMetadata", description="When enabled, converts document metadata (title, author, keywords) to PDF metadata properties. Defaults to true."),
    convert_speaker_notes: Literal["Disabled", "SeparatePage", "PageComments"] | None = Field(None, alias="ConvertSpeakerNotes", description="Determines how speaker notes are handled during conversion. Choose Disabled to exclude notes, SeparatePage to append notes on separate pages, or PageComments to embed notes as PDF comments."),
    pdfa: bool | None = Field(None, alias="Pdfa", description="When enabled, creates a PDF/A-3a compliant document for long-term archival. Defaults to false."),
) -> dict[str, Any] | ToolResult:
    """Converts PowerPoint presentations (PPTX) to PDF format with support for selective page ranges, speaker notes handling, and PDF/A compliance. Allows customization of metadata conversion, hidden slide inclusion, and password-protected document access."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPptxToPdfRequest(
            body=_models.PostConvertPptxToPdfRequestBody(file_=file_, file_name=file_name, password=password, page_range=page_range, convert_hidden_slides=convert_hidden_slides, convert_metadata=convert_metadata, convert_speaker_notes=convert_speaker_notes, pdfa=pdfa)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_presentation_to_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/pptx/to/pdf"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_presentation_to_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_presentation_to_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_presentation_to_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_presentation_to_images_png(
    file_: str | None = Field(None, alias="File", description="The PowerPoint file to convert. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output file(s). The system sanitizes the filename, appends the correct extension automatically, and adds indexing (e.g., report_0.png, report_1.png) for multiple output files."),
    password: str | None = Field(None, alias="Password", description="Password required to open protected or encrypted presentations."),
    page_range: str | None = Field(None, alias="PageRange", description="Specify which slides to convert using a range (e.g., 1-10) or comma-separated list (e.g., 1,2,5)."),
    convert_hidden_slides: bool | None = Field(None, alias="ConvertHiddenSlides", description="Include hidden slides in the conversion output."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain aspect ratio when scaling the output images."),
    rotate: int | None = Field(None, alias="Rotate", description="Rotate the output images by the specified angle in degrees.", ge=-360, le=360),
    transparent_color: str | None = Field(None, alias="TransparentColor", description="Make pixels matching the specified color transparent by adding an alpha channel. Accepts RGBA or CMYK hex strings, color names, or RGB format (e.g., 255,255,255 or 255,255,255,150 with alpha channel)."),
) -> dict[str, Any] | ToolResult:
    """Convert PowerPoint presentations to PNG images with support for selective slide ranges, hidden slides, image transformations, and transparency settings."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPptxToPngRequest(
            body=_models.PostConvertPptxToPngRequestBody(file_=file_, file_name=file_name, password=password, page_range=page_range, convert_hidden_slides=convert_hidden_slides, scale_proportions=scale_proportions, rotate=rotate, transparent_color=transparent_color)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_presentation_to_images_png: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/pptx/to/png"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_presentation_to_images_png")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_presentation_to_images_png", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_presentation_to_images_png",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_presentation(
    file_: str | None = Field(None, alias="File", description="The presentation file to convert. Accepts either a URL pointing to the file or the raw file content as binary data."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output presentation file. The system automatically sanitizes the filename, appends the correct extension, and adds numeric indexing (e.g., presentation_0.pptx, presentation_1.pptx) if multiple files are generated from a single input."),
    password: str | None = Field(None, alias="Password", description="Password required to open the input presentation if it is password-protected."),
) -> dict[str, Any] | ToolResult:
    """Converts a PowerPoint presentation to PowerPoint format, with support for password-protected documents. Useful for standardizing presentation formats or re-encoding existing presentations."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPptxToPptxRequest(
            body=_models.PostConvertPptxToPptxRequestBody(file_=file_, file_name=file_name, password=password)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_presentation: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/pptx/to/pptx"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_presentation")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_presentation", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_presentation",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def encrypt_presentation(
    file_: str | None = Field(None, alias="File", description="The PowerPoint file to encrypt. Accepts either a file URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output encrypted presentation file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing if multiple files are generated."),
    encrypt_password: str | None = Field(None, alias="EncryptPassword", description="Password to encrypt the presentation. Only users with this password can open and view the file."),
) -> dict[str, Any] | ToolResult:
    """Convert and encrypt a PowerPoint presentation with password protection. The output file is automatically named and formatted for secure distribution."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPptxToProtectRequest(
            body=_models.PostConvertPptxToProtectRequestBody(file_=file_, file_name=file_name, encrypt_password=encrypt_password)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for encrypt_presentation: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/pptx/to/protect"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("encrypt_presentation")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("encrypt_presentation", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="encrypt_presentation",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_presentation_to_tiff(
    file_: str | None = Field(None, alias="File", description="The PowerPoint file to convert. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.tiff, output_1.tiff) for multi-page conversions."),
    password: str | None = Field(None, alias="Password", description="Password required to open password-protected presentations."),
    page_range: str | None = Field(None, alias="PageRange", description="Specifies which slides to convert using a range (e.g., 1-10) or comma-separated list (e.g., 1,2,5)."),
    convert_hidden_slides: bool | None = Field(None, alias="ConvertHiddenSlides", description="Whether to include hidden slides in the conversion."),
    tiff_type: Literal["color24nc", "color32nc", "color24lzw", "color32lzw", "color24zip", "color32zip", "grayscale", "grayscalelzw", "grayscalezip", "monochromeg3", "monochromeg32d", "monochromeg4", "monochromelzw", "monochromepackbits"] | None = Field(None, alias="TiffType", description="The TIFF compression and color format to use for output images."),
    multi_page: bool | None = Field(None, alias="MultiPage", description="Whether to combine all slides into a single multi-page TIFF file or create separate TIFF files for each slide."),
    fill_order: Literal["0", "1"] | None = Field(None, alias="FillOrder", description="The logical order of bits within each byte in the TIFF output."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Whether to maintain the original aspect ratio when scaling the output image dimensions."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Whether to apply scaling only when the input image is larger than the target output dimensions."),
) -> dict[str, Any] | ToolResult:
    """Converts PowerPoint presentations (PPTX) to TIFF image format with support for multi-page output, custom compression, and selective slide inclusion. Useful for creating archival-quality image files or preparing presentations for systems that require TIFF format."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPptxToTiffRequest(
            body=_models.PostConvertPptxToTiffRequestBody(file_=file_, file_name=file_name, password=password, page_range=page_range, convert_hidden_slides=convert_hidden_slides, tiff_type=tiff_type, multi_page=multi_page, fill_order=fill_order, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_presentation_to_tiff: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/pptx/to/tiff"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_presentation_to_tiff")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_presentation_to_tiff", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_presentation_to_tiff",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_presentation_to_webp(
    file_: str | None = Field(None, alias="File", description="The PowerPoint file to convert. Accepts either a file URL or raw file content in binary format."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output WebP file(s). The API automatically sanitizes the filename, appends the correct extension, and adds numeric indexing (e.g., presentation_0.webp, presentation_1.webp) when multiple slides are converted."),
    password: str | None = Field(None, alias="Password", description="Password required to open password-protected PowerPoint documents."),
    page_range: str | None = Field(None, alias="PageRange", description="Specify which slides to convert using a range (e.g., 1-10) or comma-separated list (e.g., 1,2,5). Defaults to converting the first 2000 slides."),
    convert_hidden_slides: bool | None = Field(None, alias="ConvertHiddenSlides", description="Include hidden slides in the conversion output. By default, hidden slides are excluded."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain aspect ratio when scaling the output image dimensions. Enabled by default to prevent image distortion."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Apply scaling only when the input image dimensions exceed the output dimensions. Prevents upscaling of smaller images."),
) -> dict[str, Any] | ToolResult:
    """Convert PowerPoint presentations to WebP image format with support for selective slide conversion, scaling options, and hidden slide inclusion. Each slide is converted to a separate WebP image file."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPptxToWebpRequest(
            body=_models.PostConvertPptxToWebpRequestBody(file_=file_, file_name=file_name, password=password, page_range=page_range, convert_hidden_slides=convert_hidden_slides, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_presentation_to_webp: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/pptx/to/webp"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_presentation_to_webp")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_presentation_to_webp", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_presentation_to_webp",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_prn_to_jpg(
    file_: str | None = Field(None, alias="File", description="The PRN file to convert, provided as either a publicly accessible URL or raw binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The desired name for the output JPG file. The API automatically sanitizes the filename, appends the .jpg extension, and adds numeric indexing (e.g., output_0.jpg, output_1.jpg) if multiple files are generated from a single input."),
) -> dict[str, Any] | ToolResult:
    """Converts a PRN (printer) file to JPG image format. Accepts file input as either a URL or raw file content and generates a JPG output file with sanitized naming."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPrnToJpgRequest(
            body=_models.PostConvertPrnToJpgRequestBody(file_=file_, file_name=file_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_prn_to_jpg: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/prn/to/jpg"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_prn_to_jpg")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_prn_to_jpg", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_prn_to_jpg",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_prn_to_pdf(
    file_: str | None = Field(None, alias="File", description="The PRN file to convert. Accepts either a URL or raw file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output PDF file. The system automatically sanitizes the filename, appends the .pdf extension, and adds numeric suffixes (e.g., report_0.pdf, report_1.pdf) when generating multiple files from a single input."),
    pdf_version: Literal["1.2", "1.3", "1.4", "1.5", "1.6", "1.7", "1.8", "2.0"] | None = Field(None, alias="PdfVersion", description="PDF specification version to use for the output document."),
    pdf_resolution: int | None = Field(None, alias="PdfResolution", description="Output resolution in dots per inch (DPI). Higher values produce better quality but larger file sizes.", ge=10, le=2400),
    pdf_title: str | None = Field(None, alias="PdfTitle", description="Custom title for the PDF document metadata. Use a single quote and space (' ') to omit the title."),
    pdf_subject: str | None = Field(None, alias="PdfSubject", description="Custom subject for the PDF document metadata. Use a single quote and space (' ') to omit the subject."),
    pdf_author: str | None = Field(None, alias="PdfAuthor", description="Custom author name for the PDF document metadata. Use a single quote and space (' ') to omit the author."),
    pdf_keywords: str | None = Field(None, alias="PdfKeywords", description="Custom keywords for the PDF document metadata, typically used for searchability. Use a single quote and space (' ') to omit keywords."),
    open_page: int | None = Field(None, alias="OpenPage", description="Page number where the PDF should open when first displayed in a viewer.", ge=1, le=3000),
    open_zoom: Literal["Default", "ActualSize", "FitPage", "FitWidth", "FitHeight", "FitVisible", "25", "50", "75", "100", "125", "150", "200", "400", "800", "1600", "2400", "3200", "6400"] | None = Field(None, alias="OpenZoom", description="Default zoom level applied when opening the PDF in a viewer. Select from preset percentages or fit-to-page options."),
    color_space: Literal["Default", "RGB", "CMYK", "Gray"] | None = Field(None, alias="ColorSpace", description="Color space model for the PDF output. RGB is standard for screen viewing, CMYK for print production, and Gray for monochrome documents."),
) -> dict[str, Any] | ToolResult:
    """Converts PRN (printer) files to PDF format with customizable metadata, resolution, and viewing preferences. Supports PDF version selection, color space configuration, and document properties customization."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPrnToPdfRequest(
            body=_models.PostConvertPrnToPdfRequestBody(file_=file_, file_name=file_name, pdf_version=pdf_version, pdf_resolution=pdf_resolution, pdf_title=pdf_title, pdf_subject=pdf_subject, pdf_author=pdf_author, pdf_keywords=pdf_keywords, open_page=open_page, open_zoom=open_zoom, color_space=color_space)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_prn_to_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/prn/to/pdf"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_prn_to_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_prn_to_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_prn_to_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_prn_to_png(
    file_: str | None = Field(None, alias="File", description="The PRN file to convert, provided as either a publicly accessible URL or raw binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output PNG file. The API automatically sanitizes the filename, appends the .png extension, and adds numeric indexing (e.g., output_0.png, output_1.png) if multiple files are generated from a single input."),
) -> dict[str, Any] | ToolResult:
    """Converts a PRN (printer) file to PNG image format. Accepts file input as either a URL or raw file content and generates a PNG output file with automatic naming."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPrnToPngRequest(
            body=_models.PostConvertPrnToPngRequestBody(file_=file_, file_name=file_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_prn_to_png: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/prn/to/png"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_prn_to_png")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_prn_to_png", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_prn_to_png",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_prn_to_tiff(
    file_: str | None = Field(None, alias="File", description="The PRN file to convert, provided either as a URL reference or raw binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output TIFF file. The system automatically sanitizes the filename, appends the correct .tiff extension, and adds numeric indexing (e.g., output_0.tiff, output_1.tiff) when multiple files are generated from a single input."),
) -> dict[str, Any] | ToolResult:
    """Converts a PRN (printer) file to TIFF image format. Accepts file input as a URL or binary content and generates a TIFF output file with automatic naming and extension handling."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPrnToTiffRequest(
            body=_models.PostConvertPrnToTiffRequestBody(file_=file_, file_name=file_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_prn_to_tiff: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/prn/to/tiff"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_prn_to_tiff")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_prn_to_tiff", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_prn_to_tiff",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_postscript_to_jpg(
    file_: str | None = Field(None, alias="File", description="The PostScript file to convert. Can be provided as a URL or raw binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output JPG file. The system automatically sanitizes the filename, appends the correct .jpg extension, and adds numeric indexing (e.g., output_0.jpg, output_1.jpg) when multiple files are generated from a single input."),
) -> dict[str, Any] | ToolResult:
    """Converts PostScript (PS) files to JPG image format. Accepts file input as a URL or binary content and generates a uniquely named output file."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPsToJpgRequest(
            body=_models.PostConvertPsToJpgRequestBody(file_=file_, file_name=file_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_postscript_to_jpg: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/ps/to/jpg"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_postscript_to_jpg")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_postscript_to_jpg", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_postscript_to_jpg",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_postscript_to_pdf(
    file_: str | None = Field(None, alias="File", description="The PostScript file to convert. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.pdf, filename_1.pdf) for multiple output files."),
    pdf_version: Literal["1.2", "1.3", "1.4", "1.5", "1.6", "1.7", "1.8", "2.0"] | None = Field(None, alias="PdfVersion", description="PDF specification version to use for the output document."),
    pdf_resolution: int | None = Field(None, alias="PdfResolution", description="Output resolution in dots per inch (DPI). Higher values produce better quality but larger file sizes.", ge=10, le=2400),
    pdf_title: str | None = Field(None, alias="PdfTitle", description="Custom title for the PDF document metadata. Use a single quote and space (' ') to omit the title."),
    pdf_subject: str | None = Field(None, alias="PdfSubject", description="Custom subject for the PDF document metadata. Use a single quote and space (' ') to omit the subject."),
    pdf_author: str | None = Field(None, alias="PdfAuthor", description="Custom author name for the PDF document metadata. Use a single quote and space (' ') to omit the author."),
    pdf_keywords: str | None = Field(None, alias="PdfKeywords", description="Custom keywords for the PDF document metadata, typically used for searchability. Use a single quote and space (' ') to omit keywords."),
    open_page: int | None = Field(None, alias="OpenPage", description="Page number where the PDF should open when first viewed.", ge=1, le=3000),
    open_zoom: Literal["Default", "ActualSize", "FitPage", "FitWidth", "FitHeight", "FitVisible", "25", "50", "75", "100", "125", "150", "200", "400", "800", "1600", "2400", "3200", "6400"] | None = Field(None, alias="OpenZoom", description="Default zoom level when opening the PDF. Choose from preset percentages or fit-to-page options."),
    color_space: Literal["Default", "RGB", "CMYK", "Gray"] | None = Field(None, alias="ColorSpace", description="Color space for the PDF output. RGB is suitable for screen viewing, CMYK for professional printing, and Gray for monochrome documents."),
) -> dict[str, Any] | ToolResult:
    """Converts PostScript files to PDF format with customizable metadata, resolution, and viewer settings. Supports URL or file content input with options to control PDF version, color space, and initial document appearance."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPsToPdfRequest(
            body=_models.PostConvertPsToPdfRequestBody(file_=file_, file_name=file_name, pdf_version=pdf_version, pdf_resolution=pdf_resolution, pdf_title=pdf_title, pdf_subject=pdf_subject, pdf_author=pdf_author, pdf_keywords=pdf_keywords, open_page=open_page, open_zoom=open_zoom, color_space=color_space)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_postscript_to_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/ps/to/pdf"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_postscript_to_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_postscript_to_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_postscript_to_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_postscript_to_png(
    file_: str | None = Field(None, alias="File", description="The PostScript file to convert. Can be provided as a URL reference or raw binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Custom name for the output PNG file. The system automatically sanitizes the filename, appends the correct .png extension, and adds numeric indexing (e.g., output_0.png, output_1.png) when multiple files are generated from a single input."),
) -> dict[str, Any] | ToolResult:
    """Converts a PostScript file to PNG image format. Accepts file input as a URL or binary content and generates a PNG output file with optional custom naming."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPsToPngRequest(
            body=_models.PostConvertPsToPngRequestBody(file_=file_, file_name=file_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_postscript_to_png: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/ps/to/png"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_postscript_to_png")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_postscript_to_png", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_postscript_to_png",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_postscript_to_tiff(
    file_: str | None = Field(None, alias="File", description="The PostScript file to convert. Provide either a publicly accessible URL or the raw file content as binary data."),
    file_name: str | None = Field(None, alias="FileName", description="Custom name for the output TIFF file(s). The system automatically sanitizes the name, appends the .tiff extension, and adds numeric indexing (e.g., document_0.tiff, document_1.tiff) if multiple files are generated."),
) -> dict[str, Any] | ToolResult:
    """Converts PostScript (PS) files to TIFF image format. Accepts file input via URL or direct file content and generates output with sanitized, uniquely-named TIFF file(s)."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPsToTiffRequest(
            body=_models.PostConvertPsToTiffRequestBody(file_=file_, file_name=file_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_postscript_to_tiff: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/ps/to/tiff"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_postscript_to_tiff")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_postscript_to_tiff", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_postscript_to_tiff",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_psd_to_jpg(
    file_: str | None = Field(None, alias="File", description="The PSD file to convert. Accepts either a file upload or a URL pointing to the source file."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output JPG file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing for multiple output files to ensure unique, safe file naming."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain aspect ratio when scaling the output image to a different size."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions are larger than the target output dimensions."),
    alpha_color: str | None = Field(None, alias="AlphaColor", description="Specify a color to replace transparent areas in the image. Accepts RGBA or CMYK hex strings, or standard color names."),
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(None, alias="ColorSpace", description="Define the color space for the output image."),
) -> dict[str, Any] | ToolResult:
    """Convert a PSD (Photoshop) file to JPG format with optional scaling, color space, and transparency handling. Supports both file uploads and URL-based sources."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPsdToJpgRequest(
            body=_models.PostConvertPsdToJpgRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, alpha_color=alpha_color, color_space=color_space)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_psd_to_jpg: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/psd/to/jpg"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_psd_to_jpg")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_psd_to_jpg", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_psd_to_jpg",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_image_psd_to_png(
    file_: str | None = Field(None, alias="File", description="The PSD image file to convert. Accepts either a URL reference or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output PNG file. The system automatically sanitizes the filename, appends the correct extension, and adds numeric indexing for multiple output files to ensure unique, safe file naming."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image to the target dimensions."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the target output size, preserving quality for smaller source images."),
    red: int | None = Field(None, description="Red channel value (0-255)"),
    green: int | None = Field(None, description="Green channel value (0-255)"),
    blue: int | None = Field(None, description="Blue channel value (0-255)"),
    alpha: int | None = Field(None, description="Alpha channel value (0-255), where 0 is fully transparent and 255 is fully opaque. Optional; if not provided, defaults to 255 (fully opaque)."),
) -> dict[str, Any] | ToolResult:
    """Convert a PSD (Photoshop) image file to PNG format with optional scaling and proportional constraints. Supports both URL-based and direct file uploads."""

    # Call helper functions
    transparent_color = build_transparent_color(red, green, blue, alpha)

    # Construct request model with validation
    try:
        _request = _models.PostConvertPsdToPngRequest(
            body=_models.PostConvertPsdToPngRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, transparent_color=transparent_color)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_image_psd_to_png: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/psd/to/png"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_image_psd_to_png")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_image_psd_to_png", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_image_psd_to_png",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_image_psd_to_pnm(
    file_: str | None = Field(None, alias="File", description="The image file to convert. Accepts a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output file. The system automatically sanitizes the filename, appends the correct extension for the target format, and adds indexing (e.g., filename_0.pnm, filename_1.pnm) when multiple files are generated."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions are larger than the desired output dimensions."),
    red: int | None = Field(None, description="Red channel value (0-255)"),
    green: int | None = Field(None, description="Green channel value (0-255)"),
    blue: int | None = Field(None, description="Blue channel value (0-255)"),
    alpha: int | None = Field(None, description="Alpha channel value (0-255), where 0 is fully transparent and 255 is fully opaque. Optional; if not provided, defaults to 255 (fully opaque)."),
) -> dict[str, Any] | ToolResult:
    """Convert a PSD (Photoshop) image file to PNM (Portable Anymap) format with optional scaling and proportional constraints."""

    # Call helper functions
    transparent_color = build_transparent_color(red, green, blue, alpha)

    # Construct request model with validation
    try:
        _request = _models.PostConvertPsdToPnmRequest(
            body=_models.PostConvertPsdToPnmRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, transparent_color=transparent_color)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_image_psd_to_pnm: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/psd/to/pnm"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_image_psd_to_pnm")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_image_psd_to_pnm", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_image_psd_to_pnm",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_psd_to_svg(
    file_: str | None = Field(None, alias="File", description="The PSD file to convert. Accepts either a URL pointing to the file or the raw file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output SVG file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.svg, output_1.svg) for multiple files."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain aspect ratio when scaling the output image."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Apply scaling only if the input image dimensions exceed the output dimensions."),
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(None, alias="ColorSpace", description="Define the color space for the output image."),
) -> dict[str, Any] | ToolResult:
    """Convert a PSD (Photoshop) file to SVG (Scalable Vector Graphics) format. Supports URL or file content input with optional scaling and color space configuration."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPsdToSvgRequest(
            body=_models.PostConvertPsdToSvgRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, color_space=color_space)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_psd_to_svg: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/psd/to/svg"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_psd_to_svg")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_psd_to_svg", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_psd_to_svg",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_psd_to_tiff(
    file_: str | None = Field(None, alias="File", description="The PSD file to convert. Accepts either a URL pointing to the file or the raw file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output TIFF file(s). The system automatically sanitizes the name, appends the correct extension, and adds indexing (e.g., output_0.tiff, output_1.tiff) for multi-page conversions."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain aspect ratio when scaling the output image to fit the target dimensions."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions are larger than the target output dimensions."),
    multi_page: bool | None = Field(None, alias="MultiPage", description="Generate a single multi-page TIFF file containing all layers or pages from the input PSD, rather than separate single-page files."),
) -> dict[str, Any] | ToolResult:
    """Convert PSD (Photoshop) files to TIFF format with optional scaling and multi-page support. Supports both URL-based and direct file uploads."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPsdToTiffRequest(
            body=_models.PostConvertPsdToTiffRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, multi_page=multi_page)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_psd_to_tiff: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/psd/to/tiff"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_psd_to_tiff")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_psd_to_tiff", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_psd_to_tiff",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_image_psd_to_webp(
    file_: str | None = Field(None, alias="File", description="The image file to convert. Accepts either a URL pointing to the file or the raw file content as binary data."),
    file_name: str | None = Field(None, alias="FileName", description="Custom name for the output file. The system automatically sanitizes the name, appends the correct .webp extension, and adds indexing (e.g., output_0.webp, output_1.webp) for multiple files."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image to a different size."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions are larger than the target output dimensions."),
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(None, alias="ColorSpace", description="Define the color space for the output image. Use 'default' for automatic detection, or specify a particular color model."),
) -> dict[str, Any] | ToolResult:
    """Convert a PSD (Photoshop) image file to WebP format with optional scaling and color space adjustments. Supports both URL-based and direct file uploads."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPsdToWebpRequest(
            body=_models.PostConvertPsdToWebpRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, color_space=color_space)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_image_psd_to_webp: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/psd/to/webp"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_image_psd_to_webp")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_image_psd_to_webp", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_image_psd_to_webp",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_publication_to_jpg(
    file_: str | None = Field(None, alias="File", description="The publication file to convert. Accepts either a URL or raw file content in binary format."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output JPG file(s). The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.jpg, filename_1.jpg) when multiple files are generated."),
    password: str | None = Field(None, alias="Password", description="Password required to open the publication file if it is password-protected."),
    jpg_type: Literal["jpeg", "jpegcmyk", "jpeggray"] | None = Field(None, alias="JpgType", description="The JPG color mode and encoding type for the output image."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Whether to maintain the original aspect ratio when scaling the output image to a different size."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Whether to apply scaling only when the input image dimensions exceed the target output dimensions."),
) -> dict[str, Any] | ToolResult:
    """Converts a publication file (PUB format) to JPG image format with configurable output quality, color mode, and scaling options. Supports password-protected documents and customizable output file naming."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPubToJpgRequest(
            body=_models.PostConvertPubToJpgRequestBody(file_=file_, file_name=file_name, password=password, jpg_type=jpg_type, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_publication_to_jpg: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/pub/to/jpg"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_publication_to_jpg")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_publication_to_jpg", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_publication_to_jpg",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_pub_to_pdf(
    file_: str | None = Field(None, alias="File", description="The Publisher file to convert. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output PDF file. The system sanitizes the filename, appends the correct extension, and adds indexing (e.g., report_0.pdf, report_1.pdf) for multiple output files."),
    password: str | None = Field(None, alias="Password", description="Password required to open the source document if it is password-protected."),
    convert_metadata: bool | None = Field(None, alias="ConvertMetadata", description="Whether to preserve document metadata (title, author, keywords) in the output PDF."),
    pdf_version: Literal["1.2", "1.3", "1.4", "1.5", "1.6", "1.7", "1.8", "2.0"] | None = Field(None, alias="PdfVersion", description="PDF specification version to use for the output document."),
    pdf_resolution: int | None = Field(None, alias="PdfResolution", description="Output resolution in dots per inch (DPI). Higher values improve quality but increase file size.", ge=10, le=2400),
    pdf_title: str | None = Field(None, alias="PdfTitle", description="Custom title for the PDF document. Use a single quote and space (' ') to remove the title entirely."),
    pdf_subject: str | None = Field(None, alias="PdfSubject", description="Custom subject for the PDF document. Use a single quote and space (' ') to remove the subject entirely."),
    pdf_author: str | None = Field(None, alias="PdfAuthor", description="Custom author name for the PDF document. Use a single quote and space (' ') to remove the author entirely."),
    pdf_keywords: str | None = Field(None, alias="PdfKeywords", description="Custom keywords for the PDF document. Use a single quote and space (' ') to remove the keywords entirely."),
    open_page: int | None = Field(None, alias="OpenPage", description="Page number where the PDF should open when first displayed.", ge=1, le=3000),
    open_zoom: Literal["Default", "ActualSize", "FitPage", "FitWidth", "FitHeight", "FitVisible", "25", "50", "75", "100", "125", "150", "200", "400", "800", "1600", "2400", "3200", "6400"] | None = Field(None, alias="OpenZoom", description="Default zoom level when opening the PDF. Choose from preset percentages or fit-to-page options."),
    rotate_page: Literal["Disabled", "ByPage", "All"] | None = Field(None, alias="RotatePage", description="Automatically rotate pages based on text orientation. 'ByPage' rotates each page individually, 'All' rotates based on the majority text direction, 'Disabled' skips rotation."),
    color_space: Literal["Default", "RGB", "CMYK", "Gray"] | None = Field(None, alias="ColorSpace", description="Color space for the PDF output. RGB is standard for screen viewing, CMYK for professional printing, and Gray for monochrome documents."),
) -> dict[str, Any] | ToolResult:
    """Converts a Publisher document to PDF format with customizable metadata, resolution, and viewer settings. Supports password-protected documents and automatic page rotation based on text orientation."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPubToPdfRequest(
            body=_models.PostConvertPubToPdfRequestBody(file_=file_, file_name=file_name, password=password, convert_metadata=convert_metadata, pdf_version=pdf_version, pdf_resolution=pdf_resolution, pdf_title=pdf_title, pdf_subject=pdf_subject, pdf_author=pdf_author, pdf_keywords=pdf_keywords, open_page=open_page, open_zoom=open_zoom, rotate_page=rotate_page, color_space=color_space)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_pub_to_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/pub/to/pdf"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_pub_to_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_pub_to_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_pub_to_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_pub_to_png(
    file_: str | None = Field(None, alias="File", description="The Publisher file to convert. Accepts either a URL or raw file content in binary format."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output PNG file. The API automatically sanitizes the filename, appends the .png extension, and adds numeric suffixes (e.g., output_0.png, output_1.png) if multiple files are generated."),
    password: str | None = Field(None, alias="Password", description="Password required to open the Publisher file if it is password-protected."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintains the original aspect ratio when scaling the output image to the target dimensions."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Applies scaling only when the input image dimensions exceed the target output dimensions, leaving smaller images unchanged."),
) -> dict[str, Any] | ToolResult:
    """Converts a Microsoft Publisher (.pub) file to PNG image format. Supports password-protected documents and provides scaling options to control output image dimensions."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPubToPngRequest(
            body=_models.PostConvertPubToPngRequestBody(file_=file_, file_name=file_name, password=password, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_pub_to_png: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/pub/to/png"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_pub_to_png")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_pub_to_png", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_pub_to_png",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_pub_to_tiff(
    file_: str | None = Field(None, alias="File", description="The file to convert. Accepts either a URL reference or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output file(s). The system automatically sanitizes the filename, appends the correct .tiff extension, and adds numeric suffixes (e.g., _0, _1) for multi-page outputs to ensure unique identification."),
    password: str | None = Field(None, alias="Password", description="Password required to open password-protected Publisher documents."),
    tiff_type: Literal["color24nc", "color32nc", "color24lzw", "color32lzw", "color24zip", "color32zip", "grayscale", "grayscalelzw", "grayscalezip", "monochromeg3", "monochromeg32d", "monochromeg4", "monochromelzw", "monochromepackbits"] | None = Field(None, alias="TiffType", description="Specifies the TIFF compression type and color depth. Options range from color formats (24/32-bit with various compression) to grayscale and monochrome variants."),
    multi_page: bool | None = Field(None, alias="MultiPage", description="When enabled, combines all pages into a single multi-page TIFF file. When disabled, generates separate TIFF files for each page."),
    fill_order: Literal["0", "1"] | None = Field(None, alias="FillOrder", description="Defines the logical bit order within each byte of the TIFF data. Use 0 for most standard applications or 1 for specific compatibility requirements."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="When enabled, maintains the original aspect ratio when resizing the output image. When disabled, allows free scaling without proportion constraints."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="When enabled, scaling is applied only if the input image dimensions exceed the target output dimensions. When disabled, scaling is applied regardless of input size."),
) -> dict[str, Any] | ToolResult:
    """Converts Microsoft Publisher (.pub) files to TIFF image format with configurable compression, color depth, and scaling options. Supports password-protected documents and multi-page output."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertPubToTiffRequest(
            body=_models.PostConvertPubToTiffRequestBody(file_=file_, file_name=file_name, password=password, tiff_type=tiff_type, multi_page=multi_page, fill_order=fill_order, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_pub_to_tiff: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/pub/to/tiff"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_pub_to_tiff")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_pub_to_tiff", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_pub_to_tiff",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_rtf_to_html(
    file_: str | None = Field(None, alias="File", description="The RTF file to convert. Accepts either a URL pointing to the file or the raw file content as binary data."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the generated HTML output file. The API automatically sanitizes the filename, appends the correct extension, and adds numeric suffixes (e.g., `document_0.html`, `document_1.html`) when multiple files are produced from a single input."),
    inline_images: bool | None = Field(None, alias="InlineImages", description="Whether to embed images directly into the HTML output as base64-encoded data URIs, creating a single self-contained file without external image dependencies."),
) -> dict[str, Any] | ToolResult:
    """Converts RTF (Rich Text Format) documents to HTML format. Optionally embeds images inline within the HTML output for self-contained documents."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertRtfToHtmlRequest(
            body=_models.PostConvertRtfToHtmlRequestBody(file_=file_, file_name=file_name, inline_images=inline_images)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_rtf_to_html: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/rtf/to/html"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_rtf_to_html")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_rtf_to_html", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_rtf_to_html",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_rtf_to_jpg(
    file_: str | None = Field(None, alias="File", description="The RTF file to convert. Accepts either a URL or raw file content in binary format."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output file(s). The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.jpg, output_1.jpg) for multiple files."),
    password: str | None = Field(None, alias="Password", description="Password required to open the RTF document if it is password-protected."),
    page_range: str | None = Field(None, alias="PageRange", description="Specifies which pages to convert using a range format. Only pages within this range will be included in the output."),
) -> dict[str, Any] | ToolResult:
    """Converts RTF (Rich Text Format) documents to JPG image format. Supports password-protected documents and allows specifying which pages to convert."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertRtfToJpgRequest(
            body=_models.PostConvertRtfToJpgRequestBody(file_=file_, file_name=file_name, password=password, page_range=page_range)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_rtf_to_jpg: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/rtf/to/jpg"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_rtf_to_jpg")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_rtf_to_jpg", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_rtf_to_jpg",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_rtf_to_pdf(
    file_: str | None = Field(None, alias="File", description="The RTF file to convert. Accepts either a URL or raw file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., report_0.pdf, report_1.pdf) for multiple output files."),
    password: str | None = Field(None, alias="Password", description="Password required to open password-protected RTF documents."),
    page_range: str | None = Field(None, alias="PageRange", description="Specifies which pages to convert using a range format (e.g., 1-10 converts pages 1 through 10)."),
    convert_markups: bool | None = Field(None, alias="ConvertMarkups", description="When enabled, includes document markups such as revisions and comments in the converted PDF."),
    convert_tags: bool | None = Field(None, alias="ConvertTags", description="When enabled, converts document structure tags to improve PDF accessibility for screen readers and assistive technologies."),
    convert_metadata: bool | None = Field(None, alias="ConvertMetadata", description="When enabled, preserves document metadata (Title, Author, Keywords, etc.) in the PDF metadata."),
    bookmark_mode: Literal["none", "headings", "bookmarks"] | None = Field(None, alias="BookmarkMode", description="Controls bookmark generation in the output PDF. Use 'none' to disable bookmarks, 'headings' to generate from document headings, or 'bookmarks' to use existing bookmarks from the source document."),
    update_toc: bool | None = Field(None, alias="UpdateToc", description="When enabled, automatically updates all tables of content in the document before conversion."),
    pdfa: bool | None = Field(None, alias="Pdfa", description="When enabled, creates a PDF/A-3a compliant document for long-term archival and preservation."),
) -> dict[str, Any] | ToolResult:
    """Converts RTF (Rich Text Format) documents to PDF format with support for advanced features like bookmarks, metadata preservation, and PDF/A compliance. Handles protected documents, page range selection, and document structure conversion."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertRtfToPdfRequest(
            body=_models.PostConvertRtfToPdfRequestBody(file_=file_, file_name=file_name, password=password, page_range=page_range, convert_markups=convert_markups, convert_tags=convert_tags, convert_metadata=convert_metadata, bookmark_mode=bookmark_mode, update_toc=update_toc, pdfa=pdfa)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_rtf_to_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/rtf/to/pdf"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_rtf_to_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_rtf_to_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_rtf_to_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_rtf_to_text(
    file_: str | None = Field(None, alias="File", description="The RTF file to convert. Accepts either a file URL or raw file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output text file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.txt, output_1.txt) for multiple files."),
    password: str | None = Field(None, alias="Password", description="Password required to open password-protected RTF documents."),
    substitutions: bool | None = Field(None, alias="Substitutions", description="When enabled, replaces special symbols with their text equivalents (e.g., © becomes (c))."),
    end_line_char: Literal["crlf", "cr", "lfcr", "lf"] | None = Field(None, alias="EndLineChar", description="Specifies the line ending character to use in the output text file."),
) -> dict[str, Any] | ToolResult:
    """Converts RTF (Rich Text Format) documents to plain text format. Supports password-protected files, symbol substitution, and configurable line ending characters."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertRtfToTxtRequest(
            body=_models.PostConvertRtfToTxtRequestBody(file_=file_, file_name=file_name, password=password, substitutions=substitutions, end_line_char=end_line_char)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_rtf_to_text: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/rtf/to/txt"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_rtf_to_text")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_rtf_to_text", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_rtf_to_text",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_svg_to_jpg(
    file_: str | None = Field(None, alias="File", description="The SVG file to convert. Accepts either a URL or raw file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output JPG file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.jpg, output_1.jpg) for multiple files."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain aspect ratio when scaling the output image."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the target output dimensions."),
    alpha_color: str | None = Field(None, alias="AlphaColor", description="Replace transparent areas with a specific color. Accepts RGBA or CMYK hex strings, or standard color names."),
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(None, alias="ColorSpace", description="Define the color space for the output image."),
) -> dict[str, Any] | ToolResult:
    """Convert SVG vector graphics to JPG raster format with customizable scaling, color space, and transparency handling options."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertSvgToJpgRequest(
            body=_models.PostConvertSvgToJpgRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, alpha_color=alpha_color, color_space=color_space)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_svg_to_jpg: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/svg/to/jpg"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_svg_to_jpg")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_svg_to_jpg", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_svg_to_jpg",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_svg_to_pdf(
    file_: str | None = Field(None, alias="File", description="The SVG file to convert. Can be provided as a file upload or as a URL pointing to the SVG resource."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the generated PDF output file. The system automatically sanitizes the filename, appends the .pdf extension, and adds numeric suffixes if multiple files are generated."),
    horizontal_alignment: Literal["left", "center", "right"] | None = Field(None, alias="HorizontalAlignment", description="Controls how the SVG image is positioned horizontally within the PDF page."),
    vertical_alignment: Literal["top", "center", "bottom"] | None = Field(None, alias="VerticalAlignment", description="Controls how the SVG image is positioned vertically within the PDF page."),
    background_color: str | None = Field(None, alias="BackgroundColor", description="Sets the background color of the PDF page. Accepts hexadecimal color codes (e.g., #FFFFFF), RGB values, HSL values, or standard color names."),
    use_image_page_size: bool | None = Field(None, alias="UseImagePageSize", description="When enabled, uses the SVG image's intrinsic width and height to determine the PDF page size, overriding any explicit page size settings."),
) -> dict[str, Any] | ToolResult:
    """Converts SVG (Scalable Vector Graphics) files to PDF format with customizable layout, alignment, and styling options. Supports both file uploads and URL-based inputs."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertSvgToPdfRequest(
            body=_models.PostConvertSvgToPdfRequestBody(file_=file_, file_name=file_name, horizontal_alignment=horizontal_alignment, vertical_alignment=vertical_alignment, background_color=background_color, use_image_page_size=use_image_page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_svg_to_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/svg/to/pdf"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_svg_to_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_svg_to_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_svg_to_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_svg_to_png(
    file_: str | None = Field(None, alias="File", description="The SVG file to convert. Accepts either a URL pointing to an SVG file or the raw SVG file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output PNG file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.png, output_1.png) for multiple files from a single input."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image to the target dimensions."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Apply scaling only when the input image dimensions exceed the target output dimensions, leaving smaller images unchanged."),
    red: int | None = Field(None, description="Red channel value (0-255)"),
    green: int | None = Field(None, description="Green channel value (0-255)"),
    blue: int | None = Field(None, description="Blue channel value (0-255)"),
    alpha: int | None = Field(None, description="Alpha channel value (0-255), where 0 is fully transparent and 255 is fully opaque. Optional; if not provided, defaults to 255 (fully opaque)."),
) -> dict[str, Any] | ToolResult:
    """Convert SVG (Scalable Vector Graphics) files to PNG (Portable Network Graphics) format. Supports both URL-based and direct file content input with optional scaling controls."""

    # Call helper functions
    transparent_color = build_transparent_color(red, green, blue, alpha)

    # Construct request model with validation
    try:
        _request = _models.PostConvertSvgToPngRequest(
            body=_models.PostConvertSvgToPngRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, transparent_color=transparent_color)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_svg_to_png: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/svg/to/png"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_svg_to_png")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_svg_to_png", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_svg_to_png",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_svg_to_pnm(
    file_: str | None = Field(None, alias="File", description="The SVG file to convert. Accepts either a URL pointing to the file or the raw file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output file. The system automatically sanitizes the filename, appends the correct .pnm extension, and adds numeric indexing (e.g., output_0.pnm, output_1.pnm) when multiple files are generated."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintains the original aspect ratio when scaling the output image to prevent distortion."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Applies scaling only when the input image dimensions exceed the target output dimensions, leaving smaller images unchanged."),
    red: int | None = Field(None, description="Red channel value (0-255)"),
    green: int | None = Field(None, description="Green channel value (0-255)"),
    blue: int | None = Field(None, description="Blue channel value (0-255)"),
    alpha: int | None = Field(None, description="Alpha channel value (0-255), where 0 is fully transparent and 255 is fully opaque. Optional; if not provided, defaults to 255 (fully opaque)."),
) -> dict[str, Any] | ToolResult:
    """Converts SVG (Scalable Vector Graphics) files to PNM (Portable Anymap) format. Supports URL or file content input with optional scaling and proportional constraint controls."""

    # Call helper functions
    transparent_color = build_transparent_color(red, green, blue, alpha)

    # Construct request model with validation
    try:
        _request = _models.PostConvertSvgToPnmRequest(
            body=_models.PostConvertSvgToPnmRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, transparent_color=transparent_color)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_svg_to_pnm: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/svg/to/pnm"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_svg_to_pnm")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_svg_to_pnm", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_svg_to_pnm",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_svg_image(
    file_: str | None = Field(None, alias="File", description="The SVG file to convert. Accepts either a URL reference or raw file content in binary format."),
    file_name: str | None = Field(None, alias="FileName", description="Custom name for the output file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.svg, filename_1.svg) for multiple outputs to ensure unique, safe file naming."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain aspect ratio when scaling the output image to a different size."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Apply scaling transformations only when the input image dimensions exceed the target output dimensions."),
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(None, alias="ColorSpace", description="Define the color space for the output image. Use 'default' to preserve the source color space, or specify a target color space for conversion."),
) -> dict[str, Any] | ToolResult:
    """Convert an SVG image file with optional scaling and color space adjustments. Supports URL or direct file content input and produces a new SVG file with customizable output naming."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertSvgToSvgRequest(
            body=_models.PostConvertSvgToSvgRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, color_space=color_space)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_svg_image: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/svg/to/svg"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_svg_image")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_svg_image", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_svg_image",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_svg_to_tiff(
    file_: str | None = Field(None, alias="File", description="The SVG file to convert. Accepts either a URL pointing to the file or the raw file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output TIFF file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.tiff, output_1.tiff) for multi-page conversions to ensure unique, safe file naming."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image to the target dimensions."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Apply scaling only when the input image dimensions exceed the target output dimensions, leaving smaller images unchanged."),
    multi_page: bool | None = Field(None, alias="MultiPage", description="Generate a single multi-page TIFF file containing all converted pages, or create separate TIFF files for each page when disabled."),
) -> dict[str, Any] | ToolResult:
    """Convert SVG (Scalable Vector Graphics) files to TIFF (Tagged Image File Format) with configurable scaling and multi-page output options. Supports both URL-based and direct file content input."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertSvgToTiffRequest(
            body=_models.PostConvertSvgToTiffRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, multi_page=multi_page)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_svg_to_tiff: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/svg/to/tiff"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_svg_to_tiff")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_svg_to_tiff", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_svg_to_tiff",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_svg_to_webp(
    file_: str | None = Field(None, alias="File", description="The SVG file to convert. Accepts either a file upload or a URL pointing to the SVG resource."),
    file_name: str | None = Field(None, alias="FileName", description="Custom name for the output WebP file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing for multiple outputs to ensure unique, safe file naming."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image to a different size."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the target output dimensions."),
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(None, alias="ColorSpace", description="Define the color space for the output WebP image. Choose from standard color profiles to optimize for different use cases."),
) -> dict[str, Any] | ToolResult:
    """Convert SVG images to WebP format with optional scaling and color space adjustments. Supports both file uploads and URL-based inputs."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertSvgToWebpRequest(
            body=_models.PostConvertSvgToWebpRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, color_space=color_space)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_svg_to_webp: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/svg/to/webp"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_svg_to_webp")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_svg_to_webp", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_svg_to_webp",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def fill_template_to_docx(
    file_: str | None = Field(None, alias="File", description="The Word template file to be converted. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the generated output file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.docx, filename_1.docx) for multiple outputs."),
    binding_method: Literal["properties", "placeholders"] | None = Field(None, alias="BindingMethod", description="Specifies how data values are bound to the template. Use 'properties' to fill Word document custom property fields, or 'placeholders' to search for and replace named placeholders within the document text."),
    json_payload: str | None = Field(None, alias="JsonPayload", description="JSON array of key-value pairs to populate the template. Structure varies by binding method: for properties, include Name, Value, and Type fields; for placeholders, supports strings, integers, images, tables, HTML, and conditional values with optional dimensions and links."),
) -> dict[str, Any] | ToolResult:
    """Converts a Word document template to DOCX format by populating it with data values. Supports binding data to either document properties or text placeholders, enabling dynamic document generation from templates."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertTemplateToDocxRequest(
            body=_models.PostConvertTemplateToDocxRequestBody(file_=file_, file_name=file_name, binding_method=binding_method, json_payload=json_payload)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for fill_template_to_docx: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/template/to/docx"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("fill_template_to_docx")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("fill_template_to_docx", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="fill_template_to_docx",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_template_to_pdf(
    file_: str | None = Field(None, alias="File", description="The template document to convert. Accepts either a URL reference or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the generated PDF output file. The system automatically sanitizes the filename, appends the .pdf extension, and adds numeric suffixes (e.g., report_0.pdf, report_1.pdf) when multiple files are generated."),
    json_payload: str | None = Field(None, alias="JsonPayload", description="JSON array of data to populate into the template. Supports custom document properties (string, integer, datetime, boolean types) and placeholders (string, image, table, html, conditional types). Images should be provided as base64-encoded strings with optional dimensions and links."),
    binding_method: Literal["properties", "placeholders"] | None = Field(None, alias="BindingMethod", description="Specifies how data is bound to the template. Use 'properties' to fill Word document custom properties fields, or 'placeholders' to search for and replace named placeholders within the document text."),
) -> dict[str, Any] | ToolResult:
    """Converts a template document to PDF format while populating custom properties or placeholders with provided data. Supports dynamic content injection including text, images, tables, and HTML elements."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertTemplateToPdfRequest(
            body=_models.PostConvertTemplateToPdfRequestBody(file_=file_, file_name=file_name, json_payload=json_payload, binding_method=binding_method)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_template_to_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/template/to/pdf"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_template_to_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_template_to_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_template_to_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_tiff_to_jpg(
    file_: str | None = Field(None, alias="File", description="The image file to convert. Can be provided as a file upload or as a URL pointing to a TIFF image."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output JPG file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., image_0.jpg, image_1.jpg) for multiple outputs from a single input."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image to a different size."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions are larger than the target output dimensions."),
    alpha_color: str | None = Field(None, alias="AlphaColor", description="Specify a color to replace transparent areas in the image. Accepts RGBA or CMYK hex color codes, or standard color names."),
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(None, alias="ColorSpace", description="Define the color space for the output image. Use 'default' for automatic detection, or specify a particular color model."),
) -> dict[str, Any] | ToolResult:
    """Convert TIFF image files to JPG format with optional scaling, color space adjustment, and transparency handling. Supports both file uploads and URL-based inputs."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertTiffToJpgRequest(
            body=_models.PostConvertTiffToJpgRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, alpha_color=alpha_color, color_space=color_space)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_tiff_to_jpg: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/tiff/to/jpg"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_tiff_to_jpg")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_tiff_to_jpg", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_tiff_to_jpg",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_tiff_to_pdf(
    file_: str | None = Field(None, alias="File", description="The TIFF image file to convert. Accepts either a file URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output PDF file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.pdf, output_1.pdf) when multiple files are generated from a single input."),
    rotate: int | None = Field(None, alias="Rotate", description="Rotation angle in degrees for the image. Specify a value between -360 and 360, or leave empty to automatically rotate based on EXIF data in TIFF and JPEG images.", ge=-360, le=360),
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(None, alias="ColorSpace", description="Color space for the output image. Choose from standard color spaces or use default for automatic detection."),
    color_profile: Literal["default", "isocoatedv2"] | None = Field(None, alias="ColorProfile", description="Color profile to apply to the output image. Some profiles may override the ColorSpace setting."),
    margin_horizontal: int | None = Field(None, alias="MarginHorizontal", description="Horizontal margin for the PDF page in millimeters. Valid range is 0 to 500 mm.", ge=0, le=500),
    margin_vertical: int | None = Field(None, alias="MarginVertical", description="Vertical margin for the PDF page in millimeters. Valid range is 0 to 500 mm.", ge=0, le=500),
    pdfa: bool | None = Field(None, alias="Pdfa", description="Enable PDF/A-1b compliance for long-term archival and preservation of the output PDF document."),
    alpha_channel: bool | None = Field(None, alias="AlphaChannel", description="Enable or disable the alpha channel (transparency) in the output image if available in the source TIFF."),
) -> dict[str, Any] | ToolResult:
    """Convert TIFF image files to PDF format with support for color space management, page margins, rotation, and PDF/A compliance. Handles single or multiple TIFF images and produces properly formatted PDF output."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertTiffToPdfRequest(
            body=_models.PostConvertTiffToPdfRequestBody(file_=file_, file_name=file_name, rotate=rotate, color_space=color_space, color_profile=color_profile, margin_horizontal=margin_horizontal, margin_vertical=margin_vertical, pdfa=pdfa, alpha_channel=alpha_channel)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_tiff_to_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/tiff/to/pdf"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_tiff_to_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_tiff_to_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_tiff_to_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_tiff_to_png(
    file_: str | None = Field(None, alias="File", description="The image file to convert, provided either as a URL or as binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output PNG file. The API automatically sanitizes the filename, appends the correct .png extension, and adds numeric indexing (e.g., image_0.png, image_1.png) when multiple files are generated from a single input."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Whether to maintain the original aspect ratio when scaling the output image."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Whether to apply scaling only when the input image dimensions exceed the target output dimensions."),
    red: int | None = Field(None, description="Red channel value (0-255)"),
    green: int | None = Field(None, description="Green channel value (0-255)"),
    blue: int | None = Field(None, description="Blue channel value (0-255)"),
    alpha: int | None = Field(None, description="Alpha channel value (0-255), where 0 is fully transparent and 255 is fully opaque. Optional; if not provided, defaults to 255 (fully opaque)."),
) -> dict[str, Any] | ToolResult:
    """Convert TIFF image files to PNG format with optional scaling and proportional constraint controls. Supports both URL-based and direct file content input."""

    # Call helper functions
    transparent_color = build_transparent_color(red, green, blue, alpha)

    # Construct request model with validation
    try:
        _request = _models.PostConvertTiffToPngRequest(
            body=_models.PostConvertTiffToPngRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, transparent_color=transparent_color)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_tiff_to_png: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/tiff/to/png"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_tiff_to_png")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_tiff_to_png", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_tiff_to_png",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_tiff_to_pnm(
    file_: str | None = Field(None, alias="File", description="The TIFF image file to convert. Accepts either a URL reference or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output PNM file. The system automatically sanitizes the filename, appends the correct extension, and adds numeric indexing (e.g., output_0.pnm, output_1.pnm) when multiple files are generated."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Apply scaling only when the input image dimensions exceed the target output dimensions."),
    red: int | None = Field(None, description="Red channel value (0-255)"),
    green: int | None = Field(None, description="Green channel value (0-255)"),
    blue: int | None = Field(None, description="Blue channel value (0-255)"),
    alpha: int | None = Field(None, description="Alpha channel value (0-255), where 0 is fully transparent and 255 is fully opaque. Optional; if not provided, defaults to 255 (fully opaque)."),
) -> dict[str, Any] | ToolResult:
    """Convert a TIFF image file to PNM (Portable Anymap) format. Supports optional image scaling with proportional constraints and conditional scaling based on input dimensions."""

    # Call helper functions
    transparent_color = build_transparent_color(red, green, blue, alpha)

    # Construct request model with validation
    try:
        _request = _models.PostConvertTiffToPnmRequest(
            body=_models.PostConvertTiffToPnmRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, transparent_color=transparent_color)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_tiff_to_pnm: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/tiff/to/pnm"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_tiff_to_pnm")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_tiff_to_pnm", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_tiff_to_pnm",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_tiff_to_svg(
    file_: str | None = Field(None, alias="File", description="The TIFF image file to convert. Can be provided as a URL or raw file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output SVG file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing for multiple output files to ensure unique, safe file naming."),
    preset: Literal["none", "detailed", "crisp", "graphic", "illustration", "noisyScan"] | None = Field(None, alias="Preset", description="Vectorization preset that applies pre-configured tracing settings optimized for specific image types. When selected, presets override individual converter options except ColorMode, providing consistent and balanced SVG results."),
    color_mode: Literal["color", "bw"] | None = Field(None, alias="ColorMode", description="Color processing mode for tracing the image. Choose between full color vectorization or black-and-white conversion."),
    layering: Literal["cutout", "stacked"] | None = Field(None, alias="Layering", description="Arrangement method for color regions in the output SVG. Cutout mode creates isolated layers, while stacked mode overlays regions for blending effects."),
    curve_mode: Literal["pixel", "polygon", "spline"] | None = Field(None, alias="CurveMode", description="Shape approximation method during tracing. Pixel mode follows exact boundaries with minimal smoothing, Polygon creates straight-edged paths with sharp corners, and Spline generates smooth continuous curves for natural-looking shapes."),
) -> dict[str, Any] | ToolResult:
    """Converts TIFF raster images to scalable SVG vector format using configurable tracing and vectorization settings. Supports preset configurations for different image types, color modes, and curve approximation methods."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertTiffToSvgRequest(
            body=_models.PostConvertTiffToSvgRequestBody(file_=file_, file_name=file_name, preset=preset, color_mode=color_mode, layering=layering, curve_mode=curve_mode)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_tiff_to_svg: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/tiff/to/svg"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_tiff_to_svg")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_tiff_to_svg", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_tiff_to_svg",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_tiff_image(
    file_: str | None = Field(None, alias="File", description="The image file to convert. Accepts either a URL reference or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Custom name for the output file. The system automatically sanitizes the name, appends the correct file extension, and adds indexing (e.g., filename_0.tiff, filename_1.tiff) for multiple output files."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain aspect ratio when scaling the output image to a different size."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Apply scaling only when the input image dimensions exceed the target output dimensions."),
    multi_page: bool | None = Field(None, alias="MultiPage", description="Generate a multi-page TIFF file when processing multiple images or pages."),
) -> dict[str, Any] | ToolResult:
    """Convert and optimize TIFF images with scaling and multi-page support. Accepts file input as URL or binary content and generates output with customizable naming and formatting options."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertTiffToTiffRequest(
            body=_models.PostConvertTiffToTiffRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, multi_page=multi_page)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_tiff_image: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/tiff/to/tiff"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_tiff_image")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_tiff_image", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_tiff_image",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_image_tiff_to_webp(
    file_: str | None = Field(None, alias="File", description="The image file to convert. Accepts either a URL pointing to a TIFF file or raw binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Custom name for the output WebP file. The system automatically sanitizes the filename, appends the correct extension, and adds numeric indexing for multiple output files to ensure unique, safe file naming."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image to a different size."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions are larger than the target output dimensions."),
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(None, alias="ColorSpace", description="Define the color space for the output image. Choose from standard color profiles or use the default setting."),
) -> dict[str, Any] | ToolResult:
    """Convert TIFF image files to WebP format with optional scaling and color space adjustments. Supports both URL-based and direct file uploads."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertTiffToWebpRequest(
            body=_models.PostConvertTiffToWebpRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, color_space=color_space)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_image_tiff_to_webp: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/tiff/to/webp"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_image_tiff_to_webp")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_image_tiff_to_webp", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_image_tiff_to_webp",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_text_to_image(
    file_: str | None = Field(None, alias="File", description="The text document to convert. Accepts either a file URL or raw file content in binary format."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output JPG file(s). The API automatically sanitizes the filename, appends the correct extension, and adds numeric indexing (e.g., document_0.jpg, document_1.jpg) when multiple files are generated from a single input."),
    password: str | None = Field(None, alias="Password", description="Password required to open password-protected documents."),
    page_range: str | None = Field(None, alias="PageRange", description="Specifies which pages to convert using a range format (e.g., 1-10 converts pages 1 through 10 inclusive)."),
) -> dict[str, Any] | ToolResult:
    """Converts text documents to JPG image format. Supports file uploads or URLs, with optional password protection for secured documents and configurable page range selection."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertTxtToJpgRequest(
            body=_models.PostConvertTxtToJpgRequestBody(file_=file_, file_name=file_name, password=password, page_range=page_range)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_text_to_image: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/txt/to/jpg"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_text_to_image")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_text_to_image", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_text_to_image",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_text_to_pdf(
    file_: str | None = Field(None, alias="File", description="The text file to convert. Accepts either a URL or raw file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the generated PDF output file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.pdf, filename_1.pdf) for multiple outputs."),
    page_range: str | None = Field(None, alias="PageRange", description="Specifies which pages to include in the output using a range format (e.g., 1-10 for pages 1 through 10)."),
    font_name: Literal["Arial", "Bahnschrift", "Calibri", "Cambria", "Consolas", "Constantia", "CourierNew", "Georgia", "Tahoma", "TimesNewRoman", "Verdana"] | None = Field(None, alias="FontName", description="The font to use for text rendering in the PDF. Select from available system fonts."),
    font_size: int | None = Field(None, alias="FontSize", description="The font size in points for text in the PDF.", ge=4, le=72),
    pdfa: bool | None = Field(None, alias="Pdfa", description="When enabled, creates a PDF/A-1b compliant document suitable for long-term archival and preservation."),
    margins: str | None = Field(None, alias="Margins", description="Page margins in millimeters as a comma-separated string in the format: left,right,top,bottom (e.g., '10,10,15,15')"),
) -> dict[str, Any] | ToolResult:
    """Converts text files to PDF format with customizable formatting options including font selection, size, and page range specification. Supports PDF/A-1b compliance for archival purposes."""

    # Call helper functions
    margins_parsed = parse_margins(margins)

    # Construct request model with validation
    try:
        _request = _models.PostConvertTxtToPdfRequest(
            body=_models.PostConvertTxtToPdfRequestBody(file_=file_, file_name=file_name, page_range=page_range, font_name=font_name, font_size=font_size, pdfa=pdfa, margin_left=margins_parsed.get('MarginLeft') if margins_parsed else None, margin_right=margins_parsed.get('MarginRight') if margins_parsed else None, margin_top=margins_parsed.get('MarginTop') if margins_parsed else None, margin_bottom=margins_parsed.get('MarginBottom') if margins_parsed else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_text_to_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/txt/to/pdf"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_text_to_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_text_to_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_text_to_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_vsdx_to_jpg(
    file_: str | None = Field(None, alias="File", description="The Visio file to convert, provided either as a publicly accessible URL or as binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Custom name for the output JPEG file. The system automatically sanitizes the filename, appends the correct .jpg extension, and adds numeric indexing (e.g., output_0.jpg, output_1.jpg) if multiple files are generated from a single input."),
) -> dict[str, Any] | ToolResult:
    """Converts a Visio diagram file (VSDX format) to JPEG image format. Accepts file input as a URL or binary content and generates optimized JPEG output with customizable naming."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertVsdxToJpgRequest(
            body=_models.PostConvertVsdxToJpgRequestBody(file_=file_, file_name=file_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_vsdx_to_jpg: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/vsdx/to/jpg"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_vsdx_to_jpg")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_vsdx_to_jpg", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_vsdx_to_jpg",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_vsdx_to_pdf(
    file_: str | None = Field(None, alias="File", description="The Visio file to convert. Accepts either a URL reference or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the generated PDF output file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., `document_0.pdf`, `document_1.pdf`) when multiple files are produced."),
    pdfa_version: Literal["none", "pdfA1b", "pdfA2b", "pdfA3b"] | None = Field(None, alias="PdfaVersion", description="PDF/A compliance version for the output file. Use 'none' for standard PDF, or specify a PDF/A version for long-term archival compliance."),
) -> dict[str, Any] | ToolResult:
    """Converts a Visio diagram file (VSDX format) to PDF format. Supports optional PDF/A compliance versions for archival purposes."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertVsdxToPdfRequest(
            body=_models.PostConvertVsdxToPdfRequestBody(file_=file_, file_name=file_name, pdfa_version=pdfa_version)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_vsdx_to_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/vsdx/to/pdf"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_vsdx_to_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_vsdx_to_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_vsdx_to_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_vsdx_to_png(
    file_: str | None = Field(None, alias="File", description="The Visio file to convert. Provide either a URL pointing to the file or the raw file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the generated PNG output file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., `diagram_0.png`, `diagram_1.png`) for multiple output files."),
    background_color: str | None = Field(None, alias="BackgroundColor", description="Background color for the generated PNG image. Specify a color name, RGB values (comma-separated), or HEX code. Use `transparent` to preserve transparency."),
) -> dict[str, Any] | ToolResult:
    """Converts a Visio diagram file (VSDX format) to PNG image format. Supports file input via URL or direct file content, with optional background color customization."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertVsdxToPngRequest(
            body=_models.PostConvertVsdxToPngRequestBody(file_=file_, file_name=file_name, background_color=background_color)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_vsdx_to_png: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/vsdx/to/png"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_vsdx_to_png")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_vsdx_to_png", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_vsdx_to_png",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_vsdx_to_tiff(
    file_: str | None = Field(None, alias="File", description="The Visio file to convert. Accepts either a URL reference or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output TIFF file(s). The system automatically sanitizes the filename, appends the correct extension, and adds numeric indexing (e.g., `diagram_0.tiff`, `diagram_1.tiff`) for multi-page outputs to ensure unique, safe file naming."),
    background_color: str | None = Field(None, alias="BackgroundColor", description="Background color for the generated TIFF images. Specify a color name (e.g., `white`, `black`), RGB values (comma-separated), HEX code, or `transparent` to preserve transparency."),
    multi_page: bool | None = Field(None, alias="MultiPage", description="Whether to generate a single multi-page TIFF file or separate single-page files. When enabled, all pages are combined into one TIFF; when disabled, each page becomes a separate file."),
) -> dict[str, Any] | ToolResult:
    """Converts Visio diagram files (VSDX format) to TIFF image format. Supports single or multi-page TIFF output with customizable background color handling."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertVsdxToTiffRequest(
            body=_models.PostConvertVsdxToTiffRequestBody(file_=file_, file_name=file_name, background_color=background_color, multi_page=multi_page)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_vsdx_to_tiff: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/vsdx/to/tiff"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_vsdx_to_tiff")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_vsdx_to_tiff", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_vsdx_to_tiff",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_webpage_to_jpg(
    file_name: str | None = Field(None, alias="FileName", description="Name for the output JPG file. The system automatically sanitizes the filename, appends the correct extension, and adds numeric indexing (e.g., output_0.jpg, output_1.jpg) when multiple files are generated."),
    ad_block: bool | None = Field(None, alias="AdBlock", description="Block advertisements from rendering on the webpage during conversion."),
    cookie_consent_block: bool | None = Field(None, alias="CookieConsentBlock", description="Automatically remove EU cookie consent banners and warnings from the webpage before conversion."),
    cookies: str | None = Field(None, alias="Cookies", description="Set additional cookies to include in the page request. Provide multiple cookies as semicolon-separated name=value pairs."),
    java_script: bool | None = Field(None, alias="JavaScript", description="Enable JavaScript execution on the webpage during conversion. Disable if the page should be rendered without running scripts."),
    wait_element: str | None = Field(None, alias="WaitElement", description="CSS selector for a DOM element. The converter will wait for this element to appear in the page before starting the conversion process."),
    user_css: str | None = Field(None, alias="UserCss", description="Custom CSS rules to apply to the webpage before conversion begins."),
    css_media_type: str | None = Field(None, alias="CssMediaType", description="CSS media type to use during conversion (e.g., screen, print, or custom media types). Controls how stylesheets are applied."),
    headers: str | None = Field(None, alias="Headers", description="Custom HTTP headers to include in the page request. Provide headers as pipe-separated pairs with colon-delimited name and value."),
    zoom: float | None = Field(None, alias="Zoom", description="Set the zoom level for webpage rendering. Values below 1.0 zoom out, values above 1.0 zoom in.", ge=0.1, le=10),
    url: str | None = Field(None, alias="Url", description="The URL of the webpage to convert. Special characters in the URL must be properly encoded."),
) -> dict[str, Any] | ToolResult:
    """Converts a webpage to a JPG image file with support for JavaScript rendering, ad blocking, cookie consent removal, and custom styling. Allows fine-grained control over page rendering behavior including element waiting, custom CSS, HTTP headers, and zoom levels."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertWebToJpgRequest(
            body=_models.PostConvertWebToJpgRequestBody(file_name=file_name, ad_block=ad_block, cookie_consent_block=cookie_consent_block, cookies=cookies, java_script=java_script, wait_element=wait_element, user_css=user_css, css_media_type=css_media_type, headers=headers, zoom=zoom, url=url)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_webpage_to_jpg: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/web/to/jpg"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_webpage_to_jpg")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_webpage_to_jpg", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_webpage_to_jpg",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_webpage_to_pdf(
    file_name: str | None = Field(None, alias="FileName", description="Name for the generated PDF output file. The system sanitizes the filename, appends the .pdf extension automatically, and adds numeric suffixes (e.g., report_0.pdf, report_1.pdf) when multiple files are generated from a single conversion."),
    ad_block: bool | None = Field(None, alias="AdBlock", description="Enable ad blocking to remove advertisements from the web page during conversion."),
    cookie_consent_block: bool | None = Field(None, alias="CookieConsentBlock", description="Automatically remove EU cookie consent banners and warnings from the web page before conversion."),
    cookies: str | None = Field(None, alias="Cookies", description="Provide additional cookies to include in the page request. Format as semicolon-separated key-value pairs."),
    java_script: bool | None = Field(None, alias="JavaScript", description="Allow JavaScript execution on the web page during conversion. Disable if the page contains scripts that interfere with rendering."),
    wait_element: str | None = Field(None, alias="WaitElement", description="CSS selector for a DOM element that must be present before conversion begins. Useful for waiting until dynamic content loads."),
    user_css: str | None = Field(None, alias="UserCss", description="Custom CSS rules to apply to the page before conversion. Useful for hiding elements, adjusting styles, or overriding page formatting."),
    css_media_type: str | None = Field(None, alias="CssMediaType", description="CSS media type to use during conversion. Controls how stylesheets are applied (e.g., screen for on-screen rendering, print for print-optimized output)."),
    headers: str | None = Field(None, alias="Headers", description="Custom HTTP headers to include in the page request. Format as pipe-separated header pairs with colon-delimited names and values."),
    load_lazy_content: bool | None = Field(None, alias="LoadLazyContent", description="Load images that are initially hidden and only appear when scrolled into view. Enables conversion of lazy-loaded image content."),
    viewport_width: int | None = Field(None, alias="ViewportWidth", description="Browser viewport width in pixels. Affects how the page layout renders. Valid range is 200 to 4000 pixels.", ge=200, le=4000),
    viewport_height: int | None = Field(None, alias="ViewportHeight", description="Browser viewport height in pixels. Affects how the page layout renders. Valid range is 200 to 4000 pixels.", ge=200, le=4000),
    respect_viewport: bool | None = Field(None, alias="RespectViewport", description="When enabled, the PDF renders as it appears in the browser. When disabled, uses Chrome's print-to-PDF behavior which may adjust layout for printing."),
    margin_top: int | None = Field(None, alias="MarginTop", description="Top margin of the PDF page in millimeters. Valid range is 0 to 500 mm.", ge=0, le=500),
    margin_right: int | None = Field(None, alias="MarginRight", description="Right margin of the PDF page in millimeters. Valid range is 0 to 500 mm.", ge=0, le=500),
    margin_bottom: int | None = Field(None, alias="MarginBottom", description="Bottom margin of the PDF page in millimeters. Valid range is 0 to 500 mm.", ge=0, le=500),
    margin_left: int | None = Field(None, alias="MarginLeft", description="Left margin of the PDF page in millimeters. Valid range is 0 to 500 mm.", ge=0, le=500),
    page_range: str | None = Field(None, alias="PageRange", description="Specify which pages to include in the output PDF. Use ranges (e.g., 1-10) or comma-separated page numbers (e.g., 1,2,5)."),
    background: bool | None = Field(None, alias="Background", description="Include background colors and images from the web page in the PDF output."),
    fixed_elements: Literal["fixed", "absolute", "relative", "hide"] | None = Field(None, alias="FixedElements", description="Modify how fixed-position elements are handled during conversion. Choose how to adapt fixed elements for PDF layout."),
    show_elements: str | None = Field(None, alias="ShowElements", description="CSS selector for DOM elements that must remain visible during conversion. All other elements will be hidden."),
    avoid_break_elements: str | None = Field(None, alias="AvoidBreakElements", description="CSS selector for elements that should not be split across page breaks. Keeps these elements intact on a single page."),
    break_before_elements: str | None = Field(None, alias="BreakBeforeElements", description="CSS selector for elements that should trigger a page break before them. Useful for forcing section starts on new pages."),
    break_after_elements: str | None = Field(None, alias="BreakAfterElements", description="CSS selector for elements that should trigger a page break after them. Useful for forcing content separation across pages."),
    url: str | None = Field(None, alias="Url", description="The web page URL to convert to PDF. Special characters in the URL must be properly encoded."),
    footer_content: str | None = Field(None, description="Main HTML content for the footer. Can include text and span elements."),
    footer_css: str | None = Field(None, description="Inline CSS styles for the footer. Example: '.right { float: right; } .left { float: left; }'"),
    footer_include_page_number: bool | None = Field(None, description="If true, include a span with class 'pageNumber' for dynamic page numbering."),
    footer_include_total_pages: bool | None = Field(None, description="If true, include a span with class 'totalPages' for total page count."),
    footer_include_title: bool | None = Field(None, description="If true, include a span with class 'title' for document title."),
    footer_include_date: bool | None = Field(None, description="If true, include a span with class 'date' for current date."),
    header_content: str | None = Field(None, description="Main HTML content for the header. Can include text and span elements."),
    header_css: str | None = Field(None, description="Inline CSS styles for the header. Example: '.right { float: right; } .left { float: left; }'"),
    header_include_page_number: bool | None = Field(None, description="If true, include a span with class 'pageNumber' for dynamic page numbering."),
    header_include_total_pages: bool | None = Field(None, description="If true, include a span with class 'totalPages' for total page count."),
    header_include_title: bool | None = Field(None, description="If true, include a span with class 'title' for document title."),
    header_include_date: bool | None = Field(None, description="If true, include a span with class 'date' for current date."),
) -> dict[str, Any] | ToolResult:
    """Converts a web page to PDF format with advanced rendering options including JavaScript execution, custom styling, viewport configuration, and page layout controls. Supports ad blocking, cookie consent removal, lazy content loading, and granular page break management."""

    # Call helper functions
    footer = build_footer_html(footer_content, footer_css, footer_include_page_number, footer_include_total_pages, footer_include_title, footer_include_date)
    h_header = build_header_html(header_content, header_css, header_include_page_number, header_include_total_pages, header_include_title, header_include_date)

    # Construct request model with validation
    try:
        _request = _models.PostConvertWebToPdfRequest(
            body=_models.PostConvertWebToPdfRequestBody(file_name=file_name, ad_block=ad_block, cookie_consent_block=cookie_consent_block, cookies=cookies, java_script=java_script, wait_element=wait_element, user_css=user_css, css_media_type=css_media_type, headers=headers, load_lazy_content=load_lazy_content, viewport_width=viewport_width, viewport_height=viewport_height, respect_viewport=respect_viewport, margin_top=margin_top, margin_right=margin_right, margin_bottom=margin_bottom, margin_left=margin_left, page_range=page_range, background=background, fixed_elements=fixed_elements, show_elements=show_elements, avoid_break_elements=avoid_break_elements, break_before_elements=break_before_elements, break_after_elements=break_after_elements, url=url, footer=footer, header=h_header)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_webpage_to_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/web/to/pdf"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_webpage_to_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_webpage_to_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_webpage_to_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_webpage_to_png(
    file_name: str | None = Field(None, alias="FileName", description="Name for the output PNG file. The system sanitizes the filename, appends the .png extension automatically, and adds numeric suffixes (e.g., _0, _1) when generating multiple files from a single conversion."),
    ad_block: bool | None = Field(None, alias="AdBlock", description="Block advertisements from appearing in the converted page."),
    cookie_consent_block: bool | None = Field(None, alias="CookieConsentBlock", description="Automatically remove EU cookie consent banners and warnings from the web page before conversion."),
    cookies: str | None = Field(None, alias="Cookies", description="Provide additional cookies to include in the page request. Separate multiple cookies with semicolons."),
    java_script: bool | None = Field(None, alias="JavaScript", description="Enable JavaScript execution during page rendering. Disable if the page contains problematic scripts."),
    wait_element: str | None = Field(None, alias="WaitElement", description="CSS selector for a DOM element. The converter will wait for this element to appear before starting the conversion, useful for pages with dynamic content."),
    user_css: str | None = Field(None, alias="UserCss", description="Custom CSS rules to apply to the page before conversion begins."),
    css_media_type: str | None = Field(None, alias="CssMediaType", description="CSS media type to use during rendering. Common values are 'screen' and 'print', but custom media types are also supported."),
    headers: str | None = Field(None, alias="Headers", description="Custom HTTP headers to include in the page request. Separate multiple headers with pipe characters, with each header formatted as name:value."),
    zoom: float | None = Field(None, alias="Zoom", description="Zoom level for rendering the webpage. Values below 1.0 zoom out, values above 1.0 zoom in.", ge=0.1, le=10),
    transparent_background: bool | None = Field(None, alias="TransparentBackground", description="Use a transparent background instead of the default white background. The source HTML body element should have its background color set to 'none' for this to work effectively."),
    url: str | None = Field(None, alias="Url", description="The URL of the web page to convert. Special characters in the URL must be properly encoded."),
) -> dict[str, Any] | ToolResult:
    """Converts a web page to a PNG image with support for JavaScript rendering, ad blocking, cookie consent removal, and custom styling. Allows fine-grained control over rendering behavior through CSS media types, zoom levels, and DOM element waiting."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertWebToPngRequest(
            body=_models.PostConvertWebToPngRequestBody(file_name=file_name, ad_block=ad_block, cookie_consent_block=cookie_consent_block, cookies=cookies, java_script=java_script, wait_element=wait_element, user_css=user_css, css_media_type=css_media_type, headers=headers, zoom=zoom, transparent_background=transparent_background, url=url)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_webpage_to_png: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/web/to/png"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_webpage_to_png")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_webpage_to_png", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_webpage_to_png",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_webpage_to_text(
    file_name: str | None = Field(None, alias="FileName", description="Name for the output text file. The API sanitizes the filename, appends the correct extension, and uses indexing (e.g., output_0.txt, output_1.txt) for multiple files to ensure unique, safe file naming."),
    ad_block: bool | None = Field(None, alias="AdBlock", description="Block advertisements and ad-related content from appearing in the converted text output."),
    cookie_consent_block: bool | None = Field(None, alias="CookieConsentBlock", description="Automatically remove EU cookie consent notices and related warnings from the web page before conversion."),
    cookies: str | None = Field(None, alias="Cookies", description="Set additional cookies to include in the page request. Provide multiple cookies as name-value pairs separated by semicolons."),
    java_script: bool | None = Field(None, alias="JavaScript", description="Enable JavaScript execution on the web page during conversion. Required for pages with dynamic content."),
    wait_element: str | None = Field(None, alias="WaitElement", description="CSS selector for a DOM element that must appear before conversion begins. Useful for waiting on dynamically loaded content."),
    user_css: str | None = Field(None, alias="UserCss", description="Custom CSS rules to apply to the page before conversion. Allows styling adjustments that affect the text output."),
    css_media_type: str | None = Field(None, alias="CssMediaType", description="CSS media type to use during conversion (e.g., screen, print, or custom types). Affects which styles are applied."),
    headers: str | None = Field(None, alias="Headers", description="Custom HTTP headers to include in the page request. Provide headers as name-value pairs separated by pipe characters, with each pair separated by a colon."),
    url: str | None = Field(None, alias="Url", description="URL of the web page to convert. Special characters such as query parameters must be properly URL-encoded."),
    extract_elements: str | None = Field(None, alias="ExtractElements", description="CSS selector to extract specific DOM elements instead of converting the entire page. Use class selectors (.class-name), ID selectors (#elementId), or tag names for targeted content retrieval."),
) -> dict[str, Any] | ToolResult:
    """Converts a web page to plain text format with optional content filtering, JavaScript execution, and targeted element extraction. Supports custom headers, cookies, CSS styling, and DOM element waiting for dynamic content."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertWebToTxtRequest(
            body=_models.PostConvertWebToTxtRequestBody(file_name=file_name, ad_block=ad_block, cookie_consent_block=cookie_consent_block, cookies=cookies, java_script=java_script, wait_element=wait_element, user_css=user_css, css_media_type=css_media_type, headers=headers, url=url, extract_elements=extract_elements)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_webpage_to_text: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/web/to/txt"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_webpage_to_text")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_webpage_to_text", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_webpage_to_text",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_webp_to_gif(
    files: list[str] | None = Field(None, alias="Files", description="WebP image file(s) to convert. Accept file uploads or URLs pointing to WebP images. When providing multiple files, each is converted independently to GIF format."),
    file_name: str | None = Field(None, alias="FileName", description="Custom name for the output GIF file(s). The system automatically sanitizes the filename, appends the .gif extension, and adds numeric suffixes (e.g., image_0.gif, image_1.gif) when converting multiple files."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain the original aspect ratio when resizing the output image."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Only resize the image if the input dimensions are larger than the target output size."),
    animation_delay: int | None = Field(None, alias="AnimationDelay", description="Time interval between animation frames, specified in hundredths of a second. Controls animation playback speed.", ge=0, le=20000),
    animation_iterations: int | None = Field(None, alias="AnimationIterations", description="Number of times the animation loops. Set to 0 for infinite looping.", ge=0, le=1000),
) -> dict[str, Any] | ToolResult:
    """Convert WebP image files to animated GIF format with customizable animation settings. Supports single or batch file conversion with optional scaling and frame delay control."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertWebpToGifRequest(
            body=_models.PostConvertWebpToGifRequestBody(files=files, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, animation_delay=animation_delay, animation_iterations=animation_iterations)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_webp_to_gif: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/webp/to/gif"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_webp_to_gif")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_webp_to_gif", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_webp_to_gif",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["Files"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_webp_to_jpg(
    file_: str | None = Field(None, alias="File", description="The image file to convert. Accepts either a URL pointing to a WebP image or the raw file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output JPG file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing for multiple outputs to ensure unique, safe file naming."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the target output dimensions."),
    alpha_color: str | None = Field(None, alias="AlphaColor", description="Replace transparent areas with a solid color. Accepts RGBA or CMYK hex strings, or standard color names."),
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(None, alias="ColorSpace", description="Define the color space for the output image."),
) -> dict[str, Any] | ToolResult:
    """Convert WebP image files to JPG format with optional scaling and color space adjustments. Supports both URL-based and direct file uploads."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertWebpToJpgRequest(
            body=_models.PostConvertWebpToJpgRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, alpha_color=alpha_color, color_space=color_space)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_webp_to_jpg: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/webp/to/jpg"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_webp_to_jpg")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_webp_to_jpg", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_webp_to_jpg",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_webp_to_pdf(
    file_: str | None = Field(None, alias="File", description="The WebP image file to convert. Provide either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the output PDF file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing for multiple output files to ensure unique, safe file naming."),
    rotate: int | None = Field(None, alias="Rotate", description="Rotate the output image by the specified degrees. Use a value between -360 and 360. Leave empty to apply automatic rotation based on EXIF data in TIFF and JPEG images.", ge=-360, le=360),
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(None, alias="ColorSpace", description="Set the color space for the output PDF. Choose from standard color space options to control how colors are represented in the final document."),
    color_profile: Literal["default", "isocoatedv2"] | None = Field(None, alias="ColorProfile", description="Apply a specific color profile to the output PDF. Some profiles may override the ColorSpace setting. Use 'isocoatedv2' for ISO Coated v2 profile compliance."),
    pdfa: bool | None = Field(None, alias="Pdfa", description="Enable PDF/A-1b compliance for the output document. When true, creates an archival-grade PDF suitable for long-term preservation."),
    margin: str | None = Field(None, alias="Margin", description="Page margins in millimeters as 'horizontal,vertical' (e.g., '10,20')"),
) -> dict[str, Any] | ToolResult:
    """Convert WebP image files to PDF format with support for rotation, color space configuration, and PDF/A compliance. Accepts file input as URL or binary content and generates a properly named output PDF file."""

    # Call helper functions
    margin_parsed = parse_margin(margin)

    # Construct request model with validation
    try:
        _request = _models.PostConvertWebpToPdfRequest(
            body=_models.PostConvertWebpToPdfRequestBody(file_=file_, file_name=file_name, rotate=rotate, color_space=color_space, color_profile=color_profile, pdfa=pdfa, margin_horizontal=margin_parsed.get('MarginHorizontal') if margin_parsed else None, margin_vertical=margin_parsed.get('MarginVertical') if margin_parsed else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_webp_to_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/webp/to/pdf"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_webp_to_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_webp_to_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_webp_to_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_webp_to_png(
    file_: str | None = Field(None, alias="File", description="The image file to convert, provided either as a URL or raw file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output PNG file. The API automatically sanitizes the filename, appends the correct .png extension, and adds numeric indexing (e.g., image_0.png, image_1.png) when multiple files are generated from a single input."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Whether to maintain the original aspect ratio when scaling the output image."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Whether to apply scaling only when the input image dimensions exceed the target output dimensions."),
    red: int | None = Field(None, description="Red channel value (0-255)"),
    green: int | None = Field(None, description="Green channel value (0-255)"),
    blue: int | None = Field(None, description="Blue channel value (0-255)"),
    alpha: int | None = Field(None, description="Alpha channel value (0-255), where 0 is fully transparent and 255 is fully opaque. Optional; if not provided, defaults to 255 (fully opaque)."),
) -> dict[str, Any] | ToolResult:
    """Convert WebP image files to PNG format with optional scaling and proportional constraints. Supports both URL-based and direct file content input."""

    # Call helper functions
    transparent_color = build_transparent_color(red, green, blue, alpha)

    # Construct request model with validation
    try:
        _request = _models.PostConvertWebpToPngRequest(
            body=_models.PostConvertWebpToPngRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, transparent_color=transparent_color)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_webp_to_png: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/webp/to/png"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_webp_to_png")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_webp_to_png", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_webp_to_png",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_webp_to_pnm(
    file_: str | None = Field(None, alias="File", description="The image file to convert, provided as a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.pnm, output_1.pnm) for multiple files."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Apply scaling only when the input image dimensions exceed the target output dimensions."),
    red: int | None = Field(None, description="Red channel value (0-255)"),
    green: int | None = Field(None, description="Green channel value (0-255)"),
    blue: int | None = Field(None, description="Blue channel value (0-255)"),
    alpha: int | None = Field(None, description="Alpha channel value (0-255), where 0 is fully transparent and 255 is fully opaque. Optional; if not provided, defaults to 255 (fully opaque)."),
) -> dict[str, Any] | ToolResult:
    """Convert a WebP image to PNM (Portable Anymap) format with optional scaling and proportional constraint controls."""

    # Call helper functions
    transparent_color = build_transparent_color(red, green, blue, alpha)

    # Construct request model with validation
    try:
        _request = _models.PostConvertWebpToPnmRequest(
            body=_models.PostConvertWebpToPnmRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, transparent_color=transparent_color)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_webp_to_pnm: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/webp/to/pnm"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_webp_to_pnm")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_webp_to_pnm", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_webp_to_pnm",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_webp_to_svg(
    file_: str | None = Field(None, alias="File", description="The WebP image file to convert. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output SVG file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.svg, output_1.svg) for multiple files."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain aspect ratio when scaling the output image."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the output dimensions."),
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(None, alias="ColorSpace", description="Define the color space for the output SVG image."),
) -> dict[str, Any] | ToolResult:
    """Convert WebP image files to SVG vector format. Supports URL or file content input with optional scaling and color space configuration."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertWebpToSvgRequest(
            body=_models.PostConvertWebpToSvgRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, color_space=color_space)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_webp_to_svg: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/webp/to/svg"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_webp_to_svg")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_webp_to_svg", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_webp_to_svg",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_webp_to_tiff(
    file_: str | None = Field(None, alias="File", description="The WebP image file to convert. Provide either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output TIFF file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.tiff, output_1.tiff) for multiple files."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the target output dimensions."),
    multi_page: bool | None = Field(None, alias="MultiPage", description="Generate a multi-page TIFF file when converting. If disabled, creates a single-page TIFF."),
) -> dict[str, Any] | ToolResult:
    """Convert WebP image files to TIFF format with optional scaling and multi-page support. Accepts file input as URL or binary content and generates properly named output file(s)."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertWebpToTiffRequest(
            body=_models.PostConvertWebpToTiffRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, multi_page=multi_page)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_webp_to_tiff: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/webp/to/tiff"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_webp_to_tiff")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_webp_to_tiff", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_webp_to_tiff",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_webp_image(
    file_: str | None = Field(None, alias="File", description="The image file to convert. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.webp, filename_1.webp) for multiple outputs to ensure unique identification."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the target output dimensions."),
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(None, alias="ColorSpace", description="The color space to apply to the output image."),
) -> dict[str, Any] | ToolResult:
    """Convert a WebP image to WebP format with optional scaling and color space adjustments. Supports URL or file content input and generates a uniquely named output file."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertWebpToWebpRequest(
            body=_models.PostConvertWebpToWebpRequestBody(file_=file_, file_name=file_name, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger, color_space=color_space)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_webp_image: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/webp/to/webp"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_webp_image")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_webp_image", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_webp_image",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_wpd_to_pdf(
    file_: str | None = Field(None, alias="File", description="The document file to convert. Accepts either a URL reference or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the generated output PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., report_0.pdf, report_1.pdf) for multiple output files."),
    password: str | None = Field(None, alias="Password", description="Password required to open password-protected documents."),
    page_range: str | None = Field(None, alias="PageRange", description="Specifies which pages to convert using a range format (e.g., 1-10 converts pages 1 through 10)."),
    convert_markups: bool | None = Field(None, alias="ConvertMarkups", description="Includes document markups such as revisions and comments in the converted PDF."),
    convert_tags: bool | None = Field(None, alias="ConvertTags", description="Preserves document structure tags in the PDF for improved accessibility and screen reader compatibility."),
    convert_metadata: bool | None = Field(None, alias="ConvertMetadata", description="Transfers document metadata (title, author, keywords) from the source document to PDF metadata properties."),
    bookmark_mode: Literal["none", "headings", "bookmarks"] | None = Field(None, alias="BookmarkMode", description="Controls bookmark generation in the output PDF. Use 'none' to disable bookmarks, 'headings' to auto-generate from document headings, or 'bookmarks' to use existing bookmarks from the source file."),
    update_toc: bool | None = Field(None, alias="UpdateToc", description="Automatically updates all tables of content in the document before conversion to ensure accuracy in the PDF output."),
    pdfa: bool | None = Field(None, alias="Pdfa", description="Generates a PDF/A-3a compliant document for long-term archival and compliance requirements."),
) -> dict[str, Any] | ToolResult:
    """Converts WordPerfect documents (.wpd) to PDF format with support for metadata preservation, accessibility tags, and PDF/A compliance. Handles protected documents and allows selective page range conversion."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertWpdToPdfRequest(
            body=_models.PostConvertWpdToPdfRequestBody(file_=file_, file_name=file_name, password=password, page_range=page_range, convert_markups=convert_markups, convert_tags=convert_tags, convert_metadata=convert_metadata, bookmark_mode=bookmark_mode, update_toc=update_toc, pdfa=pdfa)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_wpd_to_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/wpd/to/pdf"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_wpd_to_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_wpd_to_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_wpd_to_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_spreadsheet_format(
    file_: str | None = Field(None, alias="File", description="The spreadsheet file to convert. Accepts either a URL pointing to the file or the raw file content as binary data."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output file(s). The system automatically sanitizes the filename, appends the correct extension, and adds numeric suffixes (e.g., `report_0.xlsx`, `report_1.xlsx`) when multiple files are generated from a single input."),
    password: str | None = Field(None, alias="Password", description="Password required to open the input file if it is password-protected."),
) -> dict[str, Any] | ToolResult:
    """Converts an Excel spreadsheet file to Excel format, with support for password-protected documents. Useful for standardizing file formats or re-encoding existing spreadsheets."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertXlsToXlsRequest(
            body=_models.PostConvertXlsToXlsRequestBody(file_=file_, file_name=file_name, password=password)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_spreadsheet_format: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/xls/to/xls"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_spreadsheet_format")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_spreadsheet_format", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_spreadsheet_format",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_spreadsheet_xls_to_xlsx(
    file_: str | None = Field(None, alias="File", description="The spreadsheet file to convert. Accepts either a URL pointing to the file or the raw file content as binary data."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output file. The system automatically sanitizes the filename, appends the correct XLSX extension, and adds numeric indexing (e.g., report_0.xlsx, report_1.xlsx) when multiple files are generated from a single input."),
    password: str | None = Field(None, alias="Password", description="The password required to open the input file if it is password-protected."),
) -> dict[str, Any] | ToolResult:
    """Converts Microsoft Excel files from the legacy XLS format to the modern XLSX format. Supports password-protected documents and generates uniquely named output files."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertXlsToXlsxRequest(
            body=_models.PostConvertXlsToXlsxRequestBody(file_=file_, file_name=file_name, password=password)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_spreadsheet_xls_to_xlsx: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/xls/to/xlsx"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_spreadsheet_xls_to_xlsx")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_spreadsheet_xls_to_xlsx", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_spreadsheet_xls_to_xlsx",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_xlsb_to_csv(
    file_: str | None = Field(None, alias="File", description="The XLSB file to convert. Can be provided as a file upload or as a URL pointing to the source file."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output CSV file. The system automatically sanitizes the filename, appends the correct extension, and adds numeric indexing (e.g., output_0.csv, output_1.csv) if multiple files are generated."),
    password: str | None = Field(None, alias="Password", description="Password required to open the XLSB file if it is password-protected."),
) -> dict[str, Any] | ToolResult:
    """Converts an Excel Binary Workbook (XLSB) file to CSV format. Supports both file uploads and URL-based sources, with optional password protection for encrypted documents."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertXlsbToCsvRequest(
            body=_models.PostConvertXlsbToCsvRequestBody(file_=file_, file_name=file_name, password=password)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_xlsb_to_csv: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/xlsb/to/csv"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_xlsb_to_csv")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_xlsb_to_csv", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_xlsb_to_csv",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_xlsb_to_pdf(
    file_: str | None = Field(None, alias="File", description="The file to convert, provided as a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., report_0.pdf, report_1.pdf) for multiple output files."),
    password: str | None = Field(None, alias="Password", description="Password required to open password-protected XLSB documents."),
    convert_metadata: bool | None = Field(None, alias="ConvertMetadata", description="Preserves document metadata such as Title, Author, and Keywords in the PDF output."),
    auto_column_fit: bool | None = Field(None, alias="AutoColumnFit", description="Automatically adjusts column widths to minimize unnecessary empty space in tables."),
    header_on_each_page: bool | None = Field(None, alias="HeaderOnEachPage", description="Repeats the header row on every page when spreadsheet content spans multiple pages. Uses the table header if detected, otherwise treats the first data row as the header."),
    thousands_separator: str | None = Field(None, alias="ThousandsSeparator", description="Character used to separate thousands in numeric values."),
    decimal_separator: str | None = Field(None, alias="DecimalSeparator", description="Character used to separate decimal places in numeric values."),
    date_format: Literal["us", "iso", "eu", "german", "japanese"] | None = Field(None, alias="DateFormat", description="Sets the date format for the output document, overriding the default US locale to ensure consistency across regional Excel settings."),
    pdfa: bool | None = Field(None, alias="Pdfa", description="Creates a PDF/A-1b compliant document for long-term archival and preservation."),
) -> dict[str, Any] | ToolResult:
    """Converts Excel Binary Workbook (XLSB) files to PDF format with support for metadata preservation, formatting options, and PDF/A compliance. Handles protected documents and provides flexible control over layout, number formatting, and date localization."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertXlsbToPdfRequest(
            body=_models.PostConvertXlsbToPdfRequestBody(file_=file_, file_name=file_name, password=password, convert_metadata=convert_metadata, auto_column_fit=auto_column_fit, header_on_each_page=header_on_each_page, thousands_separator=thousands_separator, decimal_separator=decimal_separator, date_format=date_format, pdfa=pdfa)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_xlsb_to_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/xlsb/to/pdf"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_xlsb_to_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_xlsb_to_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_xlsb_to_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_spreadsheet_to_csv(
    file_: str | None = Field(None, alias="File", description="The Excel file to convert. Accepts either a URL reference or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Custom name for the output CSV file. The system automatically sanitizes the filename, appends the correct extension, and adds numeric indexing (e.g., report_0.csv, report_1.csv) if multiple files are generated from a single input."),
    password: str | None = Field(None, alias="Password", description="Password required to open the Excel file if it is password-protected."),
) -> dict[str, Any] | ToolResult:
    """Converts an Excel spreadsheet (XLSX) file to CSV format. Supports password-protected documents and customizable output file naming."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertXlsxToCsvRequest(
            body=_models.PostConvertXlsxToCsvRequestBody(file_=file_, file_name=file_name, password=password)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_spreadsheet_to_csv: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/xlsx/to/csv"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_spreadsheet_to_csv")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_spreadsheet_to_csv", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_spreadsheet_to_csv",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_spreadsheet_to_image_xlsx(
    file_: str | None = Field(None, alias="File", description="The Excel file to convert. Accepts either a file URL or raw file content in binary format."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output JPG file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.jpg, output_1.jpg) for multiple files."),
    password: str | None = Field(None, alias="Password", description="Password required to open password-protected Excel documents."),
    jpg_type: Literal["jpeg", "jpegcmyk", "jpeggray"] | None = Field(None, alias="JpgType", description="The JPG color format to use for the output image."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Whether to maintain the original aspect ratio when scaling the output image."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Whether to apply scaling only when the input image dimensions exceed the output dimensions."),
) -> dict[str, Any] | ToolResult:
    """Converts an Excel spreadsheet file to JPG image format. Supports password-protected documents and provides options for image type, scaling, and proportional resizing."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertXlsxToJpgRequest(
            body=_models.PostConvertXlsxToJpgRequestBody(file_=file_, file_name=file_name, password=password, jpg_type=jpg_type, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_spreadsheet_to_image_xlsx: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/xlsx/to/jpg"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_spreadsheet_to_image_xlsx")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_spreadsheet_to_image_xlsx", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_spreadsheet_to_image_xlsx",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_spreadsheet_to_pdf(
    file_: str | None = Field(None, alias="File", description="The Excel file to convert. Accepts either a URL reference or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Name for the generated PDF output file. The system automatically sanitizes the filename, appends the correct extension, and adds numeric suffixes (e.g., report_0.pdf, report_1.pdf) when multiple files are produced from a single input."),
    password: str | None = Field(None, alias="Password", description="Password required to open password-protected Excel documents."),
    convert_metadata: bool | None = Field(None, alias="ConvertMetadata", description="Preserves document metadata such as title, author, and keywords in the PDF output."),
    auto_column_fit: bool | None = Field(None, alias="AutoColumnFit", description="Automatically adjusts column widths to minimize unnecessary whitespace in tables."),
    header_on_each_page: bool | None = Field(None, alias="HeaderOnEachPage", description="Repeats the header row on every page when spreadsheet content spans multiple pages. Uses the detected table header row, or the first data row if no table is present."),
    thousands_separator: str | None = Field(None, alias="ThousandsSeparator", description="Character used to separate thousands in numeric values (e.g., comma for 1,000 or period for 1.000)."),
    decimal_separator: str | None = Field(None, alias="DecimalSeparator", description="Character used to separate decimal places in numeric values (e.g., period for 1.5 or comma for 1,5)."),
    date_format: Literal["us", "iso", "eu", "german", "japanese"] | None = Field(None, alias="DateFormat", description="Date format standard for the output PDF. Overrides the default US locale format to ensure consistent date representation regardless of regional Excel settings."),
    pdfa: bool | None = Field(None, alias="Pdfa", description="Generates a PDF/A-1b compliant document for long-term archival and preservation purposes."),
) -> dict[str, Any] | ToolResult:
    """Converts Excel spreadsheets (XLSX format) to PDF documents with support for formatting options, metadata preservation, and PDF/A compliance. Handles protected documents, customizable number/date formatting, and multi-page layout control."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertXlsxToPdfRequest(
            body=_models.PostConvertXlsxToPdfRequestBody(file_=file_, file_name=file_name, password=password, convert_metadata=convert_metadata, auto_column_fit=auto_column_fit, header_on_each_page=header_on_each_page, thousands_separator=thousands_separator, decimal_separator=decimal_separator, date_format=date_format, pdfa=pdfa)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_spreadsheet_to_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/xlsx/to/pdf"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_spreadsheet_to_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_spreadsheet_to_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_spreadsheet_to_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_spreadsheet_to_image_png(
    file_: str | None = Field(None, alias="File", description="The Excel file to convert. Accepts either a URL pointing to the file or raw file content in binary format."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output PNG file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.png, output_1.png) for multiple output files."),
    password: str | None = Field(None, alias="Password", description="Password required to open the Excel file if it is password-protected."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintains the original aspect ratio when scaling the output image to fit the target dimensions."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Applies scaling only when the input image dimensions exceed the target output dimensions, preventing upscaling of smaller images."),
) -> dict[str, Any] | ToolResult:
    """Converts an Excel spreadsheet file to PNG image format. Supports URL or file content input with optional scaling and password protection for secured documents."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertXlsxToPngRequest(
            body=_models.PostConvertXlsxToPngRequestBody(file_=file_, file_name=file_name, password=password, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_spreadsheet_to_image_png: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/xlsx/to/png"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_spreadsheet_to_image_png")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_spreadsheet_to_image_png", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_spreadsheet_to_image_png",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def encrypt_xlsx_workbook(
    file_: str | None = Field(None, alias="File", description="The Excel file to encrypt. Accepts either a file URL or raw file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output encrypted file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., `report_0.xlsx`, `report_1.xlsx`) if multiple files are generated."),
    encrypt_password: str | None = Field(None, alias="EncryptPassword", description="The password required to open the encrypted Excel workbook. Users must enter this password to access the file."),
) -> dict[str, Any] | ToolResult:
    """Convert an Excel workbook to a password-protected format. Encrypts the file with a specified password that must be entered to open it."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertXlsxToProtectRequest(
            body=_models.PostConvertXlsxToProtectRequestBody(file_=file_, file_name=file_name, encrypt_password=encrypt_password)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for encrypt_xlsx_workbook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/xlsx/to/protect"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("encrypt_xlsx_workbook")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("encrypt_xlsx_workbook", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="encrypt_xlsx_workbook",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_spreadsheet_to_tiff(
    file_: str | None = Field(None, alias="File", description="The Excel file to convert. Accepts either a file URL or raw file content in binary format."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output TIFF file(s). The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.tiff, output_1.tiff) for multi-page conversions to ensure unique, safe file naming."),
    password: str | None = Field(None, alias="Password", description="Password required to open the Excel file if it is password-protected."),
    tiff_type: Literal["color24nc", "color32nc", "color24lzw", "color32lzw", "color24zip", "color32zip", "grayscale", "grayscalelzw", "grayscalezip", "monochromeg3", "monochromeg32d", "monochromeg4", "monochromelzw", "monochromepackbits"] | None = Field(None, alias="TiffType", description="Specifies the TIFF compression type and color depth. Choose from color variants (24-bit or 32-bit with no compression, LZW, or ZIP), grayscale options, or monochrome formats with various compression algorithms."),
    multi_page: bool | None = Field(None, alias="MultiPage", description="When enabled, combines all spreadsheet pages into a single multi-page TIFF file. When disabled, each page is saved as a separate TIFF file."),
    fill_order: Literal["0", "1"] | None = Field(None, alias="FillOrder", description="Defines the bit order within each byte: use 0 for most significant bit first (standard), or 1 for least significant bit first."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="When enabled, maintains the original aspect ratio when scaling the output image to fit specified dimensions."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="When enabled, scaling is applied only if the input image dimensions exceed the target output dimensions. Smaller images are not enlarged."),
) -> dict[str, Any] | ToolResult:
    """Converts Excel spreadsheet files to TIFF image format with configurable compression, color depth, and multi-page support. Supports password-protected documents and optional image scaling."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertXlsxToTiffRequest(
            body=_models.PostConvertXlsxToTiffRequestBody(file_=file_, file_name=file_name, password=password, tiff_type=tiff_type, multi_page=multi_page, fill_order=fill_order, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_spreadsheet_to_tiff: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/xlsx/to/tiff"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_spreadsheet_to_tiff")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_spreadsheet_to_tiff", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_spreadsheet_to_tiff",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_spreadsheet_to_image_webp(
    file_: str | None = Field(None, alias="File", description="The Excel file to convert. Accepts either a URL or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="Custom name for the output file. The system automatically sanitizes the filename, appends the .webp extension, and adds numeric indexing (e.g., output_0.webp, output_1.webp) if multiple files are generated."),
    password: str | None = Field(None, alias="Password", description="Password required to open password-protected Excel documents."),
    scale_proportions: bool | None = Field(None, alias="ScaleProportions", description="Maintains the original aspect ratio when scaling the output image to fit the target dimensions."),
    scale_if_larger: bool | None = Field(None, alias="ScaleIfLarger", description="Applies scaling only when the input image dimensions exceed the output dimensions, preserving quality for smaller images."),
) -> dict[str, Any] | ToolResult:
    """Converts an Excel spreadsheet file to WebP image format. Supports password-protected documents and configurable image scaling options."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertXlsxToWebpRequest(
            body=_models.PostConvertXlsxToWebpRequestBody(file_=file_, file_name=file_name, password=password, scale_proportions=scale_proportions, scale_if_larger=scale_if_larger)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_spreadsheet_to_image_webp: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/xlsx/to/webp"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_spreadsheet_to_image_webp")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_spreadsheet_to_image_webp", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_spreadsheet_to_image_webp",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_spreadsheet_format_modern(
    file_: str | None = Field(None, alias="File", description="The spreadsheet file to convert. Accepts either a URL pointing to the file or the raw file content as binary data."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output file. The system automatically sanitizes the filename, appends the correct extension, and adds numeric indexing (e.g., filename_0, filename_1) when multiple files are generated from a single input."),
    password: str | None = Field(None, alias="Password", description="The password required to open password-protected spreadsheets. Only needed if the input file is encrypted."),
) -> dict[str, Any] | ToolResult:
    """Converts an Excel spreadsheet to Excel format, with support for password-protected documents. Useful for standardizing file formats or re-encoding existing spreadsheets."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertXlsxToXlsxRequest(
            body=_models.PostConvertXlsxToXlsxRequestBody(file_=file_, file_name=file_name, password=password)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_spreadsheet_format_modern: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/xlsx/to/xlsx"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_spreadsheet_format_modern")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_spreadsheet_format_modern", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_spreadsheet_format_modern",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_spreadsheet_template_to_pdf(
    file_: str | None = Field(None, alias="File", description="The spreadsheet file to convert. Accepts either a URL reference or binary file content."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the generated PDF output file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., report_0.pdf, report_1.pdf) when multiple files are produced from a single input."),
    password: str | None = Field(None, alias="Password", description="Password required to open password-protected spreadsheet documents."),
    convert_metadata: bool | None = Field(None, alias="ConvertMetadata", description="Preserves document metadata such as title, author, and keywords in the PDF output."),
    auto_column_fit: bool | None = Field(None, alias="AutoColumnFit", description="Automatically adjusts column widths to minimize unnecessary whitespace in tables."),
    header_on_each_page: bool | None = Field(None, alias="HeaderOnEachPage", description="Repeats the header row on every page when spreadsheet content spans multiple pages. Uses the table header if detected, otherwise treats the first data row as the header."),
    thousands_separator: str | None = Field(None, alias="ThousandsSeparator", description="Character used to separate thousands in numeric values."),
    decimal_separator: str | None = Field(None, alias="DecimalSeparator", description="Character used to separate decimal places in numeric values."),
    date_format: Literal["us", "iso", "eu", "german", "japanese"] | None = Field(None, alias="DateFormat", description="Date format standard for the output document, overriding the default US locale format to ensure consistency across regional Excel settings."),
    pdfa: bool | None = Field(None, alias="Pdfa", description="Generates a PDF/A-1b compliant document for long-term archival and preservation."),
) -> dict[str, Any] | ToolResult:
    """Converts Excel spreadsheet files (XLTX format) to PDF documents with customizable formatting, metadata handling, and locale-specific number/date formatting options."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertXltxToPdfRequest(
            body=_models.PostConvertXltxToPdfRequestBody(file_=file_, file_name=file_name, password=password, convert_metadata=convert_metadata, auto_column_fit=auto_column_fit, header_on_each_page=header_on_each_page, thousands_separator=thousands_separator, decimal_separator=decimal_separator, date_format=date_format, pdfa=pdfa)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_spreadsheet_template_to_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/xltx/to/pdf"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_spreadsheet_template_to_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_spreadsheet_template_to_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_spreadsheet_template_to_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def convert_xml_to_docx(
    file_: str | None = Field(None, alias="File", description="The XML file to convert. Accepts either a URL or raw file content in binary format."),
    file_name: str | None = Field(None, alias="FileName", description="The name for the output DOCX file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.docx, filename_1.docx) for multiple output files."),
    password: str | None = Field(None, alias="Password", description="Password required to open the input XML file if it is password-protected."),
    update_toc: bool | None = Field(None, alias="UpdateToc", description="Automatically updates all tables of content in the converted document."),
    update_references: bool | None = Field(None, alias="UpdateReferences", description="Automatically updates all reference fields in the converted document."),
) -> dict[str, Any] | ToolResult:
    """Converts XML documents to DOCX format with optional support for password-protected files and automatic updates to tables of content and reference fields."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertXmlToDocxRequest(
            body=_models.PostConvertXmlToDocxRequestBody(file_=file_, file_name=file_name, password=password, update_toc=update_toc, update_references=update_references)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_xml_to_docx: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/xml/to/docx"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_xml_to_docx")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_xml_to_docx", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_xml_to_docx",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversion
@mcp.tool()
async def extract_archive(
    file_: str | None = Field(None, alias="File", description="The ZIP archive file to extract. Can be provided as a URL or raw file content in binary format."),
    password: str | None = Field(None, alias="Password", description="Password for opening password-protected ZIP archives. Required only if the archive is encrypted."),
) -> dict[str, Any] | ToolResult:
    """Extracts contents from a ZIP archive file. Supports password-protected archives by providing the required password."""

    # Construct request model with validation
    try:
        _request = _models.PostConvertZipToExtractRequest(
            body=_models.PostConvertZipToExtractRequestBody(file_=file_, password=password)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for extract_archive: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/convert/zip/to/extract"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("extract_archive")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("extract_archive", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="extract_archive",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["File"],
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
        print("  python convert_api_server.py", file=sys.stderr)
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

    parser = argparse.ArgumentParser(description="ConvertAPI MCP Server")

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
    logger.info("Starting ConvertAPI MCP Server")
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

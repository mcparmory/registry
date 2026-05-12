#!/usr/bin/env python3
"""
Shortcut MCP Server
Generated: 2026-05-12 12:53:26 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

import argparse
import asyncio
import base64
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
from typing import Annotated, Any, Literal, cast, overload

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
from mcp.types import ToolAnnotations
from pydantic import AfterValidator, Field

BASE_URL = os.getenv("BASE_URL", "https://api.app.shortcut.com")
SERVER_NAME = "Shortcut"
SERVER_VERSION = "1.0.2"

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


def _decode_base64_upload_content(value: str | bytes | bytearray, field_name: str) -> bytes:
    """Decode base64 upload content, tolerating direct bytes for compatibility."""
    if isinstance(value, bytearray):
        return bytes(value)
    if isinstance(value, bytes):
        return value
    if not isinstance(value, str):
        raise ValueError(
            f"Unsupported file input for '{field_name}': expected base64 string or bytes, "
            f"got {type(value).__name__}"
        )

    try:
        standard_b64 = value.replace("-", "+").replace("_", "/")
        padding = len(standard_b64) % 4
        if padding:
            standard_b64 += "=" * (4 - padding)
        return base64.b64decode(standard_b64, validate=True)
    except Exception as exc:
        raise ValueError(f"Invalid base64 file content for '{field_name}'") from exc


async def _make_request(
    method: str,
    path: str,
    params: dict[str, Any] | None = None,
    body: Any = None,
    body_content_type: str | None = None,
    multipart_file_fields: list[str] | None = None,
    multipart_file_content_types: dict[str, str] | None = None,
    whole_body_base64: bool = False,
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
                _file_content_types = multipart_file_content_types or {}
                if isinstance(body, dict):
                    for _key, _value in body.items():
                        if _value is None:
                            continue
                        if _key in _file_fields:
                            _file_values = _value if isinstance(_value, (list, tuple)) else [_value]
                            for _file_item in _file_values:
                                if _file_item is None:
                                    continue
                                _file_content = _decode_base64_upload_content(_file_item, _key)
                                _multipart_parts.append(
                                    (
                                        _key,
                                        (
                                            f"{_key}.bin",
                                            _file_content,
                                            _file_content_types.get(_key, "application/octet-stream"),
                                        ),
                                    )
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
                    _field_name = next(iter(_file_fields), "file")
                    _file_content = _decode_base64_upload_content(body, _field_name)
                    _field_name = next(iter(_file_fields), "file")
                    _multipart_parts.append(
                        (
                            _field_name,
                            (
                                f"{_field_name}.bin",
                                _file_content,
                                _file_content_types.get(_field_name, "application/octet-stream"),
                            ),
                        )
                    )
                _files = _multipart_parts
            _content: bytes | str | None = None
            if body_content_type is not None and body_content_type not in ("application/json", "application/x-www-form-urlencoded", "multipart/form-data"):
                _raw = body
                if whole_body_base64 and _raw is not None:
                    if not isinstance(_raw, (str, bytes, bytearray)):
                        raise ValueError(
                            f"Unsupported file input for 'body': expected base64 string or bytes, got {type(_raw).__name__}"
                        )
                    _content = _decode_base64_upload_content(_raw, "body")
                elif isinstance(_raw, (dict, list)):
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

def _check_unique_items(v: list) -> list:
    """Validate that array items are unique (OAS uniqueItems: true)."""
    seen = []
    for item in v:
        if item in seen:
            raise ValueError("array items must be unique")
        seen.append(item)
    return v

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
    multipart_file_content_types: dict[str, str] | None = None,
    whole_body_base64: bool = False,
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
                multipart_file_content_types=multipart_file_content_types,
                whole_body_base64=whole_body_base64,
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
    'api_token',
]

# Initialize authentication handlers at server startup
_auth_handlers: dict[str, Any] = {}
try:
    _auth_handlers["api_token"] = _auth.APIKeyAuth(env_var="API_KEY", location="header", param_name="Shortcut-Token")
    logging.info("Authentication configured: api_token")
except ValueError as e:
    # Extract credential names from error message (first sentence before "Leave empty")
    error_msg = str(e).split("Leave empty")[0].strip()
    logging.warning(f"Credentials for api_token not configured: {error_msg}")
    _auth_handlers["api_token"] = None

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

mcp = FastMCP("Shortcut", middleware=[_JsonCoercionMiddleware()])


@mcp.tool(
    title="List Categories",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_categories() -> dict[str, Any] | ToolResult:
    """Retrieve a complete list of all available categories with their attributes. Use this to discover category options for filtering, organizing, or referencing in other operations."""

    # Extract parameters for API call
    _http_path = "/api/v3/categories"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_categories")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_categories", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_categories",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Create Category",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_category(
    name: str = Field(..., description="The display name for the new Category. Must be between 1 and 128 characters.", min_length=1, max_length=128),
    external_id: str | None = Field(None, description="An optional external identifier for this Category, useful when importing from another tool. Must be between 1 and 128 characters if provided.", min_length=1, max_length=128),
    type_: Any | None = Field(None, alias="type", description="The entity type this Category is associated with. Currently supports Milestone or Objective types."),
) -> dict[str, Any] | ToolResult:
    """Create a new Category in Shortcut for organizing Milestones or Objectives. Categories help structure and group related work items by type."""

    # Construct request model with validation
    try:
        _request = _models.CreateCategoryRequest(
            body=_models.CreateCategoryRequestBody(name=name, external_id=external_id, type_=type_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_category: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v3/categories"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_category")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_category", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_category",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Get Category",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_category(category_public_id: str = Field(..., alias="category-public-id", description="The unique identifier for the category as a 64-bit integer.")) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific category using its unique identifier. Returns the category's properties and metadata."""

    _category_public_id = _parse_int(category_public_id)

    # Construct request model with validation
    try:
        _request = _models.GetCategoryRequest(
            path=_models.GetCategoryRequestPath(category_public_id=_category_public_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_category: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/categories/{category-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/categories/{category-public-id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_category")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_category", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_category",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Update Category",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def update_category(
    category_public_id: str = Field(..., alias="category-public-id", description="The unique identifier of the Category to update. Must be a valid 64-bit integer."),
    name: str | None = Field(None, description="The new name for the Category. Must be at least 1 character long and unique across all Categories.", min_length=1),
    archived: bool | None = Field(None, description="Whether the Category should be archived. Set to true to archive or false to unarchive."),
) -> dict[str, Any] | ToolResult:
    """Update a Category's name and/or archived status. Category names must be unique; attempting to use a name that already exists will result in an error."""

    _category_public_id = _parse_int(category_public_id)

    # Construct request model with validation
    try:
        _request = _models.UpdateCategoryRequest(
            path=_models.UpdateCategoryRequestPath(category_public_id=_category_public_id),
            body=_models.UpdateCategoryRequestBody(name=name, archived=archived)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_category: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/categories/{category-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/categories/{category-public-id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_category")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_category", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_category",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Delete Category",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_category(category_public_id: str = Field(..., alias="category-public-id", description="The unique identifier of the category to delete, provided as a 64-bit integer.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a category by its unique identifier. This operation removes the category and cannot be undone."""

    _category_public_id = _parse_int(category_public_id)

    # Construct request model with validation
    try:
        _request = _models.DeleteCategoryRequest(
            path=_models.DeleteCategoryRequestPath(category_public_id=_category_public_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_category: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/categories/{category-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/categories/{category-public-id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_category")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_category", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_category",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="List Milestones for Category",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_milestones_for_category(category_public_id: str = Field(..., alias="category-public-id", description="The unique identifier of the category. Must be a valid 64-bit integer.")) -> dict[str, Any] | ToolResult:
    """Retrieve all milestones associated with a specific category. Returns a complete list of milestones within the given category."""

    _category_public_id = _parse_int(category_public_id)

    # Construct request model with validation
    try:
        _request = _models.ListCategoryMilestonesRequest(
            path=_models.ListCategoryMilestonesRequestPath(category_public_id=_category_public_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_milestones_for_category: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/categories/{category-public-id}/milestones", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/categories/{category-public-id}/milestones"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_milestones_for_category")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_milestones_for_category", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_milestones_for_category",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="List Objectives for Category",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_objectives_for_category(category_public_id: str = Field(..., alias="category-public-id", description="The unique identifier of the Category. Must be a valid 64-bit integer.")) -> dict[str, Any] | ToolResult:
    """Retrieves all Objectives associated with a specific Category. Use this to view the complete list of objectives within a category."""

    _category_public_id = _parse_int(category_public_id)

    # Construct request model with validation
    try:
        _request = _models.ListCategoryObjectivesRequest(
            path=_models.ListCategoryObjectivesRequestPath(category_public_id=_category_public_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_objectives_for_category: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/categories/{category-public-id}/objectives", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/categories/{category-public-id}/objectives"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_objectives_for_category")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_objectives_for_category", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_objectives_for_category",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="List Custom Fields",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_custom_fields() -> dict[str, Any] | ToolResult:
    """Retrieve all custom fields available in the system. This returns the complete list of custom field definitions that can be used across resources."""

    # Extract parameters for API call
    _http_path = "/api/v3/custom-fields"
    _http_headers = {}

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


@mcp.tool(
    title="Get Custom Field",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_custom_field(custom_field_public_id: str = Field(..., alias="custom-field-public-id", description="The unique identifier of the custom field to retrieve, formatted as a UUID.")) -> dict[str, Any] | ToolResult:
    """Retrieve a specific custom field by its unique identifier. Returns the complete configuration and metadata for the custom field."""

    # Construct request model with validation
    try:
        _request = _models.GetCustomFieldRequest(
            path=_models.GetCustomFieldRequestPath(custom_field_public_id=custom_field_public_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_custom_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/custom-fields/{custom-field-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/custom-fields/{custom-field-public-id}"
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


@mcp.tool(
    title="Update Custom Field",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_custom_field(
    custom_field_public_id: str = Field(..., alias="custom-field-public-id", description="The unique identifier of the custom field to update, formatted as a UUID."),
    enabled: bool | None = Field(None, description="Whether this field is enabled for use in the workspace. Only enabled fields can be applied to stories."),
    name: str | None = Field(None, description="The display name of the custom field. Must be between 1 and 63 characters.", min_length=1, max_length=63),
    values: list[_models.UpdateCustomFieldEnumValue] | None = Field(None, description="An ordered collection of enum values defining the field's domain. The order in this collection determines the sort order of values. Omit existing values to delete them; include new values as objects with a 'value' property and optional 'color_key' to create them inline."),
    icon_set_identifier: str | None = Field(None, description="A frontend-controlled identifier for the icon associated with this custom field. Must be between 1 and 63 characters.", min_length=1, max_length=63),
    description: str | None = Field(None, description="A description explaining the purpose and use of this custom field."),
) -> dict[str, Any] | ToolResult:
    """Update the definition of a custom field, including its name, description, enabled status, enum values, and icon. Enum values are ordered by their position in the collection; omit values to delete them, or include new values with only a 'value' property to create them inline."""

    # Construct request model with validation
    try:
        _request = _models.UpdateCustomFieldRequest(
            path=_models.UpdateCustomFieldRequestPath(custom_field_public_id=custom_field_public_id),
            body=_models.UpdateCustomFieldRequestBody(enabled=enabled, name=name, values=values, icon_set_identifier=icon_set_identifier, description=description)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_custom_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/custom-fields/{custom-field-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/custom-fields/{custom-field-public-id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_custom_field")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_custom_field", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_custom_field",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Delete Custom Field",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_custom_field(custom_field_public_id: str = Field(..., alias="custom-field-public-id", description="The unique UUID identifier of the custom field to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a custom field by its unique identifier. This operation removes the custom field and all associated data."""

    # Construct request model with validation
    try:
        _request = _models.DeleteCustomFieldRequest(
            path=_models.DeleteCustomFieldRequestPath(custom_field_public_id=custom_field_public_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_custom_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/custom-fields/{custom-field-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/custom-fields/{custom-field-public-id}"
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


@mcp.tool(
    title="List Documents",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_documents() -> dict[str, Any] | ToolResult:
    """Retrieve a list of all documents that the current user has read access to. Returns documents accessible based on the user's permissions."""

    # Extract parameters for API call
    _http_path = "/api/v3/documents"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_documents")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_documents", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_documents",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Create Document",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_document(
    title: str = Field(..., description="The document title. Must be between 1 and 256 characters long.", min_length=1, max_length=256),
    content: str = Field(..., description="The document content. Can be formatted as markdown or HTML depending on the content_format parameter."),
) -> dict[str, Any] | ToolResult:
    """Creates a new document with the specified title and content. Supports both markdown and HTML content formats via the content_format parameter."""

    # Construct request model with validation
    try:
        _request = _models.CreateDocRequest(
            body=_models.CreateDocRequestBody(title=title, content=content)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_document: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v3/documents"
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
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Get Document",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_doc(doc_public_id: str = Field(..., alias="doc-public-id", description="The unique identifier of the Doc to retrieve, formatted as a UUID.")) -> dict[str, Any] | ToolResult:
    """Retrieve a Doc by its public ID, including its full content. Optionally request HTML-formatted content using the content_format query parameter."""

    # Construct request model with validation
    try:
        _request = _models.GetDocRequest(
            path=_models.GetDocRequestPath(doc_public_id=doc_public_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_doc: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/documents/{doc-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/documents/{doc-public-id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_doc")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_doc", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_doc",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Update Document",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_document(
    doc_public_id: str = Field(..., alias="doc-public-id", description="The unique public identifier for the document being updated, formatted as a UUID."),
    title: str | None = Field(None, description="The new title for the document. Must be between 1 and 256 characters long.", min_length=1, max_length=256),
    content: str | None = Field(None, description="The new content for the document. Supports markdown or HTML format as specified by the content_format parameter."),
) -> dict[str, Any] | ToolResult:
    """Update a document's title and/or content. Supports markdown or HTML input. Connected users receive real-time SSE notifications to refresh their view, while disconnected sessions trigger cache invalidation to ensure fresh content."""

    # Construct request model with validation
    try:
        _request = _models.UpdateDocRequest(
            path=_models.UpdateDocRequestPath(doc_public_id=doc_public_id),
            body=_models.UpdateDocRequestBody(title=title, content=content)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_document: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/documents/{doc-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/documents/{doc-public-id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_document")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_document", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_document",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Delete Document",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_doc(doc_public_id: str = Field(..., alias="doc-public-id", description="The unique public identifier of the Doc to delete, formatted as a UUID.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes a Doc and all its associated data. Requires admin access to the document. Connected clients will be notified of the deletion via SSE events."""

    # Construct request model with validation
    try:
        _request = _models.DeleteDocRequest(
            path=_models.DeleteDocRequestPath(doc_public_id=doc_public_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_doc: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/documents/{doc-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/documents/{doc-public-id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_doc")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_doc", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_doc",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="List Document Epics",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_document_epics(doc_public_id: str = Field(..., alias="doc-public-id", description="The unique public identifier of the Document, provided as a UUID.")) -> dict[str, Any] | ToolResult:
    """Retrieve all Epics associated with a specific Document. Returns a collection of Epics linked to the Document identified by its public ID."""

    # Construct request model with validation
    try:
        _request = _models.ListDocumentEpicsRequest(
            path=_models.ListDocumentEpicsRequestPath(doc_public_id=doc_public_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_document_epics: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/documents/{doc-public-id}/epics", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/documents/{doc-public-id}/epics"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_document_epics")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_document_epics", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_document_epics",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Link Document to Epic",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def link_document_to_epic(
    doc_public_id: str = Field(..., alias="doc-public-id", description="The unique identifier of the Document to link, provided as a UUID."),
    epic_public_id: str = Field(..., alias="epic-public-id", description="The unique identifier of the Epic to link the document to, provided as a 64-bit integer."),
) -> dict[str, Any] | ToolResult:
    """Create a relationship between a Document and an Epic, associating the document with the specified epic for organizational and tracking purposes."""

    _epic_public_id = _parse_int(epic_public_id)

    # Construct request model with validation
    try:
        _request = _models.LinkDocumentToEpicRequest(
            path=_models.LinkDocumentToEpicRequestPath(doc_public_id=doc_public_id, epic_public_id=_epic_public_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for link_document_to_epic: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/documents/{doc-public-id}/epics/{epic-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/documents/{doc-public-id}/epics/{epic-public-id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("link_document_to_epic")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("link_document_to_epic", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="link_document_to_epic",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Remove Document from Epic",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def remove_document_from_epic(
    doc_public_id: str = Field(..., alias="doc-public-id", description="The unique identifier of the Document to unlink, formatted as a UUID."),
    epic_public_id: str = Field(..., alias="epic-public-id", description="The unique identifier of the Epic to unlink, formatted as a 64-bit integer."),
) -> dict[str, Any] | ToolResult:
    """Remove the relationship between a Document and an Epic, unlinking them from each other."""

    _epic_public_id = _parse_int(epic_public_id)

    # Construct request model with validation
    try:
        _request = _models.UnlinkDocumentFromEpicRequest(
            path=_models.UnlinkDocumentFromEpicRequestPath(doc_public_id=doc_public_id, epic_public_id=_epic_public_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_document_from_epic: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/documents/{doc-public-id}/epics/{epic-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/documents/{doc-public-id}/epics/{epic-public-id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_document_from_epic")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_document_from_epic", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_document_from_epic",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="List Entity Templates",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_entity_templates() -> dict[str, Any] | ToolResult:
    """Retrieve all entity templates available in the Workspace. Entity templates define the structure and configuration for entities within your workspace."""

    # Extract parameters for API call
    _http_path = "/api/v3/entity-templates"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_entity_templates")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_entity_templates", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_entity_templates",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Get Entity Template",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_entity_template(entity_template_public_id: str = Field(..., alias="entity-template-public-id", description="The unique identifier of the entity template, formatted as a UUID.")) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific entity template using its unique identifier. This operation returns the complete configuration and metadata for the requested entity template."""

    # Construct request model with validation
    try:
        _request = _models.GetEntityTemplateRequest(
            path=_models.GetEntityTemplateRequestPath(entity_template_public_id=entity_template_public_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_entity_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/entity-templates/{entity-template-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/entity-templates/{entity-template-public-id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_entity_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_entity_template", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_entity_template",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="List Epics",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_epics(includes_description: bool | None = Field(None, description="Set to true to include the full description text for each Epic in the response; omit or set to false to return only basic Epic metadata.")) -> dict[str, Any] | ToolResult:
    """Retrieve a list of all Epics with their core attributes. Optionally include full descriptions for each Epic."""

    # Construct request model with validation
    try:
        _request = _models.ListEpicsRequest(
            query=_models.ListEpicsRequestQuery(includes_description=includes_description)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_epics: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v3/epics"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_epics")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_epics", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_epics",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Create Epic",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_epic(
    name: str = Field(..., description="The Epic's title or name. Required field, must be between 1 and 256 characters.", min_length=1, max_length=256),
    description: str | None = Field(None, description="A detailed explanation of the Epic's purpose and scope. Limited to 100,000 characters.", max_length=100000),
    objective_ids: list[Annotated[int, Field(json_schema_extra={'format': 'int64'})]] | None = Field(None, description="An array of Objective IDs to associate with this Epic. Objectives provide strategic alignment for the Epic."),
    planned_start_date: str | None = Field(None, description="The date when work on this Epic is planned to begin. Specify as an ISO 8601 formatted date-time string."),
    requested_by_id: str | None = Field(None, description="The UUID of the team member who requested this Epic. Used to track Epic ownership and accountability."),
    epic_state_id: str | None = Field(None, description="The numeric ID of the Epic State that defines the Epic's workflow status (e.g., Backlog, In Progress, Done)."),
    group_ids: list[Annotated[str, Field(json_schema_extra={'format': 'uuid'})]] | None = Field(None, description="An array of Group UUIDs to associate with this Epic. Groups help organize and categorize Epics within your workspace."),
    converted_from_story_id: str | None = Field(None, description="The numeric ID of a Story that was converted into this Epic. Use this when promoting an existing Story to Epic status."),
    external_id: str | None = Field(None, description="An external identifier for this Epic, useful when importing from other tools or systems. Limited to 128 characters and should be unique within your workspace.", max_length=128),
    deadline: str | None = Field(None, description="The date by which this Epic must be completed. Specify as an ISO 8601 formatted date-time string."),
) -> dict[str, Any] | ToolResult:
    """Create a new Epic in Shortcut. An Epic is a large body of work that can be broken down into Stories and related to Objectives and Groups."""

    _epic_state_id = _parse_int(epic_state_id)
    _converted_from_story_id = _parse_int(converted_from_story_id)

    # Construct request model with validation
    try:
        _request = _models.CreateEpicRequest(
            body=_models.CreateEpicRequestBody(description=description, objective_ids=objective_ids, name=name, planned_start_date=planned_start_date, requested_by_id=requested_by_id, epic_state_id=_epic_state_id, group_ids=group_ids, converted_from_story_id=_converted_from_story_id, external_id=external_id, deadline=deadline)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_epic: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v3/epics"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_epic")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_epic", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_epic",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="List Epics Paginated",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_epics_paginated(
    includes_description: bool | None = Field(None, description="Include the full description text for each Epic in the response. When false or omitted, descriptions are excluded from the results."),
    page: str | None = Field(None, description="The page number to retrieve, starting from 1. Defaults to the first page if not specified."),
    page_size: str | None = Field(None, description="The number of Epics to return per page, between 1 and 250 items. Defaults to 10 if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of Epics with optional descriptions. Use pagination parameters to control which results are returned and how many per page."""

    _page = _parse_int(page)
    _page_size = _parse_int(page_size)

    # Construct request model with validation
    try:
        _request = _models.ListEpicsPaginatedRequest(
            query=_models.ListEpicsPaginatedRequestQuery(includes_description=includes_description, page=_page, page_size=_page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_epics_paginated: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v3/epics/paginated"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_epics_paginated")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_epics_paginated", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_epics_paginated",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Get Epic",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_epic(epic_public_id: str = Field(..., alias="epic-public-id", description="The unique identifier of the Epic to retrieve. Must be a valid 64-bit integer.")) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific Epic by its unique identifier. Returns the Epic's properties and metadata."""

    _epic_public_id = _parse_int(epic_public_id)

    # Construct request model with validation
    try:
        _request = _models.GetEpicRequest(
            path=_models.GetEpicRequestPath(epic_public_id=_epic_public_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_epic: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/epics/{epic-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/epics/{epic-public-id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_epic")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_epic", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_epic",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Update Epic",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def update_epic(
    epic_public_id: str = Field(..., alias="epic-public-id", description="The unique identifier of the Epic to update. This is a 64-bit integer value found in the Shortcut UI."),
    description: str | None = Field(None, description="The Epic's description text. Can be up to 100,000 characters long.", max_length=100000),
    archived: bool | None = Field(None, description="Whether the Epic is archived. Set to true to archive or false to unarchive."),
    objective_ids: list[Annotated[int, Field(json_schema_extra={'format': 'int64'})]] | None = Field(None, description="An array of Objective IDs to associate with this Epic. Order is not significant."),
    name: str | None = Field(None, description="The Epic's display name. Must be between 1 and 256 characters long.", min_length=1, max_length=256),
    planned_start_date: str | None = Field(None, description="The Epic's planned start date in ISO 8601 date-time format."),
    requested_by_id: str | None = Field(None, description="The UUID of the team member who requested this Epic."),
    epic_state_id: str | None = Field(None, description="The 64-bit integer ID of the Epic State (e.g., Backlog, In Progress, Done) to assign to this Epic."),
    group_ids: list[Annotated[str, Field(json_schema_extra={'format': 'uuid'})]] | None = Field(None, description="An array of Group UUIDs to associate with this Epic. Order is not significant."),
    external_id: str | None = Field(None, description="An external identifier for this Epic, useful when importing from other tools. Maximum 128 characters.", max_length=128),
    deadline: str | None = Field(None, description="The Epic's deadline in ISO 8601 date-time format."),
) -> dict[str, Any] | ToolResult:
    """Update an Epic's properties including name, description, dates, state, and relationships. Only the Epic ID is required; all other fields are optional and will only be updated if provided."""

    _epic_public_id = _parse_int(epic_public_id)
    _epic_state_id = _parse_int(epic_state_id)

    # Construct request model with validation
    try:
        _request = _models.UpdateEpicRequest(
            path=_models.UpdateEpicRequestPath(epic_public_id=_epic_public_id),
            body=_models.UpdateEpicRequestBody(description=description, archived=archived, objective_ids=objective_ids, name=name, planned_start_date=planned_start_date, requested_by_id=requested_by_id, epic_state_id=_epic_state_id, group_ids=group_ids, external_id=external_id, deadline=deadline)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_epic: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/epics/{epic-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/epics/{epic-public-id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_epic")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_epic", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_epic",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Delete Epic",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_epic(epic_public_id: str = Field(..., alias="epic-public-id", description="The unique identifier of the Epic to delete, specified as a 64-bit integer.")) -> dict[str, Any] | ToolResult:
    """Permanently delete an Epic by its unique identifier. This operation removes the Epic and cannot be undone."""

    _epic_public_id = _parse_int(epic_public_id)

    # Construct request model with validation
    try:
        _request = _models.DeleteEpicRequest(
            path=_models.DeleteEpicRequestPath(epic_public_id=_epic_public_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_epic: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/epics/{epic-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/epics/{epic-public-id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_epic")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_epic", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_epic",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="List Epic Comments",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_epic_comments(epic_public_id: str = Field(..., alias="epic-public-id", description="The unique identifier of the Epic. Must be a valid 64-bit integer.")) -> dict[str, Any] | ToolResult:
    """Retrieve all comments associated with a specific Epic. Returns a list of comment objects ordered by creation date."""

    _epic_public_id = _parse_int(epic_public_id)

    # Construct request model with validation
    try:
        _request = _models.ListEpicCommentsRequest(
            path=_models.ListEpicCommentsRequestPath(epic_public_id=_epic_public_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_epic_comments: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/epics/{epic-public-id}/comments", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/epics/{epic-public-id}/comments"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_epic_comments")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_epic_comments", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_epic_comments",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Create Epic Comment",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_epic_comment(
    epic_public_id: str = Field(..., alias="epic-public-id", description="The unique identifier of the Epic where the comment will be posted."),
    text: str = Field(..., description="The comment text content. Must be between 1 and 100,000 characters.", min_length=1, max_length=100000),
    author_id: str | None = Field(None, description="The UUID of the team member who authored this comment. If not provided, defaults to the user associated with the API token."),
    external_id: str | None = Field(None, description="An optional external identifier for this comment, useful when importing comments from other tools. Maximum length is 128 characters.", max_length=128),
) -> dict[str, Any] | ToolResult:
    """Add a threaded comment to an Epic. The comment can be authored by the API token holder or another team member, and optionally linked to an external system via an external ID."""

    _epic_public_id = _parse_int(epic_public_id)

    # Construct request model with validation
    try:
        _request = _models.CreateEpicCommentRequest(
            path=_models.CreateEpicCommentRequestPath(epic_public_id=_epic_public_id),
            body=_models.CreateEpicCommentRequestBody(text=text, author_id=author_id, external_id=external_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_epic_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/epics/{epic-public-id}/comments", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/epics/{epic-public-id}/comments"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_epic_comment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_epic_comment", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_epic_comment",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Get Epic Comment",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_epic_comment(
    epic_public_id: str = Field(..., alias="epic-public-id", description="The unique identifier of the Epic that contains the comment. Must be a positive integer."),
    comment_public_id: str = Field(..., alias="comment-public-id", description="The unique identifier of the specific comment to retrieve. Must be a positive integer."),
) -> dict[str, Any] | ToolResult:
    """Retrieves detailed information about a specific comment on an Epic. Use this to fetch comment content, metadata, and other details by providing both the Epic ID and the Comment ID."""

    _epic_public_id = _parse_int(epic_public_id)
    _comment_public_id = _parse_int(comment_public_id)

    # Construct request model with validation
    try:
        _request = _models.GetEpicCommentRequest(
            path=_models.GetEpicCommentRequestPath(epic_public_id=_epic_public_id, comment_public_id=_comment_public_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_epic_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/epics/{epic-public-id}/comments/{comment-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/epics/{epic-public-id}/comments/{comment-public-id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_epic_comment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_epic_comment", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_epic_comment",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Create Reply to Epic Comment",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_reply_to_epic_comment(
    epic_public_id: str = Field(..., alias="epic-public-id", description="The unique identifier of the Epic containing the parent comment. Must be a positive integer."),
    comment_public_id: str = Field(..., alias="comment-public-id", description="The unique identifier of the parent Epic Comment to which you are replying. Must be a positive integer."),
    text: str = Field(..., description="The text content of the reply. Must be between 1 and 100,000 characters.", min_length=1, max_length=100000),
    author_id: str | None = Field(None, description="The UUID of the team member who authored this reply. If not provided, defaults to the user associated with the API token making the request."),
    external_id: str | None = Field(None, description="An optional external identifier for this comment, useful when importing comments from other tools. Maximum length is 128 characters.", max_length=128),
) -> dict[str, Any] | ToolResult:
    """Create a nested reply to an existing Epic Comment. This allows you to add threaded discussion to Epic Comments within an Epic."""

    _epic_public_id = _parse_int(epic_public_id)
    _comment_public_id = _parse_int(comment_public_id)

    # Construct request model with validation
    try:
        _request = _models.CreateEpicCommentCommentRequest(
            path=_models.CreateEpicCommentCommentRequestPath(epic_public_id=_epic_public_id, comment_public_id=_comment_public_id),
            body=_models.CreateEpicCommentCommentRequestBody(text=text, author_id=author_id, external_id=external_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_reply_to_epic_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/epics/{epic-public-id}/comments/{comment-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/epics/{epic-public-id}/comments/{comment-public-id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_reply_to_epic_comment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_reply_to_epic_comment", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_reply_to_epic_comment",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Update Epic Comment",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_epic_comment(
    epic_public_id: str = Field(..., alias="epic-public-id", description="The unique identifier of the Epic containing the comment. Must be a positive integer."),
    comment_public_id: str = Field(..., alias="comment-public-id", description="The unique identifier of the Comment to update. Must be a positive integer."),
    text: str = Field(..., description="The new text content for the comment. Replaces the existing comment text."),
) -> dict[str, Any] | ToolResult:
    """Update the text content of an existing threaded comment on an Epic. Allows modification of comment text while preserving the comment's identity and thread context."""

    _epic_public_id = _parse_int(epic_public_id)
    _comment_public_id = _parse_int(comment_public_id)

    # Construct request model with validation
    try:
        _request = _models.UpdateEpicCommentRequest(
            path=_models.UpdateEpicCommentRequestPath(epic_public_id=_epic_public_id, comment_public_id=_comment_public_id),
            body=_models.UpdateEpicCommentRequestBody(text=text)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_epic_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/epics/{epic-public-id}/comments/{comment-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/epics/{epic-public-id}/comments/{comment-public-id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_epic_comment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_epic_comment", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_epic_comment",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Delete Epic Comment",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_epic_comment(
    epic_public_id: str = Field(..., alias="epic-public-id", description="The unique identifier of the epic containing the comment. Must be a positive integer."),
    comment_public_id: str = Field(..., alias="comment-public-id", description="The unique identifier of the comment to delete. Must be a positive integer."),
) -> dict[str, Any] | ToolResult:
    """Permanently delete a comment from an epic. This action cannot be undone."""

    _epic_public_id = _parse_int(epic_public_id)
    _comment_public_id = _parse_int(comment_public_id)

    # Construct request model with validation
    try:
        _request = _models.DeleteEpicCommentRequest(
            path=_models.DeleteEpicCommentRequestPath(epic_public_id=_epic_public_id, comment_public_id=_comment_public_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_epic_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/epics/{epic-public-id}/comments/{comment-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/epics/{epic-public-id}/comments/{comment-public-id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_epic_comment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_epic_comment", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_epic_comment",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="List Epic Documents",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_epic_documents(epic_public_id: str = Field(..., alias="epic-public-id", description="The unique identifier of the Epic. Must be a valid 64-bit integer.")) -> dict[str, Any] | ToolResult:
    """Retrieve all documents associated with a specific Epic. Returns a collection of documents linked to the Epic for reference and collaboration."""

    _epic_public_id = _parse_int(epic_public_id)

    # Construct request model with validation
    try:
        _request = _models.ListEpicDocumentsRequest(
            path=_models.ListEpicDocumentsRequestPath(epic_public_id=_epic_public_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_epic_documents: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/epics/{epic-public-id}/documents", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/epics/{epic-public-id}/documents"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_epic_documents")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_epic_documents", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_epic_documents",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Get Epic Health",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_epic_health(epic_public_id: str = Field(..., alias="epic-public-id", description="The unique identifier of the Epic. Must be a valid 64-bit integer.")) -> dict[str, Any] | ToolResult:
    """Retrieve the current health status of a specified Epic. This provides insights into the Epic's overall condition and progress."""

    _epic_public_id = _parse_int(epic_public_id)

    # Construct request model with validation
    try:
        _request = _models.GetEpicHealthRequest(
            path=_models.GetEpicHealthRequestPath(epic_public_id=_epic_public_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_epic_health: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/epics/{epic-public-id}/health", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/epics/{epic-public-id}/health"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_epic_health")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_epic_health", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_epic_health",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Create Epic Health",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_epic_health(
    epic_public_id: str = Field(..., alias="epic-public-id", description="The unique identifier of the Epic for which you're creating a health status. Must be a valid 64-bit integer."),
    status: Literal["At Risk", "On Track", "Off Track", "No Health"] = Field(..., description="The health status level for the Epic. Must be one of: 'At Risk', 'On Track', 'Off Track', or 'No Health'."),
    text: str | None = Field(None, description="An optional detailed explanation or context for the health status being recorded."),
) -> dict[str, Any] | ToolResult:
    """Create a new health status record for an Epic to track its current state. This allows you to document whether the Epic is progressing as planned, facing risks, or has encountered issues."""

    _epic_public_id = _parse_int(epic_public_id)

    # Construct request model with validation
    try:
        _request = _models.CreateEpicHealthRequest(
            path=_models.CreateEpicHealthRequestPath(epic_public_id=_epic_public_id),
            body=_models.CreateEpicHealthRequestBody(status=status, text=text)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_epic_health: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/epics/{epic-public-id}/health", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/epics/{epic-public-id}/health"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_epic_health")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_epic_health", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_epic_health",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="List Epic Health History",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_epic_health_history(epic_public_id: str = Field(..., alias="epic-public-id", description="The unique identifier of the Epic whose health history you want to retrieve. Must be a valid 64-bit integer.")) -> dict[str, Any] | ToolResult:
    """Retrieve the complete health status history for a specified Epic, ordered from most recent to oldest. Use this to track how an Epic's health has evolved over time."""

    _epic_public_id = _parse_int(epic_public_id)

    # Construct request model with validation
    try:
        _request = _models.ListEpicHealthsRequest(
            path=_models.ListEpicHealthsRequestPath(epic_public_id=_epic_public_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_epic_health_history: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/epics/{epic-public-id}/health-history", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/epics/{epic-public-id}/health-history"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_epic_health_history")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_epic_health_history", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_epic_health_history",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="List Epic Stories",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_epic_stories(
    epic_public_id: str = Field(..., alias="epic-public-id", description="The unique identifier of the epic. Must be a valid 64-bit integer."),
    includes_description: bool | None = Field(None, description="Set to true to include story descriptions in the response; false or omit to exclude them."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all stories associated with a specific epic. Optionally include story descriptions in the response."""

    _epic_public_id = _parse_int(epic_public_id)

    # Construct request model with validation
    try:
        _request = _models.ListEpicStoriesRequest(
            path=_models.ListEpicStoriesRequestPath(epic_public_id=_epic_public_id),
            query=_models.ListEpicStoriesRequestQuery(includes_description=includes_description)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_epic_stories: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/epics/{epic-public-id}/stories", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/epics/{epic-public-id}/stories"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_epic_stories")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_epic_stories", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_epic_stories",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Remove Productboard from Epic",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def remove_productboard_from_epic(epic_public_id: str = Field(..., alias="epic-public-id", description="The unique identifier of the Epic to unlink from Productboard. Must be a valid 64-bit integer.")) -> dict[str, Any] | ToolResult:
    """Unlink a Productboard epic from an Epic, removing the association between the two resources."""

    _epic_public_id = _parse_int(epic_public_id)

    # Construct request model with validation
    try:
        _request = _models.UnlinkProductboardFromEpicRequest(
            path=_models.UnlinkProductboardFromEpicRequestPath(epic_public_id=_epic_public_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_productboard_from_epic: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/epics/{epic-public-id}/unlink-productboard", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/epics/{epic-public-id}/unlink-productboard"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_productboard_from_epic")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_productboard_from_epic", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_productboard_from_epic",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="List Stories by External Link",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_stories_by_external_link(external_link: str = Field(..., description="A valid HTTP or HTTPS URL (must start with http:// or https://) that is associated with one or more stories. Maximum length is 2048 characters.", max_length=2048, pattern="^https?://.+$")) -> dict[str, Any] | ToolResult:
    """Retrieve all stories associated with a given external link. Use this to find stories that reference or are linked to a specific URL."""

    # Construct request model with validation
    try:
        _request = _models.GetExternalLinkStoriesRequest(
            query=_models.GetExternalLinkStoriesRequestQuery(external_link=external_link)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_stories_by_external_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v3/external-link/stories"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_stories_by_external_link")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_stories_by_external_link", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_stories_by_external_link",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="List Files",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_files() -> dict[str, Any] | ToolResult:
    """Retrieve a list of all uploaded files in the workspace. Returns metadata for each file available in the current workspace."""

    # Extract parameters for API call
    _http_path = "/api/v3/files"
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
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Upload Files",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def upload_files(
    file0: str = Field(..., description="Base64-encoded file content for upload. The primary file to upload. This parameter is required; at least one file must be provided in the request.", json_schema_extra={'format': 'byte'}),
    story_id: str | None = Field(None, description="The ID of the story to associate these uploaded files with. If omitted, files are uploaded without story association."),
    file1: str | None = Field(None, description="Base64-encoded file content for upload. An optional additional file to upload alongside file0.", json_schema_extra={'format': 'byte'}),
    file2: str | None = Field(None, description="Base64-encoded file content for upload. An optional additional file to upload alongside file0 and file1.", json_schema_extra={'format': 'byte'}),
    file3: str | None = Field(None, description="Base64-encoded file content for upload. An optional additional file to upload alongside file0, file1, and file2.", json_schema_extra={'format': 'byte'}),
) -> dict[str, Any] | ToolResult:
    """Upload one or more files to the system, optionally associating them with a specific story. Files are submitted using multipart/form-data encoding with each file assigned to a separate form field."""

    _story_id = _parse_int(story_id)

    # Construct request model with validation
    try:
        _request = _models.UploadFilesRequest(
            body=_models.UploadFilesRequestBody(story_id=_story_id, file0=file0, file1=file1, file2=file2, file3=file3)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for upload_files: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v3/files"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("upload_files")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("upload_files", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="upload_files",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["file0", "file1", "file2", "file3"],
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Get File",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_file(file_public_id: str = Field(..., alias="file-public-id", description="The unique identifier for the file, provided as a 64-bit integer.")) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific uploaded file using its unique public identifier."""

    _file_public_id = _parse_int(file_public_id)

    # Construct request model with validation
    try:
        _request = _models.GetFileRequest(
            path=_models.GetFileRequestPath(file_public_id=_file_public_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/files/{file-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/files/{file-public-id}"
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
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Update File",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_file(
    file_public_id: str = Field(..., alias="file-public-id", description="The unique identifier of the file in Shortcut (64-bit integer)."),
    description: str | None = Field(None, description="A descriptive text for the file, up to 4096 characters.", max_length=4096),
    name: str | None = Field(None, description="The display name of the file, between 1 and 1024 characters.", min_length=1, max_length=1024),
    external_id: str | None = Field(None, description="An optional external identifier you can assign to the file for tracking purposes, up to 128 characters.", max_length=128),
) -> dict[str, Any] | ToolResult:
    """Update the metadata properties of an uploaded file, including its name, description, and external identifier. The file content itself cannot be modified through this operation."""

    _file_public_id = _parse_int(file_public_id)

    # Construct request model with validation
    try:
        _request = _models.UpdateFileRequest(
            path=_models.UpdateFileRequestPath(file_public_id=_file_public_id),
            body=_models.UpdateFileRequestBody(description=description, name=name, external_id=external_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/files/{file-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/files/{file-public-id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_file")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_file", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_file",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Delete File",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_file(file_public_id: str = Field(..., alias="file-public-id", description="The unique identifier of the file to delete, provided as a 64-bit integer.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a previously uploaded file by its unique identifier. This action cannot be undone."""

    _file_public_id = _parse_int(file_public_id)

    # Construct request model with validation
    try:
        _request = _models.DeleteFileRequest(
            path=_models.DeleteFileRequestPath(file_public_id=_file_public_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/files/{file-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/files/{file-public-id}"
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


@mcp.tool(
    title="List Groups",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_groups(archived: bool | None = Field(None, description="Filter groups by their archived state. Set to true to return only archived groups, false to return only active groups, or omit to return all groups regardless of status.")) -> dict[str, Any] | ToolResult:
    """Retrieve a list of groups (teams) in Shortcut. Groups represent collections of users that can be associated with stories, epics, and iterations. Optionally filter by archived status."""

    # Construct request model with validation
    try:
        _request = _models.ListGroupsRequest(
            query=_models.ListGroupsRequestQuery(archived=archived)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_groups: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v3/groups"
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


@mcp.tool(
    title="Create Group",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_group(
    name: str = Field(..., description="The display name of the group, between 1 and 63 characters. This is the human-readable identifier shown in the UI.", min_length=1, max_length=63),
    mention_name: str = Field(..., description="The mention handle for the group, between 1 and 63 characters. Used for @-mentions and programmatic references (e.g., @engineering-team).", min_length=1, max_length=63),
    description: str | None = Field(None, description="A detailed description of the group's purpose and scope, up to 4096 characters.", max_length=4096),
    member_ids: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(None, description="Array of member IDs to add to the group upon creation. Members can be added or modified after creation."),
    workflow_ids: list[Annotated[int, Field(json_schema_extra={'format': 'int64'})]] | None = Field(None, description="Array of workflow IDs to associate with the group. Workflows define the processes and automations available to group members."),
    display_icon_id: str | None = Field(None, description="A UUID-formatted icon ID to use as the group's avatar. If not provided, a default icon will be assigned."),
) -> dict[str, Any] | ToolResult:
    """Create a new group with members and workflows. Groups can be used to organize and manage collections of members and their associated workflows."""

    # Construct request model with validation
    try:
        _request = _models.CreateGroupRequest(
            body=_models.CreateGroupRequestBody(description=description, member_ids=member_ids, workflow_ids=workflow_ids, name=name, mention_name=mention_name, display_icon_id=display_icon_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v3/groups"
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
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Get Group",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_group(group_public_id: str = Field(..., alias="group-public-id", description="The unique identifier of the group, formatted as a UUID.")) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific group using its unique public identifier. Returns the group's metadata and configuration."""

    # Construct request model with validation
    try:
        _request = _models.GetGroupRequest(
            path=_models.GetGroupRequestPath(group_public_id=group_public_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/groups/{group-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/groups/{group-public-id}"
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
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Update Group",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_group(
    group_public_id: str = Field(..., alias="group-public-id", description="The unique identifier of the group to update, formatted as a UUID."),
    description: str | None = Field(None, description="A text description of the group, up to 4096 characters.", max_length=4096),
    archived: bool | None = Field(None, description="Whether the group is archived. Archived groups are typically hidden from active use but retain their data."),
    display_icon_id: str | None = Field(None, description="The UUID of an icon to use as the group's avatar."),
    mention_name: str | None = Field(None, description="The mention name for the group, used in @mentions. Must be 1-63 characters long.", min_length=1, max_length=63),
    name: str | None = Field(None, description="The display name of the group, 1-63 characters long.", min_length=1, max_length=63),
    default_workflow_id: str | None = Field(None, description="The numeric ID of the workflow to set as the default for stories created in this group."),
    member_ids: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(None, description="An array of member IDs to add to the group. Each ID should be a valid member identifier."),
    workflow_ids: list[Annotated[int, Field(json_schema_extra={'format': 'int64'})]] | None = Field(None, description="An array of workflow IDs to associate with the group, enabling these workflows for story creation."),
) -> dict[str, Any] | ToolResult:
    """Update an existing group's properties including name, description, icon, workflow settings, and membership. Allows archiving groups and modifying their configuration."""

    _default_workflow_id = _parse_int(default_workflow_id)

    # Construct request model with validation
    try:
        _request = _models.UpdateGroupRequest(
            path=_models.UpdateGroupRequestPath(group_public_id=group_public_id),
            body=_models.UpdateGroupRequestBody(description=description, archived=archived, display_icon_id=display_icon_id, mention_name=mention_name, name=name, default_workflow_id=_default_workflow_id, member_ids=member_ids, workflow_ids=workflow_ids)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/groups/{group-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/groups/{group-public-id}"
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
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="List Group Stories",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_group_stories(
    group_public_id: str = Field(..., alias="group-public-id", description="The unique identifier of the Group, formatted as a UUID."),
    limit: str | None = Field(None, description="Maximum number of results to return per request. Defaults to 1,000 and cannot exceed 1,000."),
    offset: str | None = Field(None, description="Number of results to skip before returning data, enabling pagination through large result sets. Defaults to 0."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all Stories assigned to a specific Group with pagination support. Results are limited to a maximum of 1,000 stories by default."""

    _limit = _parse_int(limit)
    _offset = _parse_int(offset)

    # Construct request model with validation
    try:
        _request = _models.ListGroupStoriesRequest(
            path=_models.ListGroupStoriesRequestPath(group_public_id=group_public_id),
            query=_models.ListGroupStoriesRequestQuery(limit=_limit, offset=_offset)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_group_stories: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/groups/{group-public-id}/stories", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/groups/{group-public-id}/stories"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_group_stories")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_group_stories", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_group_stories",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Update Health",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_health(
    health_public_id: str = Field(..., alias="health-public-id", description="The unique identifier of the Health record to update, formatted as a UUID."),
    status: Literal["At Risk", "On Track", "Off Track", "No Health"] | None = Field(None, description="The health status level for the Epic. Must be one of: At Risk, On Track, Off Track, or No Health."),
    text: str | None = Field(None, description="A text description providing context or details about the health status."),
) -> dict[str, Any] | ToolResult:
    """Update the health status and description of an Epic. Modify the current health state and optional status text to reflect the Epic's current condition."""

    # Construct request model with validation
    try:
        _request = _models.UpdateHealthRequest(
            path=_models.UpdateHealthRequestPath(health_public_id=health_public_id),
            body=_models.UpdateHealthRequestBody(status=status, text=text)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_health: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/health/{health-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/health/{health-public-id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_health")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_health", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_health",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Get Webhook Integration",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_webhook_integration(integration_public_id: str = Field(..., alias="integration-public-id", description="The unique public identifier of the webhook integration to retrieve. Must be a valid 64-bit integer.")) -> dict[str, Any] | ToolResult:
    """Retrieve a specific webhook integration by its public identifier. Use this to fetch configuration and details for a webhook integration."""

    _integration_public_id = _parse_int(integration_public_id)

    # Construct request model with validation
    try:
        _request = _models.GetGenericIntegrationRequest(
            path=_models.GetGenericIntegrationRequestPath(integration_public_id=_integration_public_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_webhook_integration: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/integrations/webhook/{integration-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/integrations/webhook/{integration-public-id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_webhook_integration")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_webhook_integration", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_webhook_integration",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Delete Webhook Integration",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_webhook_integration(integration_public_id: str = Field(..., alias="integration-public-id", description="The unique public identifier of the webhook integration to delete, provided as a 64-bit integer.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a webhook integration by its public identifier. This action cannot be undone and will remove all associated webhook configurations."""

    _integration_public_id = _parse_int(integration_public_id)

    # Construct request model with validation
    try:
        _request = _models.DeleteGenericIntegrationRequest(
            path=_models.DeleteGenericIntegrationRequestPath(integration_public_id=_integration_public_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_webhook_integration: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/integrations/webhook/{integration-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/integrations/webhook/{integration-public-id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_webhook_integration")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_webhook_integration", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_webhook_integration",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="List Iterations",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_iterations() -> dict[str, Any] | ToolResult:
    """Retrieve a list of all iterations. Iterations represent time-boxed periods used for organizing and tracking work in agile project management."""

    # Extract parameters for API call
    _http_path = "/api/v3/iterations"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_iterations")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_iterations", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_iterations",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Create Iteration",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_iteration(
    name: str = Field(..., description="The name of the iteration. Must be between 1 and 256 characters.", min_length=1, max_length=256),
    start_date: str = Field(..., description="The start date of the iteration in ISO 8601 format (e.g., 2019-07-01). Required and must be a valid date string.", min_length=1),
    end_date: str = Field(..., description="The end date of the iteration in ISO 8601 format (e.g., 2019-07-01). Required and must be a valid date string.", min_length=1),
    group_ids: list[Annotated[str, Field(json_schema_extra={'format': 'uuid'})]] | None = Field(None, description="An array of group UUIDs to add as followers to this iteration. Currently, the web UI supports only one group association at a time."),
    description: str | None = Field(None, description="A detailed description of the iteration's purpose or scope. Limited to 100,000 characters.", max_length=100000),
) -> dict[str, Any] | ToolResult:
    """Create a new iteration (sprint or planning cycle) with a specified name, date range, and optional description. Optionally add groups as followers to the iteration."""

    # Construct request model with validation
    try:
        _request = _models.CreateIterationRequest(
            body=_models.CreateIterationRequestBody(group_ids=group_ids, description=description, name=name, start_date=start_date, end_date=end_date)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_iteration: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v3/iterations"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_iteration")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_iteration", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_iteration",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Get Iteration",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_iteration(iteration_public_id: str = Field(..., alias="iteration-public-id", description="The unique identifier for the iteration as a 64-bit integer. This ID is used to look up and retrieve the specific iteration's details.")) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific iteration by its public ID. Use this to fetch iteration metadata, status, and associated data."""

    _iteration_public_id = _parse_int(iteration_public_id)

    # Construct request model with validation
    try:
        _request = _models.GetIterationRequest(
            path=_models.GetIterationRequestPath(iteration_public_id=_iteration_public_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_iteration: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/iterations/{iteration-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/iterations/{iteration-public-id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_iteration")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_iteration", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_iteration",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Update Iteration",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_iteration(
    iteration_public_id: str = Field(..., alias="iteration-public-id", description="The unique identifier of the iteration to update. Must be a valid 64-bit integer."),
    group_ids: list[Annotated[str, Field(json_schema_extra={'format': 'uuid'})]] | None = Field(None, description="An array of group UUIDs to add as followers to this iteration. Currently, the web UI supports one group association at a time."),
    description: str | None = Field(None, description="A detailed description of the iteration. Maximum length is 100,000 characters.", max_length=100000),
    name: str | None = Field(None, description="The display name of the iteration. Must be between 1 and 256 characters.", min_length=1, max_length=256),
    start_date: str | None = Field(None, description="The start date of the iteration in ISO 8601 format (e.g., YYYY-MM-DD). Must be a non-empty string.", min_length=1),
    end_date: str | None = Field(None, description="The end date of the iteration in ISO 8601 format (e.g., YYYY-MM-DD). Must be a non-empty string.", min_length=1),
) -> dict[str, Any] | ToolResult:
    """Update an existing iteration with new metadata such as name, description, dates, and group followers. Allows partial updates—only provided fields are modified."""

    _iteration_public_id = _parse_int(iteration_public_id)

    # Construct request model with validation
    try:
        _request = _models.UpdateIterationRequest(
            path=_models.UpdateIterationRequestPath(iteration_public_id=_iteration_public_id),
            body=_models.UpdateIterationRequestBody(group_ids=group_ids, description=description, name=name, start_date=start_date, end_date=end_date)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_iteration: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/iterations/{iteration-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/iterations/{iteration-public-id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_iteration")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_iteration", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_iteration",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Delete Iteration",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_iteration(iteration_public_id: str = Field(..., alias="iteration-public-id", description="The unique public identifier of the iteration to delete, provided as a 64-bit integer.")) -> dict[str, Any] | ToolResult:
    """Permanently delete an iteration by its public ID. This action cannot be undone and will remove the iteration and all associated data."""

    _iteration_public_id = _parse_int(iteration_public_id)

    # Construct request model with validation
    try:
        _request = _models.DeleteIterationRequest(
            path=_models.DeleteIterationRequestPath(iteration_public_id=_iteration_public_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_iteration: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/iterations/{iteration-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/iterations/{iteration-public-id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_iteration")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_iteration", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_iteration",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="List Iteration Stories",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_iteration_stories(
    iteration_public_id: str = Field(..., alias="iteration-public-id", description="The unique identifier of the iteration. Must be a positive integer."),
    includes_description: bool | None = Field(None, description="Set to true to include story descriptions in the response; false or omit to exclude them."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all stories associated with a specific iteration. Optionally include story descriptions in the response."""

    _iteration_public_id = _parse_int(iteration_public_id)

    # Construct request model with validation
    try:
        _request = _models.ListIterationStoriesRequest(
            path=_models.ListIterationStoriesRequestPath(iteration_public_id=_iteration_public_id),
            query=_models.ListIterationStoriesRequestQuery(includes_description=includes_description)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_iteration_stories: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/iterations/{iteration-public-id}/stories", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/iterations/{iteration-public-id}/stories"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_iteration_stories")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_iteration_stories", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_iteration_stories",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Get Key Result",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_key_result(key_result_public_id: str = Field(..., alias="key-result-public-id", description="The unique identifier of the Key Result to retrieve, formatted as a UUID.")) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific Key Result by its unique identifier. Returns the Key Result's properties and current state."""

    # Construct request model with validation
    try:
        _request = _models.GetKeyResultRequest(
            path=_models.GetKeyResultRequestPath(key_result_public_id=key_result_public_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_key_result: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/key-results/{key-result-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/key-results/{key-result-public-id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_key_result")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_key_result", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_key_result",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Update Key Result",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_key_result(
    key_result_public_id: str = Field(..., alias="key-result-public-id", description="The unique identifier of the Key Result to update, formatted as a UUID."),
    name: str | None = Field(None, description="The updated name for the Key Result. Maximum length is 1024 characters.", max_length=1024),
    numeric_value: str | None = Field(None, description="The observed numeric value as a decimal string, limited to a maximum of two decimal places."),
    boolean_value: bool | None = Field(None, description="The observed boolean value (true or false)."),
) -> dict[str, Any] | ToolResult:
    """Update a Key Result's name, initial value, observed value, or target value. Supports numeric values (up to 2 decimal places) or boolean values for the observed metric."""

    # Construct request model with validation
    try:
        _request = _models.UpdateKeyResultRequest(
            path=_models.UpdateKeyResultRequestPath(key_result_public_id=key_result_public_id),
            body=_models.UpdateKeyResultRequestBody(name=name,
                observed_value=_models.UpdateKeyResultRequestBodyObservedValue(numeric_value=numeric_value, boolean_value=boolean_value) if any(v is not None for v in [numeric_value, boolean_value]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_key_result: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/key-results/{key-result-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/key-results/{key-result-public-id}"
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
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="List Labels",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_labels(slim: bool | None = Field(None, description="When true, returns a lightweight version of each label with minimal attributes; when false or omitted, returns complete label details.")) -> dict[str, Any] | ToolResult:
    """Retrieve all labels available in the system with their complete attributes. Optionally request slim versions containing only essential label information."""

    # Construct request model with validation
    try:
        _request = _models.ListLabelsRequest(
            query=_models.ListLabelsRequestQuery(slim=slim)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_labels: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v3/labels"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_labels")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_labels", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_labels",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Create Label",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_label(
    name: str = Field(..., description="The display name for the label. Must be between 1 and 128 characters.", min_length=1, max_length=128),
    description: str | None = Field(None, description="Optional descriptive text explaining the label's purpose or usage. Limited to 1024 characters.", max_length=1024),
    external_id: str | None = Field(None, description="Optional external identifier for labels imported from other tools. Use this to maintain references to the original tool's ID. Must be between 1 and 128 characters if provided.", min_length=1, max_length=128),
) -> dict[str, Any] | ToolResult:
    """Create a new label in Shortcut to organize and categorize work items. Labels help teams tag and filter issues, stories, and other work across projects."""

    # Construct request model with validation
    try:
        _request = _models.CreateLabelRequest(
            body=_models.CreateLabelRequestBody(name=name, description=description, external_id=external_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_label: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v3/labels"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_label")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_label", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_label",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Get Label",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_label(label_public_id: str = Field(..., alias="label-public-id", description="The unique identifier of the label to retrieve, specified as a 64-bit integer.")) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific label by its unique identifier. Returns the label's properties and metadata."""

    _label_public_id = _parse_int(label_public_id)

    # Construct request model with validation
    try:
        _request = _models.GetLabelRequest(
            path=_models.GetLabelRequestPath(label_public_id=_label_public_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_label: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/labels/{label-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/labels/{label-public-id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_label")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_label", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_label",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Update Label",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def update_label(
    label_public_id: str = Field(..., alias="label-public-id", description="The unique identifier of the label to update. Must be a valid 64-bit integer."),
    name: str | None = Field(None, description="The new name for the label. Must be between 1 and 128 characters long.", min_length=1, max_length=128),
    description: str | None = Field(None, description="The new description for the label. Must not exceed 1024 characters.", max_length=1024),
    archived: bool | None = Field(None, description="Whether the label should be archived. Set to true to archive the label, or false to unarchive it."),
) -> dict[str, Any] | ToolResult:
    """Update a label's name, description, or archived status. The label name must be unique within the system; attempting to use a name that already exists will result in an error."""

    _label_public_id = _parse_int(label_public_id)

    # Construct request model with validation
    try:
        _request = _models.UpdateLabelRequest(
            path=_models.UpdateLabelRequestPath(label_public_id=_label_public_id),
            body=_models.UpdateLabelRequestBody(name=name, description=description, archived=archived)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_label: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/labels/{label-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/labels/{label-public-id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_label")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_label", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_label",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Delete Label",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_label(label_public_id: str = Field(..., alias="label-public-id", description="The unique identifier of the label to delete, specified as a 64-bit integer.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a label by its unique identifier. This operation removes the label and cannot be undone."""

    _label_public_id = _parse_int(label_public_id)

    # Construct request model with validation
    try:
        _request = _models.DeleteLabelRequest(
            path=_models.DeleteLabelRequestPath(label_public_id=_label_public_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_label: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/labels/{label-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/labels/{label-public-id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_label")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_label", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_label",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="List Epics for Label",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_epics_for_label(label_public_id: str = Field(..., alias="label-public-id", description="The unique identifier of the Label. Must be a positive integer value.")) -> dict[str, Any] | ToolResult:
    """Retrieve all Epics associated with a specific Label. Use this to view Epic-level work items grouped by a particular label."""

    _label_public_id = _parse_int(label_public_id)

    # Construct request model with validation
    try:
        _request = _models.ListLabelEpicsRequest(
            path=_models.ListLabelEpicsRequestPath(label_public_id=_label_public_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_epics_for_label: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/labels/{label-public-id}/epics", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/labels/{label-public-id}/epics"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_epics_for_label")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_epics_for_label", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_epics_for_label",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="List Stories by Label",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_stories_by_label(
    label_public_id: str = Field(..., alias="label-public-id", description="The unique identifier of the label. Must be a valid 64-bit integer."),
    includes_description: bool | None = Field(None, description="Set to true to include story descriptions in the response; false or omit to exclude them."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all stories associated with a specific label. Optionally include story descriptions in the response."""

    _label_public_id = _parse_int(label_public_id)

    # Construct request model with validation
    try:
        _request = _models.ListLabelStoriesRequest(
            path=_models.ListLabelStoriesRequestPath(label_public_id=_label_public_id),
            query=_models.ListLabelStoriesRequestQuery(includes_description=includes_description)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_stories_by_label: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/labels/{label-public-id}/stories", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/labels/{label-public-id}/stories"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_stories_by_label")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_stories_by_label", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_stories_by_label",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="List Linked Files",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_linked_files() -> dict[str, Any] | ToolResult:
    """Retrieve a complete list of all linked files with their attributes. Use this to view all file associations in the system."""

    # Extract parameters for API call
    _http_path = "/api/v3/linked-files"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_linked_files")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_linked_files", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_linked_files",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Create Linked File",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_linked_file(
    name: str = Field(..., description="The display name for the linked file. Must be between 1 and 256 characters.", min_length=1, max_length=256),
    type_: Literal["google", "url", "dropbox", "box", "onedrive"] = Field(..., alias="type", description="The source service or integration type for the file. Must be one of: google (Google Drive), url (direct link), dropbox (Dropbox), box (Box), or onedrive (OneDrive)."),
    url: str = Field(..., description="The full URL pointing to the linked file. Must be a valid HTTP or HTTPS URL and cannot exceed 2048 characters.", max_length=2048, pattern="^https?://.+$"),
    description: str | None = Field(None, description="A brief explanation of the file's purpose or contents. Limited to 512 characters.", max_length=512),
    story_id: str | None = Field(None, description="The numeric ID of the story to associate this linked file with. If omitted, the file is created without a story association."),
    content_type: str | None = Field(None, description="The MIME type describing the file's format (e.g., text/plain, application/pdf). Limited to 128 characters.", max_length=128),
) -> dict[str, Any] | ToolResult:
    """Create a new linked file in Shortcut that references an external file from an integrated service like Google Drive, Dropbox, Box, OneDrive, or a direct URL. Optionally associate the file with a specific story."""

    _story_id = _parse_int(story_id)

    # Construct request model with validation
    try:
        _request = _models.CreateLinkedFileRequest(
            body=_models.CreateLinkedFileRequestBody(description=description, story_id=_story_id, name=name, type_=type_, content_type=content_type, url=url)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_linked_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v3/linked-files"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_linked_file")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_linked_file", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_linked_file",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Get Linked File",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_linked_file(linked_file_public_id: str = Field(..., alias="linked-file-public-id", description="The unique public identifier of the linked file to retrieve. Must be a valid 64-bit integer.")) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific linked file using its unique public identifier."""

    _linked_file_public_id = _parse_int(linked_file_public_id)

    # Construct request model with validation
    try:
        _request = _models.GetLinkedFileRequest(
            path=_models.GetLinkedFileRequestPath(linked_file_public_id=_linked_file_public_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_linked_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/linked-files/{linked-file-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/linked-files/{linked-file-public-id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_linked_file")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_linked_file", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_linked_file",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Update Linked File",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_linked_file(
    linked_file_public_id: str = Field(..., alias="linked-file-public-id", description="The unique identifier of the linked file to update. Must be a valid 64-bit integer."),
    description: str | None = Field(None, description="A brief description of the file's purpose or content. Limited to 512 characters.", max_length=512),
    story_id: str | None = Field(None, description="The ID of the story to associate with this linked file. Must be a valid 64-bit integer."),
    name: str | None = Field(None, description="The display name of the file. Must be at least 1 character long.", min_length=1),
    type_: Literal["google", "url", "dropbox", "box", "onedrive"] | None = Field(None, alias="type", description="The source integration type for the file. Valid options are: google (Google Drive), url (direct link), dropbox (Dropbox), box (Box), or onedrive (OneDrive)."),
    url: str | None = Field(None, description="The web address of the linked file. Must be a valid HTTP or HTTPS URL and cannot exceed 2048 characters.", max_length=2048, pattern="^https?://.+$"),
) -> dict[str, Any] | ToolResult:
    """Update properties of a previously attached linked file, such as its name, description, associated story, or source URL. Supports files from multiple integration types including Google Drive, Dropbox, Box, OneDrive, and direct URLs."""

    _linked_file_public_id = _parse_int(linked_file_public_id)
    _story_id = _parse_int(story_id)

    # Construct request model with validation
    try:
        _request = _models.UpdateLinkedFileRequest(
            path=_models.UpdateLinkedFileRequestPath(linked_file_public_id=_linked_file_public_id),
            body=_models.UpdateLinkedFileRequestBody(description=description, story_id=_story_id, name=name, type_=type_, url=url)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_linked_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/linked-files/{linked-file-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/linked-files/{linked-file-public-id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_linked_file")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_linked_file", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_linked_file",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Delete Linked File",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_linked_file(linked_file_public_id: str = Field(..., alias="linked-file-public-id", description="The unique identifier of the linked file to delete. Must be a valid 64-bit integer.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a previously attached linked file by its unique identifier. This operation removes the file association and cannot be undone."""

    _linked_file_public_id = _parse_int(linked_file_public_id)

    # Construct request model with validation
    try:
        _request = _models.DeleteLinkedFileRequest(
            path=_models.DeleteLinkedFileRequestPath(linked_file_public_id=_linked_file_public_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_linked_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/linked-files/{linked-file-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/linked-files/{linked-file-public-id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_linked_file")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_linked_file", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_linked_file",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Get Current Member",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_current_member() -> dict[str, Any] | ToolResult:
    """Retrieves detailed information about the authenticated member, including profile data and account settings."""

    # Extract parameters for API call
    _http_path = "/api/v3/member"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_current_member")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_current_member", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_current_member",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="List Workspace Members",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_workspace_members(
    org_public_id: str | None = Field(None, alias="org-public-id", description="Filter results to members belonging to a specific Organization by providing its unique identifier (UUID format)."),
    disabled: bool | None = Field(None, description="Filter members by their account status: true returns only disabled members, false returns only enabled members. Omit to include all members regardless of status."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a list of members in the Workspace, with optional filtering by Organization and member status."""

    # Construct request model with validation
    try:
        _request = _models.ListMembersRequest(
            query=_models.ListMembersRequestQuery(org_public_id=org_public_id, disabled=disabled)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_workspace_members: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v3/members"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_workspace_members")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_workspace_members", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_workspace_members",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Get Member",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_member(
    member_public_id: str = Field(..., alias="member-public-id", description="The unique identifier of the member to retrieve, formatted as a UUID."),
    org_public_id: str | None = Field(None, alias="org-public-id", description="Optional organization identifier (UUID format) to scope the member lookup to a specific organization."),
) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific member by their unique identifier. Optionally scope the lookup to a particular organization."""

    # Construct request model with validation
    try:
        _request = _models.GetMemberRequest(
            path=_models.GetMemberRequestPath(member_public_id=member_public_id),
            query=_models.GetMemberRequestQuery(org_public_id=org_public_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_member: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/members/{member-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/members/{member-public-id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_member")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_member", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_member",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="List Milestones",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_milestones() -> dict[str, Any] | ToolResult:
    """Retrieve a list of all milestones with their attributes. Note: This endpoint is deprecated; use list_objectives for new implementations."""

    # Extract parameters for API call
    _http_path = "/api/v3/milestones"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_milestones")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_milestones", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_milestones",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Create Milestone",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_milestone(
    name: str = Field(..., description="The name of the Milestone. Must be between 1 and 256 characters.", min_length=1, max_length=256),
    description: str | None = Field(None, description="Optional description of the Milestone. Can be up to 100,000 characters.", max_length=100000),
    categories: list[_models.CreateCategoryParams] | None = Field(None, description="Optional array of Category IDs to attach to the Milestone. Provide as a list of numeric identifiers."),
) -> dict[str, Any] | ToolResult:
    """Create a new Milestone in Shortcut. Note: This operation is deprecated; use create_objective for new implementations."""

    # Construct request model with validation
    try:
        _request = _models.CreateMilestoneRequest(
            body=_models.CreateMilestoneRequestBody(name=name, description=description, categories=categories)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_milestone: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v3/milestones"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_milestone")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_milestone", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_milestone",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Get Milestone",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_milestone(milestone_public_id: str = Field(..., alias="milestone-public-id", description="The unique identifier of the milestone to retrieve, provided as a 64-bit integer.")) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific milestone by its public ID. Note: This operation is deprecated; use get_objective instead for new implementations."""

    _milestone_public_id = _parse_int(milestone_public_id)

    # Construct request model with validation
    try:
        _request = _models.GetMilestoneRequest(
            path=_models.GetMilestoneRequestPath(milestone_public_id=_milestone_public_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_milestone: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/milestones/{milestone-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/milestones/{milestone-public-id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_milestone")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_milestone", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_milestone",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Update Milestone",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def update_milestone(
    milestone_public_id: str = Field(..., alias="milestone-public-id", description="The unique identifier of the milestone to update. Must be a valid 64-bit integer."),
    description: str | None = Field(None, description="The milestone's description text. Can be up to 100,000 characters long.", max_length=100000),
    archived: bool | None = Field(None, description="Whether the milestone is archived. Set to true to archive or false to unarchive."),
    name: str | None = Field(None, description="The display name for the milestone. Must be between 1 and 256 characters.", min_length=1, max_length=256),
    categories: list[_models.CreateCategoryParams] | None = Field(None, description="An array of category IDs to attach to the milestone. Each element should be a category identifier."),
) -> dict[str, Any] | ToolResult:
    """Update properties of an existing milestone, including its name, description, archived status, and associated categories. Note: This operation is deprecated; use update_objective for new implementations."""

    _milestone_public_id = _parse_int(milestone_public_id)

    # Construct request model with validation
    try:
        _request = _models.UpdateMilestoneRequest(
            path=_models.UpdateMilestoneRequestPath(milestone_public_id=_milestone_public_id),
            body=_models.UpdateMilestoneRequestBody(description=description, archived=archived, name=name, categories=categories)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_milestone: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/milestones/{milestone-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/milestones/{milestone-public-id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_milestone")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_milestone", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_milestone",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Delete Milestone",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_milestone(milestone_public_id: str = Field(..., alias="milestone-public-id", description="The unique identifier of the milestone to delete, specified as a 64-bit integer.")) -> dict[str, Any] | ToolResult:
    """Delete a milestone by its public ID. Note: This operation is deprecated; use delete_objective instead for new implementations."""

    _milestone_public_id = _parse_int(milestone_public_id)

    # Construct request model with validation
    try:
        _request = _models.DeleteMilestoneRequest(
            path=_models.DeleteMilestoneRequestPath(milestone_public_id=_milestone_public_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_milestone: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/milestones/{milestone-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/milestones/{milestone-public-id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_milestone")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_milestone", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_milestone",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="List Epics for Milestone",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_epics_for_milestone(milestone_public_id: str = Field(..., alias="milestone-public-id", description="The unique identifier of the milestone. Must be a positive integer value.")) -> dict[str, Any] | ToolResult:
    """Retrieve all epics associated with a specific milestone. This operation is deprecated; use list_objective_epics instead for new implementations."""

    _milestone_public_id = _parse_int(milestone_public_id)

    # Construct request model with validation
    try:
        _request = _models.ListMilestoneEpicsRequest(
            path=_models.ListMilestoneEpicsRequestPath(milestone_public_id=_milestone_public_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_epics_for_milestone: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/milestones/{milestone-public-id}/epics", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/milestones/{milestone-public-id}/epics"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_epics_for_milestone")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_epics_for_milestone", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_epics_for_milestone",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="List Objectives",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_objectives() -> dict[str, Any] | ToolResult:
    """Retrieve a complete list of all objectives with their associated attributes and metadata."""

    # Extract parameters for API call
    _http_path = "/api/v3/objectives"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_objectives")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_objectives", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_objectives",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Create Objective",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_objective(
    name: str = Field(..., description="The name of the Objective. Must be between 1 and 256 characters.", min_length=1, max_length=256),
    description: str | None = Field(None, description="A detailed description of the Objective. Can be up to 100,000 characters to provide comprehensive context and guidance.", max_length=100000),
    categories: list[_models.CreateCategoryParams] | None = Field(None, description="An array of Category IDs to associate with this Objective for organizational purposes. Each ID should reference an existing Category."),
) -> dict[str, Any] | ToolResult:
    """Create a new Objective in Shortcut to define goals and track progress. Objectives can be organized with categories and include detailed descriptions."""

    # Construct request model with validation
    try:
        _request = _models.CreateObjectiveRequest(
            body=_models.CreateObjectiveRequestBody(name=name, description=description, categories=categories)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_objective: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v3/objectives"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_objective")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_objective", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_objective",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Get Objective",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_objective(objective_public_id: str = Field(..., alias="objective-public-id", description="The unique public identifier for the Objective. Must be a valid 64-bit integer.")) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific Objective by its public ID. Use this to fetch the full details of an Objective you want to inspect or reference."""

    _objective_public_id = _parse_int(objective_public_id)

    # Construct request model with validation
    try:
        _request = _models.GetObjectiveRequest(
            path=_models.GetObjectiveRequestPath(objective_public_id=_objective_public_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_objective: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/objectives/{objective-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/objectives/{objective-public-id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_objective")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_objective", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_objective",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Update Objective",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def update_objective(
    objective_public_id: str = Field(..., alias="objective-public-id", description="The unique identifier of the Objective to update. Must be a valid 64-bit integer."),
    description: str | None = Field(None, description="The Objective's description text. Can be up to 100,000 characters long.", max_length=100000),
    archived: bool | None = Field(None, description="A boolean flag to archive or unarchive the Objective. Set to true to archive, false to unarchive."),
    name: str | None = Field(None, description="The name of the Objective. Must be between 1 and 256 characters long.", min_length=1, max_length=256),
    categories: list[_models.CreateCategoryParams] | None = Field(None, description="An array of Category IDs to attach to the Objective. Provide as a list of numeric identifiers."),
) -> dict[str, Any] | ToolResult:
    """Update an Objective's properties including its name, description, archived status, and associated categories. Use this operation to modify any aspect of an existing Objective."""

    _objective_public_id = _parse_int(objective_public_id)

    # Construct request model with validation
    try:
        _request = _models.UpdateObjectiveRequest(
            path=_models.UpdateObjectiveRequestPath(objective_public_id=_objective_public_id),
            body=_models.UpdateObjectiveRequestBody(description=description, archived=archived, name=name, categories=categories)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_objective: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/objectives/{objective-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/objectives/{objective-public-id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_objective")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_objective", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_objective",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Delete Objective",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_objective(objective_public_id: str = Field(..., alias="objective-public-id", description="The unique public identifier of the Objective to delete, specified as a 64-bit integer.")) -> dict[str, Any] | ToolResult:
    """Permanently delete an Objective by its public ID. This action cannot be undone."""

    _objective_public_id = _parse_int(objective_public_id)

    # Construct request model with validation
    try:
        _request = _models.DeleteObjectiveRequest(
            path=_models.DeleteObjectiveRequestPath(objective_public_id=_objective_public_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_objective: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/objectives/{objective-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/objectives/{objective-public-id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_objective")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_objective", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_objective",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="List Epics for Objective",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_epics_for_objective(objective_public_id: str = Field(..., alias="objective-public-id", description="The unique identifier of the objective. Must be a positive integer value.")) -> dict[str, Any] | ToolResult:
    """Retrieve all epics associated with a specific objective. Epics are returned as a collection within the objective."""

    _objective_public_id = _parse_int(objective_public_id)

    # Construct request model with validation
    try:
        _request = _models.ListObjectiveEpicsRequest(
            path=_models.ListObjectiveEpicsRequestPath(objective_public_id=_objective_public_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_epics_for_objective: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/objectives/{objective-public-id}/epics", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/objectives/{objective-public-id}/epics"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_epics_for_objective")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_epics_for_objective", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_epics_for_objective",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="List Projects",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_projects() -> dict[str, Any] | ToolResult:
    """Retrieve a list of all projects with their complete attributes and metadata. Use this to discover available projects or build project directories."""

    # Extract parameters for API call
    _http_path = "/api/v3/projects"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_projects")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_projects", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_projects",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Create Project",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_project(
    name: str = Field(..., description="The display name for the project. Must be between 1 and 128 characters long.", min_length=1, max_length=128),
    team_id: str = Field(..., description="The numeric ID of the team that will own this project."),
    description: str | None = Field(None, description="A detailed description of the project's purpose and scope. Limited to 100,000 characters.", max_length=100000),
    start_time: str | None = Field(None, description="The project's start date in ISO 8601 date-time format."),
    external_id: str | None = Field(None, description="An external identifier for the project, useful when migrating from another tool. Limited to 128 characters.", max_length=128),
    iteration_length: str | None = Field(None, description="The duration of each iteration cycle in this project, specified in weeks."),
    abbreviation: str | None = Field(None, description="A short abbreviation for the project, typically 3 characters or fewer, used in story summaries. Limited to 63 characters.", max_length=63),
) -> dict[str, Any] | ToolResult:
    """Creates a new Shortcut project within a specified team. The project name is required, and you can optionally configure iteration length, description, start date, abbreviation, and external identifiers."""

    _team_id = _parse_int(team_id)
    _iteration_length = _parse_int(iteration_length)

    # Construct request model with validation
    try:
        _request = _models.CreateProjectRequest(
            body=_models.CreateProjectRequestBody(description=description, name=name, start_time=start_time, external_id=external_id, team_id=_team_id, iteration_length=_iteration_length, abbreviation=abbreviation)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v3/projects"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_project")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_project", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_project",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Get Project",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_project(project_public_id: str = Field(..., alias="project-public-id", description="The unique public identifier for the project. Must be a valid 64-bit integer.")) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific project using its unique public identifier. Returns comprehensive project metadata and configuration."""

    _project_public_id = _parse_int(project_public_id)

    # Construct request model with validation
    try:
        _request = _models.GetProjectRequest(
            path=_models.GetProjectRequestPath(project_public_id=_project_public_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/projects/{project-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/projects/{project-public-id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_project")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_project", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_project",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Update Project",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_project(
    project_public_id: str = Field(..., alias="project-public-id", description="The unique identifier of the project to update. Must be a valid 64-bit integer."),
    description: str | None = Field(None, description="The project's description text. Can be up to 100,000 characters long.", max_length=100000),
    archived: bool | None = Field(None, description="Whether the project is archived. Set to true to archive the project or false to unarchive it."),
    days_to_thermometer: str | None = Field(None, description="The number of days before the thermometer indicator appears in story summaries. Must be a non-negative 64-bit integer."),
    name: str | None = Field(None, description="The project's display name. Must be between 1 and 128 characters long.", min_length=1, max_length=128),
    show_thermometer: bool | None = Field(None, description="Enable or disable thermometer indicators in story summaries. Set to true to show thermometers or false to hide them."),
    team_id: str | None = Field(None, description="The 64-bit integer ID of the team this project belongs to. Use this to reassign the project to a different team."),
    abbreviation: str | None = Field(None, description="A short abbreviation for the project used in story summaries. Recommended to keep to 3 characters or fewer."),
) -> dict[str, Any] | ToolResult:
    """Update project properties such as name, description, team assignment, and thermometer settings. Changes are applied immediately to the specified project."""

    _project_public_id = _parse_int(project_public_id)
    _days_to_thermometer = _parse_int(days_to_thermometer)
    _team_id = _parse_int(team_id)

    # Construct request model with validation
    try:
        _request = _models.UpdateProjectRequest(
            path=_models.UpdateProjectRequestPath(project_public_id=_project_public_id),
            body=_models.UpdateProjectRequestBody(description=description, archived=archived, days_to_thermometer=_days_to_thermometer, name=name, show_thermometer=show_thermometer, team_id=_team_id, abbreviation=abbreviation)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/projects/{project-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/projects/{project-public-id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_project")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_project", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_project",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Delete Project",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_project(project_public_id: str = Field(..., alias="project-public-id", description="The unique identifier of the project to delete, provided as a 64-bit integer.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a project. Projects can only be deleted if all associated stories have been moved or deleted; attempting to delete a project with remaining stories will result in a 422 error."""

    _project_public_id = _parse_int(project_public_id)

    # Construct request model with validation
    try:
        _request = _models.DeleteProjectRequest(
            path=_models.DeleteProjectRequestPath(project_public_id=_project_public_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/projects/{project-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/projects/{project-public-id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_project")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_project", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_project",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="List Stories",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_stories(
    project_public_id: str = Field(..., alias="project-public-id", description="The unique identifier of the project. Must be a valid 64-bit integer."),
    includes_description: bool | None = Field(None, description="Set to true to include story descriptions in the response; omit or set to false to exclude them."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all stories in a project with their core attributes. Optionally include story descriptions in the response."""

    _project_public_id = _parse_int(project_public_id)

    # Construct request model with validation
    try:
        _request = _models.ListStoriesRequest(
            path=_models.ListStoriesRequestPath(project_public_id=_project_public_id),
            query=_models.ListStoriesRequestQuery(includes_description=includes_description)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_stories: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/projects/{project-public-id}/stories", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/projects/{project-public-id}/stories"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_stories")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_stories", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_stories",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="List Repositories",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_repositories() -> dict[str, Any] | ToolResult:
    """Retrieve a complete list of all repositories with their attributes. Use this operation to discover available repositories and their metadata."""

    # Extract parameters for API call
    _http_path = "/api/v3/repositories"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_repositories")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_repositories", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_repositories",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Get Repository",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_repository(repo_public_id: str = Field(..., alias="repo-public-id", description="The unique public identifier of the repository as a 64-bit integer.")) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific repository using its unique public identifier."""

    _repo_public_id = _parse_int(repo_public_id)

    # Construct request model with validation
    try:
        _request = _models.GetRepositoryRequest(
            path=_models.GetRepositoryRequestPath(repo_public_id=_repo_public_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_repository: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/repositories/{repo-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/repositories/{repo-public-id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_repository")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_repository", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_repository",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Search Epics and Stories",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def search_epics_and_stories(
    query: str = Field(..., description="Search query using supported search operators (see help documentation). Must be at least 1 character long.", min_length=1),
    page_size: str | None = Field(None, description="Number of results per page, between 1 and 250 inclusive. Defaults to a standard page size if not specified."),
    detail: Literal["full", "slim"] | None = Field(None, description="Level of detail in results: 'full' includes all descriptions, comments, and related item details (pull requests, branches, tasks); 'slim' omits large text fields and references related items by ID only. Defaults to 'full'."),
    entity_types: list[Literal["story", "milestone", "epic", "iteration", "objective"]] | None = Field(None, description="Entity types to include in search results. Supports: epic, iteration, objective, story. Defaults to story and epic if not specified. Provide as an array of entity type strings."),
) -> dict[str, Any] | ToolResult:
    """Search for Epics and Stories using search operators and filters. Results are ranked and paginated; use the `next` value from previous responses to maintain stable ordering across pages."""

    _page_size = _parse_int(page_size)

    # Construct request model with validation
    try:
        _request = _models.SearchRequest(
            query=_models.SearchRequestQuery(query=query, page_size=_page_size, detail=detail, entity_types=entity_types)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_epics_and_stories: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v3/search"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_epics_and_stories")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_epics_and_stories", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_epics_and_stories",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Search Documents",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def search_documents(
    title: str = Field(..., description="Search text to match against document titles using fuzzy matching. Must be at least 1 character long.", min_length=1),
    archived: bool | None = Field(None, description="Filter by archive status: true returns archived documents, false returns non-archived documents."),
    created_by_me: bool | None = Field(None, description="Filter by document ownership: true returns documents created by the current user, false returns documents created by others."),
    followed_by_me: bool | None = Field(None, description="Filter by follow status: true returns documents the current user is following, false returns documents not followed."),
    page_size: str | None = Field(None, description="Number of results to return per page. Must be between 1 and 250."),
) -> dict[str, Any] | ToolResult:
    """Search for documents by title with optional filtering by archive status, ownership, and follow status. Supports fuzzy matching on document titles and pagination of results."""

    _page_size = _parse_int(page_size)

    # Construct request model with validation
    try:
        _request = _models.SearchDocumentsRequest(
            query=_models.SearchDocumentsRequestQuery(title=title, archived=archived, created_by_me=created_by_me, followed_by_me=followed_by_me, page_size=_page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_documents: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v3/search/documents"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_documents")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_documents", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_documents",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Search Epics",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def search_epics(
    query: str = Field(..., description="Search query using supported operators (see search operators documentation). Must be at least 1 character long.", min_length=1),
    page_size: str | None = Field(None, description="Number of results per page, between 1 and 250 inclusive. Defaults to a standard page size if not specified."),
    detail: Literal["full", "slim"] | None = Field(None, description="Level of detail in results: 'full' includes all descriptions, comments, and related item details (pull requests, branches, tasks); 'slim' omits large text fields and references related items by ID only. Defaults to 'full'."),
    entity_types: list[Literal["story", "milestone", "epic", "iteration", "objective"]] | None = Field(None, description="Entity types to include in search results. Supports: epic, iteration, objective, story. Defaults to story and epic if not specified."),
) -> dict[str, Any] | ToolResult:
    """Search for epics using query operators and optional filters. Results support pagination via the `next` cursor to maintain stable ordering as the search index evolves."""

    _page_size = _parse_int(page_size)

    # Construct request model with validation
    try:
        _request = _models.SearchEpicsRequest(
            query=_models.SearchEpicsRequestQuery(query=query, page_size=_page_size, detail=detail, entity_types=entity_types)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_epics: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v3/search/epics"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_epics")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_epics", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_epics",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Search Iterations",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def search_iterations(
    query: str = Field(..., description="Search query using supported search operators. Must be at least 1 character long. See search operators documentation for syntax and available filters.", min_length=1),
    page_size: str | None = Field(None, description="Number of results to return per page, between 1 and 250 results. Defaults to a standard page size if not specified."),
    detail: Literal["full", "slim"] | None = Field(None, description="Level of detail in results. Use 'full' for complete data including descriptions, comments, and related item details, or 'slim' to omit large text fields and reference related items by ID only. Defaults to 'full'."),
    entity_types: list[Literal["story", "milestone", "epic", "iteration", "objective"]] | None = Field(None, description="Entity types to include in search results. Accepts multiple types: epic, iteration, objective, or story. Defaults to story and epic if not specified."),
) -> dict[str, Any] | ToolResult:
    """Search for iterations using query operators and filters. Results are ordered by search ranking and can be paginated using the next cursor from previous responses to maintain stable ordering."""

    _page_size = _parse_int(page_size)

    # Construct request model with validation
    try:
        _request = _models.SearchIterationsRequest(
            query=_models.SearchIterationsRequestQuery(query=query, page_size=_page_size, detail=detail, entity_types=entity_types)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_iterations: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v3/search/iterations"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_iterations")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_iterations", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_iterations",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Search Milestones",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def search_milestones(
    query: str = Field(..., description="Search query using supported search operators. Must be at least 1 character long.", min_length=1),
    page_size: str | None = Field(None, description="Number of results per page, between 1 and 250 inclusive. Defaults to a standard page size if not specified."),
    detail: Literal["full", "slim"] | None = Field(None, description="Level of detail in results: 'full' includes all descriptions, comments, and related item details; 'slim' omits large text fields and references related items by ID only. Defaults to 'full'."),
    entity_types: list[Literal["story", "milestone", "epic", "iteration", "objective"]] | None = Field(None, description="Entity types to include in search results. Supports: epic, iteration, objective, story. Defaults to story and epic if not specified. Provide as an array of entity type strings."),
) -> dict[str, Any] | ToolResult:
    """Search for milestones using query operators and filters. Results are paginated and support stable ordering through cursor-based navigation."""

    _page_size = _parse_int(page_size)

    # Construct request model with validation
    try:
        _request = _models.SearchMilestonesRequest(
            query=_models.SearchMilestonesRequestQuery(query=query, page_size=_page_size, detail=detail, entity_types=entity_types)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_milestones: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v3/search/milestones"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_milestones")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_milestones", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_milestones",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Search Objectives",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def search_objectives(
    query: str = Field(..., description="Search query using supported search operators. Must be at least 1 character long. See search operators documentation for syntax details.", min_length=1),
    page_size: str | None = Field(None, description="Number of results to return per page, between 1 and 250 results."),
    detail: Literal["full", "slim"] | None = Field(None, description="Level of detail in results. Use 'full' for complete data including descriptions, comments, and related item details, or 'slim' to omit large text fields and reference related items by ID only. Defaults to 'full'."),
    entity_types: list[Literal["story", "milestone", "epic", "iteration", "objective"]] | None = Field(None, description="Entity types to include in search results. Accepts any combination of: epic, iteration, objective, story. Defaults to story and epic if not specified."),
) -> dict[str, Any] | ToolResult:
    """Search for Objectives using query operators and filters. Results are ranked by relevance and can be paginated using the `next` value from previous responses to maintain stable ordering."""

    _page_size = _parse_int(page_size)

    # Construct request model with validation
    try:
        _request = _models.SearchObjectivesRequest(
            query=_models.SearchObjectivesRequestQuery(query=query, page_size=_page_size, detail=detail, entity_types=entity_types)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_objectives: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v3/search/objectives"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_objectives")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_objectives", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_objectives",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Search Stories",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def search_stories(
    query: str = Field(..., description="Search query using supported operators (see search operators documentation). Must be at least 1 character long.", min_length=1),
    page_size: str | None = Field(None, description="Number of results per page, between 1 and 250 inclusive. Defaults to a standard page size if not specified."),
    detail: Literal["full", "slim"] | None = Field(None, description="Level of detail in results: 'full' includes all descriptions, comments, and related item details; 'slim' omits large text fields and references related items by ID only. Defaults to 'full'."),
    entity_types: list[Literal["story", "milestone", "epic", "iteration", "objective"]] | None = Field(None, description="Entity types to include in search results. Supports: epic, iteration, objective, story. Defaults to story and epic if not specified. Provide as an array of entity type strings."),
) -> dict[str, Any] | ToolResult:
    """Search for stories and related entities using query operators and filters. Results support pagination via the `next` cursor to maintain stable ordering as the search index evolves."""

    _page_size = _parse_int(page_size)

    # Construct request model with validation
    try:
        _request = _models.SearchStoriesRequest(
            query=_models.SearchStoriesRequestQuery(query=query, page_size=_page_size, detail=detail, entity_types=entity_types)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_stories: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v3/search/stories"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_stories")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_stories", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_stories",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Create Story",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_story(
    name: str = Field(..., description="The story's title. Must be between 1 and 512 characters.", min_length=1, max_length=512),
    description: str | None = Field(None, description="The story's description text. Supports up to 100,000 characters.", max_length=100000),
    archived: bool | None = Field(None, description="Whether the story should be archived upon creation."),
    story_links: list[_models.CreateStoryLinkParams] | None = Field(None, description="An array of story links to attach to this story. Each link establishes a relationship between stories."),
    story_type: Literal["feature", "chore", "bug"] | None = Field(None, description="Categorizes the story as a feature, bug, or chore."),
    comments: list[_models.CreateStoryCommentParams] | None = Field(None, description="An array of comments to add to the story immediately upon creation."),
    story_template_id: str | None = Field(None, description="Associates this story with a story template by its UUID. No template content is automatically inherited."),
    sub_tasks: list[_models.LinkSubTaskParams | _models.CreateSubTaskParams] | None = Field(None, description="An array of sub-tasks to create or link. Each entry can reference an existing story or define a new sub-task. Only applicable when the Sub-task feature is enabled."),
    requested_by_id: str | None = Field(None, description="The UUID of the team member who requested this story."),
    iteration_id: str | None = Field(None, description="The numeric ID of the iteration this story belongs to."),
    tasks: list[_models.CreateTaskParams] | None = Field(None, description="An array of tasks to associate with this story."),
    workflow_state_id: str | None = Field(None, description="The numeric ID of the workflow state for this story. Either this or project_id must be provided, but not both."),
    external_id: str | None = Field(None, description="An external identifier for this story, useful when importing from other tools. Supports up to 1,024 characters.", max_length=1024),
    parent_story_id: str | None = Field(None, description="The numeric ID of the parent story, making this story a sub-task. Only applicable when the Sub-task feature is enabled."),
    estimate: str | None = Field(None, description="The point estimate for this story's complexity. Can be null to leave unestimated."),
    deadline: str | None = Field(None, description="The story's due date in ISO 8601 format."),
) -> dict[str, Any] | ToolResult:
    """Create a new story in your Shortcut workspace. You must specify either a workflow_state_id or project_id (but not both); workflow_state_id is recommended as projects are being sunset."""

    _iteration_id = _parse_int(iteration_id)
    _workflow_state_id = _parse_int(workflow_state_id)
    _parent_story_id = _parse_int(parent_story_id)
    _estimate = _parse_int(estimate)

    # Construct request model with validation
    try:
        _request = _models.CreateStoryRequest(
            body=_models.CreateStoryRequestBody(description=description, archived=archived, story_links=story_links, story_type=story_type, name=name, comments=comments, story_template_id=story_template_id, sub_tasks=sub_tasks, requested_by_id=requested_by_id, iteration_id=_iteration_id, tasks=tasks, workflow_state_id=_workflow_state_id, external_id=external_id, parent_story_id=_parent_story_id, estimate=_estimate, deadline=deadline)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_story: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v3/stories"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_story")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_story", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_story",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Create Stories",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_stories(stories: list[_models.CreateStoryParams] = Field(..., description="An array of story objects to create. Each story object uses the same schema as individual story creation. Order is preserved in processing.")) -> dict[str, Any] | ToolResult:
    """Create multiple stories in a single batch request. Each story is created with the same configuration options available in individual story creation."""

    # Construct request model with validation
    try:
        _request = _models.CreateMultipleStoriesRequest(
            body=_models.CreateMultipleStoriesRequestBody(stories=stories)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_stories: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v3/stories/bulk"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_stories")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_stories", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_stories",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Update Multiple Stories",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def update_multiple_stories(
    story_ids: Annotated[list[int], AfterValidator(_check_unique_items)] = Field(..., description="The unique identifiers of the stories to update. Required to specify which stories are affected by this bulk operation."),
    archived: bool | None = Field(None, description="Archive or unarchive the selected stories."),
    story_type: Literal["feature", "chore", "bug"] | None = Field(None, description="Classify the story as a feature request, bug fix, or chore. Must be one of: feature, chore, or bug."),
    follower_ids_add: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(None, description="UUIDs of team members to add as followers to the stories. Followers receive notifications about story updates."),
    follower_ids_remove: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(None, description="UUIDs of team members to remove from the stories' followers list."),
    requested_by_id: str | None = Field(None, description="UUID of the team member who requested the story."),
    iteration_id: str | None = Field(None, description="The iteration or sprint ID to assign the stories to."),
    custom_fields_remove: list[_models.CustomFieldValueParams] | None = Field(None, description="Custom field values to remove from the stories. Specify as a map of CustomField ID to CustomFieldEnumValue ID."),
    labels_add: list[_models.CreateLabelParams] | None = Field(None, description="Labels to add to the stories. Provide as an array of label identifiers or names."),
    workflow_state_id: str | None = Field(None, description="The workflow state ID representing the status to move the stories to (e.g., backlog, in progress, done)."),
    estimate: str | None = Field(None, description="Point estimate for story complexity and effort. Use null to mark stories as unestimated."),
    owner_ids_remove: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(None, description="UUIDs of team members to remove as owners from the stories."),
    custom_fields_add: list[_models.CustomFieldValueParams] | None = Field(None, description="Custom field values to add to the stories. Specify as a map of CustomField ID to CustomFieldEnumValue ID."),
    labels_remove: list[_models.CreateLabelParams] | None = Field(None, description="Labels to remove from the stories. Provide as an array of label identifiers or names."),
    deadline: str | None = Field(None, description="The due date for the stories in ISO 8601 date-time format."),
    owner_ids_add: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(None, description="UUIDs of team members to add as owners to the stories. Owners are responsible for completing the work."),
) -> dict[str, Any] | ToolResult:
    """Bulk update multiple stories with changes to properties like status, assignments, estimates, and metadata. Apply changes across numerous stories simultaneously to streamline project management workflows."""

    _iteration_id = _parse_int(iteration_id)
    _workflow_state_id = _parse_int(workflow_state_id)
    _estimate = _parse_int(estimate)

    # Construct request model with validation
    try:
        _request = _models.UpdateMultipleStoriesRequest(
            body=_models.UpdateMultipleStoriesRequestBody(archived=archived, story_ids=story_ids, story_type=story_type, follower_ids_add=follower_ids_add, follower_ids_remove=follower_ids_remove, requested_by_id=requested_by_id, iteration_id=_iteration_id, custom_fields_remove=custom_fields_remove, labels_add=labels_add, workflow_state_id=_workflow_state_id, estimate=_estimate, owner_ids_remove=owner_ids_remove, custom_fields_add=custom_fields_add, labels_remove=labels_remove, deadline=deadline, owner_ids_add=owner_ids_add)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_multiple_stories: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v3/stories/bulk"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_multiple_stories")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_multiple_stories", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_multiple_stories",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Delete Stories in Bulk",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_stories_bulk(story_ids: Annotated[list[int], AfterValidator(_check_unique_items)] = Field(..., description="A list of story IDs to delete. Provide the IDs as an array of strings or numbers representing the stories you want to remove. All stories must be archived before deletion.")) -> dict[str, Any] | ToolResult:
    """Permanently delete multiple archived stories in a single operation. This bulk deletion operation allows you to remove several stories at once by providing their IDs."""

    # Construct request model with validation
    try:
        _request = _models.DeleteMultipleStoriesRequest(
            body=_models.DeleteMultipleStoriesRequestBody(story_ids=story_ids)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_stories_bulk: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v3/stories/bulk"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_stories_bulk")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_stories_bulk", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_stories_bulk",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Create Story from Template",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_story_from_template(
    story_template_id: str = Field(..., description="The UUID of the story template to use as the basis for this story. Required."),
    description: str | None = Field(None, description="The story's description text. Limited to 100,000 characters.", max_length=100000),
    archived: bool | None = Field(None, description="Whether the story should be archived. Defaults to false if not specified."),
    story_links: list[_models.CreateStoryLinkParams] | None = Field(None, description="An array of story links to attach to this story, establishing relationships with other stories."),
    external_links_add: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(None, description="An array of external links to add to the story in addition to any provided by the template. Cannot be combined with external_links_remove."),
    story_type: Literal["feature", "chore", "bug"] | None = Field(None, description="The story's type classification. Must be one of: feature, chore, or bug."),
    name: str | None = Field(None, description="The story's title. Required if the template does not provide a name. Must be between 1 and 512 characters.", min_length=1, max_length=512),
    file_ids_add: Annotated[list[int], AfterValidator(_check_unique_items)] | None = Field(None, description="An array of file IDs to attach to the story in addition to files from the template. Cannot be combined with file_ids_remove."),
    file_ids_remove: Annotated[list[int], AfterValidator(_check_unique_items)] | None = Field(None, description="An array of file IDs to remove from the template's attached files. Cannot be combined with file_ids_add."),
    comments: list[_models.CreateStoryCommentParams] | None = Field(None, description="An array of comment objects to add to the story upon creation."),
    follower_ids_add: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(None, description="An array of member UUIDs to add as followers in addition to followers from the template. Cannot be combined with follower_ids_remove."),
    follower_ids_remove: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(None, description="An array of member UUIDs to remove from the template's followers. Cannot be combined with follower_ids_add."),
    sub_tasks: list[_models.LinkSubTaskParams | _models.CreateSubTaskParams] | None = Field(None, description="An array of sub-task definitions to associate with the story. Each entry can link to an existing story or create a new sub-task. Only applicable when the Sub-task feature is enabled."),
    linked_file_ids_remove: Annotated[list[int], AfterValidator(_check_unique_items)] | None = Field(None, description="An array of linked file IDs to remove from the template's linked files. Cannot be combined with linked_file_ids_add."),
    requested_by_id: str | None = Field(None, description="The UUID of the workspace member who requested this story."),
    iteration_id: str | None = Field(None, description="The numeric ID of the iteration (sprint) this story belongs to."),
    custom_fields_remove: Annotated[list[_models.RemoveCustomFieldParams], AfterValidator(_check_unique_items)] | None = Field(None, description="An array of custom field IDs to remove from the template's custom field values. Cannot be combined with custom_fields_add."),
    tasks: list[_models.CreateTaskParams] | None = Field(None, description="An array of task objects to create and associate with the story."),
    labels_add: Annotated[list[_models.CreateLabelParams], AfterValidator(_check_unique_items)] | None = Field(None, description="An array of label names or IDs to add to the story in addition to labels from the template. Cannot be combined with labels_remove."),
    workflow_state_id: str | None = Field(None, description="The numeric ID of the workflow state this story should be placed in."),
    external_id: str | None = Field(None, description="An external identifier for this story, useful when importing from other tools. Limited to 1,024 characters.", max_length=1024),
    parent_story_id: str | None = Field(None, description="The numeric ID of the parent story, making this story a sub-task. Only applicable when the Sub-task feature is enabled."),
    estimate: str | None = Field(None, description="The numeric point estimate for story complexity. Can be null to leave unestimated."),
    owner_ids_remove: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(None, description="An array of member UUIDs to remove from the template's owners. Cannot be combined with owner_ids_add."),
    custom_fields_add: Annotated[list[_models.CustomFieldValueParams], AfterValidator(_check_unique_items)] | None = Field(None, description="An array of custom field assignments, each specifying a custom field ID and its enum value. These are added to template values. Cannot be combined with custom_fields_remove."),
    linked_file_ids_add: Annotated[list[int], AfterValidator(_check_unique_items)] | None = Field(None, description="An array of linked file IDs to attach to the story in addition to files from the template. Cannot be combined with linked_file_ids_remove."),
    labels_remove: Annotated[list[_models.RemoveLabelParams], AfterValidator(_check_unique_items)] | None = Field(None, description="An array of label names or IDs to remove from the template's labels. Cannot be combined with labels_add."),
    deadline: str | None = Field(None, description="The story's due date in ISO 8601 format (e.g., 2024-12-31T23:59:59Z)."),
    owner_ids_add: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(None, description="An array of member UUIDs to add as owners in addition to owners from the template. Cannot be combined with owner_ids_remove."),
    external_links_remove: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(None, description="An array of external links to remove from the template's external links. Cannot be combined with external_links_add."),
) -> dict[str, Any] | ToolResult:
    """Create a new story in your Shortcut workspace based on a story template, with the ability to customize or override template values for all story attributes."""

    _iteration_id = _parse_int(iteration_id)
    _workflow_state_id = _parse_int(workflow_state_id)
    _parent_story_id = _parse_int(parent_story_id)
    _estimate = _parse_int(estimate)

    # Construct request model with validation
    try:
        _request = _models.CreateStoryFromTemplateRequest(
            body=_models.CreateStoryFromTemplateRequestBody(description=description, archived=archived, story_links=story_links, external_links_add=external_links_add, story_type=story_type, name=name, file_ids_add=file_ids_add, file_ids_remove=file_ids_remove, comments=comments, follower_ids_add=follower_ids_add, story_template_id=story_template_id, follower_ids_remove=follower_ids_remove, sub_tasks=sub_tasks, linked_file_ids_remove=linked_file_ids_remove, requested_by_id=requested_by_id, iteration_id=_iteration_id, custom_fields_remove=custom_fields_remove, tasks=tasks, labels_add=labels_add, workflow_state_id=_workflow_state_id, external_id=external_id, parent_story_id=_parent_story_id, estimate=_estimate, owner_ids_remove=owner_ids_remove, custom_fields_add=custom_fields_add, linked_file_ids_add=linked_file_ids_add, labels_remove=labels_remove, deadline=deadline, owner_ids_add=owner_ids_add, external_links_remove=external_links_remove)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_story_from_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v3/stories/from-template"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_story_from_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_story_from_template", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_story_from_template",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Search Stories Advanced",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def search_stories_advanced(
    archived: bool | None = Field(None, description="Filter to include or exclude archived Stories."),
    story_type: Literal["feature", "chore", "bug"] | None = Field(None, description="Filter Stories by type: feature, chore, or bug."),
    epic_ids: Annotated[list[int], AfterValidator(_check_unique_items)] | None = Field(None, description="Filter Stories associated with one or more Epics by their IDs."),
    project_ids: Annotated[list[int | None], AfterValidator(_check_unique_items)] | None = Field(None, description="Filter Stories assigned to one or more Projects by their IDs."),
    updated_at_end: str | None = Field(None, description="Filter Stories updated on or before this date (ISO 8601 format)."),
    completed_at_end: str | None = Field(None, description="Filter Stories completed on or before this date (ISO 8601 format)."),
    workflow_state_types: list[Literal["started", "backlog", "unstarted", "done"]] | None = Field(None, description="Filter Stories by Workflow State type (e.g., started, completed, unstarted)."),
    deadline_end: str | None = Field(None, description="Filter Stories with a deadline on or before this date (ISO 8601 format)."),
    created_at_start: str | None = Field(None, description="Filter Stories created on or after this date (ISO 8601 format)."),
    label_name: str | None = Field(None, description="Filter Stories by associated Label name (minimum 1 character).", min_length=1),
    requested_by_id: str | None = Field(None, description="Filter Stories requested by a specific User (UUID format)."),
    iteration_id: str | None = Field(None, description="Filter Stories associated with a specific Iteration by its ID."),
    label_ids: Annotated[list[int], AfterValidator(_check_unique_items)] | None = Field(None, description="Filter Stories associated with one or more Labels by their IDs."),
    workflow_state_id: str | None = Field(None, description="Filter Stories in a specific Workflow State by its unique ID."),
    iteration_ids: Annotated[list[int], AfterValidator(_check_unique_items)] | None = Field(None, description="Filter Stories associated with one or more Iterations by their IDs."),
    created_at_end: str | None = Field(None, description="Filter Stories created on or before this date (ISO 8601 format)."),
    deadline_start: str | None = Field(None, description="Filter Stories with a deadline on or after this date (ISO 8601 format)."),
    group_ids: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(None, description="Filter Stories associated with one or more Groups by their IDs."),
    external_id: str | None = Field(None, description="Filter Stories by external resource reference ID or URL (up to 1024 characters), useful for tracking imported items.", max_length=1024),
    includes_description: bool | None = Field(None, description="Include the full story description text in the response when true."),
    estimate: str | None = Field(None, description="Filter Stories by estimate points (whole number)."),
    completed_at_start: str | None = Field(None, description="Filter Stories completed on or after this date (ISO 8601 format)."),
    updated_at_start: str | None = Field(None, description="Filter Stories updated on or after this date (ISO 8601 format)."),
) -> dict[str, Any] | ToolResult:
    """Search and filter Stories across projects using flexible criteria including type, status, dates, assignments, and metadata. Returns matching Stories with optional description content."""

    _iteration_id = _parse_int(iteration_id)
    _workflow_state_id = _parse_int(workflow_state_id)
    _estimate = _parse_int(estimate)

    # Construct request model with validation
    try:
        _request = _models.QueryStoriesRequest(
            body=_models.QueryStoriesRequestBody(archived=archived, story_type=story_type, epic_ids=epic_ids, project_ids=project_ids, updated_at_end=updated_at_end, completed_at_end=completed_at_end, workflow_state_types=workflow_state_types, deadline_end=deadline_end, created_at_start=created_at_start, label_name=label_name, requested_by_id=requested_by_id, iteration_id=_iteration_id, label_ids=label_ids, workflow_state_id=_workflow_state_id, iteration_ids=iteration_ids, created_at_end=created_at_end, deadline_start=deadline_start, group_ids=group_ids, external_id=external_id, includes_description=includes_description, estimate=_estimate, completed_at_start=completed_at_start, updated_at_start=updated_at_start)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_stories_advanced: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v3/stories/search"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_stories_advanced")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_stories_advanced", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_stories_advanced",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Get Story",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_story(story_public_id: str = Field(..., alias="story-public-id", description="The unique public identifier for the story. Must be a valid 64-bit integer.")) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific story by its public ID. Returns the story's metadata and content."""

    _story_public_id = _parse_int(story_public_id)

    # Construct request model with validation
    try:
        _request = _models.GetStoryRequest(
            path=_models.GetStoryRequestPath(story_public_id=_story_public_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_story: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/stories/{story-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/stories/{story-public-id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_story")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_story", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_story",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Update Story",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def update_story(
    story_public_id: str = Field(..., alias="story-public-id", description="The unique identifier of the story to update. This is a 64-bit integer that uniquely identifies the story within the system."),
    description: str | None = Field(None, description="A detailed description of the story, up to 100,000 characters in length.", max_length=100000),
    archived: bool | None = Field(None, description="Whether the story is archived. Set to true to archive the story or false to unarchive it."),
    pull_request_ids: Annotated[list[int], AfterValidator(_check_unique_items)] | None = Field(None, description="An array of pull or merge request IDs to attach to this story. The order and specific format depend on your version control system integration."),
    story_type: Literal["feature", "chore", "bug"] | None = Field(None, description="The category of work this story represents: 'feature' for new functionality, 'bug' for defects, or 'chore' for maintenance tasks."),
    name: str | None = Field(None, description="The title of the story, between 1 and 512 characters in length.", min_length=1, max_length=512),
    branch_ids: Annotated[list[int], AfterValidator(_check_unique_items)] | None = Field(None, description="An array of branch IDs to attach to this story. The order and specific format depend on your version control system integration."),
    commit_ids: Annotated[list[int], AfterValidator(_check_unique_items)] | None = Field(None, description="An array of commit IDs to attach to this story. The order and specific format depend on your version control system integration."),
    sub_tasks: list[_models.LinkSubTaskParams] | None = Field(None, description="An array of story IDs to set as sub-tasks of this story. This represents the complete final state—stories not in this list will be unlinked, new stories will be linked, and the array order determines sub-task positions."),
    requested_by_id: str | None = Field(None, description="The UUID of the team member who requested this story."),
    iteration_id: str | None = Field(None, description="The 64-bit integer ID of the iteration (sprint or planning cycle) this story belongs to."),
    workflow_state_id: str | None = Field(None, description="The 64-bit integer ID of the workflow state to move this story into (e.g., 'To Do', 'In Progress', 'Done')."),
    parent_story_id: str | None = Field(None, description="The 64-bit integer ID of the parent story, making this story a sub-task. Set to null to remove the parent relationship and make this story independent."),
    estimate: str | None = Field(None, description="The point estimate for this story as a 64-bit integer, or null to mark the story as unestimated."),
    deadline: str | None = Field(None, description="The due date for this story in ISO 8601 date-time format."),
) -> dict[str, Any] | ToolResult:
    """Update one or more properties of an existing story, including its metadata, relationships, and workflow state. Changes are applied immediately and replace the current values for any fields provided."""

    _story_public_id = _parse_int(story_public_id)
    _iteration_id = _parse_int(iteration_id)
    _workflow_state_id = _parse_int(workflow_state_id)
    _parent_story_id = _parse_int(parent_story_id)
    _estimate = _parse_int(estimate)

    # Construct request model with validation
    try:
        _request = _models.UpdateStoryRequest(
            path=_models.UpdateStoryRequestPath(story_public_id=_story_public_id),
            body=_models.UpdateStoryRequestBody(description=description, archived=archived, pull_request_ids=pull_request_ids, story_type=story_type, name=name, branch_ids=branch_ids, commit_ids=commit_ids, sub_tasks=sub_tasks, requested_by_id=requested_by_id, iteration_id=_iteration_id, workflow_state_id=_workflow_state_id, parent_story_id=_parent_story_id, estimate=_estimate, deadline=deadline)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_story: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/stories/{story-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/stories/{story-public-id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_story")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_story", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_story",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Delete Story",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_story(story_public_id: str = Field(..., alias="story-public-id", description="The unique public identifier of the story to delete. Must be a valid 64-bit integer.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a story by its public ID. This action cannot be undone."""

    _story_public_id = _parse_int(story_public_id)

    # Construct request model with validation
    try:
        _request = _models.DeleteStoryRequest(
            path=_models.DeleteStoryRequestPath(story_public_id=_story_public_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_story: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/stories/{story-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/stories/{story-public-id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_story")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_story", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_story",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="List Story Comments",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_story_comments(story_public_id: str = Field(..., alias="story-public-id", description="The unique identifier of the story. Must be a positive integer value.")) -> dict[str, Any] | ToolResult:
    """Retrieves all comments associated with a specific story. Use this to fetch the complete list of comments for a given story."""

    _story_public_id = _parse_int(story_public_id)

    # Construct request model with validation
    try:
        _request = _models.ListStoryCommentRequest(
            path=_models.ListStoryCommentRequestPath(story_public_id=_story_public_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_story_comments: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/stories/{story-public-id}/comments", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/stories/{story-public-id}/comments"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_story_comments")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_story_comments", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_story_comments",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Create Story Comment",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_story_comment(
    story_public_id: str = Field(..., alias="story-public-id", description="The unique identifier of the story where the comment will be posted. Must be a valid 64-bit integer."),
    text: str = Field(..., description="The comment text content. Supports up to 100,000 characters.", max_length=100000),
    author_id: str | None = Field(None, description="The UUID of the team member authoring the comment. If not provided, defaults to the user associated with the API token."),
    external_id: str | None = Field(None, description="An external identifier for the comment, useful when migrating comments from other tools. Maximum length is 1,024 characters.", max_length=1024),
    parent_id: str | None = Field(None, description="The ID of the parent comment to thread this comment under as a reply. If omitted, the comment will be a top-level comment on the story."),
) -> dict[str, Any] | ToolResult:
    """Add a comment to a story. Comments can be standalone or threaded as replies to existing comments."""

    _story_public_id = _parse_int(story_public_id)
    _parent_id = _parse_int(parent_id)

    # Construct request model with validation
    try:
        _request = _models.CreateStoryCommentRequest(
            path=_models.CreateStoryCommentRequestPath(story_public_id=_story_public_id),
            body=_models.CreateStoryCommentRequestBody(text=text, author_id=author_id, external_id=external_id, parent_id=_parent_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_story_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/stories/{story-public-id}/comments", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/stories/{story-public-id}/comments"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_story_comment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_story_comment", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_story_comment",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Get Story Comment",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_story_comment(
    story_public_id: str = Field(..., alias="story-public-id", description="The unique identifier of the story containing the comment. Must be a positive integer."),
    comment_public_id: str = Field(..., alias="comment-public-id", description="The unique identifier of the comment to retrieve. Must be a positive integer."),
) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific comment within a story. Use this to fetch comment data by providing both the story and comment identifiers."""

    _story_public_id = _parse_int(story_public_id)
    _comment_public_id = _parse_int(comment_public_id)

    # Construct request model with validation
    try:
        _request = _models.GetStoryCommentRequest(
            path=_models.GetStoryCommentRequestPath(story_public_id=_story_public_id, comment_public_id=_comment_public_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_story_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/stories/{story-public-id}/comments/{comment-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/stories/{story-public-id}/comments/{comment-public-id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_story_comment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_story_comment", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_story_comment",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Update Story Comment",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_story_comment(
    story_public_id: str = Field(..., alias="story-public-id", description="The unique identifier of the story containing the comment to update."),
    comment_public_id: str = Field(..., alias="comment-public-id", description="The unique identifier of the comment to update."),
    text: str = Field(..., description="The new comment text content, up to 100,000 characters in length.", max_length=100000),
) -> dict[str, Any] | ToolResult:
    """Update the text content of an existing comment within a story. The comment text can be up to 100,000 characters."""

    _story_public_id = _parse_int(story_public_id)
    _comment_public_id = _parse_int(comment_public_id)

    # Construct request model with validation
    try:
        _request = _models.UpdateStoryCommentRequest(
            path=_models.UpdateStoryCommentRequestPath(story_public_id=_story_public_id, comment_public_id=_comment_public_id),
            body=_models.UpdateStoryCommentRequestBody(text=text)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_story_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/stories/{story-public-id}/comments/{comment-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/stories/{story-public-id}/comments/{comment-public-id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_story_comment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_story_comment", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_story_comment",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Delete Story Comment",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_story_comment(
    story_public_id: str = Field(..., alias="story-public-id", description="The unique identifier of the story containing the comment to delete. Must be a positive integer."),
    comment_public_id: str = Field(..., alias="comment-public-id", description="The unique identifier of the comment to delete. Must be a positive integer."),
) -> dict[str, Any] | ToolResult:
    """Remove a comment from a story. This permanently deletes the specified comment and cannot be undone."""

    _story_public_id = _parse_int(story_public_id)
    _comment_public_id = _parse_int(comment_public_id)

    # Construct request model with validation
    try:
        _request = _models.DeleteStoryCommentRequest(
            path=_models.DeleteStoryCommentRequestPath(story_public_id=_story_public_id, comment_public_id=_comment_public_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_story_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/stories/{story-public-id}/comments/{comment-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/stories/{story-public-id}/comments/{comment-public-id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_story_comment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_story_comment", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_story_comment",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Add Reaction to Story Comment",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def add_reaction_to_story_comment(
    story_public_id: str = Field(..., alias="story-public-id", description="The unique identifier of the story containing the comment. Must be a positive integer."),
    comment_public_id: str = Field(..., alias="comment-public-id", description="The unique identifier of the comment to react to. Must be a positive integer."),
    emoji: str = Field(..., description="The emoji short-code to add or remove as a reaction (e.g., `:thumbsup::skin-tone-4:`, `:heart:`, `:laughing:`). Use standard emoji short-code format with colons."),
) -> dict[str, Any] | ToolResult:
    """Add an emoji reaction to a comment on a story. Use emoji short-codes (e.g., `:thumbsup::skin-tone-4:`) to express reactions."""

    _story_public_id = _parse_int(story_public_id)
    _comment_public_id = _parse_int(comment_public_id)

    # Construct request model with validation
    try:
        _request = _models.CreateStoryReactionRequest(
            path=_models.CreateStoryReactionRequestPath(story_public_id=_story_public_id, comment_public_id=_comment_public_id),
            body=_models.CreateStoryReactionRequestBody(emoji=emoji)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_reaction_to_story_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/stories/{story-public-id}/comments/{comment-public-id}/reactions", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/stories/{story-public-id}/comments/{comment-public-id}/reactions"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_reaction_to_story_comment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_reaction_to_story_comment", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_reaction_to_story_comment",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Remove Reaction From Story Comment",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def remove_reaction_from_story_comment(
    story_public_id: str = Field(..., alias="story-public-id", description="The unique identifier of the story containing the comment. Must be a positive integer."),
    comment_public_id: str = Field(..., alias="comment-public-id", description="The unique identifier of the comment from which to remove the reaction. Must be a positive integer."),
    emoji: str = Field(..., description="The emoji short-code to remove, formatted as a colon-delimited code (e.g., `:thumbsup:` or `:thumbsup::skin-tone-4:` for variants with modifiers)."),
) -> dict[str, Any] | ToolResult:
    """Remove a reaction (emoji) from a comment on a story. Specify the story, comment, and emoji to delete the reaction."""

    _story_public_id = _parse_int(story_public_id)
    _comment_public_id = _parse_int(comment_public_id)

    # Construct request model with validation
    try:
        _request = _models.DeleteStoryReactionRequest(
            path=_models.DeleteStoryReactionRequestPath(story_public_id=_story_public_id, comment_public_id=_comment_public_id),
            body=_models.DeleteStoryReactionRequestBody(emoji=emoji)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_reaction_from_story_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/stories/{story-public-id}/comments/{comment-public-id}/reactions", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/stories/{story-public-id}/comments/{comment-public-id}/reactions"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_reaction_from_story_comment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_reaction_from_story_comment", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_reaction_from_story_comment",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Remove Comment Slack Link",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def remove_comment_slack_link(
    story_public_id: str = Field(..., alias="story-public-id", description="The unique identifier of the Story containing the comment to unlink. Must be a positive integer."),
    comment_public_id: str = Field(..., alias="comment-public-id", description="The unique identifier of the Comment to unlink from Slack. Must be a positive integer."),
) -> dict[str, Any] | ToolResult:
    """Unlinks a comment from its associated Slack thread, stopping synchronization of replies between the comment thread and Slack."""

    _story_public_id = _parse_int(story_public_id)
    _comment_public_id = _parse_int(comment_public_id)

    # Construct request model with validation
    try:
        _request = _models.UnlinkCommentThreadFromSlackRequest(
            path=_models.UnlinkCommentThreadFromSlackRequestPath(story_public_id=_story_public_id, comment_public_id=_comment_public_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_comment_slack_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/stories/{story-public-id}/comments/{comment-public-id}/unlink-from-slack", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/stories/{story-public-id}/comments/{comment-public-id}/unlink-from-slack"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_comment_slack_link")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_comment_slack_link", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_comment_slack_link",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Get Story History",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_story_history(story_public_id: str = Field(..., alias="story-public-id", description="The unique identifier of the story. Must be a valid 64-bit integer representing the story's public ID.")) -> dict[str, Any] | ToolResult:
    """Retrieve the complete history of changes for a specific story, including all revisions and modifications over time."""

    _story_public_id = _parse_int(story_public_id)

    # Construct request model with validation
    try:
        _request = _models.StoryHistoryRequest(
            path=_models.StoryHistoryRequestPath(story_public_id=_story_public_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_story_history: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/stories/{story-public-id}/history", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/stories/{story-public-id}/history"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_story_history")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_story_history", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_story_history",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="List Story Sub-Tasks",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_story_sub_tasks(story_public_id: str = Field(..., alias="story-public-id", description="The unique identifier of the parent story. Must be a valid 64-bit integer.")) -> dict[str, Any] | ToolResult:
    """Retrieve all sub-task stories associated with a parent story. Returns a complete list of child tasks for the specified story."""

    _story_public_id = _parse_int(story_public_id)

    # Construct request model with validation
    try:
        _request = _models.ListStorySubTasksRequest(
            path=_models.ListStorySubTasksRequestPath(story_public_id=_story_public_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_story_sub_tasks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/stories/{story-public-id}/sub-tasks", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/stories/{story-public-id}/sub-tasks"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_story_sub_tasks")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_story_sub_tasks", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_story_sub_tasks",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Create Task in Story",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_task_in_story(
    story_public_id: str = Field(..., alias="story-public-id", description="The unique identifier of the Story where the task will be created. Must be a valid 64-bit integer."),
    description: str = Field(..., description="A text description of the task. Must be between 1 and 2048 characters.", min_length=1, max_length=2048),
    complete: bool | None = Field(None, description="Optional boolean flag to set the task's completion status. Defaults to false (incomplete) if not provided."),
    external_id: str | None = Field(None, description="Optional identifier for linking this task to an external system or tool. Useful when importing tasks from other platforms. Maximum length is 128 characters.", max_length=128),
) -> dict[str, Any] | ToolResult:
    """Create a new task within a Story. Tasks are actionable items that can be marked complete and optionally linked to external systems via an external ID."""

    _story_public_id = _parse_int(story_public_id)

    # Construct request model with validation
    try:
        _request = _models.CreateTaskRequest(
            path=_models.CreateTaskRequestPath(story_public_id=_story_public_id),
            body=_models.CreateTaskRequestBody(description=description, complete=complete, external_id=external_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_task_in_story: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/stories/{story-public-id}/tasks", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/stories/{story-public-id}/tasks"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_task_in_story")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_task_in_story", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_task_in_story",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Get Task",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_task(
    story_public_id: str = Field(..., alias="story-public-id", description="The unique identifier of the Story that contains the Task. Must be a positive integer."),
    task_public_id: str = Field(..., alias="task-public-id", description="The unique identifier of the Task to retrieve. Must be a positive integer."),
) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific Task within a Story. Returns the Task's properties and metadata."""

    _story_public_id = _parse_int(story_public_id)
    _task_public_id = _parse_int(task_public_id)

    # Construct request model with validation
    try:
        _request = _models.GetTaskRequest(
            path=_models.GetTaskRequestPath(story_public_id=_story_public_id, task_public_id=_task_public_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_task: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/stories/{story-public-id}/tasks/{task-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/stories/{story-public-id}/tasks/{task-public-id}"
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


@mcp.tool(
    title="Update Task",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def update_task(
    story_public_id: str = Field(..., alias="story-public-id", description="The unique identifier of the parent story containing the task. Must be a positive integer."),
    task_public_id: str = Field(..., alias="task-public-id", description="The unique identifier of the task to update. Must be a positive integer."),
    description: str | None = Field(None, description="The task's description text. Must be between 1 and 2048 characters long.", min_length=1, max_length=2048),
    complete: bool | None = Field(None, description="Whether the task is complete. Set to true to mark the task as done, or false to mark it as incomplete."),
) -> dict[str, Any] | ToolResult:
    """Update properties of a specific task within a story, such as its description or completion status."""

    _story_public_id = _parse_int(story_public_id)
    _task_public_id = _parse_int(task_public_id)

    # Construct request model with validation
    try:
        _request = _models.UpdateTaskRequest(
            path=_models.UpdateTaskRequestPath(story_public_id=_story_public_id, task_public_id=_task_public_id),
            body=_models.UpdateTaskRequestBody(description=description, complete=complete)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_task: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/stories/{story-public-id}/tasks/{task-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/stories/{story-public-id}/tasks/{task-public-id}"
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
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Delete Task",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_task(
    story_public_id: str = Field(..., alias="story-public-id", description="The unique identifier of the Story containing the Task to delete. Must be a positive integer."),
    task_public_id: str = Field(..., alias="task-public-id", description="The unique identifier of the Task to delete. Must be a positive integer."),
) -> dict[str, Any] | ToolResult:
    """Permanently delete a Task from a Story. This operation removes the Task and all associated data."""

    _story_public_id = _parse_int(story_public_id)
    _task_public_id = _parse_int(task_public_id)

    # Construct request model with validation
    try:
        _request = _models.DeleteTaskRequest(
            path=_models.DeleteTaskRequestPath(story_public_id=_story_public_id, task_public_id=_task_public_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_task: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/stories/{story-public-id}/tasks/{task-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/stories/{story-public-id}/tasks/{task-public-id}"
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


@mcp.tool(
    title="Create Story Link",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_story_link(
    verb: Literal["blocks", "duplicates", "relates to"] = Field(..., description="The relationship type expressed as an active voice verb. Must be one of: 'blocks' (subject prevents object from progressing), 'duplicates' (subject and object represent identical work), or 'relates to' (subject has a general association with object)."),
    subject_id: str = Field(..., description="The numeric ID of the story performing the action (the subject of the relationship)."),
    object_id: str = Field(..., description="The numeric ID of the story being acted upon (the object of the relationship)."),
) -> dict[str, Any] | ToolResult:
    """Create a semantic relationship between two stories by specifying how one story acts upon another. The subject story performs an action (blocks, duplicates, or relates to) on the object story, establishing a directional dependency or association."""

    _subject_id = _parse_int(subject_id)
    _object_id = _parse_int(object_id)

    # Construct request model with validation
    try:
        _request = _models.CreateStoryLinkRequest(
            body=_models.CreateStoryLinkRequestBody(verb=verb, subject_id=_subject_id, object_id=_object_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_story_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v3/story-links"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_story_link")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_story_link", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_story_link",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Get Story Link",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_story_link(story_link_public_id: str = Field(..., alias="story-link-public-id", description="The unique identifier of the story link to retrieve. Must be a positive integer.")) -> dict[str, Any] | ToolResult:
    """Retrieves a specific story link and the stories it connects, along with their relationship details. Use this to understand how stories are related to each other."""

    _story_link_public_id = _parse_int(story_link_public_id)

    # Construct request model with validation
    try:
        _request = _models.GetStoryLinkRequest(
            path=_models.GetStoryLinkRequestPath(story_link_public_id=_story_link_public_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_story_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/story-links/{story-link-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/story-links/{story-link-public-id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_story_link")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_story_link", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_story_link",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Update Story Link",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_story_link(
    story_link_public_id: str = Field(..., alias="story-link-public-id", description="The unique identifier of the story link to update. Must be a positive integer."),
    verb: Literal["blocks", "duplicates", "relates to"] | None = Field(None, description="The type of relationship between the stories. Choose from: blocks (one story blocks another), duplicates (stories are duplicates), or relates to (general relationship)."),
    subject_id: str | None = Field(None, description="The ID of the subject story in the relationship. Must be a positive integer if provided."),
    object_id: str | None = Field(None, description="The ID of the object story in the relationship. Must be a positive integer if provided."),
) -> dict[str, Any] | ToolResult:
    """Updates the relationship type and/or the connected stories for an existing story link. Modify how two stories are related or change which stories are linked together."""

    _story_link_public_id = _parse_int(story_link_public_id)
    _subject_id = _parse_int(subject_id)
    _object_id = _parse_int(object_id)

    # Construct request model with validation
    try:
        _request = _models.UpdateStoryLinkRequest(
            path=_models.UpdateStoryLinkRequestPath(story_link_public_id=_story_link_public_id),
            body=_models.UpdateStoryLinkRequestBody(verb=verb, subject_id=_subject_id, object_id=_object_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_story_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/story-links/{story-link-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/story-links/{story-link-public-id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_story_link")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_story_link", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_story_link",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Delete Story Link",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_story_link(story_link_public_id: str = Field(..., alias="story-link-public-id", description="The unique identifier of the Story Link to delete. This is a 64-bit integer that uniquely identifies the relationship between stories.")) -> dict[str, Any] | ToolResult:
    """Removes the relationship between two stories by deleting the specified Story Link. This operation severs the connection without affecting the individual stories themselves."""

    _story_link_public_id = _parse_int(story_link_public_id)

    # Construct request model with validation
    try:
        _request = _models.DeleteStoryLinkRequest(
            path=_models.DeleteStoryLinkRequestPath(story_link_public_id=_story_link_public_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_story_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/story-links/{story-link-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/story-links/{story-link-public-id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_story_link")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_story_link", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_story_link",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Get Workflow",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_workflow(workflow_public_id: str = Field(..., alias="workflow-public-id", description="The unique identifier of the workflow to retrieve, provided as a 64-bit integer.")) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific workflow by its public ID. Returns the workflow's configuration, status, and metadata."""

    _workflow_public_id = _parse_int(workflow_public_id)

    # Construct request model with validation
    try:
        _request = _models.GetWorkflowRequest(
            path=_models.GetWorkflowRequestPath(workflow_public_id=_workflow_public_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_workflow: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v3/workflows/{workflow-public-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v3/workflows/{workflow-public-id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_workflow")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_workflow", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_workflow",
        method="GET",
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
        print("  python shortcut_server.py", file=sys.stderr)
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

    parser = argparse.ArgumentParser(description="Shortcut MCP Server")

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
    logger.info("Starting Shortcut MCP Server")
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

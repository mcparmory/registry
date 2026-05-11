#!/usr/bin/env python3
"""
Codacy MCP Server

API Info:
- API License: Codacy. All rights reserved (https://www.codacy.com)
- Contact: Codacy Team <code@codacy.com> (https://www.codacy.com)

Generated: 2026-05-11 23:17:00 UTC
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
from pydantic import Field

BASE_URL = os.getenv("BASE_URL", "https://app.codacy.com/api/v3")
SERVER_NAME = "Codacy"
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

def parse_time_range(value: str | None = None) -> dict | None:
    """Helper function for parameter transformation"""
    if value is None:
        return None
    parts = value.split('/')
    if len(parts) != 2:
        raise ValueError(f'Invalid ISO 8601 interval format: {value!r}. Expected \'start/end\'.') from None
    start, end = parts[0].strip(), parts[1].strip()
    if not start or not end:
        raise ValueError(f'Both start and end dates must be non-empty in interval: {value!r}') from None
    return {'from': start, 'to': end}

def parse_image_ref(value: str | None = None) -> dict | None:
    """Helper function for parameter transformation"""
    if value is None:
        return None
    try:
        repo_and_name, tag = value.rsplit(':', 1)
    except ValueError:
        raise ValueError("image_ref must be in the format 'repositoryName/imageName:tag'") from None
    try:
        repository_name, image_name = repo_and_name.rsplit('/', 1)
    except ValueError:
        raise ValueError("image_ref must be in the format 'repositoryName/imageName:tag'") from None
    if not repository_name or not image_name or not tag:
        raise ValueError("image_ref must be in the format 'repositoryName/imageName:tag'")
    return {'repositoryName': repository_name, 'imageName': image_name, 'tag': tag}

def build_adf_description(description_heading: str | None = None, description_body: str | None = None, description_bullet_points: str | None = None) -> str | None:
    """Helper function for parameter transformation"""
    try:
        if description_heading is None and description_body is None and description_bullet_points is None:
            return None
        content = []
        if description_heading is not None:
            content.append({
                "type": "heading",
                "attrs": {"level": 2},
                "content": [{"type": "text", "text": description_heading}]
            })
        if description_body is not None:
            for paragraph_text in description_body.split("\n"):
                stripped = paragraph_text.strip()
                if stripped:
                    content.append({
                        "type": "paragraph",
                        "content": [{"type": "text", "text": stripped}]
                    })
        if description_bullet_points is not None and len(description_bullet_points) > 0:
            list_items = []
            for bullet in description_bullet_points:
                if bullet is not None:
                    list_items.append({
                        "type": "listItem",
                        "content": [{
                            "type": "paragraph",
                            "content": [{"type": "text", "text": str(bullet)}]
                        }]
                    })
            if list_items:
                content.append({"type": "bulletList", "content": list_items})
        if not content:
            return None
        doc = {"version": 1, "type": "doc", "content": content}
        return json.dumps(doc)
    except Exception as e:
        raise ValueError(f"Failed to build ADF description: {e}") from e

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
    'ApiKeyAuth',
]

# Initialize authentication handlers at server startup
_auth_handlers: dict[str, Any] = {}
try:
    _auth_handlers["ApiKeyAuth"] = _auth.APIKeyAuth(env_var="API_KEY", location="header", param_name="api-token")
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

mcp = FastMCP("Codacy", middleware=[_JsonCoercionMiddleware()])

# Tags: analysis
@mcp.tool(
    title="List Organization Repositories with Analysis",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_organization_repositories_with_analysis(
    provider: str = Field(..., description="The Git provider hosting the organization. Use the short identifier code for the desired provider."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The exact organization name as it appears on the Git provider."),
    limit: str | None = Field(None, description="Maximum number of repositories to return per page. Accepts values between 1 and 100."),
    search: str | None = Field(None, description="Filters the returned repositories to those whose names contain the provided string."),
    segments: str | None = Field(None, description="Restricts results to repositories belonging to the specified segments, provided as a comma-separated list of numeric segment identifiers."),
) -> dict[str, Any] | ToolResult:
    """Retrieves repositories belonging to a specified organization on a Git provider, including their analysis metadata. Supports filtering by name or segment, with pagination cursor that must be URL-encoded for Bitbucket."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.ListOrganizationRepositoriesWithAnalysisRequest(
            path=_models.ListOrganizationRepositoriesWithAnalysisRequestPath(provider=provider, remote_organization_name=remote_organization_name),
            query=_models.ListOrganizationRepositoriesWithAnalysisRequestQuery(limit=_limit, search=search, segments=segments)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_organization_repositories_with_analysis: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/analysis/organizations/{provider}/{remoteOrganizationName}/repositories", _request.path.model_dump(by_alias=True)) if _request.path else "/analysis/organizations/{provider}/{remoteOrganizationName}/repositories"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_organization_repositories_with_analysis")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_organization_repositories_with_analysis", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_organization_repositories_with_analysis",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: analysis
@mcp.tool(
    title="Search Organization Repositories with Analysis",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def search_organization_repositories(
    provider: str = Field(..., description="The Git provider hosting the organization. Use the short identifier for the target platform (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider. Must match the exact organization identifier used by the provider."),
    limit: str | None = Field(None, description="Maximum number of repositories to return per request. Accepts values between 1 and 100 inclusive."),
    names: list[str] | None = Field(None, description="Filter results to only the specified repository names. Each item should be a repository name string; order does not affect results."),
) -> dict[str, Any] | ToolResult:
    """Search repositories within an organization on a specified Git provider, returning results enriched with analysis information. Supports filtering by repository name and paginated results."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.SearchOrganizationRepositoriesWithAnalysisRequest(
            path=_models.SearchOrganizationRepositoriesWithAnalysisRequestPath(provider=provider, remote_organization_name=remote_organization_name),
            query=_models.SearchOrganizationRepositoriesWithAnalysisRequestQuery(limit=_limit),
            body=_models.SearchOrganizationRepositoriesWithAnalysisRequestBody(names=names)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_organization_repositories: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/search/analysis/organizations/{provider}/{remoteOrganizationName}/repositories", _request.path.model_dump(by_alias=True)) if _request.path else "/search/analysis/organizations/{provider}/{remoteOrganizationName}/repositories"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_organization_repositories")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_organization_repositories", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_organization_repositories",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: analysis
@mcp.tool(
    title="Get Repository Analysis",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_repository_analysis(
    provider: str = Field(..., description="The short identifier for the Git provider hosting the repository."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="The name of the repository within the specified Git provider organization."),
    branch: str | None = Field(None, description="The name of a branch enabled on Codacy for this repository. If omitted, the main branch configured in Codacy repository settings is used. Use the listRepositoryBranches endpoint to retrieve valid branch names."),
) -> dict[str, Any] | ToolResult:
    """Retrieves detailed analysis information for a specific repository on Codacy, including code quality metrics and insights for the authenticated user. Optionally scoped to a specific enabled branch, defaulting to the repository's main branch."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoryWithAnalysisRequest(
            path=_models.GetRepositoryWithAnalysisRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name),
            query=_models.GetRepositoryWithAnalysisRequestQuery(branch=branch)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_repository_analysis: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}", _request.path.model_dump(by_alias=True)) if _request.path else "/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_repository_analysis")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_repository_analysis", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_repository_analysis",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: analysis
@mcp.tool(
    title="List Repository Tools",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_repository_tools(
    provider: str = Field(..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="The name of the repository within the specified Git provider organization."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the analysis tool settings configured for a specific repository, including which tools are enabled and their configurations. No authentication is required when accessing public repositories."""

    # Construct request model with validation
    try:
        _request = _models.ListRepositoryToolsRequest(
            path=_models.ListRepositoryToolsRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_repository_tools: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/tools", _request.path.model_dump(by_alias=True)) if _request.path else "/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/tools"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_repository_tools")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_repository_tools", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_repository_tools",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: analysis
@mcp.tool(
    title="List Tool Conflicts",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_tool_conflicts(
    provider: str = Field(..., description="Short code identifying the Git provider hosting the repository."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="The name of the repository within the specified organization on the Git provider."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a list of analysis tools that have configuration conflicts in the specified repository. Useful for diagnosing tool setup issues that may affect code analysis results."""

    # Construct request model with validation
    try:
        _request = _models.ListRepositoryToolConflictsRequest(
            path=_models.ListRepositoryToolConflictsRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_tool_conflicts: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/tools/conflicts", _request.path.model_dump(by_alias=True)) if _request.path else "/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/tools/conflicts"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_tool_conflicts")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_tool_conflicts", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_tool_conflicts",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: analysis
@mcp.tool(
    title="Configure Repository Tool",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def configure_repository_tool(
    provider: str = Field(..., description="Identifier for the Git provider hosting the repository."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="Name of the organization on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="Name of the repository within the specified organization on the Git provider."),
    tool_uuid: str = Field(..., alias="toolUuid", description="UUID uniquely identifying the analysis tool to configure."),
    enabled: bool | None = Field(None, description="Set to true to enable the tool for analysis or false to disable it entirely for this repository."),
    use_configuration_file: bool | None = Field(None, alias="useConfigurationFile", description="Set to true to have the tool read its settings from a configuration file in the repository, or false to use Codacy-managed settings."),
    patterns: list[_models.ConfigurePattern] | None = Field(None, description="List of pattern objects to enable or disable for this tool; each item should specify the pattern identifier and its desired enabled state. Order is not significant."),
) -> dict[str, Any] | ToolResult:
    """Enable or disable an analysis tool and its patterns for a specific repository. Changes are applied immediately without checking whether the repository is linked to a coding standard."""

    # Construct request model with validation
    try:
        _request = _models.ConfigureToolRequest(
            path=_models.ConfigureToolRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name, tool_uuid=tool_uuid),
            body=_models.ConfigureToolRequestBody(enabled=enabled, use_configuration_file=use_configuration_file, patterns=patterns)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for configure_repository_tool: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/tools/{toolUuid}", _request.path.model_dump(by_alias=True)) if _request.path else "/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/tools/{toolUuid}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("configure_repository_tool")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("configure_repository_tool", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="configure_repository_tool",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: analysis
@mcp.tool(
    title="List Repository Tool Patterns",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_repository_tool_patterns(
    provider: str = Field(..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="The name of the repository within the specified Git provider organization."),
    tool_uuid: str = Field(..., alias="toolUuid", description="The UUID uniquely identifying the analysis tool whose patterns should be retrieved."),
    languages: str | None = Field(None, description="Comma-separated list of programming language names to restrict results to patterns applicable to those languages."),
    categories: str | None = Field(None, description="Comma-separated list of pattern categories to filter by. Valid values are Security, ErrorProne, CodeStyle, Compatibility, UnusedCode, Complexity, Comprehensibility, Documentation, BestPractice, and Performance."),
    severity_levels: str | None = Field(None, alias="severityLevels", description="Comma-separated list of severity levels to filter by. Valid values are Error, High, Warning, and Info."),
    tags: str | None = Field(None, description="Comma-separated list of pattern tags to filter results by, such as framework or technology tags."),
    search: str | None = Field(None, description="A search string used to filter patterns by matching against pattern names or descriptions."),
    enabled: bool | None = Field(None, description="When set to true, returns only enabled patterns; when set to false, returns only disabled patterns. Omit to return all patterns regardless of enabled status."),
    recommended: bool | None = Field(None, description="When set to true, returns only recommended patterns; when set to false, returns only non-recommended patterns. Omit to return all patterns regardless of recommended status."),
    sort: str | None = Field(None, description="The field by which to sort the returned patterns. Valid values are category, recommended, and severity."),
    direction: str | None = Field(None, description="The direction in which to sort results, either ascending (asc) or descending (desc)."),
    limit: str | None = Field(None, description="Maximum number of patterns to return in a single response, between 1 and 100 inclusive."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the code pattern configurations for a specific analysis tool applied to a repository. Returns standard organization-level settings if applied, otherwise falls back to repository-specific settings."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.ListRepositoryToolPatternsRequest(
            path=_models.ListRepositoryToolPatternsRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name, tool_uuid=tool_uuid),
            query=_models.ListRepositoryToolPatternsRequestQuery(languages=languages, categories=categories, severity_levels=severity_levels, tags=tags, search=search, enabled=enabled, recommended=recommended, sort=sort, direction=direction, limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_repository_tool_patterns: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/tools/{toolUuid}/patterns", _request.path.model_dump(by_alias=True)) if _request.path else "/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/tools/{toolUuid}/patterns"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_repository_tool_patterns")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_repository_tool_patterns", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_repository_tool_patterns",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: analysis
@mcp.tool(
    title="Bulk Update Repository Tool Patterns",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def bulk_update_repository_tool_patterns(
    provider: str = Field(..., description="Short code identifying the Git provider hosting the repository."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="Name of the organization on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="Name of the repository within the organization on the Git provider."),
    tool_uuid: str = Field(..., alias="toolUuid", description="UUID that uniquely identifies the tool whose patterns will be updated."),
    enabled: bool = Field(..., description="Set to `true` to enable all matched code patterns, or `false` to disable them."),
    languages: str | None = Field(None, description="Comma-separated list of programming language names to restrict the update to patterns applicable to those languages only."),
    categories: str | None = Field(None, description="Comma-separated list of pattern categories to restrict the update. Valid values are `Security`, `ErrorProne`, `CodeStyle`, `Compatibility`, `UnusedCode`, `Complexity`, `Comprehensibility`, `Documentation`, `BestPractice`, and `Performance`."),
    severity_levels: str | None = Field(None, alias="severityLevels", description="Comma-separated list of severity levels to restrict the update. Valid values are `Error`, `High`, `Warning`, and `Info`."),
    tags: str | None = Field(None, description="Comma-separated list of pattern tags to restrict the update to patterns that carry any of the specified tags."),
    search: str | None = Field(None, description="Free-text search string used to filter patterns by name or description before applying the bulk update."),
    recommended: bool | None = Field(None, description="When set to `true`, restricts the update to recommended patterns only; when set to `false`, restricts it to non-recommended patterns only. Omit to include patterns regardless of recommended status."),
) -> dict[str, Any] | ToolResult:
    """Bulk enables or disables code patterns for a specific tool in a repository. Use optional filters to target a subset of patterns by language, category, severity, tags, or search term; omit all filters to apply the change to every pattern for the tool."""

    # Construct request model with validation
    try:
        _request = _models.UpdateRepositoryToolPatternsRequest(
            path=_models.UpdateRepositoryToolPatternsRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name, tool_uuid=tool_uuid),
            query=_models.UpdateRepositoryToolPatternsRequestQuery(languages=languages, categories=categories, severity_levels=severity_levels, tags=tags, search=search, recommended=recommended),
            body=_models.UpdateRepositoryToolPatternsRequestBody(enabled=enabled)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for bulk_update_repository_tool_patterns: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/tools/{toolUuid}/patterns", _request.path.model_dump(by_alias=True)) if _request.path else "/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/tools/{toolUuid}/patterns"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("bulk_update_repository_tool_patterns")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("bulk_update_repository_tool_patterns", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="bulk_update_repository_tool_patterns",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: analysis
@mcp.tool(
    title="Get Repository Tool Pattern",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_repository_tool_pattern_config(
    provider: str = Field(..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="The name of the repository within the specified Git provider organization."),
    tool_uuid: str = Field(..., alias="toolUuid", description="The UUID uniquely identifying the analysis tool whose pattern configuration is being retrieved."),
    pattern_id: str = Field(..., alias="patternId", description="The identifier for the specific pattern within the tool whose configuration is being retrieved."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the pattern configuration for a specific tool pattern applied to a repository. Returns the organization-level standard configuration if one is applied, otherwise falls back to the repository-level settings."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoryToolPatternRequest(
            path=_models.GetRepositoryToolPatternRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name, tool_uuid=tool_uuid, pattern_id=pattern_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_repository_tool_pattern_config: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/tools/{toolUuid}/patterns/{patternId}", _request.path.model_dump(by_alias=True)) if _request.path else "/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/tools/{toolUuid}/patterns/{patternId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_repository_tool_pattern_config")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_repository_tool_pattern_config", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_repository_tool_pattern_config",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: analysis
@mcp.tool(
    title="Get Tool Patterns Overview",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_tool_patterns_overview(
    provider: str = Field(..., description="Short code identifying the Git hosting provider for the repository."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="Name of the organization or account that owns the repository on the Git provider."),
    repository_name: str = Field(..., alias="repositoryName", description="Name of the repository within the specified organization on the Git provider."),
    tool_uuid: str = Field(..., alias="toolUuid", description="UUID uniquely identifying the analysis tool whose pattern overview is being retrieved."),
    languages: str | None = Field(None, description="Comma-separated list of programming language names to restrict the overview to patterns applicable to those languages."),
    categories: str | None = Field(None, description="Comma-separated list of pattern categories to include in the overview. Valid values are Security, ErrorProne, CodeStyle, Compatibility, UnusedCode, Complexity, Comprehensibility, Documentation, BestPractice, and Performance."),
    severity_levels: str | None = Field(None, alias="severityLevels", description="Comma-separated list of severity levels to filter patterns by. Valid values are Error, High, Warning, and Info."),
    tags: str | None = Field(None, description="Comma-separated list of tags to filter patterns by, allowing narrowing results to patterns associated with specific frameworks or topics."),
    search: str | None = Field(None, description="Search string used to filter patterns by matching against pattern names or descriptions."),
    enabled: bool | None = Field(None, description="When set to true, returns only enabled patterns; when set to false, returns only disabled patterns. Omit to return patterns regardless of enabled status."),
    recommended: bool | None = Field(None, description="When set to true, returns only patterns marked as recommended; when set to false, returns only non-recommended patterns. Omit to return patterns regardless of recommended status."),
) -> dict[str, Any] | ToolResult:
    """Retrieves an overview of code patterns for a specific analysis tool in a repository, showing counts and summaries by category, severity, and status. Uses standard settings if applied, otherwise falls back to repository-level tool configuration."""

    # Construct request model with validation
    try:
        _request = _models.ToolPatternsOverviewRequest(
            path=_models.ToolPatternsOverviewRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name, tool_uuid=tool_uuid),
            query=_models.ToolPatternsOverviewRequestQuery(languages=languages, categories=categories, severity_levels=severity_levels, tags=tags, search=search, enabled=enabled, recommended=recommended)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_tool_patterns_overview: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/tools/{toolUuid}/patterns/overview", _request.path.model_dump(by_alias=True)) if _request.path else "/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/tools/{toolUuid}/patterns/overview"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_tool_patterns_overview")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_tool_patterns_overview", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_tool_patterns_overview",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: analysis
@mcp.tool(
    title="List Tool Pattern Conflicts",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_tool_pattern_conflicts(
    provider: str = Field(..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="The name of the repository within the specified Git provider organization."),
    tool_uuid: str = Field(..., alias="toolUuid", description="The UUID uniquely identifying the analysis tool whose pattern conflicts should be retrieved."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a list of patterns for a specific tool that conflict with the repository's configured Coding Standards, helping identify rule inconsistencies that may affect code analysis."""

    # Construct request model with validation
    try:
        _request = _models.ListRepositoryToolPatternConflictsRequest(
            path=_models.ListRepositoryToolPatternConflictsRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name, tool_uuid=tool_uuid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_tool_pattern_conflicts: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/tools/{toolUuid}/conflicts", _request.path.model_dump(by_alias=True)) if _request.path else "/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/tools/{toolUuid}/conflicts"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_tool_pattern_conflicts")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_tool_pattern_conflicts", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_tool_pattern_conflicts",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: analysis
@mcp.tool(
    title="Get Repository Analysis Progress",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_repository_analysis_progress(
    provider: str = Field(..., description="Short code identifying the Git provider hosting the repository."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The name of the organization that owns the repository on the Git provider."),
    repository_name: str = Field(..., alias="repositoryName", description="The name of the repository within the organization on the Git provider."),
    branch: str | None = Field(None, description="The branch to check analysis progress for; must be a branch enabled in Codacy repository settings. Defaults to the main branch configured in Codacy if omitted."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the analysis progress overview for a specific repository on Codacy, indicating how far along the initial analysis has advanced. No authentication is required when accessing public repositories."""

    # Construct request model with validation
    try:
        _request = _models.GetFirstAnalysisOverviewRequest(
            path=_models.GetFirstAnalysisOverviewRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name),
            query=_models.GetFirstAnalysisOverviewRequestQuery(branch=branch)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_repository_analysis_progress: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/analysis-progress", _request.path.model_dump(by_alias=True)) if _request.path else "/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/analysis-progress"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_repository_analysis_progress")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_repository_analysis_progress", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_repository_analysis_progress",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: analysis
@mcp.tool(
    title="List Pull Requests",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_pull_requests(
    provider: str = Field(..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="The name of the repository within the specified Git provider organization."),
    limit: str | None = Field(None, description="Maximum number of pull requests to return in a single response. Accepts values between 1 and 100."),
    search: str | None = Field(None, description="Filters the returned pull requests to those whose names or metadata contain the provided string."),
    include_not_analyzed: bool | None = Field(None, alias="includeNotAnalyzed", description="When set to true, includes pull requests that have not yet been analyzed by Codacy alongside analyzed ones."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a list of pull requests for a specified repository, supporting sorting by last-updated, impact, or merged status. No authentication is required for public repositories."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.ListRepositoryPullRequestsRequest(
            path=_models.ListRepositoryPullRequestsRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name),
            query=_models.ListRepositoryPullRequestsRequestQuery(limit=_limit, search=search, include_not_analyzed=include_not_analyzed)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_pull_requests: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/pull-requests", _request.path.model_dump(by_alias=True)) if _request.path else "/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/pull-requests"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_pull_requests")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_pull_requests", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_pull_requests",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: analysis
@mcp.tool(
    title="Get Pull Request",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_pull_request(
    provider: str = Field(..., description="Short code identifying the Git provider hosting the repository (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="The name of the repository within the specified organization on the Git provider."),
    pull_request_number: str = Field(..., alias="pullRequestNumber", description="The unique numeric identifier of the pull request within the repository, as assigned by the Git provider."),
) -> dict[str, Any] | ToolResult:
    """Retrieves detailed analysis data for a specific pull request in a repository. No authentication is required when accessing public repositories."""

    _pull_request_number = _parse_int(pull_request_number)

    # Construct request model with validation
    try:
        _request = _models.GetRepositoryPullRequest(
            path=_models.GetRepositoryPullRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name, pull_request_number=_pull_request_number)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_pull_request: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/pull-requests/{pullRequestNumber}", _request.path.model_dump(by_alias=True)) if _request.path else "/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/pull-requests/{pullRequestNumber}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_pull_request")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_pull_request", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_pull_request",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: coverage
@mcp.tool(
    title="Get Pull Request Coverage",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_pull_request_coverage(
    provider: str = Field(..., description="Short code identifying the Git hosting provider (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization or account name as it appears on the Git provider."),
    repository_name: str = Field(..., alias="repositoryName", description="The repository name within the specified organization on the Git provider."),
    pull_request_number: str = Field(..., alias="pullRequestNumber", description="The numeric identifier of the pull request for which to retrieve coverage data."),
) -> dict[str, Any] | ToolResult:
    """Retrieves code coverage information for a specific pull request in a repository. No authentication is required when accessing public repositories."""

    _pull_request_number = _parse_int(pull_request_number)

    # Construct request model with validation
    try:
        _request = _models.GetRepositoryPullRequestCoverageRequest(
            path=_models.GetRepositoryPullRequestCoverageRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name, pull_request_number=_pull_request_number)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_pull_request_coverage: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/coverage/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/pull-requests/{pullRequestNumber}", _request.path.model_dump(by_alias=True)) if _request.path else "/coverage/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/pull-requests/{pullRequestNumber}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_pull_request_coverage")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_pull_request_coverage", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_pull_request_coverage",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: coverage
@mcp.tool(
    title="List Pull Request File Coverage",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_pull_request_file_coverage(
    provider: str = Field(..., description="Short code identifying the Git provider hosting the repository (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="The name of the repository within the specified organization on the Git provider."),
    pull_request_number: str = Field(..., alias="pullRequestNumber", description="The numeric identifier of the pull request for which file coverage data is being requested."),
) -> dict[str, Any] | ToolResult:
    """Retrieves per-file code coverage information for a specific pull request in a repository. No authentication is required when accessing public repositories."""

    _pull_request_number = _parse_int(pull_request_number)

    # Construct request model with validation
    try:
        _request = _models.GetRepositoryPullRequestFilesCoverageRequest(
            path=_models.GetRepositoryPullRequestFilesCoverageRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name, pull_request_number=_pull_request_number)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_pull_request_file_coverage: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/coverage/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/pull-requests/{pullRequestNumber}/files", _request.path.model_dump(by_alias=True)) if _request.path else "/coverage/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/pull-requests/{pullRequestNumber}/files"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_pull_request_file_coverage")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_pull_request_file_coverage", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_pull_request_file_coverage",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: coverage
@mcp.tool(
    title="Reanalyze Pull Request Coverage",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def reanalyze_pull_request_coverage(
    provider: str = Field(..., description="Short code identifying the Git provider hosting the repository. Use the provider's abbreviated identifier."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization or account name as it appears on the Git provider."),
    repository_name: str = Field(..., alias="repositoryName", description="The repository name within the specified organization on the Git provider."),
    pull_request_number: str = Field(..., alias="pullRequestNumber", description="The numeric identifier of the pull request whose coverage report should be reanalyzed."),
) -> dict[str, Any] | ToolResult:
    """Triggers a reanalysis of the latest coverage report uploaded for a specific pull request. Useful when coverage data needs to be reprocessed without uploading a new report."""

    _pull_request_number = _parse_int(pull_request_number)

    # Construct request model with validation
    try:
        _request = _models.ReanalyzeCoverageRequest(
            path=_models.ReanalyzeCoverageRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name, pull_request_number=_pull_request_number)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for reanalyze_pull_request_coverage: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/coverage/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/pull-requests/{pullRequestNumber}/reanalyze", _request.path.model_dump(by_alias=True)) if _request.path else "/coverage/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/pull-requests/{pullRequestNumber}/reanalyze"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("reanalyze_pull_request_coverage")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("reanalyze_pull_request_coverage", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="reanalyze_pull_request_coverage",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: analysis
@mcp.tool(
    title="List Pull Request Commits",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_pull_request_commits(
    provider: str = Field(..., description="The Git provider hosting the repository. Use the short identifier for the target platform (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="The name of the repository within the specified Git provider organization."),
    pull_request_number: str = Field(..., alias="pullRequestNumber", description="The unique number identifying the pull request within the repository, as assigned by the Git provider."),
    limit: str | None = Field(None, description="Maximum number of commit results to return in a single response. Accepts values between 1 and 100; defaults to 100 if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieves analysis results for all commits within a specified pull request, including code quality and issue data per commit. Results are paginated and scoped to a repository on a supported Git provider."""

    _pull_request_number = _parse_int(pull_request_number)
    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetPullRequestCommitsRequest(
            path=_models.GetPullRequestCommitsRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name, pull_request_number=_pull_request_number),
            query=_models.GetPullRequestCommitsRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_pull_request_commits: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/pull-requests/{pullRequestNumber}/commits", _request.path.model_dump(by_alias=True)) if _request.path else "/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/pull-requests/{pullRequestNumber}/commits"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_pull_request_commits")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_pull_request_commits", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_pull_request_commits",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: analysis
@mcp.tool(
    title="Bypass Pull Request Analysis",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def bypass_pull_request_analysis(
    provider: str = Field(..., description="Short code identifying the Git provider hosting the repository (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization or account name as it appears on the Git provider."),
    repository_name: str = Field(..., alias="repositoryName", description="The repository name within the specified organization on the Git provider."),
    pull_request_number: str = Field(..., alias="pullRequestNumber", description="The numeric identifier of the pull request whose analysis status should be bypassed."),
) -> dict[str, Any] | ToolResult:
    """Bypasses the analysis status check for a specific pull request, allowing it to proceed regardless of analysis results. Useful when overriding blocking analysis gates in CI/CD workflows."""

    _pull_request_number = _parse_int(pull_request_number)

    # Construct request model with validation
    try:
        _request = _models.BypassPullRequestAnalysisRequest(
            path=_models.BypassPullRequestAnalysisRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name, pull_request_number=_pull_request_number)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for bypass_pull_request_analysis: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/pull-requests/{pullRequestNumber}/bypass", _request.path.model_dump(by_alias=True)) if _request.path else "/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/pull-requests/{pullRequestNumber}/bypass"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("bypass_pull_request_analysis")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("bypass_pull_request_analysis", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="bypass_pull_request_analysis",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: analysis
@mcp.tool(
    title="Trigger Pull Request AI Review",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def trigger_pull_request_ai_review(
    provider: str = Field(..., description="Short code identifying the Git hosting provider for the repository."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="Name of the organization or account on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="Name of the repository within the organization on the Git provider."),
    pull_request_number: str = Field(..., alias="pullRequestNumber", description="The numeric identifier of the pull request to be reviewed, as assigned by the Git provider."),
) -> dict[str, Any] | ToolResult:
    """Triggers an AI-powered code review for a specific pull request in a repository. Initiates automated analysis and feedback generation for the pull request's changes."""

    _pull_request_number = _parse_int(pull_request_number)

    # Construct request model with validation
    try:
        _request = _models.TriggerPullRequestAiReviewRequest(
            path=_models.TriggerPullRequestAiReviewRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name, pull_request_number=_pull_request_number)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for trigger_pull_request_ai_review: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/pull-requests/{pullRequestNumber}/ai-reviewer/trigger", _request.path.model_dump(by_alias=True)) if _request.path else "/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/pull-requests/{pullRequestNumber}/ai-reviewer/trigger"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("trigger_pull_request_ai_review")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("trigger_pull_request_ai_review", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="trigger_pull_request_ai_review",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: analysis, coverage
@mcp.tool(
    title="List Pull Request Coverage Reports",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_pull_request_coverage_reports(
    provider: str = Field(..., description="Short code identifying the Git provider hosting the repository."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization or account name as it appears on the Git provider."),
    repository_name: str = Field(..., alias="repositoryName", description="The repository name within the specified organization on the Git provider."),
    pull_request_number: str = Field(..., alias="pullRequestNumber", description="The unique number identifying the pull request within the repository."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all coverage reports uploaded for both the common ancestor commit and the head commit of a pull request branch. Useful for comparing coverage changes introduced by the pull request."""

    _pull_request_number = _parse_int(pull_request_number)

    # Construct request model with validation
    try:
        _request = _models.GetPullRequestCoverageReportsRequest(
            path=_models.GetPullRequestCoverageReportsRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name, pull_request_number=_pull_request_number)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_pull_request_coverage_reports: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/pull-requests/{pullRequestNumber}/coverage/status", _request.path.model_dump(by_alias=True)) if _request.path else "/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/pull-requests/{pullRequestNumber}/coverage/status"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_pull_request_coverage_reports")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_pull_request_coverage_reports", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_pull_request_coverage_reports",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: analysis
@mcp.tool(
    title="List Pull Request Issues",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_pull_request_issues(
    provider: str = Field(..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="The name of the repository within the specified Git provider organization."),
    pull_request_number: str = Field(..., alias="pullRequestNumber", description="The unique number identifying the pull request within the repository."),
    status: Literal["all", "new", "fixed"] | None = Field(None, description="Filters issues by their status relative to the pull request. Use 'new' for issues introduced, 'fixed' for issues resolved, or 'all' to return both."),
    only_potential: bool | None = Field(None, alias="onlyPotential", description="When set to true, restricts results to potential issues only, which are lower-confidence findings that may require additional review."),
    limit: str | None = Field(None, description="Maximum number of issues to return in a single response. Accepts values between 1 and 100."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the list of issues found in a specific pull request for a given repository. Use the status filter to narrow results to new, fixed, or all issues, and optionally surface only potential issues."""

    _pull_request_number = _parse_int(pull_request_number)
    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.ListPullRequestIssuesRequest(
            path=_models.ListPullRequestIssuesRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name, pull_request_number=_pull_request_number),
            query=_models.ListPullRequestIssuesRequestQuery(status=status, only_potential=only_potential, limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_pull_request_issues: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/pull-requests/{pullRequestNumber}/issues", _request.path.model_dump(by_alias=True)) if _request.path else "/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/pull-requests/{pullRequestNumber}/issues"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_pull_request_issues")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_pull_request_issues", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_pull_request_issues",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: analysis
@mcp.tool(
    title="List Pull Request Clones",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_pull_request_clones(
    provider: str = Field(..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="The name of the repository within the specified organization on the Git provider."),
    pull_request_number: str = Field(..., alias="pullRequestNumber", description="The numeric identifier of the pull request for which duplicate code blocks should be retrieved."),
    status: Literal["all", "new", "fixed"] | None = Field(None, description="Filters returned clones by their status relative to the pull request: 'new' for clones introduced, 'fixed' for clones resolved, or 'all' for every detected clone regardless of status."),
    only_potential: bool | None = Field(None, alias="onlyPotential", description="When set to true, restricts results to only potential (lower-confidence) duplicate code blocks rather than confirmed clones."),
    limit: str | None = Field(None, description="Maximum number of clone results to return in a single response, between 1 and 100 inclusive."),
) -> dict[str, Any] | ToolResult:
    """Retrieves duplicate code blocks (clones) detected in a specific pull request for a repository. Use the status filter to narrow results to new, fixed, or all duplicate occurrences."""

    _pull_request_number = _parse_int(pull_request_number)
    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.ListPullRequestClonesRequest(
            path=_models.ListPullRequestClonesRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name, pull_request_number=_pull_request_number),
            query=_models.ListPullRequestClonesRequestQuery(status=status, only_potential=only_potential, limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_pull_request_clones: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/pull-requests/{pullRequestNumber}/clones", _request.path.model_dump(by_alias=True)) if _request.path else "/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/pull-requests/{pullRequestNumber}/clones"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_pull_request_clones")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_pull_request_clones", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_pull_request_clones",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: analysis
@mcp.tool(
    title="List Commit Clones",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_commit_clones(
    provider: str = Field(..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="The name of the repository within the specified organization on the Git provider."),
    commit_uuid: str = Field(..., alias="commitUuid", description="The UUID or full SHA hash identifying the specific commit to analyze for duplicate code blocks."),
    status: Literal["all", "new", "fixed"] | None = Field(None, description="Filters duplicate code blocks by their status relative to the commit: all returns every clone, new returns only newly introduced clones, and fixed returns only clones resolved in this commit."),
    only_potential: bool | None = Field(None, alias="onlyPotential", description="When set to true, restricts results to only potential duplicate code issues, excluding confirmed clones."),
    limit: str | None = Field(None, description="Maximum number of duplicate code block results to return per request. Accepts values between 1 and 100."),
) -> dict[str, Any] | ToolResult:
    """Retrieves duplicate code blocks (clones) detected in a specific commit for a repository. Use the status parameter to filter results by new, fixed, or all duplicate occurrences."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.ListCommitClonesRequest(
            path=_models.ListCommitClonesRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name, commit_uuid=commit_uuid),
            query=_models.ListCommitClonesRequestQuery(status=status, only_potential=only_potential, limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_commit_clones: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/commits/{commitUuid}/clones", _request.path.model_dump(by_alias=True)) if _request.path else "/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/commits/{commitUuid}/clones"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_commit_clones")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_commit_clones", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_commit_clones",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: analysis
@mcp.tool(
    title="List Pull Request Logs",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_pull_request_logs(
    provider: str = Field(..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="The name of the repository within the specified Git provider organization."),
    pull_request_number: str = Field(..., alias="pullRequestNumber", description="The unique number identifying the pull request within the repository, as assigned by the Git provider."),
) -> dict[str, Any] | ToolResult:
    """Retrieves analysis logs for a specific pull request in a repository, useful for diagnosing issues or reviewing the details of a Codacy analysis run."""

    _pull_request_number = _parse_int(pull_request_number)

    # Construct request model with validation
    try:
        _request = _models.ListPullRequestLogsRequest(
            path=_models.ListPullRequestLogsRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name, pull_request_number=_pull_request_number)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_pull_request_logs: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/pull-requests/{pullRequestNumber}/logs", _request.path.model_dump(by_alias=True)) if _request.path else "/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/pull-requests/{pullRequestNumber}/logs"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_pull_request_logs")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_pull_request_logs", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_pull_request_logs",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: analysis
@mcp.tool(
    title="List Commit Analysis Logs",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_commit_analysis_logs(
    provider: str = Field(..., description="Short code identifying the Git provider hosting the repository (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="The name of the repository within the specified organization on the Git provider."),
    commit_uuid: str = Field(..., alias="commitUuid", description="The unique identifier of the commit whose analysis logs are being requested, provided as a UUID or full commit SHA hash."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the analysis log entries for a specific commit in a repository, providing details about the analysis process and any issues encountered during execution."""

    # Construct request model with validation
    try:
        _request = _models.ListCommitLogsRequest(
            path=_models.ListCommitLogsRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name, commit_uuid=commit_uuid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_commit_analysis_logs: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/commits/{commitUuid}/logs", _request.path.model_dump(by_alias=True)) if _request.path else "/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/commits/{commitUuid}/logs"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_commit_analysis_logs")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_commit_analysis_logs", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_commit_analysis_logs",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: analysis
@mcp.tool(
    title="List Commit Files",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_commit_files(
    provider: str = Field(..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="The name of the repository within the specified Git provider organization."),
    commit_uuid: str = Field(..., alias="commitUuid", description="The unique identifier of the commit, provided as a UUID or full SHA hash string."),
    branch: str | None = Field(None, description="The branch to scope the analysis results to; must be a branch enabled on Codacy. Defaults to the repository's main branch if omitted."),
    filter_: Literal["withCoverageChanges"] | None = Field(None, alias="filter", description="Narrows the returned files by type: omit to return all files changed in the commit or with coverage changes, or use 'withCoverageChanges' to return only files that have coverage changes."),
    limit: str | None = Field(None, description="Maximum number of file results to return per request. Accepts values between 1 and 100."),
    search: str | None = Field(None, description="Filters the results to only include files whose relative path contains the specified string."),
    sort_column: Literal["totalCoverage", "deltaCoverage", "filename"] | None = Field(None, alias="sortColumn", description="The field by which to sort the returned files: 'filename' (default) sorts alphabetically, 'deltaCoverage' sorts by coverage change, and 'totalCoverage' sorts by overall coverage value."),
    column_order: Literal["asc", "desc"] | None = Field(None, alias="columnOrder", description="The direction in which to sort results: 'asc' for ascending order (default) or 'desc' for descending order."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the list of files changed in a specific commit along with their static analysis and coverage results. Supports filtering, searching, sorting, and pagination to narrow down results."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.ListCommitFilesRequest(
            path=_models.ListCommitFilesRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name, commit_uuid=commit_uuid),
            query=_models.ListCommitFilesRequestQuery(branch=branch, filter_=filter_, limit=_limit, search=search, sort_column=sort_column, column_order=column_order)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_commit_files: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/commits/{commitUuid}/files", _request.path.model_dump(by_alias=True)) if _request.path else "/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/commits/{commitUuid}/files"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_commit_files")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_commit_files", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_commit_files",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: analysis
@mcp.tool(
    title="List Pull Request Files",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_pull_request_files(
    provider: str = Field(..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="The name of the repository within the specified organization on the Git provider."),
    pull_request_number: str = Field(..., alias="pullRequestNumber", description="The unique numeric identifier of the pull request within the repository."),
    limit: str | None = Field(None, description="Maximum number of file results to return per request. Must be between 1 and 100."),
    sort_column: Literal["totalCoverage", "deltaCoverage", "filename"] | None = Field(None, alias="sortColumn", description="The field by which to sort the returned files. Use `filename` to sort alphabetically by file path, `deltaCoverage` to sort by the change in coverage, or `totalCoverage` to sort by the overall coverage value."),
    column_order: Literal["asc", "desc"] | None = Field(None, alias="columnOrder", description="The direction in which to order the sorted results, either ascending or descending."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the list of files changed in a pull request along with their static analysis results. Supports sorting by filename, coverage delta, or total coverage."""

    _pull_request_number = _parse_int(pull_request_number)
    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.ListPullRequestFilesRequest(
            path=_models.ListPullRequestFilesRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name, pull_request_number=_pull_request_number),
            query=_models.ListPullRequestFilesRequestQuery(limit=_limit, sort_column=sort_column, column_order=column_order)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_pull_request_files: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/pull-requests/{pullRequestNumber}/files", _request.path.model_dump(by_alias=True)) if _request.path else "/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/pull-requests/{pullRequestNumber}/files"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_pull_request_files")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_pull_request_files", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_pull_request_files",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: repository, configuration
@mcp.tool(
    title="Follow Repository",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def follow_repository(
    provider: str = Field(..., description="Short identifier for the Git provider hosting the repository (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="The name of the repository within the specified Git provider organization to follow."),
) -> dict[str, Any] | ToolResult:
    """Follow a repository that has already been added to Codacy, enabling tracking of its analysis and quality metrics for the authenticated user."""

    # Construct request model with validation
    try:
        _request = _models.FollowAddedRepositoryRequest(
            path=_models.FollowAddedRepositoryRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for follow_repository: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/follow", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/follow"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("follow_repository")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("follow_repository", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="follow_repository",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: repository, configuration
@mcp.tool(
    title="Unfollow Repository",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def unfollow_repository(
    provider: str = Field(..., description="Short identifier for the Git provider hosting the repository (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The name of the organization on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="The name of the repository within the specified Git provider organization to unfollow."),
) -> dict[str, Any] | ToolResult:
    """Stops following a repository in the specified organization on a Git provider, removing it from the list of monitored repositories."""

    # Construct request model with validation
    try:
        _request = _models.UnfollowRepositoryRequest(
            path=_models.UnfollowRepositoryRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for unfollow_repository: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/follow", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/follow"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("unfollow_repository")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("unfollow_repository", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="unfollow_repository",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: repository, configuration
@mcp.tool(
    title="Update Repository Quality Settings",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_repository_quality_settings(
    provider: str = Field(..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="The name of the repository within the specified Git provider organization."),
    max_issue_percentage: str | None = Field(None, alias="maxIssuePercentage", description="The maximum acceptable percentage of files with issues; the repository is flagged as unhealthy if this threshold is exceeded. Must be a non-negative integer representing a percentage."),
    max_duplicated_files_percentage: str | None = Field(None, alias="maxDuplicatedFilesPercentage", description="The maximum acceptable percentage of duplicated files; the repository is flagged as unhealthy if this threshold is exceeded. Must be a non-negative integer representing a percentage."),
    min_coverage_percentage: str | None = Field(None, alias="minCoveragePercentage", description="The minimum required code coverage percentage; the repository is flagged as unhealthy if coverage falls below this threshold. Must be a non-negative integer representing a percentage."),
    max_complex_files_percentage: str | None = Field(None, alias="maxComplexFilesPercentage", description="The maximum acceptable percentage of complex files; the repository is flagged as unhealthy if this threshold is exceeded. Must be a non-negative integer representing a percentage."),
    file_duplication_block_threshold: str | None = Field(None, alias="fileDuplicationBlockThreshold", description="The number of cloned blocks above which a file is considered duplicated within this repository. Must be zero or greater."),
    file_complexity_value_threshold: str | None = Field(None, alias="fileComplexityValueThreshold", description="The complexity score above which a file is considered complex within this repository. Must be zero or greater."),
) -> dict[str, Any] | ToolResult:
    """Updates the quality gate thresholds for a specific repository, defining the criteria under which the repository is considered healthy or unhealthy across issues, duplication, coverage, and complexity metrics."""

    _max_issue_percentage = _parse_int(max_issue_percentage)
    _max_duplicated_files_percentage = _parse_int(max_duplicated_files_percentage)
    _min_coverage_percentage = _parse_int(min_coverage_percentage)
    _max_complex_files_percentage = _parse_int(max_complex_files_percentage)
    _file_duplication_block_threshold = _parse_int(file_duplication_block_threshold)
    _file_complexity_value_threshold = _parse_int(file_complexity_value_threshold)

    # Construct request model with validation
    try:
        _request = _models.UpdateRepositoryQualitySettingsRequest(
            path=_models.UpdateRepositoryQualitySettingsRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name),
            body=_models.UpdateRepositoryQualitySettingsRequestBody(max_issue_percentage=_max_issue_percentage, max_duplicated_files_percentage=_max_duplicated_files_percentage, min_coverage_percentage=_min_coverage_percentage, max_complex_files_percentage=_max_complex_files_percentage, file_duplication_block_threshold=_file_duplication_block_threshold, file_complexity_value_threshold=_file_complexity_value_threshold)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_repository_quality_settings: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/settings/quality/repository", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/settings/quality/repository"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_repository_quality_settings")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_repository_quality_settings", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_repository_quality_settings",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: repository, configuration
@mcp.tool(
    title="Regenerate Repository SSH User Key",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def regenerate_repository_ssh_user_key(
    provider: str = Field(..., description="Short identifier for the Git provider hosting the repository, such as gh for GitHub, gl for GitLab, or bb for Bitbucket."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The name of the organization on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="The name of the repository within the specified organization on the Git provider."),
) -> dict[str, Any] | ToolResult:
    """Regenerates the user SSH key Codacy uses to clone the specified repository, automatically adding the new public key to the user's account on the Git provider. Using a user SSH key is recommended when the repository includes submodules."""

    # Construct request model with validation
    try:
        _request = _models.RegenerateUserSshKeyRequest(
            path=_models.RegenerateUserSshKeyRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for regenerate_repository_ssh_user_key: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/settings/ssh-user-key", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/settings/ssh-user-key"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("regenerate_repository_ssh_user_key")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("regenerate_repository_ssh_user_key", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="regenerate_repository_ssh_user_key",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: repository, configuration
@mcp.tool(
    title="Regenerate Repository SSH Key",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def regenerate_repository_ssh_key(
    provider: str = Field(..., description="Short identifier for the Git provider hosting the repository (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization or account name as it appears on the Git provider."),
    repository_name: str = Field(..., alias="repositoryName", description="The repository name within the specified organization on the Git provider."),
) -> dict[str, Any] | ToolResult:
    """Regenerates the SSH key Codacy uses to clone a specific repository, automatically updating the new public key on the Git provider."""

    # Construct request model with validation
    try:
        _request = _models.RegenerateRepositorySshKeyRequest(
            path=_models.RegenerateRepositorySshKeyRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for regenerate_repository_ssh_key: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/settings/ssh-repository-key", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/settings/ssh-repository-key"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("regenerate_repository_ssh_key")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("regenerate_repository_ssh_key", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="regenerate_repository_ssh_key",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: repository, configuration
@mcp.tool(
    title="Get Repository SSH Key",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_repository_ssh_key(
    provider: str = Field(..., description="Short code identifying the Git provider hosting the repository."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="The name of the repository within the specified organization on the Git provider."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the most recently generated public SSH key associated with a repository, which may be either a user or repository-level SSH key. Useful for verifying or displaying the active SSH key configured for repository access."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoryPublicSshKeyRequest(
            path=_models.GetRepositoryPublicSshKeyRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_repository_ssh_key: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/settings/stored-ssh-key", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/settings/stored-ssh-key"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_repository_ssh_key")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_repository_ssh_key", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_repository_ssh_key",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: repository, configuration
@mcp.tool(
    title="Sync Repository with Provider",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def sync_repository(
    provider: str = Field(..., description="Short identifier for the Git provider hosting the repository."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization or account name as it appears on the Git provider."),
    repository_name: str = Field(..., alias="repositoryName", description="The repository name as it appears under the organization on the Git provider."),
) -> dict[str, Any] | ToolResult:
    """Synchronizes a repository's name and visibility settings in Codacy with the current state from the upstream Git provider. Useful after renaming or changing the visibility of a repository directly on the provider."""

    # Construct request model with validation
    try:
        _request = _models.SyncRepositoryWithProviderRequest(
            path=_models.SyncRepositoryWithProviderRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for sync_repository: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/settings/sync", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/settings/sync"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("sync_repository")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("sync_repository", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="sync_repository",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: repository, configuration
@mcp.tool(
    title="Get Build Server Analysis Setting",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_build_server_analysis_setting(
    provider: str = Field(..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="The name of the repository within the specified Git provider organization."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the current status of the 'Run analysis on your build server' setting for a specific repository. Use this to check whether build server analysis is enabled or disabled."""

    # Construct request model with validation
    try:
        _request = _models.GetBuildServerAnalysisSettingRequest(
            path=_models.GetBuildServerAnalysisSettingRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_build_server_analysis_setting: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/settings/analysis", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/settings/analysis"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_build_server_analysis_setting")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_build_server_analysis_setting", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_build_server_analysis_setting",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: language-settings
@mcp.tool(
    title="List Repository Languages",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_repository_languages(
    provider: str = Field(..., description="Short code identifying the Git provider hosting the repository."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization or account name as it appears on the Git provider."),
    repository_name: str = Field(..., alias="repositoryName", description="The repository name as it appears within the Git provider organization."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all programming languages detected in a repository, including their associated file extensions and whether each language is enabled for analysis."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoryLanguagesRequest(
            path=_models.GetRepositoryLanguagesRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_repository_languages: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/settings/languages", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/settings/languages"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_repository_languages")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_repository_languages", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_repository_languages",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: language-settings
@mcp.tool(
    title="Configure Repository Language Settings",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def configure_repository_language_settings(
    provider: str = Field(..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="The name of the repository within the specified Git provider organization."),
    languages: list[_models.RepositoryLanguageUpdate] = Field(..., description="The complete list of languages to configure for this repository. Each item should represent a language identifier; order is not significant, and the full desired set must be provided as this replaces existing settings."),
) -> dict[str, Any] | ToolResult:
    """Updates the language response settings for a specific repository, controlling which programming languages are recognized and analyzed. Use this to tailor language detection behavior for a given repository within an organization."""

    # Construct request model with validation
    try:
        _request = _models.PatchRepositoryLanguageResponseSettingsRequest(
            path=_models.PatchRepositoryLanguageResponseSettingsRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name),
            body=_models.PatchRepositoryLanguageResponseSettingsRequestBody(languages=languages)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for configure_repository_language_settings: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/settings/languages", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/settings/languages"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("configure_repository_language_settings")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("configure_repository_language_settings", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="configure_repository_language_settings",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: repository, configuration
@mcp.tool(
    title="Get Repository Commit Quality Settings",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_repository_commit_quality_settings(
    provider: str = Field(..., description="Short code identifying the Git provider hosting the repository."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The name of the organization on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="The name of the repository within the specified Git provider organization."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the quality gate settings applied to commits for a specific repository. Note that diff coverage threshold is not included, as it is not currently supported for commit-level quality checks."""

    # Construct request model with validation
    try:
        _request = _models.GetCommitQualitySettingsRequest(
            path=_models.GetCommitQualitySettingsRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_repository_commit_quality_settings: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/settings/quality/commits", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/settings/quality/commits"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_repository_commit_quality_settings")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_repository_commit_quality_settings", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_repository_commit_quality_settings",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: repository, configuration
@mcp.tool(
    title="Reset Repository Commit Quality Settings",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def reset_repository_commit_quality_settings(
    provider: str = Field(..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The name of the organization on the Git provider under which the repository resides."),
    repository_name: str = Field(..., alias="repositoryName", description="The name of the repository within the specified Git provider organization whose commit quality settings will be reset."),
) -> dict[str, Any] | ToolResult:
    """Resets the commit quality settings for a specific repository to Codacy's default values, discarding any custom configurations previously applied."""

    # Construct request model with validation
    try:
        _request = _models.ResetCommitsQualitySettingsRequest(
            path=_models.ResetCommitsQualitySettingsRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for reset_repository_commit_quality_settings: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/settings/quality/commits/reset", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/settings/quality/commits/reset"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("reset_repository_commit_quality_settings")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("reset_repository_commit_quality_settings", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="reset_repository_commit_quality_settings",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: repository, configuration
@mcp.tool(
    title="Reset Repository Quality Settings",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def reset_repository_quality_settings(
    provider: str = Field(..., description="Short code identifying the Git provider hosting the repository (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The exact organization or account name as it appears on the Git provider."),
    repository_name: str = Field(..., alias="repositoryName", description="The exact repository name as it appears under the organization on the Git provider."),
) -> dict[str, Any] | ToolResult:
    """Resets all quality settings for a specific repository back to Codacy's default values, discarding any custom configurations that were previously applied."""

    # Construct request model with validation
    try:
        _request = _models.ResetRepositoryQualitySettingsRequest(
            path=_models.ResetRepositoryQualitySettingsRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for reset_repository_quality_settings: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/settings/quality/repository/reset", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/settings/quality/repository/reset"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("reset_repository_quality_settings")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("reset_repository_quality_settings", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="reset_repository_quality_settings",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: analysis
@mcp.tool(
    title="List Organization Pull Requests",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_organization_pull_requests(
    provider: str = Field(..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The exact organization name as it appears on the Git provider."),
    limit: str | None = Field(None, description="Maximum number of pull requests to return per request. Accepts values between 1 and 100."),
    search: str | None = Field(None, description="Filters pull requests by matching the provided string against repository names or other relevant fields."),
) -> dict[str, Any] | ToolResult:
    """Retrieves pull requests across all repositories in an organization that the authenticated user has access to. Results can be sorted by last updated date (default), impact, or merged status."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.ListOrganizationPullRequestsRequest(
            path=_models.ListOrganizationPullRequestsRequestPath(provider=provider, remote_organization_name=remote_organization_name),
            query=_models.ListOrganizationPullRequestsRequestQuery(limit=_limit, search=search)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_organization_pull_requests: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/analysis/organizations/{provider}/{remoteOrganizationName}/pull-requests", _request.path.model_dump(by_alias=True)) if _request.path else "/analysis/organizations/{provider}/{remoteOrganizationName}/pull-requests"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_organization_pull_requests")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_organization_pull_requests", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_organization_pull_requests",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: analysis
@mcp.tool(
    title="List Commit Statistics",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_commit_statistics(
    provider: str = Field(..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="The name of the repository within the specified Git provider organization."),
    branch: str | None = Field(None, description="The repository branch to retrieve commit statistics for, which must be a branch enabled in Codacy settings. Defaults to the main branch configured in the Codacy repository settings if omitted."),
    days: str | None = Field(None, description="The number of days of commit statistics to return, ranging from 1 to 365. Returns the most recent days that have analysis data, defaulting to 31 if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieves daily commit analysis statistics for a repository over the last N days that have available analysis data. Note that returned days reflect days with actual data, which may not align with the last N consecutive calendar days."""

    _days = _parse_int(days)

    # Construct request model with validation
    try:
        _request = _models.ListCommitAnalysisStatsRequest(
            path=_models.ListCommitAnalysisStatsRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name),
            query=_models.ListCommitAnalysisStatsRequestQuery(branch=branch, days=_days)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_commit_statistics: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/commit-statistics", _request.path.model_dump(by_alias=True)) if _request.path else "/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/commit-statistics"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_commit_statistics")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_commit_statistics", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_commit_statistics",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: analysis
@mcp.tool(
    title="List Repository Category Overviews",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_repository_category_overviews(
    provider: str = Field(..., description="Identifier for the Git provider hosting the repository."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="Name of the organization on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="Name of the repository within the specified organization on the Git provider."),
    branch: str | None = Field(None, description="Name of a branch enabled on Codacy for which to retrieve category overviews; defaults to the main branch configured in Codacy repository settings if omitted."),
) -> dict[str, Any] | ToolResult:
    """Retrieves analysis category overviews (e.g., code quality, security, complexity) for a specific repository, summarizing issue counts and grades per category. Authentication is not required for public repositories."""

    # Construct request model with validation
    try:
        _request = _models.ListCategoryOverviewsRequest(
            path=_models.ListCategoryOverviewsRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name),
            query=_models.ListCategoryOverviewsRequestQuery(branch=branch)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_repository_category_overviews: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/category-overviews", _request.path.model_dump(by_alias=True)) if _request.path else "/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/category-overviews"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_repository_category_overviews")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_repository_category_overviews", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_repository_category_overviews",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: analysis
@mcp.tool(
    title="Search Repository Issues",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def search_repository_issues(
    provider: str = Field(..., description="Identifier for the Git provider hosting the repository, such as GitHub, GitLab, or Bitbucket."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization or account name as it appears on the Git provider."),
    repository_name: str = Field(..., alias="repositoryName", description="The repository name within the specified organization on the Git provider."),
    limit: str | None = Field(None, description="Maximum number of issues to return per request. Accepts values between 1 and 100."),
) -> dict[str, Any] | ToolResult:
    """Searches and returns issues found by Codacy in a specific repository, equivalent to the Issues page view. Supports filtering via request body to narrow results by category, severity, or other criteria."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.SearchRepositoryIssuesRequest(
            path=_models.SearchRepositoryIssuesRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name),
            query=_models.SearchRepositoryIssuesRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_repository_issues: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/issues/search", _request.path.model_dump(by_alias=True)) if _request.path else "/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/issues/search"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_repository_issues")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_repository_issues", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_repository_issues",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: analysis
@mcp.tool(
    title="Bulk Ignore Repository Issues",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def bulk_ignore_repository_issues(
    provider: str = Field(..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="The name of the repository within the specified Git provider organization."),
    issue_ids: list[str] = Field(..., alias="issueIds", description="An unordered list of unique issue IDs to ignore. Maximum of 50 IDs per request; each item should be a valid issue identifier."),
    reason: str | None = Field(None, description="An optional reason categorizing why the issues are being ignored, used for tracking and audit purposes."),
    comment: str | None = Field(None, description="An optional free-text comment providing additional context or explanation for ignoring the specified issues."),
) -> dict[str, Any] | ToolResult:
    """Ignores a batch of issues in a specified repository, suppressing them from analysis results. Accepts up to 50 issue IDs per request, with an optional reason and comment for audit purposes."""

    # Construct request model with validation
    try:
        _request = _models.BulkIgnoreIssuesRequest(
            path=_models.BulkIgnoreIssuesRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name),
            body=_models.BulkIgnoreIssuesRequestBody(issue_ids=issue_ids, reason=reason, comment=comment)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for bulk_ignore_repository_issues: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/issues/bulk-ignore", _request.path.model_dump(by_alias=True)) if _request.path else "/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/issues/bulk-ignore"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("bulk_ignore_repository_issues")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("bulk_ignore_repository_issues", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="bulk_ignore_repository_issues",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: analysis
@mcp.tool(
    title="Get Repository Issues Overview",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def get_repository_issues_overview(
    provider: str = Field(..., description="The Git provider hosting the repository, identified by a short code (e.g., GitHub, GitLab, or Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="The name of the repository within the specified organization on the Git provider."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a summary of issues found by Codacy in a specific repository, including issue counts and breakdowns as shown on the Issues page. Supports filtering via request body parameters."""

    # Construct request model with validation
    try:
        _request = _models.IssuesOverviewRequest(
            path=_models.IssuesOverviewRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_repository_issues_overview: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/issues/overview", _request.path.model_dump(by_alias=True)) if _request.path else "/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/issues/overview"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_repository_issues_overview")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_repository_issues_overview", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_repository_issues_overview",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: analysis
@mcp.tool(
    title="Get Repository Issue",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_repository_issue(
    provider: str = Field(..., description="Short code identifying the Git provider hosting the repository (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="The name of the repository within the specified organization on the Git provider."),
    issue_id: str = Field(..., alias="issueId", description="The unique numeric identifier of the open issue to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieves detailed information about a specific open issue in a repository. Requires identifying the Git provider, organization, repository, and issue ID."""

    _issue_id = _parse_int(issue_id)

    # Construct request model with validation
    try:
        _request = _models.GetIssueRequest(
            path=_models.GetIssueRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name, issue_id=_issue_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_repository_issue: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/issues/{issueId}", _request.path.model_dump(by_alias=True)) if _request.path else "/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/issues/{issueId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_repository_issue")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_repository_issue", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_repository_issue",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: analysis
@mcp.tool(
    title="Set Issue Ignored State",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def set_issue_ignored_state(
    provider: str = Field(..., description="Short code identifying the Git provider hosting the repository."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="Name of the organization or account on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="Name of the repository within the organization on the Git provider."),
    issue_id: str = Field(..., alias="issueId", description="Unique identifier of the issue to update."),
    ignored: bool = Field(..., description="Set to true to ignore the issue or false to unignore it and restore it to an active state."),
    reason: Literal["AcceptedUse", "FalsePositive", "NotExploitable", "TestCode", "ExternalCode"] | None = Field(None, description="Predefined category explaining why the issue is being ignored; required when ignoring an issue to ensure consistent classification."),
    comment: str | None = Field(None, description="Free-text comment providing additional context or justification for the ignore action, supplementing the predefined reason."),
) -> dict[str, Any] | ToolResult:
    """Ignore or unignore a specific code analysis issue in a repository, optionally providing a predefined reason and comment to justify the action."""

    # Construct request model with validation
    try:
        _request = _models.UpdateIssueStateRequest(
            path=_models.UpdateIssueStateRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name, issue_id=issue_id),
            body=_models.UpdateIssueStateRequestBody(ignored=ignored, reason=reason, comment=comment)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for set_issue_ignored_state: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/issues/{issueId}", _request.path.model_dump(by_alias=True)) if _request.path else "/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/issues/{issueId}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("set_issue_ignored_state")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("set_issue_ignored_state", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="set_issue_ignored_state",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: analysis
@mcp.tool(
    title="Ignore Issue False Positive",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def ignore_issue_false_positive(
    provider: str = Field(..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="The name of the repository within the specified Git provider organization."),
    issue_id: str = Field(..., alias="issueId", description="The unique identifier of the issue whose false positive result should be ignored."),
) -> dict[str, Any] | ToolResult:
    """Marks a false positive result on a specific issue as ignored, suppressing it from future analysis reports. Use this to dismiss incorrectly flagged issues within a repository."""

    # Construct request model with validation
    try:
        _request = _models.IgnoreFalsePositiveRequest(
            path=_models.IgnoreFalsePositiveRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name, issue_id=issue_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for ignore_issue_false_positive: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/issues/{issueId}/false-positive/ignore", _request.path.model_dump(by_alias=True)) if _request.path else "/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/issues/{issueId}/false-positive/ignore"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("ignore_issue_false_positive")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("ignore_issue_false_positive", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="ignore_issue_false_positive",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: analysis
@mcp.tool(
    title="List Ignored Issues",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def list_ignored_issues(
    provider: str = Field(..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="The name of the repository within the specified organization on the Git provider."),
    limit: str | None = Field(None, description="Maximum number of ignored issues to return per request. Accepts values between 1 and 100."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of issues that Codacy detected but were manually marked as ignored in the specified repository. Supports filtering via request body parameters."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.SearchRepositoryIgnoredIssuesRequest(
            path=_models.SearchRepositoryIgnoredIssuesRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name),
            query=_models.SearchRepositoryIgnoredIssuesRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_ignored_issues: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/ignoredIssues/search", _request.path.model_dump(by_alias=True)) if _request.path else "/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/ignoredIssues/search"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_ignored_issues")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_ignored_issues", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_ignored_issues",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: analysis
@mcp.tool(
    title="List Repository Commits",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_repository_commits(
    provider: str = Field(..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="The name of the repository within the specified Git provider organization."),
    branch: str | None = Field(None, description="The name of a branch enabled on Codacy for this repository, as returned by listRepositoryBranches. Defaults to the main branch configured in Codacy repository settings if omitted."),
    limit: str | None = Field(None, description="Maximum number of commit results to return. Accepts values between 1 and 100."),
) -> dict[str, Any] | ToolResult:
    """Retrieves Codacy analysis results for commits in a specified branch of a repository. Defaults to the main branch if no branch is specified."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.ListRepositoryCommitsRequest(
            path=_models.ListRepositoryCommitsRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name),
            query=_models.ListRepositoryCommitsRequestQuery(branch=branch, limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_repository_commits: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/commits", _request.path.model_dump(by_alias=True)) if _request.path else "/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/commits"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_repository_commits")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_repository_commits", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_repository_commits",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: analysis
@mcp.tool(
    title="Get Commit Analysis",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_commit_analysis(
    provider: str = Field(..., description="Short code identifying the Git provider hosting the repository, such as 'gh' for GitHub, 'gl' for GitLab, or 'bb' for Bitbucket."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="The name of the repository within the specified Git provider organization."),
    commit_uuid: str = Field(..., alias="commitUuid", description="The full SHA hash or UUID that uniquely identifies the commit to retrieve analysis results for."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the analysis results for a specific commit in a repository, including code quality metrics and issue findings. Useful for inspecting the impact of a particular commit on overall code health."""

    # Construct request model with validation
    try:
        _request = _models.GetCommitRequest(
            path=_models.GetCommitRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name, commit_uuid=commit_uuid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_commit_analysis: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/commits/{commitUuid}", _request.path.model_dump(by_alias=True)) if _request.path else "/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/commits/{commitUuid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_commit_analysis")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_commit_analysis", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_commit_analysis",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: analysis
@mcp.tool(
    title="Get Commit Delta Statistics",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_commit_delta_statistics(
    provider: str = Field(..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="The name of the repository within the specified organization on the Git provider."),
    commit_uuid: str = Field(..., alias="commitUuid", description="The unique identifier for the commit, provided as a UUID or full SHA hash string."),
) -> dict[str, Any] | ToolResult:
    """Retrieves quality metric deltas introduced by a specific commit, showing how the commit changed code quality indicators. Returns zero or null values for metrics if Codacy has not yet analyzed the commit."""

    # Construct request model with validation
    try:
        _request = _models.GetCommitDeltaStatisticsRequest(
            path=_models.GetCommitDeltaStatisticsRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name, commit_uuid=commit_uuid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_commit_delta_statistics: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/commits/{commitUuid}/deltaStatistics", _request.path.model_dump(by_alias=True)) if _request.path else "/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/commits/{commitUuid}/deltaStatistics"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_commit_delta_statistics")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_commit_delta_statistics", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_commit_delta_statistics",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: analysis
@mcp.tool(
    title="List Commit Delta Issues",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_commit_delta_issues(
    provider: str = Field(..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="The name of the repository within the specified organization on the Git provider."),
    src_commit_uuid: str = Field(..., alias="srcCommitUuid", description="The SHA or UUID of the source commit to analyze; the delta is calculated from this commit against its parent or the specified target commit."),
    target_commit_uuid: str | None = Field(None, alias="targetCommitUuid", description="The SHA or UUID of an optional target commit to use as the comparison baseline instead of the source commit's parent."),
    status: Literal["all", "new", "fixed"] | None = Field(None, description="Filters results by issue status: all returns every delta issue, new returns only introduced issues, and fixed returns only resolved issues."),
    only_potential: bool | None = Field(None, alias="onlyPotential", description="When set to true, restricts results to potential issues only, excluding confirmed issues from the response."),
    limit: str | None = Field(None, description="Maximum number of issues to return per request; must be between 1 and 100."),
) -> dict[str, Any] | ToolResult:
    """Retrieves issues introduced or fixed by a specific commit, calculated as a delta between the source commit and its parent (or an optional target commit). Use this to audit code quality changes at the commit level."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.ListCommitDeltaIssuesRequest(
            path=_models.ListCommitDeltaIssuesRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name, src_commit_uuid=src_commit_uuid),
            query=_models.ListCommitDeltaIssuesRequestQuery(target_commit_uuid=target_commit_uuid, status=status, only_potential=only_potential, limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_commit_delta_issues: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/commits/{srcCommitUuid}/deltaIssues", _request.path.model_dump(by_alias=True)) if _request.path else "/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/commits/{srcCommitUuid}/deltaIssues"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_commit_delta_issues")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_commit_delta_issues", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_commit_delta_issues",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: account
@mcp.tool(
    title="Get Authenticated User",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_authenticated_user() -> dict[str, Any] | ToolResult:
    """Retrieves the profile and account details of the currently authenticated user. Useful for confirming identity, accessing user metadata, or personalizing responses based on the active session."""

    # Extract parameters for API call
    _http_path = "/user"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_authenticated_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_authenticated_user", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_authenticated_user",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: account
@mcp.tool(
    title="Update Current User",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_current_user(
    name: str | None = Field(None, description="The display name to assign to the authenticated user's profile."),
    should_do_client_qualification: bool | None = Field(None, alias="shouldDoClientQualification", description="Whether the system should trigger client qualification checks for this user."),
) -> dict[str, Any] | ToolResult:
    """Updates profile settings for the currently authenticated user. Only the fields provided will be modified."""

    # Construct request model with validation
    try:
        _request = _models.PatchUserRequest(
            body=_models.PatchUserRequestBody(name=name, should_do_client_qualification=should_do_client_qualification)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_current_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/user"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_current_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_current_user", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_current_user",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: account
@mcp.tool(
    title="List Organizations",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_organizations(limit: str | None = Field(None, description="Maximum number of organizations to return in a single response, between 1 and 100.")) -> dict[str, Any] | ToolResult:
    """Retrieves all organizations that the currently authenticated user belongs to. Returns a paginated list up to the specified limit."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.ListUserOrganizationsRequest(
            query=_models.ListUserOrganizationsRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_organizations: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/user/organizations"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_organizations")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_organizations", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_organizations",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: account
@mcp.tool(
    title="List Organizations by Provider",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_organizations_by_provider(
    provider: str = Field(..., description="The Git provider to query for organizations. Use the short identifier code for the desired platform (e.g., GitHub, GitLab, Bitbucket)."),
    limit: str | None = Field(None, description="Maximum number of organizations to return in a single response. Accepts values between 1 and 100, defaulting to 100 if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all organizations associated with the authenticated user for a specified Git provider. Useful for discovering available organizations before performing organization-scoped operations."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.ListOrganizationsRequest(
            path=_models.ListOrganizationsRequestPath(provider=provider),
            query=_models.ListOrganizationsRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_organizations_by_provider: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/user/organizations/{provider}", _request.path.model_dump(by_alias=True)) if _request.path else "/user/organizations/{provider}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_organizations_by_provider")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_organizations_by_provider", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_organizations_by_provider",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: account
@mcp.tool(
    title="Get Organization for User",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_organization_for_user(
    provider: str = Field(..., description="The Git provider hosting the organization, identified by a short code (e.g., GitHub, GitLab, Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The exact name of the organization as it appears on the specified Git provider."),
) -> dict[str, Any] | ToolResult:
    """Retrieves details for a specific organization associated with the authenticated user on a given Git provider. Useful for confirming organization membership and accessing organization-level metadata."""

    # Construct request model with validation
    try:
        _request = _models.GetUserOrganizationRequest(
            path=_models.GetUserOrganizationRequestPath(provider=provider, remote_organization_name=remote_organization_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_organization_for_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/user/organizations/{provider}/{remoteOrganizationName}", _request.path.model_dump(by_alias=True)) if _request.path else "/user/organizations/{provider}/{remoteOrganizationName}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_organization_for_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_organization_for_user", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_organization_for_user",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: account
@mcp.tool(
    title="List User Emails",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_emails() -> dict[str, Any] | ToolResult:
    """Retrieves all email addresses associated with the authenticated user's account, including primary and secondary addresses along with their verification and visibility status."""

    # Extract parameters for API call
    _http_path = "/user/emails"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_emails")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_emails", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_emails",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: account
@mcp.tool(
    title="Remove User Email",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def remove_user_email() -> dict[str, Any] | ToolResult:
    """Removes a specified email address from the authenticated user's account. The primary email and the last remaining email address cannot be removed."""

    # Extract parameters for API call
    _http_path = "/user/emails/remove"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_user_email")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_user_email", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_user_email",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: account
@mcp.tool(
    title="Set Default Email",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def set_default_email() -> dict[str, Any] | ToolResult:
    """Designates a specified email address as the primary default for the authenticated user, automatically removing the default status from any previously designated email. Only one email address can hold default status at a time."""

    # Extract parameters for API call
    _http_path = "/user/emails/set-default"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("set_default_email")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("set_default_email", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="set_default_email",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: account
@mcp.tool(
    title="List Integrations",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_integrations(limit: str | None = Field(None, description="Maximum number of integrations to return in a single response. Accepts values between 1 and 100.")) -> dict[str, Any] | ToolResult:
    """Retrieves all integrations connected to the authenticated user's account. Returns a paginated list of integration records up to the specified limit."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.ListUserIntegrationsRequest(
            query=_models.ListUserIntegrationsRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_integrations: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/user/integrations"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_integrations")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_integrations", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_integrations",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: account
@mcp.tool(
    title="Delete Integration",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_integration(provider: str = Field(..., description="The identifier for the Git provider whose integration should be deleted. Accepted values include short codes for supported providers such as GitHub, GitLab, and Bitbucket.")) -> dict[str, Any] | ToolResult:
    """Permanently removes the connected Git provider integration for the authenticated user. Once deleted, the user will need to re-authenticate to restore access for that provider."""

    # Construct request model with validation
    try:
        _request = _models.DeleteIntegrationRequest(
            path=_models.DeleteIntegrationRequestPath(provider=provider)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_integration: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/user/integrations/{provider}", _request.path.model_dump(by_alias=True)) if _request.path else "/user/integrations/{provider}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_integration")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_integration", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_integration",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: organization
@mcp.tool(
    title="Get Organization",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_organization(
    provider: str = Field(..., description="Short identifier for the Git provider hosting the organization (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The exact organization name as it appears on the specified Git provider."),
) -> dict[str, Any] | ToolResult:
    """Retrieves details for a specific organization from a Git provider. Returns organization metadata such as name, settings, and associated information."""

    # Construct request model with validation
    try:
        _request = _models.GetOrganizationRequest(
            path=_models.GetOrganizationRequestPath(provider=provider, remote_organization_name=remote_organization_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_organization: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}"
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

# Tags: organization
@mcp.tool(
    title="Delete Organization",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_organization(
    provider: str = Field(..., description="Short identifier for the Git provider hosting the organization, such as GitHub, GitLab, or Bitbucket."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The exact name of the organization as it appears on the Git provider platform."),
) -> dict[str, Any] | ToolResult:
    """Permanently removes an organization from Codacy by deleting its association with the specified Git provider. This action cannot be undone and will remove all related configuration and data within Codacy."""

    # Construct request model with validation
    try:
        _request = _models.DeleteOrganizationRequest(
            path=_models.DeleteOrganizationRequestPath(provider=provider, remote_organization_name=remote_organization_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_organization: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_organization")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_organization", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_organization",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: account
@mcp.tool(
    title="Get Organization by Installation ID",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_organization_by_installation_id(
    provider: str = Field(..., description="The git provider identifier for the installation. Currently only GitHub ('gh') is supported."),
    installation_id: str = Field(..., alias="installationId", description="The unique numeric identifier of the Codacy installation to look up the associated organization for."),
) -> dict[str, Any] | ToolResult:
    """Retrieves an organization associated with a specific provider installation ID. Currently supports GitHub ('gh') as the git provider."""

    _installation_id = _parse_int(installation_id)

    # Construct request model with validation
    try:
        _request = _models.GetOrganizationByInstallationIdRequest(
            path=_models.GetOrganizationByInstallationIdRequestPath(provider=provider, installation_id=_installation_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_organization_by_installation_id: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/installation/{installationId}", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/installation/{installationId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_organization_by_installation_id")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_organization_by_installation_id", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_organization_by_installation_id",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: organization
@mcp.tool(
    title="Get Organization Billing",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_organization_billing(
    provider: str = Field(..., description="The Git provider hosting the organization, identified by a short code (e.g., GitHub, GitLab, Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The exact name of the organization as it appears on the specified Git provider."),
) -> dict[str, Any] | ToolResult:
    """Retrieves detailed billing information for a specific organization on a Git provider, including subscription and usage details."""

    # Construct request model with validation
    try:
        _request = _models.OrganizationDetailedBillingRequest(
            path=_models.OrganizationDetailedBillingRequestPath(provider=provider, remote_organization_name=remote_organization_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_organization_billing: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/billing", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/billing"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_organization_billing")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_organization_billing", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_organization_billing",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: organization
@mcp.tool(
    title="Update Organization Billing",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def update_organization_billing(
    provider: str = Field(..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The exact name of the organization as it appears on the specified Git provider."),
) -> dict[str, Any] | ToolResult:
    """Updates the billing information for a specified organization on a given Git provider. Use this to modify billing details associated with the organization's Codacy account."""

    # Construct request model with validation
    try:
        _request = _models.UpdateOrganizationDetailedBillingRequest(
            path=_models.UpdateOrganizationDetailedBillingRequestPath(provider=provider, remote_organization_name=remote_organization_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_organization_billing: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/billing", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/billing"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_organization_billing")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_organization_billing", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_organization_billing",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: organization
@mcp.tool(
    title="Get Organization Billing Card",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_organization_billing_card(
    provider: str = Field(..., description="The Git provider hosting the organization, identified by a short code (e.g., GitHub, GitLab, Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the specified Git provider."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the payment card details associated with an organization's billing account on a specified Git provider. Useful for reviewing current billing payment method information."""

    # Construct request model with validation
    try:
        _request = _models.OrganizationBillingCardRequest(
            path=_models.OrganizationBillingCardRequestPath(provider=provider, remote_organization_name=remote_organization_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_organization_billing_card: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/billing/card", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/billing/card"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_organization_billing_card")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_organization_billing_card", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_organization_billing_card",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: organization
@mcp.tool(
    title="Add Billing Card",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def add_billing_card(
    provider: str = Field(..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the specified Git provider."),
) -> dict[str, Any] | ToolResult:
    """Adds a payment card to the specified organization's billing profile using a Stripe token. The token must be obtained from the Stripe /v1/tokens API prior to calling this endpoint."""

    # Construct request model with validation
    try:
        _request = _models.OrganizationBillingAddCardRequest(
            path=_models.OrganizationBillingAddCardRequestPath(provider=provider, remote_organization_name=remote_organization_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_billing_card: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/billing/card", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/billing/card"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_billing_card")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_billing_card", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_billing_card",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: organization
@mcp.tool(
    title="Estimate Organization Billing",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def estimate_organization_billing(
    provider: str = Field(..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform."),
    payment_plan_code: str = Field(..., alias="paymentPlanCode", description="The code identifying the payment plan to estimate costs for. Available plan codes can be retrieved using the listPaymentPlans operation."),
    promo_code: str | None = Field(None, alias="promoCode", description="An optional promotional code to apply discounts or adjustments to the billing estimation."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a billing cost estimation for an organization based on a specified payment plan and optional promotional code. Useful for previewing pricing before committing to a plan."""

    # Construct request model with validation
    try:
        _request = _models.OrganizationBillingEstimationRequest(
            path=_models.OrganizationBillingEstimationRequestPath(provider=provider, remote_organization_name=remote_organization_name),
            query=_models.OrganizationBillingEstimationRequestQuery(payment_plan_code=payment_plan_code, promo_code=promo_code)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for estimate_organization_billing: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/billing/estimation", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/billing/estimation"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("estimate_organization_billing")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("estimate_organization_billing", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="estimate_organization_billing",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: organization
@mcp.tool(
    title="Change Organization Billing Plan",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def change_organization_billing_plan(
    provider: str = Field(..., description="The Git provider hosting the organization, identified by a short code (e.g., GitHub, GitLab, Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The exact name of the organization as it appears on the Git provider."),
) -> dict[str, Any] | ToolResult:
    """Changes the billing plan for a specified organization on a Git provider. Available plan codes can be retrieved using the list_payment_plans operation."""

    # Construct request model with validation
    try:
        _request = _models.ChangeOrganizationPlanRequest(
            path=_models.ChangeOrganizationPlanRequestPath(provider=provider, remote_organization_name=remote_organization_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for change_organization_billing_plan: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/billing/change-plan", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/billing/change-plan"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("change_organization_billing_plan")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("change_organization_billing_plan", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="change_organization_billing_plan",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: organization
@mcp.tool(
    title="Apply Organization Provider Settings",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def apply_organization_provider_settings(
    provider: str = Field(..., description="The Git provider hosting the organization, identified by its short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The exact organization name as it appears on the Git provider platform."),
) -> dict[str, Any] | ToolResult:
    """Applies the organization's default provider settings to all repositories within the specified Git provider organization. Use this to propagate updated integration settings uniformly across all repositories at once."""

    # Construct request model with validation
    try:
        _request = _models.ApplyProviderSettingsRequest(
            path=_models.ApplyProviderSettingsRequestPath(provider=provider, remote_organization_name=remote_organization_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for apply_organization_provider_settings: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/integrations/providerSettings/apply", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/integrations/providerSettings/apply"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("apply_organization_provider_settings")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("apply_organization_provider_settings", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="apply_organization_provider_settings",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: organization
@mcp.tool(
    title="Get Provider Settings",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_provider_settings(
    provider: str = Field(..., description="The Git provider identifier representing the source control platform to query (e.g., GitHub, GitLab, or Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The exact organization name as it appears on the specified Git provider platform."),
) -> dict[str, Any] | ToolResult:
    """Retrieves Git provider integration settings for a specific organization, including configuration details for the connected provider account."""

    # Construct request model with validation
    try:
        _request = _models.GetProviderSettingsRequest(
            path=_models.GetProviderSettingsRequestPath(provider=provider, remote_organization_name=remote_organization_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_provider_settings: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/integrations/providerSettings", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/integrations/providerSettings"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_provider_settings")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_provider_settings", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_provider_settings",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: organization
@mcp.tool(
    title="Configure Provider Settings",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def configure_provider_settings(
    provider: str = Field(..., description="Short identifier for the Git provider platform hosting the organization."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform."),
    commit_status: bool | None = Field(None, alias="commitStatus", description="Enables or disables Codacy commit status checks, which report analysis results directly on commits and pull requests."),
    pull_request_comment: bool | None = Field(None, alias="pullRequestComment", description="Enables or disables inline issue annotations posted as pull request comments by Codacy."),
    pull_request_summary: bool | None = Field(None, alias="pullRequestSummary", description="Enables or disables pull request summary comments that aggregate Codacy issue findings."),
    coverage_summary: bool | None = Field(None, alias="coverageSummary", description="Enables or disables coverage summary reporting on pull requests. Supported on GitHub only."),
    suggestions: bool | None = Field(None, description="Enables or disables AI-generated suggested code fixes posted on pull requests. Supported on GitHub only."),
    ai_enhanced_comments: bool | None = Field(None, alias="aiEnhancedComments", description="Enables or disables AI-enhanced pull request comments; when combined with Suggested Fixes (GitHub only), AI comments also include inline code fix suggestions."),
    ai_pull_request_reviewer: bool | None = Field(None, alias="aiPullRequestReviewer", description="Enables or disables the AI Pull Request Reviewer, which automatically analyzes pull requests and posts comments on code quality and potential issues. Supported on GitHub only."),
    ai_pull_request_reviewer_automatic: bool | None = Field(None, alias="aiPullRequestReviewerAutomatic", description="Enables or disables automatic triggering of the AI Pull Request Reviewer on each new pull request; after the initial automatic review, subsequent reviews must be explicitly requested. Supported on GitHub only."),
    pull_request_unified_summary: bool | None = Field(None, alias="pullRequestUnifiedSummary", description="Enables or disables a unified pull request summary that combines both coverage and analysis results into a single Codacy comment. Supported on GitHub only."),
) -> dict[str, Any] | ToolResult:
    """Creates or updates Git provider integration settings for an organization, controlling which Codacy features are active such as status checks, pull request annotations, AI-powered reviews, and coverage summaries."""

    # Construct request model with validation
    try:
        _request = _models.UpdateProviderSettingsRequest(
            path=_models.UpdateProviderSettingsRequestPath(provider=provider, remote_organization_name=remote_organization_name),
            body=_models.UpdateProviderSettingsRequestBody(commit_status=commit_status, pull_request_comment=pull_request_comment, pull_request_summary=pull_request_summary, coverage_summary=coverage_summary, suggestions=suggestions, ai_enhanced_comments=ai_enhanced_comments, ai_pull_request_reviewer=ai_pull_request_reviewer, ai_pull_request_reviewer_automatic=ai_pull_request_reviewer_automatic, pull_request_unified_summary=pull_request_unified_summary)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for configure_provider_settings: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/integrations/providerSettings", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/integrations/providerSettings"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("configure_provider_settings")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("configure_provider_settings", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="configure_provider_settings",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: repository
@mcp.tool(
    title="Get Repository Provider Integration Settings",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_repository_provider_integration_settings(
    provider: str = Field(..., description="Short identifier for the Git provider hosting the repository (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="The name of the repository within the specified Git provider organization."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the Git provider integration settings for a specific repository, including configuration details that control how Codacy interacts with the provider for that repository."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoryIntegrationsSettingsRequest(
            path=_models.GetRepositoryIntegrationsSettingsRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_repository_provider_integration_settings: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/integrations/providerSettings", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/integrations/providerSettings"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_repository_provider_integration_settings")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_repository_provider_integration_settings", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_repository_provider_integration_settings",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: repository
@mcp.tool(
    title="Update Repository Integration Settings",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_repository_integration_settings(
    provider: str = Field(..., description="Short identifier for the Git provider hosting the repository."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization or account name as it appears on the Git provider."),
    repository_name: str = Field(..., alias="repositoryName", description="The repository name as it appears under the organization on the Git provider."),
    commit_status: bool | None = Field(None, alias="commitStatus", description="Enables or disables commit status checks, which report Codacy analysis results directly on commits and pull requests."),
    pull_request_comment: bool | None = Field(None, alias="pullRequestComment", description="Enables or disables inline issue annotations posted as pull request comments for each identified code issue."),
    pull_request_summary: bool | None = Field(None, alias="pullRequestSummary", description="Enables or disables pull request summary comments that aggregate all issues found in the analysis."),
    coverage_summary: bool | None = Field(None, alias="coverageSummary", description="Enables or disables a coverage summary comment on pull requests showing coverage changes. Available on GitHub only."),
    suggestions: bool | None = Field(None, description="Enables or disables suggested code fixes posted as pull request comments. Available on GitHub only."),
    ai_enhanced_comments: bool | None = Field(None, alias="aiEnhancedComments", description="Enables or disables AI-enhanced comments on pull requests; when combined with Suggested Fixes (GitHub only), the AI comments also include fix suggestions."),
    ai_pull_request_reviewer: bool | None = Field(None, alias="aiPullRequestReviewer", description="Enables or disables the AI Pull Request Reviewer, which automatically analyzes pull requests and posts comments on code quality and potential issues. Available on GitHub only."),
    ai_pull_request_reviewer_automatic: bool | None = Field(None, alias="aiPullRequestReviewerAutomatic", description="Enables or disables automatic triggering of the AI Pull Request Reviewer on each new pull request; after the initial automatic review, subsequent reviews must be explicitly requested. Available on GitHub only."),
    pull_request_unified_summary: bool | None = Field(None, alias="pullRequestUnifiedSummary", description="Enables or disables a unified pull request summary that combines both coverage and analysis results into a single comment. Available on GitHub only."),
) -> dict[str, Any] | ToolResult:
    """Updates the Git provider integration settings for a specific repository, controlling which Codacy features are active such as status checks, pull request comments, AI reviews, and coverage summaries."""

    # Construct request model with validation
    try:
        _request = _models.UpdateRepositoryIntegrationsSettingsRequest(
            path=_models.UpdateRepositoryIntegrationsSettingsRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name),
            body=_models.UpdateRepositoryIntegrationsSettingsRequestBody(commit_status=commit_status, pull_request_comment=pull_request_comment, pull_request_summary=pull_request_summary, coverage_summary=coverage_summary, suggestions=suggestions, ai_enhanced_comments=ai_enhanced_comments, ai_pull_request_reviewer=ai_pull_request_reviewer, ai_pull_request_reviewer_automatic=ai_pull_request_reviewer_automatic, pull_request_unified_summary=pull_request_unified_summary)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_repository_integration_settings: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/integrations/providerSettings", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/integrations/providerSettings"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_repository_integration_settings")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_repository_integration_settings", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_repository_integration_settings",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: repository
@mcp.tool(
    title="Create Post Commit Hook",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def create_post_commit_hook(
    provider: str = Field(..., description="Short identifier for the Git provider hosting the repository (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The name of the organization or account on the Git provider under which the repository resides."),
    repository_name: str = Field(..., alias="repositoryName", description="The name of the repository within the specified Git provider organization for which the post-commit hook will be created."),
) -> dict[str, Any] | ToolResult:
    """Creates a post-commit hook integration for a repository, enabling Codacy to receive commit notifications and trigger analysis automatically after each push."""

    # Construct request model with validation
    try:
        _request = _models.CreatePostCommitHookRequest(
            path=_models.CreatePostCommitHookRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_post_commit_hook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/integrations/postCommitHook", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/integrations/postCommitHook"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_post_commit_hook")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_post_commit_hook", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_post_commit_hook",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: repository
@mcp.tool(
    title="Refresh Repository Provider Integration",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def refresh_repository_provider_integration(
    provider: str = Field(..., description="The Git provider hosting the repository. Accepted values are 'gh' for GitHub, 'gl' for GitLab, or 'bb' for Bitbucket. Note: this operation is only supported for GitLab and Bitbucket."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The name of the organization or workspace on the Git provider under which the repository resides."),
    repository_name: str = Field(..., alias="repositoryName", description="The name of the repository within the specified organization on the Git provider."),
) -> dict[str, Any] | ToolResult:
    """Refreshes the Git provider integration for a specific repository on GitLab or Bitbucket, using the authenticated user's credentials to enable commenting on new pull requests."""

    # Construct request model with validation
    try:
        _request = _models.RefreshProviderRepositoryIntegrationRequest(
            path=_models.RefreshProviderRepositoryIntegrationRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for refresh_repository_provider_integration: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/integrations/refreshProvider", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/integrations/refreshProvider"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("refresh_repository_provider_integration")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("refresh_repository_provider_integration", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="refresh_repository_provider_integration",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: organization
@mcp.tool(
    title="List Organization Repositories",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_organization_repositories(
    provider: str = Field(..., description="The Git provider hosting the organization. Use the short identifier code for the desired provider."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The exact name of the organization as it appears on the Git provider."),
    limit: str | None = Field(None, description="Maximum number of repositories to return per request. Accepts values between 1 and 100; note the API may return more results than specified."),
    search: str | None = Field(None, description="A search string used to filter repositories by name. Only repositories whose names contain this string will be returned."),
    filter_: Literal["Synced", "NotSynced", "AllSynced"] | None = Field(None, alias="filter", description="Controls which repositories are returned based on their sync status: `Synced` returns repositories the user has access to, `NotSynced` returns repositories fetched from the provider but not yet synced, and `AllSynced` returns all organization repositories (requires admin access)."),
    languages: str | None = Field(None, description="Filters results to repositories that use the specified programming languages, provided as a comma-separated list of language names."),
    segments: str | None = Field(None, description="Filters results to repositories belonging to the specified segments, provided as a comma-separated list of integer segment identifiers."),
) -> dict[str, Any] | ToolResult:
    """Retrieves repositories belonging to a specific organization on a Git provider for the authenticated user. Supports filtering by sync status, language, and segment, with cursor-based pagination (Bitbucket cursors must be URL-encoded before use in subsequent requests)."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.ListOrganizationRepositoriesRequest(
            path=_models.ListOrganizationRepositoriesRequestPath(provider=provider, remote_organization_name=remote_organization_name),
            query=_models.ListOrganizationRepositoriesRequestQuery(limit=_limit, search=search, filter_=filter_, languages=languages, segments=segments)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_organization_repositories: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/repositories", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/repositories"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_organization_repositories")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_organization_repositories", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_organization_repositories",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: organization
@mcp.tool(
    title="Get Organization Onboarding Progress",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_organization_onboarding_progress(
    provider: str = Field(..., description="Short code identifying the Git provider where the organization is hosted. Use the provider's abbreviated identifier."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The exact name of the organization as it appears on the Git provider platform."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the current onboarding progress for a specific organization on a Git provider. Useful for tracking setup completion status during the organization integration workflow."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveOrganizationOnboardingProgressRequest(
            path=_models.RetrieveOrganizationOnboardingProgressRequestPath(provider=provider, remote_organization_name=remote_organization_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_organization_onboarding_progress: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/onboarding/organizations/{provider}/{remoteOrganizationName}/progress", _request.path.model_dump(by_alias=True)) if _request.path else "/onboarding/organizations/{provider}/{remoteOrganizationName}/progress"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_organization_onboarding_progress")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_organization_onboarding_progress", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_organization_onboarding_progress",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: people
@mcp.tool(
    title="List Organization People",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_organization_people(
    provider: str = Field(..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The exact name of the organization as it appears on the Git provider."),
    limit: str | None = Field(None, description="Maximum number of people to return per request; must be between 1 and 100 inclusive."),
    search: str | None = Field(None, description="Filters the returned people by matching the provided string against their name or related identifiers."),
    only_members: bool | None = Field(None, alias="onlyMembers", description="When true, restricts results to only registered Codacy users; when false, also includes commit authors who have not joined Codacy."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a list of people associated with a specific organization on a Git provider, including Codacy users and optionally commit authors who are not Codacy users."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.ListPeopleFromOrganizationRequest(
            path=_models.ListPeopleFromOrganizationRequestPath(provider=provider, remote_organization_name=remote_organization_name),
            query=_models.ListPeopleFromOrganizationRequestQuery(limit=_limit, search=search, only_members=only_members)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_organization_people: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/people", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/people"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_organization_people")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_organization_people", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_organization_people",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: people
@mcp.tool(
    title="Add Organization Members",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def add_organization_members(
    provider: str = Field(..., description="Short code identifying the Git provider hosting the organization."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform."),
) -> dict[str, Any] | ToolResult:
    """Adds people to an organization on the specified Git provider, assigning them as members or committers based on whether they have a pending join request."""

    # Construct request model with validation
    try:
        _request = _models.AddPeopleToOrganizationRequest(
            path=_models.AddPeopleToOrganizationRequestPath(provider=provider, remote_organization_name=remote_organization_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_organization_members: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/people", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/people"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_organization_members")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_organization_members", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_organization_members",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: people
@mcp.tool(
    title="Export Organization People to CSV",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def export_organization_people_csv(
    provider: str = Field(..., description="The Git provider hosting the organization, identified by its short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform."),
) -> dict[str, Any] | ToolResult:
    """Generates and returns a CSV file listing all people in the specified organization, including their name, email, last login date, and last analysis date."""

    # Construct request model with validation
    try:
        _request = _models.ListPeopleFromOrganizationCsvRequest(
            path=_models.ListPeopleFromOrganizationCsvRequestPath(provider=provider, remote_organization_name=remote_organization_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for export_organization_people_csv: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/peopleCsv", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/peopleCsv"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("export_organization_people_csv")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("export_organization_people_csv", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="export_organization_people_csv",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: people
@mcp.tool(
    title="Remove Organization Members",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def remove_organization_members(
    provider: str = Field(..., description="The Git provider hosting the organization. Use the short identifier for the target platform."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The exact organization name as it appears on the Git provider platform."),
    emails: list[str] = Field(..., description="List of member email addresses to remove from the organization. Each item must be a valid email address; order is not significant."),
) -> dict[str, Any] | ToolResult:
    """Removes one or more members from a Git provider organization by their email addresses. Useful for revoking access when offboarding users or managing organization membership."""

    # Construct request model with validation
    try:
        _request = _models.RemovePeopleFromOrganizationRequest(
            path=_models.RemovePeopleFromOrganizationRequestPath(provider=provider, remote_organization_name=remote_organization_name),
            body=_models.RemovePeopleFromOrganizationRequestBody(emails=emails)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_organization_members: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/people/remove", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/people/remove"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_organization_members")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_organization_members", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_organization_members",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: app
@mcp.tool(
    title="Get Git Provider App Permissions",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_git_provider_app_permissions(
    provider: str = Field(..., description="The Git provider hosting the organization, identified by a short code (e.g., GitHub, GitLab, or Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The exact name of the organization as it appears on the Git provider platform."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the current status of Codacy's Git provider app permissions for a specified organization, indicating which permissions have been granted or are missing."""

    # Construct request model with validation
    try:
        _request = _models.GitProviderAppPermissionsRequest(
            path=_models.GitProviderAppPermissionsRequestPath(provider=provider, remote_organization_name=remote_organization_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_git_provider_app_permissions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/gitProviderAppPermissions", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/gitProviderAppPermissions"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_git_provider_app_permissions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_git_provider_app_permissions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_git_provider_app_permissions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: people
@mcp.tool(
    title="List Organization People Suggestions",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_organization_people_suggestions(
    provider: str = Field(..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The exact name of the organization as it appears on the specified Git provider."),
    limit: str | None = Field(None, description="Maximum number of people suggestions to return per request. Accepts values between 1 and 100."),
    search: str | None = Field(None, description="Filters the returned suggestions to those whose name or identifier contains the provided search string."),
) -> dict[str, Any] | ToolResult:
    """Retrieves suggested people (users) to add to an organization on a specified Git provider. Useful for discovering potential members based on activity or association with the organization."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.PeopleSuggestionsForOrganizationRequest(
            path=_models.PeopleSuggestionsForOrganizationRequestPath(provider=provider, remote_organization_name=remote_organization_name),
            query=_models.PeopleSuggestionsForOrganizationRequestQuery(limit=_limit, search=search)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_organization_people_suggestions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/people/suggestions", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/people/suggestions"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_organization_people_suggestions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_organization_people_suggestions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_organization_people_suggestions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: repository
@mcp.tool(
    title="Reanalyze Commit",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def reanalyze_commit(
    provider: str = Field(..., description="Short code identifying the Git provider hosting the repository (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="The name of the repository within the specified Git provider organization."),
    commit_uuid: str = Field(..., alias="commitUuid", description="The full UUID or SHA hash string that uniquely identifies the commit to be reanalyzed."),
    clean_cache: bool | None = Field(None, alias="cleanCache", description="When set to true, clears any cached analysis data before reanalyzing the commit, ensuring the results are not influenced by previous runs."),
) -> dict[str, Any] | ToolResult:
    """Triggers a reanalysis of a specific commit in a repository. Optionally clears the cache before running the analysis to ensure fresh results."""

    # Construct request model with validation
    try:
        _request = _models.ReanalyzeCommitByIdRequest(
            path=_models.ReanalyzeCommitByIdRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name),
            body=_models.ReanalyzeCommitByIdRequestBody(commit_uuid=commit_uuid, clean_cache=clean_cache)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for reanalyze_commit: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/reanalyzeCommit", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/reanalyzeCommit"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("reanalyze_commit")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("reanalyze_commit", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="reanalyze_commit",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: repository
@mcp.tool(
    title="Get Repository",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_repository(
    provider: str = Field(..., description="Short code identifying the Git provider hosting the repository (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization or account name as it appears on the Git provider platform."),
    repository_name: str = Field(..., alias="repositoryName", description="The repository name as it appears within the organization on the Git provider platform."),
) -> dict[str, Any] | ToolResult:
    """Retrieves detailed information about a specific repository within an organization on a given Git provider. Authentication is not required when accessing public repositories."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoryRequest(
            path=_models.GetRepositoryRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_repository: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}"
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

# Tags: repository
@mcp.tool(
    title="Delete Repository",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_repository(
    provider: str = Field(..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The exact name of the organization on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="The exact name of the repository within the specified organization on the Git provider."),
) -> dict[str, Any] | ToolResult:
    """Permanently removes the specified repository from the organization on the given Git provider. This action cannot be undone and will remove all associated data from Codacy."""

    # Construct request model with validation
    try:
        _request = _models.DeleteRepositoryRequest(
            path=_models.DeleteRepositoryRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_repository: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_repository")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_repository", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_repository",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: people
@mcp.tool(
    title="List Repository People Suggestions",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_repository_people_suggestions(
    provider: str = Field(..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The name of the organization as it appears on the Git provider."),
    repository_name: str = Field(..., alias="repositoryName", description="The name of the repository within the specified organization on the Git provider."),
    limit: str | None = Field(None, description="Maximum number of people suggestions to return. Accepts values between 1 and 100."),
    search: str | None = Field(None, description="Filters the returned suggestions to those whose names or identifiers match the provided search string."),
) -> dict[str, Any] | ToolResult:
    """Retrieves suggested people (collaborators or contributors) for a specific repository within an organization. Useful for discovering relevant users to add or assign within a given repository context."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.PeopleSuggestionsForRepositoryRequest(
            path=_models.PeopleSuggestionsForRepositoryRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name),
            query=_models.PeopleSuggestionsForRepositoryRequestQuery(limit=_limit, search=search)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_repository_people_suggestions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/people/suggestions", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/people/suggestions"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_repository_people_suggestions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_repository_people_suggestions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_repository_people_suggestions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: repository
@mcp.tool(
    title="List Repository Branches",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_repository_branches(
    provider: str = Field(..., description="The short identifier for the Git provider hosting the repository (e.g., 'gh' for GitHub, 'gl' for GitLab, 'bb' for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="The name of the repository within the specified Git provider organization."),
    enabled: bool | None = Field(None, description="Filters branches by their enabled status. When set to true, only enabled branches are returned; when set to false, only disabled branches are returned. Omit to return all branches regardless of status."),
    limit: str | None = Field(None, description="The maximum number of branches to return in a single response. Accepts values between 1 and 100."),
    search: str | None = Field(None, description="A string used to filter branches by name, returning only branches whose names contain the provided value."),
    sort: str | None = Field(None, description="The field by which to sort the returned branches. Accepted values are 'name' to sort alphabetically or 'last-updated' to sort by most recent activity."),
    direction: str | None = Field(None, description="The direction in which to sort the results. Use 'asc' for ascending order or 'desc' for descending order."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of branches for a specified repository, with optional filtering by enabled status or search term. No authentication is required when accessing public repositories."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.ListRepositoryBranchesRequest(
            path=_models.ListRepositoryBranchesRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name),
            query=_models.ListRepositoryBranchesRequestQuery(enabled=enabled, limit=_limit, search=search, sort=sort, direction=direction)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_repository_branches: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/branches", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/branches"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_repository_branches")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_repository_branches", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_repository_branches",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: repository
@mcp.tool(
    title="Configure Branch Analysis",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def configure_branch_analysis(
    provider: str = Field(..., description="Short code identifying the Git provider hosting the repository (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization or account name as it appears on the Git provider."),
    repository_name: str = Field(..., alias="repositoryName", description="The repository name as it appears under the organization on the Git provider."),
    branch_name: str = Field(..., alias="branchName", description="The exact name of the branch within the repository to configure."),
    is_enabled: bool | None = Field(None, alias="isEnabled", description="Set to true to enable Codacy analysis on this branch, or false to disable it."),
) -> dict[str, Any] | ToolResult:
    """Enable or disable Codacy analysis for a specific repository branch. Use this to control which branches are actively analyzed within a given organization and repository."""

    # Construct request model with validation
    try:
        _request = _models.UpdateRepositoryBranchConfigurationRequest(
            path=_models.UpdateRepositoryBranchConfigurationRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name, branch_name=branch_name),
            body=_models.UpdateRepositoryBranchConfigurationRequestBody(is_enabled=is_enabled)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for configure_branch_analysis: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/branches/{branchName}", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/branches/{branchName}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("configure_branch_analysis")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("configure_branch_analysis", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="configure_branch_analysis",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: organization
@mcp.tool(
    title="Set Organization Join Mode",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def set_organization_join_mode(
    provider: str = Field(..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The exact name of the organization as it appears on the Git provider."),
    join_mode: Literal["auto", "adminAuto", "request"] = Field(..., alias="joinMode", description="The join mode to apply to the organization: 'auto' allows anyone to join automatically, 'adminAuto' grants automatic access after admin approval, and 'request' requires members to submit a join request."),
) -> dict[str, Any] | ToolResult:
    """Updates the membership join mode for an organization on a specified Git provider, controlling how new members are admitted (automatically, admin-approved automatically, or by request)."""

    # Construct request model with validation
    try:
        _request = _models.UpdateJoinModeRequest(
            path=_models.UpdateJoinModeRequestPath(provider=provider, remote_organization_name=remote_organization_name),
            body=_models.UpdateJoinModeRequestBody(join_mode=join_mode)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for set_organization_join_mode: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/joinMode", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/joinMode"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("set_organization_join_mode")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("set_organization_join_mode", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="set_organization_join_mode",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: repository
@mcp.tool(
    title="Set Default Branch",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def set_default_branch(
    provider: str = Field(..., description="Short code identifying the Git provider hosting the repository."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="Name of the organization on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="Name of the repository within the organization on the Git provider."),
    branch_name: str = Field(..., alias="branchName", description="Name of the branch to designate as the new default; this branch must already be enabled on Codacy."),
) -> dict[str, Any] | ToolResult:
    """Sets the default branch for a specified repository on Codacy. The target branch must already be enabled on Codacy before it can be designated as the default."""

    # Construct request model with validation
    try:
        _request = _models.SetRepositoryBranchAsDefaultRequest(
            path=_models.SetRepositoryBranchAsDefaultRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name, branch_name=branch_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for set_default_branch: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/branches/{branchName}/setDefault", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/branches/{branchName}/setDefault"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("set_default_branch")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("set_default_branch", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="set_default_branch",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: repository
@mcp.tool(
    title="List Branch Required Checks",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_branch_required_checks(
    provider: str = Field(..., description="Short code identifying the Git provider hosting the repository."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization or account name as it appears on the Git provider."),
    repository_name: str = Field(..., alias="repositoryName", description="The repository name within the specified organization on the Git provider."),
    branch_name: str = Field(..., alias="branchName", description="The name of the branch for which required status checks will be retrieved."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the required status checks configured for a specific branch in a repository. These checks must pass before pull requests can be merged into the branch."""

    # Construct request model with validation
    try:
        _request = _models.GetBranchRequiredChecksRequest(
            path=_models.GetBranchRequiredChecksRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name, branch_name=branch_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_branch_required_checks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/branches/{branchName}/required-checks", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/branches/{branchName}/required-checks"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_branch_required_checks")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_branch_required_checks", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_branch_required_checks",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: repository
@mcp.tool(
    title="Add Codacy Badge",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def add_codacy_badge(
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The name of the organization on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="The name of the repository within the specified Git provider organization."),
) -> dict[str, Any] | ToolResult:
    """Creates a pull request that adds the Codacy static analysis badge to the repository's README. Only applies to public GitHub repositories that do not already have the badge; the pull request is created asynchronously and may fail after a successful response."""

    # Construct request model with validation
    try:
        _request = _models.CreateBadgePullRequest(
            path=_models.CreateBadgePullRequestPath(remote_organization_name=remote_organization_name, repository_name=repository_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_codacy_badge: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/gh/{remoteOrganizationName}/repositories/{repositoryName}/badge", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/gh/{remoteOrganizationName}/repositories/{repositoryName}/badge"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_codacy_badge")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_codacy_badge", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_codacy_badge",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: organization
@mcp.tool(
    title="Check Organization Leave Eligibility",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def check_organization_leave_eligibility(
    provider: str = Field(..., description="Short code identifying the Git provider hosting the organization (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform."),
) -> dict[str, Any] | ToolResult:
    """Checks whether the authenticated user is eligible to leave the specified organization, returning either confirmation or the specific reasons preventing them from leaving."""

    # Construct request model with validation
    try:
        _request = _models.CheckIfUserCanLeaveRequest(
            path=_models.CheckIfUserCanLeaveRequestPath(provider=provider, remote_organization_name=remote_organization_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for check_organization_leave_eligibility: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/people/leave/check", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/people/leave/check"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("check_organization_leave_eligibility")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("check_organization_leave_eligibility", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="check_organization_leave_eligibility",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: organization
@mcp.tool(
    title="List Organization Join Requests",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_organization_join_requests(
    provider: str = Field(..., description="The short identifier for the Git provider hosting the organization (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The exact name of the organization as it appears on the Git provider."),
    limit: str | None = Field(None, description="Maximum number of join requests to return in a single response. Accepts values between 1 and 100."),
    search: str | None = Field(None, description="Filters the returned join requests to those matching the provided search string, such as a username or partial name."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all pending requests from users asking to join a specified organization on a Git provider. Supports filtering by search term and pagination via a result limit."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.ListOrganizationJoinRequestsRequest(
            path=_models.ListOrganizationJoinRequestsRequestPath(provider=provider, remote_organization_name=remote_organization_name),
            query=_models.ListOrganizationJoinRequestsRequestQuery(limit=_limit, search=search)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_organization_join_requests: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/join", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/join"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_organization_join_requests")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_organization_join_requests", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_organization_join_requests",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: organization
@mcp.tool(
    title="Join Organization",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def join_organization(
    provider: str = Field(..., description="Short code identifying the Git provider where the organization is hosted. Accepted values include identifiers for GitHub, GitLab, and Bitbucket."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The exact name of the organization as it appears on the specified Git provider. This must match the organization's remote identifier on that platform."),
) -> dict[str, Any] | ToolResult:
    """Joins an organization on a specified Git provider, granting the authenticated user membership in that organization. Requires the provider identifier and the organization's remote name."""

    # Construct request model with validation
    try:
        _request = _models.JoinOrganizationRequest(
            path=_models.JoinOrganizationRequestPath(provider=provider, remote_organization_name=remote_organization_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for join_organization: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/join", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/join"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("join_organization")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("join_organization", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="join_organization",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: organization
@mcp.tool(
    title="Decline Organization Join Requests",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def decline_organization_join_requests(
    provider: str = Field(..., description="Identifier for the Git provider hosting the organization. Use the short code for the target platform (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider. This must match the exact organization identifier used by the provider."),
) -> dict[str, Any] | ToolResult:
    """Declines pending requests from users seeking to join a specified organization on a Git provider. Targets the organization by provider and name, rejecting the specified user emails."""

    # Construct request model with validation
    try:
        _request = _models.DeclineRequestsToJoinOrganizationRequest(
            path=_models.DeclineRequestsToJoinOrganizationRequestPath(provider=provider, remote_organization_name=remote_organization_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for decline_organization_join_requests: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/join", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/join"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("decline_organization_join_requests")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("decline_organization_join_requests", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="decline_organization_join_requests",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: organization
@mcp.tool(
    title="Delete Organization Join Request",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_organization_join_request(
    provider: str = Field(..., description="Short code identifying the Git provider hosting the organization (e.g., GitHub, GitLab, Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform."),
    account_identifier: str = Field(..., alias="accountIdentifier", description="The unique numeric identifier of the user account whose join request should be deleted."),
) -> dict[str, Any] | ToolResult:
    """Cancels or removes a pending request for a user to join an organization on the specified Git provider. Identified by the provider, organization name, and the user's account identifier."""

    _account_identifier = _parse_int(account_identifier)

    # Construct request model with validation
    try:
        _request = _models.DeleteOrganizationJoinRequest(
            path=_models.DeleteOrganizationJoinRequestPath(provider=provider, remote_organization_name=remote_organization_name, account_identifier=_account_identifier)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_organization_join_request: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/join/{accountIdentifier}", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/join/{accountIdentifier}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_organization_join_request")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_organization_join_request", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_organization_join_request",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: repository
@mcp.tool(
    title="Add Repository",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def add_repository(
    repository_full_path: str = Field(..., alias="repositoryFullPath", description="The full path of the repository on the Git provider, beginning at the organization level with each path segment separated by a forward slash."),
    provider: str = Field(..., description="The Git provider that hosts the repository, identifying the source platform where the repository resides."),
) -> dict[str, Any] | ToolResult:
    """Adds a new repository to an existing Codacy organization, enabling code quality analysis and tracking for that repository."""

    # Construct request model with validation
    try:
        _request = _models.AddRepositoryRequest(
            body=_models.AddRepositoryRequestBody(repository_full_path=repository_full_path, provider=provider)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_repository: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/repositories"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_repository")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_repository", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_repository",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: organization
@mcp.tool(
    title="Add Organization",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def add_organization(
    provider: str = Field(..., description="The Git provider that hosts the organization, such as GitHub, GitLab, or Bitbucket."),
    remote_identifier: str = Field(..., alias="remoteIdentifier", description="The unique identifier for the organization on the Git provider, used to locate and link the organization remotely."),
    name: str = Field(..., description="The display name of the organization as it appears on the Git provider."),
    type_: Literal["Account", "Organization"] = Field(..., alias="type", description="Specifies whether the entity is a personal account or a shared organization, which determines available features and permissions."),
    products: list[Literal["quality", "coverage"]] | None = Field(None, description="A list of Codacy products to enable for the organization, where each item represents a product identifier. Order is not significant."),
) -> dict[str, Any] | ToolResult:
    """Registers an organization from a Git provider with Codacy, enabling code quality analysis and management for that organization's repositories."""

    # Construct request model with validation
    try:
        _request = _models.AddOrganizationRequest(
            body=_models.AddOrganizationRequestBody(provider=provider, remote_identifier=remote_identifier, name=name, type_=type_, products=products)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_organization: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/organizations"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_organization")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_organization", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_organization",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: enterprise
@mcp.tool(
    title="Delete Enterprise Token",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_enterprise_token(provider: str = Field(..., description="Identifier for the Git provider whose enterprise token should be deleted. Accepts short provider codes representing supported Git hosting services.")) -> dict[str, Any] | ToolResult:
    """Deletes the stored GitHub Enterprise account token for the authenticated user. Once removed, the token will no longer be used to access enterprise-level resources."""

    # Construct request model with validation
    try:
        _request = _models.DeleteEnterpriseTokenRequest(
            path=_models.DeleteEnterpriseTokenRequestPath(provider=provider)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_enterprise_token: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/user/enterprise/integrations/{provider}", _request.path.model_dump(by_alias=True)) if _request.path else "/user/enterprise/integrations/{provider}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_enterprise_token")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_enterprise_token", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_enterprise_token",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: enterprise
@mcp.tool(
    title="List Enterprise Provider Tokens",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_enterprise_provider_tokens() -> dict[str, Any] | ToolResult:
    """Retrieves all enterprise provider account tokens configured by the authenticated user on Codacy's platform. Useful for auditing or managing active integrations with enterprise identity and source control providers."""

    # Extract parameters for API call
    _http_path = "/user/enterprise/integrations"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_enterprise_provider_tokens")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_enterprise_provider_tokens", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_enterprise_provider_tokens",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: enterprise
@mcp.tool(
    title="Add Enterprise Token",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def add_enterprise_token(
    token: str = Field(..., description="The GitHub Enterprise personal access token with read permissions to be stored and used for authenticating enterprise-level resource requests."),
    provider: str = Field(..., description="The Git hosting provider associated with the enterprise account token being added."),
) -> dict[str, Any] | ToolResult:
    """Adds a GitHub Enterprise account token with read permissions for the authenticated user, enabling access to enterprise-level resources and repositories."""

    # Construct request model with validation
    try:
        _request = _models.AddEnterpriseTokenRequest(
            body=_models.AddEnterpriseTokenRequestBody(token=token, provider=provider)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_enterprise_token: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/user/enterprise/integrations"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_enterprise_token")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_enterprise_token", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_enterprise_token",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: account
@mcp.tool(
    title="List API Tokens",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_api_tokens(limit: str | None = Field(None, description="Maximum number of API tokens to return in a single response. Accepts values between 1 and 100.")) -> dict[str, Any] | ToolResult:
    """Retrieves all API tokens associated with the authenticated user's account. Useful for auditing active tokens or managing programmatic access credentials."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetUserApiTokensRequest(
            query=_models.GetUserApiTokensRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_api_tokens: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/user/tokens"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_api_tokens")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_api_tokens", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_api_tokens",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: account
@mcp.tool(
    title="Create API Token",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_api_token(expires_at: str | None = Field(None, alias="expiresAt", description="Optional expiration date and time for the API token in ISO 8601 format. If omitted, the token does not expire.")) -> dict[str, Any] | ToolResult:
    """Creates a new account-level API token for the authenticated user, optionally scoped to a specific expiration date. API tokens are used to authenticate requests to the Codacy."""

    # Construct request model with validation
    try:
        _request = _models.CreateUserApiTokenRequest(
            body=_models.CreateUserApiTokenRequestBody(expires_at=expires_at)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_api_token: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/user/tokens"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_api_token")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_api_token", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_api_token",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: account
@mcp.tool(
    title="Delete User Token",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_user_token(token_id: str = Field(..., alias="tokenId", description="The unique numeric identifier of the API token to delete. Obtain this ID from the list of tokens associated with the authenticated user's account.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes a specific API token belonging to the authenticated user. Once deleted, any integrations or clients using this token will lose access immediately."""

    _token_id = _parse_int(token_id)

    # Construct request model with validation
    try:
        _request = _models.DeleteUserApiTokenRequest(
            path=_models.DeleteUserApiTokenRequestPath(token_id=_token_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_user_token: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/user/tokens/{tokenId}", _request.path.model_dump(by_alias=True)) if _request.path else "/user/tokens/{tokenId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_user_token")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_user_token", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_user_token",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: billing
@mcp.tool(
    title="Delete Billing Subscription",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_billing_subscription(
    provider: str = Field(..., description="The Git provider hosting the organization, identified by a short code (e.g., GitHub, GitLab, or Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The exact organization name as it appears on the specified Git provider."),
) -> dict[str, Any] | ToolResult:
    """Permanently removes the billing subscription for a specified organization on a given Git provider. This action cancels the organization's current billing plan and cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteSubscriptionRequest(
            path=_models.DeleteSubscriptionRequestPath(provider=provider, remote_organization_name=remote_organization_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_billing_subscription: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/billing/{provider}/{remoteOrganizationName}/subscription", _request.path.model_dump(by_alias=True)) if _request.path else "/billing/{provider}/{remoteOrganizationName}/subscription"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_billing_subscription")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_billing_subscription", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_billing_subscription",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: integrations
@mcp.tool(
    title="List Provider Integrations",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_provider_integrations(limit: str | None = Field(None, description="Maximum number of provider integrations to return in a single response. Accepts values between 1 and 100.")) -> dict[str, Any] | ToolResult:
    """Retrieves a list of provider integrations configured on Codacy's platform. Use this to discover available third-party integrations such as version control, CI, or issue tracking providers."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.ListProviderIntegrationsRequest(
            query=_models.ListProviderIntegrationsRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_provider_integrations: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/provider/integrations"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_provider_integrations")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_provider_integrations", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_provider_integrations",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: admin
@mcp.tool(
    title="Search Entities",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def search_entities(search: str | None = Field(None, description="A search string used to filter results by matching against entity names or IDs such as organizations or repositories.")) -> dict[str, Any] | ToolResult:
    """Search across Codacy entities such as Organizations and Repositories by name or ID. Restricted to Codacy admins only."""

    # Construct request model with validation
    try:
        _request = _models.AdminSearchRequest(
            query=_models.AdminSearchRequestQuery(search=search)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_entities: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/admin"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_entities")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_entities", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_entities",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: admin
@mcp.tool(
    title="Delete Dormant Accounts",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_dormant_accounts(body: str | None = Field(None, description="Raw CSV content exported from GitHub Enterprise identifying the dormant user accounts to be deleted.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes Codacy user accounts identified as dormant, based on a CSV file exported from GitHub Enterprise. Restricted to Codacy administrators only."""

    # Construct request model with validation
    try:
        _request = _models.DeleteDormantAccountsRequest(
            body=_models.DeleteDormantAccountsRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_dormant_accounts: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/admin/dormantAccounts"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "text/plain"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_dormant_accounts")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_dormant_accounts", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_dormant_accounts",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="text/plain",
        headers=_http_headers,
    )

    return _response_data

# Tags: languages
@mcp.tool(
    title="List Tool Supported Languages",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_tool_supported_languages() -> dict[str, Any] | ToolResult:
    """Retrieves the list of programming or spoken languages supported by the currently available tools. Use this to determine valid language options before invoking language-specific tool operations."""

    # Extract parameters for API call
    _http_path = "/languages/tools"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_tool_supported_languages")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_tool_supported_languages", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_tool_supported_languages",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: tools
@mcp.tool(
    title="List Tools",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_tools(limit: str | None = Field(None, description="Maximum number of tools to return in the response. Accepts values between 1 and 100.")) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of available tools. Use the limit parameter to control how many tools are returned in a single response."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.ListToolsRequest(
            query=_models.ListToolsRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_tools: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/tools"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_tools")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_tools", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_tools",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: tools
@mcp.tool(
    title="List Tool Patterns",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_tool_patterns(
    tool_uuid: str = Field(..., alias="toolUuid", description="The unique UUID identifying the tool whose patterns should be retrieved."),
    limit: str | None = Field(None, description="Maximum number of patterns to return in a single response. Accepts values between 1 and 100."),
    enabled: bool | None = Field(None, description="Filters patterns by their enabled status. Set to true to return only enabled patterns, or false to return only disabled patterns. Omit to return all patterns regardless of status."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the list of patterns associated with a specific tool. Supports filtering by enabled status and limiting the number of results returned."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.ListPatternsRequest(
            path=_models.ListPatternsRequestPath(tool_uuid=tool_uuid),
            query=_models.ListPatternsRequestQuery(limit=_limit, enabled=enabled)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_tool_patterns: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/tools/{toolUuid}/patterns", _request.path.model_dump(by_alias=True)) if _request.path else "/tools/{toolUuid}/patterns"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_tool_patterns")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_tool_patterns", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_tool_patterns",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: tools
@mcp.tool(
    title="Submit Pattern Feedback",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def submit_pattern_feedback(
    tool_uuid: str = Field(..., alias="toolUuid", description="The unique UUID identifying the tool whose pattern is being reviewed."),
    pattern_id: str = Field(..., alias="patternId", description="The identifier of the specific pattern within the tool that the feedback applies to."),
    provider: str = Field(..., description="Short code identifying the Git hosting provider (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The name of the organization on the specified Git provider whose context scopes this feedback."),
    reaction_feedback: bool = Field(..., alias="reactionFeedback", description="Boolean vote on the enriched pattern's relevance — true indicates the pattern is considered good or relevant, false indicates it is not."),
    feedback: str | None = Field(None, description="Optional free-text explanation describing why the enriched pattern is considered irrelevant or problematic, providing additional context for the negative feedback."),
) -> dict[str, Any] | ToolResult:
    """Submits user feedback on an enriched tool pattern for a specific organization, indicating whether the pattern is considered relevant and optionally providing a written explanation."""

    # Construct request model with validation
    try:
        _request = _models.AddPatternFeedbackRequest(
            path=_models.AddPatternFeedbackRequestPath(tool_uuid=tool_uuid, pattern_id=pattern_id, provider=provider, remote_organization_name=remote_organization_name),
            body=_models.AddPatternFeedbackRequestBody(reaction_feedback=reaction_feedback, feedback=feedback)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for submit_pattern_feedback: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/tools/{toolUuid}/patterns/{patternId}/organizations/{provider}/{remoteOrganizationName}/feedback", _request.path.model_dump(by_alias=True)) if _request.path else "/tools/{toolUuid}/patterns/{patternId}/organizations/{provider}/{remoteOrganizationName}/feedback"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("submit_pattern_feedback")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("submit_pattern_feedback", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="submit_pattern_feedback",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: tools
@mcp.tool(
    title="Get Pattern",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_pattern(
    tool_uuid: str = Field(..., alias="toolUuid", description="The UUID uniquely identifying the tool whose pattern you want to retrieve."),
    pattern_id: str = Field(..., alias="patternId", description="The identifier of the specific pattern to retrieve, typically referencing a named rule or checker within the tool."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the full definition of a specific pattern associated with a given tool. Use this to inspect pattern rules, configuration, and metadata for a tool's code analysis or style enforcement pattern."""

    # Construct request model with validation
    try:
        _request = _models.GetPatternRequest(
            path=_models.GetPatternRequestPath(tool_uuid=tool_uuid, pattern_id=pattern_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_pattern: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/tools/{toolUuid}/patterns/{patternId}", _request.path.model_dump(by_alias=True)) if _request.path else "/tools/{toolUuid}/patterns/{patternId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_pattern")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_pattern", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_pattern",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: tools
@mcp.tool(
    title="List Duplication Tools",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_duplication_tools() -> dict[str, Any] | ToolResult:
    """Retrieves the complete list of available duplication tools. Use this to discover which duplication tools are accessible for subsequent operations."""

    # Extract parameters for API call
    _http_path = "/duplicationTools"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_duplication_tools")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_duplication_tools", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_duplication_tools",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: tools
@mcp.tool(
    title="List Metrics Tools",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_metrics_tools() -> dict[str, Any] | ToolResult:
    """Retrieves the complete list of available metrics tools. Use this to discover which metrics tools are accessible for monitoring, analysis, or reporting workflows."""

    # Extract parameters for API call
    _http_path = "/metricsTools"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_metrics_tools")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_metrics_tools", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_metrics_tools",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: metrics
@mcp.tool(
    title="Start Organization Metrics Collection",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def start_organization_metrics_collection(
    provider: str = Field(..., description="Short code identifying the Git provider hosting the organization."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider."),
    metrics: list[str] | None = Field(None, description="List of specific metric identifiers to start collecting. If omitted, collection is initiated for all missing metrics. Order is not significant."),
) -> dict[str, Any] | ToolResult:
    """Initiates data collection for any missing metrics within the specified organization. The organization must have metrics support enabled before calling this endpoint."""

    # Construct request model with validation
    try:
        _request = _models.InitiateMetricsForOrganizationRequest(
            path=_models.InitiateMetricsForOrganizationRequestPath(provider=provider, remote_organization_name=remote_organization_name),
            body=_models.InitiateMetricsForOrganizationRequestBody(metrics=metrics)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for start_organization_metrics_collection: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/metrics/start", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/metrics/start"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("start_organization_metrics_collection")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("start_organization_metrics_collection", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="start_organization_metrics_collection",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: metrics
@mcp.tool(
    title="List Ready Metrics",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_ready_metrics(
    provider: str = Field(..., description="Short code identifying the Git provider hosting the organization. Accepted values include identifiers for GitHub, GitLab, and Bitbucket."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider, used to scope the metrics retrieval to that specific organization."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the list of metrics that have completed data collection for a specified organization on a Git provider. Use this to determine which metrics are available and ready to query before requesting detailed metric data."""

    # Construct request model with validation
    try:
        _request = _models.ReadyMetricsForOrganizationRequest(
            path=_models.ReadyMetricsForOrganizationRequestPath(provider=provider, remote_organization_name=remote_organization_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_ready_metrics: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/metrics/ready", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/metrics/ready"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_ready_metrics")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_ready_metrics", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_ready_metrics",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: metrics
@mcp.tool(
    title="Get Latest Metric Value",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def get_latest_metric_value(
    provider: str = Field(..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform."),
    metric_name: str = Field(..., alias="metricName", description="The identifier of the metric to retrieve. Use the readyMetricsForOrganization endpoint to list all available metric names for the organization."),
    repositories: list[str] | None = Field(None, description="Optional list of repository identifiers to scope the metric value to specific repositories within the organization. Order is not significant."),
    segment_ids: list[Annotated[int, Field(json_schema_extra={'format': 'int64'})]] | None = Field(None, alias="segmentIds", description="Optional list of segment IDs used to filter the metric value by predefined organizational segments. Order is not significant."),
    dimensions_filter: list[_models.DimensionsFilter] | None = Field(None, alias="dimensionsFilter", description="Optional list of dimension filters to narrow the metric query by specific dimensional criteria. Order is not significant."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the current (latest) value of an aggregating metric for an organization, such as open issues. Note: this endpoint only supports aggregating metrics and does not work for accumulating metrics like fixed issues."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveLatestMetricValueRequest(
            path=_models.RetrieveLatestMetricValueRequestPath(provider=provider, remote_organization_name=remote_organization_name, metric_name=metric_name),
            body=_models.RetrieveLatestMetricValueRequestBody(dimensions_filter=dimensions_filter,
                entity_filter=_models.RetrieveLatestMetricValueRequestBodyEntityFilter(repositories=repositories, segment_ids=segment_ids) if any(v is not None for v in [repositories, segment_ids]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_latest_metric_value: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/metrics/{metricName}/latest", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/metrics/{metricName}/latest"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_latest_metric_value")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_latest_metric_value", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_latest_metric_value",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: metrics
@mcp.tool(
    title="Get Latest Grouped Metric Values",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def get_latest_grouped_metric_values(
    provider: str = Field(..., description="The Git provider hosting the organization, used to identify which platform to query."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform."),
    metric_name: str = Field(..., alias="metricName", description="The name of the aggregating metric to retrieve latest grouped values for. Use the readyMetricsForOrganization endpoint to list all available metric names."),
    group_by: list[str] = Field(..., alias="groupBy", description="One or more grouping dimensions that determine how metric values are aggregated and returned. Accepted values are `organization`, `repository`, or a metric-specific dimension; for OpenIssues, NewIssues, and FixedIssues the supported dimensions are `category` and `severity`."),
    repositories: list[str] | None = Field(None, description="List of repository names to scope the metric results to. When omitted, results span all repositories in the organization."),
    segment_ids: list[Annotated[int, Field(json_schema_extra={'format': 'int64'})]] | None = Field(None, alias="segmentIds", description="List of segment identifiers to filter the metric results by. When omitted, no segment filtering is applied."),
    dimensions_filter: list[_models.DimensionsFilter] | None = Field(None, alias="dimensionsFilter", description="List of dimension filter values to narrow the metric results. Valid dimension values depend on the requested metric."),
    sort_direction: str | None = Field(None, alias="sortDirection", description="Direction in which the returned metric values are sorted, either ascending or descending."),
    limit: int | None = Field(None, description="Maximum number of grouped metric value entries to return in the response."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the latest values for an aggregating metric grouped by a specified dimension such as organization, repository, or a metric-specific dimension like category or severity. Not compatible with accumulating metrics such as fixed issues."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveLatestMetricGroupedValuesRequest(
            path=_models.RetrieveLatestMetricGroupedValuesRequestPath(provider=provider, remote_organization_name=remote_organization_name, metric_name=metric_name),
            body=_models.RetrieveLatestMetricGroupedValuesRequestBody(filter_=_models.RetrieveLatestMetricGroupedValuesRequestBodyFilter(dimensions_filter=dimensions_filter,
                    entity_filter=_models.RetrieveLatestMetricGroupedValuesRequestBodyFilterEntityFilter(repositories=repositories, segment_ids=segment_ids) if any(v is not None for v in [repositories, segment_ids]) else None) if any(v is not None for v in [repositories, segment_ids, dimensions_filter]) else None,
                group_by=_models.RetrieveLatestMetricGroupedValuesRequestBodyGroupBy(group_by=group_by, sort_direction=sort_direction, limit=limit))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_latest_grouped_metric_values: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/metrics/{metricName}/latest-grouped", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/metrics/{metricName}/latest-grouped"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_latest_grouped_metric_values")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_latest_grouped_metric_values", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_latest_grouped_metric_values",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: metrics
@mcp.tool(
    title="Get Metric Period Value",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def get_metric_period_value(
    provider: str = Field(..., description="The Git provider hosting the organization, specified as a short identifier code."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform."),
    metric_name: str = Field(..., alias="metricName", description="The unique name of the metric to retrieve. Use the readyMetricsForOrganization operation to list all available metric names for the organization."),
    date: str = Field(..., description="The start date of the period for which to retrieve the metric value, in ISO 8601 date-time format."),
    period: Literal["day", "week", "month"] = Field(..., description="The granularity of the time period to retrieve the metric for, determining how the start date is interpreted and the duration of the window."),
    repositories: list[str] | None = Field(None, description="Optional list of repository names to scope the metric retrieval. When omitted, the metric is calculated across all repositories in the organization."),
    segment_ids: list[Annotated[int, Field(json_schema_extra={'format': 'int64'})]] | None = Field(None, alias="segmentIds", description="Optional list of segment IDs to filter the metric data by predefined organizational segments."),
    dimensions_filter: list[_models.DimensionsFilter] | None = Field(None, alias="dimensionsFilter", description="Optional list of dimension filters to narrow the metric data by specific dimensional criteria."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the value of a specific organization metric for a given time period, identified by its start date. Aggregating metrics return the average value for the period, while accumulating metrics return the total historical sum."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveValueForPeriodRequest(
            path=_models.RetrieveValueForPeriodRequestPath(provider=provider, remote_organization_name=remote_organization_name, metric_name=metric_name),
            body=_models.RetrieveValueForPeriodRequestBody(date=date, period=period,
                filter_=_models.RetrieveValueForPeriodRequestBodyFilter(dimensions_filter=dimensions_filter,
                    entity_filter=_models.RetrieveValueForPeriodRequestBodyFilterEntityFilter(repositories=repositories, segment_ids=segment_ids) if any(v is not None for v in [repositories, segment_ids]) else None) if any(v is not None for v in [repositories, segment_ids, dimensions_filter]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_metric_period_value: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/metrics/{metricName}/period", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/metrics/{metricName}/period"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_metric_period_value")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_metric_period_value", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_metric_period_value",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: metrics
@mcp.tool(
    title="Get Grouped Metric Values for Period",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def get_grouped_metric_values_for_period(
    provider: str = Field(..., description="Identifier for the Git provider hosting the organization."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform."),
    metric_name: str = Field(..., alias="metricName", description="The metric to retrieve values for. Use the readyMetricsForOrganization endpoint to list all available metric names for your organization."),
    group_by: list[str] = Field(..., alias="groupBy", description="Dimension by which to group the returned metric values. Accepts 'organization', 'repository', or a metric-specific dimension. For OpenIssues, NewIssues, and FixedIssues, valid dimensions are 'category' and 'severity'."),
    date: str = Field(..., description="The start date of the period for which to retrieve metric values, specified in ISO 8601 date-time format."),
    period: Literal["day", "week", "month"] = Field(..., description="The granularity of the time period to retrieve metric values for, relative to the provided start date."),
    repositories: list[str] | None = Field(None, description="List of repository names to scope the metric results to. When omitted, results include all repositories in the organization."),
    segment_ids: list[Annotated[int, Field(json_schema_extra={'format': 'int64'})]] | None = Field(None, alias="segmentIds", description="List of segment identifiers to filter the metric results by. When omitted, no segment filtering is applied."),
    dimensions_filter: list[_models.DimensionsFilter] | None = Field(None, alias="dimensionsFilter", description="List of dimension filter values to narrow metric results to specific dimension members. Items should match valid dimension values for the requested metric."),
    sort_direction: str | None = Field(None, alias="sortDirection", description="Direction in which to sort the returned grouped values, either ascending or descending."),
    limit: int | None = Field(None, description="Maximum number of grouped value entries to return in the response."),
) -> dict[str, Any] | ToolResult:
    """Retrieves metric values for a specific time period, grouped by a chosen dimension such as organization, repository, or a metric-specific dimension. Aggregating metrics return averages while accumulating metrics return sums representing total historical change."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveGroupedValuesForPeriodRequest(
            path=_models.RetrieveGroupedValuesForPeriodRequestPath(provider=provider, remote_organization_name=remote_organization_name, metric_name=metric_name),
            body=_models.RetrieveGroupedValuesForPeriodRequestBody(date=date, period=period,
                filter_=_models.RetrieveGroupedValuesForPeriodRequestBodyFilter(dimensions_filter=dimensions_filter,
                    entity_filter=_models.RetrieveGroupedValuesForPeriodRequestBodyFilterEntityFilter(repositories=repositories, segment_ids=segment_ids) if any(v is not None for v in [repositories, segment_ids]) else None) if any(v is not None for v in [repositories, segment_ids, dimensions_filter]) else None,
                group_by=_models.RetrieveGroupedValuesForPeriodRequestBodyGroupBy(group_by=group_by, sort_direction=sort_direction, limit=limit))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_grouped_metric_values_for_period: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/metrics/{metricName}/period-grouped", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/metrics/{metricName}/period-grouped"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_grouped_metric_values_for_period")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_grouped_metric_values_for_period", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_grouped_metric_values_for_period",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: metrics
@mcp.tool(
    title="Get Metric Time Range Values",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def get_metric_time_range_values(
    provider: str = Field(..., description="Identifier for the Git provider hosting the organization."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider."),
    metric_name: str = Field(..., alias="metricName", description="The metric to retrieve values for. Use the readyMetricsForOrganization endpoint to discover all available metric names for your organization."),
    group_by: list[str] = Field(..., alias="groupBy", description="Specifies how results are grouped. Accepted values are `organization`, `repository`, or a metric-specific dimension (e.g., `category` or `severity` for issue-related metrics). Order of items is not significant."),
    repositories: list[str] | None = Field(None, description="List of repository names to scope the metric results to. When omitted, results cover all repositories in the organization."),
    segment_ids: list[Annotated[int, Field(json_schema_extra={'format': 'int64'})]] | None = Field(None, alias="segmentIds", description="List of segment IDs to filter the metric results by. When omitted, no segment filtering is applied."),
    dimensions_filter: list[_models.DimensionsFilter] | None = Field(None, alias="dimensionsFilter", description="List of dimension filters to narrow metric results to specific dimension values. Valid dimensions depend on the requested metric."),
    sort_direction: str | None = Field(None, alias="sortDirection", description="Controls the sort direction of the returned results. Applies to the ordering of grouped or time-series data."),
    limit: int | None = Field(None, description="Maximum number of results to return. When omitted, the backend applies a default limit."),
    period: Literal["day", "week", "month"] | None = Field(None, description="Time granularity for grouping metric values. When omitted, the backend selects a default granularity based on the requested time range."),
    time_range: str | None = Field(None, description="Time range in ISO 8601 interval format: 'YYYY-MM-DD/YYYY-MM-DD' (start date / end date)"),
) -> dict[str, Any] | ToolResult:
    """Retrieves time-series values for a specific metric within an organization, grouped by period and optionally by repository, organization, or a metric-specific dimension. Supports filtering by repositories or segments and controlling time granularity via the period parameter."""

    # Call helper functions
    time_range_parsed = parse_time_range(time_range)

    # Construct request model with validation
    try:
        _request = _models.RetrieveTimerangeMetricValuesRequest(
            path=_models.RetrieveTimerangeMetricValuesRequestPath(provider=provider, remote_organization_name=remote_organization_name, metric_name=metric_name),
            body=_models.RetrieveTimerangeMetricValuesRequestBody(period=period, from_=time_range_parsed.get('from') if time_range_parsed else None, to=time_range_parsed.get('to') if time_range_parsed else None,
                filter_=_models.RetrieveTimerangeMetricValuesRequestBodyFilter(dimensions_filter=dimensions_filter,
                    entity_filter=_models.RetrieveTimerangeMetricValuesRequestBodyFilterEntityFilter(repositories=repositories, segment_ids=segment_ids) if any(v is not None for v in [repositories, segment_ids]) else None) if any(v is not None for v in [repositories, segment_ids, dimensions_filter]) else None,
                group_by=_models.RetrieveTimerangeMetricValuesRequestBodyGroupBy(group_by=group_by, sort_direction=sort_direction, limit=limit))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_metric_time_range_values: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/metrics/{metricName}/timerange", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/metrics/{metricName}/timerange"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_metric_time_range_values")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_metric_time_range_values", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_metric_time_range_values",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: metrics
@mcp.tool(
    title="List Ready Enterprise Metrics",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_ready_enterprise_metrics(
    provider: str = Field(..., description="Identifier for the Git provider hosting the enterprise. Specifies which version control platform to target."),
    enterprise_name: str = Field(..., alias="enterpriseName", description="The unique slug (URL-friendly name) identifying the enterprise whose ready metrics are being retrieved."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the list of metrics that have completed data collection for each organization within a specified enterprise. Useful for determining which metrics are available and ready to query before fetching detailed analytics."""

    # Construct request model with validation
    try:
        _request = _models.ReadyMetricsForEnterpriseRequest(
            path=_models.ReadyMetricsForEnterpriseRequestPath(provider=provider, enterprise_name=enterprise_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_ready_enterprise_metrics: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/enterprises/{provider}/{enterpriseName}/metrics/ready", _request.path.model_dump(by_alias=True)) if _request.path else "/enterprises/{provider}/{enterpriseName}/metrics/ready"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_ready_enterprise_metrics")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_ready_enterprise_metrics", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_ready_enterprise_metrics",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: metrics
@mcp.tool(
    title="Get Latest Enterprise Metric Values",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def get_latest_enterprise_metric_values(
    provider: str = Field(..., description="Identifier for the Git provider hosting the enterprise."),
    enterprise_name: str = Field(..., alias="enterpriseName", description="The URL-friendly slug name that uniquely identifies the enterprise."),
    metric_name: str = Field(..., alias="metricName", description="The name of the aggregating metric to retrieve latest values for. Use the readyMetricsForOrganization endpoint to discover all available metric names."),
    dimensions_filter: list[_models.DimensionsFilter] | None = Field(None, alias="dimensionsFilter", description="Optional list of dimension filters to narrow the metric results. Each item specifies a dimension constraint to apply when retrieving metric values across organizations."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the most recent value of a specified aggregating metric (e.g., open issues) for every organization within an enterprise. Note: this endpoint only supports aggregating metrics and does not work for accumulating metrics such as fixed issues."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveLatestMetricValueForEnterpriseRequest(
            path=_models.RetrieveLatestMetricValueForEnterpriseRequestPath(provider=provider, enterprise_name=enterprise_name, metric_name=metric_name),
            body=_models.RetrieveLatestMetricValueForEnterpriseRequestBody(dimensions_filter=dimensions_filter)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_latest_enterprise_metric_values: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/enterprises/{provider}/{enterpriseName}/metrics/{metricName}/latest", _request.path.model_dump(by_alias=True)) if _request.path else "/enterprises/{provider}/{enterpriseName}/metrics/{metricName}/latest"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_latest_enterprise_metric_values")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_latest_enterprise_metric_values", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_latest_enterprise_metric_values",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: metrics
@mcp.tool(
    title="List Enterprise Metric Latest Values Grouped",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def list_enterprise_metric_latest_values_grouped(
    provider: str = Field(..., description="Identifier for the Git provider hosting the enterprise."),
    enterprise_name: str = Field(..., alias="enterpriseName", description="The URL-friendly slug name that uniquely identifies the enterprise."),
    metric_name: str = Field(..., alias="metricName", description="The name of the metric to retrieve latest grouped values for. Must be a non-accumulating metric; use the ready metrics endpoint to discover available metric names."),
    group_by: list[str] = Field(..., alias="groupBy", description="One or more grouping dimensions that determine how results are aggregated. Accepted values are `organization` or a valid metric dimension; for OpenIssues, NewIssues, and FixedIssues the supported dimensions are `category` and `severity`. Grouping by `repository` is not allowed."),
    sort_direction: str | None = Field(None, alias="sortDirection", description="Direction in which the grouped results are sorted, either ascending or descending."),
    limit: int | None = Field(None, description="Maximum number of grouped result entries to return."),
    dimensions_filter: list[_models.DimensionsFilter] | None = Field(None, alias="dimensionsFilter", description="List of dimension values used to filter the grouped results, restricting output to only the specified dimension entries."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the latest values of a non-accumulating aggregating metric for all organizations in an enterprise, grouped by a specified dimension such as organization, category, or severity. Grouping by repository is not supported, and accumulating metrics (e.g., fixed issues) are excluded."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveLatestMetricGroupedValuesForEnterpriseRequest(
            path=_models.RetrieveLatestMetricGroupedValuesForEnterpriseRequestPath(provider=provider, enterprise_name=enterprise_name, metric_name=metric_name),
            body=_models.RetrieveLatestMetricGroupedValuesForEnterpriseRequestBody(group_by=_models.RetrieveLatestMetricGroupedValuesForEnterpriseRequestBodyGroupBy(group_by=group_by, sort_direction=sort_direction, limit=limit),
                filter_=_models.RetrieveLatestMetricGroupedValuesForEnterpriseRequestBodyFilter(dimensions_filter=dimensions_filter) if any(v is not None for v in [dimensions_filter]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_enterprise_metric_latest_values_grouped: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/enterprises/{provider}/{enterpriseName}/metrics/{metricName}/latest-grouped", _request.path.model_dump(by_alias=True)) if _request.path else "/enterprises/{provider}/{enterpriseName}/metrics/{metricName}/latest-grouped"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_enterprise_metric_latest_values_grouped")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_enterprise_metric_latest_values_grouped", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_enterprise_metric_latest_values_grouped",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: metrics
@mcp.tool(
    title="Get Enterprise Metric by Period",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def get_enterprise_metric_by_period(
    provider: str = Field(..., description="Identifier for the Git provider hosting the enterprise."),
    enterprise_name: str = Field(..., alias="enterpriseName", description="The URL-friendly slug name of the enterprise to retrieve metrics for."),
    metric_name: str = Field(..., alias="metricName", description="The name of the metric to retrieve. Use the list available metrics operation to discover valid metric names."),
    date: str = Field(..., description="The start date of the period to retrieve, in ISO 8601 date-time format."),
    period: Literal["day", "week", "month"] = Field(..., description="The granularity of the time period to aggregate metric values over. Must be one of: day, week, or month."),
    dimensions_filter: list[_models.DimensionsFilter] | None = Field(None, alias="dimensionsFilter", description="Optional list of dimension filters to narrow results. Each item specifies a dimension and value to filter by; order is not significant."),
) -> dict[str, Any] | ToolResult:
    """Retrieves metric values for each organization within an enterprise for a specific time period, identified by its start date. Aggregating metrics return the average value, while accumulating metrics return the total historical sum."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveValueForPeriodForEnterpriseRequest(
            path=_models.RetrieveValueForPeriodForEnterpriseRequestPath(provider=provider, enterprise_name=enterprise_name, metric_name=metric_name),
            body=_models.RetrieveValueForPeriodForEnterpriseRequestBody(date=date, period=period,
                filter_=_models.RetrieveValueForPeriodForEnterpriseRequestBodyFilter(dimensions_filter=dimensions_filter) if any(v is not None for v in [dimensions_filter]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_enterprise_metric_by_period: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/enterprises/{provider}/{enterpriseName}/metrics/{metricName}/period", _request.path.model_dump(by_alias=True)) if _request.path else "/enterprises/{provider}/{enterpriseName}/metrics/{metricName}/period"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_enterprise_metric_by_period")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_enterprise_metric_by_period", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_enterprise_metric_by_period",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: metrics
@mcp.tool(
    title="Get Enterprise Metric Grouped by Period",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def get_enterprise_metric_grouped_by_period(
    provider: str = Field(..., description="Identifier for the Git provider hosting the enterprise."),
    enterprise_name: str = Field(..., alias="enterpriseName", description="The URL-friendly slug name that uniquely identifies the enterprise."),
    metric_name: str = Field(..., alias="metricName", description="The name of the metric to retrieve data for. Use the list available metrics operation to discover valid metric names."),
    group_by: list[str] = Field(..., alias="groupBy", description="Specifies how results should be grouped. Accepted values are `organization` or a valid dimension for the requested metric (e.g., `category` or `severity` for issue-related metrics). Grouping by `repository` is not supported."),
    date: str = Field(..., description="The start date and time of the period to retrieve, in ISO 8601 date-time format."),
    period: Literal["day", "week", "month"] = Field(..., description="The granularity of the time period to retrieve data for, determining whether the period spans a day, week, or month from the specified start date."),
    dimensions_filter: list[_models.DimensionsFilter] | None = Field(None, alias="dimensionsFilter", description="Optional list of dimension filters to narrow results. Each item specifies a dimension and value to filter by, limiting the data returned to matching entries."),
    sort_direction: str | None = Field(None, alias="sortDirection", description="Controls the sort order of the returned values, either ascending or descending."),
    limit: int | None = Field(None, description="Maximum number of grouped result entries to return."),
) -> dict[str, Any] | ToolResult:
    """Retrieves metric values grouped by a specified dimension (such as organization or a metric-specific dimension) for all organizations in an enterprise, scoped to a single time period identified by its start date. Aggregating metrics return averages while accumulating metrics return sums representing total historical change."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveGroupedValuesForPeriodForEnterpriseRequest(
            path=_models.RetrieveGroupedValuesForPeriodForEnterpriseRequestPath(provider=provider, enterprise_name=enterprise_name, metric_name=metric_name),
            body=_models.RetrieveGroupedValuesForPeriodForEnterpriseRequestBody(date=date, period=period,
                filter_=_models.RetrieveGroupedValuesForPeriodForEnterpriseRequestBodyFilter(dimensions_filter=dimensions_filter) if any(v is not None for v in [dimensions_filter]) else None,
                group_by=_models.RetrieveGroupedValuesForPeriodForEnterpriseRequestBodyGroupBy(group_by=group_by, sort_direction=sort_direction, limit=limit))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_enterprise_metric_grouped_by_period: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/enterprises/{provider}/{enterpriseName}/metrics/{metricName}/period-grouped", _request.path.model_dump(by_alias=True)) if _request.path else "/enterprises/{provider}/{enterpriseName}/metrics/{metricName}/period-grouped"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_enterprise_metric_grouped_by_period")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_enterprise_metric_grouped_by_period", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_enterprise_metric_grouped_by_period",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: metrics
@mcp.tool(
    title="Get Enterprise Metric Timeseries",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def get_enterprise_metric_timeseries(
    provider: str = Field(..., description="Identifier for the Git provider hosting the enterprise."),
    enterprise_name: str = Field(..., alias="enterpriseName", description="The URL-friendly slug name that uniquely identifies the enterprise."),
    metric_name: str = Field(..., alias="metricName", description="The metric to retrieve time-series data for. Use the readyMetricsForOrganization endpoint to list all available metric names."),
    group_by: list[str] = Field(..., alias="groupBy", description="Specifies how results are grouped in addition to period date. Accepted values are `organization` or a valid dimension for the metric (e.g., `category` or `severity` for OpenIssues, NewIssues, and FixedIssues). Grouping by `repository` is not supported."),
    from_: str = Field(..., alias="from", description="Start of the time range for which metric values are retrieved, inclusive. Must be provided in ISO 8601 date-time format."),
    to: str = Field(..., description="End of the time range for which metric values are retrieved, inclusive. Must be provided in ISO 8601 date-time format."),
    dimensions_filter: list[_models.DimensionsFilter] | None = Field(None, alias="dimensionsFilter", description="Optional list of dimension filters to narrow results. Each item should specify a dimension and its filter value relevant to the requested metric."),
    sort_direction: str | None = Field(None, alias="sortDirection", description="Controls the sort order of returned results. Determines whether values are sorted in ascending or descending order."),
    limit: int | None = Field(None, description="Maximum number of results to return. Use to cap the size of the response payload."),
    period: Literal["day", "week", "month"] | None = Field(None, description="Time granularity for grouping returned data points. If omitted, the backend selects a default granularity based on the requested range."),
) -> dict[str, Any] | ToolResult:
    """Retrieves time-series values for a specific metric across all organizations in an enterprise, grouped by period and optionally by organization or a metric dimension. Aggregating metrics return averages while accumulating metrics return sums; time granularity is controlled via the period parameter."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveTimerangeMetricValuesForEnterpriseRequest(
            path=_models.RetrieveTimerangeMetricValuesForEnterpriseRequestPath(provider=provider, enterprise_name=enterprise_name, metric_name=metric_name),
            body=_models.RetrieveTimerangeMetricValuesForEnterpriseRequestBody(from_=from_, to=to, period=period,
                filter_=_models.RetrieveTimerangeMetricValuesForEnterpriseRequestBodyFilter(dimensions_filter=dimensions_filter) if any(v is not None for v in [dimensions_filter]) else None,
                group_by=_models.RetrieveTimerangeMetricValuesForEnterpriseRequestBodyGroupBy(group_by=group_by, sort_direction=sort_direction, limit=limit))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_enterprise_metric_timeseries: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/enterprises/{provider}/{enterpriseName}/metrics/{metricName}/timerange", _request.path.model_dump(by_alias=True)) if _request.path else "/enterprises/{provider}/{enterpriseName}/metrics/{metricName}/timerange"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_enterprise_metric_timeseries")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_enterprise_metric_timeseries", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_enterprise_metric_timeseries",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: repository
@mcp.tool(
    title="List Repository Files",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_repository_files(
    provider: str = Field(..., description="Short identifier for the Git provider hosting the repository."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization or account name as it appears on the Git provider."),
    repository_name: str = Field(..., alias="repositoryName", description="The repository name as it appears under the organization on the Git provider."),
    branch: str | None = Field(None, description="Name of a branch enabled on Codacy to scope the file analysis results. Defaults to the repository's main branch if omitted."),
    search: str | None = Field(None, description="Filters the returned files to those whose relative path contains this string, enabling partial-match searches."),
    sort: str | None = Field(None, description="Field by which to sort the file list. Accepted values are filename, issues, grade, duplication, complexity, and coverage."),
    direction: str | None = Field(None, description="Order in which to return sorted results — ascending (asc) or descending (desc)."),
    limit: str | None = Field(None, description="Maximum number of files to return per request. Accepts values between 1 and 100."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the most recent analysis results for all tracked files in a repository, equivalent to the Codacy Files page view. Ignored files are excluded from results."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.ListFilesRequest(
            path=_models.ListFilesRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name),
            query=_models.ListFilesRequestQuery(branch=branch, search=search, sort=sort, direction=direction, limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_repository_files: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/files", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/files"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_repository_files")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_repository_files", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_repository_files",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: repository
@mcp.tool(
    title="List Ignored Files",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_ignored_files(
    provider: str = Field(..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="The name of the repository within the specified organization on the Git provider."),
    branch: str | None = Field(None, description="The name of a branch enabled on Codacy to scope the ignored files results; defaults to the main branch configured in Codacy repository settings if omitted."),
    search: str | None = Field(None, description="A string used to filter results, returning only files whose relative path contains this value anywhere within it."),
    limit: str | None = Field(None, description="The maximum number of ignored files to return in a single response, between 1 and 100 inclusive."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the most recently recorded list of ignored files for a repository on Codacy. When a Codacy configuration file is present, the ignored files list is read-only and reflects what was excluded during the last analysis."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.ListIgnoredFilesRequest(
            path=_models.ListIgnoredFilesRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name),
            query=_models.ListIgnoredFilesRequestQuery(branch=branch, search=search, limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_ignored_files: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/ignored-files", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/ignored-files"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_ignored_files")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_ignored_files", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_ignored_files",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: repository
@mcp.tool(
    title="Get File Analysis",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_file_analysis(
    provider: str = Field(..., description="Short code identifying the Git provider hosting the repository, such as gh for GitHub, gl for GitLab, or bb for Bitbucket."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="The name of the repository within the specified organization on the Git provider."),
    file_id: str = Field(..., alias="fileId", description="The unique numeric identifier for a file tied to a specific commit, used to retrieve its analysis and coverage data."),
) -> dict[str, Any] | ToolResult:
    """Retrieves analysis information and coverage metrics for a specific file in a repository. Returns quality insights and coverage data associated with the file at a particular commit."""

    _file_id = _parse_int(file_id)

    # Construct request model with validation
    try:
        _request = _models.GetFileWithAnalysisRequest(
            path=_models.GetFileWithAnalysisRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name, file_id=_file_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_file_analysis: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/files/{fileId}", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/files/{fileId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_file_analysis")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_file_analysis", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_file_analysis",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: repository
@mcp.tool(
    title="List File Clones",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_file_clones(
    provider: str = Field(..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="The name of the repository within the specified Git provider organization."),
    file_id: str = Field(..., alias="fileId", description="The unique numeric identifier for a file tied to a specific commit. This ID is commit-scoped and can be obtained from file listing endpoints."),
    limit: str | None = Field(None, description="Maximum number of duplicate code block results to return. Accepts values between 1 and 100, defaulting to 100 if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all duplicated code blocks (clones) detected within a specific file in a repository. Useful for identifying code duplication issues at the file level."""

    _file_id = _parse_int(file_id)
    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetFileClonesRequest(
            path=_models.GetFileClonesRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name, file_id=_file_id),
            query=_models.GetFileClonesRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_file_clones: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/files/{fileId}/duplication", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/files/{fileId}/duplication"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_file_clones")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_file_clones", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_file_clones",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: repository
@mcp.tool(
    title="List File Issues",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_file_issues(
    provider: str = Field(..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="The name of the repository within the specified Git provider organization."),
    file_id: str = Field(..., alias="fileId", description="The unique identifier for a file tied to a specific commit. This ID is commit-scoped and may differ across commits for the same file path."),
    limit: str | None = Field(None, description="Maximum number of issues to return in a single response. Accepts values between 1 and 100, defaulting to 100 if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the list of code quality issues found in a specific file within a repository. Results are scoped to the file identified by its commit-specific file ID."""

    _file_id = _parse_int(file_id)
    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetFileIssuesRequest(
            path=_models.GetFileIssuesRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name, file_id=_file_id),
            query=_models.GetFileIssuesRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_file_issues: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/files/{fileId}/issues", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/files/{fileId}/issues"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_file_issues")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_file_issues", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_file_issues",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: coding standards
@mcp.tool(
    title="Get AI Risk Checklist",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_ai_risk_checklist(
    provider: str = Field(..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The exact name of the organization as it appears on the specified Git provider."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the AI risk checklist for a specified organization on a Git provider, summarizing potential security, compliance, and quality risks identified by AI analysis."""

    # Construct request model with validation
    try:
        _request = _models.GetAiRiskCheckListRequest(
            path=_models.GetAiRiskCheckListRequestPath(provider=provider, remote_organization_name=remote_organization_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_ai_risk_checklist: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/ai-risk-checklist", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/ai-risk-checklist"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_ai_risk_checklist")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_ai_risk_checklist", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_ai_risk_checklist",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: coding standards
@mcp.tool(
    title="List Coding Standards",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_coding_standards(
    provider: str = Field(..., description="The Git provider hosting the organization, used to identify which platform to query."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider, used to scope the coding standards lookup."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all coding standards for a specified organization, including both active and draft coding standards. Useful for auditing or managing code quality rules across an organization."""

    # Construct request model with validation
    try:
        _request = _models.ListCodingStandardsRequest(
            path=_models.ListCodingStandardsRequestPath(provider=provider, remote_organization_name=remote_organization_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_coding_standards: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/coding-standards", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/coding-standards"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_coding_standards")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_coding_standards", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_coding_standards",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: coding standards
@mcp.tool(
    title="Create Coding Standard",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_coding_standard(
    provider: str = Field(..., description="Short code identifying the Git provider hosting the organization (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider."),
    name: str = Field(..., description="Human-readable name for the new coding standard, used to identify it within the organization."),
    languages: list[str] = Field(..., description="List of programming languages the new coding standard will cover. Order is not significant; each item should be a supported language name."),
    source_repository: str | None = Field(None, alias="sourceRepository", description="Name of an existing repository within the same organization to use as a template for tool and language settings when creating the new coding standard."),
    source_coding_standard: str | None = Field(None, alias="sourceCodingStandard", description="Numeric identifier of an existing coding standard to use as a template, carrying over its enabled repositories and default coding standard status to the new one."),
) -> dict[str, Any] | ToolResult:
    """Creates a new draft coding standard for an organization, optionally using an existing repository or coding standard as a template. The draft must be promoted to become effective; use promoteDraftCodingStandard to complete that step."""

    _source_coding_standard = _parse_int(source_coding_standard)

    # Construct request model with validation
    try:
        _request = _models.CreateCodingStandardRequest(
            path=_models.CreateCodingStandardRequestPath(provider=provider, remote_organization_name=remote_organization_name),
            query=_models.CreateCodingStandardRequestQuery(source_repository=source_repository, source_coding_standard=_source_coding_standard),
            body=_models.CreateCodingStandardRequestBody(name=name, languages=languages)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_coding_standard: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/coding-standards", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/coding-standards"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_coding_standard")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_coding_standard", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_coding_standard",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: coding standards
@mcp.tool(
    title="Create Compliance Standard",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_compliance_standard(
    provider: str = Field(..., description="Short code identifying the Git provider hosting the organization (e.g., GitHub, GitLab, Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform."),
    name: str = Field(..., description="A human-readable display name for the compliance standard being created."),
    compliance_type: Literal["ai-risk"] = Field(..., alias="complianceType", description="The category of compliance standard to create. Currently supports AI risk compliance, which enforces policies around AI-generated code usage."),
) -> dict[str, Any] | ToolResult:
    """Creates a new compliance standard for the specified organization on a Git provider. Use this to establish compliance frameworks, such as AI risk policies, that govern code quality and usage rules across the organization."""

    # Construct request model with validation
    try:
        _request = _models.CreateComplianceStandardRequest(
            path=_models.CreateComplianceStandardRequestPath(provider=provider, remote_organization_name=remote_organization_name),
            body=_models.CreateComplianceStandardRequestBody(name=name, compliance_type=compliance_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_compliance_standard: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/compliance-standards", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/compliance-standards"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_compliance_standard")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_compliance_standard", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_compliance_standard",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: coding standards
@mcp.tool(
    title="Create Coding Standard from Preset",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_coding_standard_from_preset(
    provider: str = Field(..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform."),
    is_default: bool = Field(..., alias="isDefault", description="When set to true, this coding standard will automatically become the default applied to all repositories in the organization."),
    bug_risk: str = Field(..., alias="bugRisk", description="Preset level for bug risk rules, controlling how strictly potential bugs and error-prone patterns are flagged. Accepts values from 1 (least strict) to 4 (most strict)."),
    security: str = Field(..., description="Preset level for security rules, controlling how strictly security vulnerabilities and unsafe coding patterns are flagged. Accepts values from 1 (least strict) to 4 (most strict)."),
    best_practices: str = Field(..., alias="bestPractices", description="Preset level for best practice rules, controlling how strictly deviations from recommended coding conventions are flagged. Accepts values from 1 (least strict) to 4 (most strict)."),
    code_style: str = Field(..., alias="codeStyle", description="Preset level for code style rules, controlling how strictly formatting and stylistic inconsistencies are flagged. Accepts values from 1 (least strict) to 4 (most strict)."),
    documentation: str = Field(..., description="Preset level for documentation rules, controlling how strictly missing or inadequate code documentation is flagged. Accepts values from 1 (least strict) to 4 (most strict)."),
    name: str | None = Field(None, description="A human-readable label for the new coding standard to help identify it within the organization."),
) -> dict[str, Any] | ToolResult:
    """Creates a new coding standard for an organization by selecting preset severity levels across key code quality categories. Optionally sets the new standard as the organization's default."""

    _bug_risk = _parse_int(bug_risk)
    _security = _parse_int(security)
    _best_practices = _parse_int(best_practices)
    _code_style = _parse_int(code_style)
    _documentation = _parse_int(documentation)

    # Construct request model with validation
    try:
        _request = _models.CreateCodingStandardPresetRequest(
            path=_models.CreateCodingStandardPresetRequestPath(provider=provider, remote_organization_name=remote_organization_name),
            body=_models.CreateCodingStandardPresetRequestBody(name=name, is_default=is_default,
                presets=_models.CreateCodingStandardPresetRequestBodyPresets(bug_risk=_bug_risk, security=_security, best_practices=_best_practices, code_style=_code_style, documentation=_documentation))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_coding_standard_from_preset: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/presets-standards", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/presets-standards"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_coding_standard_from_preset")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_coding_standard_from_preset", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_coding_standard_from_preset",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: coding standards
@mcp.tool(
    title="Get Coding Standard",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_coding_standard(
    provider: str = Field(..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The exact name of the organization as it appears on the Git provider platform."),
    coding_standard_id: str = Field(..., alias="codingStandardId", description="The unique numeric identifier of the coding standard to retrieve, as assigned by Codacy."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the details of a specific coding standard within an organization, including its configured rules and settings. Useful for inspecting or auditing code quality policies applied to repositories."""

    _coding_standard_id = _parse_int(coding_standard_id)

    # Construct request model with validation
    try:
        _request = _models.GetCodingStandardRequest(
            path=_models.GetCodingStandardRequestPath(provider=provider, remote_organization_name=remote_organization_name, coding_standard_id=_coding_standard_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_coding_standard: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/coding-standards/{codingStandardId}", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/coding-standards/{codingStandardId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_coding_standard")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_coding_standard", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_coding_standard",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: coding standards
@mcp.tool(
    title="Delete Coding Standard",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_coding_standard(
    provider: str = Field(..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The exact organization name as it appears on the Git provider platform."),
    coding_standard_id: str = Field(..., alias="codingStandardId", description="The unique numeric identifier of the coding standard to delete, as returned when the coding standard was created or listed."),
) -> dict[str, Any] | ToolResult:
    """Permanently deletes a coding standard from the specified organization. This action is irreversible and removes all associated rule configurations."""

    _coding_standard_id = _parse_int(coding_standard_id)

    # Construct request model with validation
    try:
        _request = _models.DeleteCodingStandardRequest(
            path=_models.DeleteCodingStandardRequestPath(provider=provider, remote_organization_name=remote_organization_name, coding_standard_id=_coding_standard_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_coding_standard: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/coding-standards/{codingStandardId}", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/coding-standards/{codingStandardId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_coding_standard")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_coding_standard", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_coding_standard",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: coding standards
@mcp.tool(
    title="Duplicate Coding Standard",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def duplicate_coding_standard(
    provider: str = Field(..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The exact organization name as it appears on the Git provider platform."),
    coding_standard_id: str = Field(..., alias="codingStandardId", description="The unique numeric identifier of the coding standard to duplicate."),
) -> dict[str, Any] | ToolResult:
    """Creates a copy of an existing coding standard within the specified organization, preserving all rules and configurations from the original. Useful for creating variations of a standard without modifying the source."""

    _coding_standard_id = _parse_int(coding_standard_id)

    # Construct request model with validation
    try:
        _request = _models.DuplicateCodingStandardRequest(
            path=_models.DuplicateCodingStandardRequestPath(provider=provider, remote_organization_name=remote_organization_name, coding_standard_id=_coding_standard_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for duplicate_coding_standard: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/coding-standards/{codingStandardId}/duplicate", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/coding-standards/{codingStandardId}/duplicate"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("duplicate_coding_standard")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("duplicate_coding_standard", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="duplicate_coding_standard",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: coding standards
@mcp.tool(
    title="List Coding Standard Tools",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_coding_standard_tools(
    provider: str = Field(..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform."),
    coding_standard_id: str = Field(..., alias="codingStandardId", description="The unique numeric identifier of the coding standard whose tools should be listed."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all tools configured within a specific coding standard for an organization. Useful for auditing which static analysis tools are enabled and their associated rule configurations."""

    _coding_standard_id = _parse_int(coding_standard_id)

    # Construct request model with validation
    try:
        _request = _models.ListCodingStandardToolsRequest(
            path=_models.ListCodingStandardToolsRequestPath(provider=provider, remote_organization_name=remote_organization_name, coding_standard_id=_coding_standard_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_coding_standard_tools: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/coding-standards/{codingStandardId}/tools", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/coding-standards/{codingStandardId}/tools"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_coding_standard_tools")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_coding_standard_tools", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_coding_standard_tools",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: coding standards
@mcp.tool(
    title="Set Default Coding Standard",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def set_default_coding_standard(
    provider: str = Field(..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform."),
    coding_standard_id: str = Field(..., alias="codingStandardId", description="The unique numeric identifier of the coding standard to set or unset as the default."),
    is_default: bool = Field(..., alias="isDefault", description="When true, designates this coding standard as the organization's default; when false, removes its default status."),
) -> dict[str, Any] | ToolResult:
    """Sets or unsets a specific coding standard as the default for an organization, controlling which coding standard is automatically applied to new projects."""

    _coding_standard_id = _parse_int(coding_standard_id)

    # Construct request model with validation
    try:
        _request = _models.SetDefaultCodingStandardRequest(
            path=_models.SetDefaultCodingStandardRequestPath(provider=provider, remote_organization_name=remote_organization_name, coding_standard_id=_coding_standard_id),
            body=_models.SetDefaultCodingStandardRequestBody(is_default=is_default)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for set_default_coding_standard: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/coding-standards/{codingStandardId}/setDefault", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/coding-standards/{codingStandardId}/setDefault"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("set_default_coding_standard")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("set_default_coding_standard", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="set_default_coding_standard",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: coding standards
@mcp.tool(
    title="List Coding Standard Tool Patterns",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_coding_standard_tool_patterns(
    provider: str = Field(..., description="The short identifier for the Git provider hosting the organization."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider."),
    coding_standard_id: str = Field(..., alias="codingStandardId", description="The numeric identifier of the coding standard to retrieve patterns from."),
    tool_uuid: str = Field(..., alias="toolUuid", description="The UUID identifying the specific tool whose patterns should be listed."),
    languages: str | None = Field(None, description="Comma-separated list of programming language names to filter patterns by; only patterns applicable to the specified languages are returned."),
    categories: str | None = Field(None, description="Comma-separated list of pattern categories to filter by. Valid values are `Security`, `ErrorProne`, `CodeStyle`, `Compatibility`, `UnusedCode`, `Complexity`, `Comprehensibility`, `Documentation`, `BestPractice`, and `Performance`."),
    severity_levels: str | None = Field(None, alias="severityLevels", description="Comma-separated list of severity levels to filter by. Valid values are `Error`, `High`, `Warning`, and `Info`."),
    tags: str | None = Field(None, description="Comma-separated list of pattern tags to filter by; only patterns matching at least one of the specified tags are returned."),
    search: str | None = Field(None, description="A search string used to filter patterns by name or description; returns patterns whose metadata contains this value."),
    enabled: bool | None = Field(None, description="When set to `true`, returns only enabled patterns; when set to `false`, returns only disabled patterns. Omit to return patterns regardless of enabled status."),
    recommended: bool | None = Field(None, description="When set to `true`, returns only recommended patterns; when set to `false`, returns only non-recommended patterns. Omit to return patterns regardless of recommended status."),
    sort: str | None = Field(None, description="The field by which to sort the returned patterns. Valid values are `category`, `recommended`, and `severity`."),
    direction: str | None = Field(None, description="The direction in which results are sorted — `asc` for ascending or `desc` for descending."),
    limit: str | None = Field(None, description="Maximum number of patterns to return per request. Must be between 1 and 100 inclusive."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the list of code patterns configured for a specific tool within a coding standard, supporting filtering by language, category, severity, tags, and enabled/recommended status."""

    _coding_standard_id = _parse_int(coding_standard_id)
    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.ListCodingStandardPatternsRequest(
            path=_models.ListCodingStandardPatternsRequestPath(provider=provider, remote_organization_name=remote_organization_name, coding_standard_id=_coding_standard_id, tool_uuid=tool_uuid),
            query=_models.ListCodingStandardPatternsRequestQuery(languages=languages, categories=categories, severity_levels=severity_levels, tags=tags, search=search, enabled=enabled, recommended=recommended, sort=sort, direction=direction, limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_coding_standard_tool_patterns: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/coding-standards/{codingStandardId}/tools/{toolUuid}/patterns", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/coding-standards/{codingStandardId}/tools/{toolUuid}/patterns"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_coding_standard_tool_patterns")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_coding_standard_tool_patterns", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_coding_standard_tool_patterns",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: coding standards
@mcp.tool(
    title="Get Coding Standard Tool Patterns Overview",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_coding_standard_tool_patterns_overview(
    provider: str = Field(..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform."),
    coding_standard_id: str = Field(..., alias="codingStandardId", description="The numeric identifier of the coding standard whose tool patterns overview is being requested."),
    tool_uuid: str = Field(..., alias="toolUuid", description="The UUID uniquely identifying the tool within the coding standard."),
    languages: str | None = Field(None, description="Comma-separated list of programming language names to restrict the overview to patterns applicable to those languages."),
    categories: str | None = Field(None, description="Comma-separated list of pattern categories to filter by. Valid values are Security, ErrorProne, CodeStyle, Compatibility, UnusedCode, Complexity, Comprehensibility, Documentation, BestPractice, and Performance."),
    severity_levels: str | None = Field(None, alias="severityLevels", description="Comma-separated list of severity levels to filter by. Valid values are Error, High, Warning, and Info."),
    tags: str | None = Field(None, description="Comma-separated list of pattern tags to filter results to only patterns associated with those tags."),
    search: str | None = Field(None, description="A search string used to filter patterns by matching against pattern names or descriptions."),
    enabled: bool | None = Field(None, description="When set to true, returns only enabled patterns; when set to false, returns only disabled patterns. Omit to return patterns regardless of enabled state."),
    recommended: bool | None = Field(None, description="When set to true, returns only patterns marked as recommended; when set to false, returns only non-recommended patterns. Omit to return patterns regardless of recommended status."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a summary overview of code patterns for a specific tool within a coding standard, showing counts and distribution across categories, severities, and statuses. Supports filtering by language, category, severity, tags, search term, enabled state, and recommended status."""

    _coding_standard_id = _parse_int(coding_standard_id)

    # Construct request model with validation
    try:
        _request = _models.CodingStandardToolPatternsOverviewRequest(
            path=_models.CodingStandardToolPatternsOverviewRequestPath(provider=provider, remote_organization_name=remote_organization_name, coding_standard_id=_coding_standard_id, tool_uuid=tool_uuid),
            query=_models.CodingStandardToolPatternsOverviewRequestQuery(languages=languages, categories=categories, severity_levels=severity_levels, tags=tags, search=search, enabled=enabled, recommended=recommended)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_coding_standard_tool_patterns_overview: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/coding-standards/{codingStandardId}/tools/{toolUuid}/patterns/overview", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/coding-standards/{codingStandardId}/tools/{toolUuid}/patterns/overview"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_coding_standard_tool_patterns_overview")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_coding_standard_tool_patterns_overview", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_coding_standard_tool_patterns_overview",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: coding standards
@mcp.tool(
    title="Bulk Update Coding Standard Tool Patterns",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def bulk_update_coding_standard_tool_patterns(
    provider: str = Field(..., description="Short code identifying the Git provider hosting the organization."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="Exact name of the organization as it appears on the Git provider."),
    coding_standard_id: str = Field(..., alias="codingStandardId", description="Numeric identifier of the coding standard to update patterns within."),
    tool_uuid: str = Field(..., alias="toolUuid", description="UUID of the tool whose code patterns will be updated within the coding standard."),
    enabled: bool = Field(..., description="Whether to enable or disable the matched code patterns; true enables them and false disables them."),
    languages: str | None = Field(None, description="Comma-separated list of programming language names to restrict which patterns are updated."),
    categories: str | None = Field(None, description="Comma-separated list of pattern categories to restrict which patterns are updated. Valid values are Security, ErrorProne, CodeStyle, Compatibility, UnusedCode, Complexity, Comprehensibility, Documentation, BestPractice, and Performance."),
    severity_levels: str | None = Field(None, alias="severityLevels", description="Comma-separated list of severity levels to restrict which patterns are updated. Valid values are Error, High, Warning, and Info."),
    tags: str | None = Field(None, description="Comma-separated list of pattern tags to restrict which patterns are updated."),
    search: str | None = Field(None, description="Free-text string used to filter patterns by name or description before applying the update."),
    recommended: bool | None = Field(None, description="Restricts the update to patterns based on their recommended status; true targets only recommended patterns, false targets only non-recommended patterns."),
) -> dict[str, Any] | ToolResult:
    """Enable or disable multiple code patterns for a specific tool within a coding standard. Use optional filters to target a subset of patterns by language, category, severity, tags, or search term, or omit all filters to apply the update to every pattern in the tool."""

    _coding_standard_id = _parse_int(coding_standard_id)

    # Construct request model with validation
    try:
        _request = _models.UpdateCodingStandardPatternsRequest(
            path=_models.UpdateCodingStandardPatternsRequestPath(provider=provider, remote_organization_name=remote_organization_name, coding_standard_id=_coding_standard_id, tool_uuid=tool_uuid),
            query=_models.UpdateCodingStandardPatternsRequestQuery(languages=languages, categories=categories, severity_levels=severity_levels, tags=tags, search=search, recommended=recommended),
            body=_models.UpdateCodingStandardPatternsRequestBody(enabled=enabled)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for bulk_update_coding_standard_tool_patterns: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/coding-standards/{codingStandardId}/tools/{toolUuid}/patterns/update", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/coding-standards/{codingStandardId}/tools/{toolUuid}/patterns/update"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("bulk_update_coding_standard_tool_patterns")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("bulk_update_coding_standard_tool_patterns", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="bulk_update_coding_standard_tool_patterns",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: coding standards
@mcp.tool(
    title="Configure Coding Standard Tool",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def configure_coding_standard_tool(
    provider: str = Field(..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform."),
    coding_standard_id: str = Field(..., alias="codingStandardId", description="The numeric identifier of the draft coding standard to configure. Only draft coding standards can be updated."),
    tool_uuid: str = Field(..., alias="toolUuid", description="The UUID uniquely identifying the tool to configure within the coding standard."),
) -> dict[str, Any] | ToolResult:
    """Toggle a tool's enabled status and update its code patterns within a draft coding standard. Only the code patterns included in the request body are modified, with a maximum of 1000 code patterns configurable per call."""

    _coding_standard_id = _parse_int(coding_standard_id)

    # Construct request model with validation
    try:
        _request = _models.UpdateCodingStandardToolConfigurationRequest(
            path=_models.UpdateCodingStandardToolConfigurationRequestPath(provider=provider, remote_organization_name=remote_organization_name, coding_standard_id=_coding_standard_id, tool_uuid=tool_uuid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for configure_coding_standard_tool: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/coding-standards/{codingStandardId}/tools/{toolUuid}", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/coding-standards/{codingStandardId}/tools/{toolUuid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("configure_coding_standard_tool")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("configure_coding_standard_tool", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="configure_coding_standard_tool",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: coding standards
@mcp.tool(
    title="List Coding Standard Repositories",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_coding_standard_repositories(
    provider: str = Field(..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The exact name of the organization as it appears on the Git provider."),
    coding_standard_id: str = Field(..., alias="codingStandardId", description="The unique numeric identifier of the coding standard whose associated repositories should be listed."),
    limit: str | None = Field(None, description="Maximum number of repositories to return per request. Accepts values between 1 and 100; defaults to 100 if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the list of repositories currently using a specific coding standard within an organization. Useful for auditing which repositories are governed by a given set of coding rules."""

    _coding_standard_id = _parse_int(coding_standard_id)
    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.ListCodingStandardRepositoriesRequest(
            path=_models.ListCodingStandardRepositoriesRequestPath(provider=provider, remote_organization_name=remote_organization_name, coding_standard_id=_coding_standard_id),
            query=_models.ListCodingStandardRepositoriesRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_coding_standard_repositories: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/coding-standards/{codingStandardId}/repositories", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/coding-standards/{codingStandardId}/repositories"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_coding_standard_repositories")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_coding_standard_repositories", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_coding_standard_repositories",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: coding standards
@mcp.tool(
    title="Update Coding Standard Repositories",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_coding_standard_repositories(
    provider: str = Field(..., description="Identifier for the Git provider hosting the organization."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider."),
    coding_standard_id: str = Field(..., alias="codingStandardId", description="Unique numeric identifier of the coding standard to update."),
    link: list[str] = Field(..., description="List of repository names to associate with the coding standard. Order is not significant; each item should be the repository's name as it appears on the Git provider."),
    unlink: list[str] = Field(..., description="List of repository names to dissociate from the coding standard. Order is not significant; each item should be the repository's name as it appears on the Git provider."),
) -> dict[str, Any] | ToolResult:
    """Links or unlinks a set of repositories to a specified coding standard within an organization. If the coding standard is in draft state, changes take effect only upon promoting it."""

    _coding_standard_id = _parse_int(coding_standard_id)

    # Construct request model with validation
    try:
        _request = _models.ApplyCodingStandardToRepositoriesRequest(
            path=_models.ApplyCodingStandardToRepositoriesRequestPath(provider=provider, remote_organization_name=remote_organization_name, coding_standard_id=_coding_standard_id),
            body=_models.ApplyCodingStandardToRepositoriesRequestBody(link=link, unlink=unlink)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_coding_standard_repositories: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/coding-standards/{codingStandardId}/repositories", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/coding-standards/{codingStandardId}/repositories"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_coding_standard_repositories")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_coding_standard_repositories", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_coding_standard_repositories",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: gate policies
@mcp.tool(
    title="Set Default Gate Policy",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def set_default_gate_policy(
    provider: str = Field(..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The exact name of the organization as it appears on the Git provider platform."),
    gate_policy_id: str = Field(..., alias="gatePolicyId", description="The unique numeric identifier of the gate policy to designate as the default."),
) -> dict[str, Any] | ToolResult:
    """Sets a specified gate policy as the default for an organization, ensuring it is applied automatically when no other policy is explicitly assigned."""

    _gate_policy_id = _parse_int(gate_policy_id)

    # Construct request model with validation
    try:
        _request = _models.SetDefaultGatePolicyRequest(
            path=_models.SetDefaultGatePolicyRequestPath(provider=provider, remote_organization_name=remote_organization_name, gate_policy_id=_gate_policy_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for set_default_gate_policy: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/gate-policies/{gatePolicyId}/setDefault", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/gate-policies/{gatePolicyId}/setDefault"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("set_default_gate_policy")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("set_default_gate_policy", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="set_default_gate_policy",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: gate policies
@mcp.tool(
    title="Set Default Gate Policy to Codacy Builtin",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def set_default_gate_policy_to_codacy_builtin(
    provider: str = Field(..., description="The Git provider hosting the organization, identified by a short code (e.g., GitHub, GitLab, or Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The exact organization name as it appears on the Git provider platform."),
) -> dict[str, Any] | ToolResult:
    """Sets the built-in Codacy gate policy as the default quality gate for the specified organization, replacing any previously configured default policy."""

    # Construct request model with validation
    try:
        _request = _models.SetCodacyDefaultRequest(
            path=_models.SetCodacyDefaultRequestPath(provider=provider, remote_organization_name=remote_organization_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for set_default_gate_policy_to_codacy_builtin: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/gate-policies/setCodacyDefault", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/gate-policies/setCodacyDefault"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("set_default_gate_policy_to_codacy_builtin")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("set_default_gate_policy_to_codacy_builtin", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="set_default_gate_policy_to_codacy_builtin",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: gate policies
@mcp.tool(
    title="Get Gate Policy",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_gate_policy(
    provider: str = Field(..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The exact name of the organization as it appears on the Git provider platform."),
    gate_policy_id: str = Field(..., alias="gatePolicyId", description="The unique numeric identifier of the gate policy to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the details of a specific gate policy within an organization. Gate policies define quality and security criteria that must be met before code changes are accepted."""

    _gate_policy_id = _parse_int(gate_policy_id)

    # Construct request model with validation
    try:
        _request = _models.GetGatePolicyRequest(
            path=_models.GetGatePolicyRequestPath(provider=provider, remote_organization_name=remote_organization_name, gate_policy_id=_gate_policy_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_gate_policy: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/gate-policies/{gatePolicyId}", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/gate-policies/{gatePolicyId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_gate_policy")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_gate_policy", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_gate_policy",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: gate policies
@mcp.tool(
    title="Update Gate Policy",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_gate_policy(
    provider: str = Field(..., description="The short code identifying the Git provider hosting the organization."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform."),
    gate_policy_id: str = Field(..., alias="gatePolicyId", description="The unique numeric identifier of the gate policy to update."),
    threshold: str = Field(..., description="The maximum number of new issues allowed before the quality gate fails. Must be zero or greater."),
    gate_policy_name: str | None = Field(None, alias="gatePolicyName", description="The human-readable display name for the gate policy."),
    is_default: bool | None = Field(None, alias="isDefault", description="When true, this gate policy becomes the default applied to all repositories in the organization that do not have an explicitly assigned policy."),
    minimum_severity: Literal["Info", "Warning", "High", "Error"] | None = Field(None, alias="minimumSeverity", description="The minimum severity level of issues that count toward the issue threshold. Severity levels map to the UI as: Info → Minor, Warning → Medium, High → High, Error → Critical."),
    security_issue_threshold: str | None = Field(None, alias="securityIssueThreshold", description="The maximum number of new security issues allowed before the quality gate fails. Must be zero or greater."),
    security_issue_minimum_severity: Literal["Info", "Warning", "High", "Error"] | None = Field(None, alias="securityIssueMinimumSeverity", description="The minimum severity level of security issues that count toward the security issue threshold. Severity levels map to the UI as: Info → Minor, Warning → Medium, High → High, Error → Critical."),
    duplication_threshold: str | None = Field(None, alias="duplicationThreshold", description="The maximum number of new duplicated code blocks allowed before the quality gate fails."),
    coverage_threshold_with_decimals: float | None = Field(None, alias="coverageThresholdWithDecimals", description="The minimum required change in coverage percentage; the gate fails if coverage varies by less than this value. Accepts negative values to allow coverage decreases up to a specified amount, with a maximum value of 1.00 (representing 100%)."),
    diff_coverage_threshold: str | None = Field(None, alias="diffCoverageThreshold", description="The minimum required diff coverage percentage; the gate fails if diff coverage falls below this value. Must be between 0 and 100 inclusive."),
    complexity_threshold: str | None = Field(None, alias="complexityThreshold", description="The maximum allowed complexity value introduced by new code; the gate fails if this threshold is exceeded. Must be zero or greater."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing quality gate policy for an organization, allowing modification of thresholds, severity filters, and default status. Quality gate policies define the criteria that must be met for a pull request or commit to pass code quality checks."""

    _gate_policy_id = _parse_int(gate_policy_id)
    _threshold = _parse_int(threshold)
    _security_issue_threshold = _parse_int(security_issue_threshold)
    _duplication_threshold = _parse_int(duplication_threshold)
    _diff_coverage_threshold = _parse_int(diff_coverage_threshold)
    _complexity_threshold = _parse_int(complexity_threshold)

    # Construct request model with validation
    try:
        _request = _models.UpdateGatePolicyRequest(
            path=_models.UpdateGatePolicyRequestPath(provider=provider, remote_organization_name=remote_organization_name, gate_policy_id=_gate_policy_id),
            body=_models.UpdateGatePolicyRequestBody(gate_policy_name=gate_policy_name, is_default=is_default,
                settings=_models.UpdateGatePolicyRequestBodySettings(
                    security_issue_threshold=_security_issue_threshold, security_issue_minimum_severity=security_issue_minimum_severity, duplication_threshold=_duplication_threshold, coverage_threshold_with_decimals=coverage_threshold_with_decimals, diff_coverage_threshold=_diff_coverage_threshold, complexity_threshold=_complexity_threshold,
                    issue_threshold=_models.UpdateGatePolicyRequestBodySettingsIssueThreshold(threshold=_threshold, minimum_severity=minimum_severity)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_gate_policy: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/gate-policies/{gatePolicyId}", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/gate-policies/{gatePolicyId}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_gate_policy")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_gate_policy", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_gate_policy",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: gate policies
@mcp.tool(
    title="Delete Gate Policy",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_gate_policy(
    provider: str = Field(..., description="Short code identifying the Git provider for the organization (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform."),
    gate_policy_id: str = Field(..., alias="gatePolicyId", description="The unique numeric identifier of the gate policy to delete."),
) -> dict[str, Any] | ToolResult:
    """Permanently deletes a specific gate policy from an organization on the specified Git provider. This action is irreversible and removes all associated policy configurations."""

    _gate_policy_id = _parse_int(gate_policy_id)

    # Construct request model with validation
    try:
        _request = _models.DeleteGatePolicyRequest(
            path=_models.DeleteGatePolicyRequestPath(provider=provider, remote_organization_name=remote_organization_name, gate_policy_id=_gate_policy_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_gate_policy: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/gate-policies/{gatePolicyId}", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/gate-policies/{gatePolicyId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_gate_policy")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_gate_policy", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_gate_policy",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: gate policies
@mcp.tool(
    title="List Gate Policies",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_gate_policies(
    provider: str = Field(..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The exact organization name as it appears on the specified Git provider."),
    limit: str | None = Field(None, description="Maximum number of gate policies to return in a single response. Accepts values between 1 and 100, defaulting to 100 if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all gate policies configured for a specified organization on a Git provider. Gate policies define quality or security gates that govern code merging and deployment workflows."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.ListGatePoliciesRequest(
            path=_models.ListGatePoliciesRequestPath(provider=provider, remote_organization_name=remote_organization_name),
            query=_models.ListGatePoliciesRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_gate_policies: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/gate-policies", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/gate-policies"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_gate_policies")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_gate_policies", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_gate_policies",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: gate policies
@mcp.tool(
    title="Create Gate Policy",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_gate_policy(
    provider: str = Field(..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider."),
    gate_policy_name: str = Field(..., alias="gatePolicyName", description="A unique, human-readable name to identify this gate policy within the organization."),
    threshold: str = Field(..., description="The maximum number of new issues allowed before the quality gate fails; must be zero or greater."),
    is_default: bool | None = Field(None, alias="isDefault", description="When true, this policy becomes the default gate policy applied to repositories in the organization that have no explicitly assigned policy."),
    minimum_severity: Literal["Info", "Warning", "High", "Error"] | None = Field(None, alias="minimumSeverity", description="The minimum severity level of issues counted toward the issue threshold. Severity levels map to the UI as: Info → Minor, Warning → Medium, High → High, Error → Critical."),
    security_issue_threshold: str | None = Field(None, alias="securityIssueThreshold", description="The maximum number of new security issues allowed before the quality gate fails; must be zero or greater."),
    security_issue_minimum_severity: Literal["Info", "Warning", "High", "Error"] | None = Field(None, alias="securityIssueMinimumSeverity", description="The minimum severity level of security issues counted toward the security issue threshold. Severity levels map to the UI as: Info → Minor, Warning → Medium, High → High, Error → Critical."),
    duplication_threshold: str | None = Field(None, alias="duplicationThreshold", description="The maximum number of new duplicated blocks allowed before the quality gate fails."),
    coverage_threshold_with_decimals: float | None = Field(None, alias="coverageThresholdWithDecimals", description="The minimum change in coverage percentage required to pass the quality gate; use a negative value to allow coverage to decrease by that amount (e.g., -0.02 allows up to a 2% drop). Must be at most 1.00."),
    diff_coverage_threshold: str | None = Field(None, alias="diffCoverageThreshold", description="The minimum diff coverage percentage required to pass the quality gate; must be between 0 and 100 inclusive."),
    complexity_threshold: str | None = Field(None, alias="complexityThreshold", description="The maximum cumulative complexity value allowed before the quality gate fails; must be zero or greater."),
) -> dict[str, Any] | ToolResult:
    """Creates a new quality gate policy for an organization on a Git provider, defining thresholds for issues, duplication, coverage, and complexity that must be met for a gate to pass."""

    _threshold = _parse_int(threshold)
    _security_issue_threshold = _parse_int(security_issue_threshold)
    _duplication_threshold = _parse_int(duplication_threshold)
    _diff_coverage_threshold = _parse_int(diff_coverage_threshold)
    _complexity_threshold = _parse_int(complexity_threshold)

    # Construct request model with validation
    try:
        _request = _models.CreateGatePolicyRequest(
            path=_models.CreateGatePolicyRequestPath(provider=provider, remote_organization_name=remote_organization_name),
            body=_models.CreateGatePolicyRequestBody(gate_policy_name=gate_policy_name, is_default=is_default,
                settings=_models.CreateGatePolicyRequestBodySettings(
                    security_issue_threshold=_security_issue_threshold, security_issue_minimum_severity=security_issue_minimum_severity, duplication_threshold=_duplication_threshold, coverage_threshold_with_decimals=coverage_threshold_with_decimals, diff_coverage_threshold=_diff_coverage_threshold, complexity_threshold=_complexity_threshold,
                    issue_threshold=_models.CreateGatePolicyRequestBodySettingsIssueThreshold(threshold=_threshold, minimum_severity=minimum_severity)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_gate_policy: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/gate-policies", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/gate-policies"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_gate_policy")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_gate_policy", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_gate_policy",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: organization
@mcp.tool(
    title="Sync Organization Name",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def sync_organization_name(
    provider: str = Field(..., description="Short code identifying the Git provider hosting the organization, such as gh for GitHub, gl for GitLab, or bb for Bitbucket."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider, used to locate the correct organization for synchronization."),
) -> dict[str, Any] | ToolResult:
    """Synchronizes the organization's display name in Codacy with the current name from the specified Git provider, ensuring both systems remain consistent."""

    # Construct request model with validation
    try:
        _request = _models.SyncOrganizationNameRequest(
            path=_models.SyncOrganizationNameRequestPath(provider=provider, remote_organization_name=remote_organization_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for sync_organization_name: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/settings/sync", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/settings/sync"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("sync_organization_name")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("sync_organization_name", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="sync_organization_name",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: organization
@mcp.tool(
    title="Check Submodules Enabled",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def check_submodules_enabled(
    provider: str = Field(..., description="Short code identifying the Git provider for the organization, such as GitHub, GitLab, or Bitbucket."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the specified Git provider."),
) -> dict[str, Any] | ToolResult:
    """Checks whether the submodules option is currently enabled for a specified organization on a Git provider. Useful for verifying organization-level repository settings before performing submodule-dependent operations."""

    # Construct request model with validation
    try:
        _request = _models.CheckSubmodulesRequest(
            path=_models.CheckSubmodulesRequestPath(provider=provider, remote_organization_name=remote_organization_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for check_submodules_enabled: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/settings/submodules/check", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/settings/submodules/check"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("check_submodules_enabled")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("check_submodules_enabled", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="check_submodules_enabled",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: gate policies
@mcp.tool(
    title="List Gate Policy Repositories",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_gate_policy_repositories(
    provider: str = Field(..., description="The Git provider hosting the organization. Use the short identifier for the target provider."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization name as it appears on the Git provider."),
    gate_policy_id: str = Field(..., alias="gatePolicyId", description="The unique numeric identifier of the gate policy whose associated repositories should be listed."),
    limit: str | None = Field(None, description="Maximum number of repositories to return per request. Accepts values between 1 and 100."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all repositories that are following a specific gate policy within an organization. Useful for auditing which repositories are governed by a given quality gate configuration."""

    _gate_policy_id = _parse_int(gate_policy_id)
    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.ListRepositoriesFollowingGatePolicyRequest(
            path=_models.ListRepositoriesFollowingGatePolicyRequestPath(provider=provider, remote_organization_name=remote_organization_name, gate_policy_id=_gate_policy_id),
            query=_models.ListRepositoriesFollowingGatePolicyRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_gate_policy_repositories: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/gate-policies/{gatePolicyId}/repositories", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/gate-policies/{gatePolicyId}/repositories"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_gate_policy_repositories")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_gate_policy_repositories", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_gate_policy_repositories",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: gate policies
@mcp.tool(
    title="Update Gate Policy Repositories",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_gate_policy_repositories(
    provider: str = Field(..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The exact organization name as it appears on the Git provider platform."),
    gate_policy_id: str = Field(..., alias="gatePolicyId", description="The unique numeric identifier of the gate policy to which repositories will be linked or unlinked."),
    link: list[str] = Field(..., description="List of repository names to associate with the gate policy. Order is not significant; each item should be the repository's name as it appears on the Git provider."),
    unlink: list[str] = Field(..., description="List of repository names to disassociate from the gate policy. Order is not significant; each item should be the repository's name as it appears on the Git provider."),
) -> dict[str, Any] | ToolResult:
    """Links or unlinks a set of repositories to a specified gate policy within an organization. Allows simultaneous association and disassociation of repositories in a single request."""

    _gate_policy_id = _parse_int(gate_policy_id)

    # Construct request model with validation
    try:
        _request = _models.ApplyGatePolicyToRepositoriesRequest(
            path=_models.ApplyGatePolicyToRepositoriesRequestPath(provider=provider, remote_organization_name=remote_organization_name, gate_policy_id=_gate_policy_id),
            body=_models.ApplyGatePolicyToRepositoriesRequestBody(link=link, unlink=unlink)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_gate_policy_repositories: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/gate-policies/{gatePolicyId}/repositories", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/gate-policies/{gatePolicyId}/repositories"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_gate_policy_repositories")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_gate_policy_repositories", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_gate_policy_repositories",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: coding standards
@mcp.tool(
    title="Promote Coding Standard",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def promote_coding_standard(
    provider: str = Field(..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform."),
    coding_standard_id: str = Field(..., alias="codingStandardId", description="The unique numeric identifier of the draft coding standard to promote."),
) -> dict[str, Any] | ToolResult:
    """Promotes a draft coding standard to active/effective status for the specified organization, making it the default if it was marked as such. Returns the results of applying the promoted coding standard across the organization's repositories."""

    _coding_standard_id = _parse_int(coding_standard_id)

    # Construct request model with validation
    try:
        _request = _models.PromoteDraftCodingStandardRequest(
            path=_models.PromoteDraftCodingStandardRequestPath(provider=provider, remote_organization_name=remote_organization_name, coding_standard_id=_coding_standard_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for promote_coding_standard: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/coding-standards/{codingStandardId}/promote", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/coding-standards/{codingStandardId}/promote"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("promote_coding_standard")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("promote_coding_standard", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="promote_coding_standard",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: repository
@mcp.tool(
    title="List Repository API Tokens",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_repository_api_tokens(
    provider: str = Field(..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The name of the organization as it appears on the Git provider platform."),
    repository_name: str = Field(..., alias="repositoryName", description="The name of the repository within the specified organization on the Git provider."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all API tokens associated with a specific repository in a Codacy organization. These tokens can be used to authenticate API requests scoped to the repository."""

    # Construct request model with validation
    try:
        _request = _models.ListRepositoryApiTokensRequest(
            path=_models.ListRepositoryApiTokensRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_repository_api_tokens: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/tokens", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/tokens"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_repository_api_tokens")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_repository_api_tokens", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_repository_api_tokens",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: repository
@mcp.tool(
    title="Create Repository Token",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_repository_token(
    provider: str = Field(..., description="Short code identifying the Git provider hosting the repository (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization or account name as it appears on the Git provider platform."),
    repository_name: str = Field(..., alias="repositoryName", description="The repository name within the specified organization on the Git provider."),
) -> dict[str, Any] | ToolResult:
    """Creates a new API token scoped to a specific repository, enabling authenticated access to that repository's resources via the Codacy."""

    # Construct request model with validation
    try:
        _request = _models.CreateRepositoryApiTokenRequest(
            path=_models.CreateRepositoryApiTokenRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_repository_token: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/tokens", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/tokens"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_repository_token")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_repository_token", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_repository_token",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: repository
@mcp.tool(
    title="Delete Repository Token",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_repository_token(
    provider: str = Field(..., description="Short code identifying the Git provider hosting the organization and repository."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization or account name as it appears on the Git provider platform."),
    repository_name: str = Field(..., alias="repositoryName", description="The repository name as it appears under the organization on the Git provider platform."),
    token_id: str = Field(..., alias="tokenId", description="The numeric identifier of the repository API token to delete. Obtain this ID from the list repository tokens operation."),
) -> dict[str, Any] | ToolResult:
    """Permanently deletes a specific API token associated with a repository by its unique ID. This revokes any access previously granted through that token."""

    _token_id = _parse_int(token_id)

    # Construct request model with validation
    try:
        _request = _models.DeleteRepositoryApiTokenRequest(
            path=_models.DeleteRepositoryApiTokenRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name, token_id=_token_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_repository_token: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/tokens/{tokenId}", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/tokens/{tokenId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_repository_token")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_repository_token", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_repository_token",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: repository, coverage
@mcp.tool(
    title="List Coverage Reports",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_coverage_reports(
    provider: str = Field(..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="The name of the repository within the specified Git provider organization."),
    limit: str | None = Field(None, description="Maximum number of coverage reports to return, between 1 and 100 inclusive. Defaults to 100 if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the most recent coverage reports and their statuses for a specified repository. Useful for monitoring code coverage trends and identifying the latest analysis results."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.ListCoverageReportsRequest(
            path=_models.ListCoverageReportsRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name),
            query=_models.ListCoverageReportsRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_coverage_reports: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/coverage/status", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/coverage/status"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_coverage_reports")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_coverage_reports", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_coverage_reports",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: repository, coverage
@mcp.tool(
    title="List Commit Coverage Reports",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_commit_coverage_reports(
    provider: str = Field(..., description="Short code identifying the Git provider hosting the repository (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization or account name as it appears on the Git provider."),
    repository_name: str = Field(..., alias="repositoryName", description="The repository name within the specified organization on the Git provider."),
    commit_uuid: str = Field(..., alias="commitUuid", description="The full commit UUID or SHA hash that uniquely identifies the commit whose coverage reports should be listed."),
    limit: str | None = Field(None, description="Maximum number of coverage reports to return in a single response. Accepts values between 1 and 100."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all code coverage reports associated with a specific commit in a repository. Useful for reviewing coverage data uploaded from multiple sources or tools for a given commit."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.ListCommitCoverageReportsRequest(
            path=_models.ListCommitCoverageReportsRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name, commit_uuid=commit_uuid),
            query=_models.ListCommitCoverageReportsRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_commit_coverage_reports: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/commits/{commitUuid}/coverage/reports", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/commits/{commitUuid}/coverage/reports"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_commit_coverage_reports")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_commit_coverage_reports", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_commit_coverage_reports",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: repository, coverage
@mcp.tool(
    title="Get Commit Coverage Report",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_commit_coverage_report(
    provider: str = Field(..., description="Short code identifying the Git provider hosting the repository (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="The name of the repository within the specified Git provider organization."),
    commit_uuid: str = Field(..., alias="commitUuid", description="The UUID or full SHA hash that uniquely identifies the commit whose coverage report is being retrieved."),
    report_uuid: str = Field(..., alias="reportUuid", description="The UUID that uniquely identifies the specific coverage report to retrieve within the commit."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a specific coverage report and its contents for a given commit in a repository. Use this to inspect detailed coverage data associated with a particular report UUID."""

    # Construct request model with validation
    try:
        _request = _models.GetCoverageReportRequest(
            path=_models.GetCoverageReportRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name, commit_uuid=commit_uuid, report_uuid=report_uuid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_commit_coverage_report: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/commits/{commitUuid}/coverage/reports/{reportUuid}", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/commits/{commitUuid}/coverage/reports/{reportUuid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_commit_coverage_report")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_commit_coverage_report", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_commit_coverage_report",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: file
@mcp.tool(
    title="Get File Content",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_file_content(
    provider: str = Field(..., description="Short code identifying the Git hosting provider (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization or account name as it appears on the Git provider."),
    repository_name: str = Field(..., alias="repositoryName", description="The repository name within the specified organization on the Git provider."),
    file_path: str = Field(..., alias="filePath", description="URL-encoded path to the file from the root of the repository, with path separators and spaces percent-encoded."),
    start_line: str | None = Field(None, alias="startLine", description="The first line of the file to include in the response; when combined with endLine, returns only that line range."),
    end_line: str | None = Field(None, alias="endLine", description="The last line of the file to include in the response; must be greater than or equal to startLine."),
    commit_ref: str | None = Field(None, alias="commitRef", description="A commit reference (branch name, tag, or full commit hash) specifying which version of the file to retrieve; defaults to HEAD of the default branch."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the raw content of a specific file from a repository at a given commit reference, with optional line range filtering. Files exceeding 1MB will return a PayloadTooLarge error."""

    _start_line = _parse_int(start_line)
    _end_line = _parse_int(end_line)

    # Construct request model with validation
    try:
        _request = _models.GetFileContentRequest(
            path=_models.GetFileContentRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name, file_path=file_path),
            query=_models.GetFileContentRequestQuery(start_line=_start_line, end_line=_end_line, commit_ref=commit_ref)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_file_content: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/files/{filePath}/content", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/files/{filePath}/content"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_file_content")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_file_content", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_file_content",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: repository
@mcp.tool(
    title="Get File Coverage",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_file_coverage(
    provider: str = Field(..., description="Short code identifying the Git provider hosting the repository (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="The name of the repository within the specified Git provider organization."),
    file_id: str = Field(..., alias="fileId", description="The unique numeric identifier for a file within a specific commit, used to scope coverage data to that file."),
) -> dict[str, Any] | ToolResult:
    """Retrieves code coverage information for a specific file at the head commit of a repository branch. Returns coverage metrics to help identify tested and untested code areas."""

    _file_id = _parse_int(file_id)

    # Construct request model with validation
    try:
        _request = _models.GetFileCoverageRequest(
            path=_models.GetFileCoverageRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name, file_id=_file_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_file_coverage: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/files/{fileId}/coverage", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/files/{fileId}/coverage"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_file_coverage")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_file_coverage", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_file_coverage",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: repository
@mcp.tool(
    title="Set File Ignored State",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def set_file_ignored_state(
    provider: str = Field(..., description="Short identifier for the Git provider hosting the repository (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization or account name as it appears on the Git provider."),
    repository_name: str = Field(..., alias="repositoryName", description="The repository name as it appears under the organization on the Git provider."),
    ignored: bool = Field(..., description="Set to true to ignore the file (exclude it from analysis) or false to unignore it (re-include it in analysis)."),
    filepath: str = Field(..., description="The relative path to the file within the repository, starting from the repository root."),
) -> dict[str, Any] | ToolResult:
    """Ignore or unignore a specific file in a repository, controlling whether Codacy includes it in analysis. Use this to suppress analysis on generated, vendored, or otherwise irrelevant files."""

    # Construct request model with validation
    try:
        _request = _models.UpdateFileStateRequest(
            path=_models.UpdateFileStateRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name),
            body=_models.UpdateFileStateRequestBody(ignored=ignored, filepath=filepath)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for set_file_ignored_state: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/file", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/file"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("set_file_ignored_state")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("set_file_ignored_state", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="set_file_ignored_state",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: security
@mcp.tool(
    title="Ignore Security Item",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def ignore_security_item(
    provider: str = Field(..., description="Short code identifying the Git provider hosting the organization."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider."),
    srm_item_id: str = Field(..., alias="srmItemId", description="The unique UUID identifier of the security and risk management item to ignore."),
    reason: str | None = Field(None, description="Categorized reason for ignoring the item. Must be one of: AcceptedUse (intentional usage), FalsePositive (incorrect detection), NotExploitable (not actionable in context), TestCode (issue exists in test code), or ExternalCode (issue originates in third-party code)."),
    comment: str | None = Field(None, description="Free-text comment providing additional context or justification for why the security item is being ignored."),
) -> dict[str, Any] | ToolResult:
    """Marks a specific security and risk management (SRM) item as ignored for an organization, optionally providing a reason category and explanatory comment. Useful for suppressing known false positives, accepted risks, or non-applicable findings."""

    # Construct request model with validation
    try:
        _request = _models.IgnoreSecurityItemRequest(
            path=_models.IgnoreSecurityItemRequestPath(provider=provider, remote_organization_name=remote_organization_name, srm_item_id=srm_item_id),
            body=_models.IgnoreSecurityItemRequestBody(reason=reason, comment=comment)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for ignore_security_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/security/items/{srmItemId}/ignore", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/security/items/{srmItemId}/ignore"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("ignore_security_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("ignore_security_item", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="ignore_security_item",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: security
@mcp.tool(
    title="Unignore Security Item",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def unignore_security_item(
    provider: str = Field(..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The exact organization name as it appears on the Git provider platform."),
    srm_item_id: str = Field(..., alias="srmItemId", description="The unique UUID identifying the security and risk management item to be unignored."),
) -> dict[str, Any] | ToolResult:
    """Restores a previously ignored security and risk management item to an active state within the specified organization. Only items that have been explicitly ignored can be unignored."""

    # Construct request model with validation
    try:
        _request = _models.UnignoreSecurityItemRequest(
            path=_models.UnignoreSecurityItemRequestPath(provider=provider, remote_organization_name=remote_organization_name, srm_item_id=srm_item_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for unignore_security_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/security/items/{srmItemId}/unignore", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/security/items/{srmItemId}/unignore"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("unignore_security_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("unignore_security_item", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="unignore_security_item",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: security
@mcp.tool(
    title="Get Security Item",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_security_item(
    provider: str = Field(..., description="The Git provider hosting the organization, specified as a short identifier code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The exact organization name as it appears on the Git provider platform."),
    srm_item_id: str = Field(..., alias="srmItemId", description="The unique identifier of the SRM finding to retrieve, provided as a UUID."),
) -> dict[str, Any] | ToolResult:
    """Retrieves detailed information for a single security and risk management (SRM) finding within an organization. Use this to inspect a specific SRM item by its unique identifier."""

    # Construct request model with validation
    try:
        _request = _models.GetSecurityItemRequest(
            path=_models.GetSecurityItemRequestPath(provider=provider, remote_organization_name=remote_organization_name, srm_item_id=srm_item_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_security_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/security/items/{srmItemId}", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/security/items/{srmItemId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_security_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_security_item", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_security_item",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: security
@mcp.tool(
    title="Search Security Items",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def search_security_items(
    provider: str = Field(..., description="The Git provider hosting the organization. Identifies which platform to query."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider."),
    limit: str | None = Field(None, description="Maximum number of security items to return per request. Must be between 1 and 100."),
    sort: Literal["Status", "DetectedAt"] | None = Field(None, description="The field by which to sort the returned security items."),
    direction: str | None = Field(None, description="The direction in which to sort results, either ascending or descending."),
    repositories: list[str] | None = Field(None, description="List of repository names within the organization to restrict results to. Order is not significant."),
    priorities: list[str] | None = Field(None, description="List of priority levels to filter security items by. Refer to SrmPriority for valid values. Order is not significant."),
    statuses: list[str] | None = Field(None, description="List of statuses to filter security items by. Refer to SrmStatus for valid values. Order is not significant."),
    categories: list[str] | None = Field(None, description="List of security categories to filter by. Use the special value `_other_` to include items that have no assigned security category. Order is not significant."),
    scan_types: list[str] | None = Field(None, alias="scanTypes", description="List of scan types to filter results by, such as static analysis, dependency scanning, secrets detection, and others. Order is not significant."),
    segments: list[Annotated[int, Field(json_schema_extra={'format': 'int64'})]] | None = Field(None, description="List of segment IDs to filter security items by. Segments represent logical groupings within the organization. Order is not significant."),
    dast_target_urls: list[str] | None = Field(None, alias="dastTargetUrls", description="List of DAST target URLs to filter results to only items associated with those targets. Order is not significant."),
    search_text: str | None = Field(None, alias="searchText", description="Free-text search string to match against security item content, such as titles or descriptions."),
) -> dict[str, Any] | ToolResult:
    """Search and filter security and risk management (SRM) items across repositories in an organization. Supports filtering by priority, status, category, scan type, and more to help identify and triage security issues."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.SearchSecurityItemsRequest(
            path=_models.SearchSecurityItemsRequestPath(provider=provider, remote_organization_name=remote_organization_name),
            query=_models.SearchSecurityItemsRequestQuery(limit=_limit, sort=sort, direction=direction),
            body=_models.SearchSecurityItemsRequestBody(repositories=repositories, priorities=priorities, statuses=statuses, categories=categories, scan_types=scan_types, segments=segments, dast_target_urls=dast_target_urls, search_text=search_text)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_security_items: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/security/items/search", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/security/items/search"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_security_items")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_security_items", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_security_items",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: security
@mcp.tool(
    title="Get Security Dashboard Metrics",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def get_security_dashboard_metrics(
    provider: str = Field(..., description="The Git provider hosting the organization. Use the short identifier for the target provider."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider."),
    repositories: list[str] | None = Field(None, description="List of repository names to scope the dashboard metrics to. When omitted, metrics are aggregated across all repositories in the organization."),
    priorities: list[Literal["Low", "Medium", "High", "Critical"]] | None = Field(None, description="List of security issue priority levels to include in the metrics. Refer to SrmPriority for the set of valid priority values."),
    categories: list[str] | None = Field(None, description="List of security categories to filter issues by. Use the special value `_other_` to include issues that have no assigned security category."),
    scan_types: list[str] | None = Field(None, alias="scanTypes", description="List of scan types to restrict metrics to. Multiple scan types can be specified to combine results across different analysis methods."),
    segments: list[Annotated[int, Field(json_schema_extra={'format': 'int64'})]] | None = Field(None, description="List of numeric segment IDs to filter the dashboard metrics by. Segments represent logical groupings of repositories or teams within the organization."),
) -> dict[str, Any] | ToolResult:
    """Retrieves aggregated security and risk management metrics for an organization's dashboard, with optional filtering by repositories, priorities, categories, scan types, and segments."""

    # Construct request model with validation
    try:
        _request = _models.SearchSecurityDashboardRequest(
            path=_models.SearchSecurityDashboardRequestPath(provider=provider, remote_organization_name=remote_organization_name),
            body=_models.SearchSecurityDashboardRequestBody(repositories=repositories, priorities=priorities, categories=categories, scan_types=scan_types, segments=segments)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_security_dashboard_metrics: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/security/dashboard", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/security/dashboard"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_security_dashboard_metrics")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_security_dashboard_metrics", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_security_dashboard_metrics",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: security
@mcp.tool(
    title="Search Repositories with Security Findings",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def search_repositories_with_security_findings(
    provider: str = Field(..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform."),
    repositories: list[str] | None = Field(None, description="List of repository names to narrow results to specific repositories; order is not significant. If omitted, all repositories in the organization are considered."),
    segments: list[Annotated[int, Field(json_schema_extra={'format': 'int64'})]] | None = Field(None, description="List of segment IDs to filter repositories by organizational segment; order is not significant. If omitted, all segments are included."),
) -> dict[str, Any] | ToolResult:
    """Searches repositories within an organization for security findings, returning matching results with their associated security data. If no filters are applied, defaults to returning the 10 repositories with the highest number of findings."""

    # Construct request model with validation
    try:
        _request = _models.SearchSecurityDashboardRepositoriesRequest(
            path=_models.SearchSecurityDashboardRepositoriesRequestPath(provider=provider, remote_organization_name=remote_organization_name),
            body=_models.SearchSecurityDashboardRepositoriesRequestBody(repositories=repositories, segments=segments)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_repositories_with_security_findings: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/security/dashboard/repositories/search", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/security/dashboard/repositories/search"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_repositories_with_security_findings")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_repositories_with_security_findings", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_repositories_with_security_findings",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: security
@mcp.tool(
    title="Search Security Findings History",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def search_security_findings_history(
    provider: str = Field(..., description="The Git provider hosting the organization. Use the short identifier for the target platform."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider."),
    repositories: list[str] | None = Field(None, description="List of repository names to scope the history results to. When omitted, results cover all repositories in the organization. Order is not significant."),
    segments: list[Annotated[int, Field(json_schema_extra={'format': 'int64'})]] | None = Field(None, description="List of segment IDs to filter the history results by. Segments represent logical groupings within the organization. Order is not significant."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the historical evolution of security findings over time for an organization, optionally filtered by specific repositories or segments. Useful for tracking security posture trends and identifying improvements or regressions."""

    # Construct request model with validation
    try:
        _request = _models.SearchSecurityDashboardHistoryRequest(
            path=_models.SearchSecurityDashboardHistoryRequestPath(provider=provider, remote_organization_name=remote_organization_name),
            body=_models.SearchSecurityDashboardHistoryRequestBody(repositories=repositories, segments=segments)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_security_findings_history: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/security/dashboard/history/search", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/security/dashboard/history/search"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_security_findings_history")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_security_findings_history", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_security_findings_history",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: security
@mcp.tool(
    title="Search Security Category Findings",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def search_security_category_finding(
    provider: str = Field(..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform."),
    repositories: list[str] | None = Field(None, description="List of repository names to scope the results to; omit to include all repositories in the organization. Order is not significant."),
    segments: list[Annotated[int, Field(json_schema_extra={'format': 'int64'})]] | None = Field(None, description="List of segment IDs to filter results by; omit to include all segments. Order is not significant."),
) -> dict[str, Any] | ToolResult:
    """Retrieves security categories with their associated findings for an organization, optionally filtered by repositories or segments. If no filters are provided, returns the 10 categories with the highest finding counts."""

    # Construct request model with validation
    try:
        _request = _models.SearchSecurityDashboardCategoriesRequest(
            path=_models.SearchSecurityDashboardCategoriesRequestPath(provider=provider, remote_organization_name=remote_organization_name),
            body=_models.SearchSecurityDashboardCategoriesRequestBody(repositories=repositories, segments=segments)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_security_category_finding: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/security/dashboard/categories/search", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/security/dashboard/categories/search"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_security_category_finding")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_security_category_finding", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_security_category_finding",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: security
@mcp.tool(
    title="Upload DAST Report",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def upload_dast_report(
    provider: str = Field(..., description="Short identifier for the Git provider hosting the organization."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the remote Git provider."),
    tool_name: Literal["ZAP"] = Field(..., alias="toolName", description="The DAST tool that generated the report. Currently only ZAP (OWASP Zed Attack Proxy) is supported."),
    file_: str = Field(..., alias="file", description="Base64-encoded file content for upload. The binary file containing the DAST scan results. For ZAP reports, ensure the `@generated` timestamp field is in English locale using the format `EEE, d MMM yyyy HH:mm:ss` (ZAP's default), otherwise the report will be rejected.", json_schema_extra={'format': 'byte'}),
    report_format: Literal["json"] = Field(..., alias="reportFormat", description="The format of the uploaded report file. Must match the structure expected for the specified tool."),
) -> dict[str, Any] | ToolResult:
    """Uploads a Dynamic Application Security Testing (DAST) scan report to Codacy for the specified organization and tool. The report is parsed and integrated into the organization's security findings dashboard."""

    # Construct request model with validation
    try:
        _request = _models.UploadDastReportRequest(
            path=_models.UploadDastReportRequestPath(provider=provider, remote_organization_name=remote_organization_name, tool_name=tool_name),
            body=_models.UploadDastReportRequestBody(file_=file_, report_format=report_format)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for upload_dast_report: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/security/tools/dast/{toolName}/reports", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/security/tools/dast/{toolName}/reports"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("upload_dast_report")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("upload_dast_report", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="upload_dast_report",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["file"],
        headers=_http_headers,
    )

    return _response_data

# Tags: security
@mcp.tool(
    title="List DAST Reports",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_dast_reports(
    provider: str = Field(..., description="The Git provider hosting the organization, used to identify the source control platform."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider."),
    limit: str | None = Field(None, description="Maximum number of DAST reports to return per request. Accepts values between 1 and 100."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of uploaded DAST (Dynamic Application Security Testing) scan reports for an organization, including their current processing state. Results are sorted by submission date from latest to earliest."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.ListDastReportsRequest(
            path=_models.ListDastReportsRequestPath(provider=provider, remote_organization_name=remote_organization_name),
            query=_models.ListDastReportsRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_dast_reports: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/security/dast/reports", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/security/dast/reports"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_dast_reports")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_dast_reports", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_dast_reports",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: security
@mcp.tool(
    title="List Security Managers",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_security_managers(
    provider: str = Field(..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The exact organization name as it appears on the Git provider."),
    limit: str | None = Field(None, description="Maximum number of security managers to return in a single response. Accepts values between 1 and 100."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the list of organization admins and security managers for a specified organization on a Git provider. Useful for auditing access control and identifying users with elevated security permissions."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.ListSecurityManagersRequest(
            path=_models.ListSecurityManagersRequestPath(provider=provider, remote_organization_name=remote_organization_name),
            query=_models.ListSecurityManagersRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_security_managers: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/security/managers", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/security/managers"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_security_managers")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_security_managers", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_security_managers",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: security
@mcp.tool(
    title="Assign Security Manager",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def assign_security_manager(
    provider: str = Field(..., description="Identifier for the Git provider hosting the organization. Use the short code for the desired provider (e.g., GitHub, GitLab, Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform."),
    user_id: str = Field(..., alias="userId", description="The unique numeric identifier of the organization member to be assigned the Security Manager role. Must correspond to an existing member of the organization."),
) -> dict[str, Any] | ToolResult:
    """Promotes an existing organization member to the Security Manager role within the specified Git provider organization. This grants the user elevated permissions to oversee and manage security-related settings and findings."""

    _user_id = _parse_int(user_id)

    # Construct request model with validation
    try:
        _request = _models.PostSecurityManagerRequest(
            path=_models.PostSecurityManagerRequestPath(provider=provider, remote_organization_name=remote_organization_name),
            body=_models.PostSecurityManagerRequestBody(user_id=_user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for assign_security_manager: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/security/managers", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/security/managers"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("assign_security_manager")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("assign_security_manager", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="assign_security_manager",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: security
@mcp.tool(
    title="Revoke Security Manager",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def revoke_security_manager(
    provider: str = Field(..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The exact name of the organization as it appears on the Git provider."),
    user_id: str = Field(..., alias="userId", description="The unique numeric identifier of the organization member whose Security Manager role is being revoked."),
) -> dict[str, Any] | ToolResult:
    """Revokes the Security Manager role from a specified organization member, removing their elevated security permissions within the organization on the given Git provider."""

    _user_id = _parse_int(user_id)

    # Construct request model with validation
    try:
        _request = _models.DeleteSecurityManagerRequest(
            path=_models.DeleteSecurityManagerRequestPath(provider=provider, remote_organization_name=remote_organization_name, user_id=_user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for revoke_security_manager: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/security/managers/{userId}", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/security/managers/{userId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("revoke_security_manager")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("revoke_security_manager", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="revoke_security_manager",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: security
@mcp.tool(
    title="List Repositories with Security Issues",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_repositories_with_security_issues(
    provider: str = Field(..., description="The Git provider hosting the organization. Use the short identifier for the target provider."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider."),
    limit: str | None = Field(None, description="Maximum number of repositories to return per request. Must be between 1 and 100."),
    segments: str | None = Field(None, description="Narrows results to repositories belonging to the specified segments, provided as a comma-separated list of segment identifiers."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a list of repositories within an organization that have active security issues. Supports pagination and optional filtering by segment identifiers."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.ListSecurityRepositoriesRequest(
            path=_models.ListSecurityRepositoriesRequestPath(provider=provider, remote_organization_name=remote_organization_name),
            query=_models.ListSecurityRepositoriesRequestQuery(limit=_limit, segments=segments)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_repositories_with_security_issues: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/security/repositories", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/security/repositories"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_repositories_with_security_issues")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_repositories_with_security_issues", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_repositories_with_security_issues",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: security
@mcp.tool(
    title="List Security Categories",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_security_categories(
    provider: str = Field(..., description="The Git provider hosting the organization. Identifies which platform to query for security data."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider. Must match the exact organization identifier used on the platform."),
    limit: str | None = Field(None, description="Maximum number of security categories to return per request. Accepts values between 1 and 100."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a list of security subcategories that have active security issues for the specified organization. Useful for identifying which vulnerability categories require attention across the organization's repositories."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.ListSecurityCategoriesRequest(
            path=_models.ListSecurityCategoriesRequestPath(provider=provider, remote_organization_name=remote_organization_name),
            query=_models.ListSecurityCategoriesRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_security_categories: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/security/categories", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/security/categories"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_security_categories")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_security_categories", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_security_categories",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: sbom
@mcp.tool(
    title="Search SBOM Dependencies",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def search_sbom_dependencies(
    provider: str = Field(..., description="The Git provider hosting the organization. Use the short identifier for the target platform."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider."),
    limit: str | None = Field(None, description="Maximum number of dependency records to return per request. Accepts values between 1 and 100."),
    sort_column: Literal["severity", "ossfScore"] | None = Field(None, alias="sortColumn", description="Field by which to sort the returned results. Use `severity` to order by the dependency's vulnerability severity, or `ossfScore` to order by the OpenSSF scorecard score."),
    column_order: Literal["asc", "desc"] | None = Field(None, alias="columnOrder", description="Direction in which to sort the results relative to the chosen sort column. Use `asc` for ascending or `desc` for descending order."),
    text: str | None = Field(None, description="Free-text search string matched against SBOM component fields including package URL (purl) and full component name."),
    repositories: list[str] | None = Field(None, description="List of repository names within the organization to restrict results to. Order is not significant; each item should be a repository name string."),
    segments: list[Annotated[int, Field(json_schema_extra={'format': 'int64'})]] | None = Field(None, description="List of segment IDs to restrict results to. Order is not significant; each item should be an integer segment identifier."),
    finding_severities: list[Literal["Critical", "High", "Medium", "Low"]] | None = Field(None, alias="findingSeverities", description="List of vulnerability severity levels to include in results. Order is not significant; valid values are `Critical`, `High`, `Medium`, and `Low`."),
    risk_categories: list[Literal["Forbidden", "Restricted", "Reciprocal", "Notice", "Permissive", "Unencumbered", "Unknown"]] | None = Field(None, alias="riskCategories", description="List of license risk category labels to filter dependencies by. Order is not significant; each item should be a valid license risk category string."),
) -> dict[str, Any] | ToolResult:
    """Search and filter SBOM (Software Bill of Materials) dependencies used across an organization, returning vulnerability and license risk details for matched components. Supports filtering by severity, repository, segment, and text search against component identifiers."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.SearchSbomDependenciesRequest(
            path=_models.SearchSbomDependenciesRequestPath(provider=provider, remote_organization_name=remote_organization_name),
            query=_models.SearchSbomDependenciesRequestQuery(limit=_limit, sort_column=sort_column, column_order=column_order),
            body=_models.SearchSbomDependenciesRequestBody(text=text, repositories=repositories, segments=segments, finding_severities=finding_severities, risk_categories=risk_categories)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_sbom_dependencies: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/sbom/dependencies/search", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/sbom/dependencies/search"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_sbom_dependencies")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_sbom_dependencies", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_sbom_dependencies",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: sbom
@mcp.tool(
    title="Search Dependency Repositories",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def search_dependency_repositories(
    provider: str = Field(..., description="The Git provider hosting the organization. Use the short identifier for the target platform."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization name as it appears on the Git provider."),
    dependency_full_name: str = Field(..., alias="dependencyFullName", description="The fully qualified name of the SBOM dependency to search for across repositories."),
    limit: str | None = Field(None, description="Maximum number of repositories to return per page. Accepts values between 1 and 100."),
    repositories_filter: list[str] | None = Field(None, alias="repositoriesFilter", description="An optional list of repository names to restrict the search to. Order is not significant; each item should be a repository name string."),
) -> dict[str, Any] | ToolResult:
    """Search for repositories within an organization that use a specific SBOM dependency, returning a paginated list of matches. Optionally filter results to a subset of repositories by name."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.SearchRepositoriesOfSbomDependencyRequest(
            path=_models.SearchRepositoriesOfSbomDependencyRequestPath(provider=provider, remote_organization_name=remote_organization_name),
            query=_models.SearchRepositoriesOfSbomDependencyRequestQuery(limit=_limit),
            body=_models.SearchRepositoriesOfSbomDependencyRequestBody(dependency_full_name=dependency_full_name, repositories_filter=repositories_filter)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_dependency_repositories: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/sbom/dependencies/repositories/search", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/sbom/dependencies/repositories/search"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_dependency_repositories")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_dependency_repositories", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_dependency_repositories",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: sbom
@mcp.tool(
    title="Search SBOM Repositories",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def search_sbom_repositories(
    provider: str = Field(..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The exact organization name as it appears on the specified Git provider."),
    limit: str | None = Field(None, description="Maximum number of repositories to return per request. Accepts values between 1 and 100."),
    body: dict[str, Any] | None = Field(None, description="Optional request body to filter repositories by specific dependencies. Each item should be a dependency identifier in the format 'ecosystem/package-name'."),
) -> dict[str, Any] | ToolResult:
    """Search and list repositories within an organization that contain SBOM (Software Bill of Materials) dependency information, optionally filtering by specific dependencies."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.SearchSbomRepositoriesRequest(
            path=_models.SearchSbomRepositoriesRequestPath(provider=provider, remote_organization_name=remote_organization_name),
            query=_models.SearchSbomRepositoriesRequestQuery(limit=_limit),
            body=_models.SearchSbomRepositoriesRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_sbom_repositories: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/sbom/repositories/search", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/sbom/repositories/search"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_sbom_repositories")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_sbom_repositories", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_sbom_repositories",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: sbom
@mcp.tool(
    title="Get Repository SBOM Download URL",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_repository_sbom_download_url(
    provider: str = Field(..., description="Short code identifying the Git provider hosting the repository."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="The name of the repository within the specified Git provider organization."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a presigned URL for downloading the latest Software Bill of Materials (SBOM) for a specified repository. The URL provides temporary, authenticated access to the SBOM artifact."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositorySbomPresignedUrlRequest(
            path=_models.GetRepositorySbomPresignedUrlRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_repository_sbom_download_url: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/projects/{repositoryName}/sbom", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/projects/{repositoryName}/sbom"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_repository_sbom_download_url")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_repository_sbom_download_url", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_repository_sbom_download_url",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: sbom
@mcp.tool(
    title="Upload Image SBOM",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def upload_image_sbom(
    provider: str = Field(..., description="Short code identifying the Git provider hosting the organization."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider."),
    sbom: str = Field(..., description="Base64-encoded file content for upload. The SBOM file to upload, provided as binary data in either SPDX or CycloneDX format.", json_schema_extra={'format': 'byte'}),
    environment: str | None = Field(None, description="The deployment environment associated with the Docker image (e.g., production, staging), used to contextualize the SBOM within a specific runtime environment."),
    image_ref: str | None = Field(None, description="Full Docker image reference in the format 'repositoryName/imageName:tag'"),
) -> dict[str, Any] | ToolResult:
    """Uploads a Software Bill of Materials (SBOM) for a Docker image to the specified organization, enabling vulnerability tracking and dependency analysis. Accepts SBOM files in SPDX or CycloneDX format."""

    # Call helper functions
    image_ref_parsed = parse_image_ref(image_ref)

    # Construct request model with validation
    try:
        _request = _models.UploadImageSbomRequest(
            path=_models.UploadImageSbomRequestPath(provider=provider, remote_organization_name=remote_organization_name),
            body=_models.UploadImageSbomRequestBody(sbom=sbom, environment=environment, repository_name=image_ref_parsed.get('repositoryName') if image_ref_parsed else None, image_name=image_ref_parsed.get('imageName') if image_ref_parsed else None, tag=image_ref_parsed.get('tag') if image_ref_parsed else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for upload_image_sbom: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/image-sboms", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/image-sboms"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("upload_image_sbom")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("upload_image_sbom", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="upload_image_sbom",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["sbom"],
        headers=_http_headers,
    )

    return _response_data

# Tags: sbom
@mcp.tool(
    title="Delete Image SBOMs",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_image_sboms(
    provider: str = Field(..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The exact name of the organization as it appears on the specified Git provider."),
    image_name: str = Field(..., alias="imageName", description="The name of the container image whose SBOMs should be deleted. Must match the image name used when the SBOMs were originally uploaded."),
) -> dict[str, Any] | ToolResult:
    """Deletes all Software Bill of Materials (SBOMs) associated with a specific container image in the given organization. This action is irreversible and removes all SBOM records for the specified image."""

    # Construct request model with validation
    try:
        _request = _models.DeleteImageSbomsRequest(
            path=_models.DeleteImageSbomsRequestPath(provider=provider, remote_organization_name=remote_organization_name, image_name=image_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_image_sboms: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/image-sboms/{imageName}", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/image-sboms/{imageName}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_image_sboms")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_image_sboms", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_image_sboms",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: sbom
@mcp.tool(
    title="Delete Image Tag SBOM",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_image_tag_sbom(
    provider: str = Field(..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The exact name of the organization as it appears on the specified Git provider."),
    image_name: str = Field(..., alias="imageName", description="The name of the container image whose SBOM entry is being deleted."),
    tag: str = Field(..., description="The specific tag of the container image whose SBOM entry is being deleted."),
) -> dict[str, Any] | ToolResult:
    """Deletes the SBOM (Software Bill of Materials) associated with a specific image and tag combination within an organization. This action permanently removes the SBOM data for the given image/tag pair."""

    # Construct request model with validation
    try:
        _request = _models.DeleteImageTagRequest(
            path=_models.DeleteImageTagRequestPath(provider=provider, remote_organization_name=remote_organization_name, image_name=image_name, tag=tag)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_image_tag_sbom: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/image-sboms/{imageName}/tags/{tag}", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/image-sboms/{imageName}/tags/{tag}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_image_tag_sbom")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_image_tag_sbom", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_image_tag_sbom",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: sbom
@mcp.tool(
    title="List Organization Images",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_organization_images(
    provider: str = Field(..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The exact name of the organization as it appears on the specified Git provider."),
    limit: str | None = Field(None, description="Maximum number of Docker images to return in a single response. Accepts values between 1 and 100, defaulting to 100 if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the list of Docker images available for a specified organization on a Git provider. Supports pagination to control the number of results returned."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.ListOrganizationImagesRequest(
            path=_models.ListOrganizationImagesRequestPath(provider=provider, remote_organization_name=remote_organization_name),
            query=_models.ListOrganizationImagesRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_organization_images: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/images", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/images"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_organization_images")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_organization_images", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_organization_images",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: sbom
@mcp.tool(
    title="List Image Tags",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_image_tags(
    provider: str = Field(..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the specified Git provider."),
    image_name: str = Field(..., alias="imageName", description="The name of the Docker image for which to list available tags."),
    limit: str | None = Field(None, description="Maximum number of image tags to return in a single response. Accepts values between 1 and 100."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all Docker image tags associated with a specific image in an organization's SBOM registry. Results are paginated and scoped to the specified Git provider and organization."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.ListImageTagsRequest(
            path=_models.ListImageTagsRequestPath(provider=provider, remote_organization_name=remote_organization_name, image_name=image_name),
            query=_models.ListImageTagsRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_image_tags: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/images/{imageName}/tags", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/images/{imageName}/tags"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_image_tags")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_image_tags", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_image_tags",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: jira
@mcp.tool(
    title="List Jira Tickets",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_jira_tickets(
    provider: str = Field(..., description="Short code identifying the Git provider hosting the organization."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform."),
    element_type: Literal["issue", "finding", "file", "dependency"] = Field(..., alias="elementType", description="The category of Codacy element whose linked Jira tickets should be retrieved. Must be one of: issue, finding, file, or dependency."),
    element_id: str = Field(..., alias="elementId", description="The unique identifier of the specific Codacy element for which Jira tickets are being requested."),
) -> dict[str, Any] | ToolResult:
    """Retrieves Jira tickets linked to a specific Codacy element (such as an issue, finding, file, or dependency) within an organization. Useful for tracing code quality findings back to their associated Jira work items."""

    # Construct request model with validation
    try:
        _request = _models.GetJiraTicketsRequest(
            path=_models.GetJiraTicketsRequestPath(provider=provider, remote_organization_name=remote_organization_name),
            query=_models.GetJiraTicketsRequestQuery(element_type=element_type, element_id=element_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_jira_tickets: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/integrations/jira/tickets", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/integrations/jira/tickets"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_jira_tickets")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_jira_tickets", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_jira_tickets",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: jira
@mcp.tool(
    title="Create Jira Ticket",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_jira_ticket(
    provider: str = Field(..., description="Short code identifying the Git provider hosting the organization."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider."),
    element_type: Literal["issue", "finding", "file", "dependency"] = Field(..., alias="elementType", description="The category of code element the Jira ticket will be associated with, such as a code issue, security finding, file, or dependency."),
    jira_project_id: str = Field(..., alias="jiraProjectId", description="The unique numeric identifier of the Jira project in which the ticket will be created."),
    create_jira_ticket_elements: list[_models.CreateJiraTicketElement] = Field(..., alias="createJiraTicketElements", description="List of code element identifiers to associate with the Jira ticket; each item should correspond to an element of the specified elementType. Order is not significant."),
    issue_type_id: str = Field(..., alias="issueTypeId", description="The numeric identifier of the Jira issue type (e.g., Bug, Task, Story) to assign to the new ticket."),
    summary: str = Field(..., description="A short, descriptive title summarizing the purpose or content of the Jira ticket."),
    due_date: str | None = Field(None, alias="dueDate", description="Optional target completion date for the ticket, specified in YYYY-MM-DD format."),
    description_heading: str | None = Field(None, description="Optional heading text to appear at the top of the Jira ticket description (rendered as a level-2 heading)"),
    description_body: str | None = Field(None, description="Main body text of the Jira ticket description. Use newlines to separate paragraphs."),
    description_bullet_points: list[Any] | None = Field(None, description="Optional list of bullet point strings to append after the body text"),
) -> dict[str, Any] | ToolResult:
    """Creates a new Jira ticket linked to a specific Codacy organization, associating it with one or more code elements such as issues, findings, files, or dependencies."""

    # Call helper functions
    description = build_adf_description(description_heading, description_body, description_bullet_points)

    _jira_project_id = _parse_int(jira_project_id)
    _issue_type_id = _parse_int(issue_type_id)

    # Construct request model with validation
    try:
        _request = _models.CreateJiraTicketRequest(
            path=_models.CreateJiraTicketRequestPath(provider=provider, remote_organization_name=remote_organization_name),
            body=_models.CreateJiraTicketRequestBody(element_type=element_type, jira_project_id=_jira_project_id, create_jira_ticket_elements=create_jira_ticket_elements, issue_type_id=_issue_type_id, summary=summary, due_date=due_date, description=description)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_jira_ticket: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/integrations/jira/tickets", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/integrations/jira/tickets"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_jira_ticket")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_jira_ticket", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_jira_ticket",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: jira
@mcp.tool(
    title="Unlink Jira Ticket",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def unlink_jira_ticket(
    provider: str = Field(..., description="The Git provider hosting the organization. Use the short identifier for the provider (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The name of the organization as it appears on the Git provider platform."),
    jira_ticket_identifier: str = Field(..., alias="jiraTicketIdentifier", description="The unique numeric identifier of the Jira ticket to unlink. This is the internal Jira ticket ID, not the human-readable issue key."),
    element_type: Literal["issue", "finding", "file", "dependency"] = Field(..., alias="elementType", description="The type of repository element from which the Jira ticket will be unlinked. Must be one of: issue, finding, file, or dependency."),
    element_id: str = Field(..., alias="elementId", description="The unique identifier of the specific repository element (of the type specified by elementType) from which the Jira ticket will be unlinked."),
) -> dict[str, Any] | ToolResult:
    """Removes the association between a Jira ticket and a specific repository element (such as an issue, finding, file, or dependency) within an organization. Use this to detach a previously linked Jira ticket from a code analysis element."""

    _jira_ticket_identifier = _parse_int(jira_ticket_identifier)

    # Construct request model with validation
    try:
        _request = _models.UnlinkRepositoryJiraTicketRequest(
            path=_models.UnlinkRepositoryJiraTicketRequestPath(provider=provider, remote_organization_name=remote_organization_name, jira_ticket_identifier=_jira_ticket_identifier),
            body=_models.UnlinkRepositoryJiraTicketRequestBody(element_type=element_type, element_id=element_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for unlink_jira_ticket: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/integrations/jira/tickets/{jiraTicketIdentifier}", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/integrations/jira/tickets/{jiraTicketIdentifier}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("unlink_jira_ticket")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("unlink_jira_ticket", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="unlink_jira_ticket",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: organization
@mcp.tool(
    title="Get Jira Integration",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_jira_integration(
    provider: str = Field(..., description="Short code identifying the Git provider hosting the organization, such as GitHub, GitLab, or Bitbucket."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the specified Git provider."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the Jira integration configuration for a specified organization on a Git provider. Useful for inspecting whether Jira is connected and reviewing its current settings."""

    # Construct request model with validation
    try:
        _request = _models.GetJiraIntegrationRequest(
            path=_models.GetJiraIntegrationRequestPath(provider=provider, remote_organization_name=remote_organization_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_jira_integration: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/integrations/jira", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/integrations/jira"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_jira_integration")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_jira_integration", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_jira_integration",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: organization
@mcp.tool(
    title="Delete Jira Integration",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_jira_integration(
    provider: str = Field(..., description="Short code identifying the Git provider hosting the organization. Use the provider's abbreviated identifier."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform."),
) -> dict[str, Any] | ToolResult:
    """Removes the Jira integration and all associated resources from the specified organization on a Git provider. This action is irreversible and will disconnect Jira from the organization."""

    # Construct request model with validation
    try:
        _request = _models.DeleteJiraIntegrationRequest(
            path=_models.DeleteJiraIntegrationRequestPath(provider=provider, remote_organization_name=remote_organization_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_jira_integration: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/integrations/jira", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/integrations/jira"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_jira_integration")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_jira_integration", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_jira_integration",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: jira
@mcp.tool(
    title="List Jira Projects",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_jira_projects(
    provider: str = Field(..., description="The short identifier for the Git provider hosting the organization (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The exact organization name as it appears on the specified Git provider."),
    search: str | None = Field(None, description="Optional search string to filter returned Jira projects by name, returning only projects whose names contain the provided value."),
    limit: str | None = Field(None, description="Maximum number of Jira projects to return in a single response, between 1 and 100 inclusive. Defaults to 100 if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the available Jira projects linked to a specific Git provider organization, enabling users to associate repositories with Jira for issue tracking. Supports filtering and pagination to narrow down results."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetAvailableJiraProjectsRequest(
            path=_models.GetAvailableJiraProjectsRequestPath(provider=provider, remote_organization_name=remote_organization_name),
            query=_models.GetAvailableJiraProjectsRequestQuery(search=search, limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_jira_projects: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/integrations/jira/projects", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/integrations/jira/projects"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_jira_projects")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_jira_projects", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_jira_projects",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: jira
@mcp.tool(
    title="List Jira Issue Types",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_jira_issue_types(
    provider: str = Field(..., description="Short code identifying the Git provider for the organization."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform."),
    jira_project_id: str = Field(..., alias="jiraProjectId", description="The unique numeric identifier of the Jira project whose issue types should be retrieved."),
    limit: str | None = Field(None, description="Maximum number of issue types to return per request. Accepts values between 1 and 100."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all available issue types (e.g., Bug, Story, Task) for a specific Jira project, enabling users to select valid types when creating or managing Jira issues linked to a Git organization."""

    _jira_project_id = _parse_int(jira_project_id)
    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetJiraProjectIssueTypesRequest(
            path=_models.GetJiraProjectIssueTypesRequestPath(provider=provider, remote_organization_name=remote_organization_name, jira_project_id=_jira_project_id),
            query=_models.GetJiraProjectIssueTypesRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_jira_issue_types: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/integrations/jira/projects/{jiraProjectId}/issueTypes", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/integrations/jira/projects/{jiraProjectId}/issueTypes"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_jira_issue_types")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_jira_issue_types", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_jira_issue_types",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: jira
@mcp.tool(
    title="List Jira Issue Type Fields",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_jira_issue_type_fields(
    provider: str = Field(..., description="Short code identifying the Git provider hosting the organization."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform."),
    jira_project_id: str = Field(..., alias="jiraProjectId", description="The numeric identifier of the Jira project whose issue type fields are being queried."),
    jira_issue_type_id: str = Field(..., alias="jiraIssueTypeId", description="The identifier of the Jira issue type within the project for which available fields are returned."),
    limit: str | None = Field(None, description="Maximum number of fields to return per response. Accepts values between 1 and 100, defaulting to 100 when omitted."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the available fields for a specific Jira issue type within a project, enabling dynamic form construction when creating or editing issues. Results are scoped to the organization identified by the Git provider and organization name."""

    _jira_project_id = _parse_int(jira_project_id)
    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetJiraProjectIssueFieldsRequest(
            path=_models.GetJiraProjectIssueFieldsRequestPath(provider=provider, remote_organization_name=remote_organization_name, jira_project_id=_jira_project_id, jira_issue_type_id=jira_issue_type_id),
            query=_models.GetJiraProjectIssueFieldsRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_jira_issue_type_fields: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/integrations/jira/projects/{jiraProjectId}/issueTypes/{jiraIssueTypeId}/fields", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/integrations/jira/projects/{jiraProjectId}/issueTypes/{jiraIssueTypeId}/fields"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_jira_issue_type_fields")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_jira_issue_type_fields", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_jira_issue_type_fields",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: organization
@mcp.tool(
    title="Get Slack Integration",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_slack_integration(
    provider: str = Field(..., description="Short code identifying the Git provider hosting the organization. Use the provider's abbreviated identifier."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the Slack integration configuration for a specified organization on a Git provider. Use this to check whether Slack notifications are enabled and review the current integration settings."""

    # Construct request model with validation
    try:
        _request = _models.GetSlackIntegrationRequest(
            path=_models.GetSlackIntegrationRequestPath(provider=provider, remote_organization_name=remote_organization_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_slack_integration: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/integrations/slack", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/integrations/slack"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_slack_integration")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_slack_integration", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_slack_integration",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: repository
@mcp.tool(
    title="Get Pull Request Diff",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_pull_request_diff(
    provider: str = Field(..., description="Short code identifying the Git hosting provider for the repository."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="The name of the repository within the specified organization on the Git provider."),
    pull_request_number: str = Field(..., alias="pullRequestNumber", description="The unique numeric identifier of the pull request within the repository."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the human-readable Git diff for a specific pull request, showing all file changes, additions, and deletions. Useful for reviewing code changes before merging."""

    _pull_request_number = _parse_int(pull_request_number)

    # Construct request model with validation
    try:
        _request = _models.GetPullRequestDiffRequest(
            path=_models.GetPullRequestDiffRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name, pull_request_number=_pull_request_number)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_pull_request_diff: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/pull-requests/{pullRequestNumber}/diff", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/pull-requests/{pullRequestNumber}/diff"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_pull_request_diff")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_pull_request_diff", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_pull_request_diff",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: repository
@mcp.tool(
    title="Get Commit Diff",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_commit_diff(
    provider: str = Field(..., description="Short code identifying the Git hosting provider (e.g., GitHub, GitLab, Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="The name of the repository within the specified organization on the Git provider."),
    commit_uuid: str = Field(..., alias="commitUuid", description="The full SHA hash or UUID that uniquely identifies the commit whose diff should be retrieved."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the human-readable Git diff for a specific commit in a repository, showing all file changes introduced by that commit."""

    # Construct request model with validation
    try:
        _request = _models.GetCommitDiffRequest(
            path=_models.GetCommitDiffRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name, commit_uuid=commit_uuid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_commit_diff: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/commits/{commitUuid}/diff", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/commits/{commitUuid}/diff"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_commit_diff")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_commit_diff", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_commit_diff",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: repository
@mcp.tool(
    title="Get Commit Diff Between",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_commit_diff_between(
    provider: str = Field(..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="The name of the repository within the specified Git provider organization."),
    base_commit_uuid: str = Field(..., alias="baseCommitUuid", description="The SHA or UUID of the base (earlier) commit to use as the starting point of the diff comparison."),
    head_commit_uuid: str = Field(..., alias="headCommitUuid", description="The SHA or UUID of the head (later) commit to use as the ending point of the diff comparison, representing the changes introduced since the base commit."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the human-readable Git diff between a base commit and a head commit in a specified repository, showing all changes introduced between the two points in history."""

    # Construct request model with validation
    try:
        _request = _models.GetDiffBetweenCommitsRequest(
            path=_models.GetDiffBetweenCommitsRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name, base_commit_uuid=base_commit_uuid, head_commit_uuid=head_commit_uuid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_commit_diff_between: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/base/{baseCommitUuid}/head/{headCommitUuid}/diff", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/base/{baseCommitUuid}/head/{headCommitUuid}/diff"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_commit_diff_between")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_commit_diff_between", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_commit_diff_between",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: reports
@mcp.tool(
    title="Export Organization Security Items",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def export_organization_security_items(
    provider: str = Field(..., description="Identifier for the Git provider hosting the organization. Each provider has a short code (e.g., GitHub, GitLab, Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The exact name of the organization as it appears on the specified Git provider. This is the organization's handle or slug, not a display name."),
) -> dict[str, Any] | ToolResult:
    """Generates and downloads a CSV report listing all security and risk management items for a specified organization on a Git provider. Useful for auditing, compliance tracking, and offline analysis of an organization's security posture."""

    # Construct request model with validation
    try:
        _request = _models.GetReportSecurityItemsRequest(
            path=_models.GetReportSecurityItemsRequestPath(provider=provider, remote_organization_name=remote_organization_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for export_organization_security_items: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/reports/organizations/{provider}/{remoteOrganizationName}/security/items", _request.path.model_dump(by_alias=True)) if _request.path else "/reports/organizations/{provider}/{remoteOrganizationName}/security/items"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("export_organization_security_items")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("export_organization_security_items", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="export_organization_security_items",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: reports
@mcp.tool(
    title="Export Security Items CSV",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def export_security_items_csv(
    provider: str = Field(..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform."),
    repositories: list[str] | None = Field(None, description="List of repository names within the organization to restrict results to. Order is not significant."),
    priorities: list[Literal["Low", "Medium", "High", "Critical"]] | None = Field(None, description="List of priority levels to filter security issues by. Valid values are defined by the SrmPriority enumeration. Order is not significant."),
    statuses: list[Literal["Overdue", "OnTrack", "DueSoon", "ClosedOnTime", "ClosedLate", "Ignored"]] | None = Field(None, description="List of statuses to filter security issues by. Valid values are defined by the SrmStatus enumeration. Order is not significant."),
    categories: list[str] | None = Field(None, description="List of security categories to filter by. Use the special value `_other_` to include issues that have no assigned security category. Order is not significant."),
    scan_types: list[str] | None = Field(None, alias="scanTypes", description="List of scan types to restrict results to. Order is not significant."),
    segments: list[Annotated[int, Field(json_schema_extra={'format': 'int64'})]] | None = Field(None, description="List of numeric segment IDs to filter results by. Order is not significant."),
    search_text: str | None = Field(None, alias="searchText", description="Free-text string used to search within security item fields, such as title or description."),
) -> dict[str, Any] | ToolResult:
    """Generates a filtered CSV export of security and risk management items for an organization. Supports filtering by repository, priority, status, category, scan type, segment, and free-text search."""

    # Construct request model with validation
    try:
        _request = _models.SearchReportSecurityItemsRequest(
            path=_models.SearchReportSecurityItemsRequestPath(provider=provider, remote_organization_name=remote_organization_name),
            body=_models.SearchReportSecurityItemsRequestBody(repositories=repositories, priorities=priorities, statuses=statuses, categories=categories, scan_types=scan_types, segments=segments, search_text=search_text)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for export_security_items_csv: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/reports/organizations/{provider}/{remoteOrganizationName}/security/items/search", _request.path.model_dump(by_alias=True)) if _request.path else "/reports/organizations/{provider}/{remoteOrganizationName}/security/items/search"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("export_security_items_csv")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("export_security_items_csv", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="export_security_items_csv",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: analysis
@mcp.tool(
    title="Get Commit",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_commit(commit_id: str = Field(..., alias="commitId", description="The unique numeric identifier of the commit to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves detailed information about a specific commit, including its metadata, changes, and associated data. Use this to inspect the full details of a known commit by its unique identifier."""

    _commit_id = _parse_int(commit_id)

    # Construct request model with validation
    try:
        _request = _models.GetCommitDetailsByCommitIdRequest(
            path=_models.GetCommitDetailsByCommitIdRequestPath(commit_id=_commit_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_commit: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/commits/{commitId}", _request.path.model_dump(by_alias=True)) if _request.path else "/commits/{commitId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_commit")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_commit", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_commit",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: analysis
@mcp.tool(
    title="Check Repository Quickfix Suggestions",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def check_repository_quickfix_suggestions(
    provider: str = Field(..., description="Short code identifying the Git provider hosting the repository."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="Name of the organization or account on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="Name of the repository within the specified Git provider organization."),
    branch: str | None = Field(None, description="Name of a branch enabled on Codacy for this repository. Must be a branch tracked by Codacy, as returned by the listRepositoryBranches endpoint. Defaults to the main branch configured in Codacy repository settings if omitted."),
) -> dict[str, Any] | ToolResult:
    """Checks whether a repository has any available quick fix suggestions for issues on a specified branch. If no branch is provided, the repository's default branch is used."""

    # Construct request model with validation
    try:
        _request = _models.HasQuickfixSuggestionsRequest(
            path=_models.HasQuickfixSuggestionsRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name),
            query=_models.HasQuickfixSuggestionsRequestQuery(branch=branch)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for check_repository_quickfix_suggestions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/issues/hasSuggestions", _request.path.model_dump(by_alias=True)) if _request.path else "/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/issues/hasSuggestions"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("check_repository_quickfix_suggestions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("check_repository_quickfix_suggestions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="check_repository_quickfix_suggestions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: analysis
@mcp.tool(
    title="Get Issue Quickfixes Patch",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_issue_quickfixes_patch(
    provider: str = Field(..., description="Identifier for the Git provider hosting the repository."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="Name of the organization or account on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="Name of the repository within the specified organization on the Git provider."),
    branch: str | None = Field(None, description="Name of a branch enabled on Codacy for this repository. Defaults to the main branch configured in Codacy repository settings if omitted."),
) -> dict[str, Any] | ToolResult:
    """Retrieves quickfix suggestions for repository issues in patch format, allowing automated code corrections to be applied directly. If no branch is specified, the repository's default branch is used."""

    # Construct request model with validation
    try:
        _request = _models.GetQuickfixesPatchRequest(
            path=_models.GetQuickfixesPatchRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name),
            query=_models.GetQuickfixesPatchRequestQuery(branch=branch)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_issue_quickfixes_patch: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/issues/patch", _request.path.model_dump(by_alias=True)) if _request.path else "/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/issues/patch"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_issue_quickfixes_patch")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_issue_quickfixes_patch", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_issue_quickfixes_patch",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: analysis
@mcp.tool(
    title="Get Pull Request Issues Patch",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_pull_request_issues_patch(
    provider: str = Field(..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository."),
    repository_name: str = Field(..., alias="repositoryName", description="The name of the repository within the specified organization on the Git provider."),
    pull_request_number: str = Field(..., alias="pullRequestNumber", description="The unique number identifying the pull request within the repository, as shown in the Git provider's interface."),
) -> dict[str, Any] | ToolResult:
    """Retrieves quickfix patches for issues found in a specific pull request, formatted as a unified diff patch. The patch can be applied directly to resolve detected issues in the pull request's code."""

    _pull_request_number = _parse_int(pull_request_number)

    # Construct request model with validation
    try:
        _request = _models.GetPullRequestQuickfixesPatchRequest(
            path=_models.GetPullRequestQuickfixesPatchRequestPath(provider=provider, remote_organization_name=remote_organization_name, repository_name=repository_name, pull_request_number=_pull_request_number)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_pull_request_issues_patch: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/pull-requests/{pullRequestNumber}/issues/patch", _request.path.model_dump(by_alias=True)) if _request.path else "/analysis/organizations/{provider}/{remoteOrganizationName}/repositories/{repositoryName}/pull-requests/{pullRequestNumber}/issues/patch"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_pull_request_issues_patch")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_pull_request_issues_patch", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_pull_request_issues_patch",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: organization
@mcp.tool(
    title="List Organization Audit Logs",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_organization_audit_logs(
    provider: str = Field(..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider."),
    from_: str | None = Field(None, alias="from", description="Start of the audit log time window as a Unix epoch timestamp in milliseconds. If omitted, defaults to the earliest available audit log entry."),
    to: str | None = Field(None, description="End of the audit log time window as a Unix epoch timestamp in milliseconds. If omitted, defaults to the current time."),
) -> dict[str, Any] | ToolResult:
    """Retrieves audit logs for the specified organization within an optional time range. Requires Business plan and organization admin or manager role."""

    _from_ = _parse_int(from_)
    _to = _parse_int(to)

    # Construct request model with validation
    try:
        _request = _models.ListAuditLogsForOrganizationRequest(
            path=_models.ListAuditLogsForOrganizationRequestPath(provider=provider, remote_organization_name=remote_organization_name),
            query=_models.ListAuditLogsForOrganizationRequestQuery(from_=_from_, to=_to)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_organization_audit_logs: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/audit", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/audit"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_organization_audit_logs")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_organization_audit_logs", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_organization_audit_logs",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: segments
@mcp.tool(
    title="Get Segment Sync Status",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_segment_sync_status(
    provider: str = Field(..., description="Identifier for the Git provider hosting the organization. Use the short code for the desired platform (e.g., GitHub, GitLab, or Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the specified Git provider. This must match the exact remote organization name used by the provider."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the current synchronization status of segments for a specified organization on a Git provider. Useful for monitoring whether segment data is up to date or still processing."""

    # Construct request model with validation
    try:
        _request = _models.GetSegmentsSyncStatusRequest(
            path=_models.GetSegmentsSyncStatusRequestPath(provider=provider, remote_organization_name=remote_organization_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_segment_sync_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/segments/sync", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/segments/sync"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_segment_sync_status")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_segment_sync_status", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_segment_sync_status",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: segments
@mcp.tool(
    title="List Segment Keys",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_segment_keys(
    provider: str = Field(..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The exact organization name as it appears on the specified Git provider."),
    limit: str | None = Field(None, description="Maximum number of segment keys to return in a single response. Accepts values between 1 and 100, defaulting to 100 if not specified."),
    search: str | None = Field(None, description="Narrows results to segment keys whose names contain the provided string, enabling targeted lookups within large organizations."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the available segment keys for a specified organization on a Git provider. Segment keys can be filtered by search term and support pagination via a configurable result limit."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetSegmentsKeysRequest(
            path=_models.GetSegmentsKeysRequestPath(provider=provider, remote_organization_name=remote_organization_name),
            query=_models.GetSegmentsKeysRequestQuery(limit=_limit, search=search)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_segment_keys: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/segments/keys", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/segments/keys"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_segment_keys")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_segment_keys", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_segment_keys",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: segments
@mcp.tool(
    title="List Segment Keys with IDs",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_segment_keys_with_ids(
    provider: str = Field(..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the specified Git provider."),
    limit: str | None = Field(None, description="Maximum number of segment key records to return in a single response. Accepts values between 1 and 100."),
    search: str | None = Field(None, description="Filters the returned segment keys to those matching the provided search string, useful for locating specific segments by name or partial name."),
) -> dict[str, Any] | ToolResult:
    """Retrieves segment keys along with their associated IDs for a specified organization on a Git provider. Supports pagination and text-based filtering to narrow results."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetSegmentsKeysWithIdsRequest(
            path=_models.GetSegmentsKeysWithIdsRequestPath(provider=provider, remote_organization_name=remote_organization_name),
            query=_models.GetSegmentsKeysWithIdsRequestQuery(limit=_limit, search=search)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_segment_keys_with_ids: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/segments/keys/ids", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/segments/keys/ids"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_segment_keys_with_ids")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_segment_keys_with_ids", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_segment_keys_with_ids",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: segments
@mcp.tool(
    title="List Segment Values",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_segment_values(
    provider: str = Field(..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform."),
    segment_key: str = Field(..., alias="segmentKey", description="The unique key identifying the segment whose values should be retrieved."),
    search: str | None = Field(None, description="Optional search string to filter returned segment values by name or identifier, returning only items that match the provided text."),
    limit: str | None = Field(None, description="Maximum number of segment values to return in a single response, accepting values between 1 and 100."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the list of values for a specific segment within an organization, identified by its segment key. Supports optional filtering by name and result count limiting."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetSegmentsRequest(
            path=_models.GetSegmentsRequestPath(provider=provider, remote_organization_name=remote_organization_name, segment_key=segment_key),
            query=_models.GetSegmentsRequestQuery(search=search, limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_segment_values: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/segments/{segmentKey}/values", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/segments/{segmentKey}/values"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_segment_values")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_segment_values", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_segment_values",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: dast
@mcp.tool(
    title="List DAST Targets",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_dast_targets(
    provider: str = Field(..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the specified Git provider."),
    limit: str | None = Field(None, description="Maximum number of DAST targets to return in a single response. Accepts values between 1 and 100."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all configured Dynamic Application Security Testing (DAST) targets for the specified organization. Returns a paginated list of targets that have been set up for security scanning."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetDastTargetsRequest(
            path=_models.GetDastTargetsRequestPath(provider=provider, remote_organization_name=remote_organization_name),
            query=_models.GetDastTargetsRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_dast_targets: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/dast/targets", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/dast/targets"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_dast_targets")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_dast_targets", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_dast_targets",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: dast
@mcp.tool(
    title="Create DAST Target",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_dast_target(
    provider: str = Field(..., description="Short code identifying the Git provider hosting the organization (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform."),
    url: str = Field(..., description="The fully qualified URL of the application or API endpoint to be scanned. Must be a valid URI."),
    target_type: Literal["webapp", "openapi", "graphql"] | None = Field(None, alias="targetType", description="Specifies the type of DAST target to scan: 'webapp' for standard web applications, 'openapi' for REST APIs described by an OpenAPI specification, or 'graphql' for GraphQL APIs. Defaults to 'webapp' if not provided."),
    api_definition_url: str | None = Field(None, alias="apiDefinitionUrl", description="The URL pointing to the API definition file (e.g., an OpenAPI or GraphQL schema), required when the target type is 'openapi' or 'graphql'."),
) -> dict[str, Any] | ToolResult:
    """Creates a new Dynamic Application Security Testing (DAST) target for a specified organization, defining the URL and type of application to be scanned for vulnerabilities."""

    # Construct request model with validation
    try:
        _request = _models.CreateDastTargetRequest(
            path=_models.CreateDastTargetRequestPath(provider=provider, remote_organization_name=remote_organization_name),
            body=_models.CreateDastTargetRequestBody(url=url, target_type=target_type, api_definition_url=api_definition_url)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_dast_target: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/dast/targets", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/dast/targets"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_dast_target")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_dast_target", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_dast_target",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: dast
@mcp.tool(
    title="Delete DAST Target",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_dast_target(
    provider: str = Field(..., description="Short code identifying the Git provider hosting the organization, such as GitHub, GitLab, or Bitbucket."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform."),
    dast_target_id: str = Field(..., alias="dastTargetId", description="The unique numeric identifier of the DAST target to delete."),
) -> dict[str, Any] | ToolResult:
    """Permanently deletes a DAST (Dynamic Application Security Testing) target from the specified organization. This removes the target configuration and stops any associated security scans."""

    _dast_target_id = _parse_int(dast_target_id)

    # Construct request model with validation
    try:
        _request = _models.DeleteDastTargetRequest(
            path=_models.DeleteDastTargetRequestPath(provider=provider, remote_organization_name=remote_organization_name, dast_target_id=_dast_target_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_dast_target: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/dast/targets/{dastTargetId}", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/dast/targets/{dastTargetId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_dast_target")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_dast_target", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_dast_target",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: dast
@mcp.tool(
    title="Trigger DAST Analysis",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def trigger_dast_analysis(
    provider: str = Field(..., description="Short code identifying the Git provider hosting the organization, such as GitHub, GitLab, or Bitbucket."),
    remote_organization_name: str = Field(..., alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform."),
    dast_target_id: str = Field(..., alias="dastTargetId", description="Unique numeric identifier of the DAST target to be analyzed. Must reference an existing target configured under the organization."),
) -> dict[str, Any] | ToolResult:
    """Enqueues a Dynamic Application Security Testing (DAST) analysis for a specified target within an organization. Use this to initiate a security scan against a previously configured DAST target."""

    _dast_target_id = _parse_int(dast_target_id)

    # Construct request model with validation
    try:
        _request = _models.AnalyzeDastTargetRequest(
            path=_models.AnalyzeDastTargetRequestPath(provider=provider, remote_organization_name=remote_organization_name, dast_target_id=_dast_target_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for trigger_dast_analysis: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{provider}/{remoteOrganizationName}/dast/targets/{dastTargetId}/analyze", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{provider}/{remoteOrganizationName}/dast/targets/{dastTargetId}/analyze"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("trigger_dast_analysis")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("trigger_dast_analysis", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="trigger_dast_analysis",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: enterprise
@mcp.tool(
    title="List Enterprise Organizations",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_enterprise_organizations(
    enterprise_name: str = Field(..., alias="enterpriseName", description="The unique slug identifier for the enterprise whose organizations you want to retrieve."),
    provider: str = Field(..., description="The Git provider hosting the enterprise, specified as a short identifier code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    limit: str | None = Field(None, description="Maximum number of organizations to return in a single response. Accepts values between 1 and 100, defaulting to 100 if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the list of organizations belonging to a specified enterprise on a given Git provider. Supports pagination via a configurable result limit."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.ListEnterpriseOrganizationsRequest(
            path=_models.ListEnterpriseOrganizationsRequestPath(enterprise_name=enterprise_name, provider=provider),
            query=_models.ListEnterpriseOrganizationsRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_enterprise_organizations: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/enterprises/{provider}/{enterpriseName}/organizations", _request.path.model_dump(by_alias=True)) if _request.path else "/enterprises/{provider}/{enterpriseName}/organizations"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_enterprise_organizations")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_enterprise_organizations", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_enterprise_organizations",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: enterprise
@mcp.tool(
    title="List Enterprises",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_enterprises(
    provider: str = Field(..., description="The Git provider to query for enterprises, identified by its short code (e.g., GitHub, GitLab, Bitbucket)."),
    limit: str | None = Field(None, description="Maximum number of enterprise records to return in a single response, between 1 and 100 inclusive."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all enterprises associated with the authenticated user for a specified Git provider. Returns a paginated list of enterprise accounts the user has access to."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.ListEnterprisesRequest(
            path=_models.ListEnterprisesRequestPath(provider=provider),
            query=_models.ListEnterprisesRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_enterprises: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/enterprises/{provider}", _request.path.model_dump(by_alias=True)) if _request.path else "/enterprises/{provider}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_enterprises")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_enterprises", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_enterprises",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: enterprise
@mcp.tool(
    title="Get Enterprise",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_enterprise(
    enterprise_name: str = Field(..., alias="enterpriseName", description="The unique slug identifier for the enterprise, typically a lowercase hyphenated name used in URLs."),
    provider: str = Field(..., description="The short code identifying the git provider hosting the enterprise (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
) -> dict[str, Any] | ToolResult:
    """Retrieves details for a specific enterprise account by its slug identifier and git provider. Use this to fetch enterprise-level configuration, metadata, or status."""

    # Construct request model with validation
    try:
        _request = _models.GetEnterpriseRequest(
            path=_models.GetEnterpriseRequestPath(enterprise_name=enterprise_name, provider=provider)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_enterprise: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/enterprises/{provider}/{enterpriseName}", _request.path.model_dump(by_alias=True)) if _request.path else "/enterprises/{provider}/{enterpriseName}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_enterprise")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_enterprise", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_enterprise",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: enterprise
@mcp.tool(
    title="List Enterprise Seats",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_enterprise_seats(
    provider: str = Field(..., description="The Git provider hosting the enterprise, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket)."),
    enterprise_name: str = Field(..., alias="enterpriseName", description="The URL-friendly slug identifier of the enterprise whose seats are being listed."),
    limit: str | None = Field(None, description="Maximum number of seat records to return in a single response. Accepts values between 1 and 100."),
    search: str | None = Field(None, description="Optional search string used to filter the returned seats, matching against relevant seat or user identifiers."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of seats allocated within a specified enterprise on a given Git provider. Supports filtering by search term to narrow results."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.ListEnterpriseSeatsRequest(
            path=_models.ListEnterpriseSeatsRequestPath(provider=provider, enterprise_name=enterprise_name),
            query=_models.ListEnterpriseSeatsRequestQuery(limit=_limit, search=search)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_enterprise_seats: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/enterprises/{provider}/{enterpriseName}/seats", _request.path.model_dump(by_alias=True)) if _request.path else "/enterprises/{provider}/{enterpriseName}/seats"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_enterprise_seats")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_enterprise_seats", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_enterprise_seats",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: reports
@mcp.tool(
    title="Export Enterprise Seats CSV",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def export_enterprise_seats_csv(
    provider: str = Field(..., description="The Git provider hosting the enterprise, identified by a short slug (e.g., GitHub, GitLab, Bitbucket)."),
    enterprise_name: str = Field(..., alias="enterpriseName", description="The unique slug (URL-friendly identifier) of the enterprise whose seat data should be exported."),
) -> dict[str, Any] | ToolResult:
    """Exports a CSV file containing seat allocation and usage data for a specified enterprise on a given Git provider. Useful for auditing license consumption and user activity across the enterprise."""

    # Construct request model with validation
    try:
        _request = _models.ListEnterpriseSeatsCsvRequest(
            path=_models.ListEnterpriseSeatsCsvRequestPath(provider=provider, enterprise_name=enterprise_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for export_enterprise_seats_csv: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/reports/enterprises/{provider}/{enterpriseName}/seats-csv", _request.path.model_dump(by_alias=True)) if _request.path else "/reports/enterprises/{provider}/{enterpriseName}/seats-csv"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("export_enterprise_seats_csv")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("export_enterprise_seats_csv", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="export_enterprise_seats_csv",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: billing
@mcp.tool(
    title="List Payment Plans",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_payment_plans() -> dict[str, Any] | ToolResult:
    """Retrieves all available payment plans offered in Codacy, allowing users to review pricing tiers and subscription options."""

    # Extract parameters for API call
    _http_path = "/plans"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_payment_plans")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_payment_plans", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_payment_plans",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: security
@mcp.tool(
    title="Get OSSF Scorecard",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def get_ossf_scorecard() -> dict[str, Any] | ToolResult:
    """Retrieves the OSSF (Open Source Security Foundation) Scorecard for a repository, providing security health metrics and risk assessments across key supply chain security practices."""

    # Extract parameters for API call
    _http_path = "/security/dependencies/ossf/scorecard"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_ossf_scorecard")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_ossf_scorecard", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_ossf_scorecard",
        method="POST",
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
        print("  python codacy_server.py", file=sys.stderr)
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

    parser = argparse.ArgumentParser(description="Codacy MCP Server")

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
    logger.info("Starting Codacy MCP Server")
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
